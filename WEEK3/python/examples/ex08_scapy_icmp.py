#!/usr/bin/env python3
"""
================================================================================
EX08: RAW SOCKETS ȘI SCAPY - MANIPULARE ICMP
================================================================================
Demonstrează utilizarea RAW sockets și bibliotecii Scapy pentru:
  - Construirea manuală a pachetelor ICMP (Echo Request/Reply)
  - Interceptarea și analiza traficului la nivel de pachete
  - Implementarea unui "ping" custom fără utilitarul sistem
  - Traceroute simplificat folosind TTL manipulation

CONCEPTE FUNDAMENTALE:
  - RAW sockets permit acces direct la nivelurile inferioare ale stivei TCP/IP
  - Scapy abstractizează complexitatea construirii/parsării pachetelor
  - ICMP (Internet Control Message Protocol) - mesaje de diagnostic în rețea
  - TTL (Time To Live) - limitează propagarea pachetelor, esențial pentru traceroute

CERINȚE:
  - Python 3.8+
  - Scapy: pip install scapy --break-system-packages
  - Privilegii root/sudo (RAW sockets necesită acces privilegiat)

UTILIZARE:
  sudo python3 ex08_scapy_icmp.py --help
  sudo python3 ex08_scapy_icmp.py ping 8.8.8.8
  sudo python3 ex08_scapy_icmp.py traceroute 8.8.8.8
  sudo python3 ex08_scapy_icmp.py sniff --count 10
  sudo python3 ex08_scapy_icmp.py craft --dest 192.168.1.1 --ttl 64

STRUCTURA PACHET ICMP Echo:
  ┌─────────────────────────────────────────────────────────────┐
  │ IP Header (20 bytes minim)                                 │
  │ ┌─────────┬─────────┬──────────────────────────────────────┤
  │ │ Version │   IHL   │  Type of Service │  Total Length    │
  │ │  (4b)   │  (4b)   │     (8 bits)     │   (16 bits)      │
  │ ├─────────┴─────────┼──────────────────┴──────────────────┤
  │ │  Identification   │ Flags │   Fragment Offset           │
  │ │    (16 bits)      │ (3b)  │       (13 bits)             │
  │ ├───────────────────┼───────┴─────────────────────────────┤
  │ │  TTL (8 bits)     │ Protocol │  Header Checksum         │
  │ ├───────────────────┴──────────┴──────────────────────────┤
  │ │            Source IP Address (32 bits)                  │
  │ ├─────────────────────────────────────────────────────────┤
  │ │         Destination IP Address (32 bits)                │
  │ └─────────────────────────────────────────────────────────┘
  │ ICMP Header (8 bytes)                                      │
  │ ┌─────────────────┬─────────────────┬─────────────────────┤
  │ │  Type (8 bits)  │  Code (8 bits)  │  Checksum (16 bits) │
  │ ├─────────────────┴─────────────────┴─────────────────────┤
  │ │  Identifier (16 bits)  │  Sequence Number (16 bits)     │
  │ ├─────────────────────────────────────────────────────────┤
  │ │                   Payload (variable)                    │
  │ └─────────────────────────────────────────────────────────┘

TIPURI ICMP COMUNE:
  Type 0:  Echo Reply
  Type 3:  Destination Unreachable
  Type 5:  Redirect
  Type 8:  Echo Request
  Type 11: Time Exceeded (TTL expired - folosit în traceroute)

AUTOR: Starter Kit S3 - Rețele de Calculatoare ASE-CSIE
================================================================================
"""

import sys
import os
import argparse
import time
import struct
import socket
from datetime import datetime
from typing import Optional, List, Tuple

# =============================================================================
# VERIFICARE ȘI IMPORT SCAPY
# =============================================================================

