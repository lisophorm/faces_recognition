from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import cv2
import numpy as np
from deepface import DeepFace


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
REFERENCE_LABELS = {
    "harry_potter": "Harry Potter",
    "hermione_granger": "Hermione Granger",
    "prof_mcgonagall": "Prof. McGonagall",
    "prof_severus_snape": "Prof. Severus Snape",
    "ron_weasley": "Ron Weasley",
}


@dataclass(frozen=True)
class ReferenceFace:
    label: str
    image_path: Path
    embedding: np.ndarray


@dataclass(frozen=True)
class FaceAnnotation:
    label: str
    distance: float | None
    x: int
    y: int
    w: int
    h: int


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Detect and label known faces in a video using DeepFace references."
    )
    parser.add_argument("--input", required=True, type=Path, help="Input MP4 video path.")
    parser.add_argument(
        "--refs",
        required=True,
        type=Path,
        help="Reference image folder. Known subfolder names are mapped to display labels.",
    )
    parser.add_argument("--output", required=True, type=Path, help="Output MP4 video path.")
    parser.add_argument(
        "--recognition-interval",
        type=int,
        default=5,
        help="Run detection and recognition every N frames, reusing labels between runs.",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.35,
        help="Maximum cosine distance for a known-person label.",
    )
    parser.add_argument(
        "--max-frames",
        type=int,
        default=None,
        help="Optional maximum number of frames to process for short test runs.",
    )
    parser.add_argument(
        "--detector-backend",
        default="retinaface",
        help="DeepFace detector backend.",
    )
    parser.add_argument(
        "--model-name",
        default="Facenet512",
        help="DeepFace embedding model.",
    )
    return parser.parse_args()


def iter_reference_images(refs_dir: Path) -> Iterable[tuple[str, Path]]:
    for character_dir in sorted(path for path in refs_dir.iterdir() if path.is_dir()):
        label = REFERENCE_LABELS.get(character_dir.name, character_dir.name.replace("_", " ").title())
        for image_path in sorted(character_dir.iterdir()):
            if image_path.suffix.lower() in IMAGE_EXTENSIONS:
                yield label, image_path


def cosine_distance(left: np.ndarray, right: np.ndarray) -> float:
    denominator = np.linalg.norm(left) * np.linalg.norm(right)
    if denominator == 0:
        return float("inf")
    return float(1 - np.dot(left, right) / denominator)


def embedding_from_image(
    image: str | np.ndarray,
    *,
    model_name: str,
    detector_backend: str,
    enforce_detection: bool,
) -> np.ndarray | None:
    representations = DeepFace.represent(
        img_path=image,
        model_name=model_name,
        detector_backend=detector_backend,
        enforce_detection=enforce_detection,
    )
    if not representations:
        return None
    return np.asarray(representations[0]["embedding"], dtype=np.float32)


def load_reference_faces(
    refs_dir: Path,
    *,
    model_name: str,
    detector_backend: str,
) -> list[ReferenceFace]:
    if not refs_dir.exists():
        raise FileNotFoundError(f"Reference directory does not exist: {refs_dir}")

    references: list[ReferenceFace] = []
    for label, image_path in iter_reference_images(refs_dir):
        try:
            embedding = embedding_from_image(
                str(image_path),
                model_name=model_name,
                detector_backend=detector_backend,
                enforce_detection=True,
            )
        except Exception as exc:
            print(f"Warning: skipping {image_path}: {exc}")
            continue

        if embedding is None:
            print(f"Warning: skipping {image_path}: no face embedding found")
            continue

        references.append(ReferenceFace(label=label, image_path=image_path, embedding=embedding))
        print(f"Loaded reference: {label} from {image_path}")

    if not references:
        raise RuntimeError(f"No usable reference faces found in {refs_dir}")

    return references


def best_match(
    embedding: np.ndarray,
    references: list[ReferenceFace],
    threshold: float,
) -> tuple[str, float | None]:
    distances = [
        (reference.label, cosine_distance(embedding, reference.embedding))
        for reference in references
    ]
    label, distance = min(distances, key=lambda item: item[1])
    if distance <= threshold:
        return label, distance
    return "Unknown", distance


