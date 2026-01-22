#!/usr/bin/env python3
"""
EXERCIȚIU 2: Completare Reverse Proxy
======================================
Disciplina: Rețele de Calculatoare, Săptămâna 8
Nivel: Avansat
Timp estimat: 30 minute

OBIECTIVE:
- Înțelegerea conceptului de reverse proxy
- Implementarea forward-ării cererilor
- Adăugarea headers de proxy (X-Forwarded-For, Via)
- Implementarea health check pentru backend-uri

INSTRUCȚIUNI:
1. Completați funcțiile marcate cu TODO
2. Rulați testele: python3 -m pytest tests/test_ex02.py -v
3. Testați manual:
   - Terminal 1: python3 demo_http_server.py --port 8081
   - Terminal 2: python3 demo_http_server.py --port 8082
   - Terminal 3: python3 ex02_reverse_proxy.py --port 8080 --backends localhost:8081,localhost:8082

EVALUARE:
- Forward corect: 30%
- Headers proxy: 30%
- Round Robin: 20%
- Health check: 20%

© Revolvix&Hypotheticalandrei
"""

import socket
import argparse
import threading
import time
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass

# ============================================================================
# CONSTANTE
# ============================================================================

CRLF = "\r\n"
DOUBLE_CRLF = "\r\n\r\n"
BUFFER_SIZE = 4096
CONNECT_TIMEOUT = 5.0
READ_TIMEOUT = 10.0


# ============================================================================
# STRUCTURI DE DATE
# ============================================================================

@dataclass
class Backend:
    """Reprezentarea unui backend server."""
    host: str
    port: int
    healthy: bool = True
    last_check: float = 0.0
    
    def __str__(self):
        status = "✓" if self.healthy else "✗"
        return f"{self.host}:{self.port} [{status}]"
    
    @property
    def address(self) -> Tuple[str, int]:
        return (self.host, self.port)


# ============================================================================
# TODO: IMPLEMENTAȚI ACEASTĂ CLASĂ
# ============================================================================

class RoundRobinBalancer:
    """
    Load balancer cu algoritm Round Robin.
    
    Funcționare:
    - Menține o listă de backend-uri
    - La fiecare apel next_backend(), returnează următorul backend sănătos
    - Ciclează prin backend-uri în ordine
    
    Thread Safety:
    - Trebuie să fie thread-safe (folosiți Lock)
    - Mai multe thread-uri pot apela next_backend() simultan
    
    Exemple:
        >>> backends = [Backend("localhost", 8081), Backend("localhost", 8082)]
        >>> balancer = RoundRobinBalancer(backends)
        >>> balancer.next_backend().port
        8081
        >>> balancer.next_backend().port
        8082
        >>> balancer.next_backend().port  # revine la primul
        8081
    """
    
    def __init__(self, backends: List[Backend]):
        """
        Inițializează balancer-ul cu lista de backend-uri.
        
        TODO: Implementați:
        - Stocare listă backend-uri
        - Index curent (începe de la 0)
        - Lock pentru thread safety
        """
        # TODO: Implementați inițializarea
        raise NotImplementedError("TODO: Implementați __init__")
    
    def next_backend(self) -> Optional[Backend]:
        """
        Returnează următorul backend sănătos.
        
        Returns:
            Backend-ul selectat sau None dacă niciunul nu e sănătos
        
        TODO: Implementați:
        1. Obțineți lock-ul
        2. Căutați primul backend healthy începând de la index curent
        3. Actualizați indexul pentru următorul apel
        4. Returnați backend-ul sau None
        
        HINT:
        - Folosiți with self.lock pentru thread safety
        - Parcurgeți circular (modulo len(backends))
        - Verificați maximum len(backends) backend-uri
        """
        # TODO: Implementați selecția round robin
        raise NotImplementedError("TODO: Implementați next_backend")
    
    def mark_unhealthy(self, backend: Backend):
        """
        Marchează un backend ca nesănătos.
        
        TODO: Setați backend.healthy = False
        """
        # TODO: Implementați
        raise NotImplementedError("TODO: Implementați mark_unhealthy")
    
    def mark_healthy(self, backend: Backend):
        """
        Marchează un backend ca sănătos.
        
        TODO: Setați backend.healthy = True
        """
        # TODO: Implementați
        raise NotImplementedError("TODO: Implementați mark_healthy")
    
    def get_stats(self) -> Dict[str, any]:
        """
        Returnează statistici despre backend-uri.
        
        Returns:
            Dict cu: total, healthy, unhealthy, backends
        """
        # TODO: Implementați statistici
        raise NotImplementedError("TODO: Implementați get_stats")


