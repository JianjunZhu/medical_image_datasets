# AbdomenAtlas1.0Mini

Local dataset engineering workspace for `AbdomenAtlas/AbdomenAtlas1.0Mini`.

The raw case directories live under `data/raw/`:

```text
data/raw/
  BDMAP_00000001/
    ct.nii.gz
    combined_labels.nii.gz
    segmentations/
      aorta.nii.gz
      gall_bladder.nii.gz
      kidney_left.nii.gz
      kidney_right.nii.gz
      liver.nii.gz
      pancreas.nii.gz
      postcava.nii.gz
      spleen.nii.gz
      stomach.nii.gz
```

## Directory Roles

- `data/raw/BDMAP_*`: raw case directories from Hugging Face.
- `scripts/`: download, monitoring, manifest, and future processing scripts.
- `src/abdomenatlas_mini/`: lightweight path-level dataset interface.
- `docs/`: dataset source, structure, labels, and preprocessing notes.
- `data/manifests/`: generated sample indexes.
- `data/raw/`: original downloaded case data.
- `data/processed/`: reserved for derived data.
- `data/splits/`: train/val/test split files.
- `logs/`: runtime logs and pid files.
- `cache/`: downloader cache.
- `secrets/`: local credentials; do not commit or share.

## Common Commands

Build or refresh the manifest:

```bash
python scripts/build_manifest.py
```

Verify the file layout:

```bash
python scripts/verify.py
```

Create deterministic train/validation/test splits:

```bash
python scripts/make_splits.py --ratios 0.8,0.1,0.1 --seed 20260419
```

Resume download:

```bash
bash scripts/download.sh >> logs/download.log 2>&1
```

Monitor storage progress:

```bash
bash scripts/monitor_storage_progress.sh >> logs/storage_progress.log 2>&1
```

The download script reads `HF_TOKEN` first, then falls back to
`secrets/hf_token`. It also accepts `HF_TOKEN_FILE`, `PROXY_HOST`, `CONDA_ENV`,
and `CONDA_PROFILE`.

## Python Interface

```python
from abdomenatlas_mini import AbdomenAtlasMiniIndex

index = AbdomenAtlasMiniIndex("/home/jjzhu/Data/datasets/AbdomenAtlas1.0Mini")
case = index.get("BDMAP_00000001").require_complete()
print(case.ct)
print(case.segmentations["liver"])
```

For split-specific indexing:

```python
train = AbdomenAtlasMiniIndex.from_split(
    "/home/jjzhu/Data/datasets/AbdomenAtlas1.0Mini",
    "/home/jjzhu/Data/datasets/AbdomenAtlas1.0Mini/data/splits/default/train.txt",
)
```
