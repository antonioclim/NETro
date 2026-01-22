#!/usr/bin/env python3
"""
Exercițiul 1.03: Parsarea CSV-urilor generate de tshark
=======================================================
Rețele de Calculatoare - Săptămâna 1
ASE București

Obiective:
- Procesarea output-ului tshark în format CSV
- Analiza statistică a traficului de rețea
- Vizualizare simplă a datelor

Nivel: Mediu
Timp estimat: 20 minute
"""

import csv
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Generator


@dataclass
class PacketInfo:
    """Informații extrase dintr-un pachet."""
    frame_number: int
    time_relative: float
    ip_src: str
    ip_dst: str
    protocol: str
    length: int
    src_port: int | None = None
    dst_port: int | None = None
    tcp_flags: str | None = None


def parse_tshark_csv(filepath: str | Path) -> Generator[PacketInfo, None, None]:
    """
    Parsează un fișier CSV generat de tshark.
    
    Format așteptat (header):
    frame.number,frame.time_relative,ip.src,ip.dst,_ws.col.Protocol,frame.len,
    tcp.srcport,tcp.dstport,tcp.flags.str
    
    Args:
        filepath: Calea către fișierul CSV
        
    Yields:
        PacketInfo pentru fiecare pachet valid
    """
    filepath = Path(filepath)
    
    if not filepath.exists():
        raise FileNotFoundError(f"Fișierul nu există: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            try:
                # Mapăm câmpurile (tolerant la variații)
                frame_num = int(row.get('frame.number', row.get('No.', 0)))
                time_rel = float(row.get('frame.time_relative', 
                                        row.get('Time', 0)))
                ip_src = row.get('ip.src', row.get('Source', ''))
                ip_dst = row.get('ip.dst', row.get('Destination', ''))
                protocol = row.get('_ws.col.Protocol', 
                                  row.get('Protocol', 'Unknown'))
                length = int(row.get('frame.len', row.get('Length', 0)))
                
                # Porturi (pot lipsi pentru non-TCP/UDP)
                src_port = None
                dst_port = None
                if 'tcp.srcport' in row and row['tcp.srcport']:
                    src_port = int(row['tcp.srcport'])
                if 'tcp.dstport' in row and row['tcp.dstport']:
                    dst_port = int(row['tcp.dstport'])
                if 'udp.srcport' in row and row['udp.srcport']:
                    src_port = int(row['udp.srcport'])
                if 'udp.dstport' in row and row['udp.dstport']:
                    dst_port = int(row['udp.dstport'])
                
                tcp_flags = row.get('tcp.flags.str', None)
                
                yield PacketInfo(
                    frame_number=frame_num,
                    time_relative=time_rel,
                    ip_src=ip_src,
                    ip_dst=ip_dst,
                    protocol=protocol,
                    length=length,
                    src_port=src_port,
                    dst_port=dst_port,
                    tcp_flags=tcp_flags
                )
                
            except (ValueError, KeyError) as e:
                print(f"[WARN] Linie ignorată: {e}")
                continue


def analyze_capture(packets: list[PacketInfo]) -> dict:
    """
    Analizează o listă de pachete și returnează statistici.
    
    Returns:
        Dict cu statistici: total_packets, protocols, ports, etc.
    """
    if not packets:
        return {"error": "Nicio captură de analizat"}
    
    stats = {
        "total_packets": len(packets),
        "total_bytes": sum(p.length for p in packets),
        "duration_seconds": packets[-1].time_relative - packets[0].time_relative,
        "protocols": Counter(),
        "src_ips": Counter(),
        "dst_ips": Counter(),
        "dst_ports": Counter(),
        "tcp_flags": Counter(),
        "packet_sizes": [],
    }
    
    for p in packets:
        stats["protocols"][p.protocol] += 1
        stats["src_ips"][p.ip_src] += 1
        stats["dst_ips"][p.ip_dst] += 1
        stats["packet_sizes"].append(p.length)
        
        if p.dst_port:
            stats["dst_ports"][p.dst_port] += 1
        
        if p.tcp_flags:
            # Extragem flag-uri individuale
            for flag in ['S', 'A', 'F', 'R', 'P']:
                if flag in p.tcp_flags:
                    stats["tcp_flags"][flag] += 1
    
    # Calculăm statistici derivate
    sizes = stats["packet_sizes"]
    stats["avg_packet_size"] = sum(sizes) / len(sizes)
    stats["min_packet_size"] = min(sizes)
    stats["max_packet_size"] = max(sizes)
    
    if stats["duration_seconds"] > 0:
        stats["packets_per_second"] = len(packets) / stats["duration_seconds"]
        stats["bytes_per_second"] = stats["total_bytes"] / stats["duration_seconds"]
        stats["throughput_mbps"] = (stats["bytes_per_second"] * 8) / 1_000_000
    
    return stats


def print_analysis_report(stats: dict) -> None:
    """Afișează un raport formatat al analizei."""
    
    print("\n" + "="*70)
    print(" RAPORT ANALIZĂ CAPTURĂ ".center(70))
    print("="*70)
    
    print(f"\n{'Sumar General':-^70}")
    print(f"  Total pachete:     {stats['total_packets']:,}")
    print(f"  Total bytes:       {stats['total_bytes']:,} ({stats['total_bytes']/1024:.2f} KB)")
    print(f"  Durată captură:    {stats['duration_seconds']:.3f} secunde")
    
    if 'throughput_mbps' in stats:
        print(f"  Throughput mediu:  {stats['throughput_mbps']:.4f} Mbps")
        print(f"  Pachete/secundă:   {stats['packets_per_second']:.2f}")
    
    print(f"\n{'Dimensiuni Pachete':-^70}")
    print(f"  Minim:   {stats['min_packet_size']} bytes")
    print(f"  Mediu:   {stats['avg_packet_size']:.1f} bytes")
    print(f"  Maxim:   {stats['max_packet_size']} bytes")
    
    print(f"\n{'Distribuție Protocoale':-^70}")
    for proto, count in stats['protocols'].most_common(10):
        pct = (count / stats['total_packets']) * 100
        bar = '█' * int(pct / 2)
        print(f"  {proto:<12} {count:>6} ({pct:>5.1f}%) {bar}")
    
    print(f"\n{'Top 5 Porturi Destinație':-^70}")
    for port, count in stats['dst_ports'].most_common(5):
        service = get_service_name(port)
        print(f"  Port {port:<5} ({service:<10}): {count:>6} pachete")
    
    if stats['tcp_flags']:
        print(f"\n{'Flag-uri TCP':-^70}")
        flag_names = {'S': 'SYN', 'A': 'ACK', 'F': 'FIN', 'R': 'RST', 'P': 'PSH'}
        for flag, count in stats['tcp_flags'].most_common():
            name = flag_names.get(flag, flag)
            print(f"  {name:<6} ({flag}): {count:>6}")
    
    print("\n" + "="*70)


def get_service_name(port: int) -> str:
    """Returnează numele serviciului pentru porturi comune."""
    services = {
        20: "FTP-data",
        21: "FTP",
        22: "SSH",
        23: "Telnet",
        25: "SMTP",
        53: "DNS",
        80: "HTTP",
        110: "POP3",
        143: "IMAP",
        443: "HTTPS",
        993: "IMAPS",
        995: "POP3S",
        3306: "MySQL",
        5432: "PostgreSQL",
        6379: "Redis",
        8080: "HTTP-alt",
    }
    return services.get(port, "unknown")


def find_tcp_handshakes(packets: list[PacketInfo]) -> list[dict]:
    """
    Identifică handshake-urile TCP în captură.
    
    Returns:
        Lista de handshake-uri detectate cu timing
    """
    handshakes = []
    pending_syn = {}  # key: (src_ip, src_port, dst_ip, dst_port)
    
    for p in packets:
        if not p.tcp_flags or p.protocol != 'TCP':
            continue
        
        flags = p.tcp_flags
        conn_key = (p.ip_src, p.src_port, p.ip_dst, p.dst_port)
        reverse_key = (p.ip_dst, p.dst_port, p.ip_src, p.src_port)
        
        # SYN (fără ACK) - inițiere conexiune
        if 'S' in flags and 'A' not in flags:
            pending_syn[conn_key] = {
                'syn_time': p.time_relative,
                'syn_frame': p.frame_number,
                'client': p.ip_src,
                'server': p.ip_dst,
                'port': p.dst_port
            }
        
        # SYN-ACK - răspuns server
        elif 'S' in flags and 'A' in flags:
            if reverse_key in pending_syn:
                pending_syn[reverse_key]['syn_ack_time'] = p.time_relative
                pending_syn[reverse_key]['syn_ack_frame'] = p.frame_number
        
        # ACK (fără SYN) - finalizare handshake
        elif 'A' in flags and 'S' not in flags and 'F' not in flags:
            if conn_key in pending_syn and 'syn_ack_time' in pending_syn[conn_key]:
                hs = pending_syn[conn_key]
                hs['ack_time'] = p.time_relative
                hs['ack_frame'] = p.frame_number
                hs['handshake_duration_ms'] = (hs['ack_time'] - hs['syn_time']) * 1000
                handshakes.append(hs)
                del pending_syn[conn_key]
    
    return handshakes


# =============================================================================
# GENERARE CSV DE TEST
# =============================================================================

def generate_sample_csv(filepath: str = "sample_capture.csv") -> None:
    """Generează un CSV de test pentru exerciții."""
    
    sample_data = [
        {
            'frame.number': '1',
            'frame.time_relative': '0.000000',
            'ip.src': '192.168.1.100',
            'ip.dst': '93.184.216.34',
            '_ws.col.Protocol': 'TCP',
            'frame.len': '74',
            'tcp.srcport': '54321',
            'tcp.dstport': '80',
            'tcp.flags.str': '··········S·'
        },
        {
            'frame.number': '2',
            'frame.time_relative': '0.025000',
            'ip.src': '93.184.216.34',
            'ip.dst': '192.168.1.100',
            '_ws.col.Protocol': 'TCP',
            'frame.len': '74',
            'tcp.srcport': '80',
            'tcp.dstport': '54321',
            'tcp.flags.str': '·······A··S·'
        },
        {
            'frame.number': '3',
            'frame.time_relative': '0.025500',
            'ip.src': '192.168.1.100',
            'ip.dst': '93.184.216.34',
            '_ws.col.Protocol': 'TCP',
            'frame.len': '66',
            'tcp.srcport': '54321',
            'tcp.dstport': '80',
            'tcp.flags.str': '·······A····'
        },
        {
            'frame.number': '4',
            'frame.time_relative': '0.026000',
            'ip.src': '192.168.1.100',
            'ip.dst': '93.184.216.34',
            '_ws.col.Protocol': 'TCP',
            'frame.len': '200',
            'tcp.srcport': '54321',
            'tcp.dstport': '80',
            'tcp.flags.str': '·······AP···'
        },
        {
            'frame.number': '5',
            'frame.time_relative': '0.050000',
            'ip.src': '93.184.216.34',
            'ip.dst': '192.168.1.100',
            '_ws.col.Protocol': 'TCP',
            'frame.len': '1500',
            'tcp.srcport': '80',
            'tcp.dstport': '54321',
            'tcp.flags.str': '·······A····'
        },
    ]
    
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=sample_data[0].keys())
        writer.writeheader()
        writer.writerows(sample_data)
    
    print(f"[INFO] Fișier CSV de test generat: {filepath}")