# ============================================================================
# TODO: IMPLEMENTAȚI ACEASTĂ FUNCȚIE
# ============================================================================

def add_proxy_headers(request_str: str, client_ip: str, proxy_name: str = "proxy") -> str:
    """
    Adaugă sau actualizează headers specifice proxy-ului.
    
    Args:
        request_str: Request-ul HTTP ca string
        client_ip: IP-ul clientului original
        proxy_name: Numele proxy-ului pentru header Via
    
    Returns:
        Request-ul modificat cu headers adăugate
    
    HEADERS DE ADĂUGAT:
    1. X-Forwarded-For: IP-ul clientului original
       - Dacă există deja, adăugați la sfârșitul listei: "ip1, ip2, ip3"
    2. X-Forwarded-Proto: "http" (presupunem HTTP)
    3. Via: "1.1 {proxy_name}" 
       - Dacă există deja, adăugați la sfârșitul listei
    
    Exemple:
        >>> req = "GET / HTTP/1.1\\r\\nHost: localhost\\r\\n\\r\\n"
        >>> modified = add_proxy_headers(req, "192.168.1.100", "myproxy")
        >>> "X-Forwarded-For: 192.168.1.100" in modified
        True
        >>> "Via: 1.1 myproxy" in modified
        True
    
    HINT:
    - Separați request line de headers
    - Parsați headers existente
    - Adăugați/actualizați headers necesare
    - Reconstruiți request-ul
    """
    
    # TODO: Implementați adăugarea headers
    #
    # Pași sugerați:
    # 1. Split pe DOUBLE_CRLF pentru a separa headers de body
    # 2. Split prima parte pe CRLF pentru a obține liniile
    # 3. Prima linie = request line (păstrați intact)
    # 4. Parsați restul ca headers în dicționar
    # 5. Actualizați/adăugați X-Forwarded-For, X-Forwarded-Proto, Via
    # 6. Reconstruiți request-ul
    
    raise NotImplementedError("TODO: Implementați add_proxy_headers")


# ============================================================================
# TODO: IMPLEMENTAȚI ACEASTĂ FUNCȚIE
# ============================================================================

def forward_request(request: bytes, backend: Backend, client_ip: str) -> Optional[bytes]:
    """
    Trimite request-ul către un backend și returnează răspunsul.
    
    Args:
        request: Request-ul HTTP original în bytes
        backend: Backend-ul țintă
        client_ip: IP-ul clientului original
    
    Returns:
        Răspunsul de la backend în bytes, sau None în caz de eroare
    
    PAȘI:
    1. Decodifică request-ul
    2. Modifică Host header pentru backend
    3. Adaugă headers proxy
    4. Deschide conexiune TCP către backend
    5. Trimite request-ul modificat
    6. Citește răspunsul complet
    7. Închide conexiunea
    8. Returnează răspunsul
    
    EDGE CASES:
    - Timeout la conectare
    - Eroare de rețea
    - Backend indisponibil
    
    HINT:
    - Folosiți socket.settimeout() pentru timeout
    - Cititi răspunsul în bucle până când recv returnează b""
    - Tratați excepțiile și returnați None la eroare
    """
    
    # TODO: Implementați forwarding-ul
    #
    # Pași sugerați:
    # 1. Decodifică request în string
    # 2. Modifică Host header (înlocuiți host original cu backend.host:backend.port)
    # 3. Adăugați headers proxy cu add_proxy_headers()
    # 4. Creați socket TCP
    # 5. Setați timeout
    # 6. Conectați la backend
    # 7. Trimiteți request-ul
    # 8. Citiți răspunsul (în bucle)
    # 9. Închideți socket-ul
    # 10. Returnați răspunsul
    
    raise NotImplementedError("TODO: Implementați forward_request")


# ============================================================================
# TODO: IMPLEMENTAȚI ACEASTĂ FUNCȚIE
# ============================================================================

def check_backend_health(backend: Backend) -> bool:
    """
    Verifică dacă un backend este sănătos (răspunde la cereri).
    
    Args:
        backend: Backend-ul de verificat
    
    Returns:
        True dacă backend-ul răspunde, False altfel
    
    METODĂ:
    - Trimite un request HEAD /
    - Dacă primește răspuns în timeout, e sănătos
    - Actualizează backend.last_check cu timestamp curent
    
    HINT:
    - Timeout scurt (2 secunde)
    - Nu contează conținutul răspunsului, doar că răspunde
    - Tratați toate excepțiile ca nesănătos
    """
    
    # TODO: Implementați health check
    #
    # Pași sugerați:
    # 1. Creați socket TCP
    # 2. Setați timeout scurt (2s)
    # 3. Încercați să vă conectați la backend
    # 4. Trimiteți "HEAD / HTTP/1.1\r\nHost: {host}\r\n\r\n"
    # 5. Încercați să citiți răspuns
    # 6. Actualizați backend.last_check = time.time()
    # 7. Returnați True/False
    
    raise NotImplementedError("TODO: Implementați check_backend_health")


