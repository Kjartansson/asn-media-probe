#!/usr/bin/env python3
"""Compare what a media platform serves to different source IPs.

Platforms vary what they hand back based on the reputation of the requesting
address. Not by refusing it -- by quietly serving a worse manifest. You get a
200, full resolution, no error, and no audio track.

This runs one extraction from several vantage points and diffs the results, so
that difference becomes visible instead of silent.

    ./probe.py <url> --via local --via ssh:my-other-box

Exits 1 if the vantage points disagree about audio, which makes it usable as a
canary rather than only as a one-off diagnostic.
"""
from __future__ import annotations

import argparse
import json
import shlex
import subprocess
import sys
from dataclasses import dataclass
from urllib.parse import urlparse

TIMEOUT = 120


@dataclass
class Result:
    via: str
    ok: bool
    formats: int = 0
    max_height: int = 0
    has_audio: bool = False
    cdn_host: str = ""
    error: str = ""


def _run(via: str, url: str) -> tuple[bool, str]:
    """Run yt-dlp -J at `via` and return its stdout."""
    cmd = ["yt-dlp", "-J", "--no-warnings", "--no-playlist", url]
    if via == "local":
        argv = cmd
    elif via.startswith("ssh:"):
        argv = ["ssh", "-o", "BatchMode=yes", via[4:], shlex.join(cmd)]
    else:
        return False, f"unknown vantage {via!r} (use 'local' or 'ssh:<host>')"
    try:
        p = subprocess.run(argv, capture_output=True, text=True, timeout=TIMEOUT)
    except subprocess.TimeoutExpired:
        return False, f"timed out after {TIMEOUT}s"
    except FileNotFoundError as exc:
        return False, str(exc)
    if p.returncode != 0:
        return False, (p.stderr or "").strip().splitlines()[-1][:160] if p.stderr else "failed"
    return True, p.stdout


def _real_codec(v) -> bool:
    return bool(v) and str(v).lower() not in ("none", "null")


def inspect(via: str, url: str) -> Result:
    ok, out = _run(via, url)
    if not ok:
        return Result(via, False, error=out)
    try:
        info = json.loads(out)
    except json.JSONDecodeError as exc:
        return Result(via, False, error=f"unparseable JSON: {exc}")

    formats = info.get("formats") or [info]
    heights = [f.get("height") or 0 for f in formats]

    # An audio-bearing format is one that declares a real audio codec. A 0 here
    # means "nothing on offer declares audio", which on a platform whose
    # progressive formats leave acodec unset is the normal reading everywhere.
    # That is exactly why this tool compares vantage points against each other
    # instead of treating 0 as bad on its own.
    has_audio = any(_real_codec(f.get("acodec")) for f in formats) or _real_codec(
        info.get("acodec")
    )

    chosen = info.get("url") or (formats[-1].get("url") if formats else "")
    return Result(
        via,
        True,
        formats=len(formats),
        max_height=max(heights, default=0),
        has_audio=has_audio,
        cdn_host=urlparse(chosen).netloc if chosen else "",
    )


def render(results: list[Result]) -> str:
    w = max((len(r.via) for r in results), default=4)
    lines = [
        f"{'vantage'.ljust(w)}  {'fmts':>4}  {'max h':>5}  {'audio':>5}  cdn host",
        f"{'-' * w}  {'-' * 4}  {'-' * 5}  {'-' * 5}  {'-' * 24}",
    ]
    for r in results:
        if not r.ok:
            lines.append(f"{r.via.ljust(w)}  {'--':>4}  {'--':>5}  {'--':>5}  ERROR: {r.error}")
            continue
        lines.append(
            f"{r.via.ljust(w)}  {r.formats:>4}  {r.max_height:>5}  "
            f"{('yes' if r.has_audio else 'NO'):>5}  {r.cdn_host}"
        )
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("url")
    ap.add_argument(
        "--via",
        action="append",
        default=None,
        metavar="VANTAGE",
        help="'local', or 'ssh:<host>'. Repeat for each vantage point.",
    )
    args = ap.parse_args()
    vantages = args.via or ["local"]

    results = [inspect(v, args.url) for v in vantages]
    print(render(results))

    good = [r for r in results if r.ok]
    if len(good) < 2:
        return 0

    audio = {r.has_audio for r in good}
    heights = {r.max_height for r in good}
    if len(audio) > 1:
        silent = ", ".join(r.via for r in good if not r.has_audio)
        print(f"\nDISAGREEMENT: no audio offered to {silent}, but offered elsewhere.")
        print("The manifest differs by source IP. Changing the format selector will not help.")
        return 1
    if len(heights) > 1:
        print(f"\nDISAGREEMENT: max height varies by vantage point {sorted(heights)}.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