# =============================================================================
# AUTO-TEST
# =============================================================================

def run_self_test() -> bool:
    """Rulează auto-testele."""
    import tempfile
    import os
    
    print("\n" + "="*60)
    print(" AUTO-TEST ".center(60, "="))
    print("="*60 + "\n")
    
    tests_passed = 0
    tests_total = 3
    
    # Creăm fișier temporar
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        temp_path = f.name
        f.write("frame.number,frame.time_relative,ip.src,ip.dst,_ws.col.Protocol,frame.len\n")
        f.write("1,0.0,10.0.0.1,10.0.0.2,TCP,100\n")
        f.write("2,0.1,10.0.0.2,10.0.0.1,TCP,150\n")
        f.write("3,0.2,10.0.0.1,10.0.0.2,UDP,80\n")
    
    try:
        # Test 1: Parsare CSV
        print("[TEST 1] Parsare CSV...", end=" ")
        packets = list(parse_tshark_csv(temp_path))
        if len(packets) == 3:
            print("✓ PASS")
            tests_passed += 1
        else:
            print(f"✗ FAIL (așteptat 3, primit {len(packets)})")
        
        # Test 2: Analiză
        print("[TEST 2] Analiză captură...", end=" ")
        stats = analyze_capture(packets)
        if stats['total_packets'] == 3 and stats['total_bytes'] == 330:
            print("✓ PASS")
            tests_passed += 1
        else:
            print("✗ FAIL")
        
        # Test 3: Protocoale
        print("[TEST 3] Numărare protocoale...", end=" ")
        if stats['protocols']['TCP'] == 2 and stats['protocols']['UDP'] == 1:
            print("✓ PASS")
            tests_passed += 1
        else:
            print("✗ FAIL")
            
    finally:
        os.unlink(temp_path)
    
    print(f"\nRezultat: {tests_passed}/{tests_total} teste trecute")
    return tests_passed == tests_total


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--test":
            success = run_self_test()
            sys.exit(0 if success else 1)
        
        elif sys.argv[1] == "--generate":
            output = sys.argv[2] if len(sys.argv) > 2 else "sample_capture.csv"
            generate_sample_csv(output)
            sys.exit(0)
        
        else:
            # Presupunem că e un fișier CSV
            csv_file = sys.argv[1]
            print(f"[INFO] Analizez: {csv_file}")
            
            packets = list(parse_tshark_csv(csv_file))
            stats = analyze_capture(packets)
            print_analysis_report(stats)
            
            # Căutăm handshake-uri
            handshakes = find_tcp_handshakes(packets)
            if handshakes:
                print(f"\n{'TCP Handshakes Detectate':-^70}")
                for hs in handshakes:
                    print(f"  {hs['client']} → {hs['server']}:{hs['port']} "
                          f"în {hs['handshake_duration_ms']:.2f} ms")
    else:
        print("""
Utilizare:
    python ex_1_03_parse_csv.py <fisier.csv>    # Analizează captură
    python ex_1_03_parse_csv.py --generate      # Generează CSV de test
    python ex_1_03_parse_csv.py --test          # Rulează auto-teste

Generare CSV din tshark:
    tshark -r captura.pcap -T fields -E header=y -E separator=, \\
        -e frame.number -e frame.time_relative \\
        -e ip.src -e ip.dst -e _ws.col.Protocol \\
        -e frame.len -e tcp.srcport -e tcp.dstport \\
        -e tcp.flags.str > output.csv
""")
