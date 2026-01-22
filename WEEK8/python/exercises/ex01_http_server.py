#!/usr/bin/env python3
"""
EXERCIȚIU 1: Completare Server HTTP
=====================================
Disciplina: Rețele de Calculatoare, Săptămâna 8
Nivel: Intermediar
Timp estimat: 30 minute

OBIECTIVE:
- Înțelegerea formatului HTTP request/response
- Implementarea parsării cererilor HTTP
- Servirea fișierelor statice cu securitate

INSTRUCȚIUNI:
1. Completați funcțiile marcate cu TODO
2. Rulați testele: python3 -m pytest tests/test_ex01.py -v
3. Testați manual: python3 ex01_http_server.py --port 8081

EVALUARE:
- Parsare corectă request: 30%
- Servire fișiere: 30%
- Securitate (directory traversal): 20%
- HEAD method: 20%

© Revolvix&Hypotheticalandrei
"""

import socket
import os
import sys
import argparse
from pathlib import Path
from typing import Tuple, Dict, Optional

# ============================================================================
# CONSTANTE
# ============================================================================

CRLF = "\r\n"
DOUBLE_CRLF = "\r\n\r\n"

HTTP_STATUS = {
    200: "OK",
    400: "Bad Request",
    403: "Forbidden",
    404: "Not Found",
    405: "Method Not Allowed",
    500: "Internal Server Error",
}

MIME_TYPES = {
    ".html": "text/html",
    ".htm": "text/html",
    ".css": "text/css",
    ".js": "application/javascript",
    ".json": "application/json",
    ".txt": "text/plain",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".ico": "image/x-icon",
}

DEFAULT_TYPE = "application/octet-stream"


# ============================================================================
# TODO: IMPLEMENTAȚI ACEASTĂ FUNCȚIE
# ============================================================================

def parse_request(raw_request: bytes) -> Tuple[str, str, str, Dict[str, str]]:
    """
    Parsează un HTTP request și extrage componentele.
    
    Args:
        raw_request: Bytes-ul primit de la client
    
    Returns:
        Tuple cu: (method, path, version, headers_dict)
        
    Exemple:
        >>> data = b'GET /index.html HTTP/1.1\\r\\nHost: localhost\\r\\n\\r\\n'
        >>> method, path, version, headers = parse_request(data)
        >>> method
        'GET'
        >>> path
        '/index.html'
        >>> headers['host']
        'localhost'
    
    HINT:
    1. Decodifică raw_request în string (utf-8)
    2. Separă pe linii (\\r\\n)
    3. Prima linie conține: METHOD PATH VERSION
    4. Restul liniilor sunt headers în format "Key: Value"
    5. Normalizează key-urile la lowercase
    
    ATENȚIE:
    - Tratați cazul când request-ul este invalid (returnați eroare sensibilă)
    - Header keys ar trebui să fie case-insensitive
    """
    
    # TODO: Implementați parsarea request-ului HTTP
    # 
    # Pași sugerați:
    # 1. Decodifică bytes -> string
    # 2. Split pe CRLF pentru a obține liniile
    # 3. Parsează prima linie (request line): method, path, version
    # 4. Parsează headers (key: value)
    # 5. Returnează tuple-ul
    
    raise NotImplementedError("TODO: Implementați parse_request()")


# ============================================================================
# TODO: IMPLEMENTAȚI ACEASTĂ FUNCȚIE
# ============================================================================

def is_safe_path(requested_path: str, docroot: str) -> bool:
    """
    Verifică dacă calea cerută este sigură (nu permite directory traversal).
    
    Args:
        requested_path: Calea cerută de client (ex: "/images/../../../etc/passwd")
        docroot: Directorul rădăcină pentru fișiere statice
    
    Returns:
        True dacă calea este sigură, False altfel
    
    Exemple:
        >>> is_safe_path("/index.html", "/var/www")
        True
        >>> is_safe_path("/../etc/passwd", "/var/www")
        False
        >>> is_safe_path("/images/logo.png", "/var/www")
        True
    
    HINT:
    - Folosiți os.path.normpath() pentru a normaliza calea
    - Folosiți os.path.abspath() pentru a obține calea absolută
    - Verificați că rezultatul este în interiorul docroot-ului
    
    SECURITATE:
    - Aceasta este o funcție CRITICĂ pentru securitate
    - Atacatorii vor încerca ../../../etc/passwd
    - Trebuie să preveniți ORICE ieșire din docroot
    """
    
    # TODO: Implementați verificarea securității căii
    #
    # Pași sugerați:
    # 1. Normalizați requested_path (elimină .. și .)
    # 2. Construiți calea completă: docroot + requested_path
    # 3. Obțineți calea absolută pentru ambele
    # 4. Verificați că calea completă începe cu docroot
    
    raise NotImplementedError("TODO: Implementați is_safe_path()")


# ============================================================================
# TODO: IMPLEMENTAȚI ACEASTĂ FUNCȚIE
# ============================================================================

