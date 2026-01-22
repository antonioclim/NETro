#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  Exercițiul 2: UDP Multicast (IPv4)                                          ║
║  Săptămâna 3 — Rețele de Calculatoare                                        ║
╚══════════════════════════════════════════════════════════════════════════════╝

SCOPUL DIDACTIC:
    - Înțelegerea diferenței între broadcast și multicast
    - Utilizarea IP_ADD_MEMBERSHIP pentru join la grup multicast
    - Controlul TTL pentru scopul datagramelor multicast
    - Observarea mesajelor IGMP cu tcpdump

CONCEPTE CHEIE:
    1. Multicast = trimitere către un GRUP de hosturi (nu toți, ca la broadcast)
    2. Adrese multicast: 224.0.0.0 – 239.255.255.255 (Clasa D)
       - 224.0.0.x = link-local (TTL=1, nu trece de routere)
       - 239.x.x.x = administratively scoped (organizație/LAN)
    3. Receiverele trebuie să facă JOIN explicit (IP_ADD_MEMBERSHIP)
    4. IGMP (Internet Group Management Protocol) gestionează membership-ul
    5. TTL controlează "distanța" pe care o parcurge datagrama multicast

DIFERENȚE BROADCAST vs MULTICAST:
    ┌────────────────────┬─────────────────────┬─────────────────────┐
    │ Aspect             │ Broadcast           │ Multicast           │
    ├────────────────────┼─────────────────────┼─────────────────────┤
    │ Cine primește      │ TOȚI din domeniu L2 │ Doar membrii grup   │
    │ Join explicit      │ Nu                  │ Da (IGMP)           │
    │ Trece de routere   │ Nu                  │ Da (cu config)      │
    │ Overhead rețea     │ Mare                │ Optimizat           │
    │ Adresă destinație  │ 255.255.255.255     │ 224.x.x.x-239.x.x.x │
    │ MAC destinație     │ ff:ff:ff:ff:ff:ff   │ 01:00:5e:xx:xx:xx   │
    └────────────────────┴─────────────────────┴─────────────────────┘

RULARE:
    # Receiver care face JOIN la grup:
    python3 ex02_udp_multicast.py recv --group 239.1.1.1 --port 5001 --count 5

    # Sender:
    python3 ex02_udp_multicast.py send --group 239.1.1.1 --port 5001 --count 5 --ttl 1

    # Verificare membership:
    ip maddr show dev eth0

    # Captură IGMP și multicast:
    tcpdump -ni eth0 'igmp or (udp port 5001)'
