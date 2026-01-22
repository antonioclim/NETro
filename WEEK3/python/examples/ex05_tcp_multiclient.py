#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  Exercițiul 5: TCP Server Multiclient (Thread per Client)                    ║
║  Săptămâna 3 — Rețele de Calculatoare                                        ║
╚══════════════════════════════════════════════════════════════════════════════╝

SCOPUL DIDACTIC:
    - Gestionarea mai multor clienți TCP simultan
    - Pattern "thread per client" cu threading.Thread
    - Sincronizare acces la resurse partajate (threading.Lock)
    - Observarea comportamentului concurrent în Wireshark

PROBLEMA:
    Un server TCP simplu (accept → recv → send) poate servi doar un client.
    Ceilalți clienți așteaptă în coada listen().
    
    Soluția: pentru fiecare accept(), pornim un thread separat.

ALTERNATIVE LA THREADING:
    1. Process per client (multiprocessing) - overhead mare, izolare bună
    2. Event loop (select/epoll) - eficient, complex
    3. Async (asyncio) - modern, necesită async/await

RULARE:
    # Server:
    python3 ex05_tcp_multiclient.py

    # Clienți (în mai multe terminale):
    nc 127.0.0.1 3333
    # Scrieți text, primiți răspuns uppercase

OBSERVAȚII WIRESHARK:
    - Fiecare client are propriul TCP stream
    - Mesajele sunt independente pe fiecare stream
    - Filter: tcp.port == 3333
