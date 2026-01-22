#!/usr/bin/env python3
"""
NAT Observer – Aplicație pentru observarea traducerii NAT/PAT

Această aplicație demonstrează cum serverul "public" vede conexiunile
din spatele unui NAT. Toate conexiunile de la hosturi private apar
ca venind de la IP-ul public al router-ului NAT, diferențiate prin porturi.

Utilizare:
    # Pe server (h3 - în rețeaua publică)
    python3 nat_observer.py server --bind 203.0.113.2 --port 5000
    
    # Pe clienți (h1, h2 - în rețeaua privată)
    python3 nat_observer.py client --host 203.0.113.2 --port 5000 --msg "Hello from h1"

Ce observăm:
- Serverul vede toate conexiunile ca venind de la 203.0.113.1 (IP-ul NAT)
- Fiecare conexiune are un port sursă diferit (esența PAT)
- Adresele private (192.168.1.x) nu sunt vizibile din exterior

Revolvix&Hypotheticalandrei
"""

from __future__ import annotations

import argparse
import socket
import sys
from datetime import datetime


def run_server(bind_addr: str, port: int) -> None:
    """
    Pornește un server TCP care afișează IP:port sursă pentru fiecare conexiune.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        sock.bind((bind_addr, port))
        sock.listen(5)
        
        print(f"[NAT Observer Server]")
        print(f"Ascultă pe {bind_addr}:{port}")
        print(f"Așteaptă conexiuni...")
        print("-" * 60)
        
        while True:
            client_sock, client_addr = sock.accept()
            client_ip, client_port = client_addr
            
            try:
                # Primește mesajul
                data = client_sock.recv(1024)
                message = data.decode("utf-8", errors="replace").strip()
                
                # Afișează informațiile
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"[{timestamp}] Conexiune de la {client_ip}:{client_port}")
                print(f"            Mesaj: {message}")
                print()
                
                # Trimite confirmare
                response = f"Primit de la {client_ip}:{client_port}\n"
                client_sock.sendall(response.encode())
                
            finally:
                client_sock.close()
                
    except KeyboardInterrupt:
        print("\nServer oprit.")
    finally:
        sock.close()


def run_client(host: str, port: int, message: str) -> None:
    """
    Conectează-te la server și trimite un mesaj.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)
    
    try:
        print(f"[NAT Observer Client]")
        print(f"Conectare la {host}:{port}...")
        
        sock.connect((host, port))
        
        # Afișează adresa locală (va fi IP-ul privat)
        local_addr = sock.getsockname()
        print(f"Adresă locală: {local_addr[0]}:{local_addr[1]}")
        
        # Trimite mesajul
        sock.sendall(message.encode())
        print(f"Trimis: {message}")
        
        # Primește răspunsul
        response = sock.recv(1024).decode("utf-8", errors="replace")
        print(f"Răspuns server: {response}")
        
    except socket.timeout:
        print("Conexiune expirată (timeout)!")
        sys.exit(1)
    except ConnectionRefusedError:
        print("Conexiune refuzată! Serverul rulează?")
        sys.exit(1)
    finally:
        sock.close()


def main():
    parser = argparse.ArgumentParser(
        description="NAT Observer - demonstrație traducere PAT"
    )
    
    subparsers = parser.add_subparsers(dest="mode", help="Mod de operare")
    
    # Server mode
    server_parser = subparsers.add_parser("server", help="Pornește serverul")
    server_parser.add_argument(
        "--bind", default="0.0.0.0",
        help="Adresa de bind (default: 0.0.0.0)"
    )
    server_parser.add_argument(
        "--port", type=int, default=5000,
        help="Port de ascultare (default: 5000)"
    )
    
    # Client mode
    client_parser = subparsers.add_parser("client", help="Pornește clientul")
    client_parser.add_argument(
        "--host", required=True,
        help="Adresa serverului"
    )
    client_parser.add_argument(
        "--port", type=int, default=5000,
        help="Portul serverului (default: 5000)"
    )
    client_parser.add_argument(
        "--msg", "--message", default="Hello from NAT client",
        help="Mesajul de trimis"
    )
    
    args = parser.parse_args()
    
    if args.mode == "server":
        run_server(args.bind, args.port)
    elif args.mode == "client":
        run_client(args.host, args.port, args.msg)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
