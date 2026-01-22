#!/usr/bin/env python3
"""
Scenariul 3: Demonstrație Protocol UDP pentru Senzori
======================================================

Obiective didactice:
- Înțelegerea diferențelor TCP vs UDP
- Implementarea unui protocol binar peste UDP
- Observarea comportamentului connectionless
- Analiza datagramelor UDP cu tshark

Topologie:
    h1 (10.0.0.1) ---- s1 (switch) ---- h2 (10.0.0.2)
       [senzor]                          [colector]
                           |
                       h3 (10.0.0.3)
                        [senzor 2]

Utilizare:
    sudo python3 scenario_udp_demo.py

Autor: Revolvix&Hypotheticalandrei
Săptămâna 4 - Protocol UDP pentru IoT/Senzori
"""

from mininet.net import Mininet
from mininet.node import Controller, OVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink
import time
import os
import sys
import random

# Calea către aplicațiile Python
APPS_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'python', 'apps'))


def create_topology():
    """
    Creează topologia: 2 senzori (h1, h3) + 1 colector (h2).
    """
    info('*** Creare topologie pentru demo UDP Senzori ***\n')
    
    net = Mininet(
        controller=Controller,
        switch=OVSSwitch,
        link=TCLink,
        autoSetMacs=True
    )
    
    info('*** Adăugare controller ***\n')
    net.addController('c0')
    
    info('*** Adăugare switch ***\n')
    s1 = net.addSwitch('s1')
    
    info('*** Adăugare hosturi ***\n')
    h1 = net.addHost('h1', ip='10.0.0.1/24')  # Senzor 1
    h2 = net.addHost('h2', ip='10.0.0.2/24')  # Colector/Server
    h3 = net.addHost('h3', ip='10.0.0.3/24')  # Senzor 2
    
    info('*** Creare legături ***\n')
    # Simulăm legături cu caracteristici diferite
    net.addLink(h1, s1, bw=10, delay='5ms', loss=0)   # Senzor local, stabil
    net.addLink(h2, s1, bw=100, delay='1ms', loss=0)  # Server, conexiune bună
    net.addLink(h3, s1, bw=10, delay='20ms', loss=2)  # Senzor remote, instabil
    
    return net


