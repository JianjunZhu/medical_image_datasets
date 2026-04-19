#!/usr/bin/env bash

set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
dataset_root="$(cd "${script_dir}/.." && pwd)"
pid_file="${dataset_root}/logs/download.pid"

if [ ! -f "${pid_file}" ]; then
  echo "no download pid file"
  exit 0
fi

pid="$(cat "${pid_file}")"
if ps -p "${pid}" >/dev/null 2>&1; then
  kill "${pid}"
  echo "stopped download pid=${pid}"
else
  echo "download pid not running pid=${pid}"
fi
