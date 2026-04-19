---
name: medical-dataset-engineering
description: Use when organizing medical imaging datasets into reproducible dataset projects, including raw-data layout, resumable/background downloads, proxy handling, unpacking, verification, manifests, splits, and Python/PyTorch/MONAI data interfaces.
metadata:
  short-description: Build reproducible medical imaging dataset workspaces
---

# Medical Dataset Engineering

Use this skill when the user wants to create, reorganize, download, verify, document, or expose a medical imaging dataset under a `datasets/` engineering workspace.

## Target Project Shape

Each dataset should be a self-contained project:

```text
DatasetName/
  README.md
  dataset.yaml
  .gitignore
  docs/
    source.md
    structure.md
    download.md
  data/
    raw/
      README.md
      archives/      # original downloaded archives; ignored by git
      extracted/     # unpacked original data; ignored by git
    processed/       # derived data; ignored unless intentionally versioned
    manifests/       # generated indexes/status; commit only lightweight files
    splits/          # train/val/test split definitions
  scripts/
    download.sh
    start_download.sh
    status_download.sh
    stop_download.sh
    unpack_archives.py
    verify.py
    build_manifest.py
    make_splits.py   # when the dataset needs generated splits
  src/
    dataset_package/
      __init__.py
      dataset.py
      io.py
      torch_dataset.py
  logs/              # ignored by git
  cache/             # ignored by git
```

Keep original downloaded files under `data/raw/`. Never mix raw data with code, manifests, or derived data.

## Execution Workflow

1. Inspect existing files before editing:
   - Use `rg --files`, `find`, `du`, and existing README/docs/scripts.
   - Identify raw data, extracted data, generated files, logs, caches, and secrets.

2. Establish the project skeleton:
   - Create docs, scripts, `src/`, `data/raw`, `data/processed`, `data/manifests`, `data/splits`, `logs`, and `cache`.
   - Add `.gitignore` rules before downloading or moving large data.
   - Root `.gitignore` should exclude raw archives, extracted data, logs, caches, secrets, pid files, and temporary outputs.

3. Capture source truth:
   - Record official URLs, mirrors, versions, license, expected files, checksums, and known dataset sizes in `dataset.yaml` and `docs/source.md`.
   - If the source is unstable or current information matters, verify from official pages or primary sources.

4. Implement download rules:
   - Support resumable downloads (`curl -C -`, S3-aware curl, `gdown`, `rclone`, or source-specific tools).
   - Write into `data/raw/archives/` or source-equivalent raw paths.
   - Keep status in `data/manifests/download_status.json`.
   - Write logs and pid files into `logs/`.
   - Make downloads non-interactive and restartable.
   - Do not delete partial files on stop.

5. Background process contract:
   - `start_download.sh` starts with `nohup`/`setsid`, writes a pid, and exits immediately.
   - `status_download.sh` reports pid state, latest log lines, downloaded file sizes, and status JSON.
   - `stop_download.sh` terminates the download process without removing partial files.
   - The download process must exit automatically after success or terminal failure.

6. Network/proxy contract:
   - Default to direct connection unless the dataset source requires proxy.
   - Support `USE_PROXY=0|1` and `PROXY_HOST=host:port`.
   - Do not kill a shared proxy casually. If a dedicated proxy is needed, start it on separate ports, verify it works, then use it explicitly.
   - Before switching strategies, confirm whether active downloads are direct or proxied by checking process command lines, environment, logs, and status JSON.
   - For large downloads, prefer a dedicated background proxy process over the user's shared/default proxy.
   - Prefer low traffic multiplier nodes when available, then choose by measured throughput.
   - Batch test candidate nodes against the real dataset source or mirror, not only a generic connectivity URL.
   - Select the fastest stable node and bind only the download process to that proxy via explicit environment variables or downloader flags.
   - When the download finishes successfully or reaches terminal failure, automatically close the dedicated download proxy and leave the shared/default proxy untouched.

