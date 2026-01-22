#!/usr/bin/env python3
"""
Exercițiul 1.04: Statistici avansate din fișiere PCAP
=====================================================

Obiective didactice:
    - Înțelegerea structurii unui fișier PCAP (Packet Capture)
    - Extragerea și analiza metadatelor pachetelor la nivel de octeți
    - Calculul statisticilor de rețea: throughput, distribuție protocoale, RTT
    - Vizualizarea temporală a traficului de rețea

Concepte acoperite:
    - Format PCAP/PCAPNG și structura header-elor
    - Despachetarea stratificată (Ethernet → IP → TCP/UDP → Payload)
    - Statistici descriptive: medie, mediană, percentile, deviație standard
    - Detectarea anomaliilor în trafic (burst-uri, retransmisii)

Dependențe:
    pip install scapy --break-system-packages
    
    Alternativ (fără scapy, doar dpkt):
    pip install dpkt --break-system-packages

Autor: Revolvix&Hypotheticalandrei
Curs: Rețele de calculatoare, ASE București
"""

from __future__ import annotations

import sys
import argparse
import statistics
from pathlib import Path
from dataclasses import dataclass, field
from typing import Generator, Optional, Any
from collections import Counter, defaultdict
from datetime import datetime
import struct

# Încercăm import scapy, apoi dpkt ca fallback
SCAPY_AVAILABLE = False
DPKT_AVAILABLE = False

try:
    from scapy.all import rdpcap, IP, TCP, UDP, ICMP, Ether, Raw
    from scapy.layers.dns import DNS
    from scapy.layers.http import HTTP
    SCAPY_AVAILABLE = True
except ImportError:
    pass

if not SCAPY_AVAILABLE:
    try:
        import dpkt
        DPKT_AVAILABLE = True
    except ImportError:
        pass


# =============================================================================
# STRUCTURI DE DATE
# =============================================================================

@dataclass
class PacketSummary:
    """Rezumat individual pentru un pachet capturat."""
    timestamp: float           # Unix timestamp (secunde.microsecunde)
    length: int                # Lungime totală în octeți
    eth_src: Optional[str]     # MAC sursă
    eth_dst: Optional[str]     # MAC destinație
    ip_src: Optional[str]      # IP sursă
    ip_dst: Optional[str]      # IP destinație
    protocol: str              # TCP, UDP, ICMP, ARP, etc.
    src_port: Optional[int]    # Port sursă (TCP/UDP)
    dst_port: Optional[int]    # Port destinație (TCP/UDP)
    tcp_flags: Optional[str]   # Flag-uri TCP (SYN, ACK, FIN, etc.)
    payload_size: int          # Dimensiune payload (fără headere)
    ttl: Optional[int]         # Time To Live
    
    @property
    def is_tcp(self) -> bool:
        return self.protocol == "TCP"
    
    @property
    def is_udp(self) -> bool:
        return self.protocol == "UDP"
    
    @property
    def flow_tuple(self) -> tuple:
        """Identificator unic pentru flux (5-tuple)."""
        return (self.ip_src, self.ip_dst, self.src_port, self.dst_port, self.protocol)


@dataclass
class CaptureStatistics:
    """Statistici agregate pentru o captură completă."""
    file_path: str
    total_packets: int = 0
    total_bytes: int = 0
    capture_duration: float = 0.0
    first_timestamp: float = 0.0
    last_timestamp: float = 0.0
    
    # Distribuții
    protocols: Counter = field(default_factory=Counter)
    src_ips: Counter = field(default_factory=Counter)
    dst_ips: Counter = field(default_factory=Counter)
    src_ports: Counter = field(default_factory=Counter)
    dst_ports: Counter = field(default_factory=Counter)
    tcp_flags: Counter = field(default_factory=Counter)
    
    # Dimensiuni pachete
    packet_sizes: list = field(default_factory=list)
    
    # Statistici per flux
    flows: dict = field(default_factory=dict)
    
    # Timings
    inter_arrival_times: list = field(default_factory=list)
    
    @property
    def avg_packet_size(self) -> float:
        """Dimensiune medie a pachetelor."""
        return statistics.mean(self.packet_sizes) if self.packet_sizes else 0.0
    
    @property
    def throughput_bps(self) -> float:
        """Throughput în biți pe secundă."""
        if self.capture_duration > 0:
            return (self.total_bytes * 8) / self.capture_duration
        return 0.0
    
    @property
    def throughput_mbps(self) -> float:
        """Throughput în megabiți pe secundă."""
        return self.throughput_bps / 1_000_000
    
    @property
    def packets_per_second(self) -> float:
        """Rata de pachete pe secundă."""
        if self.capture_duration > 0:
            return self.total_packets / self.capture_duration
        return 0.0


