#!/usr/bin/env python3
"""
Exercițiul 9.01 – Încălzirea binară (Nivelul Prezentare - L6)

═══════════════════════════════════════════════════════════════════════════════
OBIECTIVE:
═══════════════════════════════════════════════════════════════════════════════
1. Înțelegerea reprezentării binare a datelor (endianness)
2. Construirea și parsarea unui header de protocol (struct.pack/unpack)
3. Conceptul de framing: cum delimităm mesaje pe un flux TCP
4. Verificarea integrității cu checksum (CRC32)

═══════════════════════════════════════════════════════════════════════════════
CONCEPTE CHEIE:
═══════════════════════════════════════════════════════════════════════════════

1. ENDIANNESS - Ordinea octeților în reprezentarea numerelor multi-byte
   
   Exemplu: Numărul 0x12345678 (4 bytes) în memorie:
   
   Big-Endian (Network Order):    Little-Endian (Intel x86):
   ┌────┬────┬────┬────┐          ┌────┬────┬────┬────┐
   │ 12 │ 34 │ 56 │ 78 │          │ 78 │ 56 │ 34 │ 12 │
   └────┴────┴────┴────┘          └────┴────┴────┴────┘
   addr: 0    1    2    3          addr: 0    1    2    3
   
   - Big-Endian: MSB (Most Significant Byte) la adresa mai mică
   - Little-Endian: LSB (Least Significant Byte) la adresa mai mică
   
2. NETWORK BYTE ORDER - Standard pentru protocoale de rețea
   
   Pentru portabilitate, protocoalele de rețea folosesc Big-Endian.
   Funcții de conversie: htons(), htonl(), ntohs(), ntohl()
   În Python struct: "!" sau ">" pentru big-endian, "<" pentru little-endian

3. FRAMING - Delimitarea mesajelor pe un stream TCP
   
   TCP nu păstrează granițele mesajelor! Un send() de 100 bytes poate fi
   primit ca: recv(30) + recv(50) + recv(20) sau recv(100) sau orice combinație.
   
   Soluția: Header cu lungime
   ┌──────────────┬─────────────────────────────────────┐
   │ Length (N)   │ Payload (N bytes)                   │
   └──────────────┴─────────────────────────────────────┘

4. CHECKSUM/CRC - Verificarea integrității datelor
   
   CRC32 detectează erori de transmisie sau corupere.
   Hash-uri (SHA256) detectează și modificări intenționate.

═══════════════════════════════════════════════════════════════════════════════
STRUCTURA HEADER (acest exercițiu):
═══════════════════════════════════════════════════════════════════════════════

┌─────────┬──────────┬───────┬────────────┬──────────────┐
│ Magic   │ Msg Type │ Flags │ Length     │ CRC32        │
│ 2 bytes │ 1 byte   │ 1 B   │ 4 bytes    │ 4 bytes      │
└─────────┴──────────┴───────┴────────────┴──────────────┘
Total: 12 bytes

- Magic: "S9" - identifică protocolul, ajută la resincronizare
- Msg Type: tipul mesajului (1=data, 2=ack, etc.)
- Flags: biți de opțiuni (ex: compresie, criptare)
- Length: lungimea payload-ului
- CRC32: checksum pentru verificare integritate

═══════════════════════════════════════════════════════════════════════════════
UTILIZARE:
═══════════════════════════════════════════════════════════════════════════════

# Selftest - verificare corectitudine implementare
python3 ex_9_01_endianness.py --selftest

# Demo - afișare detaliată a conversiilor
python3 ex_9_01_endianness.py --demo

# Ambele
python3 ex_9_01_endianness.py --selftest --demo
"""

from __future__ import annotations

import argparse
import struct
import zlib


# =============================================================================
# Configurare Protocol
# =============================================================================

# Format header: magic(2), msg_type(1), flags(1), length(4), crc32(4)
# Total: 12 bytes

# Network byte order (big-endian) - STANDARD pentru protocoale de rețea
HDR_BE = "!2sBBII"

