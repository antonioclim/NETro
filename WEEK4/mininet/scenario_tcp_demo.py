#!/usr/bin/env python3
"""
Scenariul 2: Demonstrație Protocoale TEXT și BINARY peste TCP
==============================================================

Obiective didactice:
- Rularea aplicațiilor client-server în topologie Mininet
- Observarea diferențelor între protocoale TEXT și BINARY
- Capturarea și analiza traficului TCP cu tshark
- Înțelegerea encapsulării L2/L3/L4

Topologie:
    h1 (10.0.0.1) ---- s1 (switch) ---- h2 (10.0.0.2)
       [client]                           [server]

Utilizare:
    sudo python3 scenario_tcp_demo.py

Cerințe:
    - Mininet instalat
    - Fișierele Python din ../python/apps/ accesibile
    - Drepturi de root (sudo)

Autor: Revolvix&Hypotheticalandrei
Săptămâna 4 - Protocoale TEXT și BINARY
"""

from mininet.net import Mininet
from mininet.node import Controller, OVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink
import time
import os
import sys

# Calea către aplicațiile Python
APPS_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'python', 'apps'))


def create_topology():
    """
    Creează topologia de rețea cu 2 hosturi pentru client-server.
    """
    info('*** Creare topologie pentru demo TCP ***\n')
    
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
    # h1 = client, h2 = server
    h1 = net.addHost('h1', ip='10.0.0.1/24')
    h2 = net.addHost('h2', ip='10.0.0.2/24')
    
    info('*** Creare legături ***\n')
    # Legături cu delay pentru observare mai clară a handshake-ului TCP
    net.addLink(h1, s1, bw=100, delay='2ms')
    net.addLink(h2, s1, bw=100, delay='2ms')
    
    return net


def setup_python_path(net):
    """
    Configurează PYTHONPATH pe toate hosturile.
    """
    for host in net.hosts:
        host.cmd(f'export PYTHONPATH={APPS_PATH}:$PYTHONPATH')


def run_text_protocol_demo(net):
    """
    Demonstrație protocol TEXT peste TCP.
    """
    h1, h2 = net.get('h1', 'h2')
    
    print("\n" + "="*70)
    print("DEMO 1: Protocol TEXT peste TCP (Port 5400)")
    print("="*70)
    
    print("""
Protocol TEXT:
- Format mesaj: "<LUNGIME> <PAYLOAD>"
- Delimitare: spațiu între lungime și date
- Codificare: UTF-8
- Avantaje: lizibil, ușor de debugat
- Dezavantaje: overhead mai mare, parsare mai lentă
""")
    
    # Pasul 1: Pornim captura pe server
    print("\n[PASUL 1] Pornire captură tshark pe serverul h2")
    print("-" * 50)
    capture_file = '/tmp/text_proto_capture.pcap'
    h2.cmd(f'tshark -i h2-eth0 -w {capture_file} -f "tcp port 5400" &')
    time.sleep(1)
    
    # Pasul 2: Pornim serverul TEXT pe h2
    print("\n[PASUL 2] Pornire server TEXT pe h2:5400")
    print("-" * 50)
    server_cmd = f'cd {APPS_PATH} && python3 text_proto_server.py --host 0.0.0.0 --port 5400 &'
    h2.cmd(server_cmd)
    print(f"Comandă: python3 text_proto_server.py --host 0.0.0.0 --port 5400")
    time.sleep(2)
    
    # Pasul 3: Clientul trimite mesaje
    print("\n[PASUL 3] Client h1 trimite mesaje către server")
    print("-" * 50)
    
    messages = [
        "Salut de la Mininet!",
        "Protocol TEXT simplu",
        "Mesaj cu caractere: ăîșțâ"
    ]
    
    for msg in messages:
        client_cmd = f'cd {APPS_PATH} && python3 text_proto_client.py --host 10.0.0.2 --port 5400 --message "{msg}"'
        result = h1.cmd(client_cmd)
        print(f"  Trimis: '{msg}'")
        print(f"  Răspuns: {result.strip()}")
        time.sleep(0.5)
    
    # Pasul 4: Oprim serverul și captura
    print("\n[PASUL 4] Oprire server și captură")
    print("-" * 50)
    h2.cmd('pkill -f text_proto_server')
    h2.cmd('pkill tshark')
    time.sleep(1)
    
    # Pasul 5: Analizăm captura
    print("\n[PASUL 5] Analiza traficului capturat")
    print("-" * 50)
    
    if os.path.exists(capture_file):
        # Afișăm sumar
        print("Sumar conversație TCP:")
        h2.cmd(f'tshark -r {capture_file} -q -z conv,tcp 2>/dev/null')
        
        # Afișăm payload-ul (follow TCP stream)
        print("\nPayload TEXT (primele 500 bytes):")
        analysis = h2.cmd(f'tshark -r {capture_file} -Y "tcp.payload" -T fields -e tcp.payload 2>/dev/null | head -10')
        print(analysis)
        
        # Statistici
        print("\nStatistici pachete:")
        stats = h2.cmd(f'tshark -r {capture_file} -q -z io,stat,0 2>/dev/null')
        print(stats)


