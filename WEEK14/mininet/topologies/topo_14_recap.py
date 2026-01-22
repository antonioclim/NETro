#!/usr/bin/env python3
"""topo_14_recap.py — Topologie Mininet pentru Săptămâna 14 (Recapitulare).

Topologie compactă pentru demonstrații load balancing și diagnosticare:

    cli ─── s1 ─── s2 ─── app1
             │       └─── app2
             └─── lb

IP-uri fixe (clasă /24) — conform planului S14:
  cli  : 10.0.14.11  (client)
  app1 : 10.0.14.100 (backend 1)
  app2 : 10.0.14.101 (backend 2)
  lb   : 10.0.14.1   (load balancer / gateway)

Utilizare:
  # CLI interactiv
  sudo python3 topo_14_recap.py --cli
  
  # Test automat
  sudo python3 topo_14_recap.py --test
  
  # Din mn direct
  sudo mn --custom topo_14_recap.py --topo recap14
"""

from __future__ import annotations

import argparse
import os
import sys

# Evită conflictul cu directorul local 'mininet/'
for p in ["", os.getcwd()]:
    if p in sys.path:
        sys.path.remove(p)

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Controller
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.log import setLogLevel


class Recap14Topo(Topo):
    """Topologie pentru recapitulare S14: client, load balancer, 2 backends."""

    def build(self, delay: str = "1ms", bw: int = 100):
        """
        Construiește topologia.
        
        Args:
            delay: Întârziere pe link-uri (default: 1ms)
            bw: Bandwidth pe link-uri în Mbps (default: 100)
        """
        # Switch-uri
        s1 = self.addSwitch("s1")
        s2 = self.addSwitch("s2")

        # Host-uri cu IP-uri fixe (conform planului S14)
        cli = self.addHost("cli", ip="10.0.14.11/24")
        lb = self.addHost("lb", ip="10.0.14.1/24")
        app1 = self.addHost("app1", ip="10.0.14.100/24")
        app2 = self.addHost("app2", ip="10.0.14.101/24")

        # Link-uri
        # cli și lb conectate la s1
        self.addLink(cli, s1, delay=delay, bw=bw)
        self.addLink(lb, s1, delay=delay, bw=bw)

        # s1 conectat la s2
        self.addLink(s1, s2, delay=delay, bw=bw)

        # app1 și app2 conectate la s2
        self.addLink(app1, s2, delay=delay, bw=bw)
        self.addLink(app2, s2, delay=delay, bw=bw)


# Dicționar pentru mn --custom --topo
topos = {"recap14": Recap14Topo}


def run_cli():
    """Pornește topologia cu CLI interactiv."""
    setLogLevel("info")
    
    topo = Recap14Topo()
    net = Mininet(
        topo=topo,
        link=TCLink,
        controller=Controller,
        autoSetMacs=True,
        autoStaticArp=True
    )
    net.addController("c0")
    
    print("\n" + "=" * 60)
    print("Topologie S14 - Recapitulare")
    print("=" * 60)
    print("""
Hosturi (plan IP S14):
  cli  : 10.0.14.11  (client)
  lb   : 10.0.14.1   (load balancer)
  app1 : 10.0.14.100 (backend 1)
  app2 : 10.0.14.101 (backend 2)

Comenzi utile în CLI:
  cli ping lb
  cli ping app1
  app1 python3 -m http.server 8080 &
  cli curl http://10.0.14.100:8080/
  net
  dump
  exit
""")
    print("=" * 60 + "\n")
    
    net.start()
    CLI(net)
    net.stop()


def run_test():
    """Rulează un test automat de conectivitate."""
    setLogLevel("info")
    
    topo = Recap14Topo()
    net = Mininet(
        topo=topo,
        link=TCLink,
        controller=Controller,
        autoSetMacs=True,
        autoStaticArp=True
    )
    net.addController("c0")
    
    net.start()
    
    print("\n" + "=" * 60)
    print("Test automat S14")
    print("=" * 60 + "\n")
    
    # Test ping all
    print("[test] Ping toate perechile...")
    net.pingAll()
    
    # Test specific
    cli = net.get("cli")
    lb = net.get("lb")
    app1 = net.get("app1")
    
    print("\n[test] Testare conexiuni specifice...")
    
    # cli -> lb
    result = cli.cmd("ping -c 2 -W 1 10.0.14.1")
    print(f"cli -> lb:\n{result}")
    
    # cli -> app1
    result = cli.cmd("ping -c 2 -W 1 10.0.14.100")
    print(f"cli -> app1:\n{result}")
    
    # Test HTTP (pornește server pe app1)
    print("[test] Pornire server HTTP pe app1:8080...")
    app1.cmd("python3 -m http.server 8080 &")
    
    import time
    time.sleep(0.5)
    
    print("[test] Testare HTTP din cli...")
    result = cli.cmd("curl -s -o /dev/null -w '%{http_code}' http://10.0.14.100:8080/ 2>/dev/null || echo 'EȘUAT'")
    print(f"HTTP status: {result}")
    
    # Cleanup
    app1.cmd("pkill -f 'python3 -m http.server' || true")
    
    print("\n" + "=" * 60)
    print("Test completat")
    print("=" * 60 + "\n")
    
    net.stop()


def main():
    parser = argparse.ArgumentParser(description="Topologie Mininet S14")
    parser.add_argument("--cli", action="store_true", help="Pornește CLI interactiv")
    parser.add_argument("--test", action="store_true", help="Rulează test automat")
    args = parser.parse_args()
    
    if args.cli:
        run_cli()
    elif args.test:
        run_test()
    else:
        print("Utilizare: python3 topo_14_recap.py [--cli | --test]")
        print("  --cli   Pornește CLI Mininet interactiv")
        print("  --test  Rulează test automat de conectivitate")


if __name__ == "__main__":
    main()
