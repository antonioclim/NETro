"""
═══════════════════════════════════════════════════════════════════════════════
  net_utils.py – Utilitare comune pentru exercițiile de rețea
═══════════════════════════════════════════════════════════════════════════════

Modul cu funcții helper pentru operațiuni de rețea:
- Citire/scriere socket cu buffering
- Parsare HTTP simplificată  
- Funcții de conectare TCP cu timeout
- Utilități de timp

═══════════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations

import socket
import time
import re
from typing import Optional
from contextlib import contextmanager


def now_s() -> float:
    """Returnează timestamp-ul curent în secunde (monotonic)."""
    return time.monotonic()


def set_timeouts(sock: socket.socket, timeout: float) -> None:
    """Setează timeout pentru operații socket."""
    sock.settimeout(timeout)


@contextmanager
def connect_tcp(host: str, port: int, timeout: float = 5.0):
    """
    Context manager pentru conexiune TCP.
    
    Exemplu:
        with connect_tcp("localhost", 8080) as sock:
            sock.sendall(b"GET / HTTP/1.1\\r\\n\\r\\n")
            response = sock.recv(4096)
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        sock.connect((host, port))
        yield sock
    finally:
        try:
            sock.close()
        except Exception:
            pass


def recv_until(sock: socket.socket, 
               delimiter: bytes = b"\r\n\r\n", 
               max_bytes: int = 65536) -> bytes:
    """
    Citește din socket până la delimiter sau max_bytes.
    
    Folosit pentru citirea header-elor HTTP.
    
    Args:
        sock: Socket de citit
        delimiter: Secvența de terminare (default: \\r\\n\\r\\n pentru HTTP)
        max_bytes: Limită maximă de bytes
    
    Returns:
        Date citite (inclusiv delimiter dacă a fost găsit)
    """
    data = b""
    while len(data) < max_bytes:
        try:
            chunk = sock.recv(1024)
            if not chunk:
                break
            data += chunk
            if delimiter in data:
                break
        except socket.timeout:
            break
        except Exception:
            break
    return data


def recv_exact(sock: socket.socket, n: int) -> bytes:
    """
    Citește exact n bytes din socket.
    
    Args:
        sock: Socket de citit
        n: Numărul exact de bytes de citit
    
    Returns:
        Exact n bytes (sau mai puțin dacă conexiunea s-a închis)
    """
    data = b""
    while len(data) < n:
        try:
            chunk = sock.recv(n - len(data))
            if not chunk:
                break
            data += chunk
        except Exception:
            break
    return data


def parse_http_content_length(headers: bytes) -> int:
    """
    Extrage Content-Length din header-e HTTP.
    
    Args:
        headers: Header-ele HTTP (bytes)
    
    Returns:
        Valoarea Content-Length sau 0 dacă nu există
    """
    try:
        headers_str = headers.decode("ascii", errors="replace")
        match = re.search(r"content-length:\s*(\d+)", headers_str, re.IGNORECASE)
        if match:
            return int(match.group(1))
    except Exception:
        pass
    return 0


def parse_http_status(response: bytes) -> int:
    """
    Extrage codul de status HTTP din răspuns.
    
    Args:
        response: Răspunsul HTTP (bytes)
    
    Returns:
        Codul de status (ex: 200) sau 0 dacă nu poate fi parsat
    """
    try:
        first_line = response.split(b"\r\n", 1)[0].decode("ascii", errors="replace")
        parts = first_line.split()
        if len(parts) >= 2:
            return int(parts[1])
    except Exception:
        pass
    return 0


def format_bytes(n: int) -> str:
    """Formatează număr de bytes în format uman."""
    for unit in ["B", "KB", "MB", "GB"]:
        if abs(n) < 1024.0:
            return f"{n:.1f} {unit}"
        n /= 1024.0
    return f"{n:.1f} TB"


def format_duration(seconds: float) -> str:
    """Formatează durată în format uman."""
    if seconds < 0.001:
        return f"{seconds * 1000000:.1f} µs"
    elif seconds < 1:
        return f"{seconds * 1000:.2f} ms"
    else:
        return f"{seconds:.3f} s"


# Revolvix&Hypotheticalandrei
