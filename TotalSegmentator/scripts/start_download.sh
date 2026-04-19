#!/usr/bin/env bash

set -u

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
dataset_root="$(cd "${script_dir}/.." && pwd)"
log_dir="${dataset_root}/logs"
pid_file="${log_dir}/download.pid"
log_file="${log_dir}/download.log"

mkdir -p "${log_dir}"

is_download_process() {
  local pid="$1"
  ps -p "${pid}" -o args= 2>/dev/null | grep -E '(^|[ /])download\.sh($| )' > /dev/null 2>&1
}

if [ -r "${pid_file}" ]; then
  old_pid="$(cat "${pid_file}")"
  if [ -n "${old_pid}" ] && is_download_process "${old_pid}"; then
    printf 'download already running: pid=%s\n' "${old_pid}"
    exit 0
  fi
fi

printf '[%s] starting background download TOTAL_SEGMENTATOR_SUBSETS=%s USE_PROXY=%s PROXY_HOST=%s\n' \
  "$(date '+%Y-%m-%d %H:%M:%S %Z')" \
  "${TOTAL_SEGMENTATOR_SUBSETS:-ct,mri}" \
  "${USE_PROXY:-0}" \
  "${PROXY_HOST:-127.0.0.1:17890}" >> "${log_file}"
nohup setsid bash "${script_dir}/download.sh" >> "${log_file}" 2>&1 < /dev/null &
pid=$!
echo "${pid}" > "${pid_file}"

printf 'download started in background: pid=%s\n' "${pid}"
printf 'log: %s\n' "${log_file}"
