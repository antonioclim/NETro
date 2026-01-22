#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
  Exercițiul 11.03 – Client DNS Didactic
═══════════════════════════════════════════════════════════════════════════════

SCOP DIDACTIC:
  - Înțelegerea structurii pachetelor DNS (RFC 1035)
  - Implementarea manuală a unui query DNS
  - Parsarea răspunsurilor DNS pentru diferite tipuri de înregistrări
  - Vizualizarea procesului de rezoluție DNS

FUNCȚIONALITĂȚI:
  - Suport pentru tipuri: A, AAAA, MX, NS, CNAME, TXT, SOA
  - Verbose mode pentru debugging
  - Afișare hexdump al pachetelor
  - Suport pentru server DNS custom

ARHITECTURA PACHETULUI DNS:
  ┌─────────────────────────────────────────┐
  │              HEADER (12 bytes)          │
  │  ID | Flags | QDCOUNT | ANCOUNT | ...   │
  ├─────────────────────────────────────────┤
  │              QUESTION SECTION           │
  │  QNAME | QTYPE | QCLASS                 │
  ├─────────────────────────────────────────┤
  │              ANSWER SECTION             │
  │  NAME | TYPE | CLASS | TTL | RDATA      │
  └─────────────────────────────────────────┘

RULARE:
  python3 ex_11_03_dns_client.py --query google.com --type A
  python3 ex_11_03_dns_client.py --query google.com --type MX
  python3 ex_11_03_dns_client.py --query ase.ro --type NS -v
═══════════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations

import argparse
import socket
import struct
import random
import sys
from dataclasses import dataclass
from typing import List, Tuple, Optional

# Constante DNS
DNS_PORT = 53
DEFAULT_DNS_SERVER = "8.8.8.8"

# Tipuri de înregistrări DNS (RFC 1035 + extensii)
RECORD_TYPES = {
    "A": 1,        # IPv4 address
    "NS": 2,       # Nameserver
    "CNAME": 5,    # Canonical name
    "SOA": 6,      # Start of Authority
    "MX": 15,      # Mail exchange
    "TXT": 16,     # Text record
    "AAAA": 28,    # IPv6 address
}

RECORD_TYPES_REVERSE = {v: k for k, v in RECORD_TYPES.items()}

# Clase DNS
DNS_CLASS_IN = 1  # Internet

# Flags
DNS_FLAG_QR = 0x8000      # Query/Response
DNS_FLAG_RD = 0x0100      # Recursion Desired
DNS_FLAG_RA = 0x0080      # Recursion Available
DNS_FLAG_AA = 0x0400      # Authoritative Answer

# Response codes
RCODE_NAMES = {
    0: "NOERROR",
    1: "FORMERR",
    2: "SERVFAIL",
    3: "NXDOMAIN",
    4: "NOTIMP",
    5: "REFUSED",
}


@dataclass
class DNSRecord:
    """Reprezentarea unei înregistrări DNS."""
    name: str
    type_: int
    class_: int
    ttl: int
    rdata: str
    
    @property
    def type_name(self) -> str:
        return RECORD_TYPES_REVERSE.get(self.type_, f"TYPE{self.type_}")


# ═══════════════════════════════════════════════════════════════════════════════
# SUBGOAL: ENCODE_DOMAIN_NAME
# Transformă "www.google.com" în format DNS wire: \x03www\x06google\x03com\x00
# 
# Pași:
#   1. Sparge domeniul în labels după "."
#   2. Pentru fiecare label: adaugă 1 byte lungime + bytes-ii label-ului
#   3. Termină cu byte-ul 0x00
# ═══════════════════════════════════════════════════════════════════════════════
def encode_domain_name(domain: str) -> bytes:
    """
    Codifică un nume de domeniu în format DNS.
    
    Exemplu: "www.google.com" → b'\x03www\x06google\x03com\x00'
    
    Format: fiecare label este prefixat cu lungimea sa, terminat cu 0x00.
    """
    result = b""
    for label in domain.split("."):
        if label:
            encoded_label = label.encode("ascii")
            result += struct.pack("B", len(encoded_label)) + encoded_label
    result += b"\x00"
    return result