def serve_file(path: str, docroot: str) -> Tuple[int, Dict[str, str], bytes]:
    """
    Servește un fișier static de pe disc.
    
    Args:
        path: Calea cerută (ex: "/index.html")
        docroot: Directorul rădăcină
    
    Returns:
        Tuple cu: (status_code, headers_dict, body_bytes)
    
    Exemple:
        >>> status, headers, body = serve_file("/index.html", "./www")
        >>> status
        200
        >>> headers['content-type']
        'text/html'
    
    HINT:
    1. Verificați securitatea căii cu is_safe_path()
    2. Dacă calea e "/" folosiți "/index.html" implicit
    3. Determinați MIME type din extensie
    4. Citiți fișierul în mod binar ('rb')
    5. Returnați headers corespunzătoare
    
    CAZURI DE TRATAT:
    - 403: cale nesigură (directory traversal)
    - 404: fișier nu există
    - 200: fișier găsit și servit
    """
    
    # TODO: Implementați servirea fișierului
    #
    # Pași sugerați:
    # 1. Normalizați path (dacă e "/" → "/index.html")
    # 2. Verificați securitatea cu is_safe_path()
    # 3. Construiți calea completă
    # 4. Verificați dacă fișierul există
    # 5. Determinați Content-Type din extensie
    # 6. Citiți conținutul fișierului
    # 7. Construiți headers (Content-Type, Content-Length)
    # 8. Returnați (status_code, headers, body)
    
    raise NotImplementedError("TODO: Implementați serve_file()")


# ============================================================================
# TODO: IMPLEMENTAȚI ACEASTĂ FUNCȚIE
# ============================================================================

def build_response(status_code: int, headers: Dict[str, str], body: bytes) -> bytes:
    """
    Construiește un răspuns HTTP complet.
    
    Args:
        status_code: Codul de status HTTP (200, 404, etc.)
        headers: Dicționar cu headers
        body: Conținutul răspunsului în bytes
    
    Returns:
        Răspunsul HTTP complet ca bytes
    
    Exemple:
        >>> resp = build_response(200, {"Content-Type": "text/plain"}, b"Hello")
        >>> resp.startswith(b"HTTP/1.1 200 OK")
        True
    
    FORMAT:
        HTTP/1.1 {status_code} {status_text}\r\n
        Header1: Value1\r\n
        Header2: Value2\r\n
        \r\n
        {body}
    """
    
    # TODO: Implementați construirea răspunsului HTTP
    #
    # Pași sugerați:
    # 1. Construiți status line: "HTTP/1.1 {code} {text}\r\n"
    # 2. Adăugați fiecare header: "{Key}: {Value}\r\n"
    # 3. Adăugați linie goală: "\r\n"
    # 4. Convertiți totul la bytes și adăugați body
    
    raise NotImplementedError("TODO: Implementați build_response()")


# ============================================================================
# TODO: IMPLEMENTAȚI ACEASTĂ FUNCȚIE
# ============================================================================

def handle_request(raw_request: bytes, docroot: str) -> bytes:
    """
    Procesează un request HTTP complet și returnează răspunsul.
    
    Args:
        raw_request: Request-ul HTTP în bytes
        docroot: Directorul rădăcină pentru fișiere
    
    Returns:
        Răspunsul HTTP complet în bytes
    
    METODE SUPORTATE:
    - GET: returnează fișierul complet (headers + body)
    - HEAD: returnează doar headers (fără body)
    - Altele: returnează 405 Method Not Allowed
    
    HINT:
    - Folosiți funcțiile implementate anterior
    - Pentru HEAD, apelați serve_file dar nu includeți body-ul în răspuns
    """
    
    # TODO: Implementați handler-ul complet
    #
    # Pași sugerați:
    # 1. Parsați request-ul
    # 2. Verificați metoda (GET, HEAD, altele)
    # 3. Pentru GET/HEAD, apelați serve_file()
    # 4. Pentru HEAD, setați body la b""
    # 5. Construiți și returnați răspunsul
    
    raise NotImplementedError("TODO: Implementați handle_request()")


# ============================================================================
# COD FURNIZAT - NU MODIFICAȚI
# ============================================================================

def run_server(host: str, port: int, docroot: str):
    """
    Pornește serverul HTTP.
    Cod furnizat - nu necesită modificări.
    """
    docroot = os.path.abspath(docroot)
    
    if not os.path.isdir(docroot):
        print(f"[EROARE] Directorul docroot nu există: {docroot}")
        sys.exit(1)
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server_socket.bind((host, port))
        server_socket.listen(5)
        print(f"[INFO] Server pornit pe http://{host}:{port}/")
        print(f"[INFO] Document root: {docroot}")
        print("[INFO] Apăsați Ctrl+C pentru oprire")
        
        while True:
            client_socket, client_addr = server_socket.accept()
            print(f"[CONN] Conexiune de la {client_addr[0]}:{client_addr[1]}")
            
            try:
                raw_request = client_socket.recv(4096)
                if raw_request:
                    response = handle_request(raw_request, docroot)
                    client_socket.sendall(response)
            except Exception as e:
                print(f"[EROARE] {e}")
                error_response = build_response(
                    500, 
                    {"Content-Type": "text/plain"}, 
                    b"Internal Server Error"
                )
                client_socket.sendall(error_response)
            finally:
                client_socket.close()
                
    except KeyboardInterrupt:
        print("\n[INFO] Server oprit de utilizator")
    finally:
        server_socket.close()


def main():
    parser = argparse.ArgumentParser(description="Server HTTP simplu")
    parser.add_argument("--host", default="0.0.0.0", help="Adresa de bind")
    parser.add_argument("--port", type=int, default=8081, help="Portul de ascultare")
    parser.add_argument("--docroot", default="www", help="Directorul cu fișiere statice")
    
    args = parser.parse_args()
    run_server(args.host, args.port, args.docroot)


if __name__ == "__main__":
    main()