7. Dedicated proxy lifecycle:
   - Start the dedicated proxy in the background on non-conflicting ports such as HTTP `127.0.0.1:17890`, SOCKS `127.0.0.1:17891`, and controller `127.0.0.1:19091`.
   - Write proxy pid and logs under the dataset `logs/` or `cache/` directory.
   - Confirm the proxy is listening before using it.
   - Confirm the active node through the controller API when available.
   - Switch nodes through the controller API instead of restarting or killing the shared proxy.
   - Keep the dedicated proxy isolated from Codex's own network path when possible.
   - Stop only the dedicated proxy pid after the download completes, after checking that no active download process still depends on it.

8. Proxy speed testing:
   - Build a short candidate list from low traffic multiplier nodes first.
   - Test direct connection as a baseline.
   - For each candidate node, switch the proxy group, then run a bounded range request or timed partial download against the actual archive URL or mirror.
   - Record node name, proxy endpoint, source URL, bytes transferred, elapsed time, and approximate MB/s in a status file or log.
   - Prefer sustained dataset-source throughput over one-off latency.
   - If direct connection beats all proxy candidates, use direct mode.
   - If a mirror is slow across direct and proxy tests, treat the source/mirror path as the bottleneck and test another official mirror before over-tuning proxy nodes.

9. Unpack and normalize:
   - `unpack_archives.py` extracts into `data/raw/extracted/`.
   - Avoid overwriting existing extracted data unless explicitly requested.
   - Normalize avoidable nested directory duplication only when it is deterministic and documented.

10. Verify:
   - `verify.py` should check expected archive presence, optional checksums, extracted directory structure, required image/label files, and incomplete cases.
   - Output a clear machine-readable or compact text summary with `status=ok` only when the dataset is usable.

11. Build manifests:
   - `build_manifest.py` creates a lightweight CSV/JSONL index under `data/manifests/`.
   - Include stable identifiers, task/subset, split if known, image paths, label paths, modality, completeness, and source-relative paths.
   - Filter system metadata files such as macOS `._*`.

12. Build splits:
   - Use deterministic split generation with fixed seed and documented ratios.
   - Store `train.txt`, `val.txt`, `test.txt`, `split.csv`, and `split.yaml` when appropriate.
   - Prefer official splits when provided; otherwise document generated split rules.

13. Add data interfaces:
   - Provide a path-level index class similar to `DatasetIndex`.
   - Provide a case record class with typed paths and `require_complete()`.
   - Support filtering by task/subset/split and lookup by case id.
   - Provide lazy image loading helper such as `load_nifti(path)` with optional imports.
   - Add PyTorch-style and MONAI-style adapters only as optional dependency layers.

14. Validate and commit:
   - Run verify, manifest build, and lightweight import checks.
   - Confirm `git status --short` does not include raw archives, extracted data, logs, caches, or secrets.
   - Commit only code, docs, lightweight manifests/splits, and configuration.

## Interface Pattern

Expose a stable path-level API:

```python
from dataset_package import DatasetIndex, load_nifti

index = DatasetIndex(root, task="TaskName", split="train", complete_only=True)
case = index.get("case_id").require_complete()

image_path = case.image
label_path = case.label
image = load_nifti(image_path)
```

For training:

```python
from dataset_package import DatasetTorchDataset, build_monai_dataset

torch_dataset = DatasetTorchDataset(root, task="TaskName", split="train", transform=None)
monai_dataset = build_monai_dataset(root, task="TaskName", split="train", transform=transform)
```

Optional dependencies must fail with actionable messages, not import-time crashes for users who only need path indexing.

## Quality Bar

- Raw data is reproducible, resumable, and excluded from Git.
- Docs identify source, structure, license, and post-download steps.
- Verification is runnable after download and after extraction.
- Manifests and splits are deterministic and lightweight.
- Interfaces are path-first, lazy-loading, and training-friendly.
- Background downloads have clear start/status/stop behavior.
- Proxy use is explicit, observable, speed-tested, and isolated when possible.
- Dedicated download proxies are automatically cleaned up after the download is done.