# Little-endian - pentru comparație didactică
HDR_LE = "<2sBBII"

# Magic bytes - identificator protocol
MAGIC = b"S9"

# Tipuri de mesaje (exemplu)
MSG_TYPE_DATA = 1
MSG_TYPE_ACK = 2
MSG_TYPE_ERROR = 3


# =============================================================================
# Funcții de Encoding/Decoding
# =============================================================================

def pack_message(payload: bytes, msg_type: int = 1, flags: int = 0, endian: str = "be") -> bytes:
    """
    Împachetează un payload într-un mesaj cu header.
    
    Procesul:
    1. Calculează lungimea payload-ului
    2. Calculează CRC32 al payload-ului
    3. Construiește header-ul cu struct.pack()
    4. Concatenează header + payload
    
    Args:
        payload: Datele de trimis (bytes)
        msg_type: Tipul mesajului (default: 1)
        flags: Biți de opțiuni (default: 0)
        endian: "be" pentru big-endian (network), "le" pentru little-endian
        
    Returns:
        bytes: Header (12 bytes) + payload
        
    Example:
        >>> msg = pack_message(b"Hello", msg_type=1, endian="be")
        >>> len(msg)
        17  # 12 bytes header + 5 bytes payload
    """
    # Selectăm formatul în funcție de endianness
    if endian == "be":
        fmt = HDR_BE
    elif endian == "le":
        fmt = HDR_LE
    else:
        raise ValueError("endian trebuie să fie 'be' sau 'le'")
    
    length = len(payload)
    
    # CRC32 returnează un întreg signed pe unele platforme
    # & 0xFFFFFFFF asigură că avem un unsigned 32-bit
    crc = zlib.crc32(payload) & 0xFFFFFFFF
    
    # struct.pack() convertește valorile Python în bytes conform formatului
    header = struct.pack(fmt, MAGIC, msg_type, flags, length, crc)
    
    return header + payload


def unpack_message(data: bytes, endian: str = "be") -> dict:
    """
    Despachetează un mesaj cu header.
    
    Procesul:
    1. Extrage header-ul (12 bytes)
    2. Parsează header-ul cu struct.unpack()
    3. Extrage payload-ul conform lungimii din header
    4. Verifică CRC32
    
    Args:
        data: Mesajul complet (header + payload)
        endian: "be" pentru big-endian (network), "le" pentru little-endian
        
    Returns:
        dict cu:
            - magic: bytes (ar trebui să fie b"S9")
            - msg_type: int
            - flags: int
            - length: int
            - crc32: int (din header)
            - crc32_ok: bool (verificare)
            - payload: bytes
    """
    if endian == "be":
        fmt = HDR_BE
    elif endian == "le":
        fmt = HDR_LE
    else:
        raise ValueError("endian trebuie să fie 'be' sau 'le'")
    
    hdr_len = struct.calcsize(fmt)
    
    if len(data) < hdr_len:
        raise ValueError(f"Date insuficiente pentru header: {len(data)} < {hdr_len}")
    
    # Parsează header-ul
    magic, msg_type, flags, length, crc = struct.unpack(fmt, data[:hdr_len])
    
    # Extrage payload-ul
    payload = data[hdr_len:hdr_len + length]
    
    # Verifică CRC
    calc_crc = zlib.crc32(payload) & 0xFFFFFFFF
    
    return {
        "magic": magic,
        "msg_type": msg_type,
        "flags": flags,
        "length": length,
        "crc32": crc,
        "crc32_ok": (calc_crc == crc),
        "payload": payload,
    }


# =============================================================================
# Demo - Vizualizare diferențe endianness
# =============================================================================

