#!/usr/bin/env python3
"""
TCP Echo Server/Client pentru testarea conectivității SDN

Aplicație simplă pentru generarea de trafic TCP și verificarea
politicilor de rețea în topologii SDN.

Plan de porturi Week 6:
    TCP_APP_PORT = 9090
    UDP_APP_PORT = 9091
    WEEK_PORT_BASE = 5600 (pentru porturi custom)

Utilizare:
    # Server
    python3 tcp_echo.py server --bind 10.0.6.12 --port 9090
    
    # Client
    python3 tcp_echo.py client --dst 10.0.6.12 --port 9090 --message "Hello TCP"

Rezolvix&Hypotheticalandrei
"""

from __future__ import annotations

import argparse
import socket
import sys


def run_server(bind_addr: str, port: int) -> None:
    """
    Server TCP echo - returnează mesajele primite.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        sock.bind((bind_addr, port))
        sock.listen(5)
        
        print(f"[TCP Echo Server]")
        print(f"Ascultă pe {bind_addr}:{port}")
        print("Apasă Ctrl+C pentru oprire.")
        print("-" * 40)
        
        while True:
            client_sock, client_addr = sock.accept()
            print(f"Conexiune de la {client_addr[0]}:{client_addr[1]}")
            
            try:
                while True:
                    data = client_sock.recv(1024)
                    if not data:
                        break
                    
                    message = data.decode("utf-8", errors="replace")
                    print(f"  Primit: {message.strip()}")
                    
                    # Echo back
                    client_sock.sendall(data)
                    print(f"  Trimis înapoi: {message.strip()}")
                    
            finally:
                client_sock.close()
                print(f"Conexiune închisă.\n")
                
    except KeyboardInterrupt:
        print("\nServer oprit.")
    finally:
        sock.close()


def run_client(dst: str, port: int, message: str) -> None:
    """
    Client TCP - trimite mesaj și afișează răspunsul.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    
    try:
        print(f"[TCP Echo Client]")
        print(f"Conectare la {dst}:{port}...")
        
        sock.connect((dst, port))
        print(f"Conectat!")
        
        # Trimite
        sock.sendall(message.encode())
        print(f"Trimis: {message}")
        
        # Primește echo
        response = sock.recv(1024).decode("utf-8", errors="replace")
        print(f"Primit: {response}")
        
        if response.strip() == message.strip():
            print("✓ Echo verificat - conexiune reușită!")
        
    except socket.timeout:
        print("✗ Conexiune expirată (timeout)!")
        print("  Cauze posibile:")
        print("  - Server-ul nu rulează")
        print("  - Politică SDN blochează traficul")
        print("  - Reguli de firewall")
        sys.exit(1)
    except ConnectionRefusedError:
        print("✗ Conexiune refuzată!")
        sys.exit(1)
    finally:
        sock.close()


def main():
    parser = argparse.ArgumentParser(description="TCP Echo Server/Client")
    subparsers = parser.add_subparsers(dest="mode")
    
    # Server
    srv = subparsers.add_parser("server")
    srv.add_argument("--bind", default="0.0.0.0")
    srv.add_argument("--port", type=int, default=9090)
    
    # Client
    cli = subparsers.add_parser("client")
    cli.add_argument("--dst", required=True)
    cli.add_argument("--port", type=int, default=9090)
    cli.add_argument("--message", default="Hello TCP")
    
    args = parser.parse_args()
    
    if args.mode == "server":
        run_server(args.bind, args.port)
    elif args.mode == "client":
        run_client(args.dst, args.port, args.message)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
