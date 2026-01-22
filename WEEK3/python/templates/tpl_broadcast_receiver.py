#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  TEMPLATE: UDP Broadcast Receiver cu Timestamp                               ║
║  Săptămâna 3 — Rețele de Calculatoare                                        ║
╚══════════════════════════════════════════════════════════════════════════════╝

SARCINĂ:
    Completați secțiunile marcate cu TODO pentru a crea un receiver UDP broadcast
    care afișează fiecare mesaj primit cu:
    - Număr de ordine (counter)
    - Timestamp
    - Adresa sursei
    - Conținutul mesajului

OUTPUT DORIT:
    [#1 @ 2025-03-10 14:32:01.123] De la 10.0.0.1:54321 → "HELLO_BCAST #0"
    [#2 @ 2025-03-10 14:32:02.125] De la 10.0.0.1:54321 → "HELLO_BCAST #1"
    ...

HINT-URI:
    - Folosiți datetime.now() pentru timestamp
    - socket.recvfrom() returnează (data, (ip, port))
    - data.decode("utf-8") convertește bytes în string

VERIFICARE:
    # Terminal 1: Porniți acest receiver
    python3 tpl_broadcast_receiver.py --port 5007 --count 5

    # Terminal 2: Trimiteți mesaje broadcast
    python3 ../examples/ex01_udp_broadcast.py send --port 5007 --count 5
"""
from __future__ import annotations

import argparse
import socket
import sys
from datetime import datetime


def run_receiver(port: int, count: int) -> int:
    """
    Receiver UDP broadcast cu timestamp și counter.
    
    Args:
        port: Portul pe care ascultă
        count: Numărul de mesaje de primit (0 = infinit)
    
    Returns:
        0 pentru succes
    """
    # ═══════════════════════════════════════════════════════════════════════
    # TODO 1: Creați un socket UDP
    # Hint: socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # ═══════════════════════════════════════════════════════════════════════
    sock = None  # TODO: înlocuiți cu crearea socket-ului
    
    # ═══════════════════════════════════════════════════════════════════════
    # TODO 2: Activați SO_REUSEADDR pentru restart rapid
    # Hint: sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # ═══════════════════════════════════════════════════════════════════════
    # TODO: adăugați setsockopt aici
    
    # ═══════════════════════════════════════════════════════════════════════
    # TODO 3: Faceți bind pe port (ascultați pe toate interfețele)
    # Hint: sock.bind(("", port))
    # ═══════════════════════════════════════════════════════════════════════
    # TODO: adăugați bind aici
    
    print(f"[INFO] Receiver pornit pe portul {port}. Aștept mesaje broadcast...")
    
    counter = 0
    
    try:
        while count == 0 or counter < count:
            # ═══════════════════════════════════════════════════════════════
            # TODO 4: Primiți o datagramă cu recvfrom()
            # recvfrom() returnează (data, (ip, port))
            # Hint: data, (sender_ip, sender_port) = sock.recvfrom(65535)
            # ═══════════════════════════════════════════════════════════════
            data = b""  # TODO: înlocuiți cu recvfrom
            sender_ip = "???"  # TODO: extrageți din rezultatul recvfrom
            sender_port = 0    # TODO: extrageți din rezultatul recvfrom
            
            # ═══════════════════════════════════════════════════════════════
            # TODO 5: Incrementați counter-ul
            # ═══════════════════════════════════════════════════════════════
            # TODO: counter += 1
            
            # ═══════════════════════════════════════════════════════════════
            # TODO 6: Obțineți timestamp-ul curent
            # Hint: datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            # ═══════════════════════════════════════════════════════════════
            ts = "???"  # TODO: înlocuiți cu timestamp real
            
            # ═══════════════════════════════════════════════════════════════
            # TODO 7: Decodificați datele din bytes în string
            # Hint: data.decode("utf-8", errors="replace")
            # ═══════════════════════════════════════════════════════════════
            text = "???"  # TODO: decodificați data
            
            # ═══════════════════════════════════════════════════════════════
            # TODO 8: Afișați în formatul cerut
            # Format: [#N @ TIMESTAMP] De la IP:PORT → "mesaj"
            # ═══════════════════════════════════════════════════════════════
            print(f"[#{counter} @ {ts}] De la {sender_ip}:{sender_port} → {text!r}")
            
    except KeyboardInterrupt:
        print(f"\n[INFO] Oprit de utilizator. Total mesaje: {counter}")
    finally:
        if sock:
            sock.close()
    
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="tpl_broadcast_receiver.py",
        description="Template: UDP Broadcast receiver cu timestamp"
    )
    parser.add_argument("--port", type=int, default=5007, help="Port de ascultare")
    parser.add_argument("--count", type=int, default=0, help="Mesaje de primit (0=infinit)")
    
    args = parser.parse_args(argv)
    return run_receiver(args.port, args.count)


if __name__ == "__main__":
    sys.exit(main())
