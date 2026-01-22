#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
 Săptămâna 2 – Exercițiul 1: Server/Client TCP Concurent
═══════════════════════════════════════════════════════════════════════════════

 OBIECTIVE DIDACTICE:
 ────────────────────
 1. Înțelegerea socket-urilor TCP (SOCK_STREAM)
 2. Diferența: server iterativ vs. server concurent (threading)
 3. Corelarea handshake TCP (SYN-SYN/ACK-ACK) cu codul
 4. Observarea încapsulării: date → segment TCP → pachet IP

 PROTOCOL APLICAȚIE:
 ──────────────────
 Request:  <mesaj text> (bytes)
 Response: b"OK: " + upper(mesaj)

 UTILIZARE:
   Server:  python3 ex_2_01_tcp.py server --port 9999
   Client:  python3 ex_2_01_tcp.py client --host 127.0.0.1 --port 9999 -m "test"
   Load:    python3 ex_2_01_tcp.py load --host 127.0.0.1 --port 9999 --clients 10
═══════════════════════════════════════════════════════════════════════════════
"""

from __future__ import annotations
import argparse
import socket
import sys
import threading
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List

# =============================================================================
# CONSTANTE
# =============================================================================
DEFAULT_PORT = 9999
DEFAULT_BIND = "0.0.0.0"
DEFAULT_BACKLOG = 32
DEFAULT_RECV_BUF = 1024
DEFAULT_TIMEOUT = 5.0


def timestamp() -> str:
    return datetime.now().strftime("%H:%M:%S.%f")[:-3]


def log(tag: str, msg: str) -> None:
    print(f"[{timestamp()}][{tag}] {msg}", flush=True)


@dataclass
class ServerConfig:
    bind: str = DEFAULT_BIND
    port: int = DEFAULT_PORT
    backlog: int = DEFAULT_BACKLOG
    recv_buf: int = DEFAULT_RECV_BUF
    mode: str = "threaded"


# =============================================================================
# HANDLER CLIENT
# =============================================================================
def handle_client(conn: socket.socket, addr: tuple[str, int], recv_buf: int) -> None:
    """
    Procesează conexiunea TCP de la client.
    
    Notă: recv_buf de 1024 e suficient pentru demo, dar în producție
    ai vrea să gestionezi mesaje mai mari cu un loop. Pentru curs, keep it simple.
    """
    client_ip, client_port = addr
    thread_name = threading.current_thread().name
    
    try:
        data = conn.recv(recv_buf)
        if not data:
            log(thread_name, f"{client_ip}:{client_port} deconectat")
            return
        
        # Strip \r\n pentru că netcat și alți clienți le adaugă
        data_clean = data.rstrip(b"\r\n")
        response = b"OK: " + data_clean.upper()
        
        log(thread_name, f"RX {len(data):4d}B de la {client_ip}:{client_port}: {data_clean!r}")
        conn.sendall(response)
        log(thread_name, f"TX {len(response):4d}B către {client_ip}:{client_port}: {response!r}")
        
    except Exception as exc:
        log(thread_name, f"EROARE {client_ip}:{client_port}: {exc}")
    finally:
        # Shutdown graceful - trimite FIN, nu doar taie conexiunea
        try:
            conn.shutdown(socket.SHUT_RDWR)
        except Exception:
            pass  # Ignoră dacă conexiunea e deja închisă
        conn.close()


# =============================================================================
# SERVER
# =============================================================================
def run_server(cfg: ServerConfig) -> None:
    """Pornește serverul TCP."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # HACK: SO_REUSEADDR pentru că altfel "Address already in use" 
    # ne face viața grea la demo-uri repetate. În producție, gândește-te
    # de două ori înainte să-l folosești.
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    sock.bind((cfg.bind, cfg.port))
    sock.listen(cfg.backlog)
    
    log("SERVER", f"TCP pe {cfg.bind}:{cfg.port} | mod={cfg.mode}")
    log("SERVER", "Așteptare conexiuni... (Ctrl+C oprire)")
    
    try:
        while True:
            conn, addr = sock.accept()
            log("MAIN", f"Conexiune nouă: {addr[0]}:{addr[1]}")
            
            if cfg.mode == "iterative":
                # Un client la un moment dat - simplu dar nu scalează
                handle_client(conn, addr, cfg.recv_buf)
            else:
                # Thread per conexiune - ok pentru demo, în producție
                # ai folosi thread pool sau asyncio
                t = threading.Thread(
                    target=handle_client,
                    args=(conn, addr, cfg.recv_buf),
                    daemon=True,
                    name=f"Worker-{addr[1]}"
                )
                t.start()
    except KeyboardInterrupt:
        log("SERVER", "Oprire (Ctrl+C)")
    finally:
        sock.close()


