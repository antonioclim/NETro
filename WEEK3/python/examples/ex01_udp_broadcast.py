#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  Exercițiul 1: UDP Broadcast (IPv4)                                          ║
║  Săptămâna 3 — Rețele de Calculatoare                                        ║
╚══════════════════════════════════════════════════════════════════════════════╝

SCOPUL DIDACTIC:
    - Înțelegerea diferenței unicast vs broadcast la nivel IP
    - Utilizarea opțiunii SO_BROADCAST pe socket-ul UDP
    - Observarea comportamentului "one-to-all" într-un domeniu L2
    - Captura și analiza traficului broadcast cu tcpdump

CONCEPTE CHEIE:
    1. Broadcast = trimitere către TOATE hosturile dintr-un domeniu de broadcast (L2)
    2. Adresa 255.255.255.255 = "limited broadcast" (nu trece de routere)
    3. Adresa x.x.x.255 = "directed broadcast" (pentru o subrețea specifică)
    4. SO_BROADCAST = flag obligatoriu pe socket pentru a permite trimiterea broadcast

RULARE:
    # Receiver (pe h2 și h3):
    python3 ex01_udp_broadcast.py recv --port 5007 --count 5

    # Sender (pe h1):
    python3 ex01_udp_broadcast.py send --dst 255.255.255.255 --port 5007 --count 5

    # Captură trafic (pe h3):
    tcpdump -ni h3-eth0 'udp port 5007'

OBSERVAȚII IMPORTANTE:
    - Broadcast-ul NU trece de routere (este limitat la domeniul L2)
    - Toate hosturile din domeniu primesc frame-ul la nivel L2, indiferent dacă
      ascultă sau nu pe portul respectiv (saturează rețeaua)
    - Este ineficient la scară mare → se preferă multicast sau unicast
"""
from __future__ import annotations

import argparse
import socket
import sys
import time
from datetime import datetime
from typing import Callable


# ════════════════════════════════════════════════════════════════════════════
#  CONSTANTE ȘI CONFIGURĂRI
# ════════════════════════════════════════════════════════════════════════════

DEFAULT_BROADCAST_ADDR = "255.255.255.255"
DEFAULT_PORT = 5007
DEFAULT_MESSAGE = "HELLO_BCAST"
DEFAULT_INTERVAL = 1.0
BUFFER_SIZE = 65535


# ════════════════════════════════════════════════════════════════════════════
#  FUNCȚII UTILITARE
# ════════════════════════════════════════════════════════════════════════════

def timestamp() -> str:
    """Returnează timestamp-ul curent în format lizibil."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]


def log(level: str, message: str) -> None:
    """Afișează un mesaj cu timestamp și nivel."""
    print(f"[{timestamp()}] [{level}] {message}")


# ════════════════════════════════════════════════════════════════════════════
#  SENDER: Trimitere UDP Broadcast
# ════════════════════════════════════════════════════════════════════════════

