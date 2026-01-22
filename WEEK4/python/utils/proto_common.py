#!/usr/bin/env python3
"""
Definiții comune pentru protocoalele din Săptămâna 4.

Acest modul definește structurile și funcțiile pentru:
1. Protocol TCP text (length-prefixed)
2. Protocol TCP binar (header fix + CRC32)
3. Protocol UDP senzor (datagram binar + CRC32)

Concepte cheie ilustrate:
- Framing: delimitarea mesajelor într-un stream TCP
- Serializare: reprezentarea datelor structurate în bytes
- Detecție erori: CRC32 pentru verificarea integrității
- Endianness: ordinea bytes în reprezentări multi-byte (Big-Endian în rețea)
"""
from __future__ import annotations
import struct
import zlib
from dataclasses import dataclass
from typing import Tuple


# ==============================================================================
# PROTOCOL BINAR TCP
# ==============================================================================
# Header format (14 bytes total):
#   magic(2)      - "NP" (Network Protocol)
#   version(1)    - versiunea protocolului (1)
#   type(1)       - tipul mesajului (ECHO/PUT/GET/ERR)
#   payload_len(2)- lungimea payload-ului în bytes
#   seq(4)        - sequence number pentru corelație request-response
#   crc32(4)      - checksum pentru header + payload
# ==============================================================================
#
# Notă despre design: Am ales formatul "!2sBBHII" pentru că:
# - "!" = network byte order (toată lumea folosește big-endian în rețea)
# - Header-ul de 14 bytes încape ușor într-un singur segment TCP
# - Sequence number de 4 bytes permite ~4 miliarde de mesaje consecutive
# - CRC pe 4 bytes oferă detecție bună a erorilor fără overhead excesiv
#
# ==============================================================================

BIN_MAGIC = b"NP"
BIN_VERSION = 1

# Format struct: ! = network byte order (big-endian)
# 2s = 2 bytes string, B = unsigned byte, H = unsigned short, I = unsigned int
BIN_HEADER_FMT = "!2sBBHII"
BIN_HEADER_LEN = struct.calcsize(BIN_HEADER_FMT)  # = 14 bytes

# Tipuri de mesaje
TYPE_ECHO_REQ = 1
TYPE_ECHO_RESP = 2
TYPE_PUT_REQ = 3
TYPE_PUT_RESP = 4
TYPE_GET_REQ = 5
TYPE_GET_RESP = 6
TYPE_KEYS_REQ = 7
TYPE_KEYS_RESP = 8
TYPE_COUNT_REQ = 9
TYPE_COUNT_RESP = 10
TYPE_ERR = 255

TYPE_NAMES = {
    TYPE_ECHO_REQ: "ECHO_REQ",
    TYPE_ECHO_RESP: "ECHO_RESP",
    TYPE_PUT_REQ: "PUT_REQ",
    TYPE_PUT_RESP: "PUT_RESP",
    TYPE_GET_REQ: "GET_REQ",
    TYPE_GET_RESP: "GET_RESP",
    TYPE_KEYS_REQ: "KEYS_REQ",
    TYPE_KEYS_RESP: "KEYS_RESP",
    TYPE_COUNT_REQ: "COUNT_REQ",
    TYPE_COUNT_RESP: "COUNT_RESP",
    TYPE_ERR: "ERROR",
}


def crc32(data: bytes) -> int:
    """
    Calculează CRC32 al datelor.
    
    Folosim zlib care e în biblioteca standard - nu trebuie instalat nimic extra.
    Masca & 0xFFFFFFFF forțează rezultat unsigned (Python poate da negativ altfel,
    ceea ce ne-ar încurca la comparații).
    
    Complexitate: O(n) unde n = lungimea datelor
    """
    return zlib.crc32(data) & 0xFFFFFFFF


