#!/usr/bin/env bash

set -u

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
dataset_root="$(cd "${script_dir}/.." && pwd)"
archives_dir="${ARCHIVES_DIR:-${dataset_root}/data/raw/archives}"
manifest_dir="${dataset_root}/data/manifests"
status_file="${manifest_dir}/download_status.json"
source_url="${SOURCE_URL:-https://msd-for-monai.s3-us-west-2.amazonaws.com}"
folder_id="${GOOGLE_DRIVE_FOLDER_ID:-1HqEgzS8BV2c7xYNrZdEAnrHk7osJJ--2}"
download_tool="${DOWNLOAD_TOOL:-s3curl}"
max_retries="${MAX_RETRIES:-20}"
retry_seconds="${RETRY_SECONDS:-60}"
use_proxy="${USE_PROXY:-1}"
proxy_host="${PROXY_HOST:-127.0.0.1:17890}"

configure_network() {
  if [ "${use_proxy}" = "1" ] || [ "${use_proxy}" = "true" ]; then
    export http_proxy="http://${proxy_host}"
    export https_proxy="http://${proxy_host}"
    export HTTP_PROXY="http://${proxy_host}"
    export HTTPS_PROXY="http://${proxy_host}"
    export all_proxy="socks5://${proxy_host}"
    export ALL_PROXY="socks5://${proxy_host}"
    export NO_PROXY="${NO_PROXY:-localhost,127.0.0.1}"
    export no_proxy="${no_proxy:-localhost,127.0.0.1}"
  else
    unset http_proxy
    unset https_proxy
    unset HTTP_PROXY
    unset HTTPS_PROXY
    unset all_proxy
    unset ALL_PROXY
    unset NO_PROXY
    unset no_proxy
  fi
}

configure_network

mkdir -p "${archives_dir}" "${manifest_dir}"

MSD_ARCHIVES=(
  "Task01_BrainTumour.tar"
  "Task02_Heart.tar"
  "Task03_Liver.tar"
  "Task04_Hippocampus.tar"
  "Task05_Prostate.tar"
  "Task06_Lung.tar"
  "Task07_Pancreas.tar"
  "Task08_HepaticVessel.tar"
  "Task09_Spleen.tar"
  "Task10_Colon.tar"
)

write_status() {
  local status="$1"
  local finished_at="${2:-null}"
  local downloaded_files downloaded_bytes now
  now="$(date --iso-8601=seconds)"
  downloaded_files="$(find "${archives_dir}" -type f 2>/dev/null | wc -l)"
  downloaded_bytes="$(find "${archives_dir}" -type f -printf '%s\n' 2>/dev/null | awk '{s+=$1} END {print s+0}')"
  if [ "${finished_at}" != "null" ]; then
    finished_at="\"${finished_at}\""
  fi
  cat > "${status_file}" <<EOF
{
  "dataset": "MSD",
  "source_url": "${source_url}",
  "folder_id": "${folder_id}",
  "download_tool": "${download_tool}",
  "download_dir": "data/raw/archives",
  "use_proxy": "${use_proxy}",
  "proxy_host": "${proxy_host}",
  "pid": $$,
  "status": "${status}",
  "last_checked_at": "${now}",
  "finished_at": ${finished_at},
  "downloaded_files": ${downloaded_files},
  "downloaded_bytes": ${downloaded_bytes}
}
EOF
}

run_gdown() {
  gdown --folder "${source_url}" \
    --output "${archives_dir}" \
    --continue
}

run_s3curl() {
  local archive url output curl_args
  for archive in "${MSD_ARCHIVES[@]}"; do
    url="${source_url%/}/${archive}"
    output="${archives_dir}/${archive}"
    printf '[%s] downloading %s\n' "$(date '+%Y-%m-%d %H:%M:%S %Z')" "${archive}"

    curl_args=(
      --fail
      --location
      --continue-at -
      --retry "${CURL_RETRIES:-10}"
      --retry-delay "${CURL_RETRY_DELAY:-15}"
      --retry-all-errors
      --connect-timeout "${CURL_CONNECT_TIMEOUT:-30}"
      --output "${output}"
    )
    if [ "${use_proxy}" = "1" ] || [ "${use_proxy}" = "true" ]; then
      curl_args+=(--proxy "http://${proxy_host}")
    fi
    curl "${curl_args[@]}" "${url}"
  done
}

run_rclone() {
  local remote="${RCLONE_REMOTE:-gdrive}"
  rclone copy "${remote}:" "${archives_dir}" \
    --drive-root-folder-id "${folder_id}" \
    --transfers "${RCLONE_TRANSFERS:-2}" \
    --checkers "${RCLONE_CHECKERS:-4}" \
    --retries "${RCLONE_RETRIES:-10}" \
    --low-level-retries "${RCLONE_LOW_LEVEL_RETRIES:-20}" \
    --stats 30s \
    --progress
}

attempt=1
write_status "running"

while [ "${attempt}" -le "${max_retries}" ]; do
  printf '[%s] download attempt %s/%s using %s\n' \
    "$(date '+%Y-%m-%d %H:%M:%S %Z')" "${attempt}" "${max_retries}" "${download_tool}"
  printf '[%s] network use_proxy=%s proxy_host=%s\n' \
    "$(date '+%Y-%m-%d %H:%M:%S %Z')" "${use_proxy}" "${proxy_host}"

  case "${download_tool}" in
    s3curl)
      run_s3curl
      status=$?
      ;;
    gdown)
      run_gdown
      status=$?
      ;;
    rclone)
      run_rclone
      status=$?
      ;;
    *)
      printf '[%s] unsupported DOWNLOAD_TOOL=%s\n' \
        "$(date '+%Y-%m-%d %H:%M:%S %Z')" "${download_tool}" >&2
      write_status "failed" "$(date --iso-8601=seconds)"
      exit 2
      ;;
  esac

  if [ "${status}" -eq 0 ]; then
    printf '[%s] download completed\n' "$(date '+%Y-%m-%d %H:%M:%S %Z')"
    write_status "completed" "$(date --iso-8601=seconds)"
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
write_status "failed" "$(date --iso-8601=seconds)"
exit 1
