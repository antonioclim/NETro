#!/usr/bin/env python3
"""
EXERCIȚIU 3: Suport POST pentru Server HTTP
=============================================
Disciplina: Rețele de Calculatoare, Săptămâna 8
Nivel: Avansat
Timp estimat: 25 minute

OBIECTIVE:
- Extinderea serverului pentru metoda POST
- Parsarea body-ului din cereri HTTP
- Procesarea form data (application/x-www-form-urlencoded)
- Returnarea răspunsurilor JSON

INSTRUCȚIUNI:
1. Completați funcțiile marcate cu TODO
2. Rulați testele: python3 -m pytest tests/test_ex03.py -v
3. Testați manual:
   curl -X POST -d "name=John&age=25" http://localhost:8081/api/form
   curl -X POST -H "Content-Type: application/json" -d '{"name":"John"}' http://localhost:8081/api/json

EVALUARE:
- Parsare Content-Length: 25%
- Citire body complet: 25%
- Parsare form data: 25%
- Răspuns JSON: 25%

© Revolvix&Hypotheticalandrei
"""

import socket
import json
import argparse
from urllib.parse import parse_qs, unquote_plus
from typing import Dict, Tuple, Any, Optional

# ============================================================================
# CONSTANTE
# ============================================================================

CRLF = "\r\n"
DOUBLE_CRLF = "\r\n\r\n"
MAX_BODY_SIZE = 1024 * 1024  # 1 MB


# ============================================================================
# TODO: IMPLEMENTAȚI ACEASTĂ FUNCȚIE
# ============================================================================

def read_request_with_body(client_socket: socket.socket) -> Tuple[str, bytes]:
    """
    Citește un request HTTP complet, inclusiv body-ul.
    
    Args:
        client_socket: Socket-ul clientului
    
    Returns:
        Tuple cu (headers_string, body_bytes)
    
    ALGORITM:
    1. Citește până găsești \\r\\n\\r\\n (end of headers)
    2. Parsează Content-Length din headers
    3. Dacă există Content-Length, citește exact atâția bytes pentru body
    4. Returnează headers și body separat
    
    EDGE CASES:
    - Request fără body (GET, HEAD) → body = b""
    - Content-Length lipsă dar metodă POST → eroare sau body = b""
    - Body mai mare decât MAX_BODY_SIZE → truncare sau eroare
    
    HINT:
    - Citiți în bucle până găsiți DOUBLE_CRLF
    - Aveți grijă că buffer-ul poate conține și partea de început a body-ului
    - Folosiți socket.recv() cu dimensiune mică pentru headers
    """
    
    # TODO: Implementați citirea request-ului cu body
    #
    # Pași sugerați:
    # 1. Inițializați buffer gol
    # 2. Citiți în bucle până găsiți DOUBLE_CRLF
    # 3. Separați headers de ce a mai rămas
    # 4. Parsați Content-Length din headers
    # 5. Calculați câți bytes de body mai trebuie citiți
    # 6. Citiți restul body-ului
    # 7. Returnați (headers_str, body_bytes)
    
    raise NotImplementedError("TODO: Implementați read_request_with_body")


# ============================================================================
# TODO: IMPLEMENTAȚI ACEASTĂ FUNCȚIE
# ============================================================================

def parse_form_data(body: bytes, content_type: str) -> Dict[str, str]:
    """
    Parsează body-ul din format application/x-www-form-urlencoded.
    
    Args:
        body: Body-ul cererii în bytes
        content_type: Valoarea header-ului Content-Type
    
    Returns:
        Dicționar cu parametrii extrași
    
    FORMAT INPUT:
        name=John+Doe&age=25&city=New%20York
    
    FORMAT OUTPUT:
        {"name": "John Doe", "age": "25", "city": "New York"}
    
    DECODIFICARE:
    - + → spațiu
    - %XX → caracter cu cod hex XX
    
    HINT:
    - Verificați că Content-Type începe cu "application/x-www-form-urlencoded"
    - Folosiți urllib.parse.parse_qs() sau implementați manual
    - parse_qs returnează liste, luați primul element
    - Tratați caracterele speciale cu unquote_plus()
    """
    
    # TODO: Implementați parsarea form data
    #
    # Pași sugerați:
    # 1. Verificați content_type
    # 2. Decodifică body din bytes în string
    # 3. Parsați perechi key=value separate de &
    # 4. Decodificați fiecare key și value (URL decoding)
    # 5. Construiți și returnați dicționarul
    
    raise NotImplementedError("TODO: Implementați parse_form_data")


# ============================================================================
# TODO: IMPLEMENTAȚI ACEASTĂ FUNCȚIE
# ============================================================================

def parse_json_body(body: bytes, content_type: str) -> Optional[Dict[str, Any]]:
    """
    Parsează body-ul din format JSON.
    
    Args:
        body: Body-ul cererii în bytes
        content_type: Valoarea header-ului Content-Type
    
    Returns:
        Dicționar parsat sau None dacă parsarea eșuează
    
    HINT:
    - Verificați că Content-Type conține "application/json"
    - Folosiți json.loads()
    - Tratați json.JSONDecodeError
    """
    
    # TODO: Implementați parsarea JSON
    #
    # Pași sugerați:
    # 1. Verificați content_type
    # 2. Decodificați body în string (utf-8)
    # 3. Parsați cu json.loads()
    # 4. Tratați excepțiile și returnați None la eroare
    
    raise NotImplementedError("TODO: Implementați parse_json_body")


