#!/usr/bin/env python3
"""
net_utils.py - Utilități pentru networking
Săptămâna 14 - Recapitulare și Integrare
Rețele de Calculatoare

Funcții helper pentru:
- Validare și conversie adrese IP
- Calculul subnet-urilor
- Parsare output comenzi networking
- Formatare și logging
"""

import re
import socket
import struct
import subprocess
import logging
from typing import Tuple, List, Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime


# =============================================================================
# CONFIGURARE LOGGING
# =============================================================================

def setup_logging(
    name: str = "netutils",
    level: int = logging.INFO,
    fmt: str = "%(asctime)s [%(levelname)s] %(message)s"
) -> logging.Logger:
    """Configurează și returnează un logger."""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setLevel(level)
        handler.setFormatter(logging.Formatter(fmt, datefmt="%H:%M:%S"))
        logger.addHandler(handler)
    
    return logger


# =============================================================================
# VALIDARE ADRESE IP
# =============================================================================

def is_valid_ipv4(ip: str) -> bool:
    """
    Verifică dacă un string este o adresă IPv4 validă.
    
    Args:
        ip: String de verificat
        
    Returns:
        True dacă este IPv4 valid, False altfel
        
    Examples:
        >>> is_valid_ipv4("192.168.1.1")
        True
        >>> is_valid_ipv4("256.1.1.1")
        False
    """
    try:
        socket.inet_aton(ip)
        return True
    except socket.error:
        return False


def is_valid_mac(mac: str) -> bool:
    """
    Verifică dacă un string este o adresă MAC validă.
    
    Acceptă formatele:
    - aa:bb:cc:dd:ee:ff
    - aa-bb-cc-dd-ee-ff
    - aabbccddeeff
    
    Args:
        mac: String de verificat
        
    Returns:
        True dacă este MAC valid, False altfel
    """
    # Normalizare: elimină separatorii
    mac_clean = mac.replace(":", "").replace("-", "").lower()
    
    if len(mac_clean) != 12:
        return False
    
    try:
        int(mac_clean, 16)
        return True
    except ValueError:
        return False


def is_valid_port(port: int) -> bool:
    """Verifică dacă un port este valid (1-65535)."""
    return isinstance(port, int) and 1 <= port <= 65535


# =============================================================================
# CONVERSII IP
# =============================================================================

def ip_to_int(ip: str) -> int:
    """
    Convertește adresă IPv4 în integer.
    
    Args:
        ip: Adresă IPv4 (ex: "192.168.1.1")
        
    Returns:
        Reprezentarea ca integer (ex: 3232235777)
    """
    return struct.unpack("!I", socket.inet_aton(ip))[0]


def int_to_ip(num: int) -> str:
    """
    Convertește integer în adresă IPv4.
    
    Args:
        num: Integer (ex: 3232235777)
        
    Returns:
        Adresă IPv4 (ex: "192.168.1.1")
    """
    return socket.inet_ntoa(struct.pack("!I", num))


def ip_to_binary(ip: str) -> str:
    """
    Convertește adresă IPv4 în reprezentare binară.
    
    Args:
        ip: Adresă IPv4 (ex: "192.168.1.1")
        
    Returns:
        String binar cu puncte (ex: "11000000.10101000.00000001.00000001")
    """
    octets = ip.split(".")
    return ".".join(format(int(o), "08b") for o in octets)


# =============================================================================
# CALCUL SUBNETS
# =============================================================================

@dataclass
class SubnetInfo:
    """Informații despre un subnet."""
    network: str
    broadcast: str
    first_host: str
    last_host: str
    netmask: str
    wildcard: str
    prefix: int
    total_hosts: int
    usable_hosts: int


def parse_cidr(cidr: str) -> Tuple[str, int]:
    """
    Parsează notație CIDR în adresă și prefix.
    
    Args:
        cidr: Notație CIDR (ex: "192.168.1.0/24")
        
    Returns:
        Tuple (ip, prefix)
        
    Raises:
        ValueError: Dacă formatul este invalid
    """
    if "/" not in cidr:
        raise ValueError(f"Invalid CIDR notation: {cidr}")
    
    parts = cidr.split("/")
    if len(parts) != 2:
        raise ValueError(f"Invalid CIDR notation: {cidr}")
    
    ip, prefix_str = parts
    
    if not is_valid_ipv4(ip):
        raise ValueError(f"Invalid IP address: {ip}")
    
    try:
        prefix = int(prefix_str)
    except ValueError:
        raise ValueError(f"Invalid prefix: {prefix_str}")
    
    if not 0 <= prefix <= 32:
        raise ValueError(f"Prefix must be 0-32, got: {prefix}")
    
    return ip, prefix


