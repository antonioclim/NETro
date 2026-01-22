#!/usr/bin/env python3
"""
Utilitare comune pentru exercițiile de rețea - Săptămâna 1
==========================================================
Rețele de Calculatoare
ASE București / CSIE

Acest modul conține funcții reutilizabile pentru:
- Configurare logging consistent
- Validare adrese IP și porturi
- Helper-e pentru socket-uri
- Formatare output

Utilizare:
    from python.utils.net_utils import setup_logging, validate_port, format_bytes
"""

import socket
import logging
import argparse
import sys
import re
from typing import Optional, Tuple
from datetime import datetime

# =============================================================================
# CONSTANTE STANDARD (conform plan transversal)
# =============================================================================

# Plan IP pentru Week 1
WEEK = 1
NETWORK_BASE = f"10.0.{WEEK}.0"
NETWORK_MASK = 24
GATEWAY = f"10.0.{WEEK}.1"
HOST_BASE = f"10.0.{WEEK}"  # .11, .12, .13 pentru h1, h2, h3
SERVER_IP = f"10.0.{WEEK}.100"

# Porturi standard
TCP_APP_PORT = 9090
UDP_APP_PORT = 9091
HTTP_PORT = 8080
PROXY_PORT = 8888
DNS_PORT = 5353
FTP_PORT = 2121
SSH_PORT = 2222

# Porturi custom pentru Week 1
WEEK_PORT_BASE = 5100 + 100 * (WEEK - 1)  # 5100 pentru Week 1
WEEK_PORT_RANGE = range(WEEK_PORT_BASE, WEEK_PORT_BASE + 100)

# Timeouts
DEFAULT_TIMEOUT = 5.0
CONNECT_TIMEOUT = 3.0
READ_TIMEOUT = 10.0


# =============================================================================
# LOGGING
# =============================================================================

def setup_logging(
    name: str = "netlab",
    level: int = logging.INFO,
    format_string: Optional[str] = None
) -> logging.Logger:
    """
    Configurează logging consistent pentru exerciții.
    
    Args:
        name: Numele logger-ului
        level: Nivelul de logging (DEBUG, INFO, WARNING, ERROR)
        format_string: Format custom (opțional)
    
    Returns:
        Logger configurat
    
    Exemplu:
        >>> log = setup_logging("ex_01")
        >>> log.info("Server pornit pe port 9090")
    """
    if format_string is None:
        format_string = "[%(asctime)s] %(levelname)-7s %(message)s"
    
    logging.basicConfig(
        level=level,
        format=format_string,
        datefmt="%H:%M:%S",
        stream=sys.stderr
    )
    
    return logging.getLogger(name)


# =============================================================================
# VALIDARE
# =============================================================================

def validate_ip(ip: str) -> bool:
    """
    Validează o adresă IPv4.
    
    Args:
        ip: String cu adresa IP
    
    Returns:
        True dacă adresa e validă
    """
    pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    if not re.match(pattern, ip):
        return False
    
    octets = ip.split('.')
    return all(0 <= int(o) <= 255 for o in octets)


def validate_port(port: int) -> bool:
    """
    Validează un număr de port.
    
    Args:
        port: Numărul portului
    
    Returns:
        True dacă portul e valid (1-65535)
    """
    return 1 <= port <= 65535


def validate_port_unprivileged(port: int) -> bool:
    """
    Validează că portul nu necesită privilegii root.
    
    Args:
        port: Numărul portului
    
    Returns:
        True dacă portul e >= 1024
    """
    return 1024 <= port <= 65535


def check_port_available(host: str, port: int) -> bool:
    """
    Verifică dacă un port este disponibil pentru bind.
    
    Args:
        host: Adresa IP
        port: Numărul portului
    
    Returns:
        True dacă portul e liber
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1.0)
    try:
        sock.bind((host, port))
        sock.close()
        return True
    except OSError:
        return False


# =============================================================================
# SOCKET HELPERS
# =============================================================================

def create_tcp_socket(
    timeout: float = DEFAULT_TIMEOUT,
    reuse_addr: bool = True
) -> socket.socket:
    """
    Creează un socket TCP configurat standard.
    
    Args:
        timeout: Timeout pentru operații (secunde)
        reuse_addr: Permite reutilizarea imediată a adresei
    
    Returns:
        Socket TCP configurat
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    if reuse_addr:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    return sock


def create_udp_socket(timeout: float = DEFAULT_TIMEOUT) -> socket.socket:
    """
    Creează un socket UDP configurat standard.
    
    Args:
        timeout: Timeout pentru operații (secunde)
    
    Returns:
        Socket UDP configurat
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(timeout)
    return sock


def get_local_ip() -> str:
    """
    Obține adresa IP locală a mașinii.
    
    Returns:
        Adresa IP locală (sau 127.0.0.1 dacă nu se poate determina)
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(("8.8.8.8", 80))
        local_ip = sock.getsockname()[0]
        sock.close()
        return local_ip
    except Exception:
        return "127.0.0.1"


