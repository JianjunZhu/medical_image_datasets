#!/usr/bin/env bash

set -u

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
dataset_dir="$(cd "${script_dir}/.." && pwd)"
log_dir="${dataset_dir}/logs"

mkdir -p "${log_dir}"
echo "$$" > "${log_dir}/monitor_storage_progress.pid"

total_bytes="${TOTAL_BYTES:-325725702760}"
interval_seconds="${INTERVAL_SECONDS:-10}"
prev_downloaded_bytes=
prev_timestamp=

while true; do
  current_timestamp="$(date +%s)"
  downloaded_bytes="$(
    find "${dataset_dir}" \
      \( -path "${dataset_dir}/cache" -o -path "${dataset_dir}/logs" -o -path "${dataset_dir}/secrets" \) -prune \
      -o -type f \( -name '*.nii.gz' -o -name '.gitattributes' \) -printf '%s\n' |
      awk '{s+=$1} END {print s+0}'
  )"
  percent="$(awk -v d="${downloaded_bytes}" -v t="${total_bytes}" 'BEGIN { if (t == 0) print "0.00"; else printf "%.4f", 100*d/t }')"
  remaining_bytes="$(awk -v d="${downloaded_bytes}" -v t="${total_bytes}" 'BEGIN { r=t-d; if (r < 0) r=0; print r }')"
  downloaded_gb="$(awk -v b="${downloaded_bytes}" 'BEGIN { printf "%.2f", b/1000000000 }')"
  total_gb="$(awk -v b="${total_bytes}" 'BEGIN { printf "%.2f", b/1000000000 }')"
  remaining_gb="$(awk -v b="${remaining_bytes}" 'BEGIN { printf "%.2f", b/1000000000 }')"

  if [ -n "${prev_downloaded_bytes:-}" ] && [ -n "${prev_timestamp:-}" ]; then
    speed_bps="$(awk -v cur="${downloaded_bytes}" -v prev="${prev_downloaded_bytes}" -v now="${current_timestamp}" -v then="${prev_timestamp}" 'BEGIN { dt=now-then; if (dt <= 0) dt=1; ds=cur-prev; if (ds < 0) ds=0; printf "%.0f", ds/dt }')"
  else
    speed_bps=0
  fi
  speed_mbps="$(awk -v bps="${speed_bps}" 'BEGIN { printf "%.2f", bps/1000000 }')"
  speed_gbps="$(awk -v bps="${speed_bps}" 'BEGIN { printf "%.4f", bps/1000000000 }')"

  printf '[%s] storage %s GB / %s GB (%s%%), remaining %s GB, speed %s MB/s (%s GB/s)\n' \
    "$(date '+%Y-%m-%d %H:%M:%S %Z')" "${downloaded_gb}" "${total_gb}" "${percent}" "${remaining_gb}" "${speed_mbps}" "${speed_gbps}"

  if [ "${downloaded_bytes}" -ge "${total_bytes}" ]; then
    exit 0
  fi

  prev_downloaded_bytes="${downloaded_bytes}"
  prev_timestamp="${current_timestamp}"
  sleep "${interval_seconds}"
done
