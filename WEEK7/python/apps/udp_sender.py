"""Expeditor UDP pentru demo-urile din Săptămâna 7."""

from __future__ import annotations

import argparse
import socket
import time
from pathlib import Path
from typing import Optional


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Expeditor UDP simplu (Săptămâna 7).")
    p.add_argument("--host", required=True, help="Adresa sau numele destinației")
    p.add_argument("--port", type=int, default=9091, help="Portul destinației (implicit: 9091)")
    p.add_argument("--message", default="hello", help="Mesajul de trimis (implicit: hello)")
    p.add_argument("--count", type=int, default=1, help="Numărul de datagrame (implicit: 1)")
    p.add_argument("--delay", type=float, default=0.1, help="Întârziere între trimiteri, în secunde (implicit: 0.1)")
    p.add_argument("--log", default="", help="Cale opțională către fișierul de log")
    return p


def log_line(path: Optional[Path], line: str) -> None:
    stamp = time.strftime("%Y-%m-%d %H:%M:%S")
    msg = f"[{stamp}] {line}"
    print(msg, flush=True)
    if path:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as f:
            f.write(msg + "\n")


def main() -> int:
    args = build_parser().parse_args()
    log_path = Path(args.log) if args.log else None

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    payload = (args.message + "\n").encode("utf-8")
    for i in range(args.count):
        s.sendto(payload, (args.host, args.port))
        log_line(log_path, f"am trimis datagrama {i+1}/{args.count} către {args.host}:{args.port}")
        time.sleep(args.delay)
    try:
        s.close()
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
