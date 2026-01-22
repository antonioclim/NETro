#!/usr/bin/env python3
"""
Utilități I/O pentru comunicare de rețea.

Aceste funcții rezolvă problema fundamentală a TCP: fluxul continuu de bytes
nu garantează primirea unui mesaj întreg într-un singur recv().

Concepte cheie:
- TCP este un stream, nu un protocol bazat pe mesaje
- Framing-ul (delimitarea mesajelor) este responsabilitatea aplicației
- recv() poate returna mai puțini bytes decât s-au cerut
"""
from __future__ import annotations
import socket


def recv_exact(sock: socket.socket, n: int, timeout: float | None = None) -> bytes:
    """
    Primește exact n bytes de pe socket.
    
    Problemă rezolvată: recv(n) poate returna mai puțin de n bytes chiar dacă
    există mai multe date disponibile sau în tranzit.
    
    Implementare: citim în buclă până acumulăm exact n bytes.
    
    Args:
        sock: Socket-ul de pe care citim
        n: Numărul exact de bytes de citit
        timeout: Timeout opțional (None = blocking indefinit)
        
    Returns:
        bytes: Exact n bytes
        
    Raises:
        ConnectionError: Dacă peer-ul închide conexiunea înainte de n bytes
        socket.timeout: Dacă timeout-ul expiră
    """
    if timeout is not None:
        sock.settimeout(timeout)
    
    chunks: list[bytes] = []
    remaining = n
    
    while remaining > 0:
        chunk = sock.recv(remaining)
        if not chunk:
            raise ConnectionError(f"peer closed connection, got {n - remaining}/{n} bytes")
        chunks.append(chunk)
        remaining -= len(chunk)
    
    return b"".join(chunks)


def recv_until(sock: socket.socket, delim: bytes, max_bytes: int = 1024 * 1024) -> bytes:
    """
    Citește până la întâlnirea unui delimitator.
    
    Util pentru protocoale text bazate pe delimitatori (ex: newline, spațiu).
    
    ATENȚIE: Citește byte cu byte, deci ineficient pentru volume mari.
    În producție, s-ar folosi buffering sau select/poll.
    
    Args:
        sock: Socket-ul de pe care citim
        delim: Secvența de bytes care marchează sfârșitul mesajului
        max_bytes: Limită de siguranță contra atacurilor de memorie
        
    Returns:
        bytes: Datele citite INCLUSIV delimitatorul
        
    Raises:
        ConnectionError: Dacă peer-ul închide conexiunea
        ValueError: Dacă se depășește max_bytes (potențial atac)
    """
    buf = bytearray()
    
    while True:
        b = sock.recv(1)
        if not b:
            raise ConnectionError("peer closed connection before delimiter")
        buf += b
        
        if buf.endswith(delim):
            return bytes(buf)
        
        if len(buf) > max_bytes:
            raise ValueError(f"recv_until exceeded {max_bytes} bytes without finding delimiter")


def recv_line(sock: socket.socket, max_bytes: int = 65536) -> str:
    """
    Citește o linie terminată cu newline.
    
    Convenție: linia returnată NU include newline-ul.
    """
    raw = recv_until(sock, b"\n", max_bytes)
    return raw[:-1].decode("utf-8", errors="replace")


def send_all(sock: socket.socket, data: bytes) -> None:
    """
    Trimite toate datele, gestionând partial sends.
    
    Notă: sock.sendall() face deja acest lucru, dar această funcție
    oferă un wrapper explicit pentru claritate didactică.
    """
    sock.sendall(data)