def calculate_subnet(cidr: str) -> SubnetInfo:
    """
    Calculează informațiile complete despre un subnet.
    
    Args:
        cidr: Notație CIDR (ex: "192.168.1.0/24")
        
    Returns:
        SubnetInfo cu toate detaliile subnet-ului
    """
    ip, prefix = parse_cidr(cidr)
    
    # Calculează masca
    mask_int = (0xFFFFFFFF << (32 - prefix)) & 0xFFFFFFFF
    netmask = int_to_ip(mask_int)
    wildcard = int_to_ip(~mask_int & 0xFFFFFFFF)
    
    # Calculează network și broadcast
    ip_int = ip_to_int(ip)
    network_int = ip_int & mask_int
    broadcast_int = network_int | (~mask_int & 0xFFFFFFFF)
    
    network = int_to_ip(network_int)
    broadcast = int_to_ip(broadcast_int)
    
    # Calculează primul și ultimul host
    total_hosts = 2 ** (32 - prefix)
    
    if prefix == 32:
        first_host = last_host = network
        usable_hosts = 1
    elif prefix == 31:
        first_host = network
        last_host = broadcast
        usable_hosts = 2
    else:
        first_host = int_to_ip(network_int + 1)
        last_host = int_to_ip(broadcast_int - 1)
        usable_hosts = total_hosts - 2
    
    return SubnetInfo(
        network=network,
        broadcast=broadcast,
        first_host=first_host,
        last_host=last_host,
        netmask=netmask,
        wildcard=wildcard,
        prefix=prefix,
        total_hosts=total_hosts,
        usable_hosts=usable_hosts
    )


def is_ip_in_subnet(ip: str, cidr: str) -> bool:
    """
    Verifică dacă o adresă IP aparține unui subnet.
    
    Args:
        ip: Adresă IP de verificat
        cidr: Subnet în notație CIDR
        
    Returns:
        True dacă IP-ul este în subnet
    """
    subnet = calculate_subnet(cidr)
    ip_int = ip_to_int(ip)
    network_int = ip_to_int(subnet.network)
    broadcast_int = ip_to_int(subnet.broadcast)
    
    return network_int <= ip_int <= broadcast_int


# =============================================================================
# PARSARE OUTPUT COMENZI
# =============================================================================

def parse_ping_output(output: str) -> Dict[str, Any]:
    """
    Parsează output-ul comenzii ping.
    
    Args:
        output: Output text de la ping
        
    Returns:
        Dict cu: packets_sent, packets_received, loss_percent, 
                 rtt_min, rtt_avg, rtt_max (dacă disponibile)
    """
    result: Dict[str, Any] = {
        "packets_sent": 0,
        "packets_received": 0,
        "loss_percent": 100.0,
        "rtt_min": None,
        "rtt_avg": None,
        "rtt_max": None
    }
    
    # Caută statisticile de pachete
    # Format: "3 packets transmitted, 3 received, 0% packet loss"
    pkt_match = re.search(
        r"(\d+) packets transmitted, (\d+) (?:packets )?received, (\d+(?:\.\d+)?)% packet loss",
        output
    )
    if pkt_match:
        result["packets_sent"] = int(pkt_match.group(1))
        result["packets_received"] = int(pkt_match.group(2))
        result["loss_percent"] = float(pkt_match.group(3))
    
    # Caută statisticile RTT
    # Format: "rtt min/avg/max/mdev = 0.123/0.456/0.789/0.111 ms"
    rtt_match = re.search(
        r"rtt min/avg/max/mdev = ([\d.]+)/([\d.]+)/([\d.]+)/([\d.]+) ms",
        output
    )
    if rtt_match:
        result["rtt_min"] = float(rtt_match.group(1))
        result["rtt_avg"] = float(rtt_match.group(2))
        result["rtt_max"] = float(rtt_match.group(3))
    
    return result


def parse_netstat_output(output: str) -> List[Dict[str, str]]:
    """
    Parsează output-ul comenzii netstat -tlnp sau ss -tlnp.
    
    Args:
        output: Output text
        
    Returns:
        List de dict-uri cu: protocol, local_addr, local_port, state, process
    """
    connections = []
    lines = output.strip().split("\n")
    
    for line in lines[1:]:  # Skip header
        parts = line.split()
        if len(parts) < 4:
            continue
        
        # Parsează adresa locală
        local = parts[3] if len(parts) > 3 else ""
        if ":" in local:
            addr, port = local.rsplit(":", 1)
        else:
            addr, port = local, ""
        
        conn = {
            "protocol": parts[0] if parts else "",
            "local_addr": addr.strip("[]"),
            "local_port": port,
            "state": parts[5] if len(parts) > 5 else "",
            "process": parts[-1] if len(parts) > 6 else ""
        }
        connections.append(conn)
    
    return connections


# =============================================================================
# EXECUTARE COMENZI
# =============================================================================

def run_command(
    cmd: List[str],
    timeout: int = 30,
    capture_stderr: bool = True
) -> Tuple[int, str, str]:
    """
    Execută o comandă și returnează rezultatul.
    
    Args:
        cmd: Lista de argumente comandă
        timeout: Timeout în secunde
        capture_stderr: Dacă să captureze stderr
        
    Returns:
        Tuple (return_code, stdout, stderr)
    """
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", f"Comanda a depășit timeout-ul după {timeout}s"
    except FileNotFoundError:
        return -1, "", f"Comandă negăsită: {cmd[0]}"
    except Exception as e:
        return -1, "", str(e)