"""
from __future__ import annotations

import argparse
import socket
import sys
import threading
from datetime import datetime
from typing import Set


# ════════════════════════════════════════════════════════════════════════════
#  CONFIGURĂRI
# ════════════════════════════════════════════════════════════════════════════

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 3333
BUFFER_SIZE = 1024


# ════════════════════════════════════════════════════════════════════════════
#  LOGGING
# ════════════════════════════════════════════════════════════════════════════

def timestamp() -> str:
    return datetime.now().strftime("%H:%M:%S.%f")[:-3]


def log(level: str, thread_id: str, message: str) -> None:
    print(f"[{timestamp()}] [{level:5s}] [{thread_id:8s}] {message}")


# ════════════════════════════════════════════════════════════════════════════
#  MANAGEMENT CLIENȚI
# ════════════════════════════════════════════════════════════════════════════

class ClientManager:
    """
    Gestionează lista de clienți conectați.
    Thread-safe prin utilizarea unui Lock.
    """
    
    def __init__(self):
        self.clients: Set[socket.socket] = set()
        self.lock = threading.Lock()
        self.client_counter = 0
    
    def add(self, client: socket.socket) -> int:
        """Adaugă un client și returnează ID-ul său."""
        with self.lock:
            self.client_counter += 1
            self.clients.add(client)
            return self.client_counter
    
    def remove(self, client: socket.socket) -> None:
        """Elimină un client din listă."""
        with self.lock:
            self.clients.discard(client)
    
    def count(self) -> int:
        """Returnează numărul de clienți conectați."""
        with self.lock:
            return len(self.clients)
    
    def broadcast(self, message: bytes, exclude: socket.socket = None) -> None:
        """Trimite mesaj către toți clienții (pentru exercițiul chat)."""
        with self.lock:
            for client in self.clients:
                if client != exclude:
                    try:
                        client.sendall(message)
                    except OSError:
                        pass


# Instanță globală pentru managementul clienților
manager = ClientManager()


# ════════════════════════════════════════════════════════════════════════════
#  HANDLER CLIENT
# ════════════════════════════════════════════════════════════════════════════

def handle_client(client_socket: socket.socket, client_addr: tuple[str, int]) -> None:
    """
    Handler pentru un client individual.
    Rulează în thread separat.
    
    Comportament:
    - Primește mesaje de la client
    - Răspunde cu mesajul în uppercase
    - Se oprește când clientul închide conexiunea
    """
    ip, port = client_addr
    client_id = manager.add(client_socket)
    thread_id = f"C{client_id:05d}"
    
    log("CONN", thread_id, f"Client conectat de la {ip}:{port}")
    log("INFO", thread_id, f"Total clienți conectați: {manager.count()}")
    
    try:
        # Mesaj de bun venit
        welcome = f"Bine ai venit! Ești clientul #{client_id}. Scrie ceva:\n"
        client_socket.sendall(welcome.encode("utf-8"))
        
        while True:
            # ─────────────────────────────────────────────────────────────────
            # recv() blochează până primește date sau conexiunea se închide
            # ─────────────────────────────────────────────────────────────────
            data = client_socket.recv(BUFFER_SIZE)
            
            if not data:
                # 0 bytes = peer-ul a închis conexiunea (FIN)
                log("INFO", thread_id, f"Client {ip}:{port} a închis conexiunea")
                break
            
            # Decodificare și procesare
            text = data.decode("utf-8", errors="replace").strip()
            log("RECV", thread_id, f"← {text!r}")
            
            # Răspuns: uppercase
            response = data.upper()
            client_socket.sendall(response)
            log("SEND", thread_id, f"→ {response.decode('utf-8', errors='replace').strip()!r}")
            
    except ConnectionResetError:
        log("WARN", thread_id, f"Conexiune resetată de {ip}:{port}")
    except BrokenPipeError:
        log("WARN", thread_id, f"Pipe întrerupt pentru {ip}:{port}")
    except OSError as e:
        log("ERROR", thread_id, f"Eroare: {e}")
    finally:
        # Cleanup
        manager.remove(client_socket)
        try:
            client_socket.close()
        except OSError:
            pass
        log("DISC", thread_id, f"Client deconectat. Rămași: {manager.count()}")


# ════════════════════════════════════════════════════════════════════════════
#  SERVER PRINCIPAL
# ════════════════════════════════════════════════════════════════════════════

def run_server(host: str, port: int) -> int:
    """
    Pornește serverul TCP multiclient.
    
    Bucla principală:
    1. accept() - așteaptă conexiune
    2. Pornește thread pentru handle_client
    3. Revine la accept()
    """
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        # ─────────────────────────────────────────────────────────────────────
        # Opțiuni socket
        # ─────────────────────────────────────────────────────────────────────
        # SO_REUSEADDR: permite restart rapid (nu așteaptă TIME_WAIT)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # Bind și listen
        server_socket.bind((host, port))
        server_socket.listen(10)  # Backlog: max 10 conexiuni în așteptare
        
        print("╔══════════════════════════════════════════════════════════════╗")
        print("║  TCP Server Multiclient (Thread per Client)                  ║")
        print(f"║  Ascultă pe: {host}:{port:<43}║")
        print("╚══════════════════════════════════════════════════════════════╝")
        log("INFO", "MAIN", f"Server pornit. Aștept conexiuni...")
        log("INFO", "MAIN", "Test: nc {host} {port}".format(host=host, port=port))
        
        while True:
            # ─────────────────────────────────────────────────────────────────
            # accept() blochează până când un client se conectează
            # Returnează (socket_nou, (ip, port))
            # ─────────────────────────────────────────────────────────────────
            client_socket, client_addr = server_socket.accept()
            
            # Pornire thread pentru acest client
            client_thread = threading.Thread(
                target=handle_client,
                args=(client_socket, client_addr),
                daemon=True  # Thread se oprește când procesul principal se oprește
            )
            client_thread.start()
            
    except KeyboardInterrupt:
        print()
        log("INFO", "MAIN", "Oprire server (Ctrl+C)")
    except OSError as e:
        log("ERROR", "MAIN", f"Nu pot asculta pe {host}:{port}: {e}")
        return 1
    finally:
        server_socket.close()
        log("INFO", "MAIN", "Server închis")
    
    return 0


# ════════════════════════════════════════════════════════════════════════════
#  MAIN
# ════════════════════════════════════════════════════════════════════════════

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="ex05_tcp_multiclient.py",
        description="Server TCP multiclient cu thread per client."
    )
    parser.add_argument(
        "--host", default=DEFAULT_HOST,
        help=f"Adresa IP de ascultare (default: {DEFAULT_HOST})"
    )
    parser.add_argument(
        "--port", type=int, default=DEFAULT_PORT,
        help=f"Portul de ascultare (default: {DEFAULT_PORT})"
    )
    args = parser.parse_args(argv)
    
    return run_server(args.host, args.port)


if __name__ == "__main__":
    sys.exit(main())
