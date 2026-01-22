#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
  Exercițiul 11.01 – Server HTTP Backend Simplu
═══════════════════════════════════════════════════════════════════════════════

SCOP DIDACTIC:
  - Înțelegerea modelului request-response HTTP
  - Implementarea unui server HTTP minimal
  - Observarea comportamentului din perspectiva backend-ului

FUNCȚIONALITĂȚI:
  - Server HTTP simplu pe port configurabil
  - Răspunde cu ID-ul backend-ului (pentru a observa load balancing)
  - Suport pentru simulare delay (pentru teste least_conn)
  - Logging minimal pentru debugging

ARHITECTURA:
  ┌─────────────────────────────────────────────────────────────┐
  │  Client  ──────►  Load Balancer  ──────►  Backend (acest    │
  │                                          server)            │
  │          ◄──────                 ◄──────                    │
  └─────────────────────────────────────────────────────────────┘

RULARE:
  python3 ex_11_01_backend.py --id 1 --port 8001
  python3 ex_11_01_backend.py --id 2 --port 8002
  python3 ex_11_01_backend.py --id 3 --port 8003 --delay 0.5

TESTARE:
  curl http://localhost:8001/
  # Response: Backend 1 | Host: hostname | Time: 2025-01-01T12:00:00

═══════════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations

import argparse
import socket
import threading
import time
import os
from datetime import datetime


def get_hostname() -> str:
    """Obține hostname-ul sau un fallback."""
    try:
        return socket.gethostname()
    except Exception:
        return "unknown"


def build_response(backend_id: int, request_count: int) -> bytes:
    """
    Construiește răspunsul HTTP.
    
    Formatul răspunsului include:
    - ID-ul backend-ului (pentru verificare load balancing)
    - Hostname-ul containerului/mașinii
    - Timestamp-ul curent
    - Numărul cererii procesate
    """
    hostname = get_hostname()
    timestamp = datetime.now().isoformat(timespec='seconds')
    
    body = f"Backend {backend_id} | Host: {hostname} | Time: {timestamp} | Request #{request_count}\n"
    body_bytes = body.encode("utf-8")
    
    response = (
        b"HTTP/1.1 200 OK\r\n"
        b"Content-Type: text/plain; charset=utf-8\r\n"
        b"Connection: close\r\n"
        b"X-Backend-ID: " + str(backend_id).encode() + b"\r\n"
        b"Content-Length: " + str(len(body_bytes)).encode() + b"\r\n"
        b"\r\n"
    ) + body_bytes
    
    return response


def handle_client(client_sock: socket.socket, 
                  client_addr: tuple,
                  backend_id: int,
                  delay: float,
                  request_counter: list,
                  verbose: bool) -> None:
    """
    Procesează o cerere HTTP.
    
    Args:
        client_sock: Socket-ul clientului
        client_addr: Adresa clientului (ip, port)
        backend_id: ID-ul acestui backend
        delay: Delay artificial în secunde (pentru teste)
        request_counter: Lista cu contor (pentru thread-safety)
        verbose: Dacă să afișeze logging
    """
    try:
        # Citim cererea (simplificat - doar headers)
        request = b""
        client_sock.settimeout(5.0)
        
        while True:
            chunk = client_sock.recv(4096)
            if not chunk:
                break
            request += chunk
            if b"\r\n\r\n" in request:
                break
        
        # Incrementăm contorul thread-safe
        with threading.Lock():
            request_counter[0] += 1
            count = request_counter[0]
        
        # Simulăm delay dacă e configurat
        if delay > 0:
            time.sleep(delay)
        
        # Construim și trimitem răspunsul
        response = build_response(backend_id, count)
        client_sock.sendall(response)
        
        if verbose:
            method = request.split(b" ", 1)[0].decode("ascii", errors="replace")
            print(f"[Backend {backend_id}] {client_addr[0]}:{client_addr[1]} - {method} - #{count}")
    
    except Exception as e:
        if verbose:
            print(f"[Backend {backend_id}] Error: {e}")
    
    finally:
        try:
            client_sock.close()
        except Exception:
            pass


def run_server(backend_id: int, 
               host: str, 
               port: int, 
               delay: float,
               verbose: bool) -> None:
    """
    Pornește serverul HTTP.
    
    Args:
        backend_id: ID-ul unic al acestui backend
        host: Adresa de bind (0.0.0.0 pentru toate interfețele)
        port: Portul de ascultare
        delay: Delay artificial per request (secunde)
        verbose: Logging detaliat
    """
    request_counter = [0]  # Lista pentru thread-safety
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind((host, port))
        server_sock.listen(128)
        
        print(f"[Backend {backend_id}] Listening on {host}:{port}")
        if delay > 0:
            print(f"[Backend {backend_id}] Delay per request: {delay}s")
        print(f"[Backend {backend_id}] Press Ctrl+C to stop")
        print("")
        
        try:
            while True:
                client_sock, client_addr = server_sock.accept()
                thread = threading.Thread(
                    target=handle_client,
                    args=(client_sock, client_addr, backend_id, delay, request_counter, verbose),
                    daemon=True
                )
                thread.start()
        
        except KeyboardInterrupt:
            print(f"\n[Backend {backend_id}] Shutting down...")
            print(f"[Backend {backend_id}] Total requests served: {request_counter[0]}")


def main():
    parser = argparse.ArgumentParser(
        description="Server HTTP backend simplu pentru demonstrații load balancing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemple:
  %(prog)s --id 1 --port 8001
  %(prog)s --id 2 --port 8002 --delay 0.2
  %(prog)s --id 3 --port 8003 -v
        """
    )
    
    parser.add_argument("--id", type=int, default=1,
                        help="ID-ul backend-ului (default: 1)")
    parser.add_argument("--host", type=str, default="0.0.0.0",
                        help="Adresa de bind (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8001,
                        help="Portul de ascultare (default: 8001)")
    parser.add_argument("--delay", type=float, default=0.0,
                        help="Delay artificial per request în secunde (default: 0)")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Logging detaliat")
    
    args = parser.parse_args()
    
    run_server(
        backend_id=args.id,
        host=args.host,
        port=args.port,
        delay=args.delay,
        verbose=args.verbose
    )


if __name__ == "__main__":
    main()


# Revolvix&Hypotheticalandrei
