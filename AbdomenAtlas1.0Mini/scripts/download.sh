#!/usr/bin/env bash

set -u

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
dataset_dir="$(cd "${script_dir}/.." && pwd)"
log_dir="${dataset_dir}/logs"
raw_dir="${RAW_DIR:-${dataset_dir}/data/raw}"
token_file="${HF_TOKEN_FILE:-${dataset_dir}/secrets/hf_token}"
proxy_host="${PROXY_HOST:-127.0.0.1:7890}"
conda_env="${CONDA_ENV:-codex-env}"
conda_profile="${CONDA_PROFILE:-/home/jjzhu/anaconda3/etc/profile.d/conda.sh}"

mkdir -p "${log_dir}"
mkdir -p "${raw_dir}"
echo "$$" > "${log_dir}/download.pid"
printf '[%s] downloader pid %s\n' "$(date '+%Y-%m-%d %H:%M:%S %Z')" "$$"

export HF_HUB_ENABLE_HF_TRANSFER="${HF_HUB_ENABLE_HF_TRANSFER:-1}"

if [ -r "${conda_profile}" ]; then
  # shellcheck source=/dev/null
  . "${conda_profile}"
  conda activate "${conda_env}"
fi

while true; do
  printf '[%s] starting download attempt\n' "$(date '+%Y-%m-%d %H:%M:%S %Z')"

  if [ -z "${HF_TOKEN:-}" ]; then
    if [ ! -r "${token_file}" ]; then
      printf '[%s] HF_TOKEN is unset and token file %s is missing or unreadable; retrying in 30 seconds\n' \
        "$(date '+%Y-%m-%d %H:%M:%S %Z')" "${token_file}"
      sleep 30
      continue
    fi
    export HF_TOKEN
    HF_TOKEN="$(tr -d '\r\n' < "${token_file}")"
  fi

  if [ -n "${proxy_host}" ]; then
    export http_proxy="http://${proxy_host}"
    export https_proxy="http://${proxy_host}"
    export HTTP_PROXY="http://${proxy_host}"
    export HTTPS_PROXY="http://${proxy_host}"
    export all_proxy="socks5://${proxy_host}"
    export ALL_PROXY="socks5://${proxy_host}"
    export NO_PROXY="${NO_PROXY:-localhost,127.0.0.1}"
    export no_proxy="${no_proxy:-localhost,127.0.0.1}"
  fi

  huggingface-cli download \
    AbdomenAtlas/AbdomenAtlas1.0Mini \
    --repo-type dataset \
    --local-dir "${raw_dir}"
  status=$?

  if [ "${status}" -eq 0 ]; then
    printf '[%s] download completed successfully\n' "$(date '+%Y-%m-%d %H:%M:%S %Z')"
    exit 0
  fi

  printf '[%s] download failed with exit code %s; retrying in 30 seconds\n' \
    "$(date '+%Y-%m-%d %H:%M:%S %Z')" "${status}"
  sleep 30
done