def run_binary_protocol_demo(net):
    """
    Demonstrație protocol BINARY peste TCP.
    """
    h1, h2 = net.get('h1', 'h2')
    
    print("\n" + "="*70)
    print("DEMO 2: Protocol BINARY peste TCP (Port 5401)")
    print("="*70)
    
    print("""
Protocol BINARY:
- Header fix: 14 bytes (magic, version, type, length, seq, crc32)
- Codificare: struct.pack() big-endian (network byte order)
- Avantaje: compact, eficient, validare CRC
- Dezavantaje: greu de citit fără parser

Structura header (14 bytes):
  [0:2]   Magic: "NP" (0x4E50)
  [2]     Version: 1
  [3]     Type: 0x01=DATA, 0x02=ACK, 0xFF=ERROR
  [4:6]   Payload length (uint16 BE)
  [6:10]  Sequence number (uint32 BE)
  [10:14] CRC32 (uint32 BE)
""")
    
    # Pasul 1: Pornim captura
    print("\n[PASUL 1] Pornire captură tshark pe serverul h2")
    print("-" * 50)
    capture_file = '/tmp/binary_proto_capture.pcap'
    h2.cmd(f'tshark -i h2-eth0 -w {capture_file} -f "tcp port 5401" &')
    time.sleep(1)
    
    # Pasul 2: Pornim serverul BINARY pe h2
    print("\n[PASUL 2] Pornire server BINARY pe h2:5401")
    print("-" * 50)
    server_cmd = f'cd {APPS_PATH} && python3 binary_proto_server.py --host 0.0.0.0 --port 5401 &'
    h2.cmd(server_cmd)
    print(f"Comandă: python3 binary_proto_server.py --host 0.0.0.0 --port 5401")
    time.sleep(2)
    
    # Pasul 3: Clientul trimite mesaje
    print("\n[PASUL 3] Client h1 trimite mesaje binare către server")
    print("-" * 50)
    
    messages = [
        "Binary payload 1",
        "Efficient transport",
        "CRC32 validated"
    ]
    
    for i, msg in enumerate(messages):
        client_cmd = f'cd {APPS_PATH} && python3 binary_proto_client.py --host 10.0.0.2 --port 5401 --message "{msg}"'
        result = h1.cmd(client_cmd)
        print(f"  Trimis (seq={i}): '{msg}'")
        print(f"  Răspuns: {result.strip()[:100]}...")
        time.sleep(0.5)
    
    # Pasul 4: Oprim serverul și captura
    print("\n[PASUL 4] Oprire server și captură")
    print("-" * 50)
    h2.cmd('pkill -f binary_proto_server')
    h2.cmd('pkill tshark')
    time.sleep(1)
    
    # Pasul 5: Analizăm captura
    print("\n[PASUL 5] Analiza header-elor binare")
    print("-" * 50)
    
    if os.path.exists(capture_file):
        # Afișăm bytes hex
        print("Primele pachete în format hex:")
        hex_dump = h2.cmd(f'tshark -r {capture_file} -x 2>/dev/null | head -50')
        print(hex_dump)
        
        # Comparație cu TEXT
        print("\nObservații:")
        print("- Header-ul binar este compact (14 bytes fix)")
        print("- Magic bytes '4E 50' (NP) identifică protocolul")
        print("- Lungimea este codificată în 2 bytes (max 65535)")
        print("- CRC32 permite validarea integrității")


