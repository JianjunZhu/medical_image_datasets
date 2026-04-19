#!/usr/bin/env bash

set -u

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
dataset_root="$(cd "${script_dir}/.." && pwd)"
pid_file="${dataset_root}/logs/download.pid"

if [ ! -r "${pid_file}" ]; then
  printf 'download pid file not found\n'
  exit 0
fi

pid="$(cat "${pid_file}")"
if [ -z "${pid}" ]; then
  printf 'download pid file is empty\n'
  exit 0
fi

if ps -p "${pid}" -o args= 2>/dev/null | grep -E '(^|[ /])download\.sh($| )' > /dev/null 2>&1; then
  kill "${pid}"
  printf 'sent TERM to download process: pid=%s\n' "${pid}"
else
  printf 'download process not running: pid=%s\n' "${pid}"
fi
