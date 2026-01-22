#!/usr/bin/env python3
"""
net_utils.py - Utilitare pentru programare de rețea (Săptămâna 8).

Funcții helper pentru:
- Parsing HTTP request/response
- Construire răspunsuri HTTP
- Validare și sanitizare path-uri (securitate)
- MIME types și formatare

Autor: Rețele de Calculatoare, ASE București
"""
from __future__ import annotations

import os
import re
import socket
import urllib.parse
from dataclasses import dataclass
from typing import Dict, Optional, Tuple


# ═══════════════════════════════════════════════════════════════════════════════
# Constante HTTP
# ═══════════════════════════════════════════════════════════════════════════════

HTTP_STATUS_CODES = {
    200: "OK",
    201: "Created",
    204: "No Content",
    301: "Moved Permanently",
    302: "Found",
    304: "Not Modified",
    400: "Bad Request",
    401: "Unauthorized",
    403: "Forbidden",
    404: "Not Found",
    405: "Method Not Allowed",
    408: "Request Timeout",
    414: "URI Too Long",
    500: "Internal Server Error",
    502: "Bad Gateway",
    503: "Service Unavailable",
}

MIME_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".htm": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".txt": "text/plain; charset=utf-8",
    ".xml": "application/xml; charset=utf-8",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".svg": "image/svg+xml",
    ".ico": "image/x-icon",
    ".pdf": "application/pdf",
    ".zip": "application/zip",
    ".woff": "font/woff",
    ".woff2": "font/woff2",
}

DEFAULT_CONTENT_TYPE = "application/octet-stream"


# ═══════════════════════════════════════════════════════════════════════════════
# Data Classes
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class HttpRequest:
    """Reprezentare structurată a unui HTTP request."""
    method: str
    target: str
    version: str
    headers: Dict[str, str]
    body: bytes = b""
    raw: bytes = b""


@dataclass
class HttpResponse:
    """Reprezentare structurată a unui HTTP response."""
    status: int
    reason: str
    headers: Dict[str, str]
    body: bytes = b""


# ═══════════════════════════════════════════════════════════════════════════════
# Funcții de citire socket
# ═══════════════════════════════════════════════════════════════════════════════

def read_until(sock: socket.socket, 
               marker: bytes = b"\r\n\r\n", 
               timeout: float = 10.0,
               max_bytes: int = 64 * 1024) -> bytes:
    """
    Citește din socket până întâlnește marker-ul specificat.
    
    Args:
        sock: Socket-ul din care se citește
        marker: Secvența care marchează sfârșitul (default: CRLFCRLF pentru HTTP)
        timeout: Timeout în secunde
        max_bytes: Numărul maxim de bytes de citit
    
    Returns:
        Bytes citiți (inclusiv marker-ul)
    
    Raises:
        TimeoutError: Dacă timeout-ul expiră
        ValueError: Dacă se depășește max_bytes
    """
    sock.settimeout(timeout)
    data = b""
    
    try:
        while marker not in data:
            chunk = sock.recv(4096)
            if not chunk:
                break
            data += chunk
            if len(data) > max_bytes:
                raise ValueError(f"Depășit limita de {max_bytes} bytes")
        return data
    except socket.timeout:
        raise TimeoutError("Socket timeout la citire")


def read_exact(sock: socket.socket, n: int, timeout: float = 10.0) -> bytes:
    """Citește exact n bytes din socket."""
    sock.settimeout(timeout)
    data = b""
    while len(data) < n:
        chunk = sock.recv(min(4096, n - len(data)))
        if not chunk:
            break
        data += chunk
    return data


# ═══════════════════════════════════════════════════════════════════════════════
# Parsing HTTP
# ═══════════════════════════════════════════════════════════════════════════════

