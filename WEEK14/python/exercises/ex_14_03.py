#!/usr/bin/env python3
"""ex_14_03.py — Exerciții avansate (challenge) pentru Săptămâna 14.

Funcționalități:
  - Implementare minimală protocol custom
  - Analiză automată pcap
  - Generare raport performanță

Utilizare:
  python3 ex_14_03.py --challenge echo      # Challenge: protocol echo extins
  python3 ex_14_03.py --challenge analyze   # Challenge: analiză pcap
  python3 ex_14_03.py --challenge benchmark # Challenge: benchmark HTTP
"""

from __future__ import annotations

import argparse
import json
import socket
import struct
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

# ============================================================================
# CHALLENGE 1: Protocol Echo Extins
# ============================================================================

def challenge_echo_protocol():
    """
    Challenge: Implementează un protocol echo extins.
    
    Protocolul:
    - Header: [magic:2][version:1][cmd:1][length:4] = 8 bytes
    - Payload: [length] bytes
    
    Comenzi:
    - 0x01: ECHO (răspunde cu același payload)
    - 0x02: REVERSE (răspunde cu payload inversat)
    - 0x03: UPPER (răspunde cu payload în uppercase)
    - 0x04: INFO (răspunde cu info server)
    """
    
    MAGIC = b'\xCA\xFE'
    VERSION = 1
    
    CMD_ECHO = 0x01
    CMD_REVERSE = 0x02
    CMD_UPPER = 0x03
    CMD_INFO = 0x04
    
    print("\n" + "=" * 60)
    print("  Challenge: Protocol Echo Extins")
    print("=" * 60)
    print("""
Implementează un server și client pentru protocolul de mai sus.

Structura header-ului (8 bytes):
  - magic    (2 bytes): 0xCAFE
  - version  (1 byte):  1
  - cmd      (1 byte):  tipul comenzii
  - length   (4 bytes): lungimea payload-ului (big-endian)

Comenzi disponibile:
  0x01 ECHO    - Returnează payload-ul nemodificat
  0x02 REVERSE - Returnează payload-ul inversat
  0x03 UPPER   - Returnează payload-ul în uppercase
  0x04 INFO    - Returnează informații despre server (JSON)

Exemplu de implementare (incompletă):
""")
    
    # Exemplu de cod starter
    starter_code = '''
def pack_message(cmd: int, payload: bytes) -> bytes:
    """Împachetează un mesaj conform protocolului."""
    magic = b'\\xCA\\xFE'
    version = struct.pack("B", 1)
    cmd_byte = struct.pack("B", cmd)
    length = struct.pack(">I", len(payload))
    return magic + version + cmd_byte + length + payload

def unpack_header(data: bytes) -> Tuple[int, int, int]:
    """Despachetează header-ul și returnează (version, cmd, length)."""
    if len(data) < 8:
        raise ValueError("Header incomplet")
    if data[:2] != b'\\xCA\\xFE':
        raise ValueError("Magic invalid")
    version = struct.unpack("B", data[2:3])[0]
    cmd = struct.unpack("B", data[3:4])[0]
    length = struct.unpack(">I", data[4:8])[0]
    return version, cmd, length

# TODO: Implementează server și client
# Server: ascultă pe port 9090, procesează comenzi
# Client: trimite comenzi, afișează răspunsuri
'''
    print(starter_code)
    
    print("""
Sarcini:
1. Completează funcțiile de mai sus
2. Implementează serverul (hint: socket.socket, bind, listen, accept)
3. Implementează clientul (hint: socket.socket, connect, send, recv)
4. Testează toate cele 4 comenzi
5. Adaugă tratarea erorilor (timeout, conexiune refuzată, etc.)

Bonus:
- Adaugă suport pentru conexiuni multiple (threading sau select)
- Implementează o comandă nouă (ex: HASH - returnează SHA256)
- Adaugă logging cu timestamp pentru fiecare comandă
""")
    
    return 0


