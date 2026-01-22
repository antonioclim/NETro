#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Topologie Mininet - Rețea IoT Segmentată cu Firewall
====================================================

Săptămâna 13 - IoT și Securitate în Rețele de Calculatoare
Academia de Studii Economice - CSIE

Descriere:
    Implementează "Defense in Depth" prin segmentare de rețea:
    - Zona IoT (10.0.1.0/24) - Senzori cu acces limitat
    - Zona Management (10.0.2.0/24) - Broker MQTT și Controller
    - Zona DMZ (10.0.3.0/24) - Gateway extern (opțional)
    - Router central cu reguli iptables ca firewall

Topologie:
    
    ┌─────────────────┐
    │   ZONA IoT      │
    │  10.0.1.0/24    │
    │ ┌─────┐ ┌─────┐ │
    │ │ s1  │ │ s2  │ │
    │ │.11  │ │.12  │ │
    │ └──┬──┘ └──┬──┘ │
    │    └───┬───┘    │
    └────────┼────────┘
             │ eth0 (.1)
    ┌────────┴────────┐
    │     ROUTER      │
    │  r1 (Firewall)  │
    │   + iptables    │
    └────────┬────────┘
             │ eth1 (.1)
    ┌────────┼────────┐
    │   ZONA MGMT     │
    │  10.0.2.0/24    │
    │ ┌─────┐ ┌─────┐ │
    │ │broker │ctrl │ │
    │ │.100 │ │.20  │ │
    │ └─────┘ └─────┘ │
    └─────────────────┘

Reguli Firewall (iptables):
    - IoT → MGMT: DOAR porturi 1883, 8883 (MQTT)
    - MGMT → IoT: PERMITE (management complet)
    - Inter-IoT: BLOCAT (izolare senzori)
    - Logging pentru trafic suspect

Utilizare:
    sudo python3 topo_segmented.py
    sudo python3 topo_segmented.py --scenario isolation
    sudo python3 topo_segmented.py --show-rules