@dataclass(frozen=True)
class BinHeader:
    """
    Header-ul unui mesaj binar decodat.
    
    frozen=True face instanțele imutabile (best practice pentru date).
    """
    magic: bytes
    version: int
    mtype: int
    payload_len: int
    seq: int
    crc: int
    
    def is_valid_protocol(self) -> bool:
        """Verifică dacă magic și version corespund protocolului nostru."""
        return self.magic == BIN_MAGIC and self.version == BIN_VERSION
    
    @property
    def type_name(self) -> str:
        """Returnează numele tipului pentru debugging."""
        return TYPE_NAMES.get(self.mtype, f"UNKNOWN({self.mtype})")


def pack_bin_message(mtype: int, payload: bytes, seq: int) -> bytes:
    """
    Construiește un mesaj binar complet (header + payload).
    
    Pași:
    1. Validare payload
    2. Construire header fără CRC
    3. Calcul CRC peste header + payload
    4. Reconstruire header cu CRC
    5. Concatenare header + payload
    
    Args:
        mtype: Tipul mesajului (TYPE_*)
        payload: Datele utile (max 65535 bytes)
        seq: Sequence number
        
    Returns:
        bytes: Mesajul complet, gata de trimis
    """
    if not isinstance(payload, (bytes, bytearray)):
        raise TypeError(f"payload must be bytes, got {type(payload)}")
    if len(payload) > 65535:
        raise ValueError(f"payload too large: {len(payload)} > 65535")
    
    # Header parțial (fără CRC) pentru calcul CRC
    header_wo_crc = struct.pack("!2sBBHI", BIN_MAGIC, BIN_VERSION, mtype, len(payload), seq)
    
    # CRC se calculează peste header (fără câmpul CRC) + payload
    msg_crc = crc32(header_wo_crc + payload)
    
    # Header complet cu CRC
    header = struct.pack(BIN_HEADER_FMT, BIN_MAGIC, BIN_VERSION, mtype, len(payload), seq, msg_crc)
    
    return header + payload


def unpack_bin_header(header_bytes: bytes) -> BinHeader:
    """
    Decodează header-ul unui mesaj binar.
    
    Args:
        header_bytes: Exact BIN_HEADER_LEN bytes
        
    Returns:
        BinHeader: Structura decodată
        
    Raises:
        ValueError: Dacă lungimea nu corespunde
    """
    if len(header_bytes) != BIN_HEADER_LEN:
        raise ValueError(f"invalid header length: {len(header_bytes)} != {BIN_HEADER_LEN}")
    
    magic, ver, mtype, plen, seq, crc = struct.unpack(BIN_HEADER_FMT, header_bytes)
    return BinHeader(magic=magic, version=ver, mtype=mtype, payload_len=plen, seq=seq, crc=crc)


def validate_bin_message(header: BinHeader, payload: bytes) -> bool:
    """
    Verifică integritatea unui mesaj folosind CRC32.
    
    Recalculează CRC-ul și compară cu cel din header.
    """
    header_wo_crc = struct.pack("!2sBBHI", header.magic, header.version, header.mtype, header.payload_len, header.seq)
    computed_crc = crc32(header_wo_crc + payload)
    return computed_crc == header.crc


# ==============================================================================
# CODARE PAYLOAD PENTRU PUT/GET
# ==============================================================================
# PUT: key_len(1) + key(N) + value(M)
# GET: key_len(1) + key(N)
# ==============================================================================

def encode_kv(key: str, value: str) -> bytes:
    """Codifică o pereche cheie-valoare pentru PUT."""
    kb = key.encode("utf-8")
    vb = value.encode("utf-8")
    if len(kb) > 255:
        raise ValueError(f"key too long: {len(kb)} > 255")
    return struct.pack("!B", len(kb)) + kb + vb


def decode_kv(payload: bytes) -> Tuple[str, str]:
    """Decodifică o pereche cheie-valoare din payload PUT."""
    if not payload:
        raise ValueError("empty payload")
    klen = payload[0]
    if len(payload) < 1 + klen:
        raise ValueError(f"truncated payload: need {1+klen}, got {len(payload)}")
    key = payload[1:1+klen].decode("utf-8", errors="replace")
    value = payload[1+klen:].decode("utf-8", errors="replace")
    return key, value


