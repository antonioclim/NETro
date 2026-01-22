#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Topologie extinsă S3: Două subrețele + router Linux cu IP forwarding.

ARHITECTURĂ:
                        ┌─────────────────────────────────────┐
                        │              ROUTER (r1)            │
                        │  r1-eth0: 10.0.1.254/24             │
                        │  r1-eth1: 10.0.2.254/24             │
                        │  ip_forward = 1                     │
                        └───────────┬─────────┬───────────────┘
                                    │         │
        ┌───────────────────────────┼─────────┼───────────────────────────┐
        │                           │         │                           │
    ┌───┴───┐                   ┌───┴───┐ ┌───┴───┐                   ┌───┴───┐
    │  a1   │───────────────────│  s1   │ │  s2   │───────────────────│  b1   │
    │10.0.1.1                   │ Switch│ │ Switch│                   │10.0.2.1
    └───────┘                   └───┬───┘ └───┬───┘                   └───────┘
                                    │         │
                                ┌───┴───┐ ┌───┴───┐
                                │  a2   │ │  b2   │
                                │10.0.1.2 │10.0.2.2
                                └───────┘ └───────┘

    SUBNET A (netA): 10.0.1.0/24            SUBNET B (netB): 10.0.2.0/24
    Gateway: 10.0.1.254                      Gateway: 10.0.2.254

SCOP DIDACTIC:
    1. Demonstrează că broadcast-ul NU traversează routerul (limited la L2)
    2. Oferă context pentru TCP tunnel (port-forwarder între subrețele)
    3. Ilustrează conceptul de default gateway și IP forwarding

RULARE:
    # Mod interactiv (CLI Mininet)
    sudo python3 topo_extended.py --cli

    # Mod test automat (pingall + verificări)
    sudo python3 topo_extended.py --test

    # Mod silențios cu comenzi specifice
    sudo python3 topo_extended.py --exec "a1 ping -c 3 b1"

EXPERIMENTE SUGERATE:
    1. Broadcast intra-subnet:
       mininet> a1 python3 python/examples/ex01_udp_broadcast.py send \
           --dst 10.0.1.255 --port 5007 --message "HELLO_A"
       mininet> a2 python3 python/examples/ex01_udp_broadcast.py recv --port 5007
       # Observație: b1 și b2 NU primesc (alt domeniu L2)

    2. Ping cross-subnet:
       mininet> a1 ping -c 3 b1
       # Funcționează prin r1 (IP forwarding activ)

    3. TCP Tunnel (port-forwarder):
       mininet> b1 python3 python/examples/ex04_echo_server.py --listen 0.0.0.0:8080
       mininet> r1 python3 python/examples/ex03_tcp_tunnel.py \
           --listen 0.0.0.0:9090 --target 10.0.2.1:8080
       mininet> a1 bash -c 'echo HELLO | nc 10.0.1.254 9090'
       # Observație: a1 vorbește cu r1:9090, care redirecționează la b1:8080

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
    from mininet.node import Host

# Importuri Mininet (disponibile doar când se rulează cu sudo)
try:
    from mininet.cli import CLI
    from mininet.link import TCLink
    from mininet.log import setLogLevel, info, error
    from mininet.net import Mininet
    from mininet.node import OVSSwitch
    from mininet.topo import Topo
    MININET_AVAILABLE = True
except ImportError:
    MININET_AVAILABLE = False


# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURAȚIE
# ═══════════════════════════════════════════════════════════════════════════

NET_A_PREFIX = "10.0.1"
NET_A_MASK = 24
NET_A_GATEWAY = f"{NET_A_PREFIX}.254"

NET_B_PREFIX = "10.0.2"
NET_B_MASK = 24
NET_B_GATEWAY = f"{NET_B_PREFIX}.254"


# ═══════════════════════════════════════════════════════════════════════════
# TOPOLOGIE
# ═══════════════════════════════════════════════════════════════════════════

