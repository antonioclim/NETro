#!/usr/bin/env python3
"""
UDP Echo Server/Client pentru testarea politicilor SDN

Aplicație pentru generarea de trafic UDP și verificarea
politicilor allow/block în rețele SDN.

Plan de porturi Week 6:
    TCP_APP_PORT = 9090
    UDP_APP_PORT = 9091
    WEEK_PORT_BASE = 5600 (pentru porturi custom)

Utilizare:
    # Server
    python3 udp_echo.py server --bind 10.0.6.13 --port 9091
    
    # Client
    python3 udp_echo.py client --dst 10.0.6.13 --port 9091 --message "Hello UDP"

Rezolvix&Hypotheticalandrei
"""

from __future__ import annotations

import argparse
import socket
import sys


def run_server(bind_addr: str, port: int) -> None:
    """
    Server UDP echo - returnează datagramele primite.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        sock.bind((bind_addr, port))
        
        print(f"[UDP Echo Server]")
        print(f"Ascultă pe {bind_addr}:{port}")
        print("Apasă Ctrl+C pentru oprire.")
        print("-" * 40)
        
        while True:
            data, client_addr = sock.recvfrom(1024)
            message = data.decode("utf-8", errors="replace")
            
            print(f"De la {client_addr[0]}:{client_addr[1]}: {message.strip()}")
            
            # Echo back
            sock.sendto(data, client_addr)
            print(f"  → Trimis înapoi")
            
    except KeyboardInterrupt:
        print("\nServer oprit.")
    finally:
        sock.close()


def run_client(dst: str, port: int, message: str) -> None:
    """
    Client UDP - trimite datagramă și așteaptă răspuns.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(3)
    
    try:
        print(f"[UDP Echo Client]")
        print(f"Destinație: {dst}:{port}")
        
        # Trimite
        sock.sendto(message.encode(), (dst, port))
        print(f"Trimis: {message}")
        
        # Așteaptă răspuns
        response, server_addr = sock.recvfrom(1024)
        print(f"Primit: {response.decode()}")
        
        print("✓ Comunicare UDP reușită!")
        
    except socket.timeout:
        print("✗ Niciun răspuns primit (timeout)!")
        print("  Cauze posibile:")
        print("  - Server-ul nu rulează")
        print("  - Trafic UDP blocat de politica SDN")
        print("  - Verifică ALLOW_UDP_TO_H3 în controller")
        sys.exit(1)
    finally:
        sock.close()


def main():
    parser = argparse.ArgumentParser(description="UDP Echo Server/Client")
    subparsers = parser.add_subparsers(dest="mode")
    
    # Server
    srv = subparsers.add_parser("server")
    srv.add_argument("--bind", default="0.0.0.0")
    srv.add_argument("--port", type=int, default=9091)
    
    # Client
    cli = subparsers.add_parser("client")
    cli.add_argument("--dst", required=True)
    cli.add_argument("--port", type=int, default=9091)
    cli.add_argument("--message", default="Hello UDP")
    
    args = parser.parse_args()
    
    if args.mode == "server":
        run_server(args.bind, args.port)
    elif args.mode == "client":
        run_client(args.dst, args.port, args.message)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
