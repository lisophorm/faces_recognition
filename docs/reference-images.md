# Reference Images

The recogniser scans each character folder and uses every supported image it
finds there.

Create this folder structure:

```text
refs/
  harry_potter/
    harry_1.jpg
    harry_2.jpg
  hermione_granger/
    hermione_1.jpg
    hermione_2.jpg
  prof_mcgonagall/
    mcgonagall_1.jpg
    mcgonagall_2.jpg
  prof_severus_snape/
    snape_1.jpg
  ron_weasley/
    ron_1.jpg
    ron_2.jpg
```

The loader walks each character folder recursively, so you can keep images
directly in the folder or inside subfolders if you want to group poses,
lighting setups, or video stills.

## Tips

Use images where:

- the face is visible and not heavily blurred
- the face is reasonably front-facing, but a mix of angles helps the gallery
- lighting is clear
- only one main face is present
- the image reflects the character appearance in the input video

More than one reference image per character improves results. A small gallery
with frontal, side, and slightly different expressions is better than a single
JPEG.

## Character folders and labels

Use filesystem-friendly folder names. The script maps them to display labels in
the output video:

- `harry_potter` -> `Harry Potter`
- `hermione_granger` -> `Hermione Granger`
- `prof_mcgonagall` -> `Prof. McGonagall`
- `prof_severus_snape` -> `Prof. Severus Snape`
- `ron_weasley` -> `Ron Weasley`