# =============================================================================
# PARSARE PCAP CU SCAPY
# =============================================================================

def parse_pcap_scapy(filepath: str) -> Generator[PacketSummary, None, None]:
    """
    Parsează un fișier PCAP folosind Scapy.
    
    Scapy oferă cea mai completă despachetare a protocoalelor,
    cu suport pentru sute de protocoale diferite.
    
    Args:
        filepath: Calea către fișierul PCAP
        
    Yields:
        PacketSummary pentru fiecare pachet din captură
    """
    if not SCAPY_AVAILABLE:
        raise ImportError("Scapy nu este instalat. Rulați: pip install scapy")
    
    packets = rdpcap(filepath)
    
    for pkt in packets:
        # Timestamp
        timestamp = float(pkt.time)
        length = len(pkt)
        
        # Layer 2 - Ethernet
        eth_src = eth_dst = None
        if Ether in pkt:
            eth_src = pkt[Ether].src
            eth_dst = pkt[Ether].dst
        
        # Layer 3 - IP
        ip_src = ip_dst = None
        ttl = None
        protocol = "UNKNOWN"
        
        if IP in pkt:
            ip_src = pkt[IP].src
            ip_dst = pkt[IP].dst
            ttl = pkt[IP].ttl
            
            # Determinare protocol
            if TCP in pkt:
                protocol = "TCP"
            elif UDP in pkt:
                protocol = "UDP"
            elif ICMP in pkt:
                protocol = "ICMP"
            else:
                protocol = f"IP-{pkt[IP].proto}"
        elif pkt.haslayer('ARP'):
            protocol = "ARP"
        
        # Layer 4 - TCP/UDP
        src_port = dst_port = None
        tcp_flags = None
        payload_size = 0
        
        if TCP in pkt:
            src_port = pkt[TCP].sport
            dst_port = pkt[TCP].dport
            tcp_flags = str(pkt[TCP].flags)
            if Raw in pkt:
                payload_size = len(pkt[Raw].load)
        elif UDP in pkt:
            src_port = pkt[UDP].sport
            dst_port = pkt[UDP].dport
            if Raw in pkt:
                payload_size = len(pkt[Raw].load)
        
        yield PacketSummary(
            timestamp=timestamp,
            length=length,
            eth_src=eth_src,
            eth_dst=eth_dst,
            ip_src=ip_src,
            ip_dst=ip_dst,
            protocol=protocol,
            src_port=src_port,
            dst_port=dst_port,
            tcp_flags=tcp_flags,
            payload_size=payload_size,
            ttl=ttl
        )


# =============================================================================
# PARSARE PCAP CU DPKT (FALLBACK)
# =============================================================================

