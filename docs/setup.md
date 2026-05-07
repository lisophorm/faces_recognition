# Setup

## Requirements

Recommended environment:

- Python 3.10 or 3.11
- An MP4 input video
- A folder of reference face images for the target characters

Python 3.12 may work with recent TensorFlow builds, but Python 3.10 or 3.11 is the safer choice for DeepFace/TensorFlow compatibility.

The script runs in CPU-only mode by default so the assessment can be executed
on a fresh clone without installing CUDA or NVIDIA user-space libraries. That
keeps the deliverable reproducible on systems that only have a standard Python
environment available.

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
- `tensorflow-cpu` as a DeepFace runtime dependency
- `tf-keras` for RetinaFace compatibility with current TensorFlow/Keras releases
- `numpy` for vector operations

The script sets `TF_USE_LEGACY_KERAS=1` before importing DeepFace so that RetinaFace works reliably with current TensorFlow/Keras installations.