def run_udp_sensor_demo(net):
    """
    Demonstrație protocol UDP pentru senzori.
    """
    h1, h2, h3 = net.get('h1', 'h2', 'h3')
    
    print("\n" + "="*70)
    print("DEMO: Protocol UDP pentru Senzori IoT")
    print("="*70)
    
    print("""
Protocol UDP Senzori:
- Datagramă fixă: 23 bytes
- Fără conexiune (connectionless)
- Fire-and-forget (nu așteaptă ACK)
- Ideal pentru date de telemetrie

Structura datagramă (23 bytes):
  [0]      Version: 1
  [1:5]    Sensor ID (uint32 BE)
  [5:9]    Temperature (float32 BE, °C)
  [9:19]   Location (10 chars, padding spații)
  [19:23]  CRC32 (uint32 BE)
""")
    
    # Pasul 1: Pornim captura pe colector
    print("\n[PASUL 1] Pornire captură UDP pe colector (h2)")
    print("-" * 50)
    capture_file = '/tmp/udp_sensor_capture.pcap'
    h2.cmd(f'tshark -i h2-eth0 -w {capture_file} -f "udp port 5402" &')
    time.sleep(1)
    
    # Pasul 2: Pornim serverul/colectorul pe h2
    print("\n[PASUL 2] Pornire colector UDP pe h2:5402")
    print("-" * 50)
    server_cmd = f'cd {APPS_PATH} && python3 udp_sensor_server.py --host 0.0.0.0 --port 5402 &'
    h2.cmd(server_cmd)
    print("Colectorul așteaptă date de la senzori...")
    time.sleep(2)
    
    # Pasul 3: Senzorul 1 (h1) trimite date
    print("\n[PASUL 3] Senzorul 1 (h1) trimite citiri de temperatură")
    print("-" * 50)
    
    temperatures = [22.5, 23.1, 22.8, 24.0, 23.5]
    for temp in temperatures:
        # Simulăm trimiterea cu client UDP
        client_cmd = f'cd {APPS_PATH} && python3 udp_sensor_client.py --host 10.0.0.2 --port 5402 --sensor-id 1001 --temperature {temp} --location "Sala_A1"'
        result = h1.cmd(client_cmd)
        print(f"  Senzor 1001 @ Sala_A1: {temp}°C")
        time.sleep(0.3)
    
    # Pasul 4: Senzorul 2 (h3) trimite date (cu pierderi simulate)
    print("\n[PASUL 4] Senzorul 2 (h3) trimite citiri (conexiune instabilă)")
    print("-" * 50)
    print("Notă: Linkul h3-s1 are 2% packet loss simulat")
    
    temperatures = [18.2, 17.9, 18.5, 19.0, 18.7]
    for temp in temperatures:
        client_cmd = f'cd {APPS_PATH} && python3 udp_sensor_client.py --host 10.0.0.2 --port 5402 --sensor-id 2001 --temperature {temp} --location "Exterior"'
        result = h3.cmd(client_cmd)
        print(f"  Senzor 2001 @ Exterior: {temp}°C")
        time.sleep(0.3)
    
    # Pasul 5: Oprim și analizăm
    print("\n[PASUL 5] Oprire și analiza traficului")
    print("-" * 50)
    h2.cmd('pkill -f udp_sensor_server')
    h2.cmd('pkill tshark')
    time.sleep(1)
    
    if os.path.exists(capture_file):
        # Statistici
        print("Statistici datagrame UDP:")
        stats = h2.cmd(f'tshark -r {capture_file} -q -z io,stat,0,udp 2>/dev/null')
        print(stats)
        
        # Hex dump pentru analiza structurii
        print("\nStructura datagramelor (hex):")
        hex_output = h2.cmd(f'tshark -r {capture_file} -x 2>/dev/null | head -40')
        print(hex_output)
        
        # Dimensiuni pachete
        print("\nDimensiuni pachete UDP:")
        sizes = h2.cmd(f'tshark -r {capture_file} -T fields -e udp.length 2>/dev/null | sort | uniq -c')
        print(sizes)


def demonstrate_udp_characteristics(net):
    """
    Demonstrează caracteristicile UDP vs TCP.
    """
    h1, h2 = net.get('h1', 'h2')
    
    print("\n" + "="*70)
    print("CARACTERISTICI UDP vs TCP")
    print("="*70)
    
    print("""
┌────────────────────┬─────────────────────┬─────────────────────┐
│ Caracteristică     │ TCP                 │ UDP                 │
├────────────────────┼─────────────────────┼─────────────────────┤
│ Conexiune          │ Orientat conexiune  │ Fără conexiune      │
│ Handshake          │ 3-way (SYN-SYN/ACK) │ Niciuna             │
│ Livrare garantată  │ Da (retransmisie)   │ Nu                  │
│ Ordine pachete     │ Da (sequence nr)    │ Nu                  │
│ Control flux       │ Da (window)         │ Nu                  │
│ Control congestie  │ Da (slow start)     │ Nu                  │
│ Overhead           │ 20+ bytes header    │ 8 bytes header      │
│ Latență            │ Mai mare            │ Mai mică            │
│ Cazuri de utilizare│ HTTP, FTP, SSH      │ DNS, VoIP, Gaming   │
└────────────────────┴─────────────────────┴─────────────────────┘
""")
    
    # Demonstrație: UDP nu are handshake
    print("\n[DEMO] UDP nu necesită handshake - trimitem direct")
    print("-" * 50)
    
    # Trimitem UDP către un port care nu ascultă
    print("Trimitem datagramă către port inexistent (5556)...")
    result = h1.cmd('echo "test" | nc -u -w1 10.0.0.2 5556 2>&1')
    print("Observație: Clientul nu primește eroare - UDP este fire-and-forget")
    print("(Doar dacă serverul trimite ICMP Port Unreachable)")
    
    # Demonstrație: multiple datagrame pot ajunge în ordine diferită
    print("\n[DEMO] Ordinea datagramelor nu este garantată")
    print("-" * 50)
    print("La latență mare sau pierderi, datagramele pot ajunge:")
    print("- În altă ordine decât au fost trimise")
    print("- Unele pot fi pierdute complet")
    print("- Unele pot fi duplicate (rar)")


