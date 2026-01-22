#!/usr/bin/env python3
"""
Scenariul 1: Demonstrație ARP și învățare CAM în Switch
=========================================================

Obiective didactice:
- Observarea rezolvării ARP (Address Resolution Protocol)
- Analiza tabelei CAM (Content Addressable Memory) într-un switch
- Capturarea și interpretarea pachetelor ARP Request/Reply

Topologie:
    h1 (10.0.0.1) ---- s1 (switch) ---- h2 (10.0.0.2)
                           |
                       h3 (10.0.0.3)

Utilizare:
    sudo python3 scenario_arp_demo.py

Cerințe:
    - Mininet instalat (apt install mininet)
    - Drepturi de root (sudo)

Autor: Revolvix&Hypotheticalandrei
Săptămâna 4 - Nivelul Fizic și Legătura de Date
"""

from mininet.net import Mininet
from mininet.node import Controller, OVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink
import time
import subprocess
import os


def create_topology():
    """
    Creează topologia de rețea cu 3 hosturi conectate la un switch.
    """
    info('*** Creare topologie pentru demo ARP ***\n')
    
    # Creăm rețeaua Mininet
    net = Mininet(
        controller=Controller,
        switch=OVSSwitch,
        link=TCLink,
        autoSetMacs=True  # MAC-uri predictibile: 00:00:00:00:00:01, etc.
    )
    
    info('*** Adăugare controller ***\n')
    net.addController('c0')
    
    info('*** Adăugare switch ***\n')
    s1 = net.addSwitch('s1')
    
    info('*** Adăugare hosturi ***\n')
    h1 = net.addHost('h1', ip='10.0.0.1/24')
    h2 = net.addHost('h2', ip='10.0.0.2/24')
    h3 = net.addHost('h3', ip='10.0.0.3/24')
    
    info('*** Creare legături ***\n')
    # Legături cu bandwidth limitat pentru observare mai clară
    net.addLink(h1, s1, bw=10, delay='5ms')
    net.addLink(h2, s1, bw=10, delay='5ms')
    net.addLink(h3, s1, bw=10, delay='5ms')
    
    return net


def clear_arp_caches(net):
    """
    Șterge cache-urile ARP de pe toate hosturile.
    """
    info('*** Ștergere cache ARP pe toate hosturile ***\n')
    for host in net.hosts:
        host.cmd('ip neigh flush all')
        info(f'    {host.name}: Cache ARP curățat\n')


def show_arp_cache(host):
    """
    Afișează cache-ul ARP al unui host.
    """
    result = host.cmd('arp -n')
    return result


def show_switch_mac_table(switch):
    """
    Afișează tabela MAC (CAM) a switch-ului.
    """
    result = switch.cmd('ovs-appctl fdb/show s1')
    return result


