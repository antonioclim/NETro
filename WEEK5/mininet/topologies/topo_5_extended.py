#!/usr/bin/env python3
"""
Topologie Mininet - Extinsă: VLSM + IPv6 Opțional
=================================================
Demonstrează subnetting cu prefixe diferite și suport dual-stack.

Arhitectura VLSM (Week 5 - Adresare IP):
    10.0.5.0/26           10.0.5.64/27          10.0.5.96/30
    (62 hosturi)          (30 hosturi)          (2 hosturi)
        |                      |                      |
       h1 -------- r1 -------- h2 -------- r1 -------- h3
    .11    .1              .65    .70              .97    .98

IPv6 (dacă este activat):
    2001:db8:5:10::/64    2001:db8:5:20::/64    2001:db8:5:30::/64

Plan porturi: WEEK_PORT_BASE = 5500

Utilizare:
    sudo python topo_5_extended.py --cli
    sudo python topo_5_extended.py --cli --ipv6
    sudo python topo_5_extended.py --test --ipv6

© 2025 ASE-CSIE | Rezolvix&Hypotheticalandrei | Licență MIT
"""

from __future__ import annotations

import argparse
import sys
from typing import Optional

try:
    from mininet.net import Mininet
    from mininet.node import Node, OVSSwitch
    from mininet.cli import CLI
    from mininet.log import setLogLevel, info
    from mininet.link import TCLink
except ImportError:
    print("Eroare: Mininet nu este instalat.")
    print("Instalare: sudo apt-get install mininet openvswitch-switch")
    sys.exit(1)


class LinuxRouter(Node):
    """Nod Linux configurat ca router cu IP forwarding."""
    
    def config(self, **params):
        super().config(**params)
        self.cmd('sysctl -w net.ipv4.ip_forward=1')
        self.cmd('sysctl -w net.ipv6.conf.all.forwarding=1')
    
    def terminate(self):
        self.cmd('sysctl -w net.ipv4.ip_forward=0')
        super().terminate()


def build_extended_topology(enable_ipv6: bool = False) -> Mininet:
    """
    Construiește topologia extinsă cu VLSM și opțional IPv6.
    
    Args:
        enable_ipv6: Activează configurarea dual-stack
    
    Returns:
        Mininet: Rețeaua configurată
    """
    info("*** Construire topologie extinsă (VLSM) ***\n")
    
    net = Mininet(
        switch=OVSSwitch,
        link=TCLink,
        waitConnected=True
    )
    
    # ═══════════════════════════════════════════════════════
    # Configurare subrețele VLSM (Week 5: 10.0.5.0/24)
    # ═══════════════════════════════════════════════════════
    
    # Subnet 1: /26 = 62 hosturi utilizabile
    subnet1 = {
        'name': 'LAN1',
        'ipv4_network': '10.0.5.0/26',
        'ipv4_router': '10.0.5.1/26',
        'ipv4_host': '10.0.5.11/26',
        'ipv4_gateway': '10.0.5.1',
        'ipv6_network': '2001:db8:5:10::/64',
        'ipv6_router': '2001:db8:5:10::1/64',
        'ipv6_host': '2001:db8:5:10::11/64',
        'ipv6_gateway': '2001:db8:5:10::1',
        'max_hosts': 62,
    }
    
    # Subnet 2: /27 = 30 hosturi utilizabile
    subnet2 = {
        'name': 'LAN2',
        'ipv4_network': '10.0.5.64/27',
        'ipv4_router': '10.0.5.65/27',
        'ipv4_host': '10.0.5.70/27',
        'ipv4_gateway': '10.0.5.65',
        'ipv6_network': '2001:db8:5:20::/64',
        'ipv6_router': '2001:db8:5:20::1/64',
        'ipv6_host': '2001:db8:5:20::10/64',
        'ipv6_gateway': '2001:db8:5:20::1',
        'max_hosts': 30,
    }
    
    # Subnet 3: /30 = 2 hosturi utilizabile (point-to-point)
    subnet3 = {
        'name': 'P2P',
        'ipv4_network': '10.0.5.96/30',
        'ipv4_router': '10.0.5.97/30',
        'ipv4_host': '10.0.5.98/30',
        'ipv4_gateway': '10.0.5.97',
        'ipv6_network': '2001:db8:5:30::/64',
        'ipv6_router': '2001:db8:5:30::1/64',
        'ipv6_host': '2001:db8:5:30::2/64',
        'ipv6_gateway': '2001:db8:5:30::1',
        'max_hosts': 2,
    }
    
    subnets = [subnet1, subnet2, subnet3]
    
    # ═══════════════════════════════════════════════════════
    # Creare noduri
    # ═══════════════════════════════════════════════════════
    info("*** Adăugare router și hosturi ***\n")
    
    # Router central
    r1 = net.addHost('r1', cls=LinuxRouter, ip=None)
    
    # Hosturi pentru fiecare subrețea
    h1 = net.addHost('h1',
                     ip=subnet1['ipv4_host'],
                     defaultRoute=f"via {subnet1['ipv4_gateway']}")
    
    h2 = net.addHost('h2',
                     ip=subnet2['ipv4_host'],
                     defaultRoute=f"via {subnet2['ipv4_gateway']}")
    
    h3 = net.addHost('h3',
                     ip=subnet3['ipv4_host'],
                     defaultRoute=f"via {subnet3['ipv4_gateway']}")
    
    # Switch-uri L2 (unul per subrețea)
    s1 = net.addSwitch('s1')
    s2 = net.addSwitch('s2')
    s3 = net.addSwitch('s3')
    
    # ═══════════════════════════════════════════════════════
    # Creare linkuri
    # ═══════════════════════════════════════════════════════
    info("*** Creare linkuri ***\n")
    
    # Subrețea 1 (LAN mare)
    net.addLink(h1, s1)
    net.addLink(r1, s1,
                intfName1='r1-eth0',
                params1={'ip': subnet1['ipv4_router']})
    
    # Subrețea 2 (LAN mediu)
    net.addLink(h2, s2)
    net.addLink(r1, s2,
                intfName1='r1-eth1',
                params1={'ip': subnet2['ipv4_router']})
    
    # Subrețea 3 (P2P)
    net.addLink(h3, s3)
    net.addLink(r1, s3,
                intfName1='r1-eth2',
                params1={'ip': subnet3['ipv4_router']})
    
    # Salvăm metadata pentru configurare ulterioară
    net.subnets = subnets
    net.enable_ipv6 = enable_ipv6
    
    return net


