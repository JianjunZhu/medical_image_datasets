#!/usr/bin/env bash

set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
dataset_root="$(cd "${script_dir}/.." && pwd)"
log_file="${dataset_root}/logs/download.log"
pid_file="${dataset_root}/logs/download.pid"

mkdir -p "${dataset_root}/logs"

if [ -f "${pid_file}" ]; then
  pid="$(cat "${pid_file}")"
  if ps -p "${pid}" >/dev/null 2>&1; then
    echo "download already running pid=${pid}"
    exit 0
  fi
fi

nohup setsid bash "${script_dir}/download.sh" >> "${log_file}" 2>&1 < /dev/null &
echo $! > "${pid_file}"
echo "started FLARE24 download pid=$(cat "${pid_file}") log=${log_file}"
