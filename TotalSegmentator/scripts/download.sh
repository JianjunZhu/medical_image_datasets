#!/usr/bin/env bash

set -u

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
dataset_root="$(cd "${script_dir}/.." && pwd)"
archives_dir="${ARCHIVES_DIR:-${dataset_root}/data/raw/archives}"
manifest_dir="${dataset_root}/data/manifests"
status_file="${manifest_dir}/download_status.json"
subsets="${TOTAL_SEGMENTATOR_SUBSETS:-ct,mri}"
max_retries="${MAX_RETRIES:-20}"
retry_seconds="${RETRY_SECONDS:-60}"
use_proxy="${USE_PROXY:-0}"
proxy_host="${PROXY_HOST:-127.0.0.1:17890}"

mkdir -p "${archives_dir}" "${manifest_dir}"

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

record_info() {
  case "$1" in
    ct)
      printf '%s|%s|%s|%s\n' \
        "Totalsegmentator_dataset_v201.zip" \
        "https://zenodo.org/records/10047292/files/Totalsegmentator_dataset_v201.zip?download=1" \
        "23581218285" \
        "fe250e5718e0a3b5df4c4ea9d58a62fe"
      ;;
    mri)
      printf '%s|%s|%s|%s\n' \
        "TotalsegmentatorMRI_dataset_v200.zip" \
        "https://zenodo.org/records/14710732/files/TotalsegmentatorMRI_dataset_v200.zip?download=1" \
        "5100514630" \
        "54638f4cb883ce3b34225195358c398f"
      ;;
    ct_small)
      printf '%s|%s|%s|%s\n' \
        "Totalsegmentator_dataset_small_v201.zip" \
        "https://zenodo.org/records/10047263/files/Totalsegmentator_dataset_small_v201.zip?download=1" \
        "" \
        "6b5524af4b15e6ba06ef2d700c0c73e0"
      ;;
    *)
      return 1
      ;;
  esac
}

downloaded_bytes() {
  find "${archives_dir}" -type f -printf '%s\n' 2>/dev/null | awk '{s+=$1} END {print s+0}'
}

downloaded_files() {
  find "${archives_dir}" -type f 2>/dev/null | wc -l
}

write_status() {
  local status="$1"
  local active_subset="${2:-}"
  local finished_at="${3:-null}"
  local now
  now="$(date --iso-8601=seconds)"
  if [ "${finished_at}" != "null" ]; then
    finished_at="\"${finished_at}\""
  fi
  cat > "${status_file}" <<EOF
{
  "dataset": "TotalSegmentator",
  "subsets": "${subsets}",
  "active_subset": "${active_subset}",
  "download_dir": "data/raw/archives",
  "use_proxy": "${use_proxy}",
  "proxy_host": "${proxy_host}",
  "pid": $$,
  "status": "${status}",
  "last_checked_at": "${now}",
  "finished_at": ${finished_at},
  "downloaded_files": $(downloaded_files),
  "downloaded_bytes": $(downloaded_bytes)
}
EOF
}

download_one() {
  local subset="$1"
  local info file url expected_size expected_md5 output size curl_args
  info="$(record_info "${subset}")" || {
    printf '[%s] unsupported subset=%s\n' "$(date '+%Y-%m-%d %H:%M:%S %Z')" "${subset}" >&2
    return 2
  }
  IFS='|' read -r file url expected_size expected_md5 <<EOF
${info}
EOF
  output="${archives_dir}/${file}"
  write_status "running" "${subset}"
  printf '[%s] downloading subset=%s file=%s\n' "$(date '+%Y-%m-%d %H:%M:%S %Z')" "${subset}" "${file}"
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
  curl "${curl_args[@]}" "${url}" || return $?
  if [ -n "${expected_size}" ]; then
    size="$(stat -c '%s' "${output}")"
    if [ "${size}" != "${expected_size}" ]; then
      printf '[%s] size mismatch for %s expected=%s actual=%s\n' \
        "$(date '+%Y-%m-%d %H:%M:%S %Z')" "${file}" "${expected_size}" "${size}" >&2
      return 3
    fi
  fi
  if command -v md5sum >/dev/null 2>&1; then
    printf '%s  %s\n' "${expected_md5}" "${output}" | md5sum -c - || return $?
  fi
}

configure_network
write_status "running"

attempt=1
while [ "${attempt}" -le "${max_retries}" ]; do
  printf '[%s] download attempt %s/%s subsets=%s\n' \
    "$(date '+%Y-%m-%d %H:%M:%S %Z')" "${attempt}" "${max_retries}" "${subsets}"
  printf '[%s] network use_proxy=%s proxy_host=%s\n' \
    "$(date '+%Y-%m-%d %H:%M:%S %Z')" "${use_proxy}" "${proxy_host}"
  status=0
  IFS=',' read -r -a subset_array <<EOF
${subsets}
EOF
  for subset in "${subset_array[@]}"; do
    subset="$(printf '%s' "${subset}" | tr -d '[:space:]')"
    [ -n "${subset}" ] || continue
    download_one "${subset}" || {
      status=$?
      break
    }
  done
  if [ "${status}" -eq 0 ]; then
    printf '[%s] download completed\n' "$(date '+%Y-%m-%d %H:%M:%S %Z')"
    write_status "completed" "" "$(date --iso-8601=seconds)"
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
write_status "failed" "" "$(date --iso-8601=seconds)"
exit 1