def configure_ipv6(net: Mininet):
    """Configurează adresele IPv6 pe toate nodurile."""
    info("*** Configurare IPv6 ***\n")
    
    subnets = net.subnets
    hosts = ['h1', 'h2', 'h3']
    router_intfs = ['r1-eth0', 'r1-eth1', 'r1-eth2']
    
    r1 = net.get('r1')
    
    for i, (host_name, intf, subnet) in enumerate(zip(hosts, router_intfs, subnets)):
        host = net.get(host_name)
        
        # Configurare router
        r1.cmd(f"ip -6 addr add {subnet['ipv6_router']} dev {intf}")
        
        # Configurare host
        host_intf = host.defaultIntf().name
        host.cmd(f"ip -6 addr add {subnet['ipv6_host']} dev {host_intf}")
        host.cmd(f"ip -6 route add default via {subnet['ipv6_gateway']}")
        
        info(f"  {host_name}: {subnet['ipv6_host']} -> {subnet['ipv6_gateway']}\n")


def display_info(net: Mininet):
    """Afișează informații despre topologie."""
    info("\n*** Configurare Topologie VLSM ***\n\n")
    
    subnets = net.subnets
    
    info("  ┌─────────────────────────────────────────────────────────────────┐\n")
    info("  │  Subrețea      │  Prefix  │  Hosturi  │  Router         │  Host         │\n")
    info("  ├─────────────────────────────────────────────────────────────────┤\n")
    
    for subnet in subnets:
        info(f"  │  {subnet['name']:<12}  │  {subnet['ipv4_network'].split('/')[1]:>6}  │  "
             f"{subnet['max_hosts']:>7}   │  {subnet['ipv4_router'].split('/')[0]:<13}  │  "
             f"{subnet['ipv4_host'].split('/')[0]:<11}  │\n")
    
    info("  └─────────────────────────────────────────────────────────────────┘\n\n")
    
    if net.enable_ipv6:
        info("  IPv6 Activat:\n")
        for subnet in subnets:
            info(f"    {subnet['name']}: {subnet['ipv6_network']}\n")
        info("\n")
    
    info("  Topologie vizuală:\n")
    info("    h1 (10.0.5.11/26)  ─┬─ s1 ─── r1-eth0 (10.0.5.1)\n")
    info("                        │\n")
    info("    h2 (10.0.5.70/27)  ─┼─ s2 ─── r1-eth1 (10.0.5.65)  ─── r1\n")
    info("                        │\n")
    info("    h3 (10.0.5.98/30)  ─┴─ s3 ─── r1-eth2 (10.0.5.97)\n\n")


