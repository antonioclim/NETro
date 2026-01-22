#!/usr/bin/env python3
"""
EXERCIȚIU 4: Rate Limiting
===========================
Disciplina: Rețele de Calculatoare, Săptămâna 8
Nivel: Intermediar
Timp estimat: 20 minute

OBIECTIVE:
- Înțelegerea conceptului de rate limiting
- Implementarea unui algoritm de limitare cereri
- Protecția serverului împotriva abuzurilor
- Returnarea codului 429 Too Many Requests

INSTRUCȚIUNI:
1. Completați funcțiile marcate cu TODO
2. Rulați testele: python3 -m pytest tests/test_ex04.py -v
3. Testați manual:
   for i in {1..15}; do curl -w "%{http_code}\\n" http://localhost:8081/; done

EVALUARE:
- Algoritm corect: 40%
- Thread safety: 30%
- Response 429: 20%
- Cleanup expired: 10%

© Revolvix&Hypotheticalandrei
"""

import socket
import time
import threading
import argparse
from typing import Dict, List, Tuple
from collections import defaultdict
from dataclasses import dataclass, field

# ============================================================================
# CONSTANTE
# ============================================================================

DEFAULT_MAX_REQUESTS = 10  # cereri permise
DEFAULT_WINDOW_SECONDS = 60  # în această fereastră de timp
CLEANUP_INTERVAL = 60  # cât de des curățăm timestamp-uri expirate


# ============================================================================
# TODO: IMPLEMENTAȚI ACEASTĂ CLASĂ
# ============================================================================

@dataclass
class RateLimiter:
    """
    Rate limiter folosind algoritm sliding window.
    
    Funcționare:
    - Pentru fiecare IP, menține o listă de timestamp-uri ale cererilor
    - La fiecare cerere nouă:
      1. Elimină timestamp-urile mai vechi decât window_seconds
      2. Verifică dacă numărul de cereri e sub max_requests
      3. Dacă da, adaugă timestamp-ul curent și permite cererea
      4. Dacă nu, refuză cererea (429)
    
    Thread Safety:
    - Mai multe thread-uri pot apela check() simultan
    - Folosiți Lock pentru sincronizare
    
    Exemple:
        >>> limiter = RateLimiter(max_requests=2, window_seconds=60)
        >>> limiter.check("192.168.1.1")
        True
        >>> limiter.check("192.168.1.1")
        True
        >>> limiter.check("192.168.1.1")  # a treia cerere în aceeași secundă
        False
    """
    
    max_requests: int = DEFAULT_MAX_REQUESTS
    window_seconds: int = DEFAULT_WINDOW_SECONDS
    
    # TODO: Adăugați câmpurile necesare:
    # - requests: Dict[str, List[float]] - IP -> listă timestamp-uri
    # - lock: threading.Lock() - pentru thread safety
    
    def __post_init__(self):
        """Inițializare după crearea dataclass-ului."""
        # TODO: Inițializați:
        # - self.requests = defaultdict(list)
        # - self.lock = threading.Lock()
        raise NotImplementedError("TODO: Implementați __post_init__")
    
    def check(self, client_ip: str) -> bool:
        """
        Verifică dacă clientul poate face o cerere nouă.
        
        Args:
            client_ip: Adresa IP a clientului
        
        Returns:
            True dacă cererea e permisă, False dacă limita e depășită
        
        ALGORITM (sliding window):
        1. Obține timestamp curent
        2. Cu lock ținut:
           a. Elimină timestamp-uri expirate (mai vechi decât window_seconds)
           b. Numără cererile rămase
           c. Dacă < max_requests: adaugă timestamp curent, return True
           d. Altfel: return False
        
        HINT:
        - Folosiți time.time() pentru timestamp
        - cutoff = now - window_seconds
        - Păstrați doar timestamp-urile > cutoff
        """
        
        # TODO: Implementați verificarea rate limit
        raise NotImplementedError("TODO: Implementați check")
    
    def get_remaining(self, client_ip: str) -> int:
        """
        Returnează câte cereri mai poate face clientul.
        
        Returns:
            Numărul de cereri rămase în fereastra curentă
        """
        
        # TODO: Implementați calculul cererilor rămase
        raise NotImplementedError("TODO: Implementați get_remaining")
    
    def get_reset_time(self, client_ip: str) -> float:
        """
        Returnează câte secunde până se resetează limita.
        
        Returns:
            Secundele până când cea mai veche cerere expiră
        """
        
        # TODO: Implementați calculul timpului de reset
        raise NotImplementedError("TODO: Implementați get_reset_time")
    
    def cleanup_expired(self):
        """
        Curăță toate timestamp-urile expirate din toate IP-urile.
        Apelată periodic de un thread de cleanup.
        """
        
        # TODO: Implementați curățarea
        #
        # Pași:
        # 1. Cu lock ținut
        # 2. Pentru fiecare IP
        # 3. Elimină timestamp-uri expirate
        # 4. Dacă lista e goală, șterge IP-ul din dicționar
        
        raise NotImplementedError("TODO: Implementați cleanup_expired")
    
    def get_stats(self) -> Dict[str, any]:
        """
        Returnează statistici despre rate limiter.
        
        Returns:
            Dict cu: total_ips, total_requests, config
        """
        
        # TODO: Implementați statistici
        raise NotImplementedError("TODO: Implementați get_stats")


