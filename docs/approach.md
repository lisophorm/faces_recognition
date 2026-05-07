# Approach

The solution uses DeepFace to perform two tasks:

1. Detect faces in each sampled video frame.
2. Compare each detected face with known character reference images.

## Detection

The default detector is RetinaFace because it usually performs well on film
footage with varied lighting, angles, and partial occlusion.

## Recognition

The script uses the Facenet512 embedding model. Each character folder is scanned
as a gallery, and every usable reference image is converted into an embedding.
The folder also gets a prototype embedding computed from the full set.

For each detected face in the video, the script calculates a new embedding and
compares it against the whole gallery using cosine distance. Detected video
crops are kept in BGR order before embedding so they follow the same DeepFace
ndarray convention as reference images loaded from disk.

The closest character match is selected when the distance is below the
configured threshold. Otherwise, the face is labelled `Unknown`.

## Performance trade-off

Running detection and recognition on every frame can be slow. By default, the
script recognises every few frames and reuses the last annotations in between.
You can control this either with `--recognition-interval` or the more intuitive
`--frame-skip` setting, where `--frame-skip 4` means the script processes one
frame and reuses its labels for the next four.

If you want a smaller output file or less video encoding work, use
`--output-frame-skip` to write only every Nth frame while keeping the output
duration aligned by lowering the written FPS.

For best accuracy, use:

```bash
--recognition-interval 1
```

For faster processing, use a higher value, such as:

```bash
--recognition-interval 10
```