def demo():
    """
    Demonstrație vizuală a diferențelor între Big-Endian și Little-Endian.
    """
    print("═" * 70)
    print("  DEMO: Endianness și Framing Binar (Nivelul Prezentare - L6)")
    print("═" * 70)
    
    # Payload cu caractere UTF-8 pentru a demonstra și codarea
    payload = "Salut, S9 – UTF‑8 ✓ România".encode("utf-8")
    
    print(f"\n▶ Payload original:")
    print(f"  Text: 'Salut, S9 – UTF‑8 ✓ România'")
    print(f"  Bytes ({len(payload)}): {payload}")
    
    # Împachetăm în ambele formate
    m_be = pack_message(payload, msg_type=2, flags=0xA5, endian="be")
    m_le = pack_message(payload, msg_type=2, flags=0xA5, endian="le")
    
    print(f"\n▶ Lungime header: {struct.calcsize(HDR_BE)} bytes")
    print(f"  Lungime mesaj total: {len(m_be)} bytes")
    
    print("\n" + "─" * 70)
    print("  COMPARAȚIE HEADER: Big-Endian vs Little-Endian")
    print("─" * 70)
    
    # Afișăm header-urile byte cu byte
    print("\n  Big-Endian (Network Order):")
    print("  ", end="")
    for i, b in enumerate(m_be[:12]):
        print(f"{b:02x} ", end="")
        if i == 1:
            print(" | ", end="")  # După magic
        elif i == 3:
            print(" | ", end="")  # După flags
        elif i == 7:
            print(" | ", end="")  # După length
    print()
    print("  ↑↑         ↑  ↑   ↑──────────↑   ↑──────────────────↑")
    print("  magic    type flags  length          crc32")
    
    print("\n  Little-Endian:")
    print("  ", end="")
    for i, b in enumerate(m_le[:12]):
        print(f"{b:02x} ", end="")
        if i == 1:
            print(" | ", end="")
        elif i == 3:
            print(" | ", end="")
        elif i == 7:
            print(" | ", end="")
    print()
    
    # Demonstrăm diferența concretă la câmpul length
    print("\n" + "─" * 70)
    print("  FOCUS: Câmpul Length (4 bytes)")
    print("─" * 70)
    print(f"\n  Valoare: {len(payload)} (0x{len(payload):08x})")
    print()
    print("  Big-Endian bytes:    ", end="")
    for b in m_be[4:8]:
        print(f"0x{b:02x} ", end="")
    print(f"  → citit de la stânga: {len(payload)}")
    
    print("  Little-Endian bytes: ", end="")
    for b in m_le[4:8]:
        print(f"0x{b:02x} ", end="")
    print(f"  → citit de la dreapta: {len(payload)}")
    
    # Parsăm corect
    print("\n" + "─" * 70)
    print("  PARSARE CORECTĂ")
    print("─" * 70)
    
    parsed_be = unpack_message(m_be, endian="be")
    print(f"\n  Big-Endian parsat cu format BE:")
    print(f"    magic: {parsed_be['magic']}")
    print(f"    msg_type: {parsed_be['msg_type']}")
    print(f"    flags: 0x{parsed_be['flags']:02x}")
    print(f"    length: {parsed_be['length']}")
    print(f"    crc32_ok: {parsed_be['crc32_ok']}")
    
    # Demonstrăm EROAREA clasică: endianness greșit
    print("\n" + "─" * 70)
    print("  ⚠ EROARE CLASICĂ: Endianness greșit la parsare!")
    print("─" * 70)
    
    wrong = unpack_message(m_be, endian="le")  # BE data, LE format - GREȘIT!
    
    print(f"\n  Mesaj BE parsat cu format LE:")
    print(f"    length: {wrong['length']}")
    print(f"      (ar trebui să fie {len(payload)}!)")
    print(f"    crc32_ok: {wrong['crc32_ok']}")
    print(f"      (CRC-ul nu se potrivește - datele par corupte!)")
    
    # Calculăm ce length s-ar obține
    # Little-endian interpretează bytes în ordine inversă
    be_length_bytes = struct.pack("!I", len(payload))
    wrong_length = struct.unpack("<I", be_length_bytes)[0]
    print(f"\n  Explicație: {len(payload)} în BE = bytes {list(be_length_bytes)}")
    print(f"    Interpretat ca LE: {wrong_length}")
    
    print("\n" + "═" * 70)
    print("  CONCLUZIE: Întotdeauna folosiți NETWORK BYTE ORDER (Big-Endian)")
    print("  în protocoalele de rețea pentru portabilitate!")
    print("═" * 70)


