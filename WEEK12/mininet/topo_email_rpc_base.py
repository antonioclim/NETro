#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Topologie Mininet de Bază – Săptămâna 12
ASE-CSIE, Rețele de Calculatoare

Topologie simplă pentru testarea protocoalelor E-mail și RPC.

Structura:
    client ──── switch ──── server
       │                      │
       └── 10.0.12.11  10.0.12.100 ┘
    
    Plan IP Week 12: 10.0.12.0/24
    Port base: 6200-6299

Rulare:
    sudo python topo_email_rpc_base.py [--bw BANDWIDTH] [--delay DELAY]

Exemple:
    # Topologie implicită
    sudo python topo_email_rpc_base.py
    
    # Cu 100Mbps și 10ms delay
    sudo python topo_email_rpc_base.py --bw 100 --delay 10ms
    
    # Mod debug
    sudo python topo_email_rpc_base.py --debug
"""

from __future__ import annotations

import argparse
import sys

try:
    from mininet.net import Mininet
    from mininet.node import Controller, OVSKernelSwitch
    from mininet.link import TCLink
    from mininet.cli import CLI
    from mininet.log import setLogLevel, info, error
except ImportError:
    print("[EROARE] Mininet nu este instalat.")
    print("  Instalați cu: sudo apt-get install mininet")
    print("  Sau rulați: sudo ./scripts/setup.sh --with-mininet")
    sys.exit(1)


def create_base_topology(bandwidth: int = 1000, delay: str = "1ms",
                         loss: float = 0) -> Mininet:
    """
    Creează o topologie de bază client-server.
    
    Args:
        bandwidth: Lățime de bandă în Mbps
        delay: Întârziere (e.g., "1ms", "10ms")
        loss: Procentaj pierdere pachete (0-100)
    
    Returns:
        Obiect Mininet configurat
    """
    info("*** Creare topologie de bază ***\n")
    
    # Creează rețeaua
    net = Mininet(
        controller=Controller,
        switch=OVSKernelSwitch,
        link=TCLink,
        waitConnected=True
    )
    
    # Adaugă controller
    info("  Adăugare controller\n")
    net.addController('c0')
    
    # Adaugă switch
    info("  Adăugare switch\n")
    s1 = net.addSwitch('s1')
    
    # Adaugă hosturi
    info("  Adăugare hosturi\n")
    
    # Client - conform plan IP Week 12: 10.0.12.0/24
    client = net.addHost(
        'client',
        ip='10.0.12.11/24',
        defaultRoute='via 10.0.12.1'
    )
    
    # Server (va rula serviciile) - conform plan IP Week 12
    server = net.addHost(
        'server',
        ip='10.0.12.100/24',
        defaultRoute='via 10.0.12.1'
    )
    
    # Adaugă legături cu parametri de performanță
    info(f"  Adăugare legături (bw={bandwidth}Mbps, delay={delay}, loss={loss}%)\n")
    
    link_opts = {
        'bw': bandwidth,
        'delay': delay,
        'loss': loss,
        'use_htb': True
    }
    
    net.addLink(client, s1, **link_opts)
    net.addLink(server, s1, **link_opts)
    
    return net


def run_demo(net: Mininet) -> None:
    """
    Rulează demonstrații automate în topologie.
    
    Args:
        net: Rețeaua Mininet
    """
    client = net.get('client')
    server = net.get('server')
    
    info("\n*** Demo: Teste de bază ***\n")
    
    # Test conectivitate
    info("\n[1] Test ping:\n")
    result = client.cmd('ping -c 3 10.0.12.100')
    print(result)
    
    # Afișează interfețe
    info("\n[2] Interfețe server:\n")
    result = server.cmd('ip addr')
    print(result)
    
    # Instrucțiuni pentru utilizator
    info("""
*** Instrucțiuni pentru testare manuală ***