def cmd_send(args: argparse.Namespace) -> int:
    """
    Trimite datagrame UDP către adresa de broadcast.
    
    Pași:
    1. Creare socket UDP (SOCK_DGRAM)
    2. Activare SO_BROADCAST (obligatoriu!)
    3. Trimitere periodică cu sendto()
    
    Args:
        args: Argumente parsate (dst, port, message, interval, count, bind)
    
    Returns:
        0 pentru succes, 1 pentru eroare
    """
    dst = args.dst
    port = args.port
    base_message = args.message
    interval = args.interval
    count = args.count

    # ─────────────────────────────────────────────────────────────────────────
    # Pas 1: Creare socket UDP
    # ─────────────────────────────────────────────────────────────────────────
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # ─────────────────────────────────────────────────────────────────────────
    # Pas 2: Activare SO_BROADCAST
    # CRITIC: Fără această opțiune, sendto() către adresa de broadcast va eșua
    #         cu PermissionError sau "Operation not permitted" pe majoritatea SO.
    # ─────────────────────────────────────────────────────────────────────────
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    # Opțional: bind pe o interfață specifică (util când ai mai multe interfețe)
    if args.bind:
        sock.bind((args.bind, 0))
        log("INFO", f"Socket legat de interfața: {args.bind}")

    log("INFO", f"UDP Broadcast Sender pornit → {dst}:{port}")
    log("INFO", f"Parametri: interval={interval}s, count={count} (0=infinit)")

    counter = 0
    try:
        while count == 0 or counter < count:
            # Construim payload-ul cu număr de secvență
            payload = f"{base_message} #{counter}".encode("utf-8")

            # ─────────────────────────────────────────────────────────────────
            # Pas 3: Trimitere datagramă
            # sendto() specifică destinația pentru fiecare datagramă (UDP e
            # connectionless, deci nu există "conexiune" persistentă).
            # ─────────────────────────────────────────────────────────────────
            sock.sendto(payload, (dst, port))
            log("SEND", f"{len(payload):4d} bytes → {dst}:{port} :: {payload.decode()!r}")

            counter += 1
            time.sleep(interval)

    except KeyboardInterrupt:
        log("INFO", "Întrerupt de utilizator (Ctrl+C).")
    except OSError as e:
        log("ERROR", f"Eroare socket: {e}")
        return 1
    finally:
        sock.close()
        log("INFO", f"Socket închis. Total trimise: {counter} datagrame.")

    return 0


# ════════════════════════════════════════════════════════════════════════════
#  RECEIVER: Primire UDP Broadcast
# ════════════════════════════════════════════════════════════════════════════

def cmd_recv(args: argparse.Namespace) -> int:
    """
    Primește datagrame UDP (inclusiv broadcast).
    
    Pași:
    1. Creare socket UDP
    2. Activare SO_REUSEADDR (pentru restart rapid în laborator)
    3. Bind pe port (și opțional pe o adresă specifică)
    4. Loop recvfrom() pentru primire datagrame
    
    Args:
        args: Argumente parsate (bind_addr, port, count, prefix, timeout)
    
    Returns:
        0 pentru succes
    """
    bind_addr = args.bind_addr
    port = args.port
    count = args.count
    prefix = args.prefix
    timeout_sec = args.timeout

    # ─────────────────────────────────────────────────────────────────────────
    # Pas 1: Creare socket UDP
    # ─────────────────────────────────────────────────────────────────────────
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # ─────────────────────────────────────────────────────────────────────────
    # Pas 2: SO_REUSEADDR permite reutilizarea portului imediat după închidere.
    # Util în laborator când reporniți frecvent programul.
    # ─────────────────────────────────────────────────────────────────────────
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # ─────────────────────────────────────────────────────────────────────────
    # Pas 3: Bind pe adresă și port
    # bind_addr="" (string gol) = INADDR_ANY = ascultă pe toate interfețele
    # Acest lucru e necesar pentru a primi broadcast!
    # ─────────────────────────────────────────────────────────────────────────
    sock.bind((bind_addr, port))

    # Opțional: timeout pentru a nu bloca la infinit
    if timeout_sec > 0:
        sock.settimeout(timeout_sec)

    log("INFO", f"UDP Broadcast Receiver pornit pe {bind_addr or '*'}:{port}")
    log("INFO", f"Parametri: count={count} (0=infinit), prefix={prefix!r}, timeout={timeout_sec}s")

    accepted = 0
    total = 0

    try:
        while count == 0 or accepted < count:
            try:
                # ─────────────────────────────────────────────────────────────
                # Pas 4: recvfrom() - blochează până primește o datagramă
                # Returnează (data, (ip_sursă, port_sursă))
                # ─────────────────────────────────────────────────────────────
                data, (sender_ip, sender_port) = sock.recvfrom(BUFFER_SIZE)
            except socket.timeout:
                log("WARN", f"Timeout după {timeout_sec}s fără date. Oprire.")
                break

            total += 1
            text = data.decode("utf-8", errors="replace")

            # Filtrare opțională după prefix
            if prefix and not text.startswith(prefix):
                log("SKIP", f"De la {sender_ip}:{sender_port} → {text!r} (nu începe cu {prefix!r})")
                continue

            accepted += 1
            log("RECV", f"{len(data):4d} bytes de la {sender_ip}:{sender_port} → {text!r}")

    except KeyboardInterrupt:
        log("INFO", "Întrerupt de utilizator (Ctrl+C).")
    finally:
        sock.close()
        log("INFO", f"Socket închis. Acceptate: {accepted}/{total} datagrame.")

    return 0


