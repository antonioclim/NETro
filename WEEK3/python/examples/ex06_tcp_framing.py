#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  Exercițiul 6: TCP Framing (Delimitare Mesaje)                               ║
║  Săptămâna 3 — Rețele de Calculatoare                                        ║
╚══════════════════════════════════════════════════════════════════════════════╝

SCOPUL DIDACTIC:
    - Demonstrarea faptului că TCP este STREAM, nu MESSAGE-oriented
    - Un recv() poate returna: parte dintr-un mesaj, exact un mesaj, sau mai multe
    - Tehnici de framing: delimitator, length-prefix, TLV

PROBLEMA:
    TCP garantează livrarea în ordine, dar NU garantează limitele mesajelor!
    
    Client trimite:            Server primește (posibile variante):
    send("HELLO")              recv() → "HELLOWORLD"  (concatenate)
    send("WORLD")              recv() → "HEL"         (fragment)
                               recv() → "LOWORLD"

SOLUȚII DE FRAMING:

    1. DELIMITATOR (ex: newline \n, CRLF, NULL byte)
       - Simplu de implementat
       - Delimitatorul nu poate apărea în date
       - Folosit de: HTTP headers, SMTP, FTP commands
       
    2. LENGTH-PREFIX (lungime + date)
       - Primele N bytes indică lungimea mesajului
       - Date binare pot conține orice
       - Folosit de: HTTP body (Content-Length), TLS records
       
    3. TLV (Type-Length-Value)
       - Tip (identifică mesajul) + Lungime + Date
       - Pentru protocoale complexe cu multiple tipuri de mesaje
       - Folosit de: ASN.1/BER, protocoale binare custom

RULARE:
    # Terminal 1: Server
    python3 ex06_tcp_framing.py server --port 4444

    # Terminal 2: Client
    python3 ex06_tcp_framing.py client --port 4444
"""
from __future__ import annotations

import argparse
import socket
import struct
import sys
import time
from datetime import datetime


def timestamp() -> str:
    return datetime.now().strftime("%H:%M:%S.%f")[:-3]


def log(level: str, message: str) -> None:
    print(f"[{timestamp()}] [{level}] {message}")


# ════════════════════════════════════════════════════════════════════════════
#  PROBLEMA: NAIVE RECV
# ════════════════════════════════════════════════════════════════════════════

def demo_naive_recv(sock: socket.socket) -> None:
    """
    Demonstrează problema: recv() nu respectă limitele mesajelor.
    """
    log("INFO", "Metoda NAIVĂ: recv() poate returna orice cantitate de date!")
    
    # Citim ce vine - poate fi incomplet sau concatenat
    data = sock.recv(1024)
    log("RECV", f"Am primit: {data!r}")
    log("WARN", "↑ Acest output poate fi diferit de mesajele individuale trimise!")


# ════════════════════════════════════════════════════════════════════════════
#  SOLUȚIA 1: DELIMITATOR (NEWLINE)
# ════════════════════════════════════════════════════════════════════════════

def recv_with_delimiter(sock: socket.socket, delimiter: bytes = b"\n") -> bytes:
    """
    Primește date până găsește delimitatorul.
    Returnează mesajul FĂRĂ delimitator.
    
    Pattern-ul fundamental pentru protocoale text-based.
    """
    buffer = b""
    
    while delimiter not in buffer:
        chunk = sock.recv(1)  # Citim byte cu byte pentru simplitate
        if not chunk:
            raise ConnectionError("Conexiune închisă înainte de delimitator")
        buffer += chunk
    
    message, _ = buffer.split(delimiter, 1)
    return message


def recv_lines(sock: socket.socket, count: int, delimiter: bytes = b"\n") -> list[bytes]:
    """Primește `count` mesaje delimitate."""
    messages = []
    for _ in range(count):
        msg = recv_with_delimiter(sock, delimiter)
        messages.append(msg)
    return messages


def send_with_delimiter(sock: socket.socket, message: bytes, delimiter: bytes = b"\n") -> None:
    """Trimite mesaj cu delimitator la sfârșit."""
    sock.sendall(message + delimiter)


# ════════════════════════════════════════════════════════════════════════════
#  SOLUȚIA 2: LENGTH-PREFIX (4 bytes big-endian)
# ════════════════════════════════════════════════════════════════════════════

def recv_exact(sock: socket.socket, n: int) -> bytes:
    """
    Primește EXACT n bytes.
    Pattern esențial pentru protocoale binare.
    """
    buffer = b""
    while len(buffer) < n:
        remaining = n - len(buffer)
        chunk = sock.recv(remaining)
        if not chunk:
            raise ConnectionError(f"Conexiune închisă. Primit {len(buffer)}/{n} bytes.")
        buffer += chunk
    return buffer


def recv_length_prefixed(sock: socket.socket) -> bytes:
    """
    Primește un mesaj cu lungime prefixată (4 bytes, big-endian).
    
    Format: [4 bytes lungime][date]
    """
    # Pas 1: Citim lungimea (4 bytes)
    length_bytes = recv_exact(sock, 4)
    length = struct.unpack(">I", length_bytes)[0]  # >I = big-endian unsigned int
    
    # Pas 2: Citim exact `length` bytes de date
    data = recv_exact(sock, length)
    return data


def send_length_prefixed(sock: socket.socket, message: bytes) -> None:
    """
    Trimite mesaj cu lungime prefixată.
    """
    length = len(message)
    header = struct.pack(">I", length)  # 4 bytes, big-endian
    sock.sendall(header + message)


# ════════════════════════════════════════════════════════════════════════════
#  SERVER DEMO
# ════════════════════════════════════════════════════════════════════════════

def run_server(port: int) -> int:
    """Server care demonstrează cele două tehnici de framing."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server.bind(("0.0.0.0", port))
        server.listen(1)
        
        print("╔══════════════════════════════════════════════════════════════╗")
        print("║  Demo TCP Framing - Server                                   ║")
        print(f"║  Port: {port:<53}║")
        print("╚══════════════════════════════════════════════════════════════╝")
        log("INFO", "Aștept client...")
        
        client, addr = server.accept()
        log("CONN", f"Client conectat: {addr}")
        
        with client:
            # ─────────────────────────────────────────────────────────────────
            # Demo 1: Primire cu DELIMITATOR
            # ─────────────────────────────────────────────────────────────────
            log("INFO", "══ Demo 1: FRAMING CU DELIMITATOR (newline) ══")
            
            for i in range(3):
                msg = recv_with_delimiter(client, b"\n")
                log("RECV", f"Mesaj #{i+1}: {msg.decode()!r}")
            
            client.sendall(b"ACK:delimiter_ok\n")
            
            # ─────────────────────────────────────────────────────────────────
            # Demo 2: Primire cu LENGTH-PREFIX
            # ─────────────────────────────────────────────────────────────────
            log("INFO", "══ Demo 2: FRAMING CU LENGTH-PREFIX (4 bytes) ══")
            
            for i in range(3):
                msg = recv_length_prefixed(client)
                log("RECV", f"Mesaj #{i+1}: {msg!r} ({len(msg)} bytes)")
            
            send_length_prefixed(client, b"ACK:length_prefix_ok")
            
        log("INFO", "Demo complet!")
        
    except KeyboardInterrupt:
        log("INFO", "Oprire")
    except OSError as e:
        log("ERROR", f"Eroare: {e}")
        return 1
    finally:
        server.close()
    
    return 0


