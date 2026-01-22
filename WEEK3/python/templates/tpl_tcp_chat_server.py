#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  TEMPLATE: TCP Chat Server (Broadcast la toți clienții)                      ║
║  Săptămâna 3 — Rețele de Calculatoare                                        ║
╚══════════════════════════════════════════════════════════════════════════════╝

SARCINĂ:
    Completați secțiunile TODO pentru a crea un server de chat care:
    1. Acceptă conexiuni de la mai mulți clienți
    2. Când un client trimite un mesaj, îl transmite TUTUROR celorlalți clienți
    3. Gestionează deconectările graceful

COMPORTAMENT DORIT:
    - Client A trimite "Hello" → Clienții B, C primesc "Hello" (dar nu și A)
    - Client B se deconectează → Clienții A, C primesc notificare

HINT-URI:
    - Mențineți o listă de clienți conectați
    - Folosiți un Lock pentru acces thread-safe la listă
    - În broadcast, excludeți expeditorul

VERIFICARE:
    # Terminal 1: Server
    python3 tpl_tcp_chat_server.py --port 4000

    # Terminal 2, 3, 4: Clienți (netcat)
    nc localhost 4000
"""
from __future__ import annotations

import argparse
import socket
import sys
import threading
from datetime import datetime
from typing import Dict


# ════════════════════════════════════════════════════════════════════════════
#  CONSTANTE
# ════════════════════════════════════════════════════════════════════════════

BUFFER_SIZE = 1024


# ════════════════════════════════════════════════════════════════════════════
#  MANAGEMENT CLIENȚI
# ════════════════════════════════════════════════════════════════════════════

# Dicționar: socket → nume_client
clients: Dict[socket.socket, str] = {}

# Lock pentru acces thread-safe la dicționarul de clienți
clients_lock = threading.Lock()

# Counter pentru generare nume clienți
client_counter = 0


def add_client(sock: socket.socket) -> str:
    """
    Adaugă un client nou în listă și returnează numele atribuit.
    """
    global client_counter
    with clients_lock:
        client_counter += 1
        name = f"User{client_counter}"
        clients[sock] = name
        return name


def remove_client(sock: socket.socket) -> str | None:
    """
    Elimină un client din listă și returnează numele său.
    """
    with clients_lock:
        return clients.pop(sock, None)


def broadcast_message(message: str, exclude: socket.socket | None = None) -> None:
    """
    Trimite un mesaj către TOȚI clienții, exceptând pe cel specificat.
    
    Args:
        message: Mesajul de trimis
        exclude: Socket-ul clientului care nu primește mesajul (expeditorul)
    """
    # ═══════════════════════════════════════════════════════════════════════
    # TODO: Implementați broadcast-ul
    # 
    # Pași:
    # 1. Obțineți lista de clienți (cu lock!)
    # 2. Pentru fiecare client (exceptând exclude):
    #    - Încercați să trimiteți mesajul
    #    - Ignorați erorile (clientul poate fi deconectat)
    #
    # Hint: 
    #   with clients_lock:
    #       for client_sock, name in clients.items():
    #           if client_sock != exclude:
    #               try:
    #                   client_sock.sendall(message.encode("utf-8"))
    #               except OSError:
    #                   pass
    # ═══════════════════════════════════════════════════════════════════════
    pass  # TODO: înlocuiți cu implementarea


def get_client_count() -> int:
    """Returnează numărul de clienți conectați."""
    with clients_lock:
        return len(clients)


# ════════════════════════════════════════════════════════════════════════════
#  HANDLER CLIENT
# ════════════════════════════════════════════════════════════════════════════

def handle_client(client_socket: socket.socket, client_addr: tuple[str, int]) -> None:
    """
    Gestionează comunicarea cu un client.
    Rulează în thread separat.
    """
    ip, port = client_addr
    client_name = add_client(client_socket)
    
    print(f"[CONNECT] {client_name} ({ip}:{port}) s-a conectat. Total: {get_client_count()}")
    
    # ═══════════════════════════════════════════════════════════════════════
    # TODO: Trimiteți mesaj de bun venit clientului
    # Hint: client_socket.sendall(f"Bine ai venit, {client_name}!\n".encode())
    # ═══════════════════════════════════════════════════════════════════════
    # TODO: mesaj bun venit
    
    # ═══════════════════════════════════════════════════════════════════════
    # TODO: Anunțați ceilalți clienți că s-a conectat cineva nou
    # Hint: broadcast_message(f"[SERVER] {client_name} s-a alăturat chat-ului\n", exclude=client_socket)
    # ═══════════════════════════════════════════════════════════════════════
    # TODO: broadcast join
    
    try:
        while True:
            # Primim date de la client
            data = client_socket.recv(BUFFER_SIZE)
            
            if not data:
                # Client s-a deconectat
                break
            
            text = data.decode("utf-8", errors="replace").strip()
            
            if not text:
                continue
            
            print(f"[MSG] {client_name}: {text}")
            
            # ═══════════════════════════════════════════════════════════════
            # TODO: Trimiteți mesajul către TOȚI ceilalți clienți
            # Format: "[Nume] mesaj\n"
            # Hint: broadcast_message(f"[{client_name}] {text}\n", exclude=client_socket)
            # ═══════════════════════════════════════════════════════════════
            # TODO: broadcast mesaj
            pass
            
    except ConnectionResetError:
        print(f"[WARN] {client_name} - conexiune resetată")
    except OSError as e:
        print(f"[ERROR] {client_name} - {e}")
    finally:
        # Cleanup
        remove_client(client_socket)
        
        # ═══════════════════════════════════════════════════════════════════
        # TODO: Anunțați ceilalți clienți că s-a deconectat
        # Hint: broadcast_message(f"[SERVER] {client_name} a părăsit chat-ul\n")
        # ═══════════════════════════════════════════════════════════════════
        # TODO: broadcast leave
        
        try:
            client_socket.close()
        except OSError:
            pass
        
        print(f"[DISCONNECT] {client_name} s-a deconectat. Total: {get_client_count()}")


# ════════════════════════════════════════════════════════════════════════════
#  SERVER PRINCIPAL
# ════════════════════════════════════════════════════════════════════════════

def run_server(host: str, port: int) -> int:
    """Pornește serverul de chat."""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server_socket.bind((host, port))
        server_socket.listen(10)
        
        print("╔══════════════════════════════════════════════════════════════╗")
        print("║  TCP Chat Server (Template)                                  ║")
        print(f"║  Ascultă pe: {host}:{port:<43}║")
        print("╚══════════════════════════════════════════════════════════════╝")
        print("[INFO] Aștept conexiuni... (Test: nc localhost " + str(port) + ")")
        
        while True:
            client_socket, client_addr = server_socket.accept()
            
            client_thread = threading.Thread(
                target=handle_client,
                args=(client_socket, client_addr),
                daemon=True
            )
            client_thread.start()
            
    except KeyboardInterrupt:
        print("\n[INFO] Oprire server")
    except OSError as e:
        print(f"[ERROR] {e}")
        return 1
    finally:
        server_socket.close()
    
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="tpl_tcp_chat_server.py",
        description="Template: TCP Chat Server cu broadcast"
    )
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=4000)
    
    args = parser.parse_args(argv)
    return run_server(args.host, args.port)


if __name__ == "__main__":
    sys.exit(main())