def start_network(net: Mininet, run_test: bool = False, start_cli: bool = True) -> int:
    """Pornește rețeaua și opțional rulează teste sau CLI."""
    info("*** Pornire rețea ***\n")
    net.start()
    
    # Configurare IPv6 dacă este activat
    if net.enable_ipv6:
        configure_ipv6(net)
    
    # Afișare informații
    display_info(net)
    
    if run_test:
        info("*** Rulare test conectivitate ***\n\n")
        
        # Test IPv4
        info("  Test IPv4 (pingall):\n")
        packet_loss = net.pingAll()
        ipv4_ok = packet_loss == 0
        
        ipv6_ok = True
        if net.enable_ipv6:
            info("\n  Test IPv6:\n")
            h1 = net.get('h1')
            h2 = net.get('h2')
            h3 = net.get('h3')
            
            # Test ping IPv6
            tests = [
                (h1, '2001:db8:5:20::10', 'h1 -> h2'),
                (h2, '2001:db8:5:30::2', 'h2 -> h3'),
                (h1, '2001:db8:5:30::2', 'h1 -> h3'),
            ]
            
            for src, dst, desc in tests:
                result = src.cmd(f'ping6 -c 2 -W 2 {dst}')
                success = '0% packet loss' in result or '0 packets lost' in result.lower()
                status = "✓" if success else "✗"
                info(f"    {desc}: {status}\n")
                if not success:
                    ipv6_ok = False
        
        info(f"\n*** Rezultat: IPv4 {'OK' if ipv4_ok else 'EȘUAT'}")
        if net.enable_ipv6:
            info(f", IPv6 {'OK' if ipv6_ok else 'EȘUAT'}")
        info(" ***\n")
        
        net.stop()
        return 0 if (ipv4_ok and ipv6_ok) else 1
    
    if start_cli:
        info("*** Comenzi utile ***\n")
        info("  nodes                         - listează nodurile\n")
        info("  net                           - afișează topologia\n")
        info("  h1 ping -c 3 10.0.5.70        - ping h1 -> h2 (IPv4)\n")
        info("  h1 ping -c 3 10.0.5.98        - ping h1 -> h3 (IPv4)\n")
        if net.enable_ipv6:
            info("  h1 ping6 -c 3 2001:db8:5:20::10  - ping IPv6\n")
        info("  r1 ip route                   - tabelul de rutare IPv4\n")
        info("  r1 ip -6 route                - tabelul de rutare IPv6\n")
        info("  r1 tcpdump -ni r1-eth0 icmp   - captură ICMP pe eth0\n")
        info("  h1 traceroute 10.0.5.98       - traseu către h3\n")
        info("  exit                          - ieșire\n\n")
        
        CLI(net)
    
    info("*** Oprire rețea ***\n")
    net.stop()
    return 0


def main(argv: Optional[list] = None) -> int:
    """Funcția principală."""
    parser = argparse.ArgumentParser(
        description="Topologie Mininet - Extinsă: VLSM + IPv6",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemple:
  sudo python %(prog)s --cli              # CLI interactiv (doar IPv4)
  sudo python %(prog)s --cli --ipv6       # CLI cu dual-stack
  sudo python %(prog)s --test             # Test IPv4
  sudo python %(prog)s --test --ipv6      # Test dual-stack
"""
    )
    
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--test", "-t",
        action="store_true",
        help="Rulează test conectivitate și ieși"
    )
    group.add_argument(
        "--cli", "-c",
        action="store_true",
        help="Pornește CLI-ul interactiv"
    )
    
    parser.add_argument(
        "--ipv6", "-6",
        action="store_true",
        help="Activează configurarea IPv6 (dual-stack)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Output detaliat"
    )
    
    args = parser.parse_args(argv)
    
    if args.verbose:
        setLogLevel('debug')
    else:
        setLogLevel('info')
    
    net = build_extended_topology(enable_ipv6=args.ipv6)
    return start_network(net, run_test=args.test, start_cli=args.cli)


if __name__ == "__main__":
    sys.exit(main())
