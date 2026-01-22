#!/usr/bin/env python3
"""
Topologie Mininet Simplă - Săptămâna 1
======================================
Rețele de Calculatoare
ASE București

Această topologie creează o rețea simplă cu:
- 3 host-uri (h1, h2, h3)
- 1 switch OpenFlow (s1)
- Legături cu bandwidth și delay configurabile

Utilizare:
    sudo python3 topo_simple.py
    sudo python3 topo_simple.py --test    # Rulează teste automate
    sudo mn --custom topo_simple.py --topo simple,3
"""

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Controller, OVSKernelSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink
import sys
import time


class SimpleTopo(Topo):
    """
    Topologie simplă: N host-uri conectate la un switch central.
    
    Structură:
        h1 ──┐
        h2 ──┼── s1
        h3 ──┘
    """
    
    def build(self, n: int = 3, bw: int = 100, delay: str = "1ms"):
        """
        Construiește topologia.
        
        Args:
            n: Numărul de host-uri
            bw: Bandwidth în Mbps pentru fiecare legătură
            delay: Delay per legătură (ex: "1ms", "10ms")
        """
        # Creăm switch-ul central
        switch = self.addSwitch('s1')
        
        # Adăugăm host-urile și le conectăm la switch
        for i in range(1, n + 1):
            host = self.addHost(f'h{i}')
            self.addLink(
                host, switch,
                bw=bw,
                delay=delay,
                loss=0,  # Fără packet loss
                max_queue_size=1000
            )


class DualSwitchTopo(Topo):
    """
    Topologie cu 2 switch-uri interconectate.
    
    Structură:
        h1 ──┐         ┌── h3
        h2 ──┼── s1 ── s2 ──┼── h4
             │         │
    """
    
    def build(self, bw: int = 100, inter_switch_bw: int = 1000):
        """
        Construiește topologia cu 2 switch-uri.
        
        Args:
            bw: Bandwidth pentru legături host-switch
            inter_switch_bw: Bandwidth pentru legătura switch-switch
        """
        # Switch-uri
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        
        # Host-uri pentru s1
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')
        
        # Host-uri pentru s2
        h3 = self.addHost('h3')
        h4 = self.addHost('h4')
        
        # Legături host-switch
        self.addLink(h1, s1, bw=bw, delay='1ms')
        self.addLink(h2, s1, bw=bw, delay='1ms')
        self.addLink(h3, s2, bw=bw, delay='1ms')
        self.addLink(h4, s2, bw=bw, delay='1ms')
        
        # Legătură switch-switch (trunk)
        self.addLink(s1, s2, bw=inter_switch_bw, delay='2ms')


def run_simple_network(n_hosts: int = 3):
    """
    Pornește rețeaua și intră în CLI.
    
    Args:
        n_hosts: Numărul de host-uri de creat
    """
    setLogLevel('info')
    
    info('*** Creare topologie cu %d host-uri\n' % n_hosts)
    topo = SimpleTopo(n=n_hosts, bw=100, delay='1ms')
    
    info('*** Pornire rețea\n')
    net = Mininet(
        topo=topo,
        controller=Controller,
        switch=OVSKernelSwitch,
        link=TCLink,
        autoSetMacs=True
    )
    
    net.start()
    
    info('\n*** Informații rețea:\n')
    for host in net.hosts:
        info(f'    {host.name}: {host.IP()}\n')
    
    info('\n*** Testare conectivitate (pingall):\n')
    net.pingAll()
    
    info('\n*** Intrare în CLI (comenzi: help, nodes, net, dump, exit)\n')
    CLI(net)
    
    info('*** Oprire rețea\n')
    net.stop()


