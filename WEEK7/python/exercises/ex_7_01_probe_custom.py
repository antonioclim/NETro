#!/usr/bin/env python3
"""
Exercițiul 7.01: Sondă TCP/UDP personalizată
============================================
Rețele de Calculatoare — Săptămâna 7
ASE București

Obiective:
- Să implementezi funcții de sondare TCP și UDP
- Să interpretezi corect diferențele: timeout vs refused vs open
- Să combini rezultatele într-un raport structurat

Nivel: Intermediar
Timp estimat: 20 minute (25 min în perechi)

Instrucțiuni:
- Completează funcțiile marcate cu TODO
- Testează cu: python3 ex_7_01_probe_custom.py --host 10.0.7.200
- Compară rezultatele cu output-ul lui nmap sau nc
"""

from __future__ import annotations

# ═══════════════════════════════════════════════════════════════════════════════
# SETUP_ENVIRONMENT — importuri și constante
# ═══════════════════════════════════════════════════════════════════════════════

import argparse
import socket
import time
from typing import List, Tuple

DEFAULT_TIMEOUT = 1.0
TCP_PORTS = [22, 80, 443, 9090]
UDP_PORTS = [53, 9091]


# ═══════════════════════════════════════════════════════════════════════════════
# PARSE_ARGUMENTS — configurare CLI
# ═══════════════════════════════════════════════════════════════════════════════

def build_parser() -> argparse.ArgumentParser:
    """Construiește parser-ul pentru argumente CLI."""
    p = argparse.ArgumentParser(
        description="Sondă TCP/UDP pentru laborator (Săptămâna 7)"
    )
    p.add_argument("--host", required=True, help="IP-ul sau hostname-ul țintă")
    p.add_argument(
        "--timeout",
        type=float,
        default=DEFAULT_TIMEOUT,
        help=f"Timeout per probă în secunde (implicit: {DEFAULT_TIMEOUT})"
    )
    p.add_argument(
        "--tcp-ports",
        default=",".join(map(str, TCP_PORTS)),
        help=f"Porturi TCP de sondat, separate prin virgulă (implicit: {TCP_PORTS})"
    )
    p.add_argument(
        "--udp-ports",
        default=",".join(map(str, UDP_PORTS)),
        help=f"Porturi UDP de sondat, separate prin virgulă (implicit: {UDP_PORTS})"
    )
    return p


def parse_ports(spec: str) -> List[int]:
    """Parsează o listă de porturi din string (ex: '22,80,443')."""
    if not spec.strip():
        return []
    return [int(p.strip()) for p in spec.split(",") if p.strip()]


# ═══════════════════════════════════════════════════════════════════════════════
# PROBE_TCP — sondare un port TCP
# ═══════════════════════════════════════════════════════════════════════════════

def probe_tcp(host: str, port: int, timeout: float) -> str:
    """
    Sondează un port TCP folosind connect().
    
    Returnează:
    - "open" dacă connect() reușește (serverul acceptă conexiuni)
    - "closed" dacă primești ConnectionRefusedError (port închis, RST primit)
    - "filtered" dacă primești timeout (probabil DROP pe firewall)
    - "error: <mesaj>" pentru alte erori
    
    TODO: Completează implementarea.
    
    Hints:
    - Creează socket cu AF_INET și SOCK_STREAM
    - Setează timeout înainte de connect
    - Folosește try/except pentru fiecare caz
    - Nu uita să închizi socket-ul în finally
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    
    try:
        # TODO: Încearcă să te conectezi la (host, port)
        # Hint: sock.connect((host, port))
        
        # Dacă ajungi aici, conexiunea a reușit
        return "open"
    
    except ConnectionRefusedError:
        # Serverul a trimis RST — portul e închis
        return "closed"
    
    except socket.timeout:
        # Niciun răspuns — probabil firewall DROP
        return "filtered"
    
    except OSError as e:
        # Alte erori de rețea (host unreachable, network down, etc.)
        return f"error: {e}"
    
    finally:
        # Închide socket-ul indiferent de rezultat
        try:
            sock.close()
        except Exception:
            pass


# ═══════════════════════════════════════════════════════════════════════════════
# PROBE_UDP — sondare un port UDP
# ═══════════════════════════════════════════════════════════════════════════════

def probe_udp(host: str, port: int, timeout: float) -> str:
    """
    Sondează un port UDP.
    
    UDP e mai complicat decât TCP pentru că nu există handshake.
    - Dacă trimitem un pachet și primim răspuns → "open"
    - Dacă primim ICMP port unreachable → "closed"
    - Dacă nu primim nimic → "open|filtered" (nu putem ști sigur)
    
    Returnează:
    - "open" dacă primim date înapoi
    - "open|filtered" dacă timeout (nu știm dacă e deschis sau filtrat)
    - "closed" dacă primim eroare ICMP (rar, depinde de SO)
    - "error: <mesaj>" pentru alte erori
    
    TODO: Completează implementarea.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(timeout)
    
    try:
        # TODO: Trimite un pachet simplu
        # Hint: sock.sendto(b"probe", (host, port))
        
        # TODO: Încearcă să primești răspuns
        # Hint: data, addr = sock.recvfrom(1024)
        
        # Dacă am primit date, portul e deschis și serviciul răspunde
        return "open"
    
    except socket.timeout:
        # Nu am primit nimic — nu putem ști sigur
        # Poate e deschis dar serviciul nu răspunde la probe-ul nostru
        # Poate e filtrat (DROP)
        return "open|filtered"
    
    except ConnectionRefusedError:
        # Unele sisteme trimit ICMP port unreachable ca ConnectionRefused
        return "closed"
    
    except OSError as e:
        return f"error: {e}"
    
    finally:
        try:
            sock.close()
        except Exception:
            pass