try:
    from scapy.all import (
        IP, ICMP, TCP, UDP, Raw, Ether,
        sr1, sr, send, sniff,
        conf, get_if_addr, get_if_list,
        ICMP_TYPES, ICMP_CODES
    )
    from scapy.layers.inet import traceroute as scapy_traceroute
    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False
    print("=" * 70)
    print("EROARE: Scapy nu este instalat!")
    print("Instalare: sudo pip3 install scapy --break-system-packages")
    print("=" * 70)


# =============================================================================
# CONSTANTE ȘI CONFIGURARE
# =============================================================================

# Tipuri ICMP
ICMP_ECHO_REQUEST = 8
ICMP_ECHO_REPLY = 0
ICMP_TIME_EXCEEDED = 11
ICMP_DEST_UNREACHABLE = 3

# Configurare implicită
DEFAULT_TIMEOUT = 2.0  # secunde
DEFAULT_TTL = 64
DEFAULT_PAYLOAD = b"S3-SCAPY-PING"
MAX_HOPS = 30  # pentru traceroute


# =============================================================================
# FUNCȚII AUXILIARE
# =============================================================================

def check_root() -> bool:
    """
    Verifică dacă scriptul rulează cu privilegii root.
    RAW sockets necesită acces privilegiat pe majoritatea sistemelor.
    """
    return os.geteuid() == 0


def get_timestamp() -> str:
    """Timestamp formatat pentru logging."""
    return datetime.now().strftime("%H:%M:%S.%f")[:-3]


def resolve_hostname(host: str) -> Optional[str]:
    """
    Rezolvă hostname în adresă IP.
    Returnează None dacă rezoluția eșuează.
    """
    try:
        return socket.gethostbyname(host)
    except socket.gaierror as e:
        print(f"[EROARE] Nu pot rezolva hostname-ul '{host}': {e}")
        return None


def format_ip_header(packet: 'IP') -> str:
    """
    Formatează header-ul IP pentru afișare lizibilă.
    Extrage câmpurile relevante din pachetul Scapy.
    """
    lines = [
        f"  ├── Version: {packet.version}",
        f"  ├── IHL: {packet.ihl} ({packet.ihl * 4} bytes)",
        f"  ├── TOS: {packet.tos}",
        f"  ├── Total Length: {packet.len}",
        f"  ├── ID: {packet.id}",
        f"  ├── Flags: {packet.flags}",
        f"  ├── Fragment Offset: {packet.frag}",
        f"  ├── TTL: {packet.ttl}",
        f"  ├── Protocol: {packet.proto}",
        f"  ├── Checksum: {hex(packet.chksum) if packet.chksum else 'auto'}",
        f"  ├── Source: {packet.src}",
        f"  └── Destination: {packet.dst}"
    ]
    return "\n".join(lines)


def format_icmp_header(icmp: 'ICMP') -> str:
    """
    Formatează header-ul ICMP pentru afișare lizibilă.
    Include descriere pentru tipurile comune.
    """
    type_desc = {
        0: "Echo Reply",
        3: "Destination Unreachable",
        5: "Redirect",
        8: "Echo Request",
        11: "Time Exceeded"
    }
    desc = type_desc.get(icmp.type, "Unknown")
    
    lines = [
        f"  ├── Type: {icmp.type} ({desc})",
        f"  ├── Code: {icmp.code}",
        f"  ├── Checksum: {hex(icmp.chksum) if icmp.chksum else 'auto'}",
        f"  ├── ID: {icmp.id}",
        f"  └── Sequence: {icmp.seq}"
    ]
    return "\n".join(lines)


# =============================================================================
# PING CUSTOM CU SCAPY
# =============================================================================

