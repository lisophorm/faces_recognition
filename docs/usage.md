# Usage

Run the annotator from the project root:

```bash
python annotate_video.py --input input/nimbus.mp4 --refs refs --output output/annotated.mp4
```

## Common options

Process only a small number of frames for testing:

```bash
python annotate_video.py --input input/nimbus.mp4 --refs refs --output output/test_annotated.mp4 --max-frames 50
```

Run recognition every frame for better accuracy but slower processing:

```bash
python annotate_video.py --input input/nimbus.mp4 --refs refs --output output/annotated.mp4 --recognition-interval 1
```

Skip four frames between recognition passes:

```bash
python annotate_video.py --input input/nimbus.mp4 --refs refs --output output/annotated.mp4 --frame-skip 4
```

`--frame-skip 4` is equivalent to `--recognition-interval 5`.

Add more images under each character folder if recognition is still too pose-sensitive. The loader uses every supported image it finds under `refs/<character>/`.

Write every fifth frame to the output video:

```bash
python annotate_video.py --input input/nimbus.mp4 --refs refs --output output/annotated.mp4 --output-frame-skip 4
```

`--output-frame-skip 4` keeps the video duration roughly the same by writing at a lower output FPS.

Use stricter matching:

```bash
python annotate_video.py --input input/nimbus.mp4 --refs refs --output output/annotated.mp4 --threshold 0.25
```

Use more permissive matching:

```bash
python annotate_video.py --input input/nimbus.mp4 --refs refs --output output/annotated.mp4 --threshold 0.40
```

Filter out low-confidence detector results:

```bash
python annotate_video.py --input input/nimbus.mp4 --refs refs --output output/annotated.mp4 --min-face-confidence 0.90
```

Show cosine distances on the video for debugging and threshold tuning:

```bash
python annotate_video.py --input input/nimbus.mp4 --refs refs --output output/annotated_debug.mp4 --show-distance
```

## Defaults

- detector backend: `retinaface`
- embedding model: `Facenet512`
- recognition interval: every 5 frames
- matching threshold: `0.35`
- minimum face confidence: `0.0`, which keeps positive-confidence detections and drops DeepFace's no-face fallback
- output frame skip: `0`, meaning every processed frame is written
- distance display: off by default for cleaner final output

## Output

The output is an MP4 file with:

- bounding boxes around detected faces
- character names where recognition is confident enough
- `Unknown` for faces that do not match the reference set