# =============================================================================
# FORMATARE OUTPUT
# =============================================================================

def format_bytes(size: int) -> str:
    """
    Formatează dimensiunea în format human-readable.
    
    Args:
        size: Dimensiune în bytes
    
    Returns:
        String formatat (ex: "1.5 KB", "2.3 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if abs(size) < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} TB"


def format_timestamp(dt: Optional[datetime] = None) -> str:
    """
    Formatează timestamp pentru logging.
    
    Args:
        dt: Datetime object (sau now dacă None)
    
    Returns:
        String formatat HH:MM:SS.mmm
    """
    if dt is None:
        dt = datetime.now()
    return dt.strftime("%H:%M:%S.%f")[:-3]


def format_address(addr: Tuple[str, int]) -> str:
    """
    Formatează o adresă socket pentru afișare.
    
    Args:
        addr: Tuple (host, port)
    
    Returns:
        String "host:port"
    """
    return f"{addr[0]}:{addr[1]}"


# =============================================================================
# ARGPARSE HELPERS
# =============================================================================

def add_common_args(parser: argparse.ArgumentParser) -> None:
    """
    Adaugă argumente comune tuturor exercițiilor.
    
    Args:
        parser: ArgumentParser instance
    """
    parser.add_argument(
        "--host", "-H",
        default="127.0.0.1",
        help="Adresa IP (default: 127.0.0.1)"
    )
    parser.add_argument(
        "--port", "-p",
        type=int,
        default=TCP_APP_PORT,
        help=f"Port (default: {TCP_APP_PORT})"
    )
    parser.add_argument(
        "--timeout", "-t",
        type=float,
        default=DEFAULT_TIMEOUT,
        help=f"Timeout în secunde (default: {DEFAULT_TIMEOUT})"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Output detaliat"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Rulează auto-teste"
    )


# =============================================================================
# SELF-TEST
# =============================================================================

def run_self_test() -> bool:
    """Rulează auto-testele pentru acest modul."""
    print("\n" + "="*50)
    print(" AUTO-TEST net_utils.py ".center(50, "="))
    print("="*50 + "\n")
    
    tests_passed = 0
    tests_total = 0
    
    # Test validate_ip
    tests_total += 1
    print("[TEST] validate_ip...", end=" ")
    if (validate_ip("192.168.1.1") and 
        validate_ip("10.0.1.100") and 
        not validate_ip("256.1.1.1") and
        not validate_ip("abc.def.ghi.jkl")):
        print("✓ PASS")
        tests_passed += 1
    else:
        print("✗ FAIL")
    
    # Test validate_port
    tests_total += 1
    print("[TEST] validate_port...", end=" ")
    if (validate_port(80) and 
        validate_port(9090) and 
        not validate_port(0) and
        not validate_port(70000)):
        print("✓ PASS")
        tests_passed += 1
    else:
        print("✗ FAIL")
    
    # Test format_bytes
    tests_total += 1
    print("[TEST] format_bytes...", end=" ")
    if (format_bytes(1024) == "1.0 KB" and
        format_bytes(1048576) == "1.0 MB"):
        print("✓ PASS")
        tests_passed += 1
    else:
        print("✗ FAIL")
    
    # Test create_tcp_socket
    tests_total += 1
    print("[TEST] create_tcp_socket...", end=" ")
    try:
        sock = create_tcp_socket()
        sock.close()
        print("✓ PASS")
        tests_passed += 1
    except Exception as e:
        print(f"✗ FAIL ({e})")
    
    # Test get_local_ip
    tests_total += 1
    print("[TEST] get_local_ip...", end=" ")
    ip = get_local_ip()
    if validate_ip(ip):
        print(f"✓ PASS ({ip})")
        tests_passed += 1
    else:
        print("✗ FAIL")
    
    print(f"\nRezultat: {tests_passed}/{tests_total} teste trecute")
    return tests_passed == tests_total


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        success = run_self_test()
        sys.exit(0 if success else 1)
    else:
        print(__doc__)
        print("\nConstante disponibile:")
        print(f"  NETWORK: {NETWORK_BASE}/{NETWORK_MASK}")
        print(f"  TCP_APP_PORT: {TCP_APP_PORT}")
        print(f"  UDP_APP_PORT: {UDP_APP_PORT}")
        print(f"  WEEK_PORT_RANGE: {WEEK_PORT_BASE}-{WEEK_PORT_BASE+99}")
        print("\nRulează cu --test pentru auto-verificare")
