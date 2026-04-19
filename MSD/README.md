# MSD

Local dataset engineering workspace for the Medical Segmentation Decathlon
Google Drive release.

Primary source:

```text
https://registry.opendata.aws/msd/
https://msd-for-monai.s3-us-west-2.amazonaws.com/
```

Original Google Drive source:

```text
https://drive.google.com/drive/folders/1HqEgzS8BV2c7xYNrZdEAnrHk7osJJ--2
```

## Directory Roles

- `data/raw/archives/`: downloaded original archives or files.
- `data/raw/extracted/`: unpacked MSD task directories.
- `data/processed/`: derived data.
- `data/manifests/`: download status, archive indexes, and sample manifests.
- `data/splits/`: downstream split files.
- `scripts/`: download, background control, unpacking, verification, and manifest scripts.
- `src/msd/`: lightweight Python path interface.
- `logs/`: runtime logs and pid files.
- `cache/`: local cache.

## Background Download

Start the download in the background:

```bash
bash scripts/start_download.sh
```

Check status:

```bash
bash scripts/status_download.sh
```

Stop the download without deleting partial files:

```bash
bash scripts/stop_download.sh
```

The download uses the local proxy by default:

```text
PROXY_HOST=127.0.0.1:17890
USE_PROXY=1
```

It writes files into `data/raw/archives/`, logs into `logs/download.log`, and
exits automatically after completion or after `MAX_RETRIES` failed attempts.

Default tool is S3 curl:

```bash
DOWNLOAD_TOOL=s3curl bash scripts/start_download.sh
```

Google Drive fallback:

```bash
DOWNLOAD_TOOL=gdown bash scripts/start_download.sh
```

To disable proxy explicitly:

```bash
USE_PROXY=0 bash scripts/start_download.sh
```

To use `rclone` instead:

```bash
DOWNLOAD_TOOL=rclone RCLONE_REMOTE=gdrive bash scripts/start_download.sh
```

## After Download

Unpack archives:

```bash
python scripts/unpack_archives.py
```

Verify unpacked tasks:

```bash
python scripts/verify.py
```

Build a sample manifest:

```bash
python scripts/build_manifest.py
```

## Python Interface

Use the path-level index after extraction and manifest generation:

```python
from pathlib import Path
from msd import MSDIndex, load_nifti

root = Path("/home/jjzhu/Data/datasets/MSD")
index = MSDIndex(root, complete_only=True)

print(len(index))
print(index.tasks())
print(index.splits())

case = index.get("Task02_Heart", "la_003", split="train").require_complete()
print(case.image)
print(case.label)

image = load_nifti(case.image)
label = load_nifti(case.label)
```

Common filters:

```python
train = MSDIndex(root, split="train", complete_only=True)
heart = MSDIndex(root, task="Task02_Heart")
records = [record.to_dict(root) for record in heart]
metadata = heart.task_metadata("Task02_Heart")
```

## Training Dataset Adapters

PyTorch-style map dataset:

```python
from pathlib import Path
from torch.utils.data import DataLoader
from msd import MSDTorchDataset

root = Path("/home/jjzhu/Data/datasets/MSD")
dataset = MSDTorchDataset(root, task="Task03_Liver", split="train")
loader = DataLoader(dataset, batch_size=2, shuffle=True, num_workers=4)

batch = next(iter(loader))
print(batch["image"])
print(batch["label"])
```

MONAI-style dataset:

```python
from pathlib import Path
from monai.transforms import Compose, LoadImaged, EnsureChannelFirstd
from msd import build_monai_dataset

root = Path("/home/jjzhu/Data/datasets/MSD")
transforms = Compose([
    LoadImaged(keys=["image", "label"]),
    EnsureChannelFirstd(keys=["image", "label"]),
])

dataset = build_monai_dataset(
    root,
    task="Task03_Liver",
    split="train",
    transform=transforms,
)
sample = dataset[0]
```
