#!/usr/bin/env bash

set -u

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
dataset_root="$(cd "${script_dir}/.." && pwd)"
pid_file="${dataset_root}/logs/download.pid"
log_file="${dataset_root}/logs/download.log"
status_file="${dataset_root}/data/manifests/download_status.json"
archives_dir="${dataset_root}/data/raw/archives"

if [ -r "${pid_file}" ]; then
  pid="$(cat "${pid_file}")"
else
  pid=""
fi

if pgrep -af 'MSD/scripts/download.sh|curl .*MSD.*/Task.*tar|gdown --folder' > /dev/null 2>&1; then
  process_status="running"
else
  process_status="not_running"
fi

printf 'download_pid=%s\n' "${pid:-none}"
printf 'process=%s\n' "${process_status}"
printf 'archives_size='
du -sh "${archives_dir}" 2>/dev/null | awk '{print $1}'

if [ -r "${status_file}" ]; then
  printf '\nstatus_file:\n'
  sed -n '1,120p' "${status_file}"
else
  printf '\nstatus_file: missing\n'
fi

if [ -r "${log_file}" ]; then
  printf '\nlast_log:\n'
  tail -40 "${log_file}"
else
  printf '\nlast_log: missing\n'
fi
