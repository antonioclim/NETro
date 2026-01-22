"""Server TCP simplu (echo) pentru laborator.

Pornește un server TCP care primește date și răspunde cu același payload.
Este util pentru a genera trafic clar de observat în pcap (SYN/SYN-ACK/ACK, payload, FIN/RST).
"""

from __future__ import annotations

import argparse
import socket
import threading
import time
from pathlib import Path
from typing import Optional


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Server TCP (echo) pentru laborator.")
    p.add_argument("--host", default="0.0.0.0", help="Adresa pe care ascultă serverul")
    p.add_argument("--port", type=int, default=9090, help="Portul TCP de ascultare")
    p.add_argument("--timeout", type=float, default=5.0, help="Timeout pentru socket-uri (secunde)")
    p.add_argument("--log", default="", help="Cale opțională către fișierul de log")
    return p


def log_line(path: Optional[Path], msg: str) -> None:
    ts = time.strftime("%H:%M:%S")
    line = f"[tcp_server {ts}] {msg}"
    print(line, flush=True)
    if path:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as f:
            f.write(line + "\n")


def handle_client(conn: socket.socket, addr: tuple[str, int], timeout: float, log_path: Optional[Path]) -> None:
    ip, port = addr[0], addr[1]
    log_line(log_path, f"Conexiune de la {ip}:{port}")
    conn.settimeout(timeout)
    try:
        while True:
            data = conn.recv(4096)
            if not data:
                break
            # Păstrăm bytes, dar logăm un text sigur
            preview = data[:80].decode("utf-8", errors="replace")
            log_line(log_path, f"Am primit {len(data)} bytes: {preview!r}")
            conn.sendall(data)
    except socket.timeout:
        log_line(log_path, f"Timeout pentru {ip}:{port}")
    except Exception as e:
        log_line(log_path, f"Eroare pentru {ip}:{port}: {e}")
    finally:
        try:
            conn.close()
        except Exception:
            pass
        log_line(log_path, f"Închis {ip}:{port}")


def main() -> int:
    args = build_parser().parse_args()
    host, port, timeout = args.host, args.port, args.timeout
    log_path = Path(args.log) if args.log else None

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host, port))
    s.listen(50)
    log_line(log_path, f"Ascult pe {host}:{port}")

    try:
        while True:
            conn, addr = s.accept()
            t = threading.Thread(
                target=handle_client, args=(conn, (addr[0], addr[1]), timeout, log_path), daemon=True
            )
            t.start()
    except KeyboardInterrupt:
        log_line(log_path, "Oprire la KeyboardInterrupt")
        return 0
    finally:
        try:
            s.close()
        except Exception:
            pass

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