# =============================================================================
# CLIENT
# =============================================================================
def tcp_client(host: str, port: int, message: bytes, timeout: float) -> Optional[bytes]:
    """
    Client TCP simplu.
    
    Folosim context manager (with) ca să ne asigurăm că socket-ul
    se închide și dacă apare o excepție.
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            t0 = time.perf_counter()
            sock.connect((host, port))
            sock.sendall(message)
            response = sock.recv(4096)
            rtt = (time.perf_counter() - t0) * 1000
            log("CLIENT", f"RX {len(response)}B în {rtt:.1f}ms: {response!r}")
            return response
    except socket.timeout:
        log("CLIENT", f"TIMEOUT {host}:{port}")
    except ConnectionRefusedError:
        # Asta apare când serverul nu rulează sau portul e greșit
        log("CLIENT", f"Conexiune refuzată {host}:{port}")
    except Exception as exc:
        log("CLIENT", f"EROARE: {exc}")
    return None


def run_load_test(host: str, port: int, num_clients: int, message: bytes,
                  timeout: float, stagger_ms: int) -> None:
    """
    Test de încărcare cu N clienți concurenți.
    
    stagger_ms pune o pauză între pornirea clienților ca să nu
    lovim serverul cu toți deodată (deși uneori exact asta vrei să testezi).
    """
    log("LOAD", f"Start: {num_clients} clienți → {host}:{port}")
    
    results: List[Optional[bytes]] = [None] * num_clients
    
    def worker(i: int) -> None:
        results[i] = tcp_client(host, port, message, timeout)
    
    threads = []
    t0 = time.perf_counter()
    
    for i in range(num_clients):
        t = threading.Thread(target=worker, args=(i,))
        t.start()
        threads.append(t)
        if stagger_ms > 0:
            time.sleep(stagger_ms / 1000)
    
    for t in threads:
        t.join()
    
    duration = (time.perf_counter() - t0) * 1000
    ok = sum(1 for r in results if r)
    log("LOAD", f"Rezultat: {ok}/{num_clients} în {duration:.0f}ms")


# =============================================================================
# CLI
# =============================================================================
def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="S2 – Server/Client TCP")
    sub = p.add_subparsers(dest="cmd", required=True)
    
    # Server
    ps = sub.add_parser("server")
    ps.add_argument("--bind", default=DEFAULT_BIND)
    ps.add_argument("--port", type=int, default=DEFAULT_PORT)
    ps.add_argument("--backlog", type=int, default=DEFAULT_BACKLOG)
    ps.add_argument("--recv-buf", type=int, default=DEFAULT_RECV_BUF)
    ps.add_argument("--mode", choices=["threaded", "iterative"], default="threaded")
    
    # Client
    pc = sub.add_parser("client")
    pc.add_argument("--host", required=True)
    pc.add_argument("--port", type=int, required=True)
    pc.add_argument("--message", "-m", required=True)
    pc.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT)
    
    # Load
    pl = sub.add_parser("load")
    pl.add_argument("--host", required=True)
    pl.add_argument("--port", type=int, required=True)
    pl.add_argument("--clients", "-n", type=int, default=10)
    pl.add_argument("--message", "-m", default="ping")
    pl.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT)
    pl.add_argument("--stagger-ms", type=int, default=50)
    
    return p.parse_args()


def main() -> int:
    args = parse_args()
    
    if args.cmd == "server":
        run_server(ServerConfig(
            bind=args.bind, port=args.port, backlog=args.backlog,
            recv_buf=args.recv_buf, mode=args.mode
        ))
    elif args.cmd == "client":
        r = tcp_client(args.host, args.port, args.message.encode(), args.timeout)
        return 0 if r else 1
    elif args.cmd == "load":
        run_load_test(args.host, args.port, args.clients,
                      args.message.encode(), args.timeout, args.stagger_ms)
    return 0


if __name__ == "__main__":
    sys.exit(main())
