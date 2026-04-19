#!/usr/bin/env bash

set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
dataset_root="$(cd "${script_dir}/.." && pwd)"
manifest_dir="${dataset_root}/data/manifests"
out_file="${manifest_dir}/proxy_speedtest.csv"
controller="${MIHOMO_CONTROLLER:-http://127.0.0.1:19091}"
proxy_group="${PROXY_GROUP:-Proxy}"
proxy_host="${PROXY_HOST:-127.0.0.1:17890}"
url="${SPEEDTEST_URL:-https://huggingface.co/datasets/FLARE-MedFM/FLARE-Task2-LaptopSeg/resolve/main/README.md}"
nodes="${PROXY_CANDIDATES:-direct}"
bytes="${SPEEDTEST_BYTES:-1048576}"

mkdir -p "${manifest_dir}"
printf 'timestamp,node,mode,url,bytes,seconds,mb_per_s\n' > "${out_file}"

test_one() {
  local node="$1"
  local mode="$2"
  local start end elapsed mbps curl_args
  curl_args=(-L --fail --silent --output /dev/null --range "0-$((bytes - 1))" --connect-timeout 15 --max-time 60)
  if [ "${mode}" = "proxy" ]; then
    curl_args+=(--proxy "http://${proxy_host}")
  fi
  start="$(date +%s.%N)"
  if curl "${curl_args[@]}" "${url}"; then
    end="$(date +%s.%N)"
    elapsed="$(awk -v s="${start}" -v e="${end}" 'BEGIN {print e-s}')"
    mbps="$(awk -v b="${bytes}" -v t="${elapsed}" 'BEGIN {if (t > 0) print (b/1048576)/t; else print 0}')"
  else
    elapsed=0
    mbps=0
  fi
  printf '%s,%s,%s,%s,%s,%s,%s\n' "$(date --iso-8601=seconds)" "${node}" "${mode}" "${url}" "${bytes}" "${elapsed}" "${mbps}" | tee -a "${out_file}"
}

IFS=',' read -r -a node_array <<EOF
${nodes}
EOF

for node in "${node_array[@]}"; do
  node="$(printf '%s' "${node}" | sed 's/^ *//;s/ *$//')"
  [ -n "${node}" ] || continue
  if [ "${node}" = "direct" ]; then
    test_one "direct" "direct"
  else
    if command -v curl >/dev/null 2>&1; then
      curl -s -X PUT "${controller}/proxies/${proxy_group}" \
        -H 'Content-Type: application/json' \
        --data "{\"name\":\"${node}\"}" >/dev/null || true
    fi
    sleep "${SWITCH_SETTLE_SECONDS:-2}"
    test_one "${node}" "proxy"
  fi
done

echo "speedtest_results=${out_file}"
