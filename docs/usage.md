# Usage

Run the annotator from the project root:

```bash
python annotate_video.py --input input/nimbus.mp4 --refs refs --output annotated.mp4
```

## Common options

Process only a small number of frames for testing:

```bash
python annotate_video.py --input input/nimbus.mp4 --refs refs --output test_annotated.mp4 --max-frames 200
```

Run recognition every frame for better accuracy but slower processing:

```bash
python annotate_video.py --input input/nimbus.mp4 --refs refs --output annotated.mp4 --recognition-interval 1
```

Use stricter matching:

```bash
python annotate_video.py --input input/nimbus.mp4 --refs refs --output annotated.mp4 --threshold 0.25
```

Use more permissive matching:

```bash
python annotate_video.py --input input/nimbus.mp4 --refs refs --output annotated.mp4 --threshold 0.40
```

## Output

The output is an MP4 file with:

- bounding boxes around detected faces
- character names where recognition is confident enough
- `Unknown` for faces that do not match the reference set
