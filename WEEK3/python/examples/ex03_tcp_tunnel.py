#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  Exercițiul 3: TCP Tunnel (Port Forwarder)                                   ║
║  Săptămâna 3 — Rețele de Calculatoare                                        ║
╚══════════════════════════════════════════════════════════════════════════════╝

SCOPUL DIDACTIC:
    - Înțelegerea conceptului de proxy/tunnel TCP
    - Forwarding bidirecțional între două conexiuni TCP
    - Utilizarea thread-urilor pentru comunicare full-duplex
    - Aplicații practice: NAT traversal, load balancing, debugging

ARHITECTURĂ:
    ┌──────────┐     ┌──────────────────────────────┐     ┌──────────┐
    │  Client  │────►│         TUNNEL               │────►│  Server  │
    │   (a1)   │     │  accept() ─► connect(target) │     │   (b1)   │
    │          │◄────│  ◄── forward bidirecțional ──►│◄────│          │
    └──────────┘     └──────────────────────────────┘     └──────────┘
    
    Client se conectează la tunnel (ex: r1:9090)
    Tunnel deschide conexiune către server țintă (ex: b1:8080)
    Tunnel copiază date în ambele direcții

PATTERN FORWARDING:
    Thread 1: client_socket → target_socket
    Thread 2: target_socket → client_socket
    
    Ambele thread-uri rulează în paralel pentru comunicare full-duplex.

UTILIZĂRI PRACTICE:
    1. NAT traversal: expune un serviciu din rețea privată
    2. Load balancing simplu: distribuie conexiuni
    3. Debugging: interceptează trafic pentru analiză
    4. Protocol translation: adaptează între protocoale

RULARE (în Mininet topologie extinsă):
    # Server echo pe b1:
    python3 ex04_echo_server.py --listen 0.0.0.0:8080

    # Tunnel pe r1 (router):
    python3 ex03_tcp_tunnel.py --listen 0.0.0.0:9090 --target 10.0.2.1:8080

    # Client din a1:
    echo "hello" | nc 10.0.1.254 9090 -w 2