def run_arp_demo(net):
    """
    Demonstrație pas cu pas a procesului ARP.
    """
    h1, h2, h3 = net.get('h1', 'h2', 'h3')
    s1 = net.get('s1')
    
    print("\n" + "="*70)
    print("DEMONSTRAȚIE ARP - Rezolvare adrese și învățare MAC")
    print("="*70)
    
    # Pasul 1: Afișăm starea inițială
    print("\n[PASUL 1] Stare inițială - cache-uri ARP goale")
    print("-" * 50)
    clear_arp_caches(net)
    print(f"h1 ARP cache:\n{show_arp_cache(h1)}")
    print(f"Tabela MAC switch s1:\n{show_switch_mac_table(s1)}")
    
    # Pasul 2: Pornim captură tshark pe h2
    print("\n[PASUL 2] Pornire captură pachete pe h2")
    print("-" * 50)
    print("Comandă: tshark -i h2-eth0 -c 5 -f 'arp or icmp'")
    
    # Pornim tshark în background
    h2.cmd('tshark -i h2-eth0 -c 5 -f "arp or icmp" -w /tmp/arp_capture.pcap &')
    time.sleep(1)
    
    # Pasul 3: h1 face ping către h2 (declanșează ARP)
    print("\n[PASUL 3] h1 trimite ping către h2 (10.0.0.2)")
    print("-" * 50)
    print("Aceasta declanșează ARP Request deoarece h1 nu cunoaște MAC-ul lui h2")
    
    result = h1.cmd('ping -c 1 10.0.0.2')
    print(f"Rezultat ping:\n{result}")
    
    time.sleep(2)
    
    # Pasul 4: Verificăm cache-urile ARP actualizate
    print("\n[PASUL 4] Cache-uri ARP după ping")
    print("-" * 50)
    print(f"h1 a învățat MAC-ul lui h2:\n{show_arp_cache(h1)}")
    print(f"h2 a învățat MAC-ul lui h1:\n{show_arp_cache(h2)}")
    
    # Pasul 5: Verificăm tabela CAM a switch-ului
    print("\n[PASUL 5] Tabela MAC a switch-ului (învățare CAM)")
    print("-" * 50)
    print("Switch-ul a învățat pe ce port se află fiecare MAC:")
    print(show_switch_mac_table(s1))
    
    # Pasul 6: Analizăm captura
    print("\n[PASUL 6] Analiza capturii (pachete ARP)")
    print("-" * 50)
    h2.cmd('pkill tshark')
    time.sleep(1)
    
    if os.path.exists('/tmp/arp_capture.pcap'):
        analysis = h2.cmd('tshark -r /tmp/arp_capture.pcap -V 2>/dev/null | head -100')
        print(analysis)
    
    # Pasul 7: Demonstrăm că al doilea ping nu generează ARP
    print("\n[PASUL 7] Al doilea ping - fără ARP (cache valid)")
    print("-" * 50)
    print("Deoarece h1 cunoaște deja MAC-ul lui h2, nu se mai trimite ARP Request")
    result = h1.cmd('ping -c 1 10.0.0.2')
    print(f"Ping direct (fără latență ARP):\n{result}")
    
    # Pasul 8: Demonstrăm broadcast ARP
    print("\n[PASUL 8] h1 face ping către h3 (ARP broadcast)")
    print("-" * 50)
    print("ARP Request este trimis broadcast (ff:ff:ff:ff:ff:ff)")
    print("Doar h3 răspunde, dar toate hosturile primesc request-ul")
    
    h3.cmd('tcpdump -i h3-eth0 -c 2 arp &')
    time.sleep(0.5)
    result = h1.cmd('ping -c 1 10.0.0.3')
    print(f"Rezultat:\n{result}")
    time.sleep(1)
    
    print("\n" + "="*70)
    print("CONCLUZII")
    print("="*70)
    print("""
1. ARP Request este trimis BROADCAST (destinație MAC: ff:ff:ff:ff:ff:ff)
2. ARP Reply este trimis UNICAST către solicitant
3. Switch-ul învață asocierea MAC→Port din pachetele primite (learning)
4. Cache-ul ARP are TTL limitat (implicit ~60s în Linux)
5. Flooding: Switch-ul trimite broadcast pe toate porturile (mai puțin sursa)
""")


def interactive_mode(net):
    """
    Oferă comenzi interactive pentru explorare.
    """
    print("\n" + "="*70)
    print("MOD INTERACTIV - Comenzi utile")
    print("="*70)
    print("""
Comenzi pentru explorare ARP și CAM:

  h1 arp -n                    # Afișează cache ARP pe h1
  h1 ip neigh                  # Alternativă modernă pentru ARP
  h1 ip neigh flush all        # Șterge cache ARP
  
  h1 ping -c 1 10.0.0.2        # Ping (declanșează ARP dacă necesar)
  h1 arping -c 1 10.0.0.2      # Trimite doar ARP Request
  
  s1 ovs-appctl fdb/show s1    # Tabela MAC a switch-ului
  s1 ovs-ofctl dump-flows s1   # Flow-uri OpenFlow
  
  h2 tcpdump -i h2-eth0 arp    # Captură pachete ARP
  h2 tshark -i h2-eth0 -f arp  # Captură cu tshark
  
  pingall                      # Ping între toate perechile
  net                          # Afișează topologia
  dump                         # Informații despre noduri
  
  exit                         # Ieșire din CLI
""")


def main():
    """
    Punctul de intrare principal.
    """
    setLogLevel('info')
    
    print("\n" + "="*70)
    print("SCENARIUL 1: Demonstrație ARP și Învățare CAM")
    print("Săptămâna 4 - Nivelul Fizic și Legătura de Date")
    print("="*70)
    
    net = create_topology()
    
    try:
        info('*** Pornire rețea ***\n')
        net.start()
        
        # Așteptăm stabilizarea rețelei
        time.sleep(2)
        
        # Rulăm demonstrația
        run_arp_demo(net)
        
        # Oferim instrucțiuni pentru modul interactiv
        interactive_mode(net)
        
        # Intrăm în CLI pentru explorare
        info('*** Intrare în CLI Mininet ***\n')
        CLI(net)
        
    finally:
        info('*** Oprire rețea ***\n')
        net.stop()
        
        # Curățare fișiere temporare
        if os.path.exists('/tmp/arp_capture.pcap'):
            os.remove('/tmp/arp_capture.pcap')


if __name__ == '__main__':
    main()