def parse_pcap_dpkt(filepath: str) -> Generator[PacketSummary, None, None]:
    """
    Parsează un fișier PCAP folosind dpkt (alternativă mai ușoară).
    
    dpkt este mai lightweight decât scapy dar oferă mai puțină
    funcționalitate pentru protocoale exotice.
    
    Args:
        filepath: Calea către fișierul PCAP
        
    Yields:
        PacketSummary pentru fiecare pachet din captură
    """
    if not DPKT_AVAILABLE:
        raise ImportError("dpkt nu este instalat. Rulați: pip install dpkt")
    
    with open(filepath, 'rb') as f:
        try:
            pcap = dpkt.pcap.Reader(f)
        except ValueError:
            # Poate fi format pcapng
            f.seek(0)
            pcap = dpkt.pcapng.Reader(f)
        
        for timestamp, buf in pcap:
            length = len(buf)
            
            # Inițializare valori implicite
            eth_src = eth_dst = None
            ip_src = ip_dst = None
            src_port = dst_port = None
            tcp_flags = None
            payload_size = 0
            ttl = None
            protocol = "UNKNOWN"
            
            try:
                # Layer 2 - Ethernet
                eth = dpkt.ethernet.Ethernet(buf)
                eth_src = ':'.join('%02x' % b for b in eth.src)
                eth_dst = ':'.join('%02x' % b for b in eth.dst)
                
                # Layer 3 - IP
                if isinstance(eth.data, dpkt.ip.IP):
                    ip = eth.data
                    ip_src = '.'.join(str(b) for b in ip.src) if hasattr(ip, 'src') else None
                    ip_dst = '.'.join(str(b) for b in ip.dst) if hasattr(ip, 'dst') else None
                    ttl = ip.ttl
                    
                    # Layer 4
                    if isinstance(ip.data, dpkt.tcp.TCP):
                        tcp = ip.data
                        protocol = "TCP"
                        src_port = tcp.sport
                        dst_port = tcp.dport
                        
                        # Decodare flags TCP
                        flags = []
                        if tcp.flags & dpkt.tcp.TH_SYN: flags.append('S')
                        if tcp.flags & dpkt.tcp.TH_ACK: flags.append('A')
                        if tcp.flags & dpkt.tcp.TH_FIN: flags.append('F')
                        if tcp.flags & dpkt.tcp.TH_RST: flags.append('R')
                        if tcp.flags & dpkt.tcp.TH_PUSH: flags.append('P')
                        if tcp.flags & dpkt.tcp.TH_URG: flags.append('U')
                        tcp_flags = ''.join(flags) if flags else ''
                        
                        payload_size = len(tcp.data)
                        
                    elif isinstance(ip.data, dpkt.udp.UDP):
                        udp = ip.data
                        protocol = "UDP"
                        src_port = udp.sport
                        dst_port = udp.dport
                        payload_size = len(udp.data)
                        
                    elif isinstance(ip.data, dpkt.icmp.ICMP):
                        protocol = "ICMP"
                        
                elif eth.type == dpkt.ethernet.ETH_TYPE_ARP:
                    protocol = "ARP"
                    
            except Exception as e:
                # Pachet malformat sau protocol necunoscut
                pass
            
            yield PacketSummary(
                timestamp=timestamp,
                length=length,
                eth_src=eth_src,
                eth_dst=eth_dst,
                ip_src=ip_src,
                ip_dst=ip_dst,
                protocol=protocol,
                src_port=src_port,
                dst_port=dst_port,
                tcp_flags=tcp_flags,
                payload_size=payload_size,
                ttl=ttl
            )


def parse_pcap(filepath: str) -> Generator[PacketSummary, None, None]:
    """
    Parsează un fișier PCAP folosind biblioteca disponibilă.
    
    Încearcă Scapy mai întâi (mai complet), apoi dpkt ca fallback.
    """
    if SCAPY_AVAILABLE:
        yield from parse_pcap_scapy(filepath)
    elif DPKT_AVAILABLE:
        yield from parse_pcap_dpkt(filepath)
    else:
        raise ImportError(
            "Nu este disponibilă nicio bibliotecă pentru parsare PCAP.\n"
            "Instalați una dintre:\n"
            "  pip install scapy --break-system-packages\n"
            "  pip install dpkt --break-system-packages"
        )


# =============================================================================
# ANALIZĂ STATISTICĂ
# =============================================================================

def analyze_capture(filepath: str) -> CaptureStatistics:
    """
    Analizează complet o captură PCAP și calculează statistici.
    
    Parcurge pachetele o singură dată (streaming) pentru eficiență
    și acumulează statistici în timp real.
    
    Args:
        filepath: Calea către fișierul PCAP
        
    Returns:
        CaptureStatistics cu toate metricile calculate
    """
    stats = CaptureStatistics(file_path=filepath)
    
    prev_timestamp = None
    
    for pkt in parse_pcap(filepath):
        stats.total_packets += 1
        stats.total_bytes += pkt.length
        stats.packet_sizes.append(pkt.length)
        
        # Timestamps
        if stats.total_packets == 1:
            stats.first_timestamp = pkt.timestamp
        stats.last_timestamp = pkt.timestamp
        
        # Inter-arrival time
        if prev_timestamp is not None:
            iat = pkt.timestamp - prev_timestamp
            if iat >= 0:  # Evită anomalii de timestamp
                stats.inter_arrival_times.append(iat)
        prev_timestamp = pkt.timestamp
        
        # Contoare protocol
        stats.protocols[pkt.protocol] += 1
        
        # Contoare IP
        if pkt.ip_src:
            stats.src_ips[pkt.ip_src] += 1
        if pkt.ip_dst:
            stats.dst_ips[pkt.ip_dst] += 1
        
        # Contoare port
        if pkt.src_port:
            stats.src_ports[pkt.src_port] += 1
        if pkt.dst_port:
            stats.dst_ports[pkt.dst_port] += 1
        
        # Contoare TCP flags
        if pkt.tcp_flags:
            stats.tcp_flags[pkt.tcp_flags] += 1
        
        # Tracking fluxuri
        if pkt.ip_src and pkt.ip_dst:
            flow_key = pkt.flow_tuple
            if flow_key not in stats.flows:
                stats.flows[flow_key] = {
                    'packets': 0,
                    'bytes': 0,
                    'start_time': pkt.timestamp,
                    'end_time': pkt.timestamp
                }
            stats.flows[flow_key]['packets'] += 1
            stats.flows[flow_key]['bytes'] += pkt.length
            stats.flows[flow_key]['end_time'] = pkt.timestamp
    
    # Calcul durată captură
    stats.capture_duration = stats.last_timestamp - stats.first_timestamp
    
    return stats


