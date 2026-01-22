#!/usr/bin/env python3
"""
Seminarul 6 – Topologie Mininet: SDN cu OpenFlow 1.3

Topologie:
    h1 (10.0.6.11) ────┐
                       │
    h2 (10.0.6.12) ────┼──── s1 (OVS) ←───── Controller (OS-Ken)
                       │          ↑
    h3 (10.0.6.13) ────┘      OpenFlow 1.3

Toate hosturile sunt în același subnet (10.0.6.0/24).
Switch-ul s1 este controlat de un controller extern (OS-Ken) via OpenFlow.

Politica așteptată (implementată în controller):
- ✓ h1 ↔ h2: PERMIT (tot traficul)
- ✗ * → h3: DROP (implicit, cu excepții configurabile)
- ? UDP → h3: CONFIGURABIL în controller

Scop didactic:
- Înțelegerea separării control plane / data plane
- Observarea instalării flow-urilor din controller
- Analiza flow table cu ovs-ofctl
- Experimentarea cu politici allow/drop per protocol

Utilizare:
    # Terminal 1 - pornește controller-ul
    osken-manager seminar/python/controllers/sdn_policy_controller.py

    # Terminal 2 - pornește topologia
    sudo python3 topo_sdn.py --cli

Revolvix&Hypotheticalandrei
"""

from __future__ import annotations

import argparse
import sys

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import OVSSwitch, RemoteController
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.log import setLogLevel, info


class SDNTopology(Topo):
    """
    Topologie SDN simplă: 3 hosturi conectate la un switch OVS.
    
    Switch-ul este configurat să folosească OpenFlow 1.3 și să se
    conecteze la un controller extern pe portul 6633.
    """
    
    def build(self):
        # Switch OpenFlow
        s1 = self.addSwitch(
            "s1",
            cls=OVSSwitch,
            protocols="OpenFlow13"  # Explicit OpenFlow 1.3
        )
        
        # Hosturi
        h1 = self.addHost("h1", ip="10.0.6.11/24")
        h2 = self.addHost("h2", ip="10.0.6.12/24")
        h3 = self.addHost("h3", ip="10.0.6.13/24")
        
        # Legături
        # Ordinea de conectare determină porturile:
        #   port 1 → h1, port 2 → h2, port 3 → h3
        self.addLink(h1, s1)
        self.addLink(h2, s1)
        self.addLink(h3, s1)


def run_smoke_test(net: Mininet) -> int:
    """
    Rulează teste pentru verificarea politicilor SDN.
    """
    h1, h2, h3 = net.get("h1", "h2", "h3")
    
    info("\n*** TEST 1: Ping h1 → h2 (PERMIT așteptat)\n")
    out1 = h1.cmd("ping -c 2 -W 3 10.0.6.12")
    ok1 = "0% packet loss" in out1 or " 2 received" in out1
    info(f"    Rezultat: {'OK (PERMIT)' if ok1 else 'FAIL'}\n")
    
    info("*** TEST 2: Ping h1 → h3 (DROP așteptat)\n")
    out2 = h1.cmd("ping -c 2 -W 3 10.0.6.13")
    ok2 = "100% packet loss" in out2 or " 0 received" in out2
    info(f"    Rezultat: {'OK (DROP)' if ok2 else 'FAIL - traficul a trecut!'}\n")
    
    info("\n*** Flow table s1:\n")
    flows = net.get("s1").cmd("ovs-ofctl -O OpenFlow13 dump-flows s1")
    info(flows + "\n")
    
    if ok1 and ok2:
        info("*** TOATE TESTELE AU TRECUT ***\n")
        return 0
    else:
        info("*** UNELE TESTE AU EȘUAT ***\n")
        return 1


def main() -> int:
    """Punct de intrare principal."""
    parser = argparse.ArgumentParser(
        description="Topologie SDN cu OpenFlow 1.3"
    )
    parser.add_argument("--cli", action="store_true", help="Mod interactiv")
    parser.add_argument("--test", action="store_true", help="Smoke test")
    parser.add_argument(
        "--controller-ip", default="127.0.0.1",
        help="IP-ul controller-ului (default: 127.0.0.1)"
    )
    parser.add_argument(
        "--controller-port", type=int, default=6633,
        help="Portul controller-ului (default: 6633)"
    )
    args = parser.parse_args()
    
    topo = SDNTopology()
    
    # Controller extern (OS-Ken)
    # Trebuie pornit separat: osken-manager ...
    controller = RemoteController(
        "c0",
        ip=args.controller_ip,
        port=args.controller_port
    )
    
    net = Mininet(
        topo=topo,
        controller=controller,
        switch=OVSSwitch,
        link=TCLink,
        autoSetMacs=True
    )
    
    net.start()
    
    try:
        info("\n" + "="*60 + "\n")
        info("  TOPOLOGIE SDN PORNITĂ\n")
        info(f"  Controller: {args.controller_ip}:{args.controller_port}\n")
        info("  \n")
        info("  Politici implementate:\n")
        info("    ✓ h1 ↔ h2: PERMIT\n")
        info("    ✗ * → h3: DROP (ICMP, TCP)\n")
        info("    ? UDP → h3: Configurabil (ALLOW_UDP_TO_H3)\n")
        info("  \n")
        info("  Comenzi utile:\n")
        info("    h1 ping 10.0.6.12\n")
        info("    h1 ping 10.0.6.13\n")
        info("    sh ovs-ofctl -O OpenFlow13 dump-flows s1\n")
        info("="*60 + "\n\n")
        
        if args.test:
            import time
            time.sleep(2)  # Așteaptă conectarea controller-ului
            return run_smoke_test(net)
        elif args.cli:
            CLI(net)
        else:
            info("Topologie pornită. Folosește --cli pentru mod interactiv.\n")
        
        return 0
    finally:
        net.stop()


if __name__ == "__main__":
    setLogLevel("info")
    sys.exit(main())
