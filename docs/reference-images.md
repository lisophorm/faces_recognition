# Reference Images

The recogniser needs clear reference images for each character.

Create this folder structure:

```text
refs/
  harry_potter/
    harry_1.jpg
    harry_2.jpg
  hermione_granger/
    hermione_1.jpg
  prof_mcgonagall/
    mcgonagall_1.jpg
  prof_severus_snape/
    snape_1.jpg
  ron_weasley/
    ron_1.jpg
```

## Tips

Use images where:

- the face is visible and not heavily blurred
- the face is reasonably front-facing
- lighting is clear
- only one main face is present
- the image reflects the character appearance in the input video

More than one reference image per character usually improves results.

## Character folders and labels

Use filesystem-friendly folder names. The script maps them to display labels in the output video:

- `harry_potter` -> `Harry Potter`
- `hermione_granger` -> `Hermione Granger`
- `prof_mcgonagall` -> `Prof. McGonagall`
- `prof_severus_snape` -> `Prof. Severus Snape`
- `ron_weasley` -> `Ron Weasley`
