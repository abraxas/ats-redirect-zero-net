#!/usr/bin/env python3
"""Origin 302 stubs and the in-netns 0.0.0.1 / loopback / TEST-NET oracles."""

from __future__ import annotations

import http.server
import os
import socket
import subprocess
import sys
import threading
from typing import Callable

WITNESS = os.environ.get("WITNESS", "ATS-REDIRECT-ZERO-NET-WITNESS")
LOOPBACK_SECRET = os.environ.get("LOOPBACK_SECRET", "LOOPBACK-ONLY-SECRET")
FOLLOW_OK = os.environ.get("FOLLOW_OK", "FOLLOW-OK")
MODE = os.environ.get("MODE", "origin-a")
BIND_PORT = int(os.environ.get("BIND_PORT", "8080"))
ZERO_NET_URL = os.environ.get("ZERO_NET_URL", "http://0.0.0.1:18080/w")
LOOPBACK_URL = os.environ.get("LOOPBACK_URL", "http://127.0.0.1:18080/loop")
ROUTABLE_URL = os.environ.get("ROUTABLE_URL", "http://203.0.113.10:18080/ok")
ANY_URL = os.environ.get("ANY_URL", "http://0.0.0.0:18080/any")
IP_FREEBIND = 15


def log(msg: str) -> None:
    print(msg, flush=True)


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, text=True, capture_output=True)


class CloseHandler(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt: str, *args: object) -> None:
        sys.stderr.write(f"{MODE} " + (fmt % args) + "\n")
        sys.stderr.flush()

    def _send(self, status: int, body: str, extra: list[tuple[str, str]] | None = None) -> None:
        payload = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Connection", "close")
        if extra:
            for key, value in extra:
                self.send_header(key, value)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(payload)

    def _dispatch(self) -> None:
        raise NotImplementedError

    def do_GET(self) -> None:
        self._dispatch()

    def do_HEAD(self) -> None:
        self._dispatch()

    def do_POST(self) -> None:
        length = int(self.headers.get("Content-Length") or 0)
        if length > 0:
            self.rfile.read(length)
        self._dispatch()


class OriginA(CloseHandler):
    def _dispatch(self) -> None:
        self._send(302, "ORIGIN-A-302\n", [("Location", ZERO_NET_URL)])


class OriginB(CloseHandler):
    def _dispatch(self) -> None:
        self._send(302, "ORIGIN-B-302\n", [("Location", LOOPBACK_URL)])


class OriginC(CloseHandler):
    def _dispatch(self) -> None:
        self._send(302, "ORIGIN-C-302\n", [("Location", ROUTABLE_URL)])


class OriginAny(CloseHandler):
    def _dispatch(self) -> None:
        self._send(302, "ORIGIN-ANY-302\n", [("Location", ANY_URL)])


class WitnessHandler(CloseHandler):
    def _dispatch(self) -> None:
        host = self.server.server_address[0]  # type: ignore[attr-defined]
        path = self.path.split("?", 1)[0]
        if host == "0.0.0.1":
            self._send(200, f"{WITNESS}\npath={path}\n")
            return
        if host == "127.0.0.1":
            self._send(200, f"{LOOPBACK_SECRET}\npath={path}\n")
            return
        if host == "203.0.113.10":
            self._send(200, f"{FOLLOW_OK}\npath={path}\n")
            return
        self._send(404, "no-oracle\n")


class FreebindServer(http.server.ThreadingHTTPServer):
    allow_reuse_address = True
    daemon_threads = True

    def server_bind(self) -> None:
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.socket.setsockopt(socket.SOL_IP, IP_FREEBIND, 1)
        except OSError as exc:
            log(f"IP_FREEBIND setsockopt: {exc}")
        super().server_bind()


def ensure_local_route(host: str) -> str:
    """Deliver host locally without putting it on an interface (avoids ATS SELF)."""
    route = run(["ip", "route", "add", "local", f"{host}/32", "dev", "lo"])
    log(f"local-route {host} rc={route.returncode} {route.stdout.strip()}{route.stderr.strip()}")
    got = run(["ip", "route", "get", host])
    log(f"route-get {host} {got.stdout.strip() or got.stderr.strip()}")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        sock.setsockopt(socket.SOL_IP, IP_FREEBIND, 1)
        sock.bind((host, 0))
        sock.close()
        return "local-route+freebind"
    except OSError as exc:
        log(f"bind-probe {host} freebind failed: {exc}")
        sock.close()
    sysctl = run(["sysctl", "-w", "net.ipv4.ip_nonlocal_bind=1"])
    log(f"sysctl rc={sysctl.returncode} {sysctl.stdout.strip()} {sysctl.stderr.strip()}")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        sock.setsockopt(socket.SOL_IP, IP_FREEBIND, 1)
        sock.bind((host, 0))
        sock.close()
        return "nonlocal+freebind"
    except OSError as exc:
        sock.close()
        log(f"bind-probe {host} after sysctl failed: {exc}")
        raise


def serve(host: str, port: int, handler: type[CloseHandler]) -> FreebindServer:
    httpd = FreebindServer((host, port), handler)
    log(f"listen {host}:{port} handler={handler.__name__}")
    return httpd


def run_origins() -> int:
    mapping: dict[str, type[CloseHandler]] = {
        "origin-a": OriginA,
        "origin-b": OriginB,
        "origin-c": OriginC,
        "origin-any": OriginAny,
    }
    handler = mapping.get(MODE)
    if handler is None:
        log(f"unknown MODE={MODE}")
        return 1
    log(f"origin mode={MODE} port={BIND_PORT} zero={ZERO_NET_URL} loop={LOOPBACK_URL} routable={ROUTABLE_URL}")
    httpd = http.server.ThreadingHTTPServer(("0.0.0.0", BIND_PORT), handler)
    httpd.allow_reuse_address = True
    httpd.serve_forever()
    return 0


def run_witness() -> int:
    targets = (
        ("0.0.0.1", 18080, True),
        ("127.0.0.1", 18080, False),
        ("203.0.113.10", 18080, True),
    )
    servers: list[FreebindServer] = []
    for host, port, need_route in targets:
        if need_route:
            try:
                method = ensure_local_route(host)
            except OSError as exc:
                log(f"catcher-fatal cannot prepare {host}: {exc}")
                return 1
            log(f"catcher-bind {host} method={method}")
        try:
            servers.append(serve(host, port, WitnessHandler))
        except OSError as exc:
            log(f"catcher-fatal cannot bind {host}:{port}: {exc}")
            return 1
    addr = run(["ip", "-4", "addr", "show", "dev", "lo"])
    log(f"catcher-lo {addr.stdout.strip() or addr.stderr.strip()}")
    ready = os.environ.get("READY_FILE", "/tmp/witness-ready")
    with open(ready, "w", encoding="utf-8") as handle:
        handle.write("ready\n")
    log(f"catcher-listen ready witness={WITNESS}")

    def serve_one(httpd: FreebindServer) -> None:
        httpd.serve_forever()

    threads = [threading.Thread(target=serve_one, args=(httpd,), daemon=True) for httpd in servers]
    for thread in threads:
        thread.start()
    threads[0].join()
    return 0


def main() -> int:
    dispatch: dict[str, Callable[[], int]] = {
        "witness": run_witness,
        "origin-a": run_origins,
        "origin-b": run_origins,
        "origin-c": run_origins,
        "origin-any": run_origins,
    }
    fn = dispatch.get(MODE)
    if fn is None:
        log(f"unknown MODE={MODE}")
        return 1
    try:
        return fn()
    except OSError as exc:
        log(f"catcher-fatal {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
