# FLARE24

Local dataset engineering workspace for MICCAI FLARE 2024 / FLARE-MedFM tasks.

Primary references:

```text
https://flare-medfm.github.io/
https://www.codabench.org/competitions/2319/
https://www.codabench.org/competitions/2320/
https://www.codabench.org/competitions/2296/
```

## Directory Roles

- `data/raw/huggingface/`: original gated Hugging Face snapshots.
- `data/raw/extracted/`: unpacked archives copied from raw snapshots.
- `data/processed/`: derived outputs.
- `data/manifests/`: download status, speed tests, and sample manifests.
- `data/splits/`: downstream split definitions.
- `scripts/`: download, proxy, unpacking, verification, and manifest scripts.
- `src/flare24_dataset/`: lightweight Python path interface.
- `logs/`: runtime logs and pid files.
- `cache/`: local download/proxy cache.
- `secrets/`: local credentials; do not commit.

## Tasks

| Task | Name | Source repo |
| --- | --- | --- |
| `task1` | Pan-cancer segmentation in CT scans | `FLARE-MedFM/FLARE-Task1-Pancancer` |
| `task2` | Abdominal CT Organ Segmentation on Laptop | `FLARE-MedFM/FLARE-Task2-LaptopSeg` |
| `task3` | Unsupervised domain adaptation for MRI/PET abdominal organ segmentation | `FLARE-MedFM/FLARE-Task3-DomainAdaption` |

## Common Commands

Start resumable background download:

```bash
bash scripts/start_download.sh
```

Check status:

```bash
bash scripts/status_download.sh
```

Unpack nested label archives:

```bash
python scripts/unpack_archives.py
```

Verify layout:

```bash
python scripts/verify.py
```

Build manifest:

```bash
python scripts/build_manifest.py
```

## Python Interface

```python
from pathlib import Path
from flare24_dataset import FLARE24Index, load_nifti

root = Path("/home/jjzhu/Data/datasets/FLARE24")
index = FLARE24Index(root, task="task2", complete_only=True)
case = index[0].require_complete()

image = load_nifti(case.image)
```