def custom_ping(
    dest: str,
    count: int = 4,
    timeout: float = DEFAULT_TIMEOUT,
    ttl: int = DEFAULT_TTL,
    payload: bytes = DEFAULT_PAYLOAD,
    verbose: bool = True
) -> Tuple[int, int, List[float]]:
    """
    Implementare ping custom folosind Scapy.
    
    Construiește manual pachete ICMP Echo Request și analizează răspunsurile.
    Demonstrează funcționarea protocolului ICMP la nivel de pachet.
    
    Args:
        dest: Adresa IP sau hostname destinație
        count: Număr de pachete de trimis
        timeout: Timeout pentru fiecare pachet (secunde)
        ttl: Time To Live pentru pachetele IP
        payload: Date incluse în payload ICMP
        verbose: Afișează detalii pentru fiecare pachet
        
    Returns:
        Tuple (pachete_trimise, pachete_primite, lista_rtt)
    """
    # Rezolvă hostname
    ip = resolve_hostname(dest)
    if not ip:
        return (0, 0, [])
    
    print("=" * 70)
    print(f"PING {dest} ({ip}) - {len(payload)} bytes payload")
    print("=" * 70)
    
    sent = 0
    received = 0
    rtts: List[float] = []
    
    # Dezactivează output verbose Scapy
    conf.verb = 0
    
    for seq in range(1, count + 1):
        # Construiește pachetul IP/ICMP
        # IP() - creează header IP cu câmpurile specificate
        # ICMP() - creează header ICMP Echo Request
        # Raw() - adaugă payload
        packet = IP(dst=ip, ttl=ttl) / ICMP(type=8, code=0, id=os.getpid() & 0xFFFF, seq=seq) / Raw(load=payload)
        
        if verbose:
            print(f"\n[{get_timestamp()}] Trimit pachet #{seq}...")
            print(f"  Destinație: {ip}, TTL: {ttl}, Seq: {seq}")
        
        # Măsoară RTT
        start_time = time.time()
        sent += 1
        
        # sr1() - Send and Receive 1 packet
        # Trimite pachetul și așteaptă un singur răspuns
        reply = sr1(packet, timeout=timeout, verbose=0)
        
        if reply is None:
            print(f"  [TIMEOUT] Niciun răspuns pentru #{seq}")
            continue
            
        rtt = (time.time() - start_time) * 1000  # conversie la ms
        
        # Verifică tipul răspunsului
        if reply.haslayer(ICMP):
            icmp_layer = reply.getlayer(ICMP)
            
            if icmp_layer.type == ICMP_ECHO_REPLY:
                # Echo Reply - ping reușit
                received += 1
                rtts.append(rtt)
                
                if verbose:
                    print(f"  [RĂSPUNS] de la {reply.src}")
                    print(f"    TTL: {reply.ttl}, RTT: {rtt:.2f} ms")
                    print(f"    ICMP Type: {icmp_layer.type} (Echo Reply)")
                    print(f"    ICMP Seq: {icmp_layer.seq}, ID: {icmp_layer.id}")
                else:
                    print(f"{len(payload)} bytes de la {reply.src}: "
                          f"icmp_seq={seq} ttl={reply.ttl} time={rtt:.2f} ms")
                    
            elif icmp_layer.type == ICMP_TIME_EXCEEDED:
                print(f"  [TTL EXPIRAT] de la {reply.src} - TTL prea mic")
                
            elif icmp_layer.type == ICMP_DEST_UNREACHABLE:
                codes = {
                    0: "Network Unreachable",
                    1: "Host Unreachable",
                    2: "Protocol Unreachable",
                    3: "Port Unreachable",
                    4: "Fragmentation Needed",
                    13: "Administratively Prohibited"
                }
                code_desc = codes.get(icmp_layer.code, "Unknown")
                print(f"  [DEST UNREACHABLE] {code_desc} de la {reply.src}")
                
        else:
            print(f"  [RĂSPUNS NEAȘTEPTAT] Tip pachet: {reply.summary()}")
    
    # Statistici finale
    print("\n" + "=" * 70)
    print(f"--- Statistici ping {dest} ---")
    loss = ((sent - received) / sent * 100) if sent > 0 else 100
    print(f"Pachete: trimise={sent}, primite={received}, pierdute={sent-received} ({loss:.1f}% loss)")
    
    if rtts:
        avg_rtt = sum(rtts) / len(rtts)
        min_rtt = min(rtts)
        max_rtt = max(rtts)
        print(f"RTT ms: min={min_rtt:.2f}, avg={avg_rtt:.2f}, max={max_rtt:.2f}")
    
    print("=" * 70)
    
    return (sent, received, rtts)