"""
from __future__ import annotations

import argparse
import socket
import struct
import sys
import time
from datetime import datetime


# ════════════════════════════════════════════════════════════════════════════
#  CONSTANTE
# ════════════════════════════════════════════════════════════════════════════

DEFAULT_GROUP = "239.1.1.1"  # Administratively scoped (pentru rețele private)
DEFAULT_PORT = 5001
DEFAULT_MESSAGE = "HELLO_MCAST"
DEFAULT_TTL = 1  # 1 = link-local, nu trece de primul router
BUFFER_SIZE = 65535


# ════════════════════════════════════════════════════════════════════════════
#  FUNCȚII UTILITARE
# ════════════════════════════════════════════════════════════════════════════

def timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]


def log(level: str, message: str) -> None:
    print(f"[{timestamp()}] [{level}] {message}")


def is_multicast_addr(ip: str) -> bool:
    """Verifică dacă adresa IP este în range-ul multicast (224.0.0.0 - 239.255.255.255)."""
    try:
        octets = list(map(int, ip.split(".")))
        return 224 <= octets[0] <= 239
    except (ValueError, IndexError):
        return False


# ════════════════════════════════════════════════════════════════════════════
#  SENDER MULTICAST
# ════════════════════════════════════════════════════════════════════════════

def cmd_send(args: argparse.Namespace) -> int:
    """
    Trimite datagrame UDP către un grup multicast.
    
    Pași:
    1. Creare socket UDP
    2. Setare TTL multicast (IP_MULTICAST_TTL)
    3. Opțional: setare interfață de ieșire (IP_MULTICAST_IF)
    4. Trimitere cu sendto() către adresa de grup
    """
    group = args.group
    port = args.port
    base_message = args.message
    interval = args.interval
    count = args.count
    ttl = args.ttl

    # Validare adresă
    if not is_multicast_addr(group):
        log("ERROR", f"Adresa {group} nu este în range-ul multicast (224-239)!")
        return 1

    # Creare socket UDP
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

    # ─────────────────────────────────────────────────────────────────────────
    # TTL (Time To Live) pentru multicast:
    # - TTL=1: Pachetul NU trece de primul router (link-local)
    # - TTL>1: Pachetul poate traversa routere (necesită IGMP routing)
    # ─────────────────────────────────────────────────────────────────────────
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

    # Opțional: Disable loopback (nu primești propriile mesaje)
    if args.no_loopback:
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 0)

    # Opțional: Specifică interfața de ieșire
    if args.iface:
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF, socket.inet_aton(args.iface))
        log("INFO", f"Interfață de ieșire setată: {args.iface}")

    log("INFO", f"Multicast Sender pornit → {group}:{port} (TTL={ttl})")
    log("INFO", f"Parametri: interval={interval}s, count={count}")

    counter = 0
    try:
        while count == 0 or counter < count:
            payload = f"{base_message} #{counter}".encode("utf-8")
            sock.sendto(payload, (group, port))
            log("SEND", f"{len(payload):4d} bytes → {group}:{port} :: {payload.decode()!r}")
            counter += 1
            time.sleep(interval)

    except KeyboardInterrupt:
        log("INFO", "Întrerupt de utilizator.")
    except OSError as e:
        log("ERROR", f"Eroare socket: {e}")
        return 1
    finally:
        sock.close()
        log("INFO", f"Socket închis. Total trimise: {counter}")

    return 0


# ════════════════════════════════════════════════════════════════════════════
#  RECEIVER MULTICAST (cu JOIN)
# ════════════════════════════════════════════════════════════════════════════

def cmd_recv(args: argparse.Namespace) -> int:
    """
    Primește datagrame UDP multicast după ce face JOIN la grup.
    
    Pași:
    1. Creare socket UDP
    2. SO_REUSEADDR pentru partajare port între procese
    3. Bind pe port (și opțional pe adresa de grup)
    4. JOIN la grup cu IP_ADD_MEMBERSHIP
    5. Loop recvfrom() pentru primire
    6. LEAVE din grup la ieșire (opțional, SO face automat la close)
    """
    group = args.group
    port = args.port
    count = args.count
    iface = args.iface
    timeout_sec = args.timeout

    if not is_multicast_addr(group):
        log("ERROR", f"Adresa {group} nu este multicast!")
        return 1

    # Creare socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Pe unele sisteme, e necesar și SO_REUSEPORT
    try:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    except AttributeError:
        pass  # Nu există pe toate platformele

    # ─────────────────────────────────────────────────────────────────────────
    # Bind: Pentru multicast, de obicei bind pe ("", port) sau (group, port)
    # Bind pe adresa grupului restricționează doar la pachete pentru acel grup.
    # ─────────────────────────────────────────────────────────────────────────
    bind_addr = args.bind_group and group or ""
    sock.bind((bind_addr, port))
    log("INFO", f"Socket bind pe {bind_addr or '*'}:{port}")

    # ─────────────────────────────────────────────────────────────────────────
    # JOIN LA GRUP (IP_ADD_MEMBERSHIP)
    # Structura mreq: 4 bytes IP grup + 4 bytes IP interfață (sau INADDR_ANY)
    # Aceasta trimite un IGMP Membership Report către routere/switch-uri
    # ─────────────────────────────────────────────────────────────────────────
    if iface:
        # Join pe o interfață specifică
        mreq = socket.inet_aton(group) + socket.inet_aton(iface)
        log("INFO", f"JOIN grup {group} pe interfața {iface}")
    else:
        # Join pe orice interfață (INADDR_ANY)
        mreq = socket.inet_aton(group) + struct.pack("=I", socket.INADDR_ANY)
        log("INFO", f"JOIN grup {group} pe toate interfețele")

    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    if timeout_sec > 0:
        sock.settimeout(timeout_sec)

    log("INFO", f"Multicast Receiver activ. Aștept datagrame pentru {group}:{port}...")

    accepted = 0
    try:
        while count == 0 or accepted < count:
            try:
                data, (sender_ip, sender_port) = sock.recvfrom(BUFFER_SIZE)
            except socket.timeout:
                log("WARN", f"Timeout după {timeout_sec}s. Oprire.")
                break

            text = data.decode("utf-8", errors="replace")
            accepted += 1
            log("RECV", f"{len(data):4d} bytes de la {sender_ip}:{sender_port} → {text!r}")

    except KeyboardInterrupt:
        log("INFO", "Întrerupt de utilizator.")
    finally:
        # ─────────────────────────────────────────────────────────────────────
        # LEAVE din grup (opțional - kernelul face asta la close())
        # Trimite IGMP Leave Group
        # ─────────────────────────────────────────────────────────────────────
        try:
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_DROP_MEMBERSHIP, mreq)
            log("INFO", f"LEAVE grup {group}")
        except OSError:
            pass
        sock.close()
        log("INFO", f"Socket închis. Primite: {accepted} datagrame.")

    return 0


# ════════════════════════════════════════════════════════════════════════════
#  PARSER ARGUMENTE
# ════════════════════════════════════════════════════════════════════════════

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ex02_udp_multicast.py",
        description="UDP Multicast sender/receiver cu JOIN/LEAVE grup.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemple:
  # Receiver cu JOIN la grup 239.1.1.1:
  python3 ex02_udp_multicast.py recv --group 239.1.1.1 --port 5001 --count 5

  # Sender către grup multicast:
  python3 ex02_udp_multicast.py send --group 239.1.1.1 --port 5001 --count 5 --ttl 1

  # Verificare membership pe interfață:
  ip maddr show dev eth0
        """
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # Sender
    ps = subparsers.add_parser("send", help="Trimite datagrame către grup multicast")
    ps.add_argument("--group", default=DEFAULT_GROUP, help=f"Adresa grupului multicast (default: {DEFAULT_GROUP})")
    ps.add_argument("--port", type=int, default=DEFAULT_PORT, help=f"Port destinație (default: {DEFAULT_PORT})")
    ps.add_argument("--message", default=DEFAULT_MESSAGE, help="Mesaj de trimis")
    ps.add_argument("--interval", type=float, default=1.0, help="Interval între mesaje (secunde)")
    ps.add_argument("--count", type=int, default=0, help="Număr de mesaje (0=infinit)")
    ps.add_argument("--ttl", type=int, default=DEFAULT_TTL, help=f"TTL multicast (default: {DEFAULT_TTL})")
    ps.add_argument("--iface", default="", help="IP interfață de ieșire (opțional)")
    ps.add_argument("--no-loopback", action="store_true", help="Dezactivează loopback local")
    ps.set_defaults(func=cmd_send)

    # Receiver
    pr = subparsers.add_parser("recv", help="Primește datagrame multicast (cu JOIN)")
    pr.add_argument("--group", default=DEFAULT_GROUP, help="Grupa multicast la care face JOIN")
    pr.add_argument("--port", type=int, default=DEFAULT_PORT, help="Port pe care ascultă")
    pr.add_argument("--count", type=int, default=0, help="Număr de mesaje de primit (0=infinit)")
    pr.add_argument("--iface", default="", help="IP interfață pentru JOIN (opțional)")
    pr.add_argument("--timeout", type=float, default=0.0, help="Timeout recvfrom (0=infinit)")
    pr.add_argument("--bind-group", action="store_true", help="Bind pe adresa grupului (nu pe '')")
    pr.set_defaults(func=cmd_recv)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