# ============================================================================
# TODO: IMPLEMENTAȚI ACEASTĂ FUNCȚIE
# ============================================================================

def build_json_response(status_code: int, data: Dict[str, Any]) -> bytes:
    """
    Construiește un răspuns HTTP cu body JSON.
    
    Args:
        status_code: Codul de status HTTP
        data: Dicționarul de serializat ca JSON
    
    Returns:
        Răspunsul HTTP complet în bytes
    
    EXEMPLU OUTPUT:
        HTTP/1.1 200 OK\r\n
        Content-Type: application/json\r\n
        Content-Length: 42\r\n
        \r\n
        {"success": true, "data": {"name": "John"}}
    
    HINT:
    - Serializați data cu json.dumps()
    - Setați Content-Type: application/json
    - Calculați Content-Length corect
    """
    
    # TODO: Implementați construirea răspunsului JSON
    #
    # Pași sugerați:
    # 1. Serializați data cu json.dumps()
    # 2. Codificați body-ul în bytes (utf-8)
    # 3. Construiți headers (Content-Type, Content-Length)
    # 4. Construiți status line
    # 5. Asamblați răspunsul complet
    
    raise NotImplementedError("TODO: Implementați build_json_response")


# ============================================================================
# TODO: IMPLEMENTAȚI ACEASTĂ FUNCȚIE
# ============================================================================

def handle_post_request(path: str, headers: Dict[str, str], body: bytes) -> bytes:
    """
    Procesează o cerere POST și returnează răspunsul.
    
    Args:
        path: Calea cerută (ex: "/api/form")
        headers: Dicționar cu headers
        body: Body-ul cererii
    
    Returns:
        Răspunsul HTTP în bytes
    
    RUTE SUPORTATE:
    - /api/form: Parsează form data și returnează JSON cu datele primite
    - /api/json: Parsează JSON și returnează JSON cu datele primite (echo)
    - /api/echo: Returnează body-ul primit ca text
    - Altele: 404 Not Found
    
    RĂSPUNS FORMAT:
        {
            "success": true/false,
            "path": "/api/form",
            "method": "POST",
            "data": { ... parsed data ... }
        }
    """
    
    # TODO: Implementați handler-ul POST
    #
    # Pași sugerați:
    # 1. Determinați ruta din path
    # 2. Pentru /api/form: parsați cu parse_form_data()
    # 3. Pentru /api/json: parsați cu parse_json_body()
    # 4. Pentru /api/echo: returnați body-ul direct
    # 5. Construiți răspunsul JSON cu datele procesate
    # 6. Tratați erorile (404, 400 pentru parsare eșuată)
    
    raise NotImplementedError("TODO: Implementați handle_post_request")


# ============================================================================
# COD FURNIZAT - SERVER PRINCIPAL
# ============================================================================

def parse_request_line(first_line: str) -> Tuple[str, str, str]:
    """Parsează request line."""
    parts = first_line.split(" ", 2)
    if len(parts) != 3:
        raise ValueError("Invalid request line")
    return parts[0], parts[1], parts[2]


def parse_headers(header_lines: list) -> Dict[str, str]:
    """Parsează headers în dicționar."""
    headers = {}
    for line in header_lines:
        if ":" in line:
            key, value = line.split(":", 1)
            headers[key.strip().lower()] = value.strip()
    return headers


def run_server(host: str, port: int):
    """Pornește serverul."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server.bind((host, port))
        server.listen(5)
        print(f"[INFO] Server POST pornit pe http://{host}:{port}/")
        print("[INFO] Rute disponibile: /api/form, /api/json, /api/echo")
        print("[INFO] Apăsați Ctrl+C pentru oprire")
        
        while True:
            client, addr = server.accept()
            print(f"[CONN] {addr[0]}:{addr[1]}")
            
            try:
                headers_str, body = read_request_with_body(client)
                lines = headers_str.split(CRLF)
                method, path, version = parse_request_line(lines[0])
                headers = parse_headers(lines[1:])
                
                print(f"[REQ] {method} {path} ({len(body)} bytes body)")
                
                if method == "POST":
                    response = handle_post_request(path, headers, body)
                elif method == "GET":
                    response = build_json_response(200, {
                        "message": "Use POST method for this API",
                        "endpoints": ["/api/form", "/api/json", "/api/echo"]
                    })
                else:
                    response = build_json_response(405, {"error": "Method not allowed"})
                
                client.sendall(response)
                
            except Exception as e:
                print(f"[ERROR] {e}")
                error_resp = build_json_response(500, {"error": str(e)})
                client.sendall(error_resp)
            finally:
                client.close()
                
    except KeyboardInterrupt:
        print("\n[INFO] Server oprit")
    finally:
        server.close()


def main():
    parser = argparse.ArgumentParser(description="Server HTTP cu suport POST")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8081)
    args = parser.parse_args()
    run_server(args.host, args.port)


if __name__ == "__main__":
    main()
