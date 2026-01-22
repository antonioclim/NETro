#!/usr/bin/env python3
"""
EXERCIȚIU CHALLENGE: Caching Proxy
===================================
Disciplina: Rețele de Calculatoare, Săptămâna 8
Nivel: Expert
Timp estimat: 45 minute

OBIECTIVE:
- Implementarea unui cache HTTP în reverse proxy
- Înțelegerea headers de cache (Cache-Control, ETag, Last-Modified)
- Optimizarea performanței prin reducerea încărcării backend-ului
- Implementarea statisticilor și managementului cache-ului

INSTRUCȚIUNI:
1. Completați funcțiile marcate cu TODO
2. Testați cu multiple cereri repetate
3. Verificați hit rate cu /cache/stats

EVALUARE:
- Cache storage: 20%
- TTL și expirare: 20%
- Cache-Control parsing: 20%
- Statistics: 20%
- Invalidare: 20%

© Revolvix&Hypotheticalandrei
"""

import socket
import time
import threading
import json
import hashlib
import argparse
from typing import Dict, Optional, Tuple, Any
from dataclasses import dataclass, field
from collections import OrderedDict

# ============================================================================
# CONSTANTE
# ============================================================================

DEFAULT_TTL = 300  # 5 minute
MAX_CACHE_SIZE = 100  # număr maxim de entries
MAX_ENTRY_SIZE = 1024 * 1024  # 1 MB per entry


# ============================================================================
# STRUCTURI DE DATE
# ============================================================================

@dataclass
class CacheEntry:
    """O intrare în cache."""
    response: bytes           # Răspunsul HTTP complet
    created_at: float         # Timestamp creare
    expires_at: float         # Timestamp expirare
    etag: Optional[str] = None          # ETag pentru validare
    last_modified: Optional[str] = None  # Last-Modified pentru validare
    hit_count: int = 0        # Număr de hit-uri
    
    def is_expired(self) -> bool:
        """Verifică dacă entry-ul a expirat."""
        return time.time() > self.expires_at
    
    def remaining_ttl(self) -> int:
        """Returnează TTL-ul rămas în secunde."""
        return max(0, int(self.expires_at - time.time()))


# ============================================================================
# TODO: IMPLEMENTAȚI ACEASTĂ CLASĂ
# ============================================================================

