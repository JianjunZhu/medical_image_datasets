#!/usr/bin/env bash

set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
dataset_root="$(cd "${script_dir}/.." && pwd)"
pid_file="${dataset_root}/logs/download.pid"
log_file="${dataset_root}/logs/download.log"
status_file="${dataset_root}/data/manifests/download_status.json"

if [ -f "${pid_file}" ]; then
  pid="$(cat "${pid_file}")"
  if ps -p "${pid}" >/dev/null 2>&1; then
    echo "download_status=running pid=${pid}"
  else
    echo "download_status=not_running stale_pid=${pid}"
  fi
else
  echo "download_status=not_started"
fi

if [ -f "${status_file}" ]; then
  echo "--- status_json ---"
  cat "${status_file}"
fi

echo "--- raw snapshot size ---"
du -sh "${dataset_root}/data/raw/huggingface" 2>/dev/null || true

if [ -f "${log_file}" ]; then
  echo "--- log_tail ---"
  tail -n "${TAIL_LINES:-40}" "${log_file}"
fi