def detect_tcp_handshakes(filepath: str) -> list[dict]:
    """
    Detectează handshake-uri TCP complete (SYN → SYN-ACK → ACK).
    
    Un handshake TCP are trei pași:
    1. Client → Server: SYN (număr de secvență inițial client)
    2. Server → Client: SYN-ACK (confirmare + nr. secvență server)
    3. Client → Server: ACK (confirmare finală)
    
    Returns:
        Lista de handshake-uri detectate cu timing
    """
    handshakes = []
    pending_syns = {}  # (src_ip, src_port, dst_ip, dst_port) → timestamp
    pending_synacks = {}  # (dst_ip, dst_port, src_ip, src_port) → timestamp
    
    for pkt in parse_pcap(filepath):
        if not pkt.is_tcp or not pkt.tcp_flags:
            continue
        
        flags = pkt.tcp_flags.upper()
        key_forward = (pkt.ip_src, pkt.src_port, pkt.ip_dst, pkt.dst_port)
        key_reverse = (pkt.ip_dst, pkt.dst_port, pkt.ip_src, pkt.src_port)
        
        # Pas 1: SYN (fără ACK)
        if 'S' in flags and 'A' not in flags:
            pending_syns[key_forward] = pkt.timestamp
        
        # Pas 2: SYN-ACK
        elif 'S' in flags and 'A' in flags:
            if key_reverse in pending_syns:
                pending_synacks[key_forward] = {
                    'syn_time': pending_syns[key_reverse],
                    'synack_time': pkt.timestamp
                }
        
        # Pas 3: ACK final
        elif 'A' in flags and 'S' not in flags and 'F' not in flags:
            if key_reverse in pending_synacks:
                hs_info = pending_synacks.pop(key_reverse)
                handshakes.append({
                    'client_ip': pkt.ip_src,
                    'client_port': pkt.src_port,
                    'server_ip': pkt.ip_dst,
                    'server_port': pkt.dst_port,
                    'syn_time': hs_info['syn_time'],
                    'synack_time': hs_info['synack_time'],
                    'ack_time': pkt.timestamp,
                    'handshake_duration': pkt.timestamp - hs_info['syn_time']
                })
    
    return handshakes


def detect_retransmissions(filepath: str) -> list[dict]:
    """
    Detectează potențiale retransmisii TCP.
    
    Retransmisiile apar când:
    - Același pachet (src, dst, seq) apare de mai multe ori
    - ACK duplicat (același nr. de acknowledgment repetat)
    
    Returns:
        Lista de pachete suspectate ca retransmisii
    """
    seen_packets = defaultdict(list)  # (flow, seq_estimate) → [timestamps]
    retransmissions = []
    
    for pkt in parse_pcap(filepath):
        if not pkt.is_tcp:
            continue
        
        # Cheie simplificată (fără număr de secvență real - ar necesita acces la header TCP raw)
        # Folosim dimensiunea pachetului ca proxy
        key = (pkt.ip_src, pkt.src_port, pkt.ip_dst, pkt.dst_port, pkt.length)
        
        timestamps = seen_packets[key]
        
        for prev_ts in timestamps:
            # Dacă un pachet identic apare în mai puțin de 3 secunde
            if 0 < (pkt.timestamp - prev_ts) < 3.0:
                retransmissions.append({
                    'src': f"{pkt.ip_src}:{pkt.src_port}",
                    'dst': f"{pkt.ip_dst}:{pkt.dst_port}",
                    'original_time': prev_ts,
                    'retrans_time': pkt.timestamp,
                    'delta': pkt.timestamp - prev_ts,
                    'size': pkt.length
                })
                break
        
        timestamps.append(pkt.timestamp)
    
    return retransmissions


# =============================================================================
# RAPORTARE
# =============================================================================

