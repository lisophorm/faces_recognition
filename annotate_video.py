"""Annotate known Harry Potter faces in an MP4 using DeepFace embeddings."""

from __future__ import annotations

import argparse
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import cv2
import numpy as np

# Keep simple CLI operations such as `--help` free from TensorFlow info logs. DeepFace is
# imported lazily below so this environment variable is set before TensorFlow loads.
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")
# DeepFace/RetinaFace are more reliable with current TensorFlow installs when
# legacy Keras compatibility is enabled. `tf-keras` is included in requirements.
os.environ.setdefault("TF_USE_LEGACY_KERAS", "1")


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
DEFAULT_RECOGNITION_INTERVAL = 5
DEFAULT_THRESHOLD = 0.35
REFERENCE_LABELS = {
    "harry_potter": "Harry Potter",
    "hermione_granger": "Hermione Granger",
    "prof_mcgonagall": "Prof. McGonagall",
    "prof_severus_snape": "Prof. Severus Snape",
    "ron_weasley": "Ron Weasley",
}


@dataclass(frozen=True)
class ReferenceGallery:
    """All usable reference faces for one character."""

    label: str
    image_paths: list[Path]
    embeddings: list[np.ndarray]
    prototype: np.ndarray


@dataclass(frozen=True)
class FaceAnnotation:
    """One detected face and the label that will be drawn on the output frame."""

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
        default=None,
        help="Run detection and recognition every N frames, reusing labels between runs.",
    )
    parser.add_argument(
        "--frame-skip",
        type=int,
        default=None,
        help=(
            "Skip this many frames between recognition passes. "
            "Overrides --recognition-interval when set."
        ),
    )
    parser.add_argument(
        "--output-frame-skip",
        type=int,
        default=0,
        help="Skip this many frames between written output frames.",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=DEFAULT_THRESHOLD,
        help="Maximum cosine distance for a known-person label.",
    )
    parser.add_argument(
        "--min-face-confidence",
        type=float,
        default=0.0,
        help=(
            "Minimum detector confidence to keep a face. "
            "RetinaFace usually returns high confidence for real faces; 0 keeps all "
            "positive-confidence detections while still dropping DeepFace's no-face fallback."
        ),
    )
    parser.add_argument(
        "--show-distance",
        action="store_true",
        help="Draw the cosine distance next to known labels for debugging/tuning.",
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


def deepface_api() -> Any:
    """Import DeepFace only when model work is needed, not for argument parsing."""
    from deepface import DeepFace

    return DeepFace


def effective_recognition_interval(args: argparse.Namespace) -> int:
    # `--frame-skip` is friendlier for users, but internally the loop needs an
    # interval. Skipping 4 frames means recognising once every 5 frames.
    if args.frame_skip is not None:
        if args.frame_skip < 0:
            raise ValueError("--frame-skip must be at least 0")
        return args.frame_skip + 1

    if args.recognition_interval is None:
        return DEFAULT_RECOGNITION_INTERVAL
    if args.recognition_interval < 1:
        raise ValueError("--recognition-interval must be at least 1")
    return args.recognition_interval


def effective_output_interval(args: argparse.Namespace) -> int:
    # Output skipping is separate from recognition skipping: it controls file
    # size/encoding work, while recognition skipping controls DeepFace calls.
    if args.output_frame_skip < 0:
        raise ValueError("--output-frame-skip must be at least 0")
    return args.output_frame_skip + 1


def validate_processing_args(args: argparse.Namespace) -> None:
    # Validate the cheap, predictable failure cases before loading ML models.
    if args.max_frames is not None and args.max_frames < 1:
        raise ValueError("--max-frames must be at least 1 when provided")
    if not np.isfinite(args.threshold) or args.threshold < 0:
        raise ValueError("--threshold must be a finite non-negative number")
    if not np.isfinite(args.min_face_confidence) or args.min_face_confidence < 0:
        raise ValueError("--min-face-confidence must be a finite non-negative number")
    if not args.input.is_file():
        raise FileNotFoundError(f"Input video does not exist: {args.input}")
    if not args.refs.is_dir():
        raise FileNotFoundError(f"Reference directory does not exist: {args.refs}")


def iter_reference_images(refs_dir: Path) -> Iterable[tuple[str, Path]]:
    # Folder names are stable machine-readable keys; display labels are kept
    # separate so the video annotation text can be presentation-friendly.
    for character_dir in sorted(path for path in refs_dir.iterdir() if path.is_dir()):
        label = REFERENCE_LABELS.get(
            character_dir.name,
            character_dir.name.replace("_", " ").title(),
        )
        for image_path in sorted(
            path for path in character_dir.rglob("*") if path.is_file()
        ):
            if image_path.suffix.lower() in IMAGE_EXTENSIONS:
                yield label, image_path


def cosine_distance(left: np.ndarray, right: np.ndarray) -> float:
    # DeepFace embeddings are compared by cosine distance: smaller is more
    # similar, and a distance below the threshold is treated as a known person.
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
    # DeepFace returns a list because an image can contain multiple faces. For
    # references, images are expected to contain one primary face; for detected
    # crops, the crop itself is treated as the face.
    representations = deepface_api().represent(
        img_path=image,
        model_name=model_name,
        detector_backend=detector_backend,
        enforce_detection=enforce_detection,
    )
    if not representations:
        return None
    return np.asarray(representations[0]["embedding"], dtype=np.float32)


def load_reference_galleries(
    refs_dir: Path,
    *,
    model_name: str,
    detector_backend: str,
) -> list[ReferenceGallery]:
    references_by_label: dict[str, list[tuple[Path, np.ndarray]]] = {}
    for label, image_path in iter_reference_images(refs_dir):
        try:
            # Enforce detection for references so weak reference images fail
            # early instead of polluting the gallery with poor embeddings.
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

        references_by_label.setdefault(label, []).append((image_path, embedding))
        print(f"Loaded reference: {label} from {image_path}")

    galleries: list[ReferenceGallery] = []
    for label, items in sorted(references_by_label.items()):
        # Group all images for a character so matching can use both individual
        # examples and an averaged representation of the character.
        image_paths = [image_path for image_path, _ in items]
        embeddings = [embedding for _, embedding in items]

        # A per-character prototype makes small reference galleries less brittle, while
        # retaining individual-image comparisons preserves useful pose-specific matches.
        normalized_embeddings = []
        for embedding in embeddings:
            norm = np.linalg.norm(embedding)
            normalized_embeddings.append(embedding if norm == 0 else embedding / norm)

        prototype = np.mean(np.stack(normalized_embeddings, axis=0), axis=0)
        prototype_norm = np.linalg.norm(prototype)
        if prototype_norm != 0:
            prototype = prototype / prototype_norm
        galleries.append(
            ReferenceGallery(
                label=label,
                image_paths=image_paths,
                embeddings=embeddings,
                prototype=prototype.astype(np.float32),
            )
        )

    if not galleries:
        raise RuntimeError(f"No usable reference faces found in {refs_dir}")

    reference_count = sum(len(gallery.image_paths) for gallery in galleries)
    print(f"Loaded {reference_count} reference images across {len(galleries)} labels.")
    return galleries


def best_match(
    embedding: np.ndarray,
    references: list[ReferenceGallery],
    threshold: float,
) -> tuple[str, float | None]:
    distances = []
    for reference in references:
        # Compare against each original reference image and the prototype. The
        # best distance wins, which helps with pose and lighting variation.
        embedding_distances = [
            cosine_distance(embedding, reference_embedding)
            for reference_embedding in reference.embeddings
        ]
        prototype_distance = cosine_distance(embedding, reference.prototype)
        distances.append(
            (reference.label, min([prototype_distance, *embedding_distances]))
        )

    label, distance = min(distances, key=lambda item: item[1])
    if distance <= threshold:
        return label, distance
    return "Unknown", distance


def detect_and_recognize(
    frame_bgr: np.ndarray,
    references: list[ReferenceGallery],
    *,
    model_name: str,
    detector_backend: str,
    threshold: float,
    min_face_confidence: float,
) -> list[FaceAnnotation]:
    # Detection and recognition are intentionally split. RetinaFace finds boxes;
    # Facenet512 then embeds each cropped face for identity matching.
    faces = deepface_api().extract_faces(
        img_path=frame_bgr,
        detector_backend=detector_backend,
        enforce_detection=False,
        align=True,
        # `represent(..., detector_backend="skip")` expects BGR arrays. DeepFace crops
        # faces as RGB by default, so make this explicit to keep video embeddings in the
        # same color convention as reference embeddings loaded from disk.
        color_face="bgr",
    )

    annotations: list[FaceAnnotation] = []
    for face in faces:
        # DeepFace gives boxes as x/y/w/h. Clamp to non-negative coordinates so
        # OpenCV drawing is robust even when a detector returns edge boxes.
        area = face.get("facial_area") or {}
        x = max(int(area.get("x", 0)), 0)
        y = max(int(area.get("y", 0)), 0)
        w = max(int(area.get("w", 0)), 0)
        h = max(int(area.get("h", 0)), 0)
        if w == 0 or h == 0:
            continue

        confidence = face.get("confidence")
        # When enforce_detection=False, DeepFace can return the full frame as a
        # zero-confidence fallback if no face is found. Do not draw that as a face.
        if confidence is not None and float(confidence) <= min_face_confidence:
            continue

        face_image = face.get("face")
        if face_image is None:
            continue

        try:
            # The face has already been detected, so `skip` avoids running a
            # detector a second time for every crop.
            embedding = embedding_from_image(
                face_image,
                model_name=model_name,
                detector_backend="skip",
                enforce_detection=False,
            )
        except Exception as exc:
            print(
                "Warning: could not embed detected face "
                f"at ({x}, {y}, {w}, {h}): {exc}"
            )
            embedding = None

        if embedding is None:
            label, distance = "Unknown", None
        else:
            label, distance = best_match(embedding, references, threshold)

        annotations.append(
            FaceAnnotation(label=label, distance=distance, x=x, y=y, w=w, h=h)
        )

    return annotations


def draw_annotations(
    frame: np.ndarray,
    annotations: list[FaceAnnotation],
    *,
    show_distance: bool,
) -> None:
    for annotation in annotations:
        # Green marks confident known-character matches; orange keeps unknown
        # faces visible without implying the identity is known.
        color = (0, 200, 0) if annotation.label != "Unknown" else (0, 165, 255)
        top_left = (annotation.x, annotation.y)
        bottom_right = (annotation.x + annotation.w, annotation.y + annotation.h)
        cv2.rectangle(frame, top_left, bottom_right, color, 2)

        text = annotation.label
        if show_distance and annotation.distance is not None:
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
    validate_processing_args(args)
    recognition_interval = effective_recognition_interval(args)
    output_interval = effective_output_interval(args)

    # Build the reference gallery once before opening the video. This is the
    # expensive startup step, but it avoids recomputing reference embeddings for
    # every frame.
    references = load_reference_galleries(
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
    output_fps = fps / output_interval
    writer = cv2.VideoWriter(
        str(args.output),
        cv2.VideoWriter_fourcc(*"mp4v"),
        output_fps,
        (width, height),
    )
    if not writer.isOpened():
        capture.release()
        raise RuntimeError(f"Could not open output video writer: {args.output}")

    print(
        f"Processing {args.input} "
        f"({width}x{height}, {fps:.2f} fps, {total_frames} frames)"
    )
    print(f"Writing annotated video to {args.output}")
    print(
        "Settings: "
        f"model={args.model_name}, detector={args.detector_backend}, "
        f"threshold={args.threshold:.2f}, "
        f"min_face_confidence={args.min_face_confidence:.2f}, "
        f"recognition_interval={recognition_interval}, output_fps={output_fps:.2f}, "
        f"show_distance={args.show_distance}"
    )

    frame_index = 0
    written_frames = 0
    last_annotations: list[FaceAnnotation] = []
    try:
        while True:
            ok, frame = capture.read()
            if not ok:
                break
            if args.max_frames is not None and frame_index >= args.max_frames:
                break

            # Recognition is the slow path. Between recognition frames, reuse
            # the previous annotations so the output remains annotated while
            # keeping runtime practical for a coding-assessment submission.
            if frame_index % recognition_interval == 0:
                print(f"Recognizing frame {frame_index}")
                last_annotations = detect_and_recognize(
                    frame,
                    references,
                    model_name=args.model_name,
                    detector_backend=args.detector_backend,
                    threshold=args.threshold,
                    min_face_confidence=args.min_face_confidence,
                )

            draw_annotations(frame, last_annotations, show_distance=args.show_distance)
            # Output-frame skipping lowers written FPS to preserve approximate
            # playback duration instead of speeding up the resulting video.
            if frame_index % output_interval == 0:
                writer.write(frame)
                written_frames += 1
            frame_index += 1
    finally:
        capture.release()
        writer.release()

    print(f"Done. Processed {frame_index} frames, wrote {written_frames} frames.")


def main() -> None:
    try:
        annotate_video(parse_args())
    except (FileNotFoundError, RuntimeError, ValueError) as exc:
        # Expected operational errors should be readable from a terminal without
        # a Python traceback. Unexpected bugs are intentionally not swallowed.
        raise SystemExit(f"Error: {exc}") from None


if __name__ == "__main__":
    main()
