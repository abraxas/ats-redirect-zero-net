#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

export COMPOSE_PROJECT_NAME="${COMPOSE_PROJECT_NAME:-ats-redirect-zero-net}"
IMAGE="${ATS_IMAGE:-ats-10.2.0-lab:local}"
LOCK="${ATS_IMAGE_LOCK:-/tmp/ats-10.2.0-lab.lock}"
# Relative to this run dir; never bake a home path into lab files.
SRC="${ATS_SRC:-../../client-reviews/trafficserver/src}"

chmod +x poc.py stub.py entrypoint.sh 2>/dev/null || chmod +x poc.py stub.py

down() {
  echo "== docker compose down -v =="
  docker compose -p "${COMPOSE_PROJECT_NAME}" down -v --remove-orphans || true
}

ensure_image() {
  echo "== ensure ${IMAGE} (lock ${LOCK}) =="
  # macOS has no flock(1); fcntl lock is portable. Inspect first so a sibling
  # rebuild of the same tag does not block a lab that can already run.
  python3 - "${LOCK}" "${IMAGE}" "${SRC}" <<'PY'
import fcntl
import os
import subprocess
import sys

lock_path, image, src = sys.argv[1], sys.argv[2], sys.argv[3]


def present() -> bool:
    inspect = subprocess.run(
        ["docker", "image", "inspect", image],
        capture_output=True,
        text=True,
    )
    return inspect.returncode == 0


if present():
    print(f"IOC ats-image present {image}", flush=True)
    sys.exit(0)

fd = os.open(lock_path, os.O_CREAT | os.O_RDWR, 0o644)
fcntl.flock(fd, fcntl.LOCK_EX)
if present():
    print(f"IOC ats-image present {image}", flush=True)
    sys.exit(0)
print(f"== docker build {image} context={src} ==", flush=True)
sys.exit(subprocess.call(["docker", "build", "-t", image, "-f", "Dockerfile", src]))
PY
}

echo "== docker compose down (clean) =="
down

ensure_image

echo "== docker compose up =="
up_ok=0
for attempt in $(seq 1 20); do
  if docker compose -p "${COMPOSE_PROJECT_NAME}" up -d --build; then
    up_ok=1
    break
  fi
  echo "compose-up-retry attempt=${attempt}"
  sleep 30
  down
done
if [[ "${up_ok}" != 1 ]]; then
  echo "FAIL ats-redirect-zero-net compose up failed ATS-REDIRECT-ZERO-NET-WITNESS" | tee poc-last-run.txt
  down
  exit 1
fi

echo "== wait ATS 127.0.0.1:18790 =="
ready=0
for i in $(seq 1 60); do
  code="$(curl -sS -o /tmp/ats-redirect-zero-net-ready -w '%{http_code}' --max-time 5 \
    -H 'Host: no-such.lab' "http://127.0.0.1:18790/" || true)"
  if [[ "${code}" =~ ^[2345][0-9][0-9]$ ]]; then
    echo "ats-ready attempt=${i} http=${code}"
    ready=1
    break
  fi
  echo "ats-wait attempt=${i} http=${code}"
  sleep 2
done
if [[ "${ready}" != 1 ]]; then
  echo "FAIL ats-redirect-zero-net ATS not ready ATS-REDIRECT-ZERO-NET-WITNESS" | tee poc-last-run.txt
  docker compose -p "${COMPOSE_PROJECT_NAME}" logs --tail=80 || true
  down
  exit 1
fi

echo "== poc.py =="
set +e
python3 ./poc.py | tee poc-last-run.txt
rc=${PIPESTATUS[0]}
set -e
if [[ "${rc}" != 0 ]]; then
  if ! tail -n1 poc-last-run.txt 2>/dev/null | grep -qE '^(SUCCESS|FAIL) '; then
    echo "FAIL ats-redirect-zero-net poc exit=${rc} ATS-REDIRECT-ZERO-NET-WITNESS" >> poc-last-run.txt
  fi
  echo "== ats logs (tail) ==" | tee -a poc-last-run.txt
  docker compose -p "${COMPOSE_PROJECT_NAME}" logs --tail=120 ats witness | tee -a poc-last-run.txt || true
fi

down
exit "${rc}"
