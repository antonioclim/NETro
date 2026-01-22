#!/usr/bin/env python3
"""
Server FTP cu pyftpdlib - Săptămâna 10

Demonstrează:
- Server FTP minimal cu autentificare
- Mod pasiv (necesar pentru NAT/Docker)
- Permisiuni pentru upload/download

Autori: Colectivul Rețele de Calculatoare, ASE București
Revolvix&Hypotheticalandrei
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer


def main() -> int:
    parser = argparse.ArgumentParser(description="Server FTP minimal")
    parser.add_argument("--bind", default="0.0.0.0", help="Adresă bind")
    parser.add_argument("--port", type=int, default=2121, help="Port FTP")
    parser.add_argument("--user", default="labftp", help="Username")
    parser.add_argument("--password", default="labftp", help="Parolă")
    parser.add_argument("--root", default="/home/ftp", help="Director rădăcină")
    parser.add_argument("--passive-start", type=int, default=30000, help="Port pasiv start")
    parser.add_argument("--passive-end", type=int, default=30009, help="Port pasiv end")
    args = parser.parse_args()
    
    # Creare director rădăcină
    root = Path(args.root)
    root.mkdir(parents=True, exist_ok=True)
    (root / "uploads").mkdir(exist_ok=True)
    
    # Fișier de test
    welcome_file = root / "welcome.txt"
    if not welcome_file.exists():
        welcome_file.write_text(
            "Bine ați venit la serverul FTP!\n"
            "Săptămâna 10 - Rețele de Calculatoare\n"
            "Revolvix&Hypotheticalandrei\n"
        )
    
    # Configurare autorizare
    authorizer = DummyAuthorizer()
    # Permisiuni: e=list, l=list, r=read, a=append, d=delete, f=rename, m=mkdir, w=write, M=chmod
    authorizer.add_user(args.user, args.password, str(root), perm="elradfmwMT")
    authorizer.add_anonymous(str(root), perm="elr")  # Anonymous: doar citire
    
    # Configurare handler
    handler = FTPHandler
    handler.authorizer = authorizer
    handler.banner = "FTP Server - Săptămâna 10 - Rețele de Calculatoare"
    
    # Mod pasiv (necesar pentru Docker)
    handler.passive_ports = range(args.passive_start, args.passive_end + 1)
    
    # Logging
    handler.log_prefix = "[%(username)s]@%(remote_ip)s "
    
    # Creare și pornire server
    server = FTPServer((args.bind, args.port), handler)
    server.max_cons = 256
    server.max_cons_per_ip = 10
    
    print(f"[ftp] Server pornit pe {args.bind}:{args.port}")
    print(f"[ftp] User: {args.user}/{args.password}")
    print(f"[ftp] Root: {args.root}")
    print(f"[ftp] Porturi pasive: {args.passive_start}-{args.passive_end}")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[ftp] Oprire...")
    finally:
        server.close_all()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
