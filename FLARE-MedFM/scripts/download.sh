#!/usr/bin/env bash

set -u

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
dataset_root="$(cd "${script_dir}/.." && pwd)"
raw_dir="${RAW_DIR:-${dataset_root}/data/raw/huggingface}"
manifest_dir="${dataset_root}/data/manifests"
status_file="${manifest_dir}/download_status.json"
default_datasets="pancancer_ct_seg,task2_laptop_seg,task3_domain_adaptation,task4_ct_fm,task4_mri_fm,flare26_mllm_3d,task5_mllm_2d,task6_medagent,task1_recist_to_3d,task1_recist_to_3d_dockers"
datasets="${FLARE_MEDFM_DATASETS:-${default_datasets}}"
max_retries="${MAX_RETRIES:-20}"
retry_seconds="${RETRY_SECONDS:-60}"
hub_download_timeout="${HF_HUB_DOWNLOAD_TIMEOUT:-120}"
hub_etag_timeout="${HF_HUB_ETAG_TIMEOUT:-60}"
hub_max_workers="${HF_HUB_MAX_WORKERS:-4}"
use_proxy="${USE_PROXY:-0}"
proxy_host="${PROXY_HOST:-127.0.0.1:17890}"
auto_stop_proxy="${AUTO_STOP_PROXY:-0}"
dedicated_proxy_pid_file="${DEDICATED_PROXY_PID_FILE:-${dataset_root}/logs/download_proxy.pid}"

mkdir -p "${raw_dir}" "${manifest_dir}" "${dataset_root}/logs"

repo_for_dataset() {
  if printf '%s' "$1" | grep -q '/'; then
    printf '%s\n' "$1"
    return 0
  fi
  case "$1" in
    pancancer_ct_seg) printf '%s\n' "FLARE-MedFM/PancancerCTSeg" ;;
    task2_laptop_seg) printf '%s\n' "FLARE-MedFM/FLARE-Task2-LaptopSeg" ;;
    task3_domain_adaptation) printf '%s\n' "FLARE-MedFM/FLARE-Task3-DomainAdaption" ;;
    task4_ct_fm) printf '%s\n' "FLARE-MedFM/FLARE-Task4-CT-FM" ;;
    task4_mri_fm) printf '%s\n' "FLARE-MedFM/FLARE-Task4-MRI-FM" ;;
    flare26_mllm_3d) printf '%s\n' "FLARE-MedFM/FLARE26-MLLM-3D" ;;
    task5_mllm_2d) printf '%s\n' "FLARE-MedFM/FLARE-Task5-MLLM-2D" ;;
    task6_medagent) printf '%s\n' "FLARE-MedFM/FLARE-Task6-MedAgent" ;;
    task1_recist_to_3d) printf '%s\n' "FLARE-MedFM/FLARE-Task1-PancancerRECIST-to-3D" ;;
    task1_recist_to_3d_dockers) printf '%s\n' "FLARE-MedFM/FLARE-Task1-PancancerRECIST-to-3D-Dockers" ;;
    *) return 1 ;;
  esac
}

dir_for_repo() {
  printf '%s\n' "${raw_dir}/$(basename "$1")"
}

load_token() {
  if [ -n "${HF_TOKEN:-}" ]; then
    return 0
  fi
  if [ -f "${HF_TOKEN_FILE:-${dataset_root}/secrets/hf_token}" ]; then
    HF_TOKEN="$(tr -d '[:space:]' < "${HF_TOKEN_FILE:-${dataset_root}/secrets/hf_token}")"
    export HF_TOKEN
    return 0
  fi
  printf '[%s] missing HF_TOKEN or secrets/hf_token for gated datasets\n' "$(date '+%Y-%m-%d %H:%M:%S %Z')" >&2
  return 2
}

configure_network() {
  export HF_HUB_DOWNLOAD_TIMEOUT="${hub_download_timeout}"
  export HF_HUB_ETAG_TIMEOUT="${hub_etag_timeout}"
  export HF_HUB_MAX_WORKERS="${hub_max_workers}"
  if [ "${use_proxy}" = "1" ] || [ "${use_proxy}" = "true" ]; then
    export http_proxy="http://${proxy_host}"
    export https_proxy="http://${proxy_host}"
    export HTTP_PROXY="http://${proxy_host}"
    export HTTPS_PROXY="http://${proxy_host}"
    export NO_PROXY="${NO_PROXY:-localhost,127.0.0.1}"
    export no_proxy="${no_proxy:-localhost,127.0.0.1}"
  else
    unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY
  fi
}

downloaded_bytes() {
  find "${raw_dir}" -type f -printf '%s\n' 2>/dev/null | awk '{s+=$1} END {print s+0}'
}

downloaded_files() {
  find "${raw_dir}" -type f 2>/dev/null | wc -l
}

