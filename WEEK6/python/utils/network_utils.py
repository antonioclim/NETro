#!/usr/bin/env python3
"""
Utilități comune pentru aplicațiile de rețea - Săptămâna 6

Acest modul consolidează funcționalitățile comune pentru a evita
duplicarea codului între diferitele aplicații client-server.

Plan de porturi Week 6:
    TCP_APP_PORT = 9090
    UDP_APP_PORT = 9091
    WEEK_PORT_BASE = 5600 (pentru porturi custom)
    WEEK_PORT_RANGE = 5600..5699

Plan IP Week 6:
    SUBNET = 10.0.6.0/24
    GATEWAY = 10.0.6.1
    H1 = 10.0.6.11
    H2 = 10.0.6.12
    H3 = 10.0.6.13
    SERVER = 10.0.6.100

Rezolvix&Hypotheticalandrei | MIT License | ASE-CSIE 2025-2026
"""

from __future__ import annotations

import logging
import socket
import sys
from dataclasses import dataclass
from typing import Optional


# ═══════════════════════════════════════════════════════════════════════════
# CONSTANTE WEEK 6
# ═══════════════════════════════════════════════════════════════════════════

WEEK = 6

# Plan IP
SUBNET = f"10.0.{WEEK}.0/24"
GATEWAY = f"10.0.{WEEK}.1"
H1_IP = f"10.0.{WEEK}.11"
H2_IP = f"10.0.{WEEK}.12"
H3_IP = f"10.0.{WEEK}.13"
SERVER_IP = f"10.0.{WEEK}.100"

# Plan porturi (evită privilegii root)
TCP_APP_PORT = 9090
UDP_APP_PORT = 9091
HTTP_PORT = 8080
PROXY_PORT = 8888
DNS_PORT = 5353
FTP_PORT = 2121
SSH_PORT = 2222
CONTROLLER_PORT = 6633

# Porturi custom pentru Week 6
WEEK_PORT_BASE = 5100 + 100 * (WEEK - 1)  # 5600
WEEK_PORT_RANGE = range(WEEK_PORT_BASE, WEEK_PORT_BASE + 100)

# Timeout-uri default
DEFAULT_TIMEOUT = 5
DEFAULT_BUFFER_SIZE = 4096


# ═══════════════════════════════════════════════════════════════════════════
# LOGGING
# ═══════════════════════════════════════════════════════════════════════════

def setup_logging(
    name: str = "network_app",
    level: int = logging.INFO,
    fmt: str = "[%(asctime)s] %(levelname)s: %(message)s"
) -> logging.Logger:
    """
    Configurează logging consistent pentru aplicații.
    
    Args:
        name: Numele logger-ului
        level: Nivelul de logging (default: INFO)
        fmt: Formatul mesajelor
    
    Returns:
        Logger configurat
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(fmt, datefmt="%H:%M:%S"))
        logger.addHandler(handler)
    
    return logger


# ═══════════════════════════════════════════════════════════════════════════
# SOCKET HELPERS
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class SocketConfig:
    """Configurație pentru socket."""
    host: str = "0.0.0.0"
    port: int = TCP_APP_PORT
    timeout: float = DEFAULT_TIMEOUT
    buffer_size: int = DEFAULT_BUFFER_SIZE
    reuse_addr: bool = True


def create_tcp_socket(config: Optional[SocketConfig] = None) -> socket.socket:
    """
    Creează un socket TCP configurat.
    
    Args:
        config: Configurația socketului (opțional)
    
    Returns:
        Socket TCP configurat
    """
    if config is None:
        config = SocketConfig()
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    if config.reuse_addr:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    if config.timeout > 0:
        sock.settimeout(config.timeout)
    
    return sock


def create_udp_socket(config: Optional[SocketConfig] = None) -> socket.socket:
    """
    Creează un socket UDP configurat.
    
    Args:
        config: Configurația socketului (opțional)
    
    Returns:
        Socket UDP configurat
    """
    if config is None:
        config = SocketConfig(port=UDP_APP_PORT)
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    if config.reuse_addr:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    if config.timeout > 0:
        sock.settimeout(config.timeout)
    
    return sock


# ═══════════════════════════════════════════════════════════════════════════
# VALIDARE
# ═══════════════════════════════════════════════════════════════════════════

def is_valid_ip(ip: str) -> bool:
    """Verifică dacă un string este o adresă IPv4 validă."""
    try:
        socket.inet_aton(ip)
        return True
    except socket.error:
        return False


def is_valid_port(port: int) -> bool:
    """Verifică dacă un port este în intervalul valid."""
    return 1 <= port <= 65535


def is_week_port(port: int) -> bool:
    """Verifică dacă portul este în intervalul custom al săptămânii."""
    return port in WEEK_PORT_RANGE


# ═══════════════════════════════════════════════════════════════════════════
# ARGPARSE HELPERS
# ═══════════════════════════════════════════════════════════════════════════

def add_common_args(parser, include_port: bool = True, include_host: bool = True):
    """
    Adaugă argumente comune la un parser argparse.
    
    Args:
        parser: ArgumentParser instance
        include_port: Include argumentul --port
        include_host: Include argumentul --host/--bind
    """
    if include_host:
        parser.add_argument(
            "--host", "--bind",
            default="0.0.0.0",
            help=f"Adresa de bind/connect (default: 0.0.0.0)"
        )
    
    if include_port:
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


# ═══════════════════════════════════════════════════════════════════════════
# INFORMAȚII WEEK
# ═══════════════════════════════════════════════════════════════════════════

def print_week_info():
    """Afișează informații despre configurația săptămânii."""
    print(f"""
╔══════════════════════════════════════════════════════════╗
║  Săptămâna {WEEK}: SDN - Software-Defined Networking        ║
╠══════════════════════════════════════════════════════════╣
║  Plan IP:                                                ║
║    Subnet:  {SUBNET:<20}                       ║
║    Gateway: {GATEWAY:<20}                       ║
║    h1:      {H1_IP:<20}                       ║
║    h2:      {H2_IP:<20}                       ║
║    h3:      {H3_IP:<20}                       ║
║    Server:  {SERVER_IP:<20}                       ║
╠══════════════════════════════════════════════════════════╣
║  Plan Porturi:                                           ║
║    TCP App:     {TCP_APP_PORT:<10}                              ║
║    UDP App:     {UDP_APP_PORT:<10}                              ║
║    Controller:  {CONTROLLER_PORT:<10}                              ║
║    Week Base:   {WEEK_PORT_BASE:<10} (range: {WEEK_PORT_BASE}-{WEEK_PORT_BASE+99})    ║
╚══════════════════════════════════════════════════════════╝
""")


if __name__ == "__main__":
    print_week_info()