# ════════════════════════════════════════════════════════════════════════════
#  CLIENT DEMO
# ════════════════════════════════════════════════════════════════════════════

def run_client(host: str, port: int) -> int:
    """Client care trimite mesaje cu diferite tehnici de framing."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        sock.connect((host, port))
        log("CONN", f"Conectat la {host}:{port}")
        
        # ─────────────────────────────────────────────────────────────────────
        # Demo 1: Trimitere cu DELIMITATOR
        # ─────────────────────────────────────────────────────────────────────
        log("INFO", "══ Trimitere cu DELIMITATOR ══")
        
        messages = [b"Hello", b"World", b"From_Client"]
        for i, msg in enumerate(messages, 1):
            send_with_delimiter(sock, msg, b"\n")
            log("SEND", f"Mesaj #{i}: {msg.decode()!r}")
            time.sleep(0.1)  # Mică pauză pentru demonstrație
        
        # Așteptăm ACK
        ack = recv_with_delimiter(sock, b"\n")
        log("RECV", f"Server ACK: {ack.decode()!r}")
        
        # ─────────────────────────────────────────────────────────────────────
        # Demo 2: Trimitere cu LENGTH-PREFIX
        # ─────────────────────────────────────────────────────────────────────
        log("INFO", "══ Trimitere cu LENGTH-PREFIX ══")
        
        binary_messages = [
            b"Date binare \x00\x01\x02",
            b"Mesaj cu newline\nin interior",
            "Unicode: café ☕ 日本語".encode("utf-8")
        ]
        
        for i, msg in enumerate(binary_messages, 1):
            send_length_prefixed(sock, msg)
            log("SEND", f"Mesaj #{i}: {msg!r} ({len(msg)} bytes)")
            time.sleep(0.1)
        
        # Așteptăm ACK
        ack = recv_length_prefixed(sock)
        log("RECV", f"Server ACK: {ack!r}")
        
        log("INFO", "Demo complet!")
        
    except ConnectionRefusedError:
        log("ERROR", f"Nu pot conecta la {host}:{port}")
        return 1
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
        prog="ex06_tcp_framing.py",
        description="Demonstrație tehnici de framing TCP."
    )
    
    subparsers = parser.add_subparsers(dest="mode", required=True)
    
    # Server
    ps = subparsers.add_parser("server", help="Pornire server demo")
    ps.add_argument("--port", type=int, default=4444)
    
    # Client
    pc = subparsers.add_parser("client", help="Pornire client demo")
    pc.add_argument("--host", default="127.0.0.1")
    pc.add_argument("--port", type=int, default=4444)
    
    args = parser.parse_args(argv)
    
    if args.mode == "server":
        return run_server(args.port)
    else:
        return run_client(args.host, args.port)


if __name__ == "__main__":
    sys.exit(main())