# =============================================================================
# TRACEROUTE CUSTOM CU SCAPY
# =============================================================================

def custom_traceroute(
    dest: str,
    max_hops: int = MAX_HOPS,
    timeout: float = DEFAULT_TIMEOUT,
    verbose: bool = True
) -> List[Tuple[int, str, float]]:
    """
    Implementare traceroute custom folosind Scapy.
    
    Principiu: Trimite pachete ICMP cu TTL crescător (1, 2, 3...).
    Fiecare router care primește un pachet cu TTL=1 îl decrementează la 0
    și trimite înapoi un mesaj ICMP Time Exceeded, revelând adresa sa.
    
    Args:
        dest: Adresa IP sau hostname destinație
        max_hops: Număr maxim de hop-uri de explorat
        timeout: Timeout pentru fiecare hop (secunde)
        verbose: Afișează detalii extinse
        
    Returns:
        Lista de tuple (hop_number, ip_address, rtt_ms)
    """
    # Rezolvă hostname
    ip = resolve_hostname(dest)
    if not ip:
        return []
    
    print("=" * 70)
    print(f"TRACEROUTE către {dest} ({ip}), max {max_hops} hops")
    print("=" * 70)
    
    route: List[Tuple[int, str, float]] = []
    conf.verb = 0
    
    for ttl in range(1, max_hops + 1):
        # Construiește pachet cu TTL specific
        packet = IP(dst=ip, ttl=ttl) / ICMP(type=8, code=0, id=os.getpid() & 0xFFFF, seq=ttl)
        
        start_time = time.time()
        reply = sr1(packet, timeout=timeout, verbose=0)
        rtt = (time.time() - start_time) * 1000
        
        if reply is None:
            print(f" {ttl:2d}  *  *  *  (timeout)")
            route.append((ttl, "*", -1))
            continue
            
        hop_ip = reply.src
        
        # Încearcă reverse DNS
        try:
            hostname = socket.gethostbyaddr(hop_ip)[0]
            display = f"{hostname} ({hop_ip})"
        except socket.herror:
            display = hop_ip
        
        route.append((ttl, hop_ip, rtt))
        
        if reply.haslayer(ICMP):
            icmp_layer = reply.getlayer(ICMP)
            
            if icmp_layer.type == ICMP_ECHO_REPLY:
                # Am ajuns la destinație
                print(f" {ttl:2d}  {display}  {rtt:.2f} ms [DESTINAȚIE]")
                print("\n" + "=" * 70)
                print(f"Ruta completă către {dest}: {ttl} hop(s)")
                print("=" * 70)
                break
                
            elif icmp_layer.type == ICMP_TIME_EXCEEDED:
                # Router intermediar
                print(f" {ttl:2d}  {display}  {rtt:.2f} ms")
                
            elif icmp_layer.type == ICMP_DEST_UNREACHABLE:
                print(f" {ttl:2d}  {display}  {rtt:.2f} ms [UNREACHABLE]")
                break
    else:
        print(f"\nNu am ajuns la destinație în {max_hops} hops")
    
    return route


# =============================================================================
# SNIFFER DE PACHETE
# =============================================================================

