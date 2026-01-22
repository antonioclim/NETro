#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
  simple_lb.py – Load Balancer Minimal în Python
═══════════════════════════════════════════════════════════════════════════════

SCOP DIDACTIC:
  - Demonstrare implementare load balancer de la zero
  - Înțelegerea algoritmului round-robin
  - Comparație cu soluții industriale (Nginx)

ATENȚIE:
  - Acest cod este didactic, NU pentru producție!
  - Lipsesc: health checks, retries, keep-alive, buffering, etc.

ARHITECTURA:
  Client ─► LB (acest script) ─► Backend 1/2/3

CONFIGURARE (environment variables):
  - BACKENDS: lista backend-uri (ex: "web1:80,web2:80,web3:80")
  - ALGO: algoritm (rr, random)
  - PORT: port de ascultare (default: 8080)

═══════════════════════════════════════════════════════════════════════════════
"""
import os
import socket
import threading
import random

# ─────────────────────────────────────────────────────────────────────────────
# Configurare
# ─────────────────────────────────────────────────────────────────────────────
BACKENDS_STR = os.environ.get("BACKENDS", "web1:80,web2:80,web3:80")
ALGO = os.environ.get("ALGO", "rr")
PORT = int(os.environ.get("PORT", "8080"))

# Parsare backend-uri
BACKENDS = []
for item in BACKENDS_STR.split(","):
    item = item.strip()
    if item:
        host, port = item.split(":")
        BACKENDS.append((host, int(port)))

# Index pentru round-robin
rr_index = 0
rr_lock = threading.Lock()

# ─────────────────────────────────────────────────────────────────────────────
# Algoritmi de selecție
# ─────────────────────────────────────────────────────────────────────────────
def pick_backend_rr():
    """Round-robin: selectează backend-urile pe rând."""
    global rr_index
    with rr_lock:
        backend = BACKENDS[rr_index]
        rr_index = (rr_index + 1) % len(BACKENDS)
    return backend


def pick_backend_random():
    """Random: selectează aleatoriu."""
    return random.choice(BACKENDS)


def pick_backend():
    """Selectează backend-ul conform algoritmului configurat."""
    if ALGO == "random":
        return pick_backend_random()
    return pick_backend_rr()

# ─────────────────────────────────────────────────────────────────────────────
# Proxy logic
# ─────────────────────────────────────────────────────────────────────────────
def forward_request(client_sock):
    """
    Forward cererea de la client către backend și răspunsul înapoi.
    
    Implementare simplificată:
    1. Citește cererea de la client
    2. Selectează backend
    3. Trimite cererea la backend
    4. Citește răspunsul și îl trimite înapoi la client
    """
    try:
        # 1. Citim cererea de la client
        request = b""
        client_sock.settimeout(5.0)
        while True:
            chunk = client_sock.recv(4096)
            if not chunk:
                return
            request += chunk
            if b"\r\n\r\n" in request:
                break
        
        # 2. Selectăm backend
        backend_host, backend_port = pick_backend()
        
        # 3. Conectăm la backend și trimitem cererea
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as backend_sock:
            backend_sock.settimeout(5.0)
            backend_sock.connect((backend_host, backend_port))
            backend_sock.sendall(request)
            
            # 4. Citim răspunsul și îl trimitem înapoi
            while True:
                response_chunk = backend_sock.recv(4096)
                if not response_chunk:
                    break
                client_sock.sendall(response_chunk)
    
    except Exception as e:
        # În caz de eroare, trimitem 502 Bad Gateway
        try:
            error_response = b"HTTP/1.1 502 Bad Gateway\r\nContent-Length: 11\r\n\r\nBad Gateway"
            client_sock.sendall(error_response)
        except:
            pass
    
    finally:
        try:
            client_sock.close()
        except:
            pass


def handle_client(client_sock):
    """Handler pentru thread-uri."""
    forward_request(client_sock)

# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────
def main():
    print(f"[LB] Pornire load balancer pe portul {PORT}")
    print(f"[LB] Algoritm: {ALGO}")
    print(f"[LB] Backend-uri: {BACKENDS}")
    print("")
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(("0.0.0.0", PORT))
        server.listen(128)
        
        print(f"[LB] Ascultare pe 0.0.0.0:{PORT}")
        
        while True:
            client_sock, addr = server.accept()
            thread = threading.Thread(target=handle_client, args=(client_sock,), daemon=True)
            thread.start()


if __name__ == "__main__":
    main()


# Revolvix&Hypotheticalandrei
