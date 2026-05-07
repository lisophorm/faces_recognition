# White Swan Data Video Annotation

This project annotates an MP4 video by detecting faces and labelling known
Harry Potter characters using reference face images.

## Quick start

Create and activate a virtual environment, then install the dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run the annotator:

```bash
python annotate_video.py --input input/nimbus.mp4 --refs refs --output annotated.mp4
```

See [docs](./docs/README.md) for setup, usage, reference image guidance,
troubleshooting, and implementation notes.
