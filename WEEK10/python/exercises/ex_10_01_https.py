#!/usr/bin/env python3
"""
Exercițiul 10.01 – HTTP(S): Semantica cererilor și comportamentul conexiunii

Acest script demonstrează:
- Server HTTPS minimal cu endpoint-uri REST demonstrative
- Client minimal pentru testare și debugging
- Diferențe între coduri de status HTTP (200, 201, 400, 404, 405, 415)
- Rolul headerelor (Content-Type, Cache-Control, Accept)
- Self-test pentru verificare rapidă

Scop pedagogic:
- Să observați că un „API" este, în ultimă instanță, un protocol pe TCP
- Să înțelegeți semantica HTTP (metode, status codes, headere)
- Să măsurați costul real al unei cereri HTTPS (handshake TLS)

Rulare:
    # Server
    python3 ex_10_01_https.py serve --port 8443
    
    # Client
    python3 ex_10_01_https.py client --url https://localhost:8443/health --insecure
    
    # Self-test
    python3 ex_10_01_https.py selftest

Autori: Colectivul Rețele de Calculatoare, ASE București
Revolvix&Hypotheticalandrei
"""
from __future__ import annotations

import argparse
import json
import os
import ssl
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from typing import Dict, Optional, Any

# ==============================================================================
# CONSTANTE
# ==============================================================================

DEFAULT_CERT = "certs/server.crt"
DEFAULT_KEY = "certs/server.key"
SERVER_VERSION = "LabHTTPS/1.0 (Week10)"

# Storage simplu pentru resurse (în memorie)
RESOURCES: Dict[int, Dict[str, Any]] = {
    1: {"id": 1, "name": "Resursa Demo", "created": "2025-01-01"},
}
NEXT_ID = 2

# ==============================================================================
# UTILITĂȚI CERTIFICAT
# ==============================================================================

def ensure_cert(cert_path: str, key_path: str) -> None:
    """
    Generează certificat self-signed dacă nu există.
    
    În producție: nu folosiți self-signed! Aici este suficient pentru laborator.
    Clientul va trebui să folosească --insecure sau să importe certificatul.
    """
    os.makedirs(os.path.dirname(cert_path) or "certs", exist_ok=True)
    
    if os.path.exists(cert_path) and os.path.exists(key_path):
        return
    
    cmd = [
        "openssl", "req", "-x509", "-newkey", "rsa:2048", "-nodes",
        "-keyout", key_path, "-out", cert_path,
        "-days", "7",
        "-subj", "/CN=lab.retele.local/O=ASE-CSIE/C=RO"
    ]
    
    try:
        subprocess.check_call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"[cert] Certificat generat: {cert_path}")
    except FileNotFoundError:
        raise RuntimeError("openssl nu este disponibil. Instalați pachetul 'openssl'.")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Nu am putut genera certificatul: {e}")


# ==============================================================================
# HANDLER HTTP
# ==============================================================================

