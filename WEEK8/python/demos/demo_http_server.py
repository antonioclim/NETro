#!/usr/bin/env python3
"""
demo_http_server.py - Server HTTP minimal implementat cu socket-uri.

Săptămâna 8 – Demo: Server HTTP (nivel aplicație peste TCP)

═══════════════════════════════════════════════════════════════════════════════
CE VOM ÎNVĂȚA
═══════════════════════════════════════════════════════════════════════════════
- Înțelegerea structurii request/response HTTP la nivel de bytes
- Observarea three-way handshake și comunicării TCP în tcpdump
- Implementarea parsing-ului HTTP request line și headers
- Servirea fișierelor statice cu Content-Type și Content-Length corecte
- Protecția împotriva atacurilor de tip directory traversal

═══════════════════════════════════════════════════════════════════════════════
LIMITĂRI INTENȚIONATE (pentru claritate didactică)
═══════════════════════════════════════════════════════════════════════════════
- Suportă doar GET și HEAD (fără POST/PUT)
- Nu suportă chunked transfer encoding
- Connection: close (un request per conexiune TCP)
- Nu suportă HTTP/2 sau HTTP/3

═══════════════════════════════════════════════════════════════════════════════
UTILIZARE
═══════════════════════════════════════════════════════════════════════════════
    # Pornire server
    python3 demo_http_server.py --host 127.0.0.1 --port 8080 --www ./www
    
    # Test cu curl
    curl -v http://127.0.0.1:8080/
    curl -v http://127.0.0.1:8080/index.html
    
    # Observare în tcpdump (three-way handshake + request/response)
    sudo tcpdump -i lo port 8080 -nn -A

Autor: Rețele de Calculatoare, ASE București, 2025
Revolvix&Hypotheticalandrei
"""

from __future__ import annotations

import argparse
import os
import socket
import sys
import threading
import time
from typing import Optional

# Adaugă directorul utils în path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.net_utils import (
    read_until,
    parse_http_request,
    safe_map_target_to_path,
    build_response,
    guess_content_type,
    format_bytes,
    get_ephemeral_port,
)


# ═══════════════════════════════════════════════════════════════════════════════
# Configurare logging cu culori
# ═══════════════════════════════════════════════════════════════════════════════

COLORS = {
    "INFO": "\033[0;32m",     # verde
    "WARN": "\033[0;33m",     # galben  
    "ERROR": "\033[0;31m",    # roșu
    "DEBUG": "\033[0;36m",    # cyan
    "RESET": "\033[0m",
}


def log(msg: str, level: str = "INFO") -> None:
    """Logging simplu cu timestamp și culori."""
    ts = time.strftime("%H:%M:%S")
    color = COLORS.get(level, "")
    reset = COLORS["RESET"] if color else ""
    print(f"[{ts}] {color}[{level}]{reset} {msg}")


# ═══════════════════════════════════════════════════════════════════════════════
# Handler pentru conexiuni client
# ═══════════════════════════════════════════════════════════════════════════════

