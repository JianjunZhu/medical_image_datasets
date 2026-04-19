#!/usr/bin/env bash

set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
dataset_root="$(cd "${script_dir}/.." && pwd)"
pid_file="${dataset_root}/logs/download_proxy.pid"
log_file="${dataset_root}/logs/download_proxy.log"
mihomo_bin="${MIHOMO_BIN:-/home/jjzhu/mihomo/mihomo}"
mihomo_dir="${MIHOMO_DIR:-${dataset_root}/cache/mihomo}"

mkdir -p "${dataset_root}/logs" "${mihomo_dir}"

if [ -f "${pid_file}" ]; then
  pid="$(cat "${pid_file}")"
  if ps -p "${pid}" >/dev/null 2>&1; then
    echo "dedicated proxy already running pid=${pid}"
    exit 0
  fi
fi

if [ ! -x "${mihomo_bin}" ]; then
  echo "mihomo binary not executable: ${mihomo_bin}" >&2
  exit 2
fi

if [ ! -f "${mihomo_dir}/config.yaml" ]; then
  echo "missing mihomo config: ${mihomo_dir}/config.yaml" >&2
  echo "copy or generate a config with HTTP/SOCKS/controller ports reserved for this dataset" >&2
  exit 3
fi

nohup setsid "${mihomo_bin}" -d "${mihomo_dir}" >> "${log_file}" 2>&1 < /dev/null &
echo $! > "${pid_file}"
sleep 2
echo "started dedicated proxy pid=$(cat "${pid_file}") log=${log_file}"
