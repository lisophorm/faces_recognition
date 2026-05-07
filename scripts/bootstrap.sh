#!/usr/bin/env bash
set -euo pipefail

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# DeepFace's dependency metadata still pulls in the GPU-capable TensorFlow wheel.
# Replace it with the CPU wheel so a fresh clone runs cleanly without CUDA.
python -m pip uninstall -y tensorflow >/dev/null 2>&1 || true
python -m pip install --force-reinstall tensorflow-cpu==2.21.0
