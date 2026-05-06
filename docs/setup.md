# Setup

## Requirements

Recommended environment:

- Python 3.10, 3.11, or 3.12
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
- `tf-keras` for RetinaFace compatibility with current TensorFlow/Keras releases
- `numpy` for vector operations
