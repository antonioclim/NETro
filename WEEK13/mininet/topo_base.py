#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Topologie Mininet - Rețea IoT de Bază
=====================================

Săptămâna 13 - IoT și Securitate în Rețele de Calculatoare
Academia de Studii Economice - CSIE

Descriere:
    Simulează o rețea IoT simplă cu:
    - 2 senzori (publishers MQTT)
    - 1 broker MQTT (Mosquitto)
    - 1 controller (subscriber MQTT)
    - 1 atacator (pentru demonstrații pentest)

Topologie:
                    ┌─────────────┐
                    │   Switch    │
                    │    (s1)     │
                    └──────┬──────┘
           ┌───────────┬───┴───┬───────────┐
           │           │       │           │
    ┌──────┴──────┐ ┌──┴──┐ ┌──┴──┐ ┌──────┴──────┐
    │  sensor1    │ │broker│ │ctrl │ │  attacker   │
    │ 10.0.0.11   │ │.100  │ │ .20 │ │  10.0.0.50  │
    └─────────────┘ └─────┘ └─────┘ └─────────────┘
    
    sensor2: 10.0.0.12

Utilizare:
    sudo python3 topo_base.py [--cli]
    
    În CLI Mininet:
        mininet> sensor1 ping broker
        mininet> attacker python3 scanner.py 10.0.0.100
        mininet> xterm broker  # deschide terminal pentru broker

