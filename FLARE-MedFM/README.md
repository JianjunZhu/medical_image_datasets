# FLARE-MedFM

Local dataset engineering workspace for the `FLARE-MedFM` Hugging Face dataset
collection.

Primary references:

```text
https://huggingface.co/FLARE-MedFM
https://flare-medfm.github.io/
```

## Directory Roles

- `data/raw/huggingface/`: original gated Hugging Face snapshots.
- `data/raw/extracted/`: unpacked archives copied from raw snapshots.
- `data/processed/`: derived outputs.
- `data/manifests/`: download status, speed tests, and sample manifests.
- `data/splits/`: downstream split definitions.
- `scripts/`: download, proxy, unpacking, verification, and manifest scripts.
- `src/flare_medfm_dataset/`: lightweight Python path interface.
- `logs/`: runtime logs and pid files.
- `cache/`: local download/proxy cache.
- `secrets/`: local credentials; do not commit.

## Datasets

| Key | Hugging Face repo |
| --- | --- |
| `pancancer_ct_seg` | `FLARE-MedFM/PancancerCTSeg` |
| `task2_laptop_seg` | `FLARE-MedFM/FLARE-Task2-LaptopSeg` |
| `task3_domain_adaptation` | `FLARE-MedFM/FLARE-Task3-DomainAdaption` |
| `task4_ct_fm` | `FLARE-MedFM/FLARE-Task4-CT-FM` |
| `task4_mri_fm` | `FLARE-MedFM/FLARE-Task4-MRI-FM` |
| `flare26_mllm_3d` | `FLARE-MedFM/FLARE26-MLLM-3D` |
| `task5_mllm_2d` | `FLARE-MedFM/FLARE-Task5-MLLM-2D` |
| `task6_medagent` | `FLARE-MedFM/FLARE-Task6-MedAgent` |
| `task1_recist_to_3d` | `FLARE-MedFM/FLARE-Task1-PancancerRECIST-to-3D` |
| `task1_recist_to_3d_dockers` | `FLARE-MedFM/FLARE-Task1-PancancerRECIST-to-3D-Dockers` |

## Common Commands

Start resumable background download for all datasets:

```bash
bash scripts/start_download.sh
```

Download selected datasets:

```bash
FLARE_MEDFM_DATASETS=task2_laptop_seg bash scripts/start_download.sh
FLARE_MEDFM_DATASETS=task4_ct_fm,task4_mri_fm bash scripts/start_download.sh
```

Check status:

```bash
bash scripts/status_download.sh
```

Unpack nested archives:

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
from flare_medfm_dataset import FLAREMedFMIndex, load_nifti

root = Path("/home/jjzhu/Data/datasets/FLARE-MedFM")
index = FLAREMedFMIndex(root, dataset="task2_laptop_seg", complete_only=True)
case = index[0].require_complete()

image = load_nifti(case.image)
```
