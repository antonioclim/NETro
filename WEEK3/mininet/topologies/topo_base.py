#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Topologie de bază S3: Un switch, trei hosts, un domeniu L2.

ARHITECTURĂ:
    ┌───────┐        ┌───────┐        ┌───────┐
    │  h1   │        │  h2   │        │  h3   │
    │10.0.3.1        │10.0.3.2        │10.0.3.3
    └───┬───┘        └───┬───┘        └───┬───┘
        │                │                │
        └────────────────┼────────────────┘
                         │
                     ┌───┴───┐
                     │  s1   │
                     │ Switch│
                     └───────┘

    Subnet: 10.0.3.0/24
    Broadcast: 10.0.3.255 sau 255.255.255.255
    
SCOP DIDACTIC:
    1. Demonstrează comunicarea UDP broadcast în același domeniu L2
    2. Experimentează UDP multicast cu join la grup
    3. Testează server TCP multiclient cu clienți simultani
    4. Analizează trafic cu tcpdump/tshark

RULARE:
    # Mod interactiv (CLI Mininet)
    sudo python3 topo_base.py --cli

    # Mod test automat (verificări de conectivitate)
    sudo python3 topo_base.py --test

AUTOR: Starter Kit Rețele S3
DATA: 2025
LICENȚĂ: MIT
"""

from __future__ import annotations

import argparse
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mininet.net import Mininet

try:
    from mininet.cli import CLI
    from mininet.link import TCLink
    from mininet.log import setLogLevel, info
    from mininet.net import Mininet
    from mininet.node import OVSSwitch
    from mininet.topo import Topo
    MININET_AVAILABLE = True
except ImportError:
    MININET_AVAILABLE = False


# ═══════════════════════════════════════════════════════════════════════════
# WEEK 3 — Plan IP Standard: 10.0.<WEEK>.0/24
# ═══════════════════════════════════════════════════════════════════════════
WEEK = 3
SUBNET_PREFIX = f"10.0.{WEEK}"  # 10.0.3.x pentru WEEK 3
SUBNET_MASK = 24
NUM_HOSTS = 3

# Porturi standard: WEEK_PORT_BASE = 5100 + 100*(WEEK-1) = 5300
WEEK_PORT_BASE = 5100 + 100 * (WEEK - 1)
UDP_BCAST_PORT = WEEK_PORT_BASE + 7     # 5307
UDP_MCAST_PORT = WEEK_PORT_BASE + 1     # 5301
TCP_TUNNEL_PORT = WEEK_PORT_BASE + 90   # 5390


class Week3BaseTopo(Topo):
    """Topologie simplă cu un switch și N hosts."""
    
    def __init__(self, num_hosts: int = NUM_HOSTS, *args, **kwargs):
        self.num_hosts = num_hosts
        super().__init__(*args, **kwargs)
    
    def build(self) -> None:
        s1 = self.addSwitch("s1", failMode='standalone')
        for i in range(1, self.num_hosts + 1):
            host = self.addHost(f"h{i}", ip=f"{SUBNET_PREFIX}.{i}/{SUBNET_MASK}")
            self.addLink(host, s1, cls=TCLink, bw=100)


def run_tests(net: "Mininet") -> bool:
    """Rulează teste automate."""
    info("\n═══ TESTE AUTOMATE ═══\n\n")
    
    packet_loss = net.pingAll(timeout=1)
    if packet_loss == 0:
        info("✓ PASS: Conectivitate completă\n")
        return True
    else:
        info(f"✗ FAIL: {packet_loss}% pierdere\n")
        return False


def print_hints() -> None:
    info("\n╔═══════════════════════════════════════════════╗\n")
    info("║         TOPOLOGIE S3 BAZĂ PREGĂTITĂ           ║\n")
    info("╠═══════════════════════════════════════════════╣\n")
    info("║  h1: 10.0.3.1  h2: 10.0.3.2  h3: 10.0.3.3    ║\n")
    info("║  Broadcast: 255.255.255.255 / 10.0.3.255     ║\n")
    info("╠═══════════════════════════════════════════════╣\n")
    info("║  pingall, xterm h1 h2, h1 tcpdump -ni h1-eth0 ║\n")
    info("╚═══════════════════════════════════════════════╝\n")


def main(argv: list[str]) -> int:
    if not MININET_AVAILABLE:
        print("EROARE: Mininet nu e instalat. Rulați cu sudo.")
        return 1
    
    parser = argparse.ArgumentParser(description="Topologie S3 bază")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--cli", action="store_true", help="Mod interactiv")
    mode.add_argument("--test", action="store_true", help="Teste automate")
    parser.add_argument("--hosts", "-n", type=int, default=NUM_HOSTS)
    args = parser.parse_args(argv)
    
    setLogLevel("warning")
    topo = Week3BaseTopo(num_hosts=args.hosts)
    net = Mininet(topo=topo, switch=OVSSwitch, link=TCLink, 
                  controller=None, autoSetMacs=True, autoStaticArp=True)
    
    try:
        net.start()
        if args.test:
            return 0 if run_tests(net) else 1
        setLogLevel("info")
        print_hints()
        CLI(net)
        return 0
    finally:
        net.stop()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
