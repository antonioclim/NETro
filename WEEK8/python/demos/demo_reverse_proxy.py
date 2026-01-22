#!/usr/bin/env python3
"""
demo_reverse_proxy.py - Reverse Proxy cu Load Balancing Round-Robin.

Săptămâna 8 – Demo: Reverse Proxy HTTP

═══════════════════════════════════════════════════════════════════════════════
CE VOM ÎNVĂȚA
═══════════════════════════════════════════════════════════════════════════════
- Conceptul de reverse proxy și rolul său în arhitecturi web
- Implementarea load balancing cu algoritm round-robin
- Modificarea header-elor HTTP (X-Forwarded-For, X-Forwarded-Host)
- Observarea a două conexiuni TCP distincte (client→proxy, proxy→backend)
- Înțelegerea diferenței dintre proxy și direct connection

═══════════════════════════════════════════════════════════════════════════════
ARHITECTURĂ
═══════════════════════════════════════════════════════════════════════════════

    ┌────────┐          ┌─────────────────┐          ┌───────────┐
    │ Client │ ───────→ │  Reverse Proxy  │ ───────→ │ Backend A │
    │        │          │   (port 8080)   │          │ (port 9001)│
    └────────┘          │                 │          └───────────┘
                        │  Round-Robin    │          ┌───────────┐
                        │                 │ ───────→ │ Backend B │
                        │                 │          │ (port 9002)│
                        └─────────────────┘          └───────────┘

═══════════════════════════════════════════════════════════════════════════════
UTILIZARE
═══════════════════════════════════════════════════════════════════════════════
    # Pornire reverse proxy cu 2 backends
    python3 demo_reverse_proxy.py --listen-port 8080 \\
        --backends 127.0.0.1:9001,127.0.0.1:9002
    
    # Test (observă alternarea backend-urilor)
    for i in {1..6}; do curl -s http://localhost:8080/ -D - | grep X-Backend; done
    
    # Captură tcpdump (vezi cele 2 conexiuni TCP)
    sudo tcpdump -i lo '(port 8080 or port 9001 or port 9002)' -nn

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
import uuid
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

# Adaugă directorul utils în path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.net_utils import (
    read_until,
    parse_http_request,
    build_response,
    get_ephemeral_port,
)


# ═══════════════════════════════════════════════════════════════════════════════
# Logging
# ═══════════════════════════════════════════════════════════════════════════════

COLORS = {
    "INFO": "\033[0;32m",
    "WARN": "\033[0;33m",
    "ERROR": "\033[0;31m",
    "DEBUG": "\033[0;36m",
    "PROXY": "\033[0;35m",  # magenta pentru proxy
    "RESET": "\033[0m",
}

def log(msg: str, level: str = "INFO") -> None:
    ts = time.strftime("%H:%M:%S")
    color = COLORS.get(level, "")
    reset = COLORS["RESET"]
    print(f"[{ts}] {color}[{level}]{reset} {msg}")


# ═══════════════════════════════════════════════════════════════════════════════
# Backend și Load Balancer
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Backend:
    """Reprezentare a unui server backend."""
    host: str
    port: int
    name: str = ""
    
    def __post_init__(self):
        if not self.name:
            self.name = f"{self.host}:{self.port}"
    
    @classmethod
    def from_string(cls, s: str, name: str = "") -> "Backend":
        """Parsează 'host:port' în Backend."""
        if ":" in s:
            host, port_str = s.rsplit(":", 1)
            return cls(host=host, port=int(port_str), name=name)
        else:
            return cls(host=s, port=80, name=name)


class RoundRobinBalancer:
    """
    Load balancer cu algoritm Round-Robin.
    
    Round-Robin: Distribuție ciclică echilibrată
    - Request 1 → Backend A
    - Request 2 → Backend B  
    - Request 3 → Backend A
    - ...
    
    Thread-safe prin lock.
    """
    
    def __init__(self, backends: List[Backend]):
        self.backends = backends
        self._index = 0
        self._lock = threading.Lock()
        log(f"RoundRobin inițializat cu {len(backends)} backends", "INFO")
    
    def next(self) -> Backend:
        """Returnează următorul backend în rotație."""
        with self._lock:
            backend = self.backends[self._index]
            self._index = (self._index + 1) % len(self.backends)
            return backend
    
    def get_all(self) -> List[Backend]:
        """Returnează lista tuturor backends."""
        return self.backends.copy()


# ═══════════════════════════════════════════════════════════════════════════════
# Reverse Proxy
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ProxyConfig:
    """Configurație reverse proxy."""
    listen_host: str
    listen_port: int
    backends: List[Backend]
    timeout: float = 10.0


class ReverseProxy:
    """
    Reverse Proxy HTTP cu load balancing.
    
    FUNCȚIONALITĂȚI:
    - Acceptă conexiuni de la clienți
    - Selectează backend cu round-robin
    - Forward request către backend (cu modificare headers)
    - Forward response către client
    - Adaugă header-uri informative (X-Forwarded-*, Via)
    """
    
    def __init__(self, config: ProxyConfig):
        self.config = config
        self.balancer = RoundRobinBalancer(config.backends)
    
    def serve_forever(self) -> None:
        """Pornește proxy-ul și acceptă conexiuni."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind((self.config.listen_host, self.config.listen_port))
            server.listen(100)
            
            backends_str = ", ".join(b.name for b in self.config.backends)
            log(f"Reverse Proxy pornit pe {self.config.listen_host}:{self.config.listen_port}", "PROXY")
            log(f"  Backends: {backends_str}", "PROXY")
            log(f"  Algoritm: Round-Robin", "PROXY")
            log("Press Ctrl+C to stop.", "INFO")
            print()
            
            try:
                while True:
                    conn, addr = server.accept()
                    # Fiecare conexiune în thread separat
                    t = threading.Thread(
                        target=self._handle_client,
                        args=(conn, addr),
                        daemon=True
                    )
                    t.start()
            except KeyboardInterrupt:
                print()
                log("Proxy oprit (Ctrl+C)", "INFO")
    
    def _handle_client(self, client_conn: socket.socket, client_addr: Tuple[str, int]) -> None:
        """
        Procesează o conexiune de la client.
        
        FLUX:
        1. Citește request de la client
        2. Selectează backend (round-robin)
        3. Modifică headers (X-Forwarded-For, etc.)
        4. Deschide conexiune către backend
        5. Trimite request modificat
        6. Citește response de la backend
        7. Trimite response către client
        """
        client_ip, client_port = client_addr
        request_id = str(uuid.uuid4())[:8]  # ID scurt pentru logging
        
        log(f"[{request_id}] Conexiune de la {client_ip}:{client_port}", "PROXY")
        
        with client_conn:
            try:
                # ─────────────────────────────────────────────────────────────
                # Pas 1: Citire request de la client
                # ─────────────────────────────────────────────────────────────
                raw_request = read_until(client_conn, b"\r\n\r\n", timeout=self.config.timeout)
                if not raw_request:
                    return
                
                req = parse_http_request(raw_request)
                log(f"[{request_id}] → {req.method} {req.target}", "DEBUG")
                
                # ─────────────────────────────────────────────────────────────
                # Pas 2: Selectare backend (round-robin)
                # ─────────────────────────────────────────────────────────────
                backend = self.balancer.next()
                log(f"[{request_id}] Backend selectat: {backend.name}", "PROXY")
                
                # ─────────────────────────────────────────────────────────────
                # Pas 3: Modificare headers pentru forward
                # ─────────────────────────────────────────────────────────────
                # Aceste header-uri informează backend-ul despre clientul original
                forward_headers = req.headers.copy()
                
                # X-Forwarded-For: IP-ul clientului original
                # (poate fi lanț dacă sunt mai multe proxy-uri)
                existing_xff = forward_headers.get("x-forwarded-for", "")
                if existing_xff:
                    forward_headers["x-forwarded-for"] = f"{existing_xff}, {client_ip}"
                else:
                    forward_headers["x-forwarded-for"] = client_ip
                
                # X-Forwarded-Host: Host-ul original cerut de client
                if "host" in forward_headers:
                    forward_headers["x-forwarded-host"] = forward_headers["host"]
                
                # X-Forwarded-Proto: Protocolul original (http în cazul nostru)
                forward_headers["x-forwarded-proto"] = "http"
                
                # Via: Identificare proxy (pentru debugging)
                forward_headers["via"] = "1.1 ASE-S8-Proxy"
                
                # X-Request-ID: Pentru corelarea logurilor
                forward_headers["x-request-id"] = request_id
                
                # Host: Actualizăm la backend
                forward_headers["host"] = f"{backend.host}:{backend.port}"
                
                # Connection: close (simplificare, nu menținem conexiuni)
                forward_headers["connection"] = "close"
                
                # Eliminăm header-uri specifice proxy-urilor
                forward_headers.pop("proxy-connection", None)
                forward_headers.pop("keep-alive", None)
                
                # ─────────────────────────────────────────────────────────────
                # Pas 4: Construire request pentru backend
                # ─────────────────────────────────────────────────────────────
                request_lines = [f"{req.method} {req.target} {req.version}"]
                for key, value in forward_headers.items():
                    request_lines.append(f"{key}: {value}")
                forward_request = "\r\n".join(request_lines).encode("iso-8859-1") + b"\r\n\r\n"
                
                # ─────────────────────────────────────────────────────────────
                # Pas 5: Forward către backend
                # ─────────────────────────────────────────────────────────────
                try:
                    with socket.create_connection(
                        (backend.host, backend.port), 
                        timeout=self.config.timeout
                    ) as backend_conn:
                        backend_conn.sendall(forward_request)
                        
                        # Pas 6: Citire response de la backend
                        response_data = b""
                        while True:
                            chunk = backend_conn.recv(8192)
                            if not chunk:
                                break
                            response_data += chunk
                
                except (socket.timeout, ConnectionRefusedError, OSError) as e:
                    # Backend indisponibil
                    log(f"[{request_id}] Backend {backend.name} indisponibil: {e}", "ERROR")
                    error_body = b"502 Bad Gateway\n\nBackend server indisponibil.\n"
                    error_resp = build_response(502, error_body, 
                                                extra_headers={"X-Proxy-Error": str(e)})
                    client_conn.sendall(error_resp)
                    return
                
                # ─────────────────────────────────────────────────────────────
                # Pas 7: Adăugare header X-Served-By în response
                # ─────────────────────────────────────────────────────────────
                # Injectăm header pentru a vedea care backend a servit request-ul
                response_data = self._inject_response_header(
                    response_data, "X-Served-By", backend.name
                )
                response_data = self._inject_response_header(
                    response_data, "X-Request-ID", request_id
                )
                
                # ─────────────────────────────────────────────────────────────
                # Pas 8: Trimitere response către client
                # ─────────────────────────────────────────────────────────────
                client_conn.sendall(response_data)
                
                log(f"[{request_id}] ← Response {len(response_data)} bytes via {backend.name}", "PROXY")
            
            except TimeoutError:
                log(f"[{request_id}] Timeout la citire request", "WARN")
            except ValueError as e:
                log(f"[{request_id}] Request invalid: {e}", "WARN")
            except Exception as e:
                log(f"[{request_id}] Eroare proxy: {e}", "ERROR")
    
    @staticmethod
    def _inject_response_header(response: bytes, header: str, value: str) -> bytes:
        """Injectează un header în răspunsul HTTP."""
        try:
            # Separăm headers de body
            if b"\r\n\r\n" not in response:
                return response
            
            head, sep, body = response.partition(b"\r\n\r\n")
            
            # Verificăm că e HTTP
            if not head.startswith(b"HTTP/"):
                return response
            
            # Verificăm să nu existe deja header-ul
            header_lower = header.lower().encode("ascii")
            for line in head.split(b"\r\n")[1:]:
                if line.lower().startswith(header_lower + b":"):
                    return response  # Există deja
            
            # Adăugăm header-ul
            new_header = f"{header}: {value}".encode("ascii")
            new_head = head + b"\r\n" + new_header
            
            return new_head + b"\r\n\r\n" + body
        
        except Exception:
            return response


