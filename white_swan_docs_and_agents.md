# Files to Add

```text
/docs
  README.md
  setup.md
  usage.md
  reference-images.md
  troubleshooting.md
  approach.md
AGENTS.md
```

---

# `/docs/README.md`

```md
# Documentation

This folder contains the project documentation for the White Swan Data video annotation assessment.

Start here:

- [Setup](./setup.md)
- [Usage](./usage.md)
- [Reference Images](./reference-images.md)
- [Troubleshooting](./troubleshooting.md)
- [Approach](./approach.md)

The main entry point for the code is `annotate_video.py` in the project root.
```

---

# `/docs/setup.md`

```md
# Setup

## Requirements

Recommended environment:

- Python 3.10 or 3.11
- An MP4 input video
- A folder of reference face images for the target characters

Install dependencies from the project root:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

On Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Dependencies

The project uses:

- `deepface` for face detection and embedding generation
- `retina-face` as the detector backend
- `opencv-python` for reading and writing video
- `tensorflow` as a DeepFace runtime dependency
- `numpy` for vector operations
```

---

# `/docs/usage.md`

```md
# Usage

Run the annotator from the project root:

```bash
python annotate_video.py --input input.mp4 --refs refs --output annotated.mp4
```

## Common options

Process only a small number of frames for testing:

```bash
python annotate_video.py --input input.mp4 --refs refs --output test_annotated.mp4 --max-frames 200
```

Run recognition every frame for better accuracy but slower processing:

```bash
python annotate_video.py --input input.mp4 --refs refs --output annotated.mp4 --recognition-interval 1
```

Use stricter matching:

```bash
python annotate_video.py --input input.mp4 --refs refs --output annotated.mp4 --threshold 0.25
```

Use more permissive matching:

```bash
python annotate_video.py --input input.mp4 --refs refs --output annotated.mp4 --threshold 0.40
```

## Output

The output is an MP4 file with:

- bounding boxes around detected faces
- character names where recognition is confident enough
- `Unknown` for faces that do not match the reference set
```

---

# `/docs/reference-images.md`

```md
# Reference Images

The recogniser needs clear reference images for each character.

Create this folder structure:

```text
refs/
  Harry Potter/
    harry_1.jpg
    harry_2.jpg
  Ron Weasley/
    ron_1.jpg
  Hermione Granger/
    hermione_1.jpg
  Prof. McGonagall/
    mcgonagall_1.jpg
  Prof. Severus Snape/
    snape_1.jpg
```

## Tips

Use images where:

- the face is visible and not heavily blurred
- the face is reasonably front-facing
- lighting is clear
- only one main face is present
- the image reflects the character appearance in the input video

More than one reference image per character usually improves results.

## Character labels

The expected labels are:

- Harry Potter
- Ron Weasley
- Hermione Granger
- Prof. McGonagall
- Prof. Severus Snape
```

---

# `/docs/troubleshooting.md`

```md
# Troubleshooting

## The script is slow

RetinaFace is accurate but slow. Increase the recognition interval:

```bash
python annotate_video.py --input input.mp4 --refs refs --output annotated.mp4 --recognition-interval 10
```

## Faces are detected but labels are wrong

Use a stricter threshold:

```bash
python annotate_video.py --input input.mp4 --refs refs --output annotated.mp4 --threshold 0.25
```

Also improve the reference images. Wrong labels usually mean the reference set is too weak or the threshold is too permissive.

## Known characters are labelled Unknown

Use a more permissive threshold:

```bash
python annotate_video.py --input input.mp4 --refs refs --output annotated.mp4 --threshold 0.40
```

Also add more reference images for the missed character.

## No faces are found in reference images

Use clearer images. Avoid profile shots, dark images, small faces, and images with many people.

## Output video does not play

The script writes MP4 using OpenCV's `mp4v` codec. If a player has trouble opening it, re-encode with ffmpeg:

```bash
ffmpeg -i annotated.mp4 -vcodec libx264 -pix_fmt yuv420p annotated_h264.mp4
```
```

---

# `/docs/approach.md`

```md
# Approach

The solution uses DeepFace to perform two tasks:

1. Detect faces in each sampled video frame.
2. Compare each detected face with known character reference images.

## Detection

The default detector is RetinaFace because it usually performs well on film footage with varied lighting, angles, and partial occlusion.

## Recognition

The script uses the Facenet512 embedding model. Each reference image is converted into an embedding. For each detected face in the video, the script calculates a new embedding and compares it with all reference embeddings using cosine distance.

The closest character match is selected when the distance is below the configured threshold. Otherwise, the face is labelled `Unknown`.

## Performance trade-off

Running detection and recognition on every frame can be slow. By default, the script recognises every few frames and reuses the last annotations in between. This gives reasonable output while keeping runtime manageable.

For best accuracy, use:

```bash
--recognition-interval 1
```

For faster processing, use a higher value, such as:

```bash
--recognition-interval 10
```
```

---

# `AGENTS.md`

```md
# AGENTS.md

Guidance for coding agents working on this repository.

## Project purpose

This project is a submission for the White Swan Data ML Engineer coding assessment. It processes an MP4 video, detects faces, and labels known Harry Potter characters where possible using DeepFace.

The primary script is:

```text
annotate_video.py
```

Documentation lives in:

```text
docs/
```

## Keep documentation updated

Whenever you change code, dependencies, CLI arguments, runtime behaviour, or project structure, update the documentation in the same change.

Required checks before finishing any code change:

1. If command-line arguments changed, update `docs/usage.md`.
2. If setup, Python version, or dependencies changed, update `docs/setup.md` and `requirements.txt`.
3. If recognition logic, model choice, detector backend, thresholds, or frame sampling changed, update `docs/approach.md`.
4. If reference image expectations changed, update `docs/reference-images.md`.
5. If common errors or operational fixes changed, update `docs/troubleshooting.md`.
6. If new docs are added, link them from `docs/README.md`.

Do not leave stale examples in the documentation.

## Coding conventions

- Keep the script runnable from the project root.
- Prefer explicit, readable Python over clever abstractions.
- Keep CLI options backwards-compatible where practical.
- Use clear warning and info messages for long-running video processing.
- Do not hard-code local machine paths.
- Treat input and output paths as user-provided CLI parameters.

## ML and video-processing notes

- Default detector backend should remain `retinaface` unless there is a documented reason to change it.
- Default recognition model should remain `Facenet512` unless there is a documented reason to change it.
- Recognition does not need perfect accuracy; practical, explainable performance is enough for this assessment.
- Prefer changes that improve robustness and make failure modes understandable.

## Testing guidance

Before finalising changes, run a short-frame test when possible:

```bash
python annotate_video.py --input input.mp4 --refs refs --output test_annotated.mp4 --max-frames 50
```

If test media or reference images are not available, document that the command was not run and why.

## Submission checklist

A complete submission should include:

- `annotate_video.py`
- `requirements.txt`
- `README.md`
- `AGENTS.md`
- `docs/`
- the generated annotated MP4 output
- instructions explaining how to run the script
```

