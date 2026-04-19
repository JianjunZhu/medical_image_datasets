# Structure

This workspace separates dataset content from engineering support files.

## Raw Layout

Raw cases live under `data/raw/`:

```text
AbdomenAtlas1.0Mini/
  data/raw/
    BDMAP_00000001/
    BDMAP_00000002/
    ...
```

Each case contains one CT volume, one combined label volume, and nine individual
organ masks under `segmentations/`.
Code should use `data/manifests/manifest.csv` or the Python index in
`src/abdomenatlas_mini` instead of hard-coding case paths.

## Integrity Checks

Use `scripts/verify.py` for quick structural validation:

```bash
python scripts/verify.py
```

Add `--deep-gzip` when you want to open every `.nii.gz` gzip stream. That is
slower, but it can catch truncated files.
