# Download

The local downloader uses Zenodo file URLs with `curl`.

Default behavior:

- download CT and MRI archives;
- direct network access, `USE_PROXY=0`;
- resumable downloads via `curl --continue-at -`;
- retries on transient network errors;
- status written to `data/manifests/download_status.json`;
- logs written to `logs/download.log`.

Start:

```bash
bash scripts/start_download.sh
```

Select subsets:

```bash
TOTAL_SEGMENTATOR_SUBSETS=ct bash scripts/start_download.sh
TOTAL_SEGMENTATOR_SUBSETS=mri bash scripts/start_download.sh
TOTAL_SEGMENTATOR_SUBSETS=ct_small bash scripts/start_download.sh
TOTAL_SEGMENTATOR_SUBSETS=ct,mri bash scripts/start_download.sh
```

Use proxy:

```bash
USE_PROXY=1 PROXY_HOST=127.0.0.1:17890 bash scripts/start_download.sh
```
