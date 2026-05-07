# Troubleshooting

## The script is slow

RetinaFace is accurate but slow. Increase the recognition interval:

```bash
python annotate_video.py --input input/nimbus.mp4 --refs refs --output annotated.mp4 --recognition-interval 10
```

## Faces are detected but labels are wrong

Use a stricter threshold:

```bash
python annotate_video.py --input input/nimbus.mp4 --refs refs --output annotated.mp4 --threshold 0.25
```

Also improve the reference images. Wrong labels usually mean the reference set
is too weak or the threshold is too permissive.

## Known characters are labelled Unknown

Use a more permissive threshold:

```bash
python annotate_video.py --input input/nimbus.mp4 --refs refs --output annotated.mp4 --threshold 0.40
```

Also add more reference images for the missed character.

## No faces are found in reference images

Use clearer images. Avoid profile shots, dark images, small faces, and images
with many people.

## The script exits with `Error: ...`

The script uses concise error messages for common setup and input problems,
such as a missing input video, missing reference folder, invalid frame interval,
or unusable output path. Fix the path or option named in the message and run the
command again.

## Output video does not play

The script writes MP4 using OpenCV's `mp4v` codec. If a player has trouble
opening it, re-encode with ffmpeg:

```bash
ffmpeg -i annotated.mp4 -vcodec libx264 -pix_fmt yuv420p annotated_h264.mp4
```