class HTTPCache:
    """
    Cache HTTP pentru răspunsuri.
    
    Funcționalități:
    - Stocare răspunsuri cu TTL
    - Cheie de cache: METHOD + URL (hash)
    - Respectare Cache-Control headers
    - LRU eviction când cache-ul e plin
    - Thread-safe
    
    Exemple:
        >>> cache = HTTPCache(default_ttl=60)
        >>> cache.set("GET /index.html", response_bytes, ttl=120)
        >>> entry = cache.get("GET /index.html")
        >>> entry.response
        b'HTTP/1.1 200 OK...'
    """
    
    def __init__(self, default_ttl: int = DEFAULT_TTL, max_size: int = MAX_CACHE_SIZE):
        """
        Inițializează cache-ul.
        
        TODO: Inițializați:
        - self.default_ttl = default_ttl
        - self.max_size = max_size
        - self.cache = OrderedDict() - pentru LRU
        - self.lock = threading.Lock()
        - self.stats = {"hits": 0, "misses": 0, "evictions": 0}
        """
        raise NotImplementedError("TODO: Implementați __init__")
    
    def _generate_key(self, method: str, url: str) -> str:
        """
        Generează cheia de cache din method și URL.
        
        HINT: Folosiți hash pentru a evita chei lungi
        """
        
        # TODO: Implementați generarea cheii
        # Exemplu: md5 hash al "GET /index.html"
        raise NotImplementedError("TODO: Implementați _generate_key")
    
    def get(self, method: str, url: str) -> Optional[CacheEntry]:
        """
        Obține o intrare din cache.
        
        Args:
            method: Metoda HTTP (GET)
            url: URL-ul cererii
        
        Returns:
            CacheEntry dacă există și nu a expirat, None altfel
        
        COMPORTAMENT:
        1. Generează cheia
        2. Cu lock ținut:
           a. Verifică dacă cheia există
           b. Verifică dacă entry-ul nu a expirat
           c. Actualizează hit_count
           d. Mută entry-ul la sfârșitul OrderedDict (LRU)
           e. Actualizează stats["hits"] sau stats["misses"]
        """
        
        # TODO: Implementați get
        raise NotImplementedError("TODO: Implementați get")
    
    def set(self, method: str, url: str, response: bytes, 
            ttl: Optional[int] = None, etag: Optional[str] = None,
            last_modified: Optional[str] = None):
        """
        Adaugă o intrare în cache.
        
        Args:
            method: Metoda HTTP
            url: URL-ul cererii
            response: Răspunsul HTTP complet
            ttl: Time-to-live în secunde (None = folosește default)
            etag: ETag pentru validare
            last_modified: Last-Modified pentru validare
        
        COMPORTAMENT:
        1. Verifică dacă răspunsul e prea mare (> MAX_ENTRY_SIZE)
        2. Generează cheia
        3. Cu lock ținut:
           a. Dacă cache-ul e plin, evict (LRU)
           b. Creează CacheEntry
           c. Adaugă în cache
        """
        
        # TODO: Implementați set
        raise NotImplementedError("TODO: Implementați set")
    
    def delete(self, method: str, url: str) -> bool:
        """
        Șterge o intrare din cache.
        
        Returns:
            True dacă a fost șters, False dacă nu exista
        """
        
        # TODO: Implementați delete
        raise NotImplementedError("TODO: Implementați delete")
    
    def clear(self):
        """Golește tot cache-ul."""
        
        # TODO: Implementați clear
        raise NotImplementedError("TODO: Implementați clear")
    
    def _evict_lru(self):
        """
        Elimină cea mai veche intrare (LRU - Least Recently Used).
        
        HINT: OrderedDict.popitem(last=False) elimină primul element
        """
        
        # TODO: Implementați eviction
        raise NotImplementedError("TODO: Implementați _evict_lru")
    
    def cleanup_expired(self) -> int:
        """
        Elimină toate intrările expirate.
        
        Returns:
            Numărul de intrări eliminate
        """
        
        # TODO: Implementați cleanup
        raise NotImplementedError("TODO: Implementați cleanup_expired")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Returnează statistici despre cache.
        
        Returns:
            Dict cu: hits, misses, hit_rate, size, entries
        """
        
        # TODO: Implementați statistici
        # hit_rate = hits / (hits + misses) dacă total > 0
        raise NotImplementedError("TODO: Implementați get_stats")


# ============================================================================
# TODO: IMPLEMENTAȚI ACEASTĂ FUNCȚIE
# ============================================================================

def parse_cache_control(headers: Dict[str, str]) -> Dict[str, Any]:
    """
    Parsează headerul Cache-Control.
    
    Args:
        headers: Dicționar cu headers HTTP
    
    Returns:
        Dict cu directive parsate
    
    FORMAT INPUT:
        Cache-Control: max-age=3600, public, no-transform
    
    FORMAT OUTPUT:
        {
            "max-age": 3600,
            "public": True,
            "no-transform": True,
            "no-cache": False,
            "no-store": False,
            "private": False
        }
    
    DIRECTIVE IMPORTANTE:
    - max-age=N: TTL în secunde
    - no-cache: trebuie revalidat mereu
    - no-store: NU se pune în cache
    - private: doar cache client, nu proxy
    - public: poate fi cached de oricine
    """
    
    # TODO: Implementați parsarea Cache-Control
    #
    # Pași:
    # 1. Obțineți valoarea header-ului "cache-control"
    # 2. Split pe ","
    # 3. Pentru fiecare directivă:
    #    - Dacă conține "=", parsați key=value
    #    - Altfel, e un flag (setați True)
    # 4. Returnați dicționarul
    
    raise NotImplementedError("TODO: Implementați parse_cache_control")


# ============================================================================
# TODO: IMPLEMENTAȚI ACEASTĂ FUNCȚIE
# ============================================================================

def is_cacheable(method: str, status_code: int, 
                 request_headers: Dict[str, str],
                 response_headers: Dict[str, str]) -> Tuple[bool, Optional[int]]:
    """
    Determină dacă un răspuns poate fi pus în cache.
    
    Args:
        method: Metoda HTTP (doar GET e cacheable)
        status_code: Codul de status (doar 200, 301 sunt cacheable)
        request_headers: Headers din request
        response_headers: Headers din response
    
    Returns:
        Tuple (is_cacheable, ttl_seconds)
        - is_cacheable: True dacă se poate pune în cache
        - ttl_seconds: TTL-ul calculat sau None pentru default
    
    REGULI:
    1. Doar GET e cacheable
    2. Doar status codes: 200, 203, 204, 206, 300, 301, 404, 405, 410, 414, 501
    3. no-store în request SAU response → NOT cacheable
    4. private în response → NOT cacheable (pentru proxy)
    5. max-age în response → folosește ca TTL
    6. Expires header → calculează TTL
    """
    
    # TODO: Implementați logica de cacheability
    raise NotImplementedError("TODO: Implementați is_cacheable")


# ============================================================================
# TODO: IMPLEMENTAȚI ACEASTĂ FUNCȚIE
# ============================================================================

def extract_etag_last_modified(response: bytes) -> Tuple[Optional[str], Optional[str]]:
    """
    Extrage ETag și Last-Modified din răspuns.
    
    Args:
        response: Răspunsul HTTP complet
    
    Returns:
        Tuple (etag, last_modified)
    
    HINT:
    - Parsați headers din răspuns
    - Căutați header-ele ETag și Last-Modified
    """
    
    # TODO: Implementați extragerea
    raise NotImplementedError("TODO: Implementați extract_etag_last_modified")


# ============================================================================
# COD FURNIZAT - CACHING PROXY SERVER
# ============================================================================

class CachingProxy:
    """Reverse proxy cu caching."""
    
    def __init__(self, host: str, port: int, backend_host: str, backend_port: int,
                 cache_ttl: int = DEFAULT_TTL):
        self.host = host
        self.port = port
        self.backend = (backend_host, backend_port)
        self.cache = HTTPCache(default_ttl=cache_ttl)
        self.running = False
    
    def forward_to_backend(self, request: bytes) -> Optional[bytes]:
        """Forward request către backend."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            sock.connect(self.backend)
            sock.sendall(request)
            
            response = b""
            while True:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                response += chunk
            
            sock.close()
            return response
        except Exception as e:
            print(f"[ERROR] Backend error: {e}")
            return None
    
    def handle_cache_stats(self) -> bytes:
        """Handler pentru /cache/stats."""
        stats = self.cache.get_stats()
        body = json.dumps(stats, indent=2).encode('utf-8')
        return (
            b"HTTP/1.1 200 OK\r\n"
            b"Content-Type: application/json\r\n" +
            b"Content-Length: " + str(len(body)).encode() + b"\r\n" +
            b"\r\n" + body
        )
    
    def handle_cache_clear(self) -> bytes:
        """Handler pentru /cache/clear."""
        self.cache.clear()
        return (
            b"HTTP/1.1 200 OK\r\n"
            b"Content-Type: text/plain\r\n"
            b"Content-Length: 14\r\n\r\n"
            b"Cache cleared!"
        )
    
    def handle_client(self, client: socket.socket, addr: Tuple[str, int]):
        """Procesează un client."""
        try:
            request = client.recv(4096)
            if not request:
                return
            
            # Parse request line
            first_line = request.split(b"\r\n")[0].decode()
            parts = first_line.split(" ")
            method, path = parts[0], parts[1]
            
            # Handle cache management endpoints
            if path == "/cache/stats":
                client.sendall(self.handle_cache_stats())
                return
            if path == "/cache/clear":
                client.sendall(self.handle_cache_clear())
                return
            
            # Check cache pentru GET
            if method == "GET":
                entry = self.cache.get(method, path)
                if entry:
                    print(f"[CACHE HIT] {method} {path}")
                    # Adaugă header X-Cache: HIT
                    response = entry.response
                    # Insert X-Cache header
                    idx = response.find(b"\r\n")
                    modified = response[:idx] + b"\r\nX-Cache: HIT" + response[idx:]
                    client.sendall(modified)
                    return
            
            print(f"[CACHE MISS] {method} {path}")
            
            # Forward to backend
            response = self.forward_to_backend(request)
            if not response:
                error = (
                    b"HTTP/1.1 502 Bad Gateway\r\n"
                    b"Content-Length: 11\r\n\r\n"
                    b"Bad Gateway"
                )
                client.sendall(error)
                return
            
            # Cache response if cacheable
            # Parse status code
            status_line = response.split(b"\r\n")[0].decode()
            status_code = int(status_line.split(" ")[1])
            
            # Parse headers
            headers_end = response.find(b"\r\n\r\n")
            headers_str = response[:headers_end].decode()
            headers = {}
            for line in headers_str.split("\r\n")[1:]:
                if ":" in line:
                    k, v = line.split(":", 1)
                    headers[k.strip().lower()] = v.strip()
            
            cacheable, ttl = is_cacheable(method, status_code, {}, headers)
            if cacheable:
                etag, last_mod = extract_etag_last_modified(response)
                self.cache.set(method, path, response, ttl=ttl, 
                              etag=etag, last_modified=last_mod)
                print(f"[CACHED] {method} {path} (TTL={ttl or 'default'})")
            
            # Add X-Cache: MISS header
            idx = response.find(b"\r\n")
            response = response[:idx] + b"\r\nX-Cache: MISS" + response[idx:]
            
            client.sendall(response)
            
        except Exception as e:
            print(f"[ERROR] {e}")
        finally:
            client.close()
    
    def run(self):
        """Pornește proxy-ul."""
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # Cleanup thread
        def cleanup_loop():
            while self.running:
                time.sleep(60)
                removed = self.cache.cleanup_expired()
                if removed > 0:
                    print(f"[CLEANUP] Removed {removed} expired entries")
        
        try:
            server.bind((self.host, self.port))
            server.listen(100)
            self.running = True
            
            cleanup_thread = threading.Thread(target=cleanup_loop, daemon=True)
            cleanup_thread.start()
            
            print(f"[INFO] Caching proxy pe http://{self.host}:{self.port}/")
            print(f"[INFO] Backend: {self.backend[0]}:{self.backend[1]}")
            print(f"[INFO] Endpoints: /cache/stats, /cache/clear")
            
            while self.running:
                client, addr = server.accept()
                thread = threading.Thread(
                    target=self.handle_client,
                    args=(client, addr),
                    daemon=True
                )
                thread.start()
                
        except KeyboardInterrupt:
            print("\n[INFO] Proxy oprit")
        finally:
            self.running = False
            server.close()


def main():
    parser = argparse.ArgumentParser(description="Caching Reverse Proxy")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--backend-host", default="localhost")
    parser.add_argument("--backend-port", type=int, default=8081)
    parser.add_argument("--cache-ttl", type=int, default=300)
    
    args = parser.parse_args()
    proxy = CachingProxy(
        args.host, args.port,
        args.backend_host, args.backend_port,
        args.cache_ttl
    )
    proxy.run()


if __name__ == "__main__":
    main()