Pe server (într-un terminal xterm):
  # Pornire server JSON-RPC
  cd /path/to/src/rpc/jsonrpc
  python jsonrpc_server.py --listen 0.0.0.0 --port 6200
  
  # Sau server SMTP
  cd /path/to/src/email
  python smtp_server.py --listen 0.0.0.0 --port 1025

Pe client (într-un alt terminal xterm):
  # Testare JSON-RPC
  python jsonrpc_client.py --server 10.0.12.100 --port 6200
  
  # Sau trimitere email
  python smtp_client.py --server 10.0.12.100 --port 1025

Pentru a deschide terminale:
  mininet> xterm client server

Pentru capturare trafic:
  mininet> server tcpdump -i server-eth0 -w /tmp/capture.pcap &
""")


def run_benchmark(net: Mininet) -> None:
    """
    Rulează benchmark de rețea.
    
    Args:
        net: Rețeaua Mininet
    """
    client = net.get('client')
    server = net.get('server')
    
    info("\n*** Benchmark de rețea ***\n")
    
    # iperf pentru throughput
    info("\n[1] Test iperf (10 secunde):\n")
    server.cmd('iperf -s &')
    import time
    time.sleep(1)
    result = client.cmd('iperf -c 10.0.12.100 -t 10')
    print(result)
    server.cmd('pkill iperf')
    
    # Latență
    info("\n[2] Test latență (100 pachete):\n")
    result = client.cmd('ping -c 100 -i 0.01 10.0.12.100 | tail -3')
    print(result)


def main():
    """Punct de intrare principal."""
    parser = argparse.ArgumentParser(
        description="Topologie Mininet pentru E-mail & RPC",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemple:
  # Topologie implicită
  sudo python topo_email_rpc_base.py
  
  # Cu parametri de rețea
  sudo python topo_email_rpc_base.py --bw 100 --delay 10ms --loss 1
  
  # Rulare demo automat
  sudo python topo_email_rpc_base.py --demo
  
  # Benchmark rețea
  sudo python topo_email_rpc_base.py --benchmark
"""
    )
    
    parser.add_argument(
        "--bw",
        type=int,
        default=1000,
        help="Lățime de bandă în Mbps (default: 1000)"
    )
    parser.add_argument(
        "--delay",
        default="1ms",
        help="Întârziere per link (default: 1ms)"
    )
    parser.add_argument(
        "--loss",
        type=float,
        default=0,
        help="Procentaj pierdere pachete (default: 0)"
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Rulează demonstrații automate"
    )
    parser.add_argument(
        "--benchmark",
        action="store_true",
        help="Rulează benchmark de rețea"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Activează logging detaliat"
    )
    
    args = parser.parse_args()
    
    # Setează nivelul de logging
    if args.debug:
        setLogLevel('debug')
    else:
        setLogLevel('info')
    
    # Creează și pornește rețeaua
    net = create_base_topology(
        bandwidth=args.bw,
        delay=args.delay,
        loss=args.loss
    )
    
    try:
        info("*** Pornire rețea ***\n")
        net.start()
        
        # Test ping rapid
        info("*** Test conectivitate ***\n")
        if net.pingAll() != 0:
            error("Eroare de conectivitate!\n")
        
        if args.demo:
            run_demo(net)
        elif args.benchmark:
            run_benchmark(net)
        else:
            # Mod interactiv
            info("\n*** Mod CLI interactiv ***\n")
            info("Comenzi utile:\n")
            info("  nodes          - Afișează nodurile\n")
            info("  net            - Afișează topologia\n")
            info("  dump           - Informații detaliate\n")
            info("  xterm h1 h2    - Deschide terminale\n")
            info("  pingall        - Test conectivitate\n")
            info("  iperf h1 h2    - Test throughput\n")
            info("  h1 command     - Execută comandă pe h1\n")
            info("  exit           - Ieșire\n")
            CLI(net)
    
    finally:
        info("\n*** Oprire rețea ***\n")
        net.stop()


if __name__ == "__main__":
    main()
