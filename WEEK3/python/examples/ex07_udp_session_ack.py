#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  Exercițiul 7: UDP cu Sesiuni și Confirmări (ACK)                            ║
║  Săptămâna 3 — Rețele de Calculatoare                                        ║
╚══════════════════════════════════════════════════════════════════════════════╝

SCOPUL DIDACTIC:
    - UDP este connectionless - nu există "sesiune" la nivel transport
    - Dacă avem nevoie de sesiuni/reliability, le implementăm la nivel aplicație
    - Pattern: TOKEN pentru identificare client, ACK pentru confirmare

CONCEPTE:
    1. UDP nu menține stare între datagrame
    2. Serverul trebuie să identifice clientul după adresă + un token
    3. Fiabilitatea (dacă e necesară) se implementează prin ACK + retransmisie

PROTOCOL DEMONSTRAT:
    CLIENT                    SERVER
    ───────                   ───────
    HELLO ─────────────────► 
                        ◄────── TOKEN:abc123
    MSG:abc123:data ────────►
                        ◄────── ACK:abc123:1
    MSG:abc123:more ────────►
                        ◄────── ACK:abc123:2
    BYE:abc123 ─────────────►
                        ◄────── BYE_ACK:abc123

RULARE:
    # Server:
    python3 ex07_udp_session_ack.py server --port 5555

    # Client:
    python3 ex07_udp_session_ack.py client --port 5555 --messages 5
"""
from __future__ import annotations

import argparse
import random
import socket
import string
import sys
import time
from datetime import datetime
from typing import Dict, Tuple


BUFFER_SIZE = 65535


def timestamp() -> str:
    return datetime.now().strftime("%H:%M:%S.%f")[:-3]


def log(level: str, message: str) -> None:
    print(f"[{timestamp()}] [{level}] {message}")


def generate_token(length: int = 8) -> str:
    """Generează un token aleator pentru identificarea sesiunii."""
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


# ════════════════════════════════════════════════════════════════════════════
#  SERVER: Gestionează sesiuni UDP
# ════════════════════════════════════════════════════════════════════════════

class Session:
    """Reprezintă o sesiune client."""
    def __init__(self, token: str, addr: Tuple[str, int]):
        self.token = token
        self.addr = addr
        self.message_count = 0
        self.created_at = time.time()
    
    def __repr__(self):
        return f"Session({self.token}, {self.addr}, msgs={self.message_count})"


def run_server(port: int) -> int:
    """
    Server UDP cu gestiune de sesiuni.
    
    Protocolul:
    - HELLO → generează token și îl trimite
    - MSG:token:data → procesează, trimite ACK
    - BYE:token → închide sesiunea
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    # Dicționar: token → Session
    sessions: Dict[str, Session] = {}
    
    try:
        sock.bind(("0.0.0.0", port))
        
        print("╔══════════════════════════════════════════════════════════════╗")
        print("║  UDP Session Server (cu ACK)                                 ║")
        print(f"║  Port: {port:<53}║")
        print("╚══════════════════════════════════════════════════════════════╝")
        log("INFO", "Server pornit. Aștept datagrame...")
        
        while True:
            data, addr = sock.recvfrom(BUFFER_SIZE)
            text = data.decode("utf-8", errors="replace").strip()
            
            log("RECV", f"De la {addr[0]}:{addr[1]} → {text!r}")
            
            # ─────────────────────────────────────────────────────────────────
            # Parsare comenzi
            # ─────────────────────────────────────────────────────────────────
            
            if text == "HELLO":
                # Client nou - generăm token
                token = generate_token()
                session = Session(token, addr)
                sessions[token] = session
                
                response = f"TOKEN:{token}"
                sock.sendto(response.encode(), addr)
                log("SEND", f"Către {addr[0]}:{addr[1]} → {response}")
                log("INFO", f"Sesiune nouă: {token} pentru {addr}")
                
            elif text.startswith("MSG:"):
                # Format: MSG:token:data
                parts = text.split(":", 2)
                if len(parts) < 3:
                    sock.sendto(b"ERROR:format_invalid", addr)
                    continue
                
                _, token, msg_data = parts
                
                if token not in sessions:
                    sock.sendto(b"ERROR:token_invalid", addr)
                    log("WARN", f"Token necunoscut: {token}")
                    continue
                
                session = sessions[token]
                session.message_count += 1
                
                # Trimitem ACK cu numărul mesajului
                response = f"ACK:{token}:{session.message_count}"
                sock.sendto(response.encode(), addr)
                log("SEND", f"→ {response}")
                log("INFO", f"[{token}] Mesaj #{session.message_count}: {msg_data!r}")
                
            elif text.startswith("BYE:"):
                # Format: BYE:token
                token = text.split(":", 1)[1]
                
                if token in sessions:
                    session = sessions.pop(token)
                    response = f"BYE_ACK:{token}"
                    sock.sendto(response.encode(), addr)
                    log("SEND", f"→ {response}")
                    log("INFO", f"Sesiune închisă: {token} (total mesaje: {session.message_count})")
                else:
                    sock.sendto(b"ERROR:token_invalid", addr)
                    
            else:
                sock.sendto(b"ERROR:unknown_command", addr)
                log("WARN", f"Comandă necunoscută: {text!r}")
                
    except KeyboardInterrupt:
        log("INFO", f"Oprire. Sesiuni active: {len(sessions)}")
    finally:
        sock.close()
    
    return 0


