#!/usr/bin/env python3
"""
Seminarul 6 – Topologie Mininet: NAT/PAT

Topologie:
    (private)                      (public)
   h1 ───┐                        ┌─── h3
        s1 ─── rnat ─── s2 ───────┘
   h2 ───┘

Adresare:
- h1: 192.168.1.10/24   gw 192.168.1.1
- h2: 192.168.1.20/24   gw 192.168.1.1
- rnat(private): 192.168.1.1/24
- rnat(public): 203.0.113.1/24  (TEST-NET-3, RFC 5737)
- h3: 203.0.113.2/24    gw 203.0.113.1

Scop didactic:
- Demonstrarea translatării PAT (MASQUERADE)
- Observarea diferenței între adrese private și publice
- Înțelegerea tabelei NAT și a mapării bidirecționale

Utilizare:
    sudo python3 topo_nat.py --cli     # Mod interactiv
    sudo python3 topo_nat.py --test    # Smoke test automat

Revolvix&Hypotheticalandrei
"""

from __future__ import annotations

import argparse
import sys

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node, OVSSwitch
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.log import setLogLevel, info


class LinuxRouter(Node):
    """
    Nod Mininet configurat ca router Linux.
    
    Activează IP forwarding și oferă cleanup pentru regulile NAT.
    """
    
    def config(self, **params):
        super().config(**params)
        # Activează forwarding IPv4
        self.cmd("sysctl -w net.ipv4.ip_forward=1")

    def terminate(self):
        # Curățare reguli iptables la oprire
        self.cmd("iptables -t nat -F 2>/dev/null || true")
        self.cmd("iptables -F 2>/dev/null || true")
        super().terminate()


class NatTopology(Topo):
    """
    Topologie NAT cu:
    - 2 hosturi private (h1, h2)
    - 1 router Linux cu NAT (rnat)
    - 1 host "public" (h3)
    - 2 switch-uri OVS (s1 privat, s2 public)
    """
    
    def build(self):
        # Switch-uri
        s1 = self.addSwitch("s1")  # Rețea privată
        s2 = self.addSwitch("s2")  # Rețea publică
        
        # Router Linux cu NAT
        rnat = self.addNode("rnat", cls=LinuxRouter)
        
        # Hosturi
        h1 = self.addHost("h1")
        h2 = self.addHost("h2")
        h3 = self.addHost("h3")
        
        # Legături
        self.addLink(h1, s1)       # h1-eth0 ↔ s1
        self.addLink(h2, s1)       # h2-eth0 ↔ s1
        self.addLink(s1, rnat)     # rnat-eth0 (privat)
        self.addLink(rnat, s2)     # rnat-eth1 (public)
        self.addLink(s2, h3)       # h3-eth0 ↔ s2


def configure_network(net: Mininet) -> None:
    """
    Configurează adresele IP, rutele și regulile NAT.
    
    Această funcție demonstrează:
    1. Configurarea adreselor pe interfețe specifice
    2. Adăugarea rutelor implicite (default gateway)
    3. Configurarea NAT cu iptables (MASQUERADE)
    """
    h1, h2, h3 = net.get("h1", "h2", "h3")
    rnat = net.get("rnat")
    
    # === Configurare adrese IP ===
    # Rețea privată (192.168.1.0/24)
    h1.setIP("192.168.1.10/24", intf="h1-eth0")
    h2.setIP("192.168.1.20/24", intf="h2-eth0")
    rnat.setIP("192.168.1.1/24", intf="rnat-eth0")
    
    # Rețea publică (203.0.113.0/24 - TEST-NET-3)
    rnat.setIP("203.0.113.1/24", intf="rnat-eth1")
    h3.setIP("203.0.113.2/24", intf="h3-eth0")
    
    # === Configurare rute ===
    # Hosturile private folosesc rnat ca default gateway
    h1.cmd("ip route add default via 192.168.1.1")
    h2.cmd("ip route add default via 192.168.1.1")
    # Hostul public folosește tot rnat (pentru simplicitate)
    h3.cmd("ip route add default via 203.0.113.1")
    
    # === Configurare NAT (iptables) ===
    # Curățăm regulile existente pentru a evita duplicarea
    rnat.cmd("iptables -t nat -F")
    rnat.cmd("iptables -F")
    
    # Permit forwarding între interfețe
    rnat.cmd("iptables -A FORWARD -i rnat-eth0 -o rnat-eth1 -j ACCEPT")
    rnat.cmd("iptables -A FORWARD -i rnat-eth1 -o rnat-eth0 "
             "-m state --state ESTABLISHED,RELATED -j ACCEPT")
    
    # NAT MASQUERADE pentru traficul din rețeaua privată
    # MASQUERADE: folosește automat IP-ul interfeței de ieșire
    rnat.cmd("iptables -t nat -A POSTROUTING -o rnat-eth1 "
             "-s 192.168.1.0/24 -j MASQUERADE")
    
    info("*** Configurare NAT completă\n")
    info("*** h1/h2 (192.168.1.x) → NAT → 203.0.113.1 → h3\n")


