# TotalSegmentator

Local dataset engineering workspace for the TotalSegmentator CT and MRI datasets.

Official project:

```text
https://github.com/wasserth/TotalSegmentator
```

Official datasets:

```text
CT v2.0.1:  https://zenodo.org/records/10047292
MRI v2.0.0: https://zenodo.org/records/14710732
```

## Directory Roles

- `data/raw/archives/`: downloaded original zip archives.
- `data/raw/extracted/`: unpacked CT/MRI dataset directories.
- `data/processed/`: derived data.
- `data/manifests/`: download status and sample manifests.
- `data/splits/`: downstream split files.
- `scripts/`: download, background control, unpacking, verification, and manifest scripts.
- `src/totalsegmentator_dataset/`: lightweight Python path interface.
- `logs/`: runtime logs and pid files.
- `cache/`: local cache.

## Dataset Summary

| Dataset | Record | Version | Subjects | Size | License |
| --- | --- | --- | ---: | ---: | --- |
| CT | `10047292` | `2.0.1` | 1228 | 23.6 GB | CC BY 4.0 |
| MRI | `14710732` | `2.0.0` | 616 | 5.1 GB | CC BY-NC-SA 2.0 |
| CT small | `10047263` | `2.0.1` | 102 | 3.2 GB | See Zenodo record |

## Background Download

Download CT and MRI in the background:

```bash
bash scripts/start_download.sh
```

Download only one subset:

```bash
TOTAL_SEGMENTATOR_SUBSETS=ct bash scripts/start_download.sh
TOTAL_SEGMENTATOR_SUBSETS=mri bash scripts/start_download.sh
TOTAL_SEGMENTATOR_SUBSETS=ct_small bash scripts/start_download.sh
```

Check status:

```bash
bash scripts/status_download.sh
```

Stop the background process without deleting partial files:

```bash
bash scripts/stop_download.sh
```

The downloader uses direct network access by default:

```text
USE_PROXY=0
```

To use a local HTTP proxy:

```bash
USE_PROXY=1 PROXY_HOST=127.0.0.1:17890 bash scripts/start_download.sh
```

## After Download

Unpack archives:

```bash
python scripts/unpack_archives.py
```

Verify downloaded archives and extracted structure:

```bash
python scripts/verify.py
```

Build a sample manifest:

```bash
python scripts/build_manifest.py
```