# ════════════════════════════════════════════════════════════════════════════
#  CLIENT: Inițiază sesiune și trimite mesaje
# ════════════════════════════════════════════════════════════════════════════

def run_client(host: str, port: int, num_messages: int, timeout: float) -> int:
    """
    Client UDP care:
    1. Trimite HELLO și primește TOKEN
    2. Trimite N mesaje și așteaptă ACK pentru fiecare
    3. Trimite BYE și așteaptă BYE_ACK
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(timeout)
    server_addr = (host, port)
    
    try:
        print("╔══════════════════════════════════════════════════════════════╗")
        print("║  UDP Session Client                                          ║")
        print(f"║  Server: {host}:{port:<44}║")
        print("╚══════════════════════════════════════════════════════════════╝")
        
        # ─────────────────────────────────────────────────────────────────────
        # Pas 1: HELLO → primire TOKEN
        # ─────────────────────────────────────────────────────────────────────
        log("SEND", "HELLO")
        sock.sendto(b"HELLO", server_addr)
        
        try:
            data, _ = sock.recvfrom(BUFFER_SIZE)
            response = data.decode().strip()
            log("RECV", response)
            
            if not response.startswith("TOKEN:"):
                log("ERROR", f"Răspuns neașteptat: {response}")
                return 1
            
            token = response.split(":", 1)[1]
            log("INFO", f"Sesiune inițiată. Token: {token}")
            
        except socket.timeout:
            log("ERROR", "Timeout la HELLO")
            return 1
        
        # ─────────────────────────────────────────────────────────────────────
        # Pas 2: Trimitere mesaje cu ACK
        # ─────────────────────────────────────────────────────────────────────
        for i in range(1, num_messages + 1):
            msg_data = f"Mesaj_nr_{i}_din_{num_messages}"
            request = f"MSG:{token}:{msg_data}"
            
            log("SEND", request)
            sock.sendto(request.encode(), server_addr)
            
            try:
                data, _ = sock.recvfrom(BUFFER_SIZE)
                response = data.decode().strip()
                log("RECV", response)
                
                if response.startswith("ACK:"):
                    _, ack_token, ack_num = response.split(":")
                    if ack_token == token and int(ack_num) == i:
                        log("INFO", f"✓ ACK primit pentru mesaj #{i}")
                    else:
                        log("WARN", f"ACK neașteptat: {response}")
                elif response.startswith("ERROR:"):
                    log("ERROR", f"Server a răspuns cu eroare: {response}")
                    return 1
                    
            except socket.timeout:
                log("WARN", f"Timeout pentru mesaj #{i} (nu s-a primit ACK)")
            
            time.sleep(0.2)  # Mică pauză între mesaje
        
        # ─────────────────────────────────────────────────────────────────────
        # Pas 3: BYE → închidere sesiune
        # ─────────────────────────────────────────────────────────────────────
        request = f"BYE:{token}"
        log("SEND", request)
        sock.sendto(request.encode(), server_addr)
        
        try:
            data, _ = sock.recvfrom(BUFFER_SIZE)
            response = data.decode().strip()
            log("RECV", response)
            
            if response == f"BYE_ACK:{token}":
                log("INFO", "✓ Sesiune închisă corect")
            else:
                log("WARN", f"Răspuns neașteptat la BYE: {response}")
                
        except socket.timeout:
            log("WARN", "Timeout la BYE")
        
        log("INFO", f"Client terminat. Total mesaje trimise: {num_messages}")
        
    except OSError as e:
        log("ERROR", f"Eroare: {e}")
        return 1
    finally:
        sock.close()
    
    return 0


# ════════════════════════════════════════════════════════════════════════════
#  MAIN
# ════════════════════════════════════════════════════════════════════════════

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="ex07_udp_session_ack.py",
        description="UDP cu sesiuni și confirmări la nivel aplicație."
    )
    
    subparsers = parser.add_subparsers(dest="mode", required=True)
    
    # Server
    ps = subparsers.add_parser("server", help="Pornire server")
    ps.add_argument("--port", type=int, default=5555)
    
    # Client
    pc = subparsers.add_parser("client", help="Pornire client")
    pc.add_argument("--host", default="127.0.0.1")
    pc.add_argument("--port", type=int, default=5555)
    pc.add_argument("--messages", type=int, default=3, help="Număr de mesaje de trimis")
    pc.add_argument("--timeout", type=float, default=2.0, help="Timeout pentru ACK (secunde)")
    
    args = parser.parse_args(argv)
    
    if args.mode == "server":
        return run_server(args.port)
    else:
        return run_client(args.host, args.port, args.messages, args.timeout)


if __name__ == "__main__":
    sys.exit(main())
