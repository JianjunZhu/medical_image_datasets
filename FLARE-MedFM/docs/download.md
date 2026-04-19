# Download

FLARE-MedFM datasets are gated Hugging Face datasets. First request/accept
access on Hugging Face, then provide a token:

```bash
export HF_TOKEN=...
# or
mkdir -p secrets
printf '%s' "$HF_TOKEN" > secrets/hf_token
```

Start all 10 datasets in the background:

```bash
bash scripts/start_download.sh
```

Download selected datasets:

```bash
FLARE_MEDFM_DATASETS=task2_laptop_seg bash scripts/start_download.sh
FLARE_MEDFM_DATASETS=task4_ct_fm,task4_mri_fm bash scripts/start_download.sh
FLARE_MEDFM_DATASETS=FLARE-MedFM/PancancerCTSeg bash scripts/start_download.sh
```

Check status:

```bash
bash scripts/status_download.sh
```

Stop without deleting partial files:

```bash
bash scripts/stop_download.sh
```

## Proxy Strategy

Direct mode is the default:

```bash
USE_PROXY=0 bash scripts/start_download.sh
```

To use an existing proxy:

```bash
USE_PROXY=1 PROXY_HOST=127.0.0.1:7890 bash scripts/start_download.sh
```

For large downloads, prefer a dedicated background proxy if available. Test
direct mode and low-traffic-multiplier nodes against Hugging Face/Xet endpoints,
keep the fastest stable node for the download, and automatically close the
dedicated proxy after download completion.

```bash
bash scripts/speedtest_proxy.sh
AUTO_STOP_PROXY=1 USE_PROXY=1 PROXY_HOST=127.0.0.1:17890 bash scripts/start_download.sh
```