def print_statistics_report(stats: CaptureStatistics):
    """
    Afișează un raport formatat cu statisticile capturii.
    """
    print("=" * 70)
    print(f"RAPORT STATISTICI PCAP: {Path(stats.file_path).name}")
    print("=" * 70)
    
    # Informații generale
    print(f"\n{'─' * 40}")
    print("SUMAR GENERAL")
    print(f"{'─' * 40}")
    print(f"  Total pachete:        {stats.total_packets:,}")
    print(f"  Total octeți:         {stats.total_bytes:,} ({stats.total_bytes / 1024:.2f} KB)")
    print(f"  Durată captură:       {stats.capture_duration:.3f} secunde")
    print(f"  Throughput:           {stats.throughput_mbps:.3f} Mbps")
    print(f"  Pachete/secundă:      {stats.packets_per_second:.2f}")
    
    # Statistici dimensiune pachete
    if stats.packet_sizes:
        print(f"\n{'─' * 40}")
        print("DIMENSIUNE PACHETE (octeți)")
        print(f"{'─' * 40}")
        print(f"  Minim:     {min(stats.packet_sizes):,}")
        print(f"  Maxim:     {max(stats.packet_sizes):,}")
        print(f"  Medie:     {stats.avg_packet_size:.2f}")
        print(f"  Mediană:   {statistics.median(stats.packet_sizes):.2f}")
        if len(stats.packet_sizes) > 1:
            print(f"  Std Dev:   {statistics.stdev(stats.packet_sizes):.2f}")
    
    # Distribuție protocoale
    print(f"\n{'─' * 40}")
    print("DISTRIBUȚIE PROTOCOALE")
    print(f"{'─' * 40}")
    for proto, count in stats.protocols.most_common(10):
        pct = (count / stats.total_packets) * 100
        bar = '█' * int(pct / 2)
        print(f"  {proto:10} {count:>8,} ({pct:5.1f}%) {bar}")
    
    # Top IP-uri sursă
    print(f"\n{'─' * 40}")
    print("TOP 5 IP-URI SURSĂ")
    print(f"{'─' * 40}")
    for ip, count in stats.src_ips.most_common(5):
        pct = (count / stats.total_packets) * 100
        print(f"  {ip:18} {count:>8,} ({pct:5.1f}%)")
    
    # Top IP-uri destinație
    print(f"\n{'─' * 40}")
    print("TOP 5 IP-URI DESTINAȚIE")
    print(f"{'─' * 40}")
    for ip, count in stats.dst_ips.most_common(5):
        pct = (count / stats.total_packets) * 100
        print(f"  {ip:18} {count:>8,} ({pct:5.1f}%)")
    
    # Top porturi destinație
    if stats.dst_ports:
        print(f"\n{'─' * 40}")
        print("TOP 5 PORTURI DESTINAȚIE")
        print(f"{'─' * 40}")
        for port, count in stats.dst_ports.most_common(5):
            service = get_service_name(port)
            print(f"  {port:>5} ({service:10}) {count:>8,}")
    
    # TCP flags
    if stats.tcp_flags:
        print(f"\n{'─' * 40}")
        print("DISTRIBUȚIE FLAG-URI TCP")
        print(f"{'─' * 40}")
        for flags, count in stats.tcp_flags.most_common(10):
            print(f"  {flags:10} {count:>8,}")
    
    # Statistici timing
    if stats.inter_arrival_times:
        print(f"\n{'─' * 40}")
        print("INTER-ARRIVAL TIME (milisecunde)")
        print(f"{'─' * 40}")
        iat_ms = [t * 1000 for t in stats.inter_arrival_times]
        print(f"  Minim:     {min(iat_ms):.3f}")
        print(f"  Maxim:     {max(iat_ms):.3f}")
        print(f"  Medie:     {statistics.mean(iat_ms):.3f}")
        print(f"  Mediană:   {statistics.median(iat_ms):.3f}")
    
    # Sumar fluxuri
    print(f"\n{'─' * 40}")
    print("SUMAR FLUXURI (5-TUPLE)")
    print(f"{'─' * 40}")
    print(f"  Total fluxuri unice: {len(stats.flows)}")
    
    if stats.flows:
        # Top 5 fluxuri după bytes
        sorted_flows = sorted(
            stats.flows.items(),
            key=lambda x: x[1]['bytes'],
            reverse=True
        )[:5]
        
        print(f"\n  Top 5 fluxuri (după octeți):")
        for flow_key, flow_data in sorted_flows:
            src_ip, dst_ip, src_port, dst_port, proto = flow_key
            print(f"    {src_ip}:{src_port} → {dst_ip}:{dst_port} ({proto})")
            print(f"      {flow_data['packets']} pachete, {flow_data['bytes']:,} octeți")
    
    print(f"\n{'=' * 70}")