Autor: Colectiv Didactic ASE-CSIE
Data: 2025
"""

import sys
import argparse
import time

# Verificare Mininet
try:
    from mininet.net import Mininet
    from mininet.node import Controller, OVSSwitch, Host, Node
    from mininet.cli import CLI
    from mininet.log import setLogLevel, info, error
    from mininet.link import TCLink
    from mininet.topo import Topo
    MININET_DISPONIBIL = True
except ImportError:
    MININET_DISPONIBIL = False
    print("[!] Mininet nu este instalat.")


# ============================================================================
# ROUTER LINUX CU IP FORWARDING
# ============================================================================

class LinuxRouter(Node):
    """
    Router Linux cu IP forwarding activat.
    
    Folosit ca punct de segmentare și firewall între zone.
    Implementează iptables pentru control trafic.
    """
    
    def config(self, **params):
        super().config(**params)
        # Activare IP forwarding
        self.cmd('sysctl -w net.ipv4.ip_forward=1')
    
    def terminate(self):
        # Dezactivare IP forwarding la cleanup
        self.cmd('sysctl -w net.ipv4.ip_forward=0')
        super().terminate()


# ============================================================================
# TOPOLOGIE SEGMENTATĂ
# ============================================================================

class IoTSegmentedTopo(Topo):
    """
    Topologie segmentată cu zone separate și router/firewall.
    
    Zone:
        - IoT Zone (10.0.1.0/24): Senzori cu privilegii minime
        - Management Zone (10.0.2.0/24): Broker și Controller
        - DMZ (opțional, 10.0.3.0/24): Expunere externă controlată
    
    Principiul "Least Privilege":
        - Senzorii pot doar comunica cu broker-ul pe porturi specifice
        - Nu pot comunica între ei (prevent lateral movement)
        - Management zone are control complet
    """
    
    def build(self, **kwargs):
        """Construiește topologia segmentată."""
        info("*** Construire topologie IoT Segmentată\n")
        
        # ===================================================================
        # ROUTER CENTRAL (Firewall)
        # ===================================================================
        
        router = self.addNode(
            'r1',
            cls=LinuxRouter,
            ip='10.0.1.1/24'  # IP pe interfața către IoT
        )
        info(f"    Router adăugat: r1 (gateway/firewall)\n")
        
        # ===================================================================
        # SWITCH-URI PER ZONĂ
        # ===================================================================
        
        # Switch pentru zona IoT
        s_iot = self.addSwitch('s_iot', cls=OVSSwitch, failMode='standalone')
        info(f"    Switch IoT adăugat: s_iot\n")
        
        # Switch pentru zona Management
        s_mgmt = self.addSwitch('s_mgmt', cls=OVSSwitch, failMode='standalone')
        info(f"    Switch Management adăugat: s_mgmt\n")
        
        # ===================================================================
        # CONECTARE ROUTER LA SWITCH-URI
        # ===================================================================
        
        # Router eth0 -> Switch IoT (10.0.1.1)
        self.addLink(
            router, s_iot,
            intfName1='r1-eth0',
            params1={'ip': '10.0.1.1/24'}
        )
        
        # Router eth1 -> Switch Management (10.0.2.1)
        self.addLink(
            router, s_mgmt,
            intfName1='r1-eth1',
            params1={'ip': '10.0.2.1/24'}
        )
        
        # ===================================================================
        # ZONA IoT - SENZORI
        # ===================================================================
        
        # Sensor 1
        sensor1 = self.addHost(
            'sensor1',
            ip='10.0.1.11/24',
            defaultRoute='via 10.0.1.1'  # Gateway = router
        )
        self.addLink(sensor1, s_iot, cls=TCLink, bw=100, delay='5ms')
        info(f"    [IoT] sensor1: 10.0.1.11\n")
        
        # Sensor 2
        sensor2 = self.addHost(
            'sensor2',
            ip='10.0.1.12/24',
            defaultRoute='via 10.0.1.1'
        )
        self.addLink(sensor2, s_iot, cls=TCLink, bw=100, delay='5ms')
        info(f"    [IoT] sensor2: 10.0.1.12\n")
        
        # Sensor 3 (opțional - dispozitiv compromis pentru demo)
        sensor3 = self.addHost(
            'sensor3',
            ip='10.0.1.13/24',
            defaultRoute='via 10.0.1.1'
        )
        self.addLink(sensor3, s_iot, cls=TCLink, bw=100, delay='5ms')
        info(f"    [IoT] sensor3: 10.0.1.13 (pentru demo atacuri)\n")
        
        # ===================================================================
        # ZONA MANAGEMENT
        # ===================================================================
        
        # MQTT Broker
        broker = self.addHost(
            'broker',
            ip='10.0.2.100/24',
            defaultRoute='via 10.0.2.1'
        )
        self.addLink(broker, s_mgmt, cls=TCLink, bw=1000, delay='1ms')
        info(f"    [MGMT] broker: 10.0.2.100\n")
        
        # Controller / Dashboard
        controller = self.addHost(
            'ctrl',
            ip='10.0.2.20/24',
            defaultRoute='via 10.0.2.1'
        )
        self.addLink(controller, s_mgmt, cls=TCLink, bw=100, delay='2ms')
        info(f"    [MGMT] ctrl: 10.0.2.20\n")
        
        # Admin workstation
        admin = self.addHost(
            'admin',
            ip='10.0.2.10/24',
            defaultRoute='via 10.0.2.1'
        )
        self.addLink(admin, s_mgmt, cls=TCLink, bw=100, delay='2ms')
        info(f"    [MGMT] admin: 10.0.2.10\n")


# ============================================================================
# CONFIGURARE FIREWALL (IPTABLES)
# ============================================================================

def configure_firewall(router, strict: bool = True):
    """
    Configurează reguli iptables pe router.
    
    Args:
        router: Obiect Mininet Node (router)
        strict: True = reguli stricte, False = permisiv pentru debug
    
    Reguli implementate:
        1. Default policy: DROP (deny all)
        2. Permite established/related (stateful)
        3. IoT → MGMT: doar MQTT (1883, 8883)
        4. MGMT → IoT: permit all (management)
        5. IoT ↔ IoT: DROP (izolare laterală)
        6. Log trafic blocat
    """
    info("\n*** Configurare Firewall (iptables)\n")
    
    # Reset reguli existente
    router.cmd('iptables -F')
    router.cmd('iptables -X')
    router.cmd('iptables -t nat -F')
    
    if not strict:
        # Mod permisiv pentru debugging
        info("    [!] Mod PERMISIV activat (doar logging)\n")
        router.cmd('iptables -P FORWARD ACCEPT')
        router.cmd('iptables -A FORWARD -j LOG --log-prefix "[FW-DEBUG] "')
        return
    
    # =========================================================================
    # POLITICI DEFAULT - DROP
    # =========================================================================
    
    router.cmd('iptables -P INPUT DROP')
    router.cmd('iptables -P FORWARD DROP')
    router.cmd('iptables -P OUTPUT ACCEPT')
    info("    Politici default: INPUT=DROP, FORWARD=DROP, OUTPUT=ACCEPT\n")
    
    # =========================================================================
    # LOOPBACK
    # =========================================================================
    
    router.cmd('iptables -A INPUT -i lo -j ACCEPT')
    router.cmd('iptables -A OUTPUT -o lo -j ACCEPT')
    
    # =========================================================================
    # STATEFUL - ESTABLISHED/RELATED
    # =========================================================================
    
    router.cmd('iptables -A FORWARD -m state --state ESTABLISHED,RELATED -j ACCEPT')
    router.cmd('iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT')
    info("    Stateful: ESTABLISHED/RELATED permis\n")
    
    # =========================================================================
    # REGULI ICMP (ping pentru diagnostic)
    # =========================================================================
    
    router.cmd('iptables -A FORWARD -p icmp --icmp-type echo-request -j ACCEPT')
    router.cmd('iptables -A FORWARD -p icmp --icmp-type echo-reply -j ACCEPT')
    router.cmd('iptables -A INPUT -p icmp --icmp-type echo-request -j ACCEPT')
    info("    ICMP: ping permis (diagnostic)\n")
    
    # =========================================================================
    # IoT → MANAGEMENT: DOAR MQTT
    # =========================================================================
    
    # Subnet IoT: 10.0.1.0/24
    # Subnet MGMT: 10.0.2.0/24
    
    # MQTT plain (port 1883)
    router.cmd('iptables -A FORWARD -s 10.0.1.0/24 -d 10.0.2.0/24 -p tcp --dport 1883 -j ACCEPT')
    
    # MQTT TLS (port 8883)
    router.cmd('iptables -A FORWARD -s 10.0.1.0/24 -d 10.0.2.0/24 -p tcp --dport 8883 -j ACCEPT')
    
    # DNS (pentru rezolvare nume, opțional)
    router.cmd('iptables -A FORWARD -s 10.0.1.0/24 -d 10.0.2.0/24 -p udp --dport 53 -j ACCEPT')
    
    info("    IoT → MGMT: PERMIT tcp/1883,8883 (MQTT), udp/53 (DNS)\n")
    
    # =========================================================================
    # MANAGEMENT → IoT: PERMIT ALL (pentru management)
    # =========================================================================
    
    router.cmd('iptables -A FORWARD -s 10.0.2.0/24 -d 10.0.1.0/24 -j ACCEPT')
    info("    MGMT → IoT: PERMIT ALL (management)\n")
    
    # =========================================================================
    # IoT ↔ IoT: DROP (izolare laterală)
    # =========================================================================
    
    # Această regulă nu e necesară explicit deoarece traficul intra-subnet
    # nu trece prin router. Dar o adăugăm pentru claritate și logging.
    router.cmd('iptables -A FORWARD -s 10.0.1.0/24 -d 10.0.1.0/24 -j DROP')
    info("    IoT ↔ IoT: DROP (izolare - dar traficul nu trece prin router)\n")
    
    # =========================================================================
    # LOGGING TRAFIC BLOCAT
    # =========================================================================
    
    router.cmd('iptables -A FORWARD -j LOG --log-prefix "[FW-BLOCKED] " --log-level 4')
    info("    Logging: Trafic blocat înregistrat cu prefix [FW-BLOCKED]\n")
    
    # =========================================================================
    # AFIȘARE REGULI
    # =========================================================================
    
    info("\n*** Reguli iptables active:\n")
    result = router.cmd('iptables -L -v -n --line-numbers')
    for line in result.split('\n')[:20]:  # Primele 20 linii
        info(f"    {line}\n")


def show_firewall_rules(router):
    """Afișează regulile iptables curente."""
    info("\n*** Reguli iptables pe router:\n")
    info("\n--- FILTER table ---\n")
    print(router.cmd('iptables -L -v -n --line-numbers'))
    info("\n--- NAT table ---\n")
    print(router.cmd('iptables -t nat -L -v -n'))


# ============================================================================
# SCENARII
# ============================================================================

def scenario_isolation_test(net):
    """
    Testează izolarea între zone.
    
    Verifică:
        1. Senzor poate comunica cu broker (MQTT)
        2. Senzor NU poate comunica cu alte porturi
        3. Admin poate accesa tot
    """
    info("\n" + "="*60 + "\n")
    info("  SCENARIU: Test Izolare Zone\n")
    info("="*60 + "\n\n")
    
    sensor1 = net.get('sensor1')
    sensor2 = net.get('sensor2')
    broker = net.get('broker')
    admin = net.get('admin')
    
    # Test 1: Ping cross-zone
    info("1. Test ping sensor1 → broker:\n")
    result = sensor1.cmd('ping -c 2 10.0.2.100')
    print(f"   {result}")
    
    # Test 2: Conexiune MQTT (ar trebui să funcționeze)
    info("2. Test conexiune MQTT (port 1883):\n")
    result = sensor1.cmd('nc -zv 10.0.2.100 1883 2>&1')
    print(f"   {result}")
    
    # Test 3: Conexiune SSH (ar trebui blocată)
    info("3. Test conexiune SSH (port 22) - ar trebui BLOCATĂ:\n")
    result = sensor1.cmd('nc -zv -w 2 10.0.2.100 22 2>&1')
    print(f"   {result}")
    
    # Test 4: Admin poate accesa sensor (management)
    info("4. Test admin → sensor1 (ar trebui să funcționeze):\n")
    result = admin.cmd('ping -c 2 10.0.1.11')
    print(f"   {result}")
    
    # Test 5: Verificare log firewall
    info("5. Log-uri firewall (ultimele intrări blocate):\n")
    router = net.get('r1')
    result = router.cmd('dmesg | grep FW-BLOCKED | tail -5')
    print(f"   {result if result else '   (niciun trafic blocat încă)'}")
    
    info("\n[✓] Test izolare complet!\n")


def scenario_lateral_movement(net):
    """
    Demonstrează prevenirea lateral movement.
    
    Simulează un sensor compromis care încearcă să atace alt sensor.
    """
    info("\n" + "="*60 + "\n")
    info("  SCENARIU: Prevenire Lateral Movement\n")
    info("="*60 + "\n\n")
    
    sensor3 = net.get('sensor3')  # "Compromis"
    sensor1 = net.get('sensor1')  # Țintă
    
    info("Premisă: sensor3 a fost compromis și încearcă să atace sensor1\n\n")
    
    # Scanare porturi
    info("1. Atacator (sensor3) încearcă scanare porturi pe sensor1:\n")
    result = sensor3.cmd('nc -zv -w 1 10.0.1.11 22 80 443 2>&1')
    print(f"   {result}")
    
    # Ping
    info("2. Atacator încearcă ping:\n")
    result = sensor3.cmd('ping -c 1 -W 1 10.0.1.11')
    print(f"   {result}")
    
    info("""