class LabHTTPHandler(BaseHTTPRequestHandler):
    """
    Handler HTTP cu endpoint-uri demonstrative pentru Săptămâna 10.
    
    Endpoint-uri disponibile:
    - GET  /              - Pagină de start
    - GET  /health        - Health check (status: ok)
    - GET  /resources     - Listare resurse
    - GET  /resources/:id - Obținere resursă
    - POST /resources     - Creare resursă (201 Created)
    - PUT  /resources/:id - Actualizare resursă
    - DELETE /resources/:id - Ștergere resursă (204 No Content)
    - POST /echo          - Echo JSON (necesită Content-Type: application/json)
    - GET  /cache-demo    - Demonstrează Cache-Control
    - *    /405-demo      - Returnează 405 Method Not Allowed
    """
    
    server_version = SERVER_VERSION
    
    def _send_json(self, data: Any, status: int = 200, headers: Optional[Dict[str, str]] = None) -> None:
        """Trimite răspuns JSON."""
        body = json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        if headers:
            for k, v in headers.items():
                self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)
    
    def _send_error_json(self, status: int, message: str) -> None:
        """Trimite eroare în format JSON."""
        self._send_json({"error": message, "status": status}, status=status)
    
    def _read_json_body(self) -> Optional[Dict]:
        """Citește body JSON din cerere."""
        content_type = self.headers.get("Content-Type", "")
        if "application/json" not in content_type:
            return None
        
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return {}
        
        body = self.rfile.read(length)
        try:
            return json.loads(body.decode("utf-8"))
        except json.JSONDecodeError:
            return None
    
    def _parse_resource_id(self) -> Optional[int]:
        """Extrage ID-ul resursei din path."""
        parts = self.path.strip("/").split("/")
        if len(parts) >= 2 and parts[0] == "resources":
            try:
                return int(parts[1])
            except ValueError:
                return None
        return None
    
    # --------------------------------------------------------------------------
    # GET
    # --------------------------------------------------------------------------
    
    def do_GET(self) -> None:
        """Procesează cereri GET."""
        path = self.path.split("?")[0]
        
        if path == "/":
            self._handle_root()
        elif path == "/health":
            self._handle_health()
        elif path == "/resources":
            self._handle_list_resources()
        elif path.startswith("/resources/"):
            self._handle_get_resource()
        elif path == "/cache-demo":
            self._handle_cache_demo()
        elif path == "/405-demo":
            self._send_error_json(405, "GET not allowed on this endpoint")
        else:
            self._send_error_json(404, f"Endpoint {path} not found")
    
    def _handle_root(self) -> None:
        """Pagina de start."""
        html = """<!DOCTYPE html>
<html lang="ro">
<head><meta charset="UTF-8"><title>Lab HTTPS - S10</title></head>
<body style="font-family: sans-serif; max-width: 600px; margin: 2rem auto;">
<h1>🔒 Server HTTPS Demo</h1>
<p>Săptămâna 10 – Rețele de Calculatoare</p>
<h2>Endpoint-uri disponibile:</h2>
<ul>
<li><code>GET /health</code> – Health check</li>
<li><code>GET /resources</code> – Listare resurse</li>
<li><code>GET /resources/:id</code> – Obținere resursă</li>
<li><code>POST /resources</code> – Creare resursă</li>
<li><code>PUT /resources/:id</code> – Actualizare</li>
<li><code>DELETE /resources/:id</code> – Ștergere</li>
<li><code>POST /echo</code> – Echo JSON</li>
<li><code>GET /cache-demo</code> – Cache-Control demo</li>
</ul>
<p><small>Revolvix&amp;Hypotheticalandrei</small></p>
</body>
</html>"""
        body = html.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
    
    def _handle_health(self) -> None:
        """Health check."""
        self._send_json({
            "status": "ok",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "server": SERVER_VERSION
        })
    
    def _handle_list_resources(self) -> None:
        """Listare resurse."""
        self._send_json({
            "resources": list(RESOURCES.values()),
            "total": len(RESOURCES)
        })
    
    def _handle_get_resource(self) -> None:
        """Obținere resursă după ID."""
        res_id = self._parse_resource_id()
        if res_id is None:
            self._send_error_json(400, "Invalid resource ID")
            return
        
        if res_id not in RESOURCES:
            self._send_error_json(404, f"Resource {res_id} not found")
            return
        
        self._send_json(RESOURCES[res_id])
    
    def _handle_cache_demo(self) -> None:
        """Demonstrare Cache-Control."""
        self._send_json(
            {"message": "This response can be cached for 60 seconds", "time": time.time()},
            headers={"Cache-Control": "max-age=60, must-revalidate"}
        )
    
    # --------------------------------------------------------------------------
    # POST
    # --------------------------------------------------------------------------
    
    def do_POST(self) -> None:
        """Procesează cereri POST."""
        global NEXT_ID
        path = self.path.split("?")[0]
        
        if path == "/resources":
            data = self._read_json_body()
            if data is None:
                self._send_error_json(415, "Content-Type must be application/json")
                return
            
            name = data.get("name", "Unnamed")
            new_resource = {
                "id": NEXT_ID,
                "name": name,
                "created": time.strftime("%Y-%m-%d")
            }
            RESOURCES[NEXT_ID] = new_resource
            
            self._send_json(
                new_resource,
                status=201,
                headers={"Location": f"/resources/{NEXT_ID}"}
            )
            NEXT_ID += 1
        
        elif path == "/echo":
            data = self._read_json_body()
            if data is None:
                self._send_error_json(415, "Content-Type must be application/json")
                return
            self._send_json({"echo": data, "received_at": time.time()})
        
        elif path == "/405-demo":
            self._send_error_json(405, "POST not allowed on this endpoint")
        
        else:
            self._send_error_json(404, f"Endpoint {path} not found")
    
    # --------------------------------------------------------------------------
    # PUT
    # --------------------------------------------------------------------------
    
    def do_PUT(self) -> None:
        """Procesează cereri PUT."""
        path = self.path.split("?")[0]
        
        if path.startswith("/resources/"):
            res_id = self._parse_resource_id()
            if res_id is None:
                self._send_error_json(400, "Invalid resource ID")
                return
            
            if res_id not in RESOURCES:
                self._send_error_json(404, f"Resource {res_id} not found")
                return
            
            data = self._read_json_body()
            if data is None:
                self._send_error_json(415, "Content-Type must be application/json")
                return
            
            RESOURCES[res_id]["name"] = data.get("name", RESOURCES[res_id]["name"])
            self._send_json(RESOURCES[res_id])
        else:
            self._send_error_json(404, f"Endpoint {path} not found")
    
    # --------------------------------------------------------------------------
    # DELETE
    # --------------------------------------------------------------------------
    
    def do_DELETE(self) -> None:
        """Procesează cereri DELETE."""
        path = self.path.split("?")[0]
        
        if path.startswith("/resources/"):
            res_id = self._parse_resource_id()
            if res_id is None:
                self._send_error_json(400, "Invalid resource ID")
                return
            
            if res_id not in RESOURCES:
                self._send_error_json(404, f"Resource {res_id} not found")
                return
            
            del RESOURCES[res_id]
            self.send_response(204)
            self.end_headers()
        else:
            self._send_error_json(404, f"Endpoint {path} not found")
    
    # --------------------------------------------------------------------------
    # OPTIONS (CORS preflight)
    # --------------------------------------------------------------------------
    
    def do_OPTIONS(self) -> None:
        """CORS preflight."""
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
    
    def log_message(self, format: str, *args) -> None:
        """Custom logging."""
        print(f"[{time.strftime('%H:%M:%S')}] {args[0]}")