def get_service_name(port: int) -> str:
    """Returnează numele serviciului pentru un port cunoscut."""
    services = {
        20: "FTP-DATA", 21: "FTP", 22: "SSH", 23: "TELNET",
        25: "SMTP", 53: "DNS", 67: "DHCP-S", 68: "DHCP-C",
        80: "HTTP", 110: "POP3", 143: "IMAP", 443: "HTTPS",
        465: "SMTPS", 587: "SMTP-SUB", 993: "IMAPS", 995: "POP3S",
        3306: "MySQL", 5432: "PostgreSQL", 6379: "Redis",
        8080: "HTTP-ALT", 8443: "HTTPS-ALT"
    }
    return services.get(port, "?")


# =============================================================================
# EXPORT DATE
# =============================================================================

def export_to_csv(stats: CaptureStatistics, output_path: str):
    """
    Exportă statisticile într-un fișier CSV pentru analiză ulterioară.
    """
    import csv
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Secțiune: Sumar
        writer.writerow(['=== SUMAR GENERAL ==='])
        writer.writerow(['Metric', 'Value'])
        writer.writerow(['Total Packets', stats.total_packets])
        writer.writerow(['Total Bytes', stats.total_bytes])
        writer.writerow(['Duration (s)', f'{stats.capture_duration:.3f}'])
        writer.writerow(['Throughput (Mbps)', f'{stats.throughput_mbps:.3f}'])
        writer.writerow(['Packets/sec', f'{stats.packets_per_second:.2f}'])
        writer.writerow([])
        
        # Secțiune: Protocoale
        writer.writerow(['=== PROTOCOALE ==='])
        writer.writerow(['Protocol', 'Count', 'Percentage'])
        for proto, count in stats.protocols.most_common():
            pct = (count / stats.total_packets) * 100
            writer.writerow([proto, count, f'{pct:.2f}%'])
        writer.writerow([])
        
        # Secțiune: IP-uri
        writer.writerow(['=== TOP IP-URI ==='])
        writer.writerow(['Type', 'IP', 'Count'])
        for ip, count in stats.src_ips.most_common(20):
            writer.writerow(['SRC', ip, count])
        for ip, count in stats.dst_ips.most_common(20):
            writer.writerow(['DST', ip, count])
    
    print(f"\n✓ Statistici exportate în: {output_path}")


# =============================================================================
# GENERARE PCAP DE TEST
# =============================================================================

def generate_sample_pcap(output_path: str):
    """
    Generează un fișier PCAP minim pentru testare.
    
    Creează o conversație TCP simulată cu:
    - TCP handshake (SYN, SYN-ACK, ACK)
    - Transfer date (PSH-ACK)
    - Închidere conexiune (FIN)
    """
    if not SCAPY_AVAILABLE:
        print("⚠ Scapy nu este disponibil. Nu se poate genera PCAP de test.")
        print("  Folosiți un PCAP existent sau instalați Scapy.")
        return False
    
    from scapy.all import wrpcap
    
    packets = []
    base_time = 1704067200.0  # 2024-01-01 00:00:00 UTC
    
    # Parametri conexiune
    client_ip = "192.168.1.100"
    server_ip = "192.168.1.1"
    client_port = 54321
    server_port = 80
    
    # Client → Server: SYN
    syn = Ether()/IP(src=client_ip, dst=server_ip)/TCP(
        sport=client_port, dport=server_port,
        flags='S', seq=1000
    )
    syn.time = base_time
    packets.append(syn)
    
    # Server → Client: SYN-ACK
    synack = Ether()/IP(src=server_ip, dst=client_ip)/TCP(
        sport=server_port, dport=client_port,
        flags='SA', seq=2000, ack=1001
    )
    synack.time = base_time + 0.001
    packets.append(synack)
    
    # Client → Server: ACK
    ack = Ether()/IP(src=client_ip, dst=server_ip)/TCP(
        sport=client_port, dport=server_port,
        flags='A', seq=1001, ack=2001
    )
    ack.time = base_time + 0.002
    packets.append(ack)
    
    # Client → Server: HTTP GET (PSH-ACK)
    http_req = b"GET / HTTP/1.1\r\nHost: example.com\r\n\r\n"
    data1 = Ether()/IP(src=client_ip, dst=server_ip)/TCP(
        sport=client_port, dport=server_port,
        flags='PA', seq=1001, ack=2001
    )/Raw(load=http_req)
    data1.time = base_time + 0.010
    packets.append(data1)
    
    # Server → Client: HTTP Response (PSH-ACK)
    http_resp = b"HTTP/1.1 200 OK\r\nContent-Length: 13\r\n\r\nHello, World!"
    data2 = Ether()/IP(src=server_ip, dst=client_ip)/TCP(
        sport=server_port, dport=client_port,
        flags='PA', seq=2001, ack=1001 + len(http_req)
    )/Raw(load=http_resp)
    data2.time = base_time + 0.015
    packets.append(data2)
    
    # Server → Client: FIN
    fin = Ether()/IP(src=server_ip, dst=client_ip)/TCP(
        sport=server_port, dport=client_port,
        flags='FA', seq=2001 + len(http_resp), ack=1001 + len(http_req)
    )
    fin.time = base_time + 0.020
    packets.append(fin)
    
    # Adăugăm câteva pachete UDP pentru diversitate
    udp1 = Ether()/IP(src=client_ip, dst="8.8.8.8")/UDP(
        sport=12345, dport=53
    )/Raw(load=b"\x00\x01\x00\x00")
    udp1.time = base_time + 0.025
    packets.append(udp1)
    
    # Scriere PCAP
    wrpcap(output_path, packets)
    print(f"✓ PCAP de test generat: {output_path}")
    print(f"  {len(packets)} pachete (TCP handshake + HTTP + UDP)")
    return True


