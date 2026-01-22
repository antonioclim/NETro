#!/usr/bin/env python3
"""tcp_echo_client.py — Client TCP echo pentru demonstrații.

Funcționalități:
  - Conectează la un server TCP
  - Trimite un mesaj și verifică echo-ul
  - Raportează latența și validitatea

Utilizare:
  python3 tcp_echo_client.py --host 10.0.0.2 --port 9000 --message "hello"
"""

from __future__ import annotations

import argparse
import socket
import sys
import time
from datetime import datetime


def log(msg: str) -> None:
    """Logging cu timestamp."""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    print(f"[{ts}] [echo-client] {msg}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="TCP Echo Client")
    parser.add_argument("--host", required=True, help="Adresa serverului")
    parser.add_argument("--port", type=int, default=9000, help="Portul serverului")
    parser.add_argument("--message", default="hello", help="Mesajul de trimis")
    parser.add_argument("--timeout", type=float, default=5.0, help="Timeout (s)")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    
    log(f"Conectare la {args.host}:{args.port}...")
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(args.timeout)
    
    try:
        start = time.time()
        sock.connect((args.host, args.port))
        connect_time = (time.time() - start) * 1000
        log(f"Conectat (timp conectare: {connect_time:.2f} ms)")
        
        message = args.message.encode("utf-8")
        log(f"Trimit: {message!r}")
        
        start = time.time()
        sock.sendall(message)
        
        response = sock.recv(4096)
        rtt = (time.time() - start) * 1000
        
        log(f"Primit: {response!r}")
        log(f"RTT: {rtt:.2f} ms")
        
        if response == message:
            log("✓ Echo valid")
            return 0
        else:
            log("✗ Echo nepotrivit!")
            return 1
    
    except socket.timeout:
        log("✗ Timeout conexiune")
        return 1
    except ConnectionRefusedError:
        log("✗ Conexiune refuzată")
        return 1
    except Exception as e:
        log(f"✗ Eroare: {e}")
        return 1
    finally:
        sock.close()


if __name__ == "__main__":
    raise SystemExit(main())