# ============================================================================
# COD FURNIZAT - NU MODIFICAȚI
# ============================================================================

class ReverseProxy:
    """
    Reverse proxy server.
    Cod parțial furnizat - trebuie să implementați metodele TODO.
    """
    
    def __init__(self, host: str, port: int, backends: List[Backend]):
        self.host = host
        self.port = port
        self.balancer = RoundRobinBalancer(backends)
        self.running = False
        self.server_socket = None
        
        # Health check thread
        self.health_check_interval = 30  # secunde
        self.health_thread = None
    
    def start_health_checks(self):
        """Pornește thread-ul de health check."""
        def health_loop():
            while self.running:
                for backend in self.balancer.backends:
                    is_healthy = check_backend_health(backend)
                    if is_healthy:
                        self.balancer.mark_healthy(backend)
                    else:
                        self.balancer.mark_unhealthy(backend)
                    print(f"[HEALTH] {backend}")
                time.sleep(self.health_check_interval)
        
        self.health_thread = threading.Thread(target=health_loop, daemon=True)
        self.health_thread.start()
    
    def handle_client(self, client_socket: socket.socket, client_addr: Tuple[str, int]):
        """Procesează o conexiune client."""
        client_ip = client_addr[0]
        
        try:
            request = client_socket.recv(BUFFER_SIZE)
            if not request:
                return
            
            # Selectăm backend
            backend = self.balancer.next_backend()
            if not backend:
                error_response = (
                    b"HTTP/1.1 503 Service Unavailable\r\n"
                    b"Content-Type: text/plain\r\n"
                    b"Content-Length: 23\r\n\r\n"
                    b"No backends available"
                )
                client_socket.sendall(error_response)
                return
            
            print(f"[PROXY] {client_ip} -> {backend}")
            
            # Forward request
            response = forward_request(request, backend, client_ip)
            
            if response:
                client_socket.sendall(response)
            else:
                # Backend a eșuat
                self.balancer.mark_unhealthy(backend)
                error_response = (
                    b"HTTP/1.1 502 Bad Gateway\r\n"
                    b"Content-Type: text/plain\r\n"
                    b"Content-Length: 15\r\n\r\n"
                    b"Backend failed"
                )
                client_socket.sendall(error_response)
                
        except Exception as e:
            print(f"[EROARE] {e}")
        finally:
            client_socket.close()
    
    def run(self):
        """Pornește serverul proxy."""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(100)
            self.running = True
            
            print(f"[INFO] Reverse proxy pornit pe http://{self.host}:{self.port}/")
            print(f"[INFO] Backend-uri: {[str(b) for b in self.balancer.backends]}")
            print("[INFO] Apăsați Ctrl+C pentru oprire")
            
            # Pornește health checks
            self.start_health_checks()
            
            while self.running:
                try:
                    client_socket, client_addr = self.server_socket.accept()
                    # Handle în thread separat
                    thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, client_addr),
                        daemon=True
                    )
                    thread.start()
                except socket.error:
                    break
                    
        except KeyboardInterrupt:
            print("\n[INFO] Proxy oprit de utilizator")
        finally:
            self.running = False
            if self.server_socket:
                self.server_socket.close()


def parse_backends(backends_str: str) -> List[Backend]:
    """Parsează string-ul de backend-uri."""
    backends = []
    for backend_str in backends_str.split(","):
        host, port = backend_str.strip().split(":")
        backends.append(Backend(host=host, port=int(port)))
    return backends


def main():
    parser = argparse.ArgumentParser(description="Reverse Proxy")
    parser.add_argument("--host", default="0.0.0.0", help="Adresa de bind")
    parser.add_argument("--port", type=int, default=8080, help="Portul proxy")
    parser.add_argument(
        "--backends", 
        default="localhost:8081,localhost:8082",
        help="Lista de backend-uri (host:port,host:port,...)"
    )
    
    args = parser.parse_args()
    backends = parse_backends(args.backends)
    
    proxy = ReverseProxy(args.host, args.port, backends)
    proxy.run()


if __name__ == "__main__":
    main()
