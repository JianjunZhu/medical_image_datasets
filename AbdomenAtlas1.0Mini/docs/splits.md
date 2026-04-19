# Splits

Splits are generated from complete cases in `data/manifests/manifest.csv`.

Default command:

```bash
python scripts/make_splits.py --ratios 0.8,0.1,0.1 --seed 20260419
```

Outputs:

- `data/splits/default/train.txt`
- `data/splits/default/val.txt`
- `data/splits/default/test.txt`
- `data/splits/default/split.csv`
- `data/splits/default/split.yaml`

The split generator shuffles case IDs with a fixed seed, slices by ratio, and
sorts each output split for readable diffs.
