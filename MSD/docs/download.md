# Download

Download is controlled by four scripts:

- `scripts/download.sh`: foreground download implementation.
- `scripts/start_download.sh`: start download in the background.
- `scripts/status_download.sh`: inspect process, status file, archive size, and logs.
- `scripts/stop_download.sh`: stop the background download without deleting partial files.

## Start

```bash
bash scripts/start_download.sh
```

The script writes the process ID to `logs/download.pid` and appends logs to
`logs/download.log`.

## Status

```bash
bash scripts/status_download.sh
```

## Stop

```bash
bash scripts/stop_download.sh
```

## Proxy

`scripts/download.sh` uses a local proxy by default:

```text
USE_PROXY=1
PROXY_HOST=127.0.0.1:17890
```

It exports `http_proxy`, `https_proxy`, `HTTP_PROXY`, `HTTPS_PROXY`,
`all_proxy`, and `ALL_PROXY` before invoking the download tool.

To disable proxy:

```bash
USE_PROXY=0 bash scripts/start_download.sh
```

## Resume

Default `s3curl` mode downloads the AWS Open Data S3 mirror:

```text
https://msd-for-monai.s3-us-west-2.amazonaws.com/Task01_BrainTumour.tar
...
https://msd-for-monai.s3-us-west-2.amazonaws.com/Task10_Colon.tar
```

It uses `curl --location --continue-at -`, so partially downloaded tar files can
resume. `gdown` and `rclone` remain available as fallback tools.

## Completion

When the download command exits successfully, `scripts/download.sh` writes
`completed` to `data/manifests/download_status.json` and exits. Because it is a
normal background process, it ends automatically after completion.