# ==============================================================================
# SERVER
# ==============================================================================

def run_server(host: str, port: int, cert: str, key: str) -> None:
    """Pornește serverul HTTPS."""
    ensure_cert(cert, key)
    
    server = ThreadingHTTPServer((host, port), LabHTTPHandler)
    
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(cert, key)
    server.socket = context.wrap_socket(server.socket, server_side=True)
    
    print(f"[server] HTTPS server pornit pe https://{host}:{port}/")
    print(f"[server] Certificate: {cert}")
    print("[server] Apăsați Ctrl+C pentru oprire.")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[server] Oprire...")
        server.shutdown()


# ==============================================================================
# CLIENT
# ==============================================================================

def run_client(url: str, method: str, data: Optional[str], insecure: bool) -> int:
    """Execută cerere HTTP(S)."""
    
    # Creare context SSL
    if insecure:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
    else:
        ctx = None
    
    # Creare cerere
    req = Request(url, method=method)
    req.add_header("User-Agent", "LabHTTPS-Client/1.0")
    
    if data:
        body = data.encode("utf-8")
        req.data = body
        req.add_header("Content-Type", "application/json")
        req.add_header("Content-Length", str(len(body)))
    
    # Măsurare timp
    start = time.perf_counter()
    
    try:
        with urlopen(req, context=ctx, timeout=10) as resp:
            elapsed = (time.perf_counter() - start) * 1000
            
            print(f"[client] {method} {url}")
            print(f"[client] Status: {resp.status} {resp.reason}")
            print(f"[client] Time: {elapsed:.1f} ms")
            print(f"[client] Headers:")
            for h, v in resp.headers.items():
                print(f"         {h}: {v}")
            
            body = resp.read().decode("utf-8")
            if body:
                print(f"[client] Body:")
                print(body[:1000])
            
            return 0
    
    except HTTPError as e:
        elapsed = (time.perf_counter() - start) * 1000
        print(f"[client] HTTP Error: {e.code} {e.reason}")
        print(f"[client] Time: {elapsed:.1f} ms")
        body = e.read().decode("utf-8")
        if body:
            print(f"[client] Body: {body[:500]}")
        return 1
    
    except URLError as e:
        print(f"[client] Connection Error: {e.reason}")
        return 2


