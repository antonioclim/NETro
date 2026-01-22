#!/usr/bin/env python3
"""
Topologie Mininet pentru Seminar 8: HTTP Server & Reverse Proxy
================================================================
Disciplina: Rețele de Calculatoare, Săptămâna 8

TOPOLOGIE:
                      +----------+
                      |   sw1    |
                      +----+-----+
                           |
         +-----------------+------------------+
         |                 |                  |
    +----+----+       +----+----+        +----+----+
    |   h1    |       |   h2    |        |   h3    |
    | (client)|       | (proxy) |        |(backend)|
    | 10.0.0.1|       | 10.0.0.2|        | 10.0.0.3|
    +---------+       +---------+        +---------+

UTILIZARE:
    sudo python3 topo_http_proxy.py [--delay N] [--loss N]

SCENARII:
    1. Client (h1) face cereri HTTP către Proxy (h2)
    2. Proxy (h2) forward-ează către Backend (h3)
    3. Observăm traficul cu tcpdump pe fiecare host

© Revolvix&Hypotheticalandrei
"""

from mininet.net import Mininet
from mininet.node import Controller, OVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink
import argparse
import os
import sys
import time


def create_topology(delay_ms=0, loss_pct=0):
    """
    Creează topologia pentru demo HTTP/Proxy.
    
    Args:
        delay_ms: Delay artificat per link (milisecunde)
        loss_pct: Procent pierdere pachete
    
    Returns:
        Obiectul Mininet
    """
    info("*** Creăm topologia HTTP/Proxy ***\n")
    
    # Creăm rețeaua cu link-uri TC pentru QoS
    net = Mininet(controller=Controller, switch=OVSSwitch, link=TCLink)
    
    info("*** Adăugăm controller ***\n")
    net.addController('c0')
    
    info("*** Adăugăm switch ***\n")
    sw1 = net.addSwitch('sw1')
    
    info("*** Adăugăm host-uri ***\n")
    # h1: Client
    h1 = net.addHost('h1', ip='10.0.0.1/24')
    # h2: Reverse Proxy
    h2 = net.addHost('h2', ip='10.0.0.2/24')
    # h3: Backend Server
    h3 = net.addHost('h3', ip='10.0.0.3/24')
    
    info("*** Configurăm link-uri ***\n")
    link_opts = {}
    if delay_ms > 0:
        link_opts['delay'] = f'{delay_ms}ms'
    if loss_pct > 0:
        link_opts['loss'] = loss_pct
    
    # Conectăm toate host-urile la switch
    net.addLink(h1, sw1, **link_opts)
    net.addLink(h2, sw1, **link_opts)
    net.addLink(h3, sw1, **link_opts)
    
    return net


def setup_servers(net):
    """
    Configurează serverele pe host-uri.
    """
    h2 = net.get('h2')  # Proxy
    h3 = net.get('h3')  # Backend
    
    info("*** Pornim Backend Server pe h3 (port 8081) ***\n")
    # Presupunem că fișierele sunt în directorul curent
    # În practică, ar trebui să specificăm calea completă
    h3.cmd('cd /home/claude/starterkit_s8 && python3 python/demos/demo_http_server.py --port 8081 --docroot www/ &')
    time.sleep(1)
    
    info("*** Pornim Reverse Proxy pe h2 (port 8080) ***\n")
    h2.cmd('cd /home/claude/starterkit_s8 && python3 python/demos/demo_reverse_proxy.py --port 8080 --backends 10.0.0.3:8081 &')
    time.sleep(1)
    
    info("*** Servere pornite! ***\n")


def run_demo(net):
    """
    Rulează demonstrația interactivă.
    """
    h1 = net.get('h1')  # Client
    h2 = net.get('h2')  # Proxy
    h3 = net.get('h3')  # Backend
    
    print("\n" + "="*60)
    print("DEMO: HTTP Request prin Reverse Proxy")
    print("="*60)
    
    print("\n[1] Verificăm conectivitatea...")
    print(h1.cmd('ping -c 1 10.0.0.2'))
    print(h1.cmd('ping -c 1 10.0.0.3'))
    
    print("\n[2] Request direct la Backend (h1 -> h3)...")
    print(h1.cmd('curl -s http://10.0.0.3:8081/'))
    
    print("\n[3] Request prin Proxy (h1 -> h2 -> h3)...")
    print(h1.cmd('curl -s http://10.0.0.2:8080/'))
    
    print("\n[4] Request cu verbose output...")
    print(h1.cmd('curl -v http://10.0.0.2:8080/ 2>&1 | head -20'))
    
    print("\n" + "="*60)
    print("CAPTURI DE TRAFIC")
    print("="*60)
    
    print("\n[5] Pornim tcpdump pe Proxy (h2)...")
    h2.cmd('tcpdump -i h2-eth0 -c 10 -w /tmp/proxy_capture.pcap &')
    
    print("[6] Facem 3 cereri...")
    for i in range(3):
        h1.cmd(f'curl -s http://10.0.0.2:8080/ > /dev/null')
        print(f"    Request {i+1} trimis")
        time.sleep(0.5)
    
    time.sleep(2)
    print("\n[7] Analizăm captura...")
    print(h2.cmd('tcpdump -r /tmp/proxy_capture.pcap -n 2>/dev/null | head -20'))


def interactive_mode(net):
    """
    Mod interactiv cu CLI Mininet.
    """
    print("\n" + "="*60)
    print("MOD INTERACTIV")
    print("="*60)
    print("""
Comenzi utile:
    h1 curl http://10.0.0.2:8080/          - Request prin proxy
    h1 curl http://10.0.0.3:8081/          - Request direct la backend
    h2 tcpdump -i h2-eth0                  - Captură pe proxy
    h3 tail -f /var/log/http_server.log   - Logs backend (dacă există)
    
    pingall                                - Verifică conectivitate
    net                                    - Afișează topologia
    dump                                   - Detalii host-uri
    
    exit                                   - Ieșire
""")
    CLI(net)


def main():
    parser = argparse.ArgumentParser(
        description="Topologie Mininet pentru HTTP Server & Reverse Proxy"
    )
    parser.add_argument(
        '--delay', type=int, default=0,
        help='Delay per link în milisecunde (default: 0)'
    )
    parser.add_argument(
        '--loss', type=int, default=0,
        help='Procent pierdere pachete (default: 0)'
    )
    parser.add_argument(
        '--no-demo', action='store_true',
        help='Sări peste demo automat, intră direct în CLI'
    )
    parser.add_argument(
        '--cli-only', action='store_true',
        help='Doar CLI, fără pornire servere'
    )
    
    args = parser.parse_args()
    
    # Verificăm dacă rulăm ca root
    if os.geteuid() != 0:
        print("EROARE: Acest script trebuie rulat ca root (sudo)")
        sys.exit(1)
    
    setLogLevel('info')
    
    # Creăm topologia
    net = create_topology(delay_ms=args.delay, loss_pct=args.loss)
    
    try:
        info("*** Pornim rețeaua ***\n")
        net.start()
        
        if not args.cli_only:
            # Pornim serverele
            setup_servers(net)
        
        if not args.no_demo and not args.cli_only:
            # Rulăm demo-ul
            run_demo(net)
        
        # Intrăm în mod interactiv
        interactive_mode(net)
        
    finally:
        info("*** Oprim rețeaua ***\n")
        net.stop()


if __name__ == '__main__':
    main()
