"""Proxy TCP în spațiul utilizatorului care acționează ca un filtru simplu.

Acesta este un instrument didactic:
- demonstrează interceptarea în spațiul utilizatorului (nivel aplicație)
- poate permite sau respinge conexiuni pe baza unor liste allow/block de IP-uri sursă

Nu este un înlocuitor pentru filtrarea bazată pe iptables.
"""

from __future__ import annotations

import argparse
import socket
import threading
import time
from pathlib import Path
from typing import Optional, Set


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Filtru proxy TCP (Săptămâna 7).")
    p.add_argument("--listen-host", default="0.0.0.0", help="Adresa de bind a proxy-ului (implicit: 0.0.0.0)")
    p.add_argument("--listen-port", type=int, default=8888, help="Portul de bind al proxy-ului (implicit: 8888)")
    p.add_argument("--upstream-host", required=True, help="Host-ul serverului upstream")
    p.add_argument("--upstream-port", type=int, default=9090, help="Portul serverului upstream (implicit: 9090)")
    p.add_argument("--allow", default="", help="IP-uri sursă permise, separate prin virgulă (gol înseamnă permite tot)")
    p.add_argument("--block", default="", help="IP-uri sursă blocate, separate prin virgulă (gol înseamnă nu bloca nimic)")
    p.add_argument("--log", default="", help="Cale opțională către fișierul de log")
    p.add_argument("--timeout", type=float, default=5.0, help="Timeout socket în secunde (implicit: 5)")
    return p


def parse_ip_set(s: str) -> Set[str]:
    out: Set[str] = set()
    for part in s.split(","):
        part = part.strip()
        if part:
            out.add(part)
    return out


def log_line(path: Optional[Path], line: str) -> None:
    stamp = time.strftime("%Y-%m-%d %H:%M:%S")
    msg = f"[{stamp}] {line}"
    print(msg, flush=True)
    if path:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as f:
            f.write(msg + "\n")


def pipe(src: socket.socket, dst: socket.socket, buf: int = 4096) -> None:
    try:
        while True:
            data = src.recv(buf)
            if not data:
                break
            dst.sendall(data)
    except Exception:
        pass
    finally:
        try:
            dst.shutdown(socket.SHUT_WR)
        except Exception:
            pass


def handle(
    conn: socket.socket,
    addr: tuple[str, int],
    upstream: tuple[str, int],
    allow: Set[str],
    block: Set[str],
    log_path: Optional[Path],
    timeout: float,
) -> None:
    src_ip = addr[0]
    conn.settimeout(timeout)

    if src_ip in block or (allow and src_ip not in allow):
        log_line(log_path, f"conexiune blocată de la {src_ip}:{addr[1]}")
        try:
            conn.close()
        except Exception:
            pass
        return

    log_line(log_path, f"conexiune permisă de la {src_ip}:{addr[1]} către upstream {upstream[0]}:{upstream[1]}")

    up = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    up.settimeout(timeout)
    try:
        up.connect(upstream)
    except Exception as exc:
        log_line(log_path, f"conectarea către upstream a eșuat: {exc}")
        try:
            conn.close()
        except Exception:
            pass
        return

    t1 = threading.Thread(target=pipe, args=(conn, up), daemon=True)
    t2 = threading.Thread(target=pipe, args=(up, conn), daemon=True)
    t1.start()
    t2.start()
    t1.join()
    t2.join()

    try:
        conn.close()
    except Exception:
        pass
    try:
        up.close()
    except Exception:
        pass

    log_line(log_path, f"conexiune închisă pentru {src_ip}:{addr[1]}")


def main() -> int:
    args = build_parser().parse_args()
    allow = parse_ip_set(args.allow)
    block = parse_ip_set(args.block)
    log_path = Path(args.log) if args.log else None

    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((args.listen_host, args.listen_port))
    srv.listen(50)

    upstream = (args.upstream_host, args.upstream_port)
    log_line(
        log_path,
        f"proxy ascultă pe {args.listen_host}:{args.listen_port} și forward către {upstream[0]}:{upstream[1]}",
    )

    try:
        while True:
            conn, addr = srv.accept()
            th = threading.Thread(
                target=handle, args=(conn, addr, upstream, allow, block, log_path, args.timeout), daemon=True
            )
            th.start()
    except KeyboardInterrupt:
        log_line(log_path, "întrerupt")
    finally:
        try:
            srv.close()
        except Exception:
            pass
        log_line(log_path, "proxy oprit")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