# ==============================================================================
# SELF-TEST
# ==============================================================================

def run_selftest() -> int:
    """Rulează self-test: pornește server, execută cereri, verifică rezultate."""
    import socket
    
    # Găsește port liber
    with socket.socket() as s:
        s.bind(("", 0))
        port = s.getsockname()[1]
    
    cert = "certs/test_server.crt"
    key = "certs/test_server.key"
    
    print(f"[selftest] Pornire server pe portul {port}...")
    ensure_cert(cert, key)
    
    # Pornire server în thread
    server = ThreadingHTTPServer(("127.0.0.1", port), LabHTTPHandler)
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(cert, key)
    server.socket = context.wrap_socket(server.socket, server_side=True)
    
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    time.sleep(0.5)
    
    base_url = f"https://127.0.0.1:{port}"
    errors = 0
    
    # SSL context pentru client
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    tests = [
        ("GET", "/health", None, 200),
        ("GET", "/resources", None, 200),
        ("POST", "/resources", '{"name":"Test"}', 201),
        ("GET", "/resources/1", None, 200),
        ("PUT", "/resources/1", '{"name":"Updated"}', 200),
        ("GET", "/nonexistent", None, 404),
        ("POST", "/echo", '{"test":true}', 200),
    ]
    
    print(f"[selftest] Rulare {len(tests)} teste...")
    
    for method, path, body, expected_status in tests:
        url = base_url + path
        req = Request(url, method=method)
        req.add_header("Content-Type", "application/json")
        if body:
            req.data = body.encode("utf-8")
        
        try:
            with urlopen(req, context=ctx, timeout=5) as resp:
                status = resp.status
        except HTTPError as e:
            status = e.code
        except Exception as e:
            print(f"  ✗ {method} {path} - Error: {e}")
            errors += 1
            continue
        
        if status == expected_status:
            print(f"  ✓ {method} {path} → {status}")
        else:
            print(f"  ✗ {method} {path} → {status} (expected {expected_status})")
            errors += 1
    
    server.shutdown()
    
    print()
    if errors == 0:
        print("[selftest] Toate testele au trecut! ✓")
        return 0
    else:
        print(f"[selftest] {errors} test(e) eșuat(e)!")
        return 1


# ==============================================================================
# MAIN
# ==============================================================================

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Exercițiul 10.01 – Server/Client HTTPS demonstrativ"
    )
    subparsers = parser.add_subparsers(dest="command", help="Comandă")
    
    # serve
    serve_parser = subparsers.add_parser("serve", help="Pornește serverul HTTPS")
    serve_parser.add_argument("--bind", default="0.0.0.0", help="Adresă bind")
    serve_parser.add_argument("--port", type=int, default=8443, help="Port (default: 8443)")
    serve_parser.add_argument("--cert", default=DEFAULT_CERT, help="Cale certificat")
    serve_parser.add_argument("--key", default=DEFAULT_KEY, help="Cale cheie privată")
    
    # client
    client_parser = subparsers.add_parser("client", help="Execută cerere HTTP(S)")
    client_parser.add_argument("--url", required=True, help="URL complet")
    client_parser.add_argument("--method", default="GET", help="Metodă HTTP")
    client_parser.add_argument("--data", default=None, help="Body JSON")
    client_parser.add_argument("--insecure", action="store_true", help="Ignoră certificat")
    
    # selftest
    subparsers.add_parser("selftest", help="Rulează self-test")
    
    args = parser.parse_args()
    
    if args.command == "serve":
        run_server(args.bind, args.port, args.cert, args.key)
        return 0
    elif args.command == "client":
        return run_client(args.url, args.method, args.data, args.insecure)
    elif args.command == "selftest":
        return run_selftest()
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