def compare_protocols(net):
    """
    Comparație directă între cele două protocoale.
    """
    print("\n" + "="*70)
    print("COMPARAȚIE: TEXT vs BINARY")
    print("="*70)
    
    print("""
┌─────────────────┬──────────────────────┬──────────────────────┐
│ Criteriu        │ Protocol TEXT        │ Protocol BINARY      │
├─────────────────┼──────────────────────┼──────────────────────┤
│ Format          │ "<len> <payload>"    │ Header 14B + payload │
│ Overhead        │ Variabil (cifre len) │ Fix 14 bytes         │
│ Citibilitate    │ Da (ASCII/UTF-8)     │ Nu (necesită parser) │
│ Validare        │ Nu (doar lungime)    │ Da (CRC32)           │
│ Parsing         │ String split/find    │ struct.unpack()      │
│ Byte order      │ N/A (text)           │ Big-endian (network) │
│ Extensibilitate │ Dificilă             │ Ușoară (type field)  │
│ Debugging       │ Ușor (telnet/nc)     │ Necesită tool        │
│ Performanță     │ Moderată             │ Înaltă               │
└─────────────────┴──────────────────────┴──────────────────────┘

Când folosim fiecare:
- TEXT: API-uri simple, debugging, interoperabilitate
- BINARY: Transfer mare de date, IoT, protocoale critice
""")


def interactive_mode(net):
    """
    Instrucțiuni pentru modul interactiv.
    """
    print("\n" + "="*70)
    print("MOD INTERACTIV - Comenzi pentru experimentare")
    print("="*70)
    print(f"""
Calea aplicațiilor: {APPS_PATH}

Comenzi pentru server TEXT:
  h2 cd {APPS_PATH} && python3 text_proto_server.py --port 5400 &
  h1 cd {APPS_PATH} && python3 text_proto_client.py --host 10.0.0.2 --port 5400 --message "Test"

Comenzi pentru server BINARY:
  h2 cd {APPS_PATH} && python3 binary_proto_server.py --port 5401 &
  h1 cd {APPS_PATH} && python3 binary_proto_client.py --host 10.0.0.2 --port 5401 --message "Test"

Captură și analiză:
  h2 tshark -i h2-eth0 -f "tcp port 5400" -w /tmp/capture.pcap &
  h2 tshark -r /tmp/capture.pcap -V
  h2 tshark -r /tmp/capture.pcap -x  # Hex dump

Test cu netcat (doar TEXT):
  h2 nc -l 5400
  h1 echo "5 hello" | nc 10.0.0.2 5400

Verificare conexiuni:
  h2 ss -tlnp                        # Porturi în ascultare
  h2 netstat -an | grep ESTABLISHED  # Conexiuni active

Oprire procese:
  h2 pkill -f proto_server
  
exit - Ieșire din CLI
""")


def main():
    """
    Punctul de intrare principal.
    """
    setLogLevel('info')
    
    print("\n" + "="*70)
    print("SCENARIUL 2: Protocoale TEXT și BINARY peste TCP")
    print("Săptămâna 4 - Implementare protocoale custom")
    print("="*70)
    
    # Verificăm existența fișierelor Python
    if not os.path.exists(APPS_PATH):
        print(f"\n[EROARE] Nu s-a găsit directorul: {APPS_PATH}")
        print("Asigurați-vă că rulați din directorul mininet/ al kit-ului.")
        sys.exit(1)
    
    required_files = [
        'text_proto_server.py',
        'text_proto_client.py',
        'binary_proto_server.py',
        'binary_proto_client.py'
    ]
    
    for f in required_files:
        if not os.path.exists(os.path.join(APPS_PATH, f)):
            print(f"\n[EROARE] Lipsește fișierul: {f}")
            sys.exit(1)
    
    net = create_topology()
    
    try:
        info('*** Pornire rețea ***\n')
        net.start()
        
        # Configurăm Python path
        setup_python_path(net)
        
        # Așteptăm stabilizarea
        time.sleep(2)
        
        # Demonstrații
        run_text_protocol_demo(net)
        run_binary_protocol_demo(net)
        compare_protocols(net)
        
        # Mod interactiv
        interactive_mode(net)
        
        info('*** Intrare în CLI Mininet ***\n')
        CLI(net)
        
    finally:
        info('*** Oprire rețea ***\n')
        
        # Curățare procese
        for host in net.hosts:
            host.cmd('pkill -f proto_server')
            host.cmd('pkill -f proto_client')
            host.cmd('pkill tshark')
        
        net.stop()
        
        # Curățare fișiere
        for f in ['/tmp/text_proto_capture.pcap', '/tmp/binary_proto_capture.pcap']:
            if os.path.exists(f):
                os.remove(f)


if __name__ == '__main__':
    main()