def run_smoke_test(net: Mininet) -> int:
    """
    Rulează teste de bază pentru verificarea funcționalității.
    
    Returns:
        0 dacă toate testele trec, 1 altfel
    """
    h1, h2, h3 = net.get("h1", "h2", "h3")
    rnat = net.get("rnat")
    
    info("\n*** TEST 1: Ping h1 → h3 (prin NAT)\n")
    out1 = h1.cmd("ping -c 2 -W 2 203.0.113.2")
    ok1 = "0% packet loss" in out1 or "2 received" in out1
    info(f"    Rezultat: {'OK' if ok1 else 'FAIL'}\n")
    
    info("*** TEST 2: Ping h2 → h3 (prin NAT)\n")
    out2 = h2.cmd("ping -c 2 -W 2 203.0.113.2")
    ok2 = "0% packet loss" in out2 or "2 received" in out2
    info(f"    Rezultat: {'OK' if ok2 else 'FAIL'}\n")
    
    info("*** TEST 3: Verificare tabel NAT\n")
    nat_table = rnat.cmd("iptables -t nat -L -n -v")
    ok3 = "MASQUERADE" in nat_table
    info(f"    MASQUERADE prezent: {'OK' if ok3 else 'FAIL'}\n")
    
    info("\n*** Tabel NAT (rnat):\n")
    info(nat_table + "\n")
    
    if ok1 and ok2 and ok3:
        info("*** TOATE TESTELE AU TRECUT ***\n")
        return 0
    else:
        info("*** UNELE TESTE AU EȘUAT ***\n")
        if not ok1:
            info(f"    h1 ping output: {out1}\n")
        if not ok2:
            info(f"    h2 ping output: {out2}\n")
        return 1


def main() -> int:
    """Punct de intrare principal."""
    parser = argparse.ArgumentParser(
        description="Topologie Mininet pentru demonstrația NAT/PAT"
    )
    parser.add_argument(
        "--cli", action="store_true",
        help="Lansează CLI Mininet interactiv"
    )
    parser.add_argument(
        "--test", action="store_true",
        help="Rulează smoke test automat"
    )
    args = parser.parse_args()
    
    # Construire topologie
    topo = NatTopology()
    net = Mininet(
        topo=topo,
        controller=None,      # Nu avem nevoie de controller SDN
        switch=OVSSwitch,
        link=TCLink,
        autoSetMacs=True      # MAC-uri predictibile
    )
    
    net.start()
    
    try:
        configure_network(net)
        
        if args.test:
            return run_smoke_test(net)
        elif args.cli:
            info("\n" + "="*60 + "\n")
            info("  TOPOLOGIE NAT/PAT PORNITĂ\n")
            info("  Comenzi utile:\n")
            info("    h1 ping 203.0.113.2\n")
            info("    rnat iptables -t nat -L -n -v\n")
            info("    h3 tcpdump -ni h3-eth0 icmp\n")
            info("="*60 + "\n\n")
            CLI(net)
        else:
            info("Topologie pornită. Folosește --cli pentru mod interactiv.\n")
        
        return 0
    finally:
        net.stop()


if __name__ == "__main__":
    setLogLevel("info")
    sys.exit(main())