def handle_client(conn: socket.socket, 
                  addr: tuple, 
                  www_root: str, 
                  backend_id: str) -> None:
    """
    Procesează un client HTTP.
    
    ALGORITM (pas cu pas):
    1. Citește request-ul (până la CRLFCRLF - delimitator HTTP)
    2. Parsează request line (METHOD TARGET VERSION)
    3. Validează metoda (doar GET/HEAD)
    4. Mapează target la fișier (cu protecție directory traversal!)
    5. Citește fișierul sau generează 404
    6. Trimite răspunsul HTTP complet
    7. Închide conexiunea
    
    Args:
        conn: Socket-ul conexiunii acceptate
        addr: Adresa clientului (ip, port)
        www_root: Directorul rădăcină pentru fișiere
        backend_id: Identificator pentru header-ul X-Backend
    """
    client_ip, client_port = addr
    log(f"[+] Conexiune nouă: {client_ip}:{client_port}", "INFO")
    
    try:
        # ─────────────────────────────────────────────────────────────────────
        # PASUL 1: Citire request HTTP
        # ─────────────────────────────────────────────────────────────────────
        # HTTP/1.x folosește CRLF (\r\n) ca delimitator
        # Un request HTTP termină header-ele cu o linie goală (CRLFCRLF)
        raw = read_until(conn, marker=b"\r\n\r\n", timeout=5.0)
        
        # ─────────────────────────────────────────────────────────────────────
        # PASUL 2: Parsare request
        # ─────────────────────────────────────────────────────────────────────
        req = parse_http_request(raw)
        log(f"    {req.method} {req.target} {req.version}", "DEBUG")
        
        # ─────────────────────────────────────────────────────────────────────
        # PASUL 3: Validare metodă HTTP
        # ─────────────────────────────────────────────────────────────────────
        # În acest demo acceptăm doar GET și HEAD
        # GET: returnează headers + body
        # HEAD: returnează doar headers (util pentru verificare existență)
        if req.method not in ("GET", "HEAD"):
            body = b"405 Method Not Allowed\n\nAcest server suporta doar GET si HEAD.\n"
            resp = build_response(405, body, extra_headers={"X-Backend": backend_id})
            conn.sendall(resp)
            log(f"    → 405 Method Not Allowed ({req.method})", "WARN")
            return
        
        # ─────────────────────────────────────────────────────────────────────
        # PASUL 4: Mapare path → fișier (CU SECURITATE!)
        # ─────────────────────────────────────────────────────────────────────
        filepath, error = safe_map_target_to_path(req.target, www_root)
        
        # Verificăm erori de securitate
        if error == "URI_TOO_LONG":
            resp = build_response(414, b"URI Too Long\n", 
                                  extra_headers={"X-Backend": backend_id})
            conn.sendall(resp)
            log(f"    → 414 URI Too Long", "WARN")
            return
        
        if error == "TRAVERSAL":
            # ATENȚIE: Directory traversal detectat!
            # Un atacator încearcă să acceseze fișiere din afara www_root
            # Ex: GET /../../../etc/passwd
            resp = build_response(400, b"Bad Request\n", 
                                  extra_headers={"X-Backend": backend_id})
            conn.sendall(resp)
            log(f"    → 400 Bad Request (directory traversal detectat!)", "WARN")
            return
        
        # ─────────────────────────────────────────────────────────────────────
        # PASUL 5: Verificare existență fișier
        # ─────────────────────────────────────────────────────────────────────
        if not filepath or not os.path.isfile(filepath):
            body = b"<!DOCTYPE html>\n<html><body><h1>404 - Not Found</h1><p>Resursa nu exista.</p></body></html>\n"
            resp = build_response(404, body, 
                                  content_type="text/html; charset=utf-8",
                                  extra_headers={"X-Backend": backend_id})
            conn.sendall(resp)
            log(f"    → 404 Not Found: {req.target}", "WARN")
            return
        
        # ─────────────────────────────────────────────────────────────────────
        # PASUL 6: Citire și trimitere fișier
        # ─────────────────────────────────────────────────────────────────────
        with open(filepath, "rb") as f:
            content = f.read()
        
        content_type = guess_content_type(filepath)
        extra_headers = {"X-Backend": backend_id}
        
        if req.method == "HEAD":
            # HEAD: trimitem header-ele, dar fără body
            # IMPORTANT: Content-Length trebuie să reflecte dimensiunea reală!
            resp = build_response(200, b"", 
                                  content_type=content_type,
                                  extra_headers=extra_headers)
            # Corectăm Content-Length pentru HEAD
            resp = resp.replace(
                b"Content-Length: 0\r\n", 
                f"Content-Length: {len(content)}\r\n".encode("ascii")
            )
            conn.sendall(resp)
            log(f"    → 200 OK (HEAD) {format_bytes(len(content))}", "INFO")
        else:
            # GET: trimitem header-ele + body
            resp = build_response(200, content, 
                                  content_type=content_type,
                                  extra_headers=extra_headers)
            conn.sendall(resp)
            log(f"    → 200 OK {format_bytes(len(content))}", "INFO")
    
    # ─────────────────────────────────────────────────────────────────────────
    # Tratare erori
    # ─────────────────────────────────────────────────────────────────────────
    except TimeoutError:
        log(f"    → 408 Request Timeout", "WARN")
        try:
            conn.sendall(build_response(408, b"Request Timeout\n"))
        except Exception:
            pass
    
    except ValueError as e:
        log(f"    → 400 Bad Request: {e}", "WARN")
        try:
            conn.sendall(build_response(400, f"Bad Request: {e}\n".encode()))
        except Exception:
            pass
    
    except Exception as e:
        log(f"    → 500 Internal Server Error: {e}", "ERROR")
        try:
            conn.sendall(build_response(500, b"Internal Server Error\n"))
        except Exception:
            pass
    
    finally:
        try:
            conn.close()
        except Exception:
            pass
        log(f"[-] Conexiune închisă: {client_ip}:{client_port}", "DEBUG")