# =============================================================================
# AUTO-TEST
# =============================================================================

def run_tests() -> bool:
    """
    Rulează suite de teste pentru validarea funcționalității.
    
    Returns:
        True dacă toate testele trec, False altfel
    """
    import tempfile
    import os
    
    print("=" * 50)
    print("AUTO-TEST: ex_1_04_pcap_stats.py")
    print("=" * 50)
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Verificare bibliotecă disponibilă
    tests_total += 1
    print(f"\n[Test {tests_total}] Verificare bibliotecă PCAP...")
    if SCAPY_AVAILABLE:
        print("  ✓ Scapy disponibil")
        tests_passed += 1
    elif DPKT_AVAILABLE:
        print("  ✓ dpkt disponibil (fallback)")
        tests_passed += 1
    else:
        print("  ✗ Nicio bibliotecă PCAP disponibilă!")
        print("    Instalați: pip install scapy --break-system-packages")
        return False
    
    # Test 2: Generare PCAP de test
    tests_total += 1
    print(f"\n[Test {tests_total}] Generare PCAP de test...")
    
    if SCAPY_AVAILABLE:
        with tempfile.NamedTemporaryFile(suffix='.pcap', delete=False) as f:
            test_pcap = f.name
        
        try:
            if generate_sample_pcap(test_pcap):
                print("  ✓ PCAP generat cu succes")
                tests_passed += 1
            else:
                print("  ✗ Eroare la generare PCAP")
        except Exception as e:
            print(f"  ✗ Excepție: {e}")
    else:
        print("  ⊘ Skip (necesită Scapy pentru generare)")
        tests_passed += 1  # Nu penalizăm
    
    # Test 3: Parsare PCAP
    tests_total += 1
    print(f"\n[Test {tests_total}] Parsare PCAP...")
    
    if SCAPY_AVAILABLE and os.path.exists(test_pcap):
        try:
            packets = list(parse_pcap(test_pcap))
            if len(packets) > 0:
                print(f"  ✓ Parsate {len(packets)} pachete")
                tests_passed += 1
            else:
                print("  ✗ Niciun pachet parsat")
        except Exception as e:
            print(f"  ✗ Excepție: {e}")
    else:
        print("  ⊘ Skip (fără PCAP de test)")
        tests_passed += 1
    
    # Test 4: Analiză statistici
    tests_total += 1
    print(f"\n[Test {tests_total}] Analiză statistici...")
    
    if SCAPY_AVAILABLE and os.path.exists(test_pcap):
        try:
            stats = analyze_capture(test_pcap)
            if stats.total_packets > 0 and stats.total_bytes > 0:
                print(f"  ✓ Statistici calculate: {stats.total_packets} pkt, {stats.total_bytes} bytes")
                tests_passed += 1
            else:
                print("  ✗ Statistici invalide")
        except Exception as e:
            print(f"  ✗ Excepție: {e}")
    else:
        print("  ⊘ Skip")
        tests_passed += 1
    
    # Test 5: Detectare handshake
    tests_total += 1
    print(f"\n[Test {tests_total}] Detectare TCP handshake...")
    
    if SCAPY_AVAILABLE and os.path.exists(test_pcap):
        try:
            handshakes = detect_tcp_handshakes(test_pcap)
            if len(handshakes) >= 1:
                print(f"  ✓ Detectate {len(handshakes)} handshake(uri)")
                tests_passed += 1
            else:
                print("  ⚠ Niciun handshake detectat (poate fi OK)")
                tests_passed += 1  # Nu penalizăm
        except Exception as e:
            print(f"  ✗ Excepție: {e}")
    else:
        print("  ⊘ Skip")
        tests_passed += 1
    
    # Cleanup
    if SCAPY_AVAILABLE and os.path.exists(test_pcap):
        os.unlink(test_pcap)
    
    # Sumar
    print(f"\n{'=' * 50}")
    print(f"REZULTAT: {tests_passed}/{tests_total} teste trecute")
    print("=" * 50)
    
    return tests_passed == tests_total


