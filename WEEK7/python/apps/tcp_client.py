"""Client TCP pentru demo-urile din Săptămâna 7.

Trimite un singur mesaj și verifică răspunsul (echo).
"""

from __future__ import annotations

import argparse
import socket
import time
from pathlib import Path
from typing import Optional


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Client TCP simplu (Săptămâna 7).")
    p.add_argument("--host", required=True, help="Adresa sau numele serverului")
    p.add_argument("--port", type=int, default=9090, help="Portul serverului (implicit: 9090)")
    p.add_argument("--message", default="hello", help="Mesajul de trimis (implicit: hello)")
    p.add_argument("--timeout", type=float, default=3.0, help="Timeout în secunde (implicit: 3)")
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

    msg_bytes = (args.message + "\n").encode("utf-8")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(args.timeout)

    try:
        log_line(log_path, f"conectare la {args.host}:{args.port}")
        s.connect((args.host, args.port))
        s.sendall(msg_bytes)
        data = s.recv(4096)
        if not data:
            log_line(log_path, "nu am primit răspuns")
            return 2
        echoed = data.decode("utf-8", errors="replace").strip()
        log_line(log_path, f"primit: {echoed}")
        if echoed != args.message:
            log_line(log_path, "echo diferit de mesaj")
            return 3
        log_line(log_path, "ok")
        return 0
    except socket.timeout:
        log_line(log_path, "timeout")
        return 4
    except ConnectionRefusedError:
        log_line(log_path, "conexiune refuzată")
        return 5
    except Exception as exc:
        log_line(log_path, f"eroare: {exc}")
        return 6
    finally:
        try:
            s.close()
        except Exception:
            pass


if __name__ == "__main__":
    raise SystemExit(main())