def packet_callback(packet, verbose: bool = True):
    """
    Callback pentru procesarea pachetelor capturate.
    Afișează informații structurate despre fiecare pachet.
    """
    timestamp = get_timestamp()
    
    if packet.haslayer(IP):
        ip = packet.getlayer(IP)
        
        if packet.haslayer(ICMP):
            icmp = packet.getlayer(ICMP)
            type_names = {0: "Reply", 8: "Request", 11: "TimeExceeded", 3: "Unreachable"}
            icmp_type = type_names.get(icmp.type, f"Type{icmp.type}")
            
            print(f"[{timestamp}] ICMP {icmp_type}: {ip.src} → {ip.dst} "
                  f"(TTL={ip.ttl}, ID={icmp.id}, Seq={icmp.seq})")
            
            if verbose:
                print(f"  └── Checksum: {hex(icmp.chksum)}, Length: {ip.len} bytes")
                
        elif packet.haslayer(TCP):
            tcp = packet.getlayer(TCP)
            flags = str(tcp.flags)
            print(f"[{timestamp}] TCP: {ip.src}:{tcp.sport} → {ip.dst}:{tcp.dport} "
                  f"[{flags}] (TTL={ip.ttl})")
            
        elif packet.haslayer(UDP):
            udp = packet.getlayer(UDP)
            print(f"[{timestamp}] UDP: {ip.src}:{udp.sport} → {ip.dst}:{udp.dport} "
                  f"(TTL={ip.ttl}, Len={udp.len})")
        else:
            print(f"[{timestamp}] IP: {ip.src} → {ip.dst} (Proto={ip.proto}, TTL={ip.ttl})")


def sniff_packets(
    count: int = 10,
    filter_str: str = "icmp",
    iface: Optional[str] = None,
    timeout: Optional[float] = None
) -> int:
    """
    Capturează și analizează pachete de rețea.
    
    Args:
        count: Număr de pachete de capturat (0 = infinit)
        filter_str: Filtru BPF (ex: "icmp", "tcp port 80", "udp")
        iface: Interfața de rețea (None = toate)
        timeout: Timeout pentru capturare (secunde)
        
    Returns:
        Număr de pachete capturate
    """
    print("=" * 70)
    print(f"PACKET SNIFFER - Capturez pachete")
    print(f"  Filtru: {filter_str}")
    print(f"  Interfață: {iface or 'toate'}")
    print(f"  Count: {count if count > 0 else 'infinit'}")
    print("  Ctrl+C pentru a opri")
    print("=" * 70 + "\n")
    
    conf.verb = 0
    
    try:
        packets = sniff(
            filter=filter_str,
            prn=packet_callback,
            count=count if count > 0 else 0,
            iface=iface,
            timeout=timeout
        )
        
        print(f"\n{'=' * 70}")
        print(f"Capturate {len(packets)} pachete")
        print("=" * 70)
        
        return len(packets)
        
    except KeyboardInterrupt:
        print("\n\nCapturare oprită de utilizator")
        return 0


# =============================================================================
# CONSTRUIRE MANUALĂ PACHETE
# =============================================================================