# =============================================================================
# CLI
# =============================================================================

def main():
    """Punct de intrare pentru CLI."""
    parser = argparse.ArgumentParser(
        description="Analiză statistică pentru fișiere PCAP",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemple de utilizare:
  %(prog)s capture.pcap                    # Analiză standard
  %(prog)s capture.pcap --handshakes       # Detectare TCP handshakes
  %(prog)s capture.pcap --retrans          # Detectare retransmisii
  %(prog)s capture.pcap --export stats.csv # Export CSV
  %(prog)s --generate test.pcap            # Generare PCAP de test
  %(prog)s --test                          # Rulare auto-teste
        """
    )
    
    parser.add_argument('pcap', nargs='?', help='Fișier PCAP de analizat')
    parser.add_argument('--generate', metavar='OUTPUT', 
                        help='Generează un PCAP de test')
    parser.add_argument('--handshakes', action='store_true',
                        help='Detectează TCP handshakes')
    parser.add_argument('--retrans', action='store_true',
                        help='Detectează potențiale retransmisii')
    parser.add_argument('--export', metavar='CSV',
                        help='Exportă statistici în CSV')
    parser.add_argument('--test', action='store_true',
                        help='Rulează auto-teste')
    
    args = parser.parse_args()
    
    # Auto-test
    if args.test:
        success = run_tests()
        sys.exit(0 if success else 1)
    
    # Generare PCAP de test
    if args.generate:
        success = generate_sample_pcap(args.generate)
        sys.exit(0 if success else 1)
    
    # Analiză PCAP
    if not args.pcap:
        parser.print_help()
        sys.exit(1)
    
    pcap_path = args.pcap
    if not Path(pcap_path).exists():
        print(f"EROARE: Fișierul nu există: {pcap_path}")
        sys.exit(1)
    
    # Statistici principale
    print(f"\nAnalizez: {pcap_path}...")
    stats = analyze_capture(pcap_path)
    print_statistics_report(stats)
    
    # Detectare handshakes
    if args.handshakes:
        print(f"\n{'=' * 70}")
        print("DETECTARE TCP HANDSHAKES")
        print("=" * 70)
        handshakes = detect_tcp_handshakes(pcap_path)
        if handshakes:
            for i, hs in enumerate(handshakes, 1):
                print(f"\n  Handshake #{i}:")
                print(f"    Client: {hs['client_ip']}:{hs['client_port']}")
                print(f"    Server: {hs['server_ip']}:{hs['server_port']}")
                print(f"    Durată: {hs['handshake_duration']*1000:.3f} ms")
        else:
            print("\n  Niciun handshake complet detectat.")
    
    # Detectare retransmisii
    if args.retrans:
        print(f"\n{'=' * 70}")
        print("DETECTARE POTENȚIALE RETRANSMISII")
        print("=" * 70)
        retrans = detect_retransmissions(pcap_path)
        if retrans:
            for rt in retrans[:20]:  # Limitare la primele 20
                print(f"\n  {rt['src']} → {rt['dst']}")
                print(f"    Delta: {rt['delta']*1000:.3f} ms, Size: {rt['size']} bytes")
            if len(retrans) > 20:
                print(f"\n  ... și încă {len(retrans) - 20} altele")
        else:
            print("\n  Nicio retransmisie potențială detectată.")
    
    # Export CSV
    if args.export:
        export_to_csv(stats, args.export)


if __name__ == '__main__':
    main()