# ═══════════════════════════════════════════════════════════════════════════════
# SUBGOAL: DECODE_DOMAIN_NAME
# Inversul operației de encode, cu suport pentru compresie DNS (pointeri)
# 
# Pași:
#   1. Citește byte-ul de lungime
#   2. Dacă primii 2 biți = 11 (0xC0 mask) → e un pointer, urmează offset-ul
#   3. Dacă lungime = 0 → sfârșitul numelui
#   4. Altfel → citește N bytes ca label și continuă
# ═══════════════════════════════════════════════════════════════════════════════
def decode_domain_name(data: bytes, offset: int) -> Tuple[str, int]:
    """
    Decodifică un nume de domeniu din răspuns DNS.
    
    Gestionează compresia pointerilor (RFC 1035, secțiunea 4.1.4):
    - Dacă primii 2 biți sunt 11, următorii 14 biți sunt offset-ul pointerului.
    
    Returns: (domain_name, new_offset)
    """
    labels = []
    original_offset = offset
    jumped = False
    
    while True:
        if offset >= len(data):
            break
            
        length = data[offset]
        
        # Verificăm pointer de compresie (primii 2 biți = 11)
        if (length & 0xC0) == 0xC0:
            if not jumped:
                original_offset = offset + 2
            # Calculăm offset-ul pointerului (14 biți)
            pointer = ((length & 0x3F) << 8) | data[offset + 1]
            offset = pointer
            jumped = True
            continue
        
        if length == 0:
            offset += 1
            break
        
        offset += 1
        labels.append(data[offset:offset + length].decode("ascii", errors="replace"))
        offset += length
    
    return ".".join(labels), original_offset if jumped else offset


# ═══════════════════════════════════════════════════════════════════════════════
# SUBGOAL: BUILD_DNS_QUERY
# Construiește pachetul DNS complet (header + question section)
# 
# Pași:
#   1. Creează header-ul de 12 bytes: ID, Flags, QDCOUNT=1, restul=0
#   2. Creează question section: QNAME (encodat) + QTYPE + QCLASS
#   3. Concatenează header + question
# ═══════════════════════════════════════════════════════════════════════════════
def build_dns_query(domain: str, record_type: int, transaction_id: int) -> bytes:
    """
    Construiește un pachet DNS query.
    
    Header (12 bytes):
      - ID (2): identificator tranzacție
      - Flags (2): QR=0 (query), RD=1 (recursion desired)
      - QDCOUNT (2): 1 (o singură întrebare)
      - ANCOUNT (2): 0
      - NSCOUNT (2): 0
      - ARCOUNT (2): 0
    
    Question:
      - QNAME: domeniu codificat
      - QTYPE (2): tip înregistrare
      - QCLASS (2): IN (1)
    """
    # Header
    flags = DNS_FLAG_RD  # Recursion Desired
    header = struct.pack(
        ">HHHHHH",
        transaction_id,  # ID
        flags,           # Flags
        1,               # QDCOUNT
        0,               # ANCOUNT
        0,               # NSCOUNT
        0                # ARCOUNT
    )
    
    # Question section
    question = encode_domain_name(domain)
    question += struct.pack(">HH", record_type, DNS_CLASS_IN)
    
    return header + question