def craft_custom_packet(
    dest: str,
    src: Optional[str] = None,
    ttl: int = DEFAULT_TTL,
    payload: bytes = DEFAULT_PAYLOAD,
    icmp_type: int = 8,
    icmp_code: int = 0,
    show_details: bool = True
) -> Optional['IP']:
    """
    Construiește manual un pachet IP/ICMP.
    Demonstrează structura internă a pachetelor.
    
    Args:
        dest: Adresa IP destinație
        src: Adresa IP sursă (None = auto)
        ttl: Time To Live
        payload: Date în payload
        icmp_type: Tip ICMP (8=Echo Request, 0=Echo Reply)
        icmp_code: Cod ICMP
        show_details: Afișează structura pachetului
        
    Returns:
        Obiect pachet Scapy sau None în caz de eroare
    """
    ip = resolve_hostname(dest)
    if not ip:
        return None
    
    # Construiește straturile pachetului
    ip_layer = IP(
        dst=ip,
        ttl=ttl,
        id=os.getpid() & 0xFFFF
    )
    
    if src:
        ip_layer.src = src
    
    icmp_layer = ICMP(
        type=icmp_type,
        code=icmp_code,
        id=os.getpid() & 0xFFFF,
        seq=1
    )
    
    payload_layer = Raw(load=payload)
    
    # Asamblează pachetul
    packet = ip_layer / icmp_layer / payload_layer
    
    if show_details:
        print("=" * 70)
        print("PACHET CUSTOM CONSTRUIT")
        print("=" * 70)
        
        print("\n[IP HEADER]")
        # Calculează checksum pentru afișare
        packet = IP(bytes(packet))  # Reconstruiește pentru a calcula checksum-uri
        print(format_ip_header(packet))
        
        print("\n[ICMP HEADER]")
        print(format_icmp_header(packet.getlayer(ICMP)))
        
        print("\n[PAYLOAD]")
        print(f"  └── {payload} ({len(payload)} bytes)")
        
        print("\n[REZUMAT SCAPY]")
        print(f"  {packet.summary()}")
        
        print("\n[BYTES RAW]")
        raw_bytes = bytes(packet)
        hex_display = " ".join(f"{b:02x}" for b in raw_bytes[:48])
        print(f"  {hex_display}...")
        print(f"  (total {len(raw_bytes)} bytes)")
        
        print("=" * 70)
    
    return packet


def send_custom_packet(packet: 'IP', wait_reply: bool = True, timeout: float = DEFAULT_TIMEOUT):
    """
    Trimite un pachet custom și opțional așteaptă răspuns.
    """
    print(f"\n[TRIMITERE] Pachet către {packet.dst}...")
    
    if wait_reply:
        reply = sr1(packet, timeout=timeout, verbose=0)
        
        if reply:
            print(f"[RĂSPUNS PRIMIT]")
            print(f"  De la: {reply.src}")
            
            if reply.haslayer(ICMP):
                icmp = reply.getlayer(ICMP)
                print(f"  ICMP Type: {icmp.type}, Code: {icmp.code}")
            
            return reply
        else:
            print("[TIMEOUT] Niciun răspuns primit")
            return None
    else:
        send(packet, verbose=0)
        print("[TRIMIS] Pachet expediat (fără așteptare răspuns)")
        return None


# =============================================================================
# INTERFAȚĂ LINIE DE COMANDĂ
# =============================================================================