# ═══════════════════════════════════════════════════════════════════════════════
# Self-test
# ═══════════════════════════════════════════════════════════════════════════════

def selftest() -> int:
    """Test automat pentru reverse proxy."""
    log("Rulare selftest pentru reverse proxy...", "INFO")
    
    # Pentru test complet, am avea nevoie de backend-uri
    # Aici facem doar un test de inițializare
    
    backends = [
        Backend.from_string("127.0.0.1:9001", "backend-A"),
        Backend.from_string("127.0.0.1:9002", "backend-B"),
    ]
    
    balancer = RoundRobinBalancer(backends)
    
    # Test round-robin
    selected = [balancer.next().name for _ in range(6)]
    expected = ["backend-A", "backend-B", "backend-A", "backend-B", "backend-A", "backend-B"]
    
    if selected == expected:
        log("✓ Round-robin funcționează corect", "INFO")
        log(f"  Selecții: {' → '.join(selected)}", "DEBUG")
        return 0
    else:
        log("✗ Round-robin incorect", "ERROR")
        log(f"  Așteptat: {expected}", "ERROR")
        log(f"  Obținut: {selected}", "ERROR")
        return 1


# ═══════════════════════════════════════════════════════════════════════════════
# Entry point
# ═══════════════════════════════════════════════════════════════════════════════

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Reverse Proxy HTTP cu Load Balancing - Săptămâna 8",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemple:
  # Proxy către un singur backend
  python3 demo_reverse_proxy.py --backends 127.0.0.1:9001
  
  # Proxy cu round-robin între 2 backends
  python3 demo_reverse_proxy.py --backends 127.0.0.1:9001,127.0.0.1:9002
  
  # Test round-robin
  for i in {1..6}; do curl -s localhost:8080/ -D - | grep X-Served-By; done
        """
    )
    parser.add_argument("--listen-host", default="0.0.0.0",
                        help="Adresa de ascultare (default: 0.0.0.0)")
    parser.add_argument("--listen-port", type=int, default=8080,
                        help="Portul de ascultare (default: 8080)")
    parser.add_argument("--backends", required=False,
                        default="127.0.0.1:9001,127.0.0.1:9002",
                        help="Lista backend-uri (host:port,host:port,...)")
    parser.add_argument("--timeout", type=float, default=10.0,
                        help="Timeout conexiuni (default: 10s)")
    parser.add_argument("--selftest", action="store_true",
                        help="Rulează testul automat")
    
    args = parser.parse_args()
    
    if args.selftest:
        return selftest()
    
    # Parsare backends
    backend_strs = args.backends.split(",")
    backends = []
    for i, bs in enumerate(backend_strs):
        bs = bs.strip()
        if bs:
            name = f"backend-{chr(65 + i)}"  # A, B, C, ...
            backends.append(Backend.from_string(bs, name))
    
    if not backends:
        log("EROARE: Trebuie specificat cel puțin un backend", "ERROR")
        return 1
    
    config = ProxyConfig(
        listen_host=args.listen_host,
        listen_port=args.listen_port,
        backends=backends,
        timeout=args.timeout,
    )
    
    proxy = ReverseProxy(config)
    proxy.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