class Week3ExtendedTopo(Topo):
    """
    Topologie cu două subrețele și router central.
    
    Noduri:
        - a1, a2: hosts în netA (10.0.1.0/24)
        - b1, b2: hosts în netB (10.0.2.0/24)
        - r1: router Linux (două interfețe, IP forwarding)
        - s1: switch pentru netA
        - s2: switch pentru netB
    """
    
    def build(self) -> None:
        """Construiește topologia."""
        
        # ─── Switch-uri ───
        s1 = self.addSwitch("s1", failMode='standalone')  # netA
        s2 = self.addSwitch("s2", failMode='standalone')  # netB
        
        # ─── Hosts netA ───
        a1 = self.addHost(
            "a1",
            ip=f"{NET_A_PREFIX}.1/{NET_A_MASK}",
            defaultRoute=f"via {NET_A_GATEWAY}"
        )
        a2 = self.addHost(
            "a2",
            ip=f"{NET_A_PREFIX}.2/{NET_A_MASK}",
            defaultRoute=f"via {NET_A_GATEWAY}"
        )
        
        # ─── Hosts netB ───
        b1 = self.addHost(
            "b1",
            ip=f"{NET_B_PREFIX}.1/{NET_B_MASK}",
            defaultRoute=f"via {NET_B_GATEWAY}"
        )
        b2 = self.addHost(
            "b2",
            ip=f"{NET_B_PREFIX}.2/{NET_B_MASK}",
            defaultRoute=f"via {NET_B_GATEWAY}"
        )
        
        # ─── Router (configurat manual în config_router) ───
        r1 = self.addHost("r1")
        
        # ─── Legături netA ───
        self.addLink(a1, s1, cls=TCLink, bw=100)
        self.addLink(a2, s1, cls=TCLink, bw=100)
        self.addLink(r1, s1, cls=TCLink, bw=100)  # r1-eth0 → s1
        
        # ─── Legături netB ───
        self.addLink(b1, s2, cls=TCLink, bw=100)
        self.addLink(b2, s2, cls=TCLink, bw=100)
        self.addLink(r1, s2, cls=TCLink, bw=100)  # r1-eth1 → s2


# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURARE ROUTER
# ═══════════════════════════════════════════════════════════════════════════

def config_router(net: "Mininet") -> None:
    """
    Configurează r1 ca router Linux cu IP forwarding.
    
    Interfețe:
        - r1-eth0: 10.0.1.254/24 (gateway netA)
        - r1-eth1: 10.0.2.254/24 (gateway netB)
    """
    r1: "Host" = net.get("r1")
    
    # Curăță configurația default
    r1.cmd("ip addr flush dev r1-eth0 2>/dev/null || true")
    r1.cmd("ip addr flush dev r1-eth1 2>/dev/null || true")
    
    # Configurează IP-uri
    r1.cmd(f"ip addr add {NET_A_GATEWAY}/{NET_A_MASK} dev r1-eth0")
    r1.cmd(f"ip addr add {NET_B_GATEWAY}/{NET_B_MASK} dev r1-eth1")
    
    # Activează interfețele
    r1.cmd("ip link set r1-eth0 up")
    r1.cmd("ip link set r1-eth1 up")
    
    # CRUCIAL: Activează IP forwarding
    r1.cmd("sysctl -w net.ipv4.ip_forward=1 >/dev/null 2>&1")
    
    # Dezactivează rp_filter (reverse path filtering) pentru a permite forwarding
    r1.cmd("sysctl -w net.ipv4.conf.all.rp_filter=0 >/dev/null 2>&1")
    r1.cmd("sysctl -w net.ipv4.conf.r1-eth0.rp_filter=0 >/dev/null 2>&1")
    r1.cmd("sysctl -w net.ipv4.conf.r1-eth1.rp_filter=0 >/dev/null 2>&1")
    
    info("╔══════════════════════════════════════════════════════════════╗\n")
    info("║              ROUTER r1 CONFIGURAT                           ║\n")
    info("╠══════════════════════════════════════════════════════════════╣\n")
    info(f"║  r1-eth0: {NET_A_GATEWAY}/{NET_A_MASK} (gateway netA)            ║\n")
    info(f"║  r1-eth1: {NET_B_GATEWAY}/{NET_B_MASK} (gateway netB)            ║\n")
    info("║  ip_forward = 1                                             ║\n")
    info("╚══════════════════════════════════════════════════════════════╝\n")