# ═══════════════════════════════════════════════════════════════════════════════
# SUBGOAL: PARSE_DNS_RESPONSE
# Extrage informațiile din pachetul de răspuns DNS
# 
# Pași:
#   1. Parsează header-ul (12 bytes) → extrage flags, counts, rcode
#   2. Sari peste question section (QDCOUNT întrebări)
#   3. Parsează answer/authority/additional sections
#   4. Pentru fiecare record: decode name, citește TYPE/CLASS/TTL/RDLENGTH, parse RDATA
# ═══════════════════════════════════════════════════════════════════════════════
def parse_dns_response(data: bytes, verbose: bool = False) -> Tuple[int, List[DNSRecord]]:
    """
    Parsează răspunsul DNS.
    
    Returns: (rcode, list of records)
    """
    if len(data) < 12:
        raise ValueError("Răspuns DNS prea scurt")
    
    # Parse header
    (trans_id, flags, qdcount, ancount, nscount, arcount) = struct.unpack(">HHHHHH", data[:12])
    
    rcode = flags & 0x000F
    is_response = bool(flags & DNS_FLAG_QR)
    is_authoritative = bool(flags & DNS_FLAG_AA)
    recursion_available = bool(flags & DNS_FLAG_RA)
    
    if verbose:
        print(f"\n[DEBUG] Header:")
        print(f"  Transaction ID: 0x{trans_id:04X}")
        print(f"  Is Response: {is_response}")
        print(f"  Is Authoritative: {is_authoritative}")
        print(f"  Recursion Available: {recursion_available}")
        print(f"  RCODE: {rcode} ({RCODE_NAMES.get(rcode, 'UNKNOWN')})")
        print(f"  Questions: {qdcount}, Answers: {ancount}, NS: {nscount}, Additional: {arcount}")
    
    offset = 12
    
    # Skip question section
    for _ in range(qdcount):
        name, offset = decode_domain_name(data, offset)
        offset += 4  # QTYPE + QCLASS
    
    # Parse answer section
    records: List[DNSRecord] = []
    
    for section_name, count in [("Answer", ancount), ("Authority", nscount), ("Additional", arcount)]:
        for _ in range(count):
            if offset >= len(data):
                break
                
            name, offset = decode_domain_name(data, offset)
            
            if offset + 10 > len(data):
                break
            
            (rtype, rclass, ttl, rdlength) = struct.unpack(">HHIH", data[offset:offset + 10])
            offset += 10
            
            rdata_raw = data[offset:offset + rdlength]
            offset += rdlength
            
            # Parse RDATA based on type
            rdata = parse_rdata(rtype, rdata_raw, data)
            
            records.append(DNSRecord(
                name=name,
                type_=rtype,
                class_=rclass,
                ttl=ttl,
                rdata=rdata
            ))
    
    return rcode, records


def parse_rdata(rtype: int, rdata: bytes, full_packet: bytes) -> str:
    """Parsează RDATA în funcție de tipul înregistrării."""
    
    if rtype == RECORD_TYPES["A"]:  # IPv4
        if len(rdata) == 4:
            return ".".join(str(b) for b in rdata)
        return f"<invalid A: {rdata.hex()}>"
    
    elif rtype == RECORD_TYPES["AAAA"]:  # IPv6
        if len(rdata) == 16:
            parts = [f"{rdata[i]:02x}{rdata[i+1]:02x}" for i in range(0, 16, 2)]
            return ":".join(parts)
        return f"<invalid AAAA: {rdata.hex()}>"
    
    elif rtype == RECORD_TYPES["MX"]:  # Mail exchange
        if len(rdata) >= 2:
            preference = struct.unpack(">H", rdata[:2])[0]
            # MX exchange poate folosi compresie, așa că trebuie să parsăm cu referință la pachetul complet
            # Simplificare: presupunem că nu e compresie în RDATA
            exchange = decode_name_from_rdata(rdata[2:])
            return f"{preference} {exchange}"
        return f"<invalid MX: {rdata.hex()}>"
    
    elif rtype == RECORD_TYPES["NS"]:  # Nameserver
        return decode_name_from_rdata(rdata)
    
    elif rtype == RECORD_TYPES["CNAME"]:  # Canonical name
        return decode_name_from_rdata(rdata)
    
    elif rtype == RECORD_TYPES["TXT"]:  # Text
        # TXT: unul sau mai multe <length><text> perechi
        texts = []
        pos = 0
        while pos < len(rdata):
            length = rdata[pos]
            pos += 1
            if pos + length <= len(rdata):
                texts.append(rdata[pos:pos + length].decode("utf-8", errors="replace"))
                pos += length
        return " ".join(f'"{t}"' for t in texts)
    
    elif rtype == RECORD_TYPES["SOA"]:  # Start of Authority
        try:
            mname = decode_name_from_rdata(rdata)
            return f"SOA {mname} ..."
        except:
            return f"<SOA: {rdata.hex()[:40]}...>"
    
    else:
        return f"<{RECORD_TYPES_REVERSE.get(rtype, f'TYPE{rtype}')}: {rdata.hex()}>"


