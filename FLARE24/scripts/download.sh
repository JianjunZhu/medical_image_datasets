#!/usr/bin/env bash

set -u

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
dataset_root="$(cd "${script_dir}/.." && pwd)"
raw_dir="${RAW_DIR:-${dataset_root}/data/raw/huggingface}"
manifest_dir="${dataset_root}/data/manifests"
status_file="${manifest_dir}/download_status.json"
tasks="${FLARE24_TASKS:-task1,task2,task3}"
max_retries="${MAX_RETRIES:-5}"
retry_seconds="${RETRY_SECONDS:-120}"
use_proxy="${USE_PROXY:-0}"
proxy_host="${PROXY_HOST:-127.0.0.1:17890}"
auto_stop_proxy="${AUTO_STOP_PROXY:-0}"
dedicated_proxy_pid_file="${DEDICATED_PROXY_PID_FILE:-${dataset_root}/logs/download_proxy.pid}"

mkdir -p "${raw_dir}" "${manifest_dir}" "${dataset_root}/logs"

repo_for_task() {
  case "$1" in
    task1) printf '%s\n' "FLARE-MedFM/FLARE-Task1-Pancancer" ;;
    task2) printf '%s\n' "FLARE-MedFM/FLARE-Task2-LaptopSeg" ;;
    task3) printf '%s\n' "FLARE-MedFM/FLARE-Task3-DomainAdaption" ;;
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
  local active_task="${2:-}"
  local active_repo="${3:-}"
  local finished_at="${4:-null}"
  local now
  now="$(date --iso-8601=seconds)"
  if [ "${finished_at}" != "null" ]; then
    finished_at="\"${finished_at}\""
  fi
  cat > "${status_file}" <<EOF
{
  "dataset": "FLARE24",
  "tasks": "${tasks}",
  "active_task": "${active_task}",
  "active_repo": "${active_repo}",
  "download_dir": "data/raw/huggingface",
  "use_proxy": "${use_proxy}",
  "proxy_host": "${proxy_host}",
  "auto_stop_proxy": "${auto_stop_proxy}",
  "dedicated_proxy_pid_file": "${dedicated_proxy_pid_file}",
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
  local task="$1"
  local repo local_dir
  repo="$(repo_for_task "${task}")" || {
    printf '[%s] unsupported task=%s\n' "$(date '+%Y-%m-%d %H:%M:%S %Z')" "${task}" >&2
    return 2
  }
  local_dir="$(dir_for_repo "${repo}")"
  write_status "running" "${task}" "${repo}"
  printf '[%s] downloading task=%s repo=%s local_dir=%s\n' \
    "$(date '+%Y-%m-%d %H:%M:%S %Z')" "${task}" "${repo}" "${local_dir}"
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
    "$(date '+%Y-%m-%d %H:%M:%S %Z')" "${attempt}" "${max_retries}" "${tasks}"
  printf '[%s] network use_proxy=%s proxy_host=%s\n' \
    "$(date '+%Y-%m-%d %H:%M:%S %Z')" "${use_proxy}" "${proxy_host}"
  status=0
  IFS=',' read -r -a task_array <<EOF
${tasks}
EOF
  for task in "${task_array[@]}"; do
    task="$(printf '%s' "${task}" | tr -d '[:space:]')"
    [ -n "${task}" ] || continue
    download_one "${task}" || {
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