# ============================================================================
# CHALLENGE 2: Analiză PCAP
# ============================================================================

def challenge_analyze_pcap():
    """
    Challenge: Implementează un analizor de pcap simplu.
    """
    
    print("\n" + "=" * 60)
    print("  Challenge: Analiză PCAP")
    print("=" * 60)
    print("""
Implementează un script Python care analizează un fișier pcap
și extrage statistici utile.

Cerințe:
1. Parsează header-ul global pcap (24 bytes)
2. Parsează fiecare packet header + date
3. Extrage și numără:
   - Pachete per protocol (TCP/UDP/ICMP)
   - Top 5 adrese IP sursă
   - Top 5 porturi destinație
   - Conversații TCP unice (src_ip:src_port -> dst_ip:dst_port)

Structura pcap:
  Global Header (24 bytes):
    - magic_number (4 bytes): 0xa1b2c3d4 sau 0xd4c3b2a1
    - version_major (2 bytes)
    - version_minor (2 bytes)
    - thiszone (4 bytes)
    - sigfigs (4 bytes)
    - snaplen (4 bytes)
    - network (4 bytes): 1 = Ethernet

  Per-Packet Header (16 bytes):
    - ts_sec (4 bytes)
    - ts_usec (4 bytes)
    - incl_len (4 bytes): bytes captured
    - orig_len (4 bytes): original length

  Ethernet Header (14 bytes):
    - dst_mac (6 bytes)
    - src_mac (6 bytes)
    - ethertype (2 bytes): 0x0800 = IPv4

  IP Header (20+ bytes):
    - version_ihl (1 byte): version=4, ihl=header_length/4
    - ...
    - protocol (1 byte, offset 9): 6=TCP, 17=UDP, 1=ICMP
    - src_ip (4 bytes, offset 12)
    - dst_ip (4 bytes, offset 16)

Exemplu de cod starter:
""")
    
    starter_code = '''
import struct
from collections import Counter

def analyze_pcap(filepath: str) -> Dict[str, Any]:
    """Analizează un fișier pcap și returnează statistici."""
    
    stats = {
        "packets": 0,
        "protocols": Counter(),
        "src_ips": Counter(),
        "dst_ports": Counter(),
        "conversations": set(),
    }
    
    with open(filepath, "rb") as f:
        # Citește global header (24 bytes)
        global_header = f.read(24)
        magic = struct.unpack("<I", global_header[:4])[0]
        
        # Verifică endianness
        if magic == 0xa1b2c3d4:
            endian = "<"  # little-endian
        elif magic == 0xd4c3b2a1:
            endian = ">"  # big-endian
        else:
            raise ValueError("Invalid pcap magic")
        
        while True:
            # Citește packet header (16 bytes)
            pkt_header = f.read(16)
            if len(pkt_header) < 16:
                break
            
            ts_sec, ts_usec, incl_len, orig_len = struct.unpack(
                f"{endian}IIII", pkt_header
            )
            
            # Citește datele pachetului
            pkt_data = f.read(incl_len)
            if len(pkt_data) < incl_len:
                break
            
            stats["packets"] += 1
            
            # TODO: Parsează Ethernet header
            # TODO: Parsează IP header
            # TODO: Extrage protocol, IP-uri, porturi
            # TODO: Actualizează statisticile
    
    return stats
'''
    print(starter_code)
    
    print("""
Sarcini:
1. Completează funcția analyze_pcap()
2. Implementează parsarea Ethernet și IP headers
3. Extrage și numără protocoalele
4. Identifică conversațiile TCP
5. Afișează un raport formatat

Testare:
  python3 ex_14_03.py --challenge analyze --pcap artifacts/demo.pcap

Bonus:
- Adaugă suport pentru IPv6
- Calculează durata totală a capturii
- Identifică posibile scanări de porturi
""")
    
    return 0


# ============================================================================
# CHALLENGE 3: Benchmark HTTP
# ============================================================================