write_status() {
  local status="$1"
  local active_dataset="${2:-}"
  local active_repo="${3:-}"
  local finished_at="${4:-null}"
  local now
  now="$(date --iso-8601=seconds)"
  if [ "${finished_at}" != "null" ]; then
    finished_at="\"${finished_at}\""
  fi
  cat > "${status_file}" <<EOF
{
  "dataset": "FLARE-MedFM",
  "datasets": "${datasets}",
  "active_dataset": "${active_dataset}",
  "active_repo": "${active_repo}",
  "download_dir": "data/raw/huggingface",
  "use_proxy": "${use_proxy}",
  "proxy_host": "${proxy_host}",
  "auto_stop_proxy": "${auto_stop_proxy}",
  "dedicated_proxy_pid_file": "${dedicated_proxy_pid_file}",
  "max_retries": ${max_retries},
  "retry_seconds": ${retry_seconds},
  "hf_hub_download_timeout": ${hub_download_timeout},
  "hf_hub_etag_timeout": ${hub_etag_timeout},
  "hf_hub_max_workers": ${hub_max_workers},
  "pid": $$,
  "status": "${status}",
  "last_checked_at": "${now}",
  "finished_at": ${finished_at},
  "downloaded_files": $(downloaded_files),
  "downloaded_bytes": $(downloaded_bytes)
}
EOF
}

cleanup_proxy() {
  if [ "${auto_stop_proxy}" = "1" ] || [ "${auto_stop_proxy}" = "true" ]; then
    if [ -f "${dedicated_proxy_pid_file}" ]; then
      printf '[%s] auto stopping dedicated download proxy\n' "$(date '+%Y-%m-%d %H:%M:%S %Z')"
      bash "${script_dir}/stop_proxy.sh" || true
    fi
  fi
}

download_one() {
  local dataset_key="$1"
  local repo local_dir
  repo="$(repo_for_dataset "${dataset_key}")" || {
    printf '[%s] unsupported dataset=%s\n' "$(date '+%Y-%m-%d %H:%M:%S %Z')" "${dataset_key}" >&2
    return 2
  }
  local_dir="$(dir_for_repo "${repo}")"
  write_status "running" "${dataset_key}" "${repo}"
  printf '[%s] downloading dataset=%s repo=%s local_dir=%s\n' \
    "$(date '+%Y-%m-%d %H:%M:%S %Z')" "${dataset_key}" "${repo}" "${local_dir}"
  python - "${repo}" "${local_dir}" <<'PY'
import os
import sys
from huggingface_hub import snapshot_download

repo_id = sys.argv[1]
local_dir = sys.argv[2]
token = os.environ.get("HF_TOKEN")

snapshot_download(
    repo_id=repo_id,
    repo_type="dataset",
    local_dir=local_dir,
    local_dir_use_symlinks=False,
    resume_download=True,
    token=token,
    max_workers=int(os.environ.get("HF_HUB_MAX_WORKERS", "4")),
)
PY
}

load_token || {
  write_status "failed" "" "" "$(date --iso-8601=seconds)"
  exit 2
}
configure_network
write_status "running"
trap cleanup_proxy EXIT

attempt=1
while [ "${attempt}" -le "${max_retries}" ]; do
  printf '[%s] download attempt %s/%s tasks=%s\n' \
    "$(date '+%Y-%m-%d %H:%M:%S %Z')" "${attempt}" "${max_retries}" "${datasets}"
  printf '[%s] network use_proxy=%s proxy_host=%s\n' \
    "$(date '+%Y-%m-%d %H:%M:%S %Z')" "${use_proxy}" "${proxy_host}"
  printf '[%s] retry max_retries=%s retry_seconds=%s hf_timeout=%s hf_etag_timeout=%s hf_max_workers=%s\n' \
    "$(date '+%Y-%m-%d %H:%M:%S %Z')" "${max_retries}" "${retry_seconds}" \
    "${hub_download_timeout}" "${hub_etag_timeout}" "${hub_max_workers}"
  status=0
  IFS=',' read -r -a dataset_array <<EOF
${datasets}
EOF
  for dataset_key in "${dataset_array[@]}"; do
    dataset_key="$(printf '%s' "${dataset_key}" | tr -d '[:space:]')"
    [ -n "${dataset_key}" ] || continue
    download_one "${dataset_key}" || {
      status=$?
      break
    }
  done
  if [ "${status}" -eq 0 ]; then
    printf '[%s] download completed\n' "$(date '+%Y-%m-%d %H:%M:%S %Z')"
    write_status "completed" "" "" "$(date --iso-8601=seconds)"
    exit 0
  fi
  printf '[%s] download failed with exit code %s\n' \
    "$(date '+%Y-%m-%d %H:%M:%S %Z')" "${status}"
  write_status "running"
  attempt=$((attempt + 1))
  if [ "${attempt}" -le "${max_retries}" ]; then
    sleep "${retry_seconds}"
  fi
done

printf '[%s] download failed after %s attempts\n' \
  "$(date '+%Y-%m-%d %H:%M:%S %Z')" "${max_retries}" >&2
write_status "failed" "" "" "$(date --iso-8601=seconds)"
exit 1