def decode_name_from_rdata(data: bytes) -> str:
    """Decodifică un nume de domeniu din RDATA (fără compresie)."""
    labels = []
    pos = 0
    while pos < len(data):
        length = data[pos]
        if length == 0:
            break
        pos += 1
        if pos + length <= len(data):
            labels.append(data[pos:pos + length].decode("ascii", errors="replace"))
            pos += length
    return ".".join(labels)


def hexdump(data: bytes, prefix: str = "") -> str:
    """Formatează date binare ca hexdump."""
    lines = []
    for i in range(0, len(data), 16):
        chunk = data[i:i + 16]
        hex_part = " ".join(f"{b:02X}" for b in chunk)
        ascii_part = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
        lines.append(f"{prefix}{i:04X}  {hex_part:<48}  {ascii_part}")
    return "\n".join(lines)


def dns_query(domain: str, record_type: str, server: str, timeout: float, verbose: bool) -> None:
    """Execută query DNS și afișează rezultatele."""
    
    if record_type not in RECORD_TYPES:
        print(f"[ERROR] Tip necunoscut: {record_type}")
        print(f"Tipuri suportate: {', '.join(RECORD_TYPES.keys())}")
        sys.exit(1)
    
    rtype = RECORD_TYPES[record_type]
    transaction_id = random.randint(0, 0xFFFF)
    
    print(f"\n{'═' * 60}")
    print(f"DNS Query: {domain} ({record_type})")
    print(f"Server: {server}:{DNS_PORT}")
    print(f"{'═' * 60}")
    
    # Construire query
    query = build_dns_query(domain, rtype, transaction_id)
    
    if verbose:
        print(f"\n[DEBUG] Query packet ({len(query)} bytes):")
        print(hexdump(query, "  "))
    
    # Trimitere și primire
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(timeout)
        
        sock.sendto(query, (server, DNS_PORT))
        response, addr = sock.recvfrom(4096)
        
        if verbose:
            print(f"\n[DEBUG] Response packet ({len(response)} bytes):")
            print(hexdump(response, "  "))
        
        sock.close()
        
    except socket.timeout:
        print(f"\n[ERROR] Timeout după {timeout} secunde")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] {e}")
        sys.exit(1)
    
    # Parsare răspuns
    try:
        rcode, records = parse_dns_response(response, verbose)
    except Exception as e:
        print(f"\n[ERROR] Parsare răspuns: {e}")
        sys.exit(1)
    
    # Afișare rezultate
    print(f"\nStatus: {RCODE_NAMES.get(rcode, f'RCODE={rcode}')}")
    
    if rcode != 0:
        print(f"\n[!] Query eșuat cu cod: {RCODE_NAMES.get(rcode, rcode)}")
        return
    
    if not records:
        print("\n[!] Nicio înregistrare găsită")
        return
    
    print(f"\nÎnregistrări ({len(records)}):")
    print("-" * 60)
    
    for rec in records:
        print(f"  {rec.name}")
        print(f"    Tip: {rec.type_name}")
        print(f"    TTL: {rec.ttl}s")
        print(f"    Date: {rec.rdata}")
        print()


def main():
    parser = argparse.ArgumentParser(
        description="Client DNS didactic",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemple:
  %(prog)s --query google.com --type A
  %(prog)s --query google.com --type MX
  %(prog)s --query ase.ro --type NS -v

Tipuri suportate: A, AAAA, MX, NS, CNAME, TXT, SOA
        """
    )
    parser.add_argument("--query", "-q", required=True,
                        help="Domeniu de interogat")
    parser.add_argument("--type", "-t", default="A",
                        help="Tip înregistrare (default: A)")
    parser.add_argument("--server", "-s", default=DEFAULT_DNS_SERVER,
                        help=f"Server DNS (default: {DEFAULT_DNS_SERVER})")
    parser.add_argument("--timeout", type=float, default=5.0,
                        help="Timeout în secunde (default: 5)")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Afișare detaliată (debug)")
    
    args = parser.parse_args()
    dns_query(args.query, args.type.upper(), args.server, args.timeout, args.verbose)


if __name__ == "__main__":
    main()
