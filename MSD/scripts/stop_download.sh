#!/usr/bin/env bash

set -u

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
dataset_root="$(cd "${script_dir}/.." && pwd)"
pid_file="${dataset_root}/logs/download.pid"
status_file="${dataset_root}/data/manifests/download_status.json"
archives_dir="${dataset_root}/data/raw/archives"

if [ ! -r "${pid_file}" ]; then
  printf 'download pid file is missing\n'
  exit 0
fi

pid="$(cat "${pid_file}")"
if [ -z "${pid}" ] || ! ps -p "${pid}" -o args= 2>/dev/null | grep -E '(^|[ /])download\.sh($| )' > /dev/null 2>&1; then
  printf 'download process is not running\n'
  exit 0
fi

kill "${pid}"
printf 'sent TERM to download process: pid=%s\n' "${pid}"

mkdir -p "$(dirname "${status_file}")"
downloaded_files="$(find "${archives_dir}" -type f 2>/dev/null | wc -l)"
downloaded_bytes="$(find "${archives_dir}" -type f -printf '%s\n' 2>/dev/null | awk '{s+=$1} END {print s+0}')"
cat > "${status_file}" <<EOF
{
  "dataset": "MSD",
  "status": "stopped",
  "pid": ${pid},
  "last_checked_at": "$(date --iso-8601=seconds)",
  "downloaded_files": ${downloaded_files},
  "downloaded_bytes": ${downloaded_bytes}
}
EOF