# ═══════════════════════════════════════════════════════════════════════════════
# RUN_SCAN — orchestrare scanare
# ═══════════════════════════════════════════════════════════════════════════════

def run_scan(
    host: str,
    tcp_ports: List[int],
    udp_ports: List[int],
    timeout: float
) -> Tuple[List[Tuple[int, str]], List[Tuple[int, str]]]:
    """
    Rulează sondarea pe toate porturile specificate.
    
    Returnează două liste de tupluri (port, status).
    """
    tcp_results = []
    udp_results = []
    
    # Sondare TCP
    for port in tcp_ports:
        status = probe_tcp(host, port, timeout)
        tcp_results.append((port, status))
    
    # Sondare UDP
    for port in udp_ports:
        status = probe_udp(host, port, timeout)
        udp_results.append((port, status))
    
    return tcp_results, udp_results


# ═══════════════════════════════════════════════════════════════════════════════
# GENERATE_REPORT — afișare rezultate
# ═══════════════════════════════════════════════════════════════════════════════

def generate_report(
    host: str,
    tcp_results: List[Tuple[int, str]],
    udp_results: List[Tuple[int, str]],
    duration: float
) -> None:
    """Afișează raportul în format tabelar."""
    print(f"\n{'='*50}")
    print(f"Raport sondare pentru {host}")
    print(f"{'='*50}")
    
    if tcp_results:
        print("\nTCP:")
        print(f"  {'Port':<8} {'Status':<20}")
        print(f"  {'-'*8} {'-'*20}")
        for port, status in tcp_results:
            # Highlight pentru porturi deschise
            marker = " *" if status == "open" else ""
            print(f"  {port:<8} {status:<20}{marker}")
    
    if udp_results:
        print("\nUDP:")
        print(f"  {'Port':<8} {'Status':<20}")
        print(f"  {'-'*8} {'-'*20}")
        for port, status in udp_results:
            marker = " *" if status == "open" else ""
            print(f"  {port:<8} {status:<20}{marker}")
    
    print(f"\nDurată: {duration:.2f}s")
    print(f"{'='*50}\n")


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN — punctul de intrare
# ═══════════════════════════════════════════════════════════════════════════════

def main() -> int:
    args = build_parser().parse_args()
    
    tcp_ports = parse_ports(args.tcp_ports)
    udp_ports = parse_ports(args.udp_ports)
    
    print(f"[probe] Țintă: {args.host}")
    print(f"[probe] TCP: {tcp_ports}")
    print(f"[probe] UDP: {udp_ports}")
    print(f"[probe] Timeout: {args.timeout}s")
    
    start = time.time()
    tcp_results, udp_results = run_scan(
        args.host,
        tcp_ports,
        udp_ports,
        args.timeout
    )
    duration = time.time() - start
    
    generate_report(args.host, tcp_results, udp_results, duration)
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
