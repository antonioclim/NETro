#!/usr/bin/env python3
"""
FTP Demo Client - folosind ftplib (biblioteca standard Python)

Client FTP pentru comparație cu pseudo-FTP-ul nostru.

Utilizare:
    python3 ftp_demo_client.py --host 127.0.0.1 --port 2121 --user test --password 12345 list
    python3 ftp_demo_client.py ... get hello.txt
    python3 ftp_demo_client.py ... put myfile.txt
"""

import argparse
import sys
from ftplib import FTP
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="FTP Demo Client")
    parser.add_argument("--host", default="127.0.0.1", help="Adresa serverului")
    parser.add_argument("--port", type=int, default=2121, help="Port")
    parser.add_argument("--user", default="test", help="Username")
    parser.add_argument("--password", default="12345", help="Password")
    parser.add_argument("--local-dir", default="./client-files", help="Director local")
    parser.add_argument("--passive", action="store_true", default=True, 
                        help="Mod pasiv (default)")
    parser.add_argument("--active", action="store_true", help="Mod activ")
    parser.add_argument("command", help="Comandă: list, get, put, pwd")
    parser.add_argument("argument", nargs="?", help="Argument pentru comandă")
    
    args = parser.parse_args()
    
    local_dir = Path(args.local_dir).resolve()
    local_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # Conectare
        ftp = FTP()
        ftp.connect(args.host, args.port)
        print(f"[CLIENT] Conectat la {args.host}:{args.port}")
        
        # Setăm modul activ/pasiv
        if args.active:
            ftp.set_pasv(False)
            print("[CLIENT] Mod activ")
        else:
            ftp.set_pasv(True)
            print("[CLIENT] Mod pasiv")
        
        # Autentificare
        response = ftp.login(args.user, args.password)
        print(f"[CLIENT] Login: {response}")
        
        # Executăm comanda
        cmd = args.command.lower()
        
        if cmd == "list" or cmd == "ls":
            print("[CLIENT] === Listare director ===")
            ftp.retrlines("LIST")
        
        elif cmd == "pwd":
            print(f"[CLIENT] Director curent: {ftp.pwd()}")
        
        elif cmd == "get":
            if not args.argument:
                print("Utilizare: get <filename>")
                return 1
            
            local_path = local_dir / args.argument
            print(f"[CLIENT] Descărcare: {args.argument} -> {local_path}")
            
            with open(local_path, "wb") as f:
                ftp.retrbinary(f"RETR {args.argument}", f.write)
            
            print(f"[CLIENT] ✓ Salvat: {local_path} ({local_path.stat().st_size} bytes)")
        
        elif cmd == "put":
            if not args.argument:
                print("Utilizare: put <filename>")
                return 1
            
            local_path = local_dir / args.argument
            if not local_path.is_file():
                print(f"Fișier inexistent: {local_path}")
                return 1
            
            print(f"[CLIENT] Încărcare: {local_path}")
            
            with open(local_path, "rb") as f:
                ftp.storbinary(f"STOR {args.argument}", f)
            
            print(f"[CLIENT] ✓ Încărcat: {args.argument}")
        
        else:
            print(f"Comandă necunoscută: {cmd}")
            return 1
        
        # Deconectare
        ftp.quit()
        print("[CLIENT] Deconectat")
        
    except Exception as e:
        print(f"[CLIENT] Eroare: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
