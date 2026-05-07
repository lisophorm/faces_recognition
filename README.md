# White Swan Data Video Annotation

This project is a coding-assessment solution that annotates an MP4 video by detecting faces and labelling known Harry Potter characters using DeepFace.

It is designed to run after a clean clone and a standard Python install, without CUDA or NVIDIA driver dependencies. GPU acceleration is intentionally disabled by default for portability and reproducibility.

The implementation uses:

- RetinaFace for face detection
- Facenet512 embeddings for face recognition
- cosine-distance matching against a small reference gallery
- OpenCV for video reading, drawing, and writing

## Quick start

Create and activate a virtual environment, then install the dependencies from the project root:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt```

On Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

The `scripts/bootstrap.sh` helper normalizes TensorFlow to the CPU wheel on
Linux. On Windows, use the same Python environment and install the CPU-only
TensorFlow wheel manually if needed:

```powershell
python -m pip uninstall -y tensorflow
python -m pip install --force-reinstall tensorflow-cpu==2.21.0
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

The loader also scans subfolders recursively, so it is safe to organise poses or source images under each character directory.

See [docs](./docs/README.md) for setup, usage, reference image guidance, troubleshooting, and implementation notes.
