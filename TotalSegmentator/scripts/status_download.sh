#!/usr/bin/env bash

set -u

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
dataset_root="$(cd "${script_dir}/.." && pwd)"
pid_file="${dataset_root}/logs/download.pid"
status_file="${dataset_root}/data/manifests/download_status.json"

if [ -r "${status_file}" ]; then
  cat "${status_file}"
else
  printf '{"dataset":"TotalSegmentator","status":"unknown"}\n'
fi

if [ -r "${pid_file}" ]; then
  pid="$(cat "${pid_file}")"
  if [ -n "${pid}" ] && ps -p "${pid}" >/dev/null 2>&1; then
    printf '\nprocess=running pid=%s\n' "${pid}"
  else
    printf '\nprocess=not_running pid=%s\n' "${pid}"
  fi
fi
