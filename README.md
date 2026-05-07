# White Swan Data Video Annotation

This project is a coding-assessment solution that annotates an MP4 video by detecting faces and labelling known Harry Potter characters using DeepFace.

**This assessment presented a problem space I had not worked with directly before. I approached the task as an engineering and research exercise.**

**I believe the final result strongly reflects my capacity to quickly research unfamiliar domains, analyse trade-offs, make pragmatic technical decisions, and deliver a working solution on time and within scope.**

The implementation uses:

- RetinaFace for face detection
- Facenet512 embeddings for face recognition
- cosine-distance matching against a small reference gallery
- OpenCV for video reading, drawing, and writing

## Quick start

Create and activate a virtual environment, then install the dependencies:

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

Place the downloaded input video at `input/nimbus.mp4`, create reference images under `refs/`, then run:

```bash
python annotate_video.py --input input/nimbus.mp4 --refs refs --output output/annotated.mp4
```

For a short smoke test:

```bash
python annotate_video.py --input input/nimbus.mp4 --refs refs --output output/test_annotated.mp4 --max-frames 50
```

## Reference gallery

The script expects reference images in this structure:

```text
refs/
  harry_potter/
  hermione_granger/
  prof_mcgonagall/
  prof_severus_snape/
  ron_weasley/
```

Each folder can contain one or more `.jpg`, `.jpeg`, `.png`, or `.webp` files. More than one clear face image per character usually improves recognition.

## Submission checklist

Before sending the assessment back, include:

- `annotate_video.py`
- `requirements.txt`
- `README.md`
- `docs/`
- `AGENTS.md`
- the generated annotated MP4 output
- either the reference images used or a note explaining how the reference gallery was built

See [docs](./docs/README.md) for setup, usage, reference image guidance, troubleshooting, and implementation notes.