# ============================================================================
# TODO: IMPLEMENTAȚI ACEASTĂ FUNCȚIE
# ============================================================================

def build_rate_limit_response(limiter: RateLimiter, client_ip: str) -> bytes:
    """
    Construiește răspunsul 429 Too Many Requests.
    
    Args:
        limiter: Instanța RateLimiter
        client_ip: IP-ul clientului
    
    Returns:
        Răspunsul HTTP 429 în bytes
    
    HEADERS SPECIALE:
    - Retry-After: numărul de secunde până la reset
    - X-RateLimit-Limit: limita maximă
    - X-RateLimit-Remaining: cereri rămase (0)
    - X-RateLimit-Reset: timestamp Unix când se resetează
    
    BODY:
        {
            "error": "Too Many Requests",
            "message": "Rate limit exceeded. Try again in X seconds.",
            "retry_after": X
        }
    """
    
    # TODO: Implementați răspunsul 429
    #
    # Pași:
    # 1. Calculați retry_after cu limiter.get_reset_time()
    # 2. Construiți body JSON
    # 3. Adăugați headers speciale pentru rate limiting
    # 4. Construiți și returnați răspunsul HTTP complet
    
    raise NotImplementedError("TODO: Implementați build_rate_limit_response")


# ============================================================================
# TODO: IMPLEMENTAȚI ACEASTĂ FUNCȚIE
# ============================================================================

def add_rate_limit_headers(response: bytes, limiter: RateLimiter, client_ip: str) -> bytes:
    """
    Adaugă headers de rate limit la un răspuns existent.
    
    Args:
        response: Răspunsul HTTP original
        limiter: Instanța RateLimiter  
        client_ip: IP-ul clientului
    
    Returns:
        Răspunsul modificat cu headers adăugate
    
    HEADERS DE ADĂUGAT:
    - X-RateLimit-Limit: limita maximă
    - X-RateLimit-Remaining: cereri rămase
    - X-RateLimit-Reset: timestamp când se resetează
    
    HINT:
    - Găsiți poziția lui \\r\\n\\r\\n în response
    - Inserați headers înainte de \\r\\n\\r\\n final
    """
    
    # TODO: Implementați adăugarea headers
    raise NotImplementedError("TODO: Implementați add_rate_limit_headers")


# ============================================================================
# COD FURNIZAT - SERVER CU RATE LIMITING
# ============================================================================

def simple_response(status_code: int, body: str) -> bytes:
    """Construiește un răspuns HTTP simplu."""
    status_text = {200: "OK", 404: "Not Found", 429: "Too Many Requests"}
    body_bytes = body.encode('utf-8')
    response = (
        f"HTTP/1.1 {status_code} {status_text.get(status_code, 'Unknown')}\r\n"
        f"Content-Type: text/plain\r\n"
        f"Content-Length: {len(body_bytes)}\r\n"
        f"\r\n"
    ).encode('utf-8') + body_bytes
    return response


def run_server(host: str, port: int, max_requests: int, window_seconds: int):
    """Pornește serverul cu rate limiting."""
    limiter = RateLimiter(max_requests=max_requests, window_seconds=window_seconds)
    
    # Thread pentru cleanup periodic
    def cleanup_loop():
        while True:
            time.sleep(CLEANUP_INTERVAL)
            limiter.cleanup_expired()
            print(f"[CLEANUP] Stats: {limiter.get_stats()}")
    
    cleanup_thread = threading.Thread(target=cleanup_loop, daemon=True)
    cleanup_thread.start()
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server.bind((host, port))
        server.listen(5)
        print(f"[INFO] Server cu rate limiting pornit pe http://{host}:{port}/")
        print(f"[INFO] Limită: {max_requests} cereri / {window_seconds} secunde")
        print("[INFO] Apăsați Ctrl+C pentru oprire")
        
        while True:
            client, addr = server.accept()
            client_ip = addr[0]
            
            try:
                # Citim request (simplificat)
                request = client.recv(4096)
                if not request:
                    continue
                
                # Verificăm rate limit
                if not limiter.check(client_ip):
                    print(f"[RATE] {client_ip} - BLOCKED")
                    response = build_rate_limit_response(limiter, client_ip)
                    client.sendall(response)
                else:
                    remaining = limiter.get_remaining(client_ip)
                    print(f"[OK] {client_ip} - {remaining} cereri rămase")
                    
                    # Răspuns normal
                    response = simple_response(200, f"Hello! You have {remaining} requests remaining.")
                    response = add_rate_limit_headers(response, limiter, client_ip)
                    client.sendall(response)
                    
            except Exception as e:
                print(f"[ERROR] {e}")
            finally:
                client.close()
                
    except KeyboardInterrupt:
        print("\n[INFO] Server oprit")
    finally:
        server.close()


def main():
    parser = argparse.ArgumentParser(description="Server HTTP cu Rate Limiting")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8081)
    parser.add_argument("--max-requests", type=int, default=10, help="Cereri permise")
    parser.add_argument("--window", type=int, default=60, help="Fereastră în secunde")
    
    args = parser.parse_args()
    run_server(args.host, args.port, args.max_requests, args.window)


if __name__ == "__main__":
    main()