def challenge_benchmark():
    """
    Challenge: Implementează un benchmark HTTP simplu.
    """
    
    print("\n" + "=" * 60)
    print("  Challenge: Benchmark HTTP")
    print("=" * 60)
    print("""
Implementează un tool de benchmark HTTP similar cu Apache Bench (ab).

Cerințe:
1. Acceptă parametri: URL, număr cereri, concurență
2. Trimite cereri HTTP GET
3. Măsoară și raportează:
   - Total time
   - Requests per second
   - Time per request (mean)
   - Time per request (across all concurrent)
   - Transfer rate
   - Connection times (min, mean, max)
   - Percentile latencies (50%, 90%, 99%)

Exemplu de cod starter:
""")
    
    starter_code = '''
import threading
import time
from queue import Queue
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

def http_worker(url: str, results: Queue, timeout: float = 5.0):
    """Worker thread pentru cereri HTTP."""
    try:
        start = time.time()
        req = Request(url, method="GET")
        with urlopen(req, timeout=timeout) as response:
            data = response.read()
            latency = time.time() - start
            results.put({
                "success": True,
                "status": response.status,
                "latency": latency,
                "bytes": len(data),
            })
    except Exception as e:
        latency = time.time() - start
        results.put({
            "success": False,
            "error": str(e),
            "latency": latency,
        })

def run_benchmark(url: str, n_requests: int, concurrency: int) -> Dict:
    """Rulează benchmark-ul."""
    results = Queue()
    threads = []
    
    start_time = time.time()
    
    # TODO: Implementează logica de concurență
    # - Pornește `concurrency` thread-uri
    # - Distribuie `n_requests` cereri între ele
    # - Colectează rezultatele
    
    total_time = time.time() - start_time
    
    # TODO: Calculează și returnează statisticile
    return {
        "total_time": total_time,
        "requests": n_requests,
        "concurrency": concurrency,
        # ... alte statistici
    }
'''
    print(starter_code)
    
    print("""
Sarcini:
1. Completează logica de concurență cu thread-uri
2. Implementează calculul statisticilor
3. Afișează un raport similar cu `ab`
4. Adaugă progress indicator

Utilizare dorită:
  python3 ex_14_03.py --challenge benchmark \\
    --url http://10.0.14.10:8080/ \\
    --requests 100 \\
    --concurrency 10

Output așteptat:
  Server Hostname:        10.0.14.10
  Server Port:            8080
  Document Path:          /
  Concurrency Level:      10
  Time taken for tests:   1.234 seconds
  Complete requests:      100
  Failed requests:        0
  Requests per second:    81.04 [#/sec]
  Time per request:       123.4 [ms] (mean)
  
  Connection Times (ms)
                min   mean    max
  Connect:        1     5     15
  Processing:    10    50    200
  Total:         11    55    215
  
  Percentage of requests served within a certain time (ms)
    50%     45
    90%    120
    99%    200

Bonus:
- Adaugă suport pentru POST cu payload
- Implementează keep-alive connections
- Adaugă export rezultate în JSON/CSV
""")
    
    return 0


# ============================================================================
# MAIN
# ============================================================================

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Exerciții avansate S14")
    parser.add_argument(
        "--challenge",
        choices=["echo", "analyze", "benchmark"],
        required=True,
        help="Alege challenge-ul"
    )
    parser.add_argument("--pcap", help="Fișier pcap pentru analyze")
    parser.add_argument("--url", help="URL pentru benchmark")
    parser.add_argument("--requests", type=int, default=100, help="Număr cereri")
    parser.add_argument("--concurrency", type=int, default=10, help="Concurență")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    
    if args.challenge == "echo":
        return challenge_echo_protocol()
    elif args.challenge == "analyze":
        return challenge_analyze_pcap()
    elif args.challenge == "benchmark":
        return challenge_benchmark()
    else:
        print(f"Challenge necunoscut: {args.challenge}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