def create_parser() -> argparse.ArgumentParser:
    """Creează parser-ul pentru argumentele liniei de comandă."""
    parser = argparse.ArgumentParser(
        description="EX08: RAW Sockets și Scapy - Manipulare ICMP",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXEMPLE:
  sudo python3 ex08_scapy_icmp.py ping 8.8.8.8
  sudo python3 ex08_scapy_icmp.py ping google.com -c 10 --ttl 32
  sudo python3 ex08_scapy_icmp.py traceroute 8.8.8.8 --max-hops 15
  sudo python3 ex08_scapy_icmp.py sniff --filter "icmp" --count 20
  sudo python3 ex08_scapy_icmp.py craft --dest 192.168.1.1 --ttl 64

NOTE:
  - Necesită privilegii root (sudo)
  - Scapy trebuie instalat: pip3 install scapy --break-system-packages
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Comandă disponibilă")
    
    # Subcomandă: ping
    ping_parser = subparsers.add_parser("ping", help="Ping custom cu Scapy")
    ping_parser.add_argument("target", help="Adresa IP sau hostname")
    ping_parser.add_argument("-c", "--count", type=int, default=4, help="Număr pachete (default: 4)")
    ping_parser.add_argument("-t", "--timeout", type=float, default=2.0, help="Timeout per pachet (default: 2.0s)")
    ping_parser.add_argument("--ttl", type=int, default=64, help="TTL pentru pachete (default: 64)")
    ping_parser.add_argument("-v", "--verbose", action="store_true", help="Output detaliat")
    
    # Subcomandă: traceroute
    trace_parser = subparsers.add_parser("traceroute", help="Traceroute custom cu Scapy")
    trace_parser.add_argument("target", help="Adresa IP sau hostname")
    trace_parser.add_argument("--max-hops", type=int, default=30, help="Număr maxim hops (default: 30)")
    trace_parser.add_argument("-t", "--timeout", type=float, default=2.0, help="Timeout per hop (default: 2.0s)")
    
    # Subcomandă: sniff
    sniff_parser = subparsers.add_parser("sniff", help="Capturare pachete")
    sniff_parser.add_argument("-c", "--count", type=int, default=10, help="Număr pachete (default: 10, 0=infinit)")
    sniff_parser.add_argument("-f", "--filter", type=str, default="icmp", help="Filtru BPF (default: icmp)")
    sniff_parser.add_argument("-i", "--interface", type=str, help="Interfață rețea")
    sniff_parser.add_argument("-t", "--timeout", type=float, help="Timeout capturare")
    
    # Subcomandă: craft
    craft_parser = subparsers.add_parser("craft", help="Construiește pachet custom")
    craft_parser.add_argument("--dest", "-d", required=True, help="Adresa IP destinație")
    craft_parser.add_argument("--src", "-s", help="Adresa IP sursă (opțional)")
    craft_parser.add_argument("--ttl", type=int, default=64, help="TTL (default: 64)")
    craft_parser.add_argument("--type", type=int, default=8, help="Tip ICMP (default: 8=Echo Request)")
    craft_parser.add_argument("--code", type=int, default=0, help="Cod ICMP (default: 0)")
    craft_parser.add_argument("--send", action="store_true", help="Trimite pachetul")
    
    # Subcomandă: info
    info_parser = subparsers.add_parser("info", help="Informații despre interfețe")
    
    return parser


def show_network_info():
    """Afișează informații despre interfețele de rețea."""
    print("=" * 70)
    print("INFORMAȚII REȚEA")
    print("=" * 70)
    
    print("\n[INTERFEȚE DISPONIBILE]")
    for iface in get_if_list():
        try:
            addr = get_if_addr(iface)
            print(f"  {iface}: {addr}")
        except Exception:
            print(f"  {iface}: (nu pot obține adresa)")
    
    print("\n[TIPURI ICMP CUNOSCUTE]")
    for code, name in sorted(ICMP_TYPES.items()):
        print(f"  {code:2d}: {name}")
    
    print("=" * 70)


# =============================================================================
# MAIN
# =============================================================================

def main():
    """Punct de intrare principal."""
    # Verifică disponibilitatea Scapy
    if not SCAPY_AVAILABLE:
        sys.exit(1)
    
    # Verifică privilegii root
    if not check_root():
        print("=" * 70)
        print("AVERTIZARE: Acest script necesită privilegii root!")
        print("Rulați cu: sudo python3 ex08_scapy_icmp.py ...")
        print("=" * 70)
        sys.exit(1)
    
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        print("\n" + "=" * 70)
        print("DEMO RAPID: Ping local")
        print("=" * 70)
        custom_ping("127.0.0.1", count=2, verbose=True)
        sys.exit(0)
    
    if args.command == "ping":
        custom_ping(
            args.target,
            count=args.count,
            timeout=args.timeout,
            ttl=args.ttl,
            verbose=args.verbose
        )
        
    elif args.command == "traceroute":
        custom_traceroute(
            args.target,
            max_hops=args.max_hops,
            timeout=args.timeout
        )
        
    elif args.command == "sniff":
        sniff_packets(
            count=args.count,
            filter_str=args.filter,
            iface=args.interface,
            timeout=args.timeout
        )
        
    elif args.command == "craft":
        packet = craft_custom_packet(
            dest=args.dest,
            src=args.src,
            ttl=args.ttl,
            icmp_type=args.type,
            icmp_code=args.code
        )
        
        if packet and args.send:
            send_custom_packet(packet)
            
    elif args.command == "info":
        show_network_info()


if __name__ == "__main__":
    main()