# ═══════════════════════════════════════════════════════════════════════════
# TESTE AUTOMATE
# ═══════════════════════════════════════════════════════════════════════════

def run_tests(net: "Mininet") -> bool:
    """
    Rulează teste automate pentru validarea topologiei.
    
    Returns:
        True dacă toate testele trec, False altfel.
    """
    info("\n" + "═" * 60 + "\n")
    info("                    TESTE AUTOMATE\n")
    info("═" * 60 + "\n\n")
    
    all_passed = True
    
    # Test 1: Ping intra-subnet (netA)
    info("┌─ Test 1: Ping intra-subnet (a1 → a2) ─────────────────────────┐\n")
    a1 = net.get("a1")
    result = a1.cmd(f"ping -c 1 -W 1 {NET_A_PREFIX}.2")
    if "1 received" in result:
        info("│  ✓ PASS: a1 poate comunica cu a2                            │\n")
    else:
        info("│  ✗ FAIL: a1 NU poate comunica cu a2                          │\n")
        all_passed = False
    info("└─────────────────────────────────────────────────────────────────┘\n\n")
    
    # Test 2: Ping intra-subnet (netB)
    info("┌─ Test 2: Ping intra-subnet (b1 → b2) ─────────────────────────┐\n")
    b1 = net.get("b1")
    result = b1.cmd(f"ping -c 1 -W 1 {NET_B_PREFIX}.2")
    if "1 received" in result:
        info("│  ✓ PASS: b1 poate comunica cu b2                            │\n")
    else:
        info("│  ✗ FAIL: b1 NU poate comunica cu b2                          │\n")
        all_passed = False
    info("└─────────────────────────────────────────────────────────────────┘\n\n")
    
    # Test 3: Ping cross-subnet (a1 → b1 via r1)
    info("┌─ Test 3: Ping cross-subnet (a1 → b1 via r1) ──────────────────┐\n")
    result = a1.cmd(f"ping -c 1 -W 1 {NET_B_PREFIX}.1")
    if "1 received" in result:
        info("│  ✓ PASS: a1 poate comunica cu b1 prin router                │\n")
    else:
        info("│  ✗ FAIL: a1 NU poate comunica cu b1 (verificați ip_forward) │\n")
        all_passed = False
    info("└─────────────────────────────────────────────────────────────────┘\n\n")
    
    # Test 4: Verificare IP forwarding pe r1
    info("┌─ Test 4: Verificare IP forwarding pe r1 ──────────────────────┐\n")
    r1 = net.get("r1")
    forward_status = r1.cmd("cat /proc/sys/net/ipv4/ip_forward").strip()
    if forward_status == "1":
        info("│  ✓ PASS: ip_forward = 1 pe r1                               │\n")
    else:
        info(f"│  ✗ FAIL: ip_forward = {forward_status} (ar trebui să fie 1)      │\n")
        all_passed = False
    info("└─────────────────────────────────────────────────────────────────┘\n\n")
    
    # Sumar
    info("═" * 60 + "\n")
    if all_passed:
        info("              ✓ TOATE TESTELE AU TRECUT\n")
    else:
        info("              ✗ UNELE TESTE AU EȘUAT\n")
    info("═" * 60 + "\n")
    
    return all_passed


# ═══════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════