"""
from __future__ import annotations

import argparse
import socket
import sys
import threading
from datetime import datetime
from typing import Tuple


# ════════════════════════════════════════════════════════════════════════════
#  CONSTANTE
# ════════════════════════════════════════════════════════════════════════════

BUFFER_SIZE = 4096
DEFAULT_LISTEN = "0.0.0.0:9090"
DEFAULT_TARGET = "127.0.0.1:8080"


# ════════════════════════════════════════════════════════════════════════════
#  FUNCȚII UTILITARE
# ════════════════════════════════════════════════════════════════════════════

def timestamp() -> str:
    return datetime.now().strftime("%H:%M:%S.%f")[:-3]


def log(level: str, tunnel_id: str, message: str) -> None:
    print(f"[{timestamp()}] [{level}] [{tunnel_id}] {message}")


def parse_addr(addr_str: str) -> Tuple[str, int]:
    """Parsează 'host:port' în (host, port)."""
    if ":" not in addr_str:
        raise ValueError(f"Format invalid: {addr_str}. Folosiți 'host:port'.")
    host, port_str = addr_str.rsplit(":", 1)
    return host, int(port_str)


# ════════════════════════════════════════════════════════════════════════════
#  FORWARDING UNIDIRECȚIONAL
# ════════════════════════════════════════════════════════════════════════════

def forward_stream(
    src: socket.socket,
    dst: socket.socket,
    direction: str,
    tunnel_id: str,
    on_close: threading.Event
) -> None:
    """
    Copiază date de la src la dst până când conexiunea se închide.
    
    Acesta este pattern-ul fundamental pentru proxy/tunnel:
    - Citește chunk-uri din src
    - Le scrie în dst
    - Se oprește când src returnează 0 bytes (conexiune închisă)
    
    Args:
        src: Socket sursă (de citit)
        dst: Socket destinație (de scris)
        direction: String descriptiv (ex: "client→target")
        tunnel_id: ID pentru logging
        on_close: Event pentru a semnala celuilalt thread să se oprească
    """
    total_bytes = 0
    
    try:
        while not on_close.is_set():
            # Citim date din sursă
            data = src.recv(BUFFER_SIZE)
            
            if not data:
                # 0 bytes = peer-ul a închis conexiunea
                log("INFO", tunnel_id, f"{direction}: Conexiune închisă de peer")
                break
            
            # Scriem datele în destinație
            dst.sendall(data)
            total_bytes += len(data)
            
            # Logging detaliat (poate fi comentat pentru producție)
            preview = data[:50].decode("utf-8", errors="replace")
            if len(data) > 50:
                preview += "..."
            log("DATA", tunnel_id, f"{direction}: {len(data)} bytes: {preview!r}")
            
    except ConnectionResetError:
        log("WARN", tunnel_id, f"{direction}: Connection reset by peer")
    except BrokenPipeError:
        log("WARN", tunnel_id, f"{direction}: Broken pipe (peer închis)")
    except OSError as e:
        if not on_close.is_set():
            log("ERROR", tunnel_id, f"{direction}: {e}")
    finally:
        # Semnalăm celuilalt thread să se oprească
        on_close.set()
        log("INFO", tunnel_id, f"{direction}: Forwarding oprit. Total: {total_bytes} bytes")


# ════════════════════════════════════════════════════════════════════════════
#  HANDLER CONEXIUNE CLIENT
# ════════════════════════════════════════════════════════════════════════════

def handle_client(
    client_socket: socket.socket,
    client_addr: Tuple[str, int],
    target_host: str,
    target_port: int,
    tunnel_id: str
) -> None:
    """
    Gestionează o conexiune client: deschide conexiune către target,
    pornește forwarding bidirecțional.
    
    Pași:
    1. Deschide conexiune TCP către server țintă
    2. Pornește 2 thread-uri pentru forwarding (client↔target)
    3. Așteaptă terminarea ambelor direcții
    4. Închide ambele conexiuni
    """
    log("INFO", tunnel_id, f"Client conectat de la {client_addr[0]}:{client_addr[1]}")
    
    target_socket = None
    
    try:
        # ─────────────────────────────────────────────────────────────────────
        # Pas 1: Conectare la server țintă
        # ─────────────────────────────────────────────────────────────────────
        target_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        target_socket.settimeout(10.0)  # Timeout pentru connect
        
        log("INFO", tunnel_id, f"Conectare la target {target_host}:{target_port}...")
        target_socket.connect((target_host, target_port))
        target_socket.settimeout(None)  # Dezactivăm timeout pentru transfer
        
        log("INFO", tunnel_id, f"Conexiune stabilită cu target {target_host}:{target_port}")
        
        # ─────────────────────────────────────────────────────────────────────
        # Pas 2: Event pentru sincronizare între thread-uri
        # ─────────────────────────────────────────────────────────────────────
        close_event = threading.Event()
        
        # ─────────────────────────────────────────────────────────────────────
        # Pas 3: Pornire thread-uri pentru forwarding bidirecțional
        # ─────────────────────────────────────────────────────────────────────
        thread_client_to_target = threading.Thread(
            target=forward_stream,
            args=(client_socket, target_socket, "client→target", tunnel_id, close_event),
            daemon=True
        )
        
        thread_target_to_client = threading.Thread(
            target=forward_stream,
            args=(target_socket, client_socket, "target→client", tunnel_id, close_event),
            daemon=True
        )
        
        thread_client_to_target.start()
        thread_target_to_client.start()
        
        # ─────────────────────────────────────────────────────────────────────
        # Pas 4: Așteptăm terminarea ambelor thread-uri
        # ─────────────────────────────────────────────────────────────────────
        thread_client_to_target.join()
        thread_target_to_client.join()
        
    except ConnectionRefusedError:
        log("ERROR", tunnel_id, f"Target {target_host}:{target_port} a refuzat conexiunea")
    except socket.timeout:
        log("ERROR", tunnel_id, f"Timeout la conectare către {target_host}:{target_port}")
    except OSError as e:
        log("ERROR", tunnel_id, f"Eroare: {e}")
    finally:
        # ─────────────────────────────────────────────────────────────────────
        # Pas 5: Cleanup - închidem ambele socket-uri
        # ─────────────────────────────────────────────────────────────────────
        try:
            client_socket.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        client_socket.close()
        
        if target_socket:
            try:
                target_socket.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            target_socket.close()
        
        log("INFO", tunnel_id, "Tunnel închis")


# ════════════════════════════════════════════════════════════════════════════
#  SERVER PRINCIPAL (ACCEPT LOOP)
# ════════════════════════════════════════════════════════════════════════════

def run_tunnel(listen_host: str, listen_port: int, target_host: str, target_port: int) -> int:
    """
    Pornește serverul tunnel care acceptă conexiuni și le redirecționează.
    
    Pentru fiecare client:
    1. Accept conexiune
    2. Pornește thread pentru handle_client
    3. Continuă să accepte alte conexiuni
    """
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server_socket.bind((listen_host, listen_port))
        server_socket.listen(10)  # Backlog de 10 conexiuni în așteptare
        
        print(f"╔══════════════════════════════════════════════════════════════╗")
        print(f"║  TCP Tunnel activ                                            ║")
        print(f"║  Listen: {listen_host}:{listen_port:<44}║")
        print(f"║  Target: {target_host}:{target_port:<44}║")
        print(f"╚══════════════════════════════════════════════════════════════╝")
        print(f"[{timestamp()}] [INFO] Aștept conexiuni... (Ctrl+C pentru oprire)")
        
        tunnel_counter = 0
        
        while True:
            try:
                client_socket, client_addr = server_socket.accept()
                tunnel_counter += 1
                tunnel_id = f"T{tunnel_counter:04d}"
                
                # Pornire thread pentru acest client
                client_thread = threading.Thread(
                    target=handle_client,
                    args=(client_socket, client_addr, target_host, target_port, tunnel_id),
                    daemon=True
                )
                client_thread.start()
                
            except OSError as e:
                log("ERROR", "MAIN", f"Eroare accept: {e}")
                break
                
    except KeyboardInterrupt:
        print(f"\n[{timestamp()}] [INFO] Oprire server (Ctrl+C)")
    except OSError as e:
        print(f"[{timestamp()}] [ERROR] Nu pot face bind pe {listen_host}:{listen_port}: {e}")
        return 1
    finally:
        server_socket.close()
        print(f"[{timestamp()}] [INFO] Server socket închis")
    
    return 0


# ════════════════════════════════════════════════════════════════════════════
#  MAIN
# ════════════════════════════════════════════════════════════════════════════

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="ex03_tcp_tunnel.py",
        description="TCP Tunnel (Port Forwarder) pentru redirecționarea traficului.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemple:
  # Tunnel de la localhost:9090 către server:8080
  python3 ex03_tcp_tunnel.py --listen 0.0.0.0:9090 --target 192.168.1.100:8080

  # Test cu netcat
  echo "hello" | nc localhost 9090

Topologie tipică Mininet:
  a1 (10.0.1.1) ──► r1:9090 (tunnel) ──► b1:8080 (server echo)
        """
    )
    
    parser.add_argument(
        "--listen", default=DEFAULT_LISTEN,
        help=f"Adresa de ascultare (host:port), default: {DEFAULT_LISTEN}"
    )
    parser.add_argument(
        "--target", default=DEFAULT_TARGET,
        help=f"Adresa serverului țintă (host:port), default: {DEFAULT_TARGET}"
    )
    
    args = parser.parse_args(argv)
    
    try:
        listen_host, listen_port = parse_addr(args.listen)
        target_host, target_port = parse_addr(args.target)
    except ValueError as e:
        print(f"Eroare: {e}")
        return 1
    
    return run_tunnel(listen_host, listen_port, target_host, target_port)


if __name__ == "__main__":
    sys.exit(main())
