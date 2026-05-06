# Approach

The solution uses DeepFace to perform two tasks:

1. Detect faces in each sampled video frame.
2. Compare each detected face with known character reference images.

## Detection

The default detector is RetinaFace because it usually performs well on film footage with varied lighting, angles, and partial occlusion.

## Recognition

The script uses the Facenet512 embedding model. Each reference image is converted into an embedding. For each detected face in the video, the script calculates a new embedding and compares it with all reference embeddings using cosine distance.

The closest character match is selected when the distance is below the configured threshold. Otherwise, the face is labelled `Unknown`.

## Performance trade-off

Running detection and recognition on every frame can be slow. By default, the script recognises every few frames and reuses the last annotations in between. This gives reasonable output while keeping runtime manageable.

For best accuracy, use:

```bash
--recognition-interval 1
```

For faster processing, use a higher value, such as:

```bash
--recognition-interval 10
```