def encode_key(key: str) -> bytes:
    """Codifică doar cheia pentru GET."""
    kb = key.encode("utf-8")
    if len(kb) > 255:
        raise ValueError(f"key too long: {len(kb)} > 255")
    return struct.pack("!B", len(kb)) + kb


def decode_key(payload: bytes) -> str:
    """Decodifică cheia din payload GET."""
    if not payload:
        raise ValueError("empty payload")
    klen = payload[0]
    if len(payload) < 1 + klen:
        raise ValueError(f"truncated payload: need {1+klen}, got {len(payload)}")
    return payload[1:1+klen].decode("utf-8", errors="replace")


# ==============================================================================
# PROTOCOL UDP SENZOR
# ==============================================================================
# Datagram format (23 bytes total):
#   version(1)    - versiunea protocolului
#   sensor_id(4)  - identificator unic senzor (unsigned int)
#   temperature(4)- temperatură în °C (float IEEE 754)
#   location(10)  - nume locație (string padding cu \0)
#   crc32(4)      - checksum pentru integritate
# ==============================================================================

UDP_VER = 1
UDP_FMT_WO_CRC = "!BIf10s"  # fără CRC, pentru calcul
UDP_FMT = "!BIf10sI"        # format complet
UDP_LEN = struct.calcsize(UDP_FMT)  # = 23 bytes


def pack_udp_sensor(sensor_id: int, temp_c: float, location: str) -> bytes:
    """
    Construiește un datagram UDP pentru un senzor de temperatură.
    
    Args:
        sensor_id: ID unic al senzorului (0-2^32)
        temp_c: Temperatura în grade Celsius
        location: Numele locației (max 10 caractere)
        
    Returns:
        bytes: Datagram de exact UDP_LEN bytes
    """
    # Truncăm și padding locația la exact 10 bytes
    loc_b = location.encode("utf-8")[:10]
    loc_b = loc_b.ljust(10, b"\x00")
    
    # Construim payload fără CRC
    base = struct.pack(UDP_FMT_WO_CRC, UDP_VER, sensor_id, temp_c, loc_b)
    
    # Calculăm CRC
    c = crc32(base)
    
    # Mesaj complet
    return struct.pack(UDP_FMT, UDP_VER, sensor_id, temp_c, loc_b, c)


def unpack_udp_sensor(data: bytes) -> Tuple[int, int, float, str]:
    """
    Decodifică un datagram UDP de la un senzor.
    
    Args:
        data: Exact UDP_LEN bytes
        
    Returns:
        Tuple de (version, sensor_id, temperature, location)
        
    Raises:
        ValueError: Dacă lungimea e greșită sau CRC nu corespunde
    """
    if len(data) != UDP_LEN:
        raise ValueError(f"invalid datagram length: {len(data)} != {UDP_LEN}")
    
    ver, sensor_id, temp_c, loc_b, received_crc = struct.unpack(UDP_FMT, data)
    
    # Recalculăm CRC pentru verificare
    base = struct.pack(UDP_FMT_WO_CRC, ver, sensor_id, temp_c, loc_b)
    computed_crc = crc32(base)
    
    if computed_crc != received_crc:
        raise ValueError(f"CRC mismatch: computed {computed_crc:08x}, received {received_crc:08x}")
    
    # Decodăm locația și eliminăm padding-ul
    loc = loc_b.decode("utf-8", errors="replace").rstrip("\x00")
    
    return ver, sensor_id, temp_c, loc


def format_sensor_reading(sensor_id: int, temp_c: float, location: str) -> str:
    """Formatează citirea unui senzor pentru afișare."""
    return f"[Sensor {sensor_id:04d}] {location}: {temp_c:+.1f}°C"
