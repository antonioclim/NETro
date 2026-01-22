#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  Exercițiul 4: TCP Echo Server                                               ║
║  Săptămâna 3 — Rețele de Calculatoare                                        ║
╚══════════════════════════════════════════════════════════════════════════════╝

SCOPUL DIDACTIC:
    - Server TCP minimal pentru teste
    - Pattern standard: accept → recv → send → close
    - Transformare simplă (uppercase) pentru vizibilitate

UTILIZARE:
    Serverul primește date și le returnează cu litere mari (uppercase).
    Este util ca "țintă" pentru TCP tunnel sau pentru teste de conectivitate.

RULARE:
    python3 ex04_echo_server.py --listen 0.0.0.0:8080

    # Test cu netcat:
    echo "hello" | nc localhost 8080
    # Output: HELLO
"""
from __future__ import annotations

import argparse
import socket
import sys
import threading
from datetime import datetime


BUFFER_SIZE = 4096


def timestamp() -> str:
    return datetime.now().strftime("%H:%M:%S.%f")[:-3]


def log(level: str, message: str) -> None:
    print(f"[{timestamp()}] [{level}] {message}")


def handle_client(client_socket: socket.socket, client_addr: tuple[str, int]) -> None:
    """Gestionează un client: primește date, răspunde cu uppercase."""
    ip, port = client_addr
    log("CONN", f"Client conectat: {ip}:{port}")
    
    with client_socket:
        total_bytes = 0
        while True:
            data = client_socket.recv(BUFFER_SIZE)
            if not data:
                break
            
            total_bytes += len(data)
            
            # Transformare uppercase pentru vizibilitate
            response = data.upper()
            client_socket.sendall(response)
            
            log("ECHO", f"{ip}:{port} → {data!r} → {response!r}")
    
    log("DISC", f"Client deconectat: {ip}:{port} (total: {total_bytes} bytes)")


def parse_addr(addr_str: str) -> tuple[str, int]:
    if ":" not in addr_str:
        return "0.0.0.0", int(addr_str)
    host, port = addr_str.rsplit(":", 1)
    return host, int(port)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="ex04_echo_server.py",
        description="Server TCP echo simplu (returnează uppercase)."
    )
    parser.add_argument(
        "--listen", default="0.0.0.0:8080",
        help="Adresa de ascultare (host:port sau doar port)"
    )
    parser.add_argument(
        "--single", action="store_true",
        help="Mod single-client (fără threading)"
    )
    args = parser.parse_args(argv)
    
    host, port = parse_addr(args.listen)
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server.bind((host, port))
        server.listen(5)
        log("INFO", f"Echo server pornit pe {host}:{port}")
        log("INFO", "Aștept conexiuni... (Ctrl+C pentru oprire)")
        
        while True:
            client_socket, client_addr = server.accept()
            
            if args.single:
                # Mod blocking (un client la un moment dat)
                handle_client(client_socket, client_addr)
            else:
                # Mod threaded (mai mulți clienți simultan)
                t = threading.Thread(
                    target=handle_client,
                    args=(client_socket, client_addr),
                    daemon=True
                )
                t.start()
                
    except KeyboardInterrupt:
        log("INFO", "Oprire (Ctrl+C)")
    except OSError as e:
        log("ERROR", f"Nu pot asculta pe {host}:{port}: {e}")
        return 1
    finally:
        server.close()
        log("INFO", "Server închis")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
