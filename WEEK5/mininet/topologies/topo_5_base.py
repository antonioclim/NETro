#!/usr/bin/env python3
"""
Topologie Mininet - Bază: 2 Subrețele + 1 Router
================================================
Demonstrează rutare statică între două subrețele IPv4.

Arhitectura (Week 5 - Adresare IP):
    10.0.5.0/25              10.0.5.128/25
    (126 hosturi)            (126 hosturi)
        |                        |
       h1 -------- r1 -------- h2
    .11    .1          .129    .140

Plan porturi: WEEK_PORT_BASE = 5500

Utilizare:
    sudo python topo_5_base.py --test    # Test automat pingall
    sudo python topo_5_base.py --cli     # CLI interactiv

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
    """
    Nod Linux configurat ca router cu IP forwarding activat.
    """
    
    def config(self, **params):
        super().config(**params)
        # Activăm IP forwarding
        self.cmd('sysctl -w net.ipv4.ip_forward=1')
        self.cmd('sysctl -w net.ipv6.conf.all.forwarding=1')
    
    def terminate(self):
        # Dezactivăm forwarding la oprire (opțional)
        self.cmd('sysctl -w net.ipv4.ip_forward=0')
        super().terminate()


def build_base_topology() -> Mininet:
    """
    Construiește topologia de bază cu 2 subrețele și 1 router.
    
    Returns:
        Mininet: Rețeaua configurată
    """
    info("*** Construire topologie bază ***\n")
    
    net = Mininet(
        switch=OVSSwitch,
        link=TCLink,
        waitConnected=True
    )
    
    # ═══════════════════════════════════════════════════════
    # Configurare adrese (Week 5: 10.0.5.0/24 split în 2)
    # ═══════════════════════════════════════════════════════
    subnet1 = {
        'network': '10.0.5.0/25',
        'router_ip': '10.0.5.1/25',
        'host_ip': '10.0.5.11/25',
        'gateway': '10.0.5.1',
    }
    
    subnet2 = {
        'network': '10.0.5.128/25',
        'router_ip': '10.0.5.129/25',
        'host_ip': '10.0.5.140/25',
        'gateway': '10.0.5.129',
    }
    
    # ═══════════════════════════════════════════════════════
    # Creare noduri
    # ═══════════════════════════════════════════════════════
    info("*** Adăugare router și hosturi ***\n")
    
    # Router (cu IP forwarding)
    r1 = net.addHost('r1', cls=LinuxRouter, ip=None)
    
    # Hosturi
    h1 = net.addHost('h1', ip=subnet1['host_ip'], defaultRoute=f"via {subnet1['gateway']}")
    h2 = net.addHost('h2', ip=subnet2['host_ip'], defaultRoute=f"via {subnet2['gateway']}")
    
    # Switch-uri L2 (unul per subrețea)
    s1 = net.addSwitch('s1')
    s2 = net.addSwitch('s2')
    
    # ═══════════════════════════════════════════════════════
    # Creare linkuri
    # ═══════════════════════════════════════════════════════
    info("*** Creare linkuri ***\n")
    
    # Link-uri subrețea 1
    net.addLink(h1, s1)
    net.addLink(r1, s1,
                intfName1='r1-eth0',
                params1={'ip': subnet1['router_ip']})
    
    # Link-uri subrețea 2
    net.addLink(h2, s2)
    net.addLink(r1, s2,
                intfName1='r1-eth1',
                params1={'ip': subnet2['router_ip']})
    
    return net


def start_network(net: Mininet, run_test: bool = False, start_cli: bool = True):
    """
    Pornește rețeaua și opțional rulează teste sau CLI.
    """
    info("*** Pornire rețea ***\n")
    net.start()
    
    # Informații despre configurare
    info("\n*** Configurare noduri ***\n")
    for host in net.hosts:
        info(f"{host.name}:\n")
        info(f"  IP: {host.cmd('ip -4 addr show dev ' + host.defaultIntf().name + ' | grep inet').strip()}\n")
        if hasattr(host, 'defaultRoute') or host.name == 'r1':
            info(f"  Route: {host.cmd('ip route').strip()}\n")
    
    info("\n*** Topologie ***\n")
    info("  h1 (10.0.5.11/25) --- s1 --- r1 --- s2 --- h2 (10.0.5.140/25)\n")
    info("                    10.0.5.1       10.0.5.129\n\n")
    
    if run_test:
        info("*** Rulare test conectivitate (pingall) ***\n")
        packet_loss = net.pingAll()
        
        if packet_loss == 0:
            info("\n*** TEST REUȘIT: Toate nodurile comunică! ***\n")
        else:
            info(f"\n*** TEST EȘUAT: {packet_loss}% pierdere pachete ***\n")
        
        net.stop()
        return 0 if packet_loss == 0 else 1
    
    if start_cli:
        info("*** Comenzi utile ***\n")
        info("  nodes                     - listează nodurile\n")
        info("  net                       - afișează topologia\n")
        info("  h1 ip addr                - adresele h1\n")
        info("  h1 ip route               - rutele h1\n")
        info("  h1 ping -c 3 10.0.5.140   - ping către h2\n")
        info("  r1 ip route               - rutele router\n")
        info("  r1 tcpdump -ni r1-eth0    - captură pe interfața router\n")
        info("  xterm h1                  - terminal pentru h1\n")
        info("  exit                      - ieșire\n\n")
        
        CLI(net)
    
    info("*** Oprire rețea ***\n")
    net.stop()
    return 0


def main(argv: Optional[list] = None) -> int:
    """Funcția principală."""
    parser = argparse.ArgumentParser(
        description="Topologie Mininet - Bază: 2 Subrețele + 1 Router",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemple:
  sudo python %(prog)s --test    # Test automat
  sudo python %(prog)s --cli     # CLI interactiv
  sudo python %(prog)s           # Doar construiește și oprește
"""
    )
    
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--test", "-t",
        action="store_true",
        help="Rulează test conectivitate (pingall) și ieși"
    )
    group.add_argument(
        "--cli", "-c",
        action="store_true",
        help="Pornește CLI-ul interactiv Mininet"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Output detaliat"
    )
    
    args = parser.parse_args(argv)
    
    # Setăm nivelul de logging
    if args.verbose:
        setLogLevel('debug')
    else:
        setLogLevel('info')
    
    # Construim și rulăm
    net = build_base_topology()
    return start_network(net, run_test=args.test, start_cli=args.cli)


if __name__ == "__main__":
    sys.exit(main())