def print_usage_hints() -> None:
    """Afișează sugestii de utilizare."""
    info("\n")
    info("╔══════════════════════════════════════════════════════════════════╗\n")
    info("║                    TOPOLOGIE PREGĂTITĂ                           ║\n")
    info("╠══════════════════════════════════════════════════════════════════╣\n")
    info("║  Hosts disponibile:                                              ║\n")
    info("║    netA: a1 (10.0.1.1), a2 (10.0.1.2)                            ║\n")
    info("║    netB: b1 (10.0.2.1), b2 (10.0.2.2)                            ║\n")
    info("║    router: r1 (10.0.1.254 / 10.0.2.254)                          ║\n")
    info("╠══════════════════════════════════════════════════════════════════╣\n")
    info("║  Comenzi utile:                                                  ║\n")
    info("║    pingall              - verifică conectivitatea                ║\n")
    info("║    a1 ping -c 2 b1      - ping cross-subnet                      ║\n")
    info("║    xterm a1 b1          - terminale separate                     ║\n")
    info("║    a1 ip route          - afișează rutele                        ║\n")
    info("║    r1 ip addr           - verifică IP-urile routerului           ║\n")
    info("╠══════════════════════════════════════════════════════════════════╣\n")
    info("║  Experimente S3:                                                 ║\n")
    info("║    1. Broadcast în netA (verificați că netB NU primește)         ║\n")
    info("║    2. TCP tunnel pe r1 pentru a conecta a1 cu b1                 ║\n")
    info("║    3. Captură trafic: a1 tcpdump -ni a1-eth0                     ║\n")
    info("╚══════════════════════════════════════════════════════════════════╝\n")


def main(argv: list[str]) -> int:
    """Funcția principală."""
    
    if not MININET_AVAILABLE:
        print("EROARE: Mininet nu este instalat sau nu rulați cu sudo.")
        print("Instalare: sudo apt-get install mininet openvswitch-switch")
        print("Rulare: sudo python3 topo_extended.py --cli")
        return 1
    
    # Parser argumente
    parser = argparse.ArgumentParser(
        description="Topologie S3 extinsă: 2 subrețele + router Linux.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemple:
  sudo python3 topo_extended.py --cli           # Mod interactiv
  sudo python3 topo_extended.py --test          # Rulează teste
  sudo python3 topo_extended.py --exec "a1 ping -c 2 b1"  # Execută comandă
        """
    )
    
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "--cli", action="store_true",
        help="Pornește CLI-ul Mininet (mod interactiv)"
    )
    mode_group.add_argument(
        "--test", action="store_true",
        help="Rulează teste automate și afișează rezultatele"
    )
    mode_group.add_argument(
        "--exec", type=str, metavar="CMD",
        help="Execută o comandă și ieși (ex: 'a1 ping -c 2 b1')"
    )
    
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Output detaliat"
    )
    
    args = parser.parse_args(argv)
    
    # Setare nivel log
    setLogLevel("info" if args.verbose else "warning")
    
    # Creează rețeaua
    topo = Week3ExtendedTopo()
    net = Mininet(
        topo=topo,
        switch=OVSSwitch,
        link=TCLink,
        controller=None,
        autoSetMacs=True,
        autoStaticArp=True
    )
    
    try:
        net.start()
        config_router(net)
        
        if args.test:
            # Mod test: rulează testele și ieși
            success = run_tests(net)
            return 0 if success else 1
            
        elif args.exec:
            # Mod exec: rulează comandă specifică
            # Parsează: "host cmd args..."
            parts = args.exec.split(maxsplit=1)
            if len(parts) < 2:
                error(f"Format incorect. Folosiți: --exec 'host comandă'\n")
                return 1
            host_name, cmd = parts
            host = net.get(host_name)
            if host is None:
                error(f"Host necunoscut: {host_name}\n")
                return 1
            output = host.cmd(cmd)
            print(output)
            return 0
            
        else:
            # Mod CLI (default sau explicit cu --cli)
            setLogLevel("info")
            print_usage_hints()
            CLI(net)
            return 0
            
    finally:
        net.stop()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
