#!/usr/bin/env bash
set -euo pipefail

python3 /lab/stub.py &
witness_pid=$!

ready=0
for _ in $(seq 1 50); do
  if [[ -f /tmp/witness-ready ]]; then
    ready=1
    break
  fi
  if ! kill -0 "${witness_pid}" 2>/dev/null; then
    echo "IOC witness-exited-early" >&2
    wait "${witness_pid}" || true
    break
  fi
  sleep 0.2
done
if [[ "${ready}" != 1 ]]; then
  echo "IOC witness-not-ready (ATS still starting; poc will FAIL on bind)" >&2
fi

exec traffic_server