def parse_http_request(raw: bytes) -> HttpRequest:
    """
    Parsează un HTTP request din bytes.
    
    Args:
        raw: Bytes brut al request-ului (minimum până la CRLFCRLF)
    
    Returns:
        HttpRequest cu câmpurile parsate
    
    Raises:
        ValueError: Dacă request-ul este invalid
    """
    if not raw:
        raise ValueError("Request gol")
    
    # Separăm headers de body
    if b"\r\n\r\n" in raw:
        head_bytes, body = raw.split(b"\r\n\r\n", 1)
    else:
        head_bytes = raw
        body = b""
    
    # Decodăm headers (HTTP/1.x folosește ISO-8859-1)
    try:
        head = head_bytes.decode("iso-8859-1")
    except UnicodeDecodeError:
        raise ValueError("Encoding invalid în headers")
    
    lines = head.split("\r\n")
    if not lines:
        raise ValueError("Request fără request line")
    
    # Parsăm request line: METHOD SP REQUEST-TARGET SP HTTP-VERSION
    request_line = lines[0]
    parts = request_line.split(" ")
    if len(parts) < 3:
        raise ValueError(f"Request line invalid: {request_line}")
    
    method = parts[0].upper()
    target = parts[1]
    version = parts[2]
    
    # Validare metodă
    valid_methods = {"GET", "POST", "PUT", "DELETE", "HEAD", "OPTIONS", "PATCH"}
    if method not in valid_methods:
        raise ValueError(f"Metodă HTTP necunoscută: {method}")
    
    # Validare versiune
    if not version.startswith("HTTP/"):
        raise ValueError(f"Versiune HTTP invalidă: {version}")
    
    # Parsăm headers
    headers: Dict[str, str] = {}
    for line in lines[1:]:
        if not line:
            continue
        if ":" not in line:
            continue  # Ignorăm linii malformate
        key, value = line.split(":", 1)
        # Normalizăm cheile la lowercase
        headers[key.strip().lower()] = value.strip()
    
    return HttpRequest(
        method=method,
        target=target,
        version=version,
        headers=headers,
        body=body,
        raw=raw
    )


def parse_http_response(raw: bytes) -> HttpResponse:
    """Parsează un HTTP response din bytes."""
    if b"\r\n\r\n" in raw:
        head_bytes, body = raw.split(b"\r\n\r\n", 1)
    else:
        head_bytes = raw
        body = b""
    
    head = head_bytes.decode("iso-8859-1", errors="replace")
    lines = head.split("\r\n")
    
    # Status line: HTTP/1.1 200 OK
    status_line = lines[0] if lines else ""
    match = re.match(r"HTTP/\d\.\d\s+(\d+)\s+(.*)", status_line)
    if not match:
        raise ValueError(f"Status line invalid: {status_line}")
    
    status = int(match.group(1))
    reason = match.group(2)
    
    headers: Dict[str, str] = {}
    for line in lines[1:]:
        if ":" in line:
            k, v = line.split(":", 1)
            headers[k.strip().lower()] = v.strip()
    
    return HttpResponse(status=status, reason=reason, headers=headers, body=body)


# ═══════════════════════════════════════════════════════════════════════════════
# Construire răspunsuri HTTP
# ═══════════════════════════════════════════════════════════════════════════════

def build_response(status: int, 
                   body: bytes = b"",
                   content_type: str = "text/plain; charset=utf-8",
                   extra_headers: Optional[Dict[str, str]] = None) -> bytes:
    """
    Construiește un răspuns HTTP complet.
    
    Args:
        status: Cod de status HTTP (ex: 200, 404, 500)
        body: Conținutul răspunsului
        content_type: Header Content-Type
        extra_headers: Headers adiționale
    
    Returns:
        Răspunsul HTTP complet ca bytes
    """
    reason = HTTP_STATUS_CODES.get(status, "Unknown")
    
    headers = [
        f"HTTP/1.1 {status} {reason}",
        f"Content-Type: {content_type}",
        f"Content-Length: {len(body)}",
        "Connection: close",
        "Server: ASE-S8-Server/1.0",
    ]
    
    if extra_headers:
        for key, value in extra_headers.items():
            headers.append(f"{key}: {value}")
    
    head = "\r\n".join(headers) + "\r\n\r\n"
    return head.encode("iso-8859-1") + body