# =============================================================================
# Self-test - Verificare corectitudine
# =============================================================================

def selftest():
    """
    Verifică corectitudinea implementării prin teste automate.
    """
    print("═" * 50)
    print("  SELF-TEST: Verificare implementare")
    print("═" * 50)
    
    # Test 1: Payload simplu
    print("\n▶ Test 1: Payload simplu...")
    p1 = b"abcd" * 10
    for endian in ["be", "le"]:
        m = pack_message(p1, msg_type=1, flags=0, endian=endian)
        u = unpack_message(m, endian=endian)
        assert u["magic"] == MAGIC, f"Magic greșit: {u['magic']}"
        assert u["payload"] == p1, "Payload greșit"
        assert u["crc32_ok"], "CRC greșit"
        assert u["length"] == len(p1), f"Length greșit: {u['length']} != {len(p1)}"
    print("   ✓ OK")
    
    # Test 2: Payload gol
    print("▶ Test 2: Payload gol...")
    m = pack_message(b"", endian="be")
    u = unpack_message(m, endian="be")
    assert u["length"] == 0
    assert u["crc32_ok"]
    print("   ✓ OK")
    
    # Test 3: Payload mare
    print("▶ Test 3: Payload mare (64KB)...")
    p3 = bytes(range(256)) * 256  # 64KB
    m = pack_message(p3, endian="be")
    u = unpack_message(m, endian="be")
    assert u["payload"] == p3
    assert u["crc32_ok"]
    print("   ✓ OK")
    
    # Test 4: Flags
    print("▶ Test 4: Toate flag-urile (0xFF)...")
    m = pack_message(b"test", flags=0xFF, endian="be")
    u = unpack_message(m, endian="be")
    assert u["flags"] == 0xFF
    print("   ✓ OK")
    
    # Test 5: Toate tipurile de mesaj
    print("▶ Test 5: Tipuri de mesaj (0-255)...")
    for mt in [0, 1, 127, 255]:
        m = pack_message(b"x", msg_type=mt, endian="be")
        u = unpack_message(m, endian="be")
        assert u["msg_type"] == mt, f"msg_type greșit: {u['msg_type']} != {mt}"
    print("   ✓ OK")
    
    # Test 6: UTF-8
    print("▶ Test 6: Payload UTF-8 (caractere românești)...")
    utf8_text = "ăâîșțĂÂÎȘȚ – România ✓".encode("utf-8")
    m = pack_message(utf8_text, endian="be")
    u = unpack_message(m, endian="be")
    assert u["payload"] == utf8_text
    assert u["payload"].decode("utf-8") == "ăâîșțĂÂÎȘȚ – România ✓"
    print("   ✓ OK")
    
    print("\n" + "═" * 50)
    print("  [OK] Toate testele au trecut!")
    print("═" * 50)


# =============================================================================
# Main
# =============================================================================

def main():
    ap = argparse.ArgumentParser(
        description="Exercițiu L6: Endianness și Framing Binar",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemple:
  %(prog)s --selftest        Verificare corectitudine
  %(prog)s --demo            Demo vizual endianness
  %(prog)s --selftest --demo Ambele
        """
    )
    ap.add_argument("--demo", action="store_true", help="Rulează demo-ul vizual")
    ap.add_argument("--selftest", action="store_true", help="Rulează testele automate")
    args = ap.parse_args()
    
    if not (args.selftest or args.demo):
        ap.print_help()
        print("\n[!] Specifică --selftest și/sau --demo pentru a rula.")
        return
    
    if args.selftest:
        selftest()
        print()
    
    if args.demo:
        demo()


if __name__ == "__main__":
    main()
