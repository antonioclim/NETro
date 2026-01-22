#!/usr/bin/env python3
"""
Utilitare comune pentru Starterkit S9 – Protocoale de Fișiere

Acest modul centralizează funcții reutilizabile:
- Framing binar (header + payload)
- Compresie / decompresie
- Hashing (SHA256, CRC32)
- Recepție exactă de bytes
- Conversii endianness

Folosit de: ex_9_01_endianness.py, ex_9_02_pseudo_ftp.py
Licență: MIT
"""

from __future__ import annotations

import gzip
import hashlib
import socket
import struct
import zlib
from typing import Optional, Tuple


# =============================================================================
# Constante Protocol
# =============================================================================

# Week 9 Port Plan
WEEK = 9
WEEK_PORT_BASE = 5100 + 100 * (WEEK - 1)  # 5900
TCP_APP_PORT = WEEK_PORT_BASE  # 5900
UDP_APP_PORT = WEEK_PORT_BASE + 1  # 5901
FTP_CONTROL_PORT = 2121
FTP_PASV_START = 30000
FTP_PASV_END = 30010

# Week 9 IP Plan
NETWORK_PREFIX = f"10.0.{WEEK}"  # 10.0.9
GATEWAY = f"{NETWORK_PREFIX}.1"
HOST_BASE = f"{NETWORK_PREFIX}.11"  # h1=.11, h2=.12, etc.
SERVER_IP = f"{NETWORK_PREFIX}.100"

# Framing constants
BUFFER_SIZE = 8192
DEFAULT_TIMEOUT = 30

# Binary header format: Magic(2) + Version(1) + Flags(1) + Length(4) + CRC32(4) = 12 bytes
HEADER_FORMAT = "!2sBBII"
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)
MAGIC = b"PF"  # Pseudo-FTP
VERSION = 1
FLAG_GZIP = 0x01
FLAG_SHA256 = 0x02


# =============================================================================
# Framing Functions (L6 - Prezentare)
# =============================================================================

def pack_data(payload: bytes, use_gzip: bool = False, include_sha256: bool = False) -> bytes:
    """
    Împachetează payload-ul cu header binar pentru transfer.
    
    Demonstrează conceptele L6 (Prezentare):
    - Framing: header cu lungime pentru delimitare mesaje
    - Compresie: opțional gzip
    - Integritate: CRC32 checksum
    
    Args:
        payload: Datele de împachetat
        use_gzip: Activează compresie gzip
        include_sha256: Adaugă hash SHA256 după payload
        
    Returns:
        bytes: Header (12 bytes) + payload (opțional comprimat)
    """
    flags = 0
    
    # Compresie opțională
    if use_gzip and len(payload) > 0:
        payload = gzip.compress(payload)
        flags |= FLAG_GZIP
    
    # SHA256 opțional (adăugat la sfârșitul payload-ului)
    if include_sha256:
        sha = hashlib.sha256(payload).digest()
        payload = payload + sha
        flags |= FLAG_SHA256
    
    length = len(payload)
    crc = zlib.crc32(payload) & 0xFFFFFFFF
    
    header = struct.pack(HEADER_FORMAT, MAGIC, VERSION, flags, length, crc)
    return header + payload


def unpack_data(data: bytes) -> Tuple[bytes, dict]:
    """
    Despachetează datele primite cu header binar.
    
    Args:
        data: Mesajul complet (header + payload)
        
    Returns:
        Tuple[bytes, dict]: (payload decomprimat, metadata)
        
    Raises:
        ValueError: Dacă datele sunt invalide
    """
    if len(data) < HEADER_SIZE:
        raise ValueError(f"Date insuficiente: {len(data)} < {HEADER_SIZE}")
    
    magic, version, flags, length, crc = struct.unpack(HEADER_FORMAT, data[:HEADER_SIZE])
    
    if magic != MAGIC:
        raise ValueError(f"Magic invalid: {magic} (expected {MAGIC})")
    
    payload = data[HEADER_SIZE:HEADER_SIZE + length]
    
    if len(payload) != length:
        raise ValueError(f"Payload incomplet: {len(payload)} != {length}")
    
    # Verificare CRC
    calc_crc = zlib.crc32(payload) & 0xFFFFFFFF
    if calc_crc != crc:
        raise ValueError(f"CRC invalid: {calc_crc:08x} != {crc:08x}")
    
    # Extragere SHA256 dacă prezent
    sha256_hash = None
    if flags & FLAG_SHA256:
        sha256_hash = payload[-32:]
        payload = payload[:-32]
    
    # Decompresie dacă necesar
    if flags & FLAG_GZIP:
        payload = gzip.decompress(payload)
    
    return payload, {
        "version": version,
        "flags": flags,
        "compressed": bool(flags & FLAG_GZIP),
        "has_sha256": bool(flags & FLAG_SHA256),
        "sha256": sha256_hash.hex() if sha256_hash else None,
        "wire_length": length,
        "crc": crc,
    }


# =============================================================================
# Socket Utilities
# =============================================================================