def detect_and_recognize(
    frame_bgr: np.ndarray,
    references: list[ReferenceFace],
    *,
    model_name: str,
    detector_backend: str,
    threshold: float,
) -> list[FaceAnnotation]:
    faces = DeepFace.extract_faces(
        img_path=frame_bgr,
        detector_backend=detector_backend,
        enforce_detection=False,
        align=True,
    )

    annotations: list[FaceAnnotation] = []
    for face in faces:
        area = face.get("facial_area") or {}
        x = max(int(area.get("x", 0)), 0)
        y = max(int(area.get("y", 0)), 0)
        w = max(int(area.get("w", 0)), 0)
        h = max(int(area.get("h", 0)), 0)
        if w == 0 or h == 0:
            continue

        face_image = face.get("face")
        if face_image is None:
            continue

        try:
            embedding = embedding_from_image(
                face_image,
                model_name=model_name,
                detector_backend="skip",
                enforce_detection=False,
            )
        except Exception as exc:
            print(f"Warning: could not embed detected face at ({x}, {y}, {w}, {h}): {exc}")
            embedding = None

        if embedding is None:
            label, distance = "Unknown", None
        else:
            label, distance = best_match(embedding, references, threshold)

        annotations.append(FaceAnnotation(label=label, distance=distance, x=x, y=y, w=w, h=h))

    return annotations


def draw_annotations(frame: np.ndarray, annotations: list[FaceAnnotation]) -> None:
    for annotation in annotations:
        color = (0, 200, 0) if annotation.label != "Unknown" else (0, 165, 255)
        top_left = (annotation.x, annotation.y)
        bottom_right = (annotation.x + annotation.w, annotation.y + annotation.h)
        cv2.rectangle(frame, top_left, bottom_right, color, 2)

        text = annotation.label
        if annotation.distance is not None:
            text = f"{text} ({annotation.distance:.2f})"

        text_origin = (annotation.x, max(annotation.y - 10, 20))
        cv2.putText(
            frame,
            text,
            text_origin,
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            color,
            2,
            cv2.LINE_AA,
        )


def annotate_video(args: argparse.Namespace) -> None:
    if args.recognition_interval < 1:
        raise ValueError("--recognition-interval must be at least 1")
    if args.max_frames is not None and args.max_frames < 1:
        raise ValueError("--max-frames must be at least 1 when provided")
    if not args.input.exists():
        raise FileNotFoundError(f"Input video does not exist: {args.input}")

    references = load_reference_faces(
        args.refs,
        model_name=args.model_name,
        detector_backend=args.detector_backend,
    )

    capture = cv2.VideoCapture(str(args.input))
    if not capture.isOpened():
        raise RuntimeError(f"Could not open input video: {args.input}")

    fps = capture.get(cv2.CAP_PROP_FPS) or 25
    width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
    if width <= 0 or height <= 0:
        raise RuntimeError("Input video has invalid dimensions")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    writer = cv2.VideoWriter(
        str(args.output),
        cv2.VideoWriter_fourcc(*"mp4v"),
        fps,
        (width, height),
    )
    if not writer.isOpened():
        capture.release()
        raise RuntimeError(f"Could not open output video writer: {args.output}")

    print(f"Processing {args.input} ({width}x{height}, {fps:.2f} fps, {total_frames} frames)")
    print(f"Writing annotated video to {args.output}")

    frame_index = 0
    last_annotations: list[FaceAnnotation] = []
    try:
        while True:
            ok, frame = capture.read()
            if not ok:
                break
            if args.max_frames is not None and frame_index >= args.max_frames:
                break

            if frame_index % args.recognition_interval == 0:
                print(f"Recognizing frame {frame_index}")
                last_annotations = detect_and_recognize(
                    frame,
                    references,
                    model_name=args.model_name,
                    detector_backend=args.detector_backend,
                    threshold=args.threshold,
                )

            draw_annotations(frame, last_annotations)
            writer.write(frame)
            frame_index += 1
    finally:
        capture.release()
        writer.release()

    print(f"Done. Processed {frame_index} frames.")


def main() -> None:
    annotate_video(parse_args())


if __name__ == "__main__":
    main()