NOTĂ: Traficul între senzori (10.0.1.x ↔ 10.0.1.y) NU trece prin router!
      Ei sunt pe același switch (s_iot), deci comunicarea directă e posibilă.
      
Pentru izolare completă intra-zonă, aveți opțiuni:
  a) Switch-uri separate per senzor
  b) VLANs cu ACLs pe switch
  c) Microsegmentare cu SDN controller
  d) Host-based firewall pe fiecare senzor

În producție, izolarea Layer 2 necesită configurare suplimentară!
""")


def scenario_attack_blocked(net):
    """
    Demonstrează blocarea unui atac din zona IoT.
    """
    info("\n" + "="*60 + "\n")
    info("  SCENARIU: Atac Blocat de Firewall\n")
    info("="*60 + "\n\n")
    
    sensor3 = net.get('sensor3')
    ctrl = net.get('ctrl')
    router = net.get('r1')
    
    info("Senzor compromis încearcă să acceseze servicii din zona MGMT\n\n")
    
    # Încercare SSH
    info("1. Încercare SSH către controller (10.0.2.20):\n")
    result = sensor3.cmd('timeout 2 nc -zv 10.0.2.20 22 2>&1')
    print(f"   Rezultat: {result if result else 'Timeout/Blocat'}")
    
    # Încercare HTTP
    info("2. Încercare HTTP către controller:\n")
    result = sensor3.cmd('timeout 2 nc -zv 10.0.2.20 80 2>&1')
    print(f"   Rezultat: {result if result else 'Timeout/Blocat'}")
    
    # Verificare log
    info("3. Verificare log firewall:\n")
    time.sleep(1)
    result = router.cmd('dmesg | grep FW-BLOCKED | tail -5')
    print(f"   {result if result else '   (verificați cu: dmesg | grep FW)'}")
    
    # MQTT ar trebui să funcționeze
    info("4. DAR MQTT funcționează (port 1883):\n")
    result = sensor3.cmd('nc -zv 10.0.2.100 1883 2>&1')
    print(f"   {result}")
    
    info("""