Autor: Colectiv Didactic ASE-CSIE
Data: 2025
"""

import sys
import argparse
import time

# Verificare disponibilitate Mininet
try:
    from mininet.net import Mininet
    from mininet.node import Controller, OVSSwitch, Host
    from mininet.cli import CLI
    from mininet.log import setLogLevel, info, error
    from mininet.link import TCLink
    from mininet.topo import Topo
    MININET_DISPONIBIL = True
except ImportError:
    MININET_DISPONIBIL = False
    print("[!] Mininet nu este instalat.")
    print("    Instalare: sudo apt-get install mininet")
    print("    Sau: pip install mininet --break-system-packages")


# ============================================================================
# DEFINIRE TOPOLOGIE
# ============================================================================

class IoTBaseTopo(Topo):
    """
    Topologie de bază pentru rețea IoT.
    
    Componente:
        - switch central (OpenFlow)
        - 2 senzori IoT
        - 1 broker MQTT
        - 1 controller
        - 1 atacator (opțional)
    
    Parametri rețea:
        - Subnet: 10.0.0.0/24
        - Gateway implicit: 10.0.0.1
        - Bandwidth link-uri: 100 Mbps
        - Delay: 2ms (simulare latență realistă)
    """
    
    def build(self, include_attacker: bool = True, **kwargs):
        """
        Construiește topologia.
        
        Args:
            include_attacker: Include host atacator pentru demonstrații
        """
        info("*** Construire topologie IoT Base\n")
        
        # ===================================================================
        # SWITCH CENTRAL
        # ===================================================================
        
        s1 = self.addSwitch('s1', cls=OVSSwitch, failMode='standalone')
        info(f"    Switch adăugat: s1\n")
        
        # ===================================================================
        # SENZORI IoT
        # ===================================================================
        
        # Sensor 1 - Living Room
        sensor1 = self.addHost(
            'sensor1',
            ip='10.0.0.11/24',
            defaultRoute='via 10.0.0.1'
        )
        self.addLink(
            sensor1, s1,
            cls=TCLink,
            bw=100,  # 100 Mbps
            delay='2ms'
        )
        info(f"    Sensor adăugat: sensor1 (10.0.0.11)\n")
        
        # Sensor 2 - Bedroom
        sensor2 = self.addHost(
            'sensor2',
            ip='10.0.0.12/24',
            defaultRoute='via 10.0.0.1'
        )
        self.addLink(
            sensor2, s1,
            cls=TCLink,
            bw=100,
            delay='2ms'
        )
        info(f"    Sensor adăugat: sensor2 (10.0.0.12)\n")
        
        # ===================================================================
        # BROKER MQTT
        # ===================================================================
        
        broker = self.addHost(
            'broker',
            ip='10.0.0.100/24',
            defaultRoute='via 10.0.0.1'
        )
        self.addLink(
            broker, s1,
            cls=TCLink,
            bw=1000,  # 1 Gbps - server principal
            delay='1ms'
        )
        info(f"    Broker adăugat: broker (10.0.0.100)\n")
        
        # ===================================================================
        # CONTROLLER
        # ===================================================================
        
        controller = self.addHost(
            'ctrl',
            ip='10.0.0.20/24',
            defaultRoute='via 10.0.0.1'
        )
        self.addLink(
            controller, s1,
            cls=TCLink,
            bw=100,
            delay='2ms'
        )
        info(f"    Controller adăugat: ctrl (10.0.0.20)\n")
        
        # ===================================================================
        # ATACATOR (pentru demonstrații)
        # ===================================================================
        
        if include_attacker:
            attacker = self.addHost(
                'attacker',
                ip='10.0.0.50/24',
                defaultRoute='via 10.0.0.1'
            )
            self.addLink(
                attacker, s1,
                cls=TCLink,
                bw=100,
                delay='2ms'
            )
            info(f"    Attacker adăugat: attacker (10.0.0.50)\n")


# ============================================================================
# FUNCȚII HELPER
# ============================================================================

def start_mosquitto(host, config_path: str = None):
    """
    Pornește Mosquitto broker pe un host.
    
    Args:
        host: Obiect Mininet Host
        config_path: Calea către fișierul de configurare (opțional)
    """
    config_arg = f"-c {config_path}" if config_path else ""
    cmd = f"mosquitto {config_arg} -v &"
    info(f"*** Pornire Mosquitto pe {host.name}: {cmd}\n")
    host.cmd(cmd)
    time.sleep(1)  # Așteaptă pornirea


def start_sensor_simulation(host, broker_ip: str, topic: str, interval: int = 5):
    """
    Pornește simulare sensor care publică date periodic.
    
    Args:
        host: Obiect Mininet Host
        broker_ip: IP-ul broker-ului MQTT
        topic: Topic-ul pe care publică
        interval: Interval între mesaje (secunde)
    """
    # Script Python inline pentru simulare sensor
    script = f'''
import time
import random
import paho.mqtt.client as mqtt

client = mqtt.Client()
client.connect("{broker_ip}", 1883)

while True:
    temp = round(20 + random.uniform(-5, 5), 1)
    humidity = round(50 + random.uniform(-10, 10), 1)
    client.publish("{topic}/temperature", temp)
    client.publish("{topic}/humidity", humidity)
    time.sleep({interval})
'''
    
    # Salvează script-ul și rulează-l
    script_path = f"/tmp/sensor_{host.name}.py"
    host.cmd(f"echo '{script}' > {script_path}")
    host.cmd(f"python3 {script_path} &")
    info(f"*** Sensor simulation started on {host.name}\n")


def run_test_connectivity(net):
    """
    Testează conectivitatea între toate host-urile.
    
    Args:
        net: Obiect Mininet Network
    """
    info("\n*** Test conectivitate (ping all)\n")
    net.pingAll()


def capture_traffic(host, interface: str = None, output_file: str = "/tmp/capture.pcap"):
    """
    Pornește captură de trafic pe un host.
    
    Args:
        host: Obiect Mininet Host
        interface: Interfața de captură (None = toate)
        output_file: Fișierul de output
    """
    iface_arg = f"-i {interface}" if interface else "-i any"
    cmd = f"tcpdump {iface_arg} -w {output_file} &"
    info(f"*** Captură trafic pe {host.name}: {cmd}\n")
    host.cmd(cmd)


# ============================================================================
# SCENARII PREDEFINITE
# ============================================================================

def scenario_basic_mqtt(net):
    """
    Scenariu: Comunicare MQTT de bază.
    
    1. Pornește broker
    2. Sensor1 publică date
    3. Controller subscrie și primește
    """
    info("\n" + "="*60 + "\n")
    info("  SCENARIU: Comunicare MQTT de Bază\n")
    info("="*60 + "\n\n")
    
    broker = net.get('broker')
    sensor1 = net.get('sensor1')
    ctrl = net.get('ctrl')
    
    # 1. Pornire broker
    info("1. Pornire broker Mosquitto...\n")
    broker.cmd("mosquitto -v &")
    time.sleep(2)
    
    # 2. Subscriber pe controller
    info("2. Controller subscrie la home/#...\n")
    ctrl.cmd("mosquitto_sub -h 10.0.0.100 -t 'home/#' -v > /tmp/mqtt_received.txt &")
    time.sleep(1)
    
    # 3. Sensor publică
    info("3. Sensor1 publică temperatură...\n")
    sensor1.cmd("mosquitto_pub -h 10.0.0.100 -t 'home/living/temp' -m '22.5'")
    sensor1.cmd("mosquitto_pub -h 10.0.0.100 -t 'home/living/humidity' -m '45'")
    time.sleep(1)
    
    # 4. Verificare
    info("4. Mesaje primite de controller:\n")
    result = ctrl.cmd("cat /tmp/mqtt_received.txt")
    print(result)
    
    info("\n[✓] Scenariu complet!\n")


def scenario_sniff_attack(net):
    """
    Scenariu: Atacator interceptează trafic MQTT.
    
    Demonstrează vulnerabilitatea comunicației necriptate.
    """
    info("\n" + "="*60 + "\n")
    info("  SCENARIU: Interceptare Trafic MQTT (Sniffing)\n")
    info("="*60 + "\n\n")
    
    attacker = net.get('attacker')
    broker = net.get('broker')
    sensor1 = net.get('sensor1')
    
    # 1. Atacatorul pornește tcpdump
    info("1. Atacator pornește captură trafic port 1883...\n")
    attacker.cmd("tcpdump -i attacker-eth0 port 1883 -A > /tmp/sniffed.txt &")
    time.sleep(1)
    
    # 2. Broker pornit
    broker.cmd("mosquitto -v &")
    time.sleep(2)
    
    # 3. Sensor publică date "sensibile"
    info("2. Sensor publică date (vizibile atacatorului!)...\n")
    sensor1.cmd("mosquitto_pub -h 10.0.0.100 -t 'home/alarm/code' -m 'PIN:1234'")
    sensor1.cmd("mosquitto_pub -h 10.0.0.100 -t 'home/alarm/status' -m 'DISARMED'")
    time.sleep(2)
    
    # 4. Afișare date capturate
    attacker.cmd("pkill tcpdump")
    info("3. Date interceptate de atacator:\n")
    result = attacker.cmd("grep -a 'PIN\\|DISARMED' /tmp/sniffed.txt")
    print(result if result else "    [folosiți Wireshark pe /tmp/capture.pcap pentru analiză completă]")
    
    info("\n[!] LECȚIE: Fără TLS, traficul MQTT poate fi citit de oricine în rețea!\n")


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Punct de intrare principal."""
    
    if not MININET_DISPONIBIL:
        print("[!] Mininet nu este disponibil. Instalați cu:")
        print("    sudo apt-get install mininet")
        sys.exit(1)
    
    parser = argparse.ArgumentParser(
        description="Topologie Mininet - Rețea IoT de Bază",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemple:
    sudo python3 topo_base.py              # Pornește și deschide CLI
    sudo python3 topo_base.py --no-cli     # Doar pornește rețeaua
    sudo python3 topo_base.py --scenario basic  # Rulează scenariu MQTT
    sudo python3 topo_base.py --scenario sniff  # Demonstrație sniffing
        """
    )
    
    parser.add_argument(
        '--no-cli',
        action='store_true',
        help='Nu deschide CLI Mininet'
    )
    
    parser.add_argument(
        '--no-attacker',
        action='store_true',
        help='Nu include host-ul atacator'
    )
    
    parser.add_argument(
        '--scenario',
        choices=['basic', 'sniff'],
        help='Rulează un scenariu predefinit'
    )
    
    parser.add_argument(
        '--test',
        action='store_true',
        help='Rulează test de conectivitate'
    )
    
    args = parser.parse_args()
    
    # Setare nivel logging
    setLogLevel('info')
    
    info("\n" + "="*60 + "\n")
    info("  Mininet IoT Base Topology - Săptămâna 13\n")
    info("="*60 + "\n\n")
    
    # Creare topologie
    topo = IoTBaseTopo(include_attacker=not args.no_attacker)
    
    # Creare rețea
    net = Mininet(
        topo=topo,
        controller=Controller,
        switch=OVSSwitch,
        link=TCLink,
        autoSetMacs=True
    )
    
    try:
        # Pornire rețea
        info("*** Pornire rețea...\n")
        net.start()
        
        # Test conectivitate
        if args.test:
            run_test_connectivity(net)
        
        # Rulare scenariu
        if args.scenario == 'basic':
            scenario_basic_mqtt(net)
        elif args.scenario == 'sniff':
            scenario_sniff_attack(net)
        
        # CLI interactiv
        if not args.no_cli and not args.scenario:
            info("\n*** Comenzi utile în CLI:\n")
            info("    sensor1 ping broker\n")
            info("    xterm broker  # terminal pentru broker\n")
            info("    broker mosquitto -v &  # pornește broker\n")
            info("    attacker tcpdump -i attacker-eth0 port 1883\n")
            info("    exit  # oprește Mininet\n\n")
            CLI(net)
        
    finally:
        # Cleanup
        info("\n*** Oprire rețea...\n")
        net.stop()


# ============================================================================
# ALTERNATIVĂ: Folosire ca modul
# ============================================================================

def create_network(include_attacker: bool = True) -> 'Mininet':
    """
    Creează și returnează rețeaua Mininet (pentru import din alt script).
    
    Args:
        include_attacker: Include host atacator
        
    Returns:
        Obiect Mininet Network (nepornit)
    """
    if not MININET_DISPONIBIL:
        raise ImportError("Mininet nu este instalat")
    
    topo = IoTBaseTopo(include_attacker=include_attacker)
    net = Mininet(
        topo=topo,
        controller=Controller,
        switch=OVSSwitch,
        link=TCLink
    )
    return net


if __name__ == "__main__":
    main()