def recv_all(sock: socket.socket, length: int, timeout: Optional[float] = None) -> bytes:
    """
    Primește exact `length` bytes de pe socket.
    
    Args:
        sock: Socket deschis
        length: Numărul exact de bytes de primit
        timeout: Timeout opțional în secunde
        
    Returns:
        bytes: Exact `length` bytes
        
    Raises:
        ConnectionError: Conexiune închisă prematur
        socket.timeout: Timeout depășit
    """
    if timeout:
        sock.settimeout(timeout)
    
    data = b""
    while len(data) < length:
        chunk = sock.recv(min(length - len(data), BUFFER_SIZE))
        if not chunk:
            raise ConnectionError(f"Conexiune închisă după {len(data)}/{length} bytes")
        data += chunk
    
    return data


def recv_framed(sock: socket.socket, timeout: Optional[float] = None) -> Tuple[bytes, dict]:
    """
    Primește un mesaj complet cu framing (header + payload).
    
    Args:
        sock: Socket deschis
        timeout: Timeout opțional
        
    Returns:
        Tuple[bytes, dict]: (payload, metadata)
    """
    # Citim header-ul
    header = recv_all(sock, HEADER_SIZE, timeout)
    magic, version, flags, length, crc = struct.unpack(HEADER_FORMAT, header)
    
    if magic != MAGIC:
        raise ValueError(f"Magic invalid: {magic}")
    
    # Citim payload-ul
    payload = recv_all(sock, length, timeout) if length > 0 else b""
    
    return unpack_data(header + payload)


def send_framed(sock: socket.socket, payload: bytes, use_gzip: bool = False) -> int:
    """
    Trimite un mesaj cu framing complet.
    
    Args:
        sock: Socket deschis
        payload: Datele de trimis
        use_gzip: Activează compresie
        
    Returns:
        int: Numărul de bytes trimiși
    """
    packed = pack_data(payload, use_gzip=use_gzip)
    sock.sendall(packed)
    return len(packed)


# =============================================================================
# Hashing Utilities
# =============================================================================

def compute_sha256(data: bytes) -> str:
    """Calculează hash SHA256 și returnează hex string."""
    return hashlib.sha256(data).hexdigest()


def compute_crc32(data: bytes) -> int:
    """Calculează CRC32 și returnează unsigned int."""
    return zlib.crc32(data) & 0xFFFFFFFF


def verify_sha256(data: bytes, expected_hash: str) -> bool:
    """Verifică hash SHA256."""
    return compute_sha256(data) == expected_hash.lower()


# =============================================================================
# Compression Utilities
# =============================================================================

def compress_gzip(data: bytes, level: int = 9) -> bytes:
    """Comprimă cu gzip."""
    return gzip.compress(data, compresslevel=level)


def decompress_gzip(data: bytes) -> bytes:
    """Decomprimă gzip."""
    return gzip.decompress(data)


def compression_ratio(original: bytes, compressed: bytes) -> float:
    """Calculează raportul de compresie."""
    if len(original) == 0:
        return 1.0
    return len(compressed) / len(original)


# =============================================================================
# Endianness Helpers
# =============================================================================

def to_network_order_u32(value: int) -> bytes:
    """Convertește un uint32 la network byte order (big-endian)."""
    return struct.pack("!I", value)


def from_network_order_u32(data: bytes) -> int:
    """Convertește din network byte order la int."""
    return struct.unpack("!I", data)[0]


def to_network_order_u16(value: int) -> bytes:
    """Convertește un uint16 la network byte order."""
    return struct.pack("!H", value)


def from_network_order_u16(data: bytes) -> int:
    """Convertește din network byte order la int."""
    return struct.unpack("!H", data)[0]


# =============================================================================
# Self-test
# =============================================================================

def _selftest():
    """Verifică funcționalitatea modulului."""
    print("═" * 50)
    print("  net_utils.py - Self-test")
    print("═" * 50)
    
    # Test pack/unpack
    print("\n▶ Test pack_data / unpack_data...")
    original = b"Hello, S9! \xc8\x9a\xc4\x83"  # Include UTF-8
    packed = pack_data(original, use_gzip=True)
    unpacked, meta = unpack_data(packed)
    assert unpacked == original, "Payload mismatch"
    assert meta["compressed"] is True
    print("   ✓ pack/unpack OK")
    
    # Test fără compresie
    print("▶ Test fără compresie...")
    packed = pack_data(original, use_gzip=False)
    unpacked, meta = unpack_data(packed)
    assert unpacked == original
    assert meta["compressed"] is False
    print("   ✓ OK")
    
    # Test hashing
    print("▶ Test SHA256...")
    h = compute_sha256(b"test")
    assert len(h) == 64
    assert verify_sha256(b"test", h)
    print("   ✓ OK")
    
    # Test endianness
    print("▶ Test endianness helpers...")
    val = 0x12345678
    net_bytes = to_network_order_u32(val)
    assert net_bytes == b"\x12\x34\x56\x78"
    assert from_network_order_u32(net_bytes) == val
    print("   ✓ OK")
    
    print("\n═" * 50)
    print("  Toate testele au trecut!")
    print("═" * 50)


if __name__ == "__main__":
    _selftest()