[✓] Firewall-ul a blocat accesul la servicii neautorizate!
    Senzorul compromis poate doar să comunice prin MQTT.
    
    Chiar dacă atacatorul are acces la un senzor, daunele sunt limitate.
    Aceasta este esența "Defense in Depth"!
""")


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Punct de intrare principal."""
    
    if not MININET_DISPONIBIL:
        print("[!] Mininet nu este disponibil.")
        sys.exit(1)
    
    parser = argparse.ArgumentParser(
        description="Topologie Mininet - Rețea IoT Segmentată cu Firewall"
    )
    
    parser.add_argument(
        '--no-cli',
        action='store_true',
        help='Nu deschide CLI Mininet'
    )
    
    parser.add_argument(
        '--permissive',
        action='store_true',
        help='Firewall în mod permisiv (doar logging)'
    )
    
    parser.add_argument(
        '--scenario',
        choices=['isolation', 'lateral', 'attack'],
        help='Rulează un scenariu predefinit'
    )
    
    parser.add_argument(
        '--show-rules',
        action='store_true',
        help='Afișează regulile firewall și ieși'
    )
    
    args = parser.parse_args()
    
    setLogLevel('info')
    
    info("\n" + "="*60 + "\n")
    info("  Mininet IoT Segmented Topology - Săptămâna 13\n")
    info("  Defense in Depth cu Firewall\n")
    info("="*60 + "\n\n")
    
    # Creare topologie
    topo = IoTSegmentedTopo()
    
    # Creare rețea
    net = Mininet(
        topo=topo,
        controller=Controller,
        switch=OVSSwitch,
        link=TCLink
    )
    
    try:
        info("*** Pornire rețea...\n")
        net.start()
        
        # Obține router
        router = net.get('r1')
        
        # Configurare firewall
        configure_firewall(router, strict=not args.permissive)
        
        # Afișare reguli și ieșire
        if args.show_rules:
            show_firewall_rules(router)
            return
        
        # Test conectivitate de bază
        info("\n*** Test conectivitate de bază:\n")
        sensor1 = net.get('sensor1')
        broker = net.get('broker')
        info(f"    sensor1 ping broker: ")
        result = sensor1.cmd('ping -c 1 10.0.2.100')
        info("OK\n" if "1 received" in result else "FAIL\n")
        
        # Rulare scenariu
        if args.scenario == 'isolation':
            scenario_isolation_test(net)
        elif args.scenario == 'lateral':
            scenario_lateral_movement(net)
        elif args.scenario == 'attack':
            scenario_attack_blocked(net)
        
        # CLI interactiv
        if not args.no_cli and not args.scenario:
            info("\n*** Comenzi utile:\n")
            info("    sensor1 ping broker  # test cross-zone\n")
            info("    sensor1 nc -zv 10.0.2.100 1883  # test MQTT\n")
            info("    r1 iptables -L -v -n  # vezi reguli firewall\n")
            info("    r1 dmesg | grep FW  # vezi log blocare\n")
            info("    xterm sensor3  # terminal pentru test atacuri\n")
            CLI(net)
        
    finally:
        info("\n*** Oprire rețea...\n")
        net.stop()


if __name__ == "__main__":
    main()