def show_udp_header_analysis(net):
    """
    Analiza detaliată a header-ului UDP.
    """
    print("\n" + "="*70)
    print("ANALIZA HEADER UDP (8 bytes)")
    print("="*70)
    
    print("""
Header UDP (8 bytes total):

    0                   1                   2                   3
    0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |          Source Port          |       Destination Port        |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |            Length             |           Checksum            |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

Câmpuri:
- Source Port (16 biți): Port sursă (0-65535)
- Destination Port (16 biți): Port destinație
- Length (16 biți): Lungime totală (header + date), minim 8
- Checksum (16 biți): Verificare integritate (opțional în IPv4)

Exemplu pentru senzorul nostru:
- Src Port: 12345 (efemer, alocat de OS)
- Dst Port: 5402 (portul colectorului)
- Length: 8 + 23 = 31 bytes (header + datagramă senzor)
- Checksum: calculat automat de kernel
""")


def interactive_mode(net):
    """
    Instrucțiuni pentru modul interactiv.
    """
    print("\n" + "="*70)
    print("MOD INTERACTIV - Comenzi pentru experimentare UDP")
    print("="*70)
    print(f"""
Calea aplicațiilor: {APPS_PATH}

Pornire colector (server):
  h2 cd {APPS_PATH} && python3 udp_sensor_server.py --port 5402 &

Trimitere date senzor:
  h1 cd {APPS_PATH} && python3 udp_sensor_client.py \\
     --host 10.0.0.2 --port 5402 \\
     --sensor-id 1001 --temperature 25.5 --location "Lab"

Testare cu netcat (UDP):
  h2 nc -u -l 5402                    # Server UDP simplu
  h1 echo "test" | nc -u 10.0.0.2 5402  # Client UDP

Captură și analiză:
  h2 tshark -i h2-eth0 -f "udp port 5402" -V
  h2 tcpdump -i h2-eth0 -vv udp port 5402

Simulare pierderi (pe link):
  # Adăugare 10% loss pe h1-eth0
  h1 tc qdisc add dev h1-eth0 root netem loss 10%
  
  # Verificare
  h1 tc qdisc show dev h1-eth0
  
  # Resetare
  h1 tc qdisc del dev h1-eth0 root

Broadcast UDP (toate hosturile):
  h1 echo "broadcast" | nc -u -b 10.0.0.255 5402

Verificare porturi UDP:
  h2 ss -ulnp
  h2 netstat -anu

exit - Ieșire din CLI
""")


def main():
    """
    Punctul de intrare principal.
    """
    setLogLevel('info')
    
    print("\n" + "="*70)
    print("SCENARIUL 3: Protocol UDP pentru Senzori IoT")
    print("Săptămâna 4 - Datagrame UDP și telemetrie")
    print("="*70)
    
    # Verificăm existența fișierelor Python
    if not os.path.exists(APPS_PATH):
        print(f"\n[EROARE] Nu s-a găsit directorul: {APPS_PATH}")
        sys.exit(1)
    
    required_files = [
        'udp_sensor_server.py',
        'udp_sensor_client.py'
    ]
    
    for f in required_files:
        if not os.path.exists(os.path.join(APPS_PATH, f)):
            print(f"\n[EROARE] Lipsește fișierul: {f}")
            sys.exit(1)
    
    net = create_topology()
    
    try:
        info('*** Pornire rețea ***\n')
        net.start()
        
        time.sleep(2)
        
        # Demonstrații
        run_udp_sensor_demo(net)
        demonstrate_udp_characteristics(net)
        show_udp_header_analysis(net)
        
        # Mod interactiv
        interactive_mode(net)
        
        info('*** Intrare în CLI Mininet ***\n')
        CLI(net)
        
    finally:
        info('*** Oprire rețea ***\n')
        
        # Curățare
        for host in net.hosts:
            host.cmd('pkill -f udp_sensor')
            host.cmd('pkill tshark')
            host.cmd('pkill tcpdump')
        
        net.stop()
        
        if os.path.exists('/tmp/udp_sensor_capture.pcap'):
            os.remove('/tmp/udp_sensor_capture.pcap')


if __name__ == '__main__':
    main()
