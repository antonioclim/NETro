#!/usr/bin/env python3
"""
FTP Demo Server - folosind pyftpdlib

Exemplu de server FTP real pentru comparație cu pseudo-FTP-ul nostru.
Demonstrează protocoalele și comenzile standard FTP.

Utilizare:
    python3 ftp_demo_server.py --host 127.0.0.1 --port 2121 --root ./server-files
"""

import argparse
import sys
from pathlib import Path

try:
    from pyftpdlib.authorizers import DummyAuthorizer
    from pyftpdlib.handlers import FTPHandler
    from pyftpdlib.servers import FTPServer
except ImportError:
    print("Eroare: pyftpdlib nu este instalat.")
    print("Instalați cu: pip install pyftpdlib --break-system-packages")
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="FTP Demo Server")
    parser.add_argument("--host", default="127.0.0.1", help="Adresă de bind")
    parser.add_argument("--port", type=int, default=2121, help="Port (default: 2121)")
    parser.add_argument("--root", default="./server-files", help="Director root")
    parser.add_argument("--user", default="test", help="Username")
    parser.add_argument("--password", default="12345", help="Password")
    parser.add_argument("--passive-ports", default="60000-60100", 
                        help="Range de porturi passive")
    
    args = parser.parse_args()
    
    # Asigurăm că directorul root există
    root_path = Path(args.root).resolve()
    root_path.mkdir(parents=True, exist_ok=True)
    
    # Configurăm autorizarea
    authorizer = DummyAuthorizer()
    
    # Adăugăm utilizatorul cu toate permisiunile
    # Permisiuni: e=cwd, l=list, r=retr, a=appe, d=delete, f=rename, m=mkdir, w=stor
    authorizer.add_user(args.user, args.password, str(root_path), perm="elradfmw")
    
    # Configurăm handler-ul
    handler = FTPHandler
    handler.authorizer = authorizer
    handler.banner = "Pseudo-FTP Demo Server (pyftpdlib)"
    
    # Configurăm porturile passive
    start_port, end_port = map(int, args.passive_ports.split("-"))
    handler.passive_ports = range(start_port, end_port + 1)
    
    # Creăm și pornim serverul
    address = (args.host, args.port)
    server = FTPServer(address, handler)
    
    # Configurări server
    server.max_cons = 256
    server.max_cons_per_ip = 5
    
    print(f"[FTP SERVER] Pornit pe {args.host}:{args.port}")
    print(f"[FTP SERVER] Root: {root_path}")
    print(f"[FTP SERVER] User: {args.user}")
    print(f"[FTP SERVER] Passive ports: {args.passive_ports}")
    print("[FTP SERVER] Ctrl+C pentru oprire")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[FTP SERVER] Oprire...")
        server.close_all()


if __name__ == "__main__":
    main()
