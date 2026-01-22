#!/usr/bin/env python3
"""
Topologie Mininet de bază pentru Seminar/Laborator 9
Rețele de Calculatoare - ASE București

Topologie simplă cu 2 hosts și 1 switch:
    h1 (server) ──── s1 ──── h2 (client)
    10.0.9.11              10.0.9.12

Plan IP Week 9: 10.0.9.0/24
  - Gateway: 10.0.9.1
  - Hosts: 10.0.9.11-19
  - Server: 10.0.9.100

Utilizare:
    sudo python topo_base.py
    
În CLI Mininet:
    mininet> pingall
    mininet> h1 python /path/to/server.py &
    mininet> h2 python /path/to/client.py --host 10.0.9.11

Revolvix&Hypotheticalandrei | Licență MIT
"""

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Controller, OVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink
import argparse
import os
import sys

# Week 9 IP Plan
WEEK = 9
NETWORK = f"10.0.{WEEK}"
H1_IP = f"{NETWORK}.11/24"
H2_IP = f"{NETWORK}.12/24"
SERVER_IP = f"{NETWORK}.100/24"

class FTPBaseTopo(Topo):
    """
    Topologie de bază cu 2 hosts pentru testare server-client.
    
    Configurație:
    - h1: Server FTP (10.0.0.1)
    - h2: Client FTP (10.0.0.2)
    - s1: Switch OpenFlow
    - Link-uri cu bandwidth configurabil
    """
    
    def build(self, bw=100, delay='0ms', loss=0):
        """
        Construiește topologia.
        
        Args:
            bw: Bandwidth în Mbps (default: 100)
            delay: Latență unidirecțională (default: '0ms')
            loss: Packet loss în procente (default: 0)
        """
        info('*** Construire topologie de bază (Week 9: 10.0.9.0/24)\n')
        
        # Adăugare switch
        s1 = self.addSwitch('s1', cls=OVSSwitch)
        
        # Adăugare hosts cu IP-uri Week 9
        h1 = self.addHost('h1', ip=H1_IP)  # 10.0.9.11
        h2 = self.addHost('h2', ip=H2_IP)  # 10.0.9.12
        
        # Configurare link-uri cu parametri de performanță
        link_opts = {
            'bw': bw,
            'delay': delay,
            'loss': loss,
            'use_htb': True  # Hierarchical Token Bucket pentru rate limiting
        }
        
        # Adăugare link-uri
        self.addLink(h1, s1, **link_opts)
        self.addLink(h2, s1, **link_opts)
        
        info(f'*** Topologie: h1 --[{bw}Mbps, {delay}, {loss}% loss]-- s1 --[{bw}Mbps, {delay}, {loss}% loss]-- h2\n')


def setup_environment(net):
    """
    Configurează mediul pentru demo-uri.
    
    - Creează directoare necesare
    - Copiază fișiere de test
    """
    h1 = net.get('h1')
    h2 = net.get('h2')
    
    # Creează directoare pentru server și client
    h1.cmd('mkdir -p /tmp/server-files')
    h2.cmd('mkdir -p /tmp/client-files')
    
    # Creează fișiere de test pe server
    h1.cmd('echo "Test file content for FTP demo" > /tmp/server-files/test.txt')
    h1.cmd('dd if=/dev/urandom of=/tmp/server-files/binary.bin bs=1024 count=10 2>/dev/null')
    
    info('*** Mediu configurat:\n')
    info('    h1:/tmp/server-files/ - directorul serverului\n')
    info('    h2:/tmp/client-files/ - directorul clientului\n')


def print_help():
    """Afișează instrucțiuni pentru utilizare în CLI."""
    help_text = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                    MININET FTP BASE TOPOLOGY - HELP                          ║
║                    Week 9 IP Plan: 10.0.9.0/24                               ║
╚══════════════════════════════════════════════════════════════════════════════╝

INFORMAȚII HOSTS:
  h1 (10.0.9.11) - Server FTP
  h2 (10.0.9.12) - Client FTP

COMENZI UTILE:

  Verificare conectivitate:
    mininet> pingall
    mininet> h1 ping -c 3 h2

  Pornire server (exemplu):
    mininet> h1 python3 /path/to/ex_9_02_pseudo_ftp.py server --port 5900 &

  Pornire client (exemplu):
    mininet> h2 python3 /path/to/ex_9_02_pseudo_ftp.py client --host 10.0.9.11 --port 5900

  Verificare procese:
    mininet> h1 ps aux | grep python
    
  Oprire server:
    mininet> h1 pkill -f pseudo_ftp

  Capturare trafic:
    mininet> h1 tcpdump -i h1-eth0 -w /tmp/capture.pcap &
    
  Adăugare latență în runtime:
    mininet> sh tc qdisc add dev s1-eth1 root netem delay 50ms
    
  Verificare latență:
    mininet> h1 ping -c 5 h2

DIRECTOARE:
  Server: h1:/tmp/server-files/
  Client: h2:/tmp/client-files/

IEȘIRE:
  mininet> exit
  sau Ctrl+D

═══════════════════════════════════════════════════════════════════════════════
"""
    print(help_text)


def run_topology(bw=100, delay='0ms', loss=0, interactive=True):
    """
    Pornește topologia Mininet.
    
    Args:
        bw: Bandwidth în Mbps
        delay: Latență ca string (ex: '10ms')
        loss: Packet loss în procente
        interactive: Dacă True, pornește CLI; altfel returnează rețeaua
    """
    setLogLevel('info')
    
    info('*** Creare topologie FTP Base\n')
    topo = FTPBaseTopo(bw=bw, delay=delay, loss=loss)
    
    info('*** Pornire rețea Mininet\n')
    net = Mininet(
        topo=topo,
        controller=Controller,
        link=TCLink,
        autoSetMacs=True
    )
    
    net.start()
    
    info('*** Configurare mediu\n')
    setup_environment(net)
    
    info('*** Test conectivitate\n')
    net.pingAll()
    
    if interactive:
        info('\n*** Tastați "help" pentru instrucțiuni\n')
        
        # Înregistrăm comanda help
        CLI.do_ftphelp = lambda self, _: print_help()
        
        CLI(net)
        
        info('*** Oprire rețea\n')
        net.stop()
    else:
        return net


def main():
    """Punct de intrare principal."""
    parser = argparse.ArgumentParser(
        description='Topologie Mininet de bază pentru Seminar 9 - FTP',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemple:
  sudo python topo_base.py                    # Configurație default
  sudo python topo_base.py --delay 50ms       # Cu 50ms latență
  sudo python topo_base.py --loss 5           # Cu 5% packet loss
  sudo python topo_base.py --bw 10            # Bandwidth limitat la 10 Mbps
        """
    )
    
    parser.add_argument(
        '--bw', type=int, default=100,
        help='Bandwidth în Mbps (default: 100)'
    )
    parser.add_argument(
        '--delay', type=str, default='0ms',
        help='Latență unidirecțională (default: 0ms)'
    )
    parser.add_argument(
        '--loss', type=float, default=0,
        help='Packet loss în procente (default: 0)'
    )
    
    args = parser.parse_args()
    
    # Verificare privilegii root
    if os.geteuid() != 0:
        print("EROARE: Acest script necesită privilegii root.")
        print("Rulați cu: sudo python topo_base.py")
        sys.exit(1)
    
    run_topology(bw=args.bw, delay=args.delay, loss=args.loss)


if __name__ == '__main__':
    main()