def run_automated_tests():
    """
    Rulează teste automate pentru verificare.
    """
    setLogLevel('warning')
    
    print("\n" + "="*60)
    print(" TEST AUTOMAT TOPOLOGIE MININET ".center(60))
    print("="*60 + "\n")
    
    tests_passed = 0
    tests_total = 4
    
    # Creăm rețeaua
    print("[TEST] Creare rețea cu 3 host-uri...", end=" ", flush=True)
    try:
        topo = SimpleTopo(n=3)
        net = Mininet(topo=topo, controller=Controller, link=TCLink)
        net.start()
        time.sleep(1)  # Așteptăm stabilizarea
        print("✓ PASS")
        tests_passed += 1
    except Exception as e:
        print(f"✗ FAIL ({e})")
        return False
    
    try:
        # Test 1: Verificăm că avem 3 host-uri
        print("[TEST] Verificare număr host-uri...", end=" ", flush=True)
        if len(net.hosts) == 3:
            print("✓ PASS")
            tests_passed += 1
        else:
            print(f"✗ FAIL (așteptat 3, găsit {len(net.hosts)})")
        
        # Test 2: Ping între h1 și h2
        print("[TEST] Ping h1 -> h2...", end=" ", flush=True)
        h1, h2 = net.get('h1'), net.get('h2')
        result = h1.cmd(f'ping -c 1 -W 1 {h2.IP()}')
        if '1 received' in result:
            print("✓ PASS")
            tests_passed += 1
        else:
            print("✗ FAIL")
        
        # Test 3: Ping all
        print("[TEST] Pingall (0% loss)...", end=" ", flush=True)
        loss = net.pingAll(timeout=1)
        if loss == 0:
            print("✓ PASS")
            tests_passed += 1
        else:
            print(f"✗ FAIL ({loss}% loss)")
        
    finally:
        net.stop()
    
    print(f"\nRezultat: {tests_passed}/{tests_total} teste trecute")
    return tests_passed == tests_total


def demo_server_client():
    """
    Demonstrație: server netcat pe h1, client pe h2.
    """
    setLogLevel('info')
    
    print("\n" + "="*60)
    print(" DEMO: Server-Client în Mininet ".center(60))
    print("="*60 + "\n")
    
    topo = SimpleTopo(n=2)
    net = Mininet(topo=topo, controller=Controller, link=TCLink)
    net.start()
    
    h1, h2 = net.get('h1'), net.get('h2')
    
    print(f"[INFO] h1 IP: {h1.IP()}")
    print(f"[INFO] h2 IP: {h2.IP()}")
    
    # Pornim server pe h1
    print("\n[DEMO] Pornire server netcat pe h1:5000...")
    h1.cmd('nc -l -p 5000 > /tmp/received.txt &')
    time.sleep(0.5)
    
    # Trimitem date de la h2
    print("[DEMO] Trimitere mesaj de la h2...")
    h2.cmd(f'echo "Hello from h2!" | nc {h1.IP()} 5000')
    time.sleep(0.5)
    
    # Verificăm ce a primit h1
    received = h1.cmd('cat /tmp/received.txt')
    print(f"[DEMO] h1 a primit: {received.strip()}")
    
    # Captură tshark pe h1
    print("\n[DEMO] Captură trafic pe h1 (5 pachete)...")
    h1.cmd('tshark -i h1-eth0 -c 5 -w /tmp/capture.pcap 2>/dev/null &')
    time.sleep(0.5)
    
    # Generăm trafic
    h2.cmd(f'ping -c 3 {h1.IP()}')
    time.sleep(1)
    
    # Afișăm captura
    capture_output = h1.cmd('tshark -r /tmp/capture.pcap 2>/dev/null')
    print(f"[DEMO] Captură:\n{capture_output}")
    
    net.stop()
    print("\n[INFO] Demo încheiat.")


# Înregistrăm topologiile pentru utilizare cu --custom
topos = {
    'simple': SimpleTopo,
    'dual': DualSwitchTopo
}


if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == '--test':
            success = run_automated_tests()
            sys.exit(0 if success else 1)
        elif sys.argv[1] == '--demo':
            demo_server_client()
        elif sys.argv[1].isdigit():
            run_simple_network(int(sys.argv[1]))
        else:
            print(f"""
Utilizare:
    sudo python3 topo_simple.py           # Rețea cu 3 host-uri + CLI
    sudo python3 topo_simple.py 5         # Rețea cu 5 host-uri
    sudo python3 topo_simple.py --test    # Teste automate
    sudo python3 topo_simple.py --demo    # Demo server-client
    
    # Sau cu mn:
    sudo mn --custom topo_simple.py --topo simple,4
    sudo mn --custom topo_simple.py --topo dual
""")
    else:
        run_simple_network()