def build_redirect(location: str, permanent: bool = False) -> bytes:
    """Construiește un răspuns de redirect."""
    status = 301 if permanent else 302
    body = f"Redirecting to {location}".encode("utf-8")
    return build_response(
        status, body, 
        extra_headers={"Location": location}
    )


# ═══════════════════════════════════════════════════════════════════════════════
# Securitate: Validare path-uri
# ═══════════════════════════════════════════════════════════════════════════════

def safe_map_target_to_path(target: str, 
                            www_root: str,
                            max_uri_length: int = 2048) -> Tuple[Optional[str], Optional[str]]:
    """
    Mapează un URI target la o cale de fișier, cu protecție directory traversal.
    
    Args:
        target: URI-ul din request (ex: "/index.html", "/../etc/passwd")
        www_root: Directorul rădăcină pentru fișiere
        max_uri_length: Lungimea maximă a URI-ului
    
    Returns:
        Tuple (filepath, error) unde:
        - filepath: Calea completă sau None dacă e eroare
        - error: None dacă OK, sau unul din: "URI_TOO_LONG", "TRAVERSAL"
    """
    # Verificare lungime
    if len(target) > max_uri_length:
        return None, "URI_TOO_LONG"
    
    # Extrage doar path-ul (fără query string și fragment)
    parsed = urllib.parse.urlparse(target)
    path = parsed.path
    
    # Decodare percent-encoding (%20 -> space, etc.)
    path = urllib.parse.unquote(path)
    
    # Elimină / de la început pentru os.path.join
    path = path.lstrip("/")
    
    # Dacă e empty sau "/", mapăm la index.html
    if not path:
        path = "index.html"
    
    # Construim calea completă
    www_root = os.path.abspath(www_root)
    full_path = os.path.normpath(os.path.join(www_root, path))
    
    # VERIFICARE CRITICĂ: path-ul rezultat trebuie să fie în www_root
    if not full_path.startswith(www_root + os.sep) and full_path != www_root:
        # Încercare de directory traversal!
        return None, "TRAVERSAL"
    
    return full_path, None


# ═══════════════════════════════════════════════════════════════════════════════
# Utilități diverse
# ═══════════════════════════════════════════════════════════════════════════════

def guess_content_type(filepath: str) -> str:
    """Ghicește Content-Type pe baza extensiei fișierului."""
    _, ext = os.path.splitext(filepath.lower())
    return MIME_TYPES.get(ext, DEFAULT_CONTENT_TYPE)


def format_bytes(n: int) -> str:
    """Formatează numărul de bytes human-readable."""
    for unit in ["B", "KB", "MB", "GB"]:
        if abs(n) < 1024:
            return f"{n:.1f} {unit}" if unit != "B" else f"{n} {unit}"
        n /= 1024
    return f"{n:.1f} TB"


def get_ephemeral_port() -> int:
    """Găsește un port efemer liber."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def format_headers(headers: Dict[str, str], indent: str = "  ") -> str:
    """Formatează headers pentru afișare."""
    return "\n".join(f"{indent}{k}: {v}" for k, v in sorted(headers.items()))


# ═══════════════════════════════════════════════════════════════════════════════
# Self-test
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # Test rapid parsing
    sample_request = b"GET /index.html HTTP/1.1\r\nHost: localhost\r\nUser-Agent: test\r\n\r\n"
    req = parse_http_request(sample_request)
    print(f"✓ Parsed: {req.method} {req.target} {req.version}")
    
    # Test response building
    resp = build_response(200, b"Hello, World!", extra_headers={"X-Test": "ok"})
    print(f"✓ Built response: {len(resp)} bytes")
    
    # Test path validation
    path, err = safe_map_target_to_path("/../etc/passwd", "/var/www")
    assert err == "TRAVERSAL", "Directory traversal nu a fost detectat!"
    print("✓ Directory traversal detection OK")
    
    print("\n[OK] Toate testele au trecut!")