# ════════════════════════════════════════════════════════════════════════════
#  PARSER ARGUMENTE
# ════════════════════════════════════════════════════════════════════════════

def build_parser() -> argparse.ArgumentParser:
    """Construiește parser-ul de argumente cu subcomenzile send și recv."""
    parser = argparse.ArgumentParser(
        prog="ex01_udp_broadcast.py",
        description="UDP Broadcast sender/receiver pentru demonstrații de rețea.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemple:
  # Pornire receiver pe portul 5007, primește 5 mesaje:
  python3 ex01_udp_broadcast.py recv --port 5007 --count 5

  # Pornire sender către broadcast, 5 mesaje, interval 0.5s:
  python3 ex01_udp_broadcast.py send --dst 255.255.255.255 --port 5007 --count 5 --interval 0.5
        """
    )

    subparsers = parser.add_subparsers(dest="command", required=True, help="Comandă de executat")

    # ─────────────────────────────────────────────────────────────────────────
    # Subcomanda: send
    # ─────────────────────────────────────────────────────────────────────────
    parser_send = subparsers.add_parser("send", help="Trimite datagrame UDP broadcast")
    parser_send.add_argument(
        "--dst", default=DEFAULT_BROADCAST_ADDR,
        help=f"Adresa de broadcast destinație (default: {DEFAULT_BROADCAST_ADDR})"
    )
    parser_send.add_argument(
        "--port", type=int, default=DEFAULT_PORT,
        help=f"Portul UDP destinație (default: {DEFAULT_PORT})"
    )
    parser_send.add_argument(
        "--message", default=DEFAULT_MESSAGE,
        help=f"Mesajul de trimis (default: {DEFAULT_MESSAGE})"
    )
    parser_send.add_argument(
        "--interval", type=float, default=DEFAULT_INTERVAL,
        help=f"Interval între datagrame în secunde (default: {DEFAULT_INTERVAL})"
    )
    parser_send.add_argument(
        "--count", type=int, default=0,
        help="Număr de datagrame de trimis (0 = infinit)"
    )
    parser_send.add_argument(
        "--bind", default="",
        help="Adresă IP locală de bind (opțional, pentru multi-homed hosts)"
    )
    parser_send.set_defaults(func=cmd_send)

    # ─────────────────────────────────────────────────────────────────────────
    # Subcomanda: recv
    # ─────────────────────────────────────────────────────────────────────────
    parser_recv = subparsers.add_parser("recv", help="Primește datagrame UDP broadcast")
    parser_recv.add_argument(
        "--bind-addr", default="",
        help="Adresa de bind (default: '' = toate interfețele)"
    )
    parser_recv.add_argument(
        "--port", type=int, default=DEFAULT_PORT,
        help=f"Portul UDP pe care ascultă (default: {DEFAULT_PORT})"
    )
    parser_recv.add_argument(
        "--count", type=int, default=0,
        help="Număr de mesaje de acceptat (0 = infinit)"
    )
    parser_recv.add_argument(
        "--prefix", default="",
        help="Filtrare: acceptă doar mesaje care încep cu acest prefix"
    )
    parser_recv.add_argument(
        "--timeout", type=float, default=0.0,
        help="Timeout socket în secunde (0 = fără timeout)"
    )
    parser_recv.set_defaults(func=cmd_recv)

    return parser


# ════════════════════════════════════════════════════════════════════════════
#  MAIN
# ════════════════════════════════════════════════════════════════════════════

def main(argv: list[str] | None = None) -> int:
    """Punct de intrare principal."""
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