# ═══════════════════════════════════════════════════════════════════════════════
# Funcția principală de server
# ═══════════════════════════════════════════════════════════════════════════════

def serve(host: str, port: int, www_root: str, backend_id: str, threaded: bool) -> None:
    """
    Pornește serverul HTTP.
    
    PAȘI SOCKET:
    1. socket()     - Creare socket TCP
    2. setsockopt() - Opțiuni (SO_REUSEADDR pentru restart rapid)
    3. bind()       - Asociere cu adresa și portul
    4. listen()     - Activare mod server (ascultă conexiuni)
    5. accept()     - Acceptare conexiuni (blocare până vine client)
    
    Args:
        host: Adresa pe care se face bind (0.0.0.0 pentru toate interfețele)
        port: Portul TCP
        www_root: Directorul cu fișiere statice
        backend_id: Identificator pentru header-ul X-Backend
        threaded: True pentru mod multi-threaded
    """
    www_root = os.path.abspath(www_root)
    
    # Verificare director www
    if not os.path.isdir(www_root):
        log(f"EROARE: Directorul '{www_root}' nu există!", "ERROR")
        sys.exit(1)
    
    # ─────────────────────────────────────────────────────────────────────────
    # Creare și configurare socket server
    # ─────────────────────────────────────────────────────────────────────────
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        # SO_REUSEADDR: permite refolosirea portului imediat după închidere
        # Fără această opțiune, portul rămâne în TIME_WAIT ~2 minute
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # Bind: asociere socket cu (host, port)
        server.bind((host, port))
        
        # Listen: activează modul server, backlog=50 (max conexiuni în așteptare)
        server.listen(50)
        
        mode = "multi-threaded" if threaded else "single-threaded"
        log(f"Server HTTP pornit pe http://{host}:{port}/", "INFO")
        log(f"  www_root: {www_root}", "INFO")
        log(f"  backend_id: {backend_id}", "INFO")
        log(f"  mode: {mode}", "INFO")
        log(f"Press Ctrl+C to stop.", "INFO")
        print()
        
        try:
            while True:
                # Accept: blochează până vine o conexiune
                # Returnează (socket nou pentru client, adresa client)
                conn, addr = server.accept()
                
                if threaded:
                    # Mod multi-threaded: fiecare client în thread separat
                    # daemon=True: thread-ul se oprește când main thread se oprește
                    t = threading.Thread(
                        target=handle_client, 
                        args=(conn, addr, www_root, backend_id),
                        daemon=True
                    )
                    t.start()
                else:
                    # Mod single-threaded: procesăm secvențial
                    # Doar pentru debugging (un singur client la un moment dat)
                    handle_client(conn, addr, www_root, backend_id)
        
        except KeyboardInterrupt:
            print()
            log("Server oprit (Ctrl+C)", "INFO")


# ═══════════════════════════════════════════════════════════════════════════════
# Self-test
# ═══════════════════════════════════════════════════════════════════════════════