def check_port_open(host: str, port: int, timeout: float = 3.0) -> bool:
    """
    Verifică dacă un port este deschis.
    
    Args:
        host: Hostname sau IP
        port: Număr port
        timeout: Timeout în secunde
        
    Returns:
        True dacă portul este deschis
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except socket.error:
        return False


def resolve_hostname(hostname: str) -> Optional[str]:
    """
    Rezolvă un hostname la adresa IP.
    
    Args:
        hostname: Numele de rezolvat
        
    Returns:
        Adresa IP sau None dacă rezolvarea eșuează
    """
    try:
        return socket.gethostbyname(hostname)
    except socket.gaierror:
        return None


# =============================================================================
# FORMATARE OUTPUT
# =============================================================================

def format_bytes(num_bytes: int) -> str:
    """
    Formatează un număr de bytes în format human-readable.
    
    Args:
        num_bytes: Numărul de bytes
        
    Returns:
        String formatat (ex: "1.5 KB", "2.3 MB")
    """
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if abs(num_bytes) < 1024.0:
            return f"{num_bytes:.1f} {unit}"
        num_bytes /= 1024.0
    return f"{num_bytes:.1f} PB"


def format_duration(seconds: float) -> str:
    """
    Formatează o durată în secunde în format human-readable.
    
    Args:
        seconds: Durata în secunde
        
    Returns:
        String formatat (ex: "1m 30s", "2h 15m")
    """
    if seconds < 1:
        return f"{seconds*1000:.1f}ms"
    elif seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{mins}m {secs}s"
    else:
        hours = int(seconds // 3600)
        mins = int((seconds % 3600) // 60)
        return f"{hours}h {mins}m"


def format_table(
    headers: List[str],
    rows: List[List[str]],
    separator: str = " | "
) -> str:
    """
    Formatează date într-un tabel text aliniat.
    
    Args:
        headers: Lista de headere
        rows: Lista de rânduri (fiecare rând e o listă de valori)
        separator: Separatorul între coloane
        
    Returns:
        Tabelul formatat ca string
    """
    # Calculează lățimile coloanelor
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            if i < len(widths):
                widths[i] = max(widths[i], len(str(cell)))
    
    # Formatează header
    header_line = separator.join(h.ljust(widths[i]) for i, h in enumerate(headers))
    separator_line = "-" * len(header_line)
    
    # Formatează rânduri
    row_lines = []
    for row in rows:
        cells = [str(cell).ljust(widths[i]) for i, cell in enumerate(row)]
        row_lines.append(separator.join(cells))
    
    return "\n".join([header_line, separator_line] + row_lines)


# =============================================================================
# TIMESTAMP-URI
# =============================================================================

def get_timestamp() -> str:
    """Returnează timestamp ISO format."""
    return datetime.now().isoformat(timespec="seconds")


def get_timestamp_filename() -> str:
    """Returnează timestamp pentru nume fișier (fără caractere speciale)."""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


# =============================================================================
# MAIN - PENTRU TESTARE
# =============================================================================

if __name__ == "__main__":
    # Teste rapide
    print("=== Test Validare IP ===")
    print(f"192.168.1.1 valid: {is_valid_ipv4('192.168.1.1')}")
    print(f"256.1.1.1 valid: {is_valid_ipv4('256.1.1.1')}")
    
    print("\n=== Test Validare MAC ===")
    print(f"aa:bb:cc:dd:ee:ff valid: {is_valid_mac('aa:bb:cc:dd:ee:ff')}")
    print(f"aabbccddeeff valid: {is_valid_mac('aabbccddeeff')}")
    
    print("\n=== Test Conversie IP ===")
    ip = "192.168.1.1"
    num = ip_to_int(ip)
    print(f"{ip} -> {num} -> {int_to_ip(num)}")
    print(f"Binar: {ip_to_binary(ip)}")
    
    print("\n=== Test Calcul Subnet ===")
    subnet = calculate_subnet("192.168.1.0/24")
    print(f"Rețea: {subnet.network}")
    print(f"Broadcast: {subnet.broadcast}")
    print(f"Primul host: {subnet.first_host}")
    print(f"Ultimul host: {subnet.last_host}")
    print(f"Hosturi utilizabile: {subnet.usable_hosts}")
    
    print("\n=== Test Verificare Port ===")
    print(f"localhost:22 deschis: {check_port_open('localhost', 22, 1)}")
    
    print("\n=== Test Formatare ===")
    print(f"1536 bytes: {format_bytes(1536)}")
    print(f"125.5 secunde: {format_duration(125.5)}")
    
    print("\n=== Test Tabel ===")
    headers = ["Host", "IP", "Status"]
    rows = [
        ["app1", "10.0.0.2", "ACTIV"],
        ["app2", "10.0.0.3", "ACTIV"],
        ["client", "10.0.0.1", "ACTIV"]
    ]
    print(format_table(headers, rows))
