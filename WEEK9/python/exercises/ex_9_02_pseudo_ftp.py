#!/usr/bin/env python3
"""
Exercițiul 9.02 – Server/Client Pseudo-FTP cu Sesiune și Prezentare

═══════════════════════════════════════════════════════════════════════════════
OBIECTIVE:
═══════════════════════════════════════════════════════════════════════════════
1. Implementarea conceptelor de sesiune (L5): autentificare, stare, CWD
2. Implementarea conceptelor de prezentare (L6): header binar, compresie
3. Separarea canalelor de control și date (similar FTP)
4. Moduri activ/pasiv pentru transfer de date

═══════════════════════════════════════════════════════════════════════════════
PROTOCOL PSEUDO-FTP (Simplificat pentru scop didactic):
═══════════════════════════════════════════════════════════════════════════════

CONEXIUNE DE CONTROL (port 3333):
┌─────────────────────────────────────────────────────────────────────────────┐
│ Comenzi text (ca FTP):                                                      │
│   USER <username>     - Setează utilizatorul                               │
│   PASS <password>     - Autentificare                                       │
│   PWD                 - Afișează directorul curent                          │
│   CWD <path>          - Schimbă directorul                                  │
│   LIST                - Listează fișierele                                  │
│   ACTIVE_GET <file>   - Descarcă fișier în mod activ                       │
│   PASSIVE_GET <file>  - Descarcă fișier în mod pasiv                       │
│   ACTIVE_PUT <file>   - Încarcă fișier în mod activ                        │
│   PASSIVE_PUT <file>  - Încarcă fișier în mod pasiv                        │
│   QUIT                - Încheie sesiunea                                    │
└─────────────────────────────────────────────────────────────────────────────┘

CONEXIUNE DE DATE (port dinamic):
┌─────────────────────────────────────────────────────────────────────────────┐
│ Header binar (12 bytes):                                                    │
│   - Magic: 2 bytes ("PF")                                                   │
│   - Version: 1 byte                                                         │
│   - Flags: 1 byte (bit 0 = compresie gzip)                                 │
│   - Length: 4 bytes (big-endian)                                            │
│   - CRC32: 4 bytes                                                          │
│                                                                             │
│ Payload: N bytes (opțional comprimat)                                       │
└─────────────────────────────────────────────────────────────────────────────┘

═══════════════════════════════════════════════════════════════════════════════
UTILIZARE:
═══════════════════════════════════════════════════════════════════════════════

# Server
python3 ex_9_02_pseudo_ftp.py server --host 127.0.0.1 --port 3333 --root ./server-files

# Client - comenzi individuale
python3 ex_9_02_pseudo_ftp.py client --host 127.0.0.1 --port 3333 --user test --password 12345 list
python3 ex_9_02_pseudo_ftp.py client ... get hello.txt
python3 ex_9_02_pseudo_ftp.py client ... put myfile.txt

# Client - interactiv
python3 ex_9_02_pseudo_ftp.py client ... --interactive
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import os
import socket
import struct
import sys
import threading
import zlib
from pathlib import Path
from typing import Optional


# =============================================================================
# Configurare Protocol
# =============================================================================

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 3333
BUFFER_SIZE = 8192
DEFAULT_USER = "test"
DEFAULT_PASS = "12345"

# Header format pentru transfer de date (L6 - Prezentare)
# Magic(2) + Version(1) + Flags(1) + Length(4) + CRC32(4) = 12 bytes
HEADER_FORMAT = "!2sBBII"
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)
MAGIC = b"PF"  # Pseudo-FTP
VERSION = 1
FLAG_GZIP = 0x01


# =============================================================================
# Funcții de Protocol (Nivelul Prezentare - L6)
# =============================================================================

def pack_data(payload: bytes, use_gzip: bool = False) -> bytes:
    """
    Împachetează payload-ul cu header binar (L6).
    
    Demonstrează:
    - Framing: header cu lungime pentru delimitare mesaje
    - Compresie: opțional gzip
    - Integritate: CRC32 checksum
    """
    flags = FLAG_GZIP if use_gzip else 0
    
    # Compresie opțională
    if use_gzip and len(payload) > 0:
        payload = gzip.compress(payload)
    
    length = len(payload)
    crc = zlib.crc32(payload) & 0xFFFFFFFF
    
    header = struct.pack(HEADER_FORMAT, MAGIC, VERSION, flags, length, crc)
    return header + payload


def unpack_data(data: bytes) -> tuple[bytes, dict]:
    """
    Despachetează datele primite.
    
    Returns:
        (payload, metadata) unde metadata conține informații despre header
    """
    if len(data) < HEADER_SIZE:
        raise ValueError(f"Date insuficiente: {len(data)} < {HEADER_SIZE}")
    
    magic, version, flags, length, crc = struct.unpack(HEADER_FORMAT, data[:HEADER_SIZE])
    
    if magic != MAGIC:
        raise ValueError(f"Magic invalid: {magic}")
    
    payload = data[HEADER_SIZE:HEADER_SIZE + length]
    
    if len(payload) != length:
        raise ValueError(f"Payload incomplet: {len(payload)} != {length}")
    
    # Verificare CRC
    calc_crc = zlib.crc32(payload) & 0xFFFFFFFF
    if calc_crc != crc:
        raise ValueError(f"CRC invalid: {calc_crc:08x} != {crc:08x}")
    
    # Decompresie dacă e necesar
    if flags & FLAG_GZIP:
        payload = gzip.decompress(payload)
    
    return payload, {
        "version": version,
        "flags": flags,
        "compressed": bool(flags & FLAG_GZIP),
        "wire_length": length,
        "crc": crc,
    }


def recv_all(sock: socket.socket, length: int) -> bytes:
    """Primește exact `length` bytes de pe socket."""
    data = b""
    while len(data) < length:
        chunk = sock.recv(min(length - len(data), BUFFER_SIZE))
        if not chunk:
            raise ConnectionError("Conexiune închisă prematur")
        data += chunk
    return data


def recv_framed(sock: socket.socket) -> tuple[bytes, dict]:
    """Primește un mesaj cu framing (header + payload)."""
    # Citim header-ul
    header = recv_all(sock, HEADER_SIZE)
    magic, version, flags, length, crc = struct.unpack(HEADER_FORMAT, header)
    
    if magic != MAGIC:
        raise ValueError(f"Magic invalid: {magic}")
    
    # Citim payload-ul
    payload = recv_all(sock, length) if length > 0 else b""
    
    return unpack_data(header + payload)


# =============================================================================
# Stare Sesiune (Nivelul Sesiune - L5)
# =============================================================================

class Session:
    """
    Reprezentare a unei sesiuni client (L5).
    
    Demonstrează conceptele de sesiune:
    - Autentificare (USER/PASS)
    - Stare persistentă (authenticated, cwd)
    - Expirare (nu implementată pentru simplitate)
    """
    
    def __init__(self, root_dir: Path):
        self.root_dir = root_dir.resolve()
        self.authenticated = False
        self.username: Optional[str] = None
        self.cwd = Path("/")  # Director curent relativ
        
    def is_authenticated(self) -> bool:
        return self.authenticated
    
    def login(self, username: str, password: str) -> bool:
        """Autentificare simplă (demo)."""
        # Pentru demo, acceptăm test/12345
        if username == DEFAULT_USER and password == DEFAULT_PASS:
            self.authenticated = True
            self.username = username
            return True
        return False
    
    def get_absolute_path(self, path: str) -> Path:
        """Convertește un path relativ la unul absolut în sandbox."""
        if path.startswith("/"):
            rel_path = Path(path[1:])
        else:
            rel_path = self.cwd / path
        
        # Normalizare și securizare
        abs_path = (self.root_dir / rel_path).resolve()
        
        # Verificare că suntem în sandbox
        try:
            abs_path.relative_to(self.root_dir)
        except ValueError:
            raise PermissionError(f"Acces interzis: {path}")
        
        return abs_path
    
    def change_dir(self, path: str) -> bool:
        """Schimbă directorul curent."""
        try:
            abs_path = self.get_absolute_path(path)
            if abs_path.is_dir():
                self.cwd = abs_path.relative_to(self.root_dir)
                return True
        except (PermissionError, FileNotFoundError):
            pass
        return False


# =============================================================================
# Server Pseudo-FTP
# =============================================================================

class PseudoFTPServer:
    """Server pseudo-FTP cu suport pentru sesiune și moduri activ/pasiv."""
    
    def __init__(self, host: str, port: int, root_dir: Path):
        self.host = host
        self.port = port
        self.root_dir = root_dir.resolve()
        self.running = False
        
        # Asigurăm că directorul root există
        self.root_dir.mkdir(parents=True, exist_ok=True)
        
    def start(self):
        """Pornește serverul."""
        self.running = True
        
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind((self.host, self.port))
            server.listen(5)
            
            print(f"[SERVER] Pseudo-FTP pornit pe {self.host}:{self.port}")
            print(f"[SERVER] Root directory: {self.root_dir}")
            print(f"[SERVER] Credențiale demo: {DEFAULT_USER}/{DEFAULT_PASS}")
            print("[SERVER] Ctrl+C pentru oprire")
            
            while self.running:
                try:
                    client, addr = server.accept()
                    print(f"[SERVER] Conexiune nouă de la {addr}")
                    
                    thread = threading.Thread(
                        target=self.handle_client,
                        args=(client, addr),
                        daemon=True
                    )
                    thread.start()
                except KeyboardInterrupt:
                    print("\n[SERVER] Oprire...")
                    self.running = False
                    break
    
    def handle_client(self, client: socket.socket, addr):
        """Handler pentru un client conectat."""
        session = Session(self.root_dir)
        
        # Mesaj de bun venit (similar FTP)
        self.send_response(client, 220, "Pseudo-FTP Server Ready")
        
        try:
            while True:
                # Primim comanda
                data = client.recv(BUFFER_SIZE)
                if not data:
                    break
                
                command = data.decode("utf-8").strip()
                if not command:
                    continue
                
                print(f"[{addr}] <- {command}")
                
                # Procesăm comanda
                self.process_command(client, session, command)
                
        except (ConnectionResetError, BrokenPipeError):
            print(f"[{addr}] Conexiune pierdută")
        except Exception as e:
            print(f"[{addr}] Eroare: {e}")
        finally:
            client.close()
            print(f"[{addr}] Deconectat")
    
    def send_response(self, client: socket.socket, code: int, message: str):
        """Trimite un răspuns pe conexiunea de control."""
        response = f"{code} {message}\n"
        client.sendall(response.encode("utf-8"))
    
    def process_command(self, client: socket.socket, session: Session, command: str):
        """Procesează o comandă FTP-like."""
        parts = command.split(maxsplit=1)
        cmd = parts[0].upper()
        arg = parts[1] if len(parts) > 1 else ""
        
        # Comenzi care nu necesită autentificare
        if cmd == "USER":
            session.username = arg
            self.send_response(client, 331, "Username OK, need password")
            return
        
        if cmd == "PASS":
            if session.login(session.username or "", arg):
                self.send_response(client, 230, "Login successful")
            else:
                self.send_response(client, 530, "Login failed")
            return
        
        if cmd == "QUIT":
            self.send_response(client, 221, "Goodbye")
            return
        
        # Comenzi care necesită autentificare
        if not session.is_authenticated():
            self.send_response(client, 530, "Not logged in")
            return
        
        if cmd == "PWD":
            self.send_response(client, 257, f'"/{session.cwd}" is current directory')
        
        elif cmd == "CWD":
            if session.change_dir(arg):
                self.send_response(client, 250, f"Directory changed to /{session.cwd}")
            else:
                self.send_response(client, 550, "Failed to change directory")
        
        elif cmd == "LIST":
            self.cmd_list(client, session)
        
        elif cmd == "PASSIVE_GET":
            self.cmd_passive_get(client, session, arg)
        
        elif cmd == "ACTIVE_GET":
            self.cmd_active_get(client, session, arg)
        
        elif cmd == "PASSIVE_PUT":
            self.cmd_passive_put(client, session, arg)
        
        elif cmd == "ACTIVE_PUT":
            self.cmd_active_put(client, session, arg)
        
        else:
            self.send_response(client, 502, f"Command not implemented: {cmd}")
    
    def cmd_list(self, client: socket.socket, session: Session):
        """Listează fișierele din directorul curent."""
        try:
            dir_path = session.get_absolute_path(".")
            files = []
            
            for item in dir_path.iterdir():
                stat = item.stat()
                if item.is_dir():
                    files.append(f"drwxr-xr-x  - {item.name}/")
                else:
                    files.append(f"-rw-r--r--  {stat.st_size:>8} {item.name}")
            
            listing = "\n".join(sorted(files))
            self.send_response(client, 150, "Opening data connection")
            client.sendall(f"{listing}\n".encode("utf-8"))
            self.send_response(client, 226, "Directory listing complete")
            
        except Exception as e:
            self.send_response(client, 550, str(e))
    
    def cmd_passive_get(self, client: socket.socket, session: Session, filename: str):
        """GET în mod pasiv - serverul deschide un port pentru date."""
        try:
            file_path = session.get_absolute_path(filename)
            
            if not file_path.is_file():
                self.send_response(client, 550, "File not found")
                return
            
            # Deschidem un socket pentru date
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as data_server:
                data_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                data_server.bind((self.host, 0))
                data_server.listen(1)
                data_port = data_server.getsockname()[1]
                
                # Anunțăm clientul
                self.send_response(client, 227, f"Entering Passive Mode ({data_port})")
                
                # Așteptăm conexiunea clientului
                data_server.settimeout(30)
                data_conn, _ = data_server.accept()
                
                with data_conn:
                    # Citim și trimitem fișierul
                    content = file_path.read_bytes()
                    packed = pack_data(content, use_gzip=len(content) > 1024)
                    data_conn.sendall(packed)
                    
                    # Calculăm hash pentru verificare
                    sha256 = hashlib.sha256(content).hexdigest()
                    self.send_response(client, 226, f"Transfer complete (SHA256: {sha256[:16]}...)")
                    
        except Exception as e:
            self.send_response(client, 550, str(e))
    
    def cmd_active_get(self, client: socket.socket, session: Session, arg: str):
        """GET în mod activ - serverul se conectează la client."""
        try:
            parts = arg.split()
            if len(parts) != 2:
                self.send_response(client, 501, "Syntax: ACTIVE_GET <filename> <port>")
                return
            
            filename, port_str = parts
            data_port = int(port_str)
            file_path = session.get_absolute_path(filename)
            
            if not file_path.is_file():
                self.send_response(client, 550, "File not found")
                return
            
            # Obținem IP-ul clientului din conexiunea de control
            client_host = client.getpeername()[0]
            
            # Ne conectăm la client
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as data_conn:
                data_conn.connect((client_host, data_port))
                
                content = file_path.read_bytes()
                packed = pack_data(content, use_gzip=len(content) > 1024)
                data_conn.sendall(packed)
                
                sha256 = hashlib.sha256(content).hexdigest()
                self.send_response(client, 226, f"Transfer complete (SHA256: {sha256[:16]}...)")
                
        except Exception as e:
            self.send_response(client, 550, str(e))
    
    def cmd_passive_put(self, client: socket.socket, session: Session, filename: str):
        """PUT în mod pasiv - serverul deschide un port pentru a primi date."""
        try:
            file_path = session.get_absolute_path(filename)
            
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as data_server:
                data_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                data_server.bind((self.host, 0))
                data_server.listen(1)
                data_port = data_server.getsockname()[1]
                
                self.send_response(client, 227, f"Entering Passive Mode ({data_port})")
                
                data_server.settimeout(30)
                data_conn, _ = data_server.accept()
                
                with data_conn:
                    # Primim datele
                    raw_data = b""
                    while True:
                        chunk = data_conn.recv(BUFFER_SIZE)
                        if not chunk:
                            break
                        raw_data += chunk
                    
                    content, meta = unpack_data(raw_data)
                    file_path.write_bytes(content)
                    
                    sha256 = hashlib.sha256(content).hexdigest()
                    self.send_response(client, 226, f"Transfer complete (SHA256: {sha256[:16]}...)")
                    
        except Exception as e:
            self.send_response(client, 550, str(e))
    
    def cmd_active_put(self, client: socket.socket, session: Session, arg: str):
        """PUT în mod activ - serverul se conectează la client pentru a primi date."""
        try:
            parts = arg.split()
            if len(parts) != 2:
                self.send_response(client, 501, "Syntax: ACTIVE_PUT <filename> <port>")
                return
            
            filename, port_str = parts
            data_port = int(port_str)
            file_path = session.get_absolute_path(filename)
            
            client_host = client.getpeername()[0]
            
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as data_conn:
                data_conn.connect((client_host, data_port))
                
                raw_data = b""
                while True:
                    chunk = data_conn.recv(BUFFER_SIZE)
                    if not chunk:
                        break
                    raw_data += chunk
                
                content, meta = unpack_data(raw_data)
                file_path.write_bytes(content)
                
                sha256 = hashlib.sha256(content).hexdigest()
                self.send_response(client, 226, f"Transfer complete (SHA256: {sha256[:16]}...)")
                
        except Exception as e:
            self.send_response(client, 550, str(e))


# =============================================================================
# Client Pseudo-FTP
# =============================================================================

class PseudoFTPClient:
    """Client pseudo-FTP cu suport pentru moduri activ/pasiv."""
    
    def __init__(self, host: str, port: int, local_dir: Path):
        self.host = host
        self.port = port
        self.local_dir = local_dir.resolve()
        self.control: Optional[socket.socket] = None
        
        self.local_dir.mkdir(parents=True, exist_ok=True)
    
    def connect(self):
        """Stabilește conexiunea de control."""
        self.control = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.control.connect((self.host, self.port))
        
        # Citim mesajul de bun venit
        response = self.recv_response()
        print(f"[CLIENT] {response}")
    
    def close(self):
        """Închide conexiunea."""
        if self.control:
            self.control.close()
            self.control = None
    
    def send_command(self, command: str) -> str:
        """Trimite o comandă și primește răspunsul."""
        if not self.control:
            raise ConnectionError("Not connected")
        
        self.control.sendall(f"{command}\n".encode("utf-8"))
        return self.recv_response()
    
    def recv_response(self) -> str:
        """Primește un răspuns de pe conexiunea de control."""
        data = self.control.recv(BUFFER_SIZE)
        return data.decode("utf-8").strip()
    
    def login(self, username: str, password: str) -> bool:
        """Autentificare."""
        response = self.send_command(f"USER {username}")
        print(f"[CLIENT] {response}")
        
        if not response.startswith("331"):
            return False
        
        response = self.send_command(f"PASS {password}")
        print(f"[CLIENT] {response}")
        
        return response.startswith("230")
    
    def list_files(self) -> str:
        """Listează fișierele de pe server."""
        response = self.send_command("LIST")
        print(f"[CLIENT] {response}")
        
        # Pentru LIST, răspunsul include și listarea
        if response.startswith("150"):
            # Primim listarea
            listing = self.recv_response()
            # Primim confirmarea
            final = self.recv_response()
            print(f"[CLIENT] {final}")
            return listing
        
        return ""
    
    def passive_get(self, filename: str, use_gzip: bool = False) -> bool:
        """Descarcă un fișier în mod pasiv."""
        response = self.send_command(f"PASSIVE_GET {filename}")
        print(f"[CLIENT] {response}")
        
        if not response.startswith("227"):
            return False
        
        # Extragem portul din răspuns
        # Format: "227 Entering Passive Mode (12345)"
        try:
            port_str = response.split("(")[1].split(")")[0]
            data_port = int(port_str)
        except (IndexError, ValueError):
            print(f"[CLIENT] Nu pot extrage portul din: {response}")
            return False
        
        # Ne conectăm pentru date
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as data_conn:
            data_conn.connect((self.host, data_port))
            
            # Primim datele
            raw_data = b""
            while True:
                chunk = data_conn.recv(BUFFER_SIZE)
                if not chunk:
                    break
                raw_data += chunk
        
        # Despachetăm și salvăm
        try:
            content, meta = unpack_data(raw_data)
            local_path = self.local_dir / filename
            local_path.write_bytes(content)
            
            print(f"[CLIENT] Salvat: {local_path} ({len(content)} bytes)")
            if meta["compressed"]:
                print(f"[CLIENT] (comprimat pe fir: {meta['wire_length']} bytes)")
            
            # Citim confirmarea
            final = self.recv_response()
            print(f"[CLIENT] {final}")
            
            return True
            
        except Exception as e:
            print(f"[CLIENT] Eroare: {e}")
            return False
    
    def active_get(self, filename: str) -> bool:
        """Descarcă un fișier în mod activ."""
        # Deschidem socket pentru date
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as data_server:
            data_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            data_server.bind(("", 0))
            data_server.listen(1)
            data_port = data_server.getsockname()[1]
            
            # Trimitem comanda cu portul nostru
            response = self.send_command(f"ACTIVE_GET {filename} {data_port}")
            print(f"[CLIENT] {response}")
            
            if response.startswith("5"):
                return False
            
            # Așteptăm conexiunea serverului
            data_server.settimeout(30)
            data_conn, _ = data_server.accept()
            
            with data_conn:
                raw_data = b""
                while True:
                    chunk = data_conn.recv(BUFFER_SIZE)
                    if not chunk:
                        break
                    raw_data += chunk
        
        try:
            content, meta = unpack_data(raw_data)
            local_path = self.local_dir / filename
            local_path.write_bytes(content)
            
            print(f"[CLIENT] Salvat: {local_path} ({len(content)} bytes)")
            
            final = self.recv_response()
            print(f"[CLIENT] {final}")
            
            return True
            
        except Exception as e:
            print(f"[CLIENT] Eroare: {e}")
            return False
    
    def passive_put(self, filename: str, use_gzip: bool = False) -> bool:
        """Încarcă un fișier în mod pasiv."""
        local_path = self.local_dir / filename
        if not local_path.is_file():
            print(f"[CLIENT] Fișier inexistent: {local_path}")
            return False
        
        response = self.send_command(f"PASSIVE_PUT {filename}")
        print(f"[CLIENT] {response}")
        
        if not response.startswith("227"):
            return False
        
        try:
            port_str = response.split("(")[1].split(")")[0]
            data_port = int(port_str)
        except (IndexError, ValueError):
            return False
        
        content = local_path.read_bytes()
        packed = pack_data(content, use_gzip=use_gzip)
        
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as data_conn:
            data_conn.connect((self.host, data_port))
            data_conn.sendall(packed)
        
        final = self.recv_response()
        print(f"[CLIENT] {final}")
        
        return final.startswith("226")
    
    def interactive(self):
        """Mod interactiv pentru client."""
        print("\n=== Pseudo-FTP Client Interactiv ===")
        print("Comenzi: list, pwd, cwd <dir>, get <file>, put <file>, quit")
        print("=" * 40)
        
        while True:
            try:
                cmd = input("ftp> ").strip()
                if not cmd:
                    continue
                
                parts = cmd.split(maxsplit=1)
                action = parts[0].lower()
                arg = parts[1] if len(parts) > 1 else ""
                
                if action == "quit" or action == "exit":
                    self.send_command("QUIT")
                    break
                
                elif action == "list" or action == "ls":
                    listing = self.list_files()
                    if listing:
                        print(listing)
                
                elif action == "pwd":
                    response = self.send_command("PWD")
                    print(response)
                
                elif action == "cwd" or action == "cd":
                    response = self.send_command(f"CWD {arg}")
                    print(response)
                
                elif action == "get":
                    if arg:
                        self.passive_get(arg)
                    else:
                        print("Utilizare: get <filename>")
                
                elif action == "put":
                    if arg:
                        self.passive_put(arg)
                    else:
                        print("Utilizare: put <filename>")
                
                else:
                    # Trimitem comanda direct
                    response = self.send_command(cmd)
                    print(response)
                    
            except KeyboardInterrupt:
                print("\n[CLIENT] Întrerupere. Utilizează 'quit' pentru a ieși.")
            except EOFError:
                break


# =============================================================================
# Main
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Pseudo-FTP Server/Client (Demo L5/L6)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemple:
  # Server
  %(prog)s server --host 127.0.0.1 --port 3333 --root ./server-files
  
  # Client - comenzi
  %(prog)s client --host 127.0.0.1 --port 3333 --user test --password 12345 list
  %(prog)s client ... get hello.txt
  %(prog)s client ... --mode active get hello.txt
  
  # Client - interactiv
  %(prog)s client ... --interactive
        """
    )
    
    subparsers = parser.add_subparsers(dest="mode", help="Mod de operare")
    
    # Server
    server_p = subparsers.add_parser("server", help="Pornește serverul")
    server_p.add_argument("--host", default=DEFAULT_HOST, help="Adresă de bind")
    server_p.add_argument("--port", type=int, default=DEFAULT_PORT, help="Port")
    server_p.add_argument("--root", default="./server-files", help="Director root")
    
    # Client
    client_p = subparsers.add_parser("client", help="Pornește clientul")
    client_p.add_argument("--host", default=DEFAULT_HOST, help="Adresa serverului")
    client_p.add_argument("--port", type=int, default=DEFAULT_PORT, help="Port")
    client_p.add_argument("--user", default=DEFAULT_USER, help="Username")
    client_p.add_argument("--password", default=DEFAULT_PASS, help="Password")
    client_p.add_argument("--local-dir", default="./client-files", help="Director local")
    client_p.add_argument("--mode", choices=["passive", "active"], default="passive")
    client_p.add_argument("--gzip", action="store_true", help="Folosește compresie")
    client_p.add_argument("--interactive", "-i", action="store_true", help="Mod interactiv")
    client_p.add_argument("command", nargs="?", help="Comandă: list, get, put")
    client_p.add_argument("argument", nargs="?", help="Argument pentru comandă")
    
    args = parser.parse_args()
    
    if args.mode == "server":
        server = PseudoFTPServer(args.host, args.port, Path(args.root))
        server.start()
    
    elif args.mode == "client":
        client = PseudoFTPClient(args.host, args.port, Path(args.local_dir))
        
        try:
            client.connect()
            
            if not client.login(args.user, args.password):
                print("[CLIENT] Autentificare eșuată!")
                return 1
            
            if args.interactive:
                client.interactive()
            elif args.command:
                cmd = args.command.lower()
                
                if cmd == "list":
                    listing = client.list_files()
                    if listing:
                        print(listing)
                
                elif cmd == "get":
                    if not args.argument:
                        print("Utilizare: get <filename>")
                        return 1
                    
                    if args.mode == "active":
                        client.active_get(args.argument)
                    else:
                        client.passive_get(args.argument, use_gzip=args.gzip)
                
                elif cmd == "put":
                    if not args.argument:
                        print("Utilizare: put <filename>")
                        return 1
                    client.passive_put(args.argument, use_gzip=args.gzip)
                
                else:
                    print(f"Comandă necunoscută: {cmd}")
                    return 1
            else:
                # Fără comandă, intrăm în mod interactiv
                client.interactive()
            
        finally:
            client.close()
    
    else:
        parser.print_help()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