def selftest() -> int:
    """
    Test minimal local pentru verificarea funcționalității.
    
    Returns:
        0 dacă testul trece, 1 altfel
    """
    log("Rulare selftest...", "INFO")
    
    # Pregătire - căutăm directorul www
    www_root = os.path.join(os.path.dirname(__file__), "..", "..", "www")
    if not os.path.isdir(www_root):
        www_root = os.path.join(os.path.dirname(__file__), "www")
    if not os.path.isdir(www_root):
        log("Directorul www nu a fost găsit pentru selftest", "ERROR")
        return 1
    
    host = "127.0.0.1"
    port = get_ephemeral_port()
    
    # Pornim serverul în thread
    thread = threading.Thread(
        target=serve, 
        args=(host, port, www_root, "selftest", True),
        daemon=True
    )
    thread.start()
    time.sleep(0.5)
    
    # Test 1: GET /
    try:
        with socket.create_connection((host, port), timeout=2.0) as c:
            c.sendall(b"GET / HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n")
            data = c.recv(4096)
        
        if b"HTTP/1.1 200" in data:
            log("✓ Test GET / → 200 OK", "INFO")
        else:
            log(f"✗ Test GET / → răspuns neașteptat", "ERROR")
            return 1
    except Exception as e:
        log(f"✗ Test GET / eșuat: {e}", "ERROR")
        return 1
    
    # Test 2: GET /not-found → 404
    try:
        with socket.create_connection((host, port), timeout=2.0) as c:
            c.sendall(b"GET /not-found HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n")
            data = c.recv(4096)
        
        if b"HTTP/1.1 404" in data:
            log("✓ Test GET /not-found → 404 Not Found", "INFO")
        else:
            log(f"✗ Test 404 → răspuns neașteptat", "ERROR")
            return 1
    except Exception as e:
        log(f"✗ Test 404 eșuat: {e}", "ERROR")
        return 1
    
    # Test 3: Directory traversal → 400
    try:
        with socket.create_connection((host, port), timeout=2.0) as c:
            c.sendall(b"GET /../../../etc/passwd HTTP/1.1\r\nHost: localhost\r\n\r\n")
            data = c.recv(4096)
        
        if b"HTTP/1.1 400" in data:
            log("✓ Test directory traversal → 400 Bad Request", "INFO")
        else:
            log(f"✗ Directory traversal nu a fost blocat!", "ERROR")
            return 1
    except Exception as e:
        log(f"✗ Test traversal eșuat: {e}", "ERROR")
        return 1
    
    log("Toate testele au trecut!", "INFO")
    return 0


# ═══════════════════════════════════════════════════════════════════════════════
# Entry point
# ═══════════════════════════════════════════════════════════════════════════════

def main() -> int:
    """Entry point principal."""
    parser = argparse.ArgumentParser(
        description="Server HTTP minimal cu socket-uri (demo didactic) - Săptămâna 8",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemple:
  python3 demo_http_server.py --port 8080 --www ./www
  python3 demo_http_server.py --host 0.0.0.0 --port 80 --id backend-A
  python3 demo_http_server.py --selftest
        """
    )
    parser.add_argument("--host", default="0.0.0.0",
                        help="Adresa pe care ascultă serverul (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8080,
                        help="Portul TCP (default: 8080)")
    parser.add_argument("--www", default=os.path.join(os.path.dirname(__file__), 
                                                       "..", "..", "www"),
                        help="Directorul cu fișiere statice")
    parser.add_argument("--id", dest="backend_id", default="http-server",
                        help="Identificator pentru header-ul X-Backend")
    parser.add_argument("--mode", choices=["single", "threaded"], default="threaded",
                        help="Mod de execuție (default: threaded)")
    parser.add_argument("--selftest", action="store_true",
                        help="Rulează testul automat")
    
    args = parser.parse_args()
    
    if args.selftest:
        return selftest()
    
    serve(args.host, args.port, args.www, args.backend_id, 
          threaded=(args.mode == "threaded"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
