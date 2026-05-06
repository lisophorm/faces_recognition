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
