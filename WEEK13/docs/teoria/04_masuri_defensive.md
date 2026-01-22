# Măsuri Defensive în Securitatea Rețelelor IoT

## Cuprins

1. [Principii Fundamentale de Apărare](#1-principii-fundamentale-de-apărare)
2. [Segmentarea Rețelei](#2-segmentarea-rețelei)
3. [Criptografie și TLS](#3-criptografie-și-tls)
4. [Autentificare și Autorizare](#4-autentificare-și-autorizare)
5. [Monitorizare și Detecție](#5-monitorizare-și-detecție)
6. [Hardening și Best Practices](#6-hardening-și-best-practices)
7. [Incident Response](#7-incident-response)

---

## 1. Principii Fundamentale de Apărare

### 1.1 Defense in Depth (Apărare pe Multiple Niveluri)

Securitatea eficientă nu se bazează pe un singur mecanism, ci pe straturi suprapuse de protecție. Compromiterea unui nivel nu duce automat la compromiterea întregului sistem.

```
┌─────────────────────────────────────────────────────────────────┐
│                    DEFENSE IN DEPTH LAYERS                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │                    LAYER 7: APPLICATION                   │ │
│  │  Input validation, secure coding, WAF                     │ │
│  ├───────────────────────────────────────────────────────────┤ │
│  │                    LAYER 6: DATA                          │ │
│  │  Encryption at rest, access controls, DLP                 │ │
│  ├───────────────────────────────────────────────────────────┤ │
│  │                    LAYER 5: HOST                          │ │
│  │  Hardening, patching, AV/EDR, logging                     │ │
│  ├───────────────────────────────────────────────────────────┤ │
│  │                    LAYER 4: NETWORK                       │ │
│  │  Segmentation, firewall, IDS/IPS, VPN                     │ │
│  ├───────────────────────────────────────────────────────────┤ │
│  │                    LAYER 3: PERIMETER                     │ │
│  │  DMZ, edge firewall, WAF, DDoS protection                 │ │
│  ├───────────────────────────────────────────────────────────┤ │
│  │                    LAYER 2: PHYSICAL                      │ │
│  │  Physical access controls, surveillance                   │ │
│  ├───────────────────────────────────────────────────────────┤ │
│  │                    LAYER 1: POLICIES                      │ │
│  │  Security policies, awareness training, governance        │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 Principiul Privilegiului Minim (Least Privilege)

Fiecare entitate (utilizator, serviciu, dispozitiv) primește exact permisiunile necesare pentru funcționare, nimic mai mult.

**Aplicare în IoT:**
- Senzori: doar PUBLISH pe topicuri specifice
- Controller: SUBSCRIBE pe senzori, PUBLISH pe actuatoare
- Dashboard: READ-ONLY pe toate datele
- Admin: acces complet, dar auditat

```python
# Exemplu ACL MQTT (acl.acl)
# ─────────────────────────────

# Senzor: poate doar publica în zona sa
user sensor_living
topic write home/living/temperature
topic write home/living/humidity
# NU poate: citi comenzi, publica în alte zone

# Controller: citește senzori, scrie comenzi
user controller
topic read home/#
topic write commands/#
# NU poate: modifica configurații

# Admin: acces complet pentru management
user admin
topic readwrite #
```

### 1.3 Zero Trust Architecture

Paradigma "never trust, always verify" - nicio entitate nu este implicit de încredere, indiferent de poziția în rețea.

**Pilonii Zero Trust:**
1. **Verificare continuă**: Autentificare la fiecare request
2. **Segmentare micro**: Izolare la nivel de workload
3. **Acces contextual**: Decizie bazată pe identitate + device + locație + timp
4. **Audit complet**: Logging pentru orice interacțiune

---

## 2. Segmentarea Rețelei

### 2.1 Arhitecturi de Segmentare

**Modelul cu Zone de Securitate:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    NETWORK SEGMENTATION                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│                        ┌─────────────┐                         │
│                        │  INTERNET   │                         │
│                        └──────┬──────┘                         │
│                               │                                 │
│                        ┌──────▼──────┐                         │
│                        │   EDGE FW   │                         │
│                        └──────┬──────┘                         │
│                               │                                 │
│            ┌──────────────────┼──────────────────┐             │
│            │                  │                  │             │
│     ┌──────▼──────┐   ┌───────▼──────┐   ┌──────▼──────┐      │
│     │    DMZ      │   │   INTERNAL   │   │    IoT      │      │
│     │  10.1.0.0/24│   │  10.2.0.0/24 │   │ 10.3.0.0/24 │      │
│     ├─────────────┤   ├──────────────┤   ├─────────────┤      │
│     │ • Web server│   │ • Workstations│  │ • Sensors   │      │
│     │ • Reverse   │   │ • Management │   │ • Actuators │      │
│     │   proxy     │   │   console    │   │ • Broker    │      │
│     └─────────────┘   └──────────────┘   └─────────────┘      │
│                                                                 │
│     TRUST: LOW           TRUST: HIGH       TRUST: MINIMAL      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Implementare cu iptables

**Firewall pentru Zona IoT (din topo_segmented.py):**

```bash
#!/bin/bash
# Firewall pentru router între zone IoT și Management

# Politici default: DROP everything
iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT DROP

# Permitere conexiuni existente (stateful)
iptables -A FORWARD -m state --state ESTABLISHED,RELATED -j ACCEPT

# IoT → Management: DOAR MQTT (1883, 8883) și DNS (53)
iptables -A FORWARD -s 10.0.1.0/24 -d 10.0.2.0/24 \
    -p tcp --dport 1883 -j ACCEPT
iptables -A FORWARD -s 10.0.1.0/24 -d 10.0.2.0/24 \
    -p tcp --dport 8883 -j ACCEPT
iptables -A FORWARD -s 10.0.1.0/24 -d 10.0.2.0/24 \
    -p udp --dport 53 -j ACCEPT

# Management → IoT: Acces complet (pentru administrare)
iptables -A FORWARD -s 10.0.2.0/24 -d 10.0.1.0/24 -j ACCEPT

# IoT ↔ IoT: BLOCAT (previne lateral movement)
# Această regulă este implicită prin DROP default

# Logging pentru trafic blocat
iptables -A FORWARD -j LOG --log-prefix "[FW-BLOCKED] "
```

### 2.3 VLAN și Layer 2 Isolation

**Segmentare Layer 2 pentru izolare completă:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    VLAN ARCHITECTURE                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                     CORE SWITCH                          │   │
│  │                   (Layer 3 Routing)                      │   │
│  └───┬───────────────────┬───────────────────┬─────────────┘   │
│      │                   │                   │                  │
│   VLAN 10             VLAN 20             VLAN 30               │
│   IoT_Sensors         IoT_Control         Management            │
│      │                   │                   │                  │
│  ┌───▼───┐           ┌───▼───┐           ┌───▼───┐             │
│  │ Temp  │           │ MQTT  │           │ Admin │             │
│  │ Humid │           │Broker │           │Console│             │
│  │ Motion│           │Gateway│           │Monitor│             │
│  └───────┘           └───────┘           └───────┘             │
│                                                                 │
│  Inter-VLAN ACL:                                               │
│  • VLAN 10 → VLAN 20: permit tcp 1883,8883                     │
│  • VLAN 20 → VLAN 10: deny all (sensors don't accept)          │
│  • VLAN 30 → ALL: permit all (admin access)                    │
│  • VLAN 10 ↔ VLAN 10: deny (no lateral)                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Criptografie și TLS

### 3.1 TLS pentru MQTT

Configurarea TLS elimină riscul interceptării traficului în plaintext.

**Configurație Mosquitto securizată (tls.conf):**

```ini
# ====================================
# Mosquitto TLS Configuration
# ====================================

# Listener TLS-only (disable plaintext!)
listener 8883

# Certificate paths
cafile /etc/mosquitto/certs/ca.crt
certfile /etc/mosquitto/certs/server.crt
keyfile /etc/mosquitto/certs/server.key

# TLS Protocol settings
tls_version tlsv1.2   # Minimum TLS 1.2
ciphers ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-GCM-SHA256

# Client authentication (mutual TLS)
require_certificate true
use_identity_as_username true
```

### 3.2 Generarea Certificatelor

**Script pentru PKI completă:**

```bash
#!/bin/bash
# generate_certificates.sh

CERTS_DIR="/etc/mosquitto/certs"
mkdir -p "$CERTS_DIR"

# 1. Generare CA (Certificate Authority)
openssl genrsa -out "$CERTS_DIR/ca.key" 2048
openssl req -x509 -new -nodes \
    -key "$CERTS_DIR/ca.key" \
    -sha256 -days 1825 \
    -out "$CERTS_DIR/ca.crt" \
    -subj "/C=RO/ST=Bucuresti/O=ASE-CSIE/CN=MQTT-CA"

# 2. Generare certificat server
openssl genrsa -out "$CERTS_DIR/server.key" 2048
openssl req -new \
    -key "$CERTS_DIR/server.key" \
    -out "$CERTS_DIR/server.csr" \
    -subj "/C=RO/ST=Bucuresti/O=ASE-CSIE/CN=mqtt-broker"
openssl x509 -req \
    -in "$CERTS_DIR/server.csr" \
    -CA "$CERTS_DIR/ca.crt" \
    -CAkey "$CERTS_DIR/ca.key" \
    -CAcreateserial \
    -out "$CERTS_DIR/server.crt" \
    -days 365 -sha256

# 3. Generare certificat client (pentru mutual TLS)
openssl genrsa -out "$CERTS_DIR/client.key" 2048
openssl req -new \
    -key "$CERTS_DIR/client.key" \
    -out "$CERTS_DIR/client.csr" \
    -subj "/C=RO/ST=Bucuresti/O=ASE-CSIE/CN=sensor-1"
openssl x509 -req \
    -in "$CERTS_DIR/client.csr" \
    -CA "$CERTS_DIR/ca.crt" \
    -CAkey "$CERTS_DIR/ca.key" \
    -CAcreateserial \
    -out "$CERTS_DIR/client.crt" \
    -days 365 -sha256

# 4. Setare permisiuni
chmod 600 "$CERTS_DIR"/*.key
chmod 644 "$CERTS_DIR"/*.crt
```

### 3.3 Verificare TLS în Practică

**Testare conexiune securizată:**

```bash
# Conectare cu TLS (client verifică server)
mosquitto_sub -h broker.local -p 8883 \
    --cafile ca.crt \
    -t "sensors/#" -v

# Conectare cu mutual TLS (ambele părți verifică)
mosquitto_pub -h broker.local -p 8883 \
    --cafile ca.crt \
    --cert client.crt \
    --key client.key \
    -t "sensors/temp" \
    -m "23.5"

# Verificare certificat cu OpenSSL
openssl s_client -connect broker.local:8883 \
    -CAfile ca.crt \
    -verify 5
```

---

## 4. Autentificare și Autorizare

### 4.1 Autentificare Bazată pe Parole

**Crearea fișierului de parole:**

```bash
# Creare utilizatori Mosquitto
mosquitto_passwd -c /etc/mosquitto/passwd admin
mosquitto_passwd /etc/mosquitto/passwd sensor1
mosquitto_passwd /etc/mosquitto/passwd controller
mosquitto_passwd /etc/mosquitto/passwd dashboard
```

**Configurație:**

```ini
# mosquitto.conf
allow_anonymous false
password_file /etc/mosquitto/passwd
```

### 4.2 Access Control Lists (ACL)

**Structură ACL granulară:**

```ini
# /etc/mosquitto/acl.acl

# Wildcards disponibile:
# % c = client ID
# %u = username
# # = multi-level wildcard (a/b/c/d)
# + = single-level wildcard (a/+/c)

# ── ADMIN: Acces complet pentru management ──
user admin
topic readwrite #

# ── SENZORI: Pot doar publica în zona lor ──
user sensor1
topic write home/living/temperature
topic write home/living/humidity
topic read commands/sensor1/#

user sensor2
topic write home/bedroom/temperature
topic read commands/sensor2/#

# ── CONTROLLER: Citește senzori, scrie comenzi ──
user controller
topic read home/#
topic read factory/#
topic write commands/#

# ── DASHBOARD: Read-only pentru vizualizare ──
user dashboard
topic read home/#
topic read factory/#
topic read status/#
topic read alerts/#

# ── STUDENT: Sandbox pentru experimente ──
user student
topic readwrite test/#
topic readwrite sandbox/%u/#

# ── GUEST: Acces minimal la date publice ──
user guest
topic read public/#
```

### 4.3 Autentificare Avansată

**Opțiuni enterprise:**

| Metodă | Complexitate | Scalabilitate | Securitate |
|--------|-------------|---------------|------------|
| Password file | Low | Low (<100 users) | Medium |
| Auth plugin (MySQL/LDAP) | Medium | High | High |
| JWT Tokens | High | Very High | Very High |
| mTLS (certificate-based) | High | High | Highest |

---

## 5. Monitorizare și Detecție

### 5.1 Logging și Audit

**Configurație logging Mosquitto:**

```ini
# mosquitto.conf - Logging detaliat
log_dest file /var/log/mosquitto/mosquitto.log
log_type all
log_timestamp true
log_timestamp_format %Y-%m-%d %H:%M:%S

# Log connections
connection_messages true
log_type subscribe
log_type unsubscribe
```

**Analiză loguri pentru detecție:**

```bash
# Detectare încercări eșuate de autentificare
grep "Connection refused" /var/log/mosquitto/mosquitto.log | \
    awk '{print $NF}' | sort | uniq -c | sort -rn

# Detectare subscriberi la wildcard (potențial malițios)
grep "subscribe.*#" /var/log/mosquitto/mosquitto.log

# Detectare conexiuni de la IP-uri noi
grep "New connection" /var/log/mosquitto/mosquitto.log | \
    awk '{print $6}' | sort | uniq
```

### 5.2 Intrusion Detection pentru IoT

**Scapy-based anomaly detector:**

```python
from scapy.all import sniff, IP, TCP, UDP
from collections import defaultdict
import time

class IoTIDSimple:
    """Detector simplu de intruziuni pentru trafic IoT"""
    
    def __init__(self):
        self.connection_counts = defaultdict(int)
        self.alerts = []
        
        # Thresholds
        self.SCAN_THRESHOLD = 10  # ports/sec from same IP
        self.BRUTEFORCE_THRESHOLD = 5  # failed auth/min
        
    def analyze_packet(self, pkt):
        if IP in pkt and TCP in pkt:
            src_ip = pkt[IP].src
            dst_port = pkt[TCP].dport
            
            # Detectare scan porturi
            key = f"{src_ip}:{int(time.time())}"
            self.connection_counts[key] += 1
            
            if self.connection_counts[key] > self.SCAN_THRESHOLD:
                self.alert(f"PORT SCAN detected from {src_ip}")
                
            # Detectare conexiuni MQTT suspecte
            if dst_port == 1883:
                # MQTT pe port plaintext = risc
                self.alert(f"MQTT cleartext connection: {src_ip}")
                
    def alert(self, message):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        alert = f"[{timestamp}] ALERT: {message}"
        print(alert)
        self.alerts.append(alert)
        
    def run(self, interface="eth0"):
        sniff(iface=interface, prn=self.analyze_packet)
```

### 5.3 Network Traffic Analysis

**Identificare pattern-uri anormale:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    TRAFFIC ANOMALIES                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Normal Pattern:                 Anomaly Indicators:            │
│  ────────────────                ───────────────────            │
│                                                                 │
│  Senzor → Broker               ✗ Senzor → Senzor (lateral)     │
│  [periodic, 1 msg/min]         ✗ Burst de mesaje               │
│                                ✗ Topic wildcard subscribe       │
│  Controller → Senzori          ✗ Topic necunoscut               │
│  [command/response]            ✗ Payload size > normal          │
│                                                                 │
│  Broker connections:           ✗ Multe conexiuni eșuate         │
│  [5-10 stable clients]         ✗ IP necunoscut                  │
│                                ✗ Ore neobișnuite                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 6. Hardening și Best Practices

### 6.1 Checklist Securitate MQTT Broker

```markdown
## MQTT Security Checklist

### Transport Layer
- [ ] TLS 1.2+ enabled (port 8883)
- [ ] Plaintext disabled (port 1883 closed)
- [ ] Strong cipher suites only
- [ ] Certificate validation enabled
- [ ] Perfect Forward Secrecy (ECDHE)

### Authentication
- [ ] Anonymous access disabled
- [ ] Strong passwords enforced
- [ ] Password file permissions (600)
- [ ] Consider mTLS for devices

### Authorization
- [ ] ACL file configured
- [ ] Least privilege per user
- [ ] Wildcard subscribe restricted
- [ ] Admin access audited

### Availability
- [ ] max_connections limited
- [ ] max_packet_size restricted
- [ ] Rate limiting enabled
- [ ] Persistence configured

### Monitoring
- [ ] Detailed logging enabled
- [ ] Log rotation configured
- [ ] Alerting for failed auth
- [ ] Retention policy defined
```

### 6.2 Hardening Dispozitive IoT

**Măsuri pentru senzori și actuatoare:**

| Categorie | Acțiune | Prioritate |
|-----------|---------|------------|
| Credentials | Schimbare parole default | CRITICĂ |
| Firmware | Update la ultima versiune | CRITICĂ |
| Network | Plasare în VLAN dedicat | HIGH |
| Services | Dezactivare servicii inutile | HIGH |
| Crypto | Activare TLS/DTLS | HIGH |
| Access | Restricționare IP-uri management | MEDIUM |
| Logging | Activare syslog remote | MEDIUM |

### 6.3 Secure Development Practices

**Pentru cod IoT:**

```python
# ❌ INSECURE: Hardcoded credentials
BROKER = "mqtt://admin:password123@broker.local"

# ✓ SECURE: Environment variables + TLS
import os
import ssl

def create_secure_client():
    client = mqtt.Client()
    
    # Credentials din environment
    username = os.environ.get('MQTT_USER')
    password = os.environ.get('MQTT_PASS')
    client.username_pw_set(username, password)
    
    # TLS configuration
    client.tls_set(
        ca_certs='/path/to/ca.crt',
        certfile='/path/to/client.crt',
        keyfile='/path/to/client.key',
        tls_version=ssl.PROTOCOL_TLS_CLIENT
    )
    
    # Certificate verification
    client.tls_insecure_set(False)
    
    return client
```

---

## 7. Incident Response

### 7.1 Faze Incident Response

```
┌─────────────────────────────────────────────────────────────────┐
│                    INCIDENT RESPONSE LIFECYCLE                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. PREPARATION        2. IDENTIFICATION     3. CONTAINMENT     │
│  ┌─────────────┐      ┌─────────────┐       ┌─────────────┐    │
│  │ • IR Plan   │ ───► │ • Detect    │ ───►  │ • Isolate   │    │
│  │ • Team      │      │ • Classify  │       │ • Preserve  │    │
│  │ • Tools     │      │ • Assess    │       │ • Document  │    │
│  └─────────────┘      └─────────────┘       └─────────────┘    │
│                                                    │            │
│  ┌─────────────────────────────────────────────────┘            │
│  │                                                              │
│  ▼                                                              │
│  4. ERADICATION        5. RECOVERY           6. LESSONS         │
│  ┌─────────────┐      ┌─────────────┐       ┌─────────────┐    │
│  │ • Remove    │ ───► │ • Restore   │ ───►  │ • Postmortem│    │
│  │ • Patch     │      │ • Validate  │       │ • Update    │    │
│  │ • Harden    │      │ • Monitor   │       │ • Train     │    │
│  └─────────────┘      └─────────────┘       └─────────────┘    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 7.2 Playbook pentru Compromitere MQTT

**Scenariul: Detectare acces neautorizat la broker:**

```markdown
## MQTT Unauthorized Access Playbook

### DETECT
1. Alert trigger: multiple failed authentications from IP X
2. Alert trigger: wildcard subscribe (#) from new client
3. Alert trigger: publish to control topic from unknown client

### CONTAIN
1. Block attacker IP at firewall
   iptables -I INPUT -s <IP> -j DROP
   
2. Revoke compromised credentials
   mosquitto_passwd -D /etc/mosquitto/passwd <username>
   
3. Restart broker to force disconnect
   systemctl restart mosquitto

### INVESTIGATE
1. Preserve logs
   cp /var/log/mosquitto/mosquitto.log /evidence/
   
2. Capture current connections
   netstat -an | grep 1883 > /evidence/connections.txt
   
3. Check for data exfiltration
   grep "subscribe" /evidence/mosquitto.log | grep "#"

### ERADICATE
1. Rotate all credentials
2. Update ACLs to restrict access
3. Enable TLS if not already active
4. Patch any identified vulnerabilities

### RECOVER
1. Restart services with new configuration
2. Verify normal operations
3. Monitor for 24-48 hours
4. Update detection rules based on IoCs
```

### 7.3 Forensics pentru IoT

**Colectare evidențe:**

```bash
# 1. Network capture (live)
tcpdump -i eth0 -w /evidence/capture_$(date +%s).pcap

# 2. Broker state
mosquitto_rr -h localhost -u admin -P pass \
    -t '$SYS/#' -e '$SYS/+/+/+' > /evidence/broker_state.txt

# 3. System state
ps aux > /evidence/processes.txt
netstat -tulpn > /evidence/listening.txt
iptables -L -v -n > /evidence/firewall.txt

# 4. Logs
tar czf /evidence/logs.tar.gz /var/log/mosquitto/ /var/log/syslog
```

---

## Exerciții Practice

### Exercițiul 4.1: Configurare TLS pentru MQTT

1. Generați certificatele folosind `scripts/setup.sh --certs`
2. Configurați Mosquitto cu `tls.conf`
3. Verificați că plaintext este blocat
4. Testați conexiune TLS cu `ex_02_mqtt_client.py`

### Exercițiul 4.2: Implementare ACL

1. Creați utilizatori cu `mosquitto_passwd`
2. Configurați ACL din `acl.acl`
3. Testați permisiunile pentru fiecare rol
4. Verificați că accesul neautorizat este blocat

### Exercițiul 4.3: Segmentare cu Mininet

1. Porniți topologia segmentată: `make mininet-extended`
2. Verificați regulile firewall: `--show-rules`
3. Testați scenariul de izolare: `--scenario isolation`
4. Observați logurile de trafic blocat

### Exercițiul 4.4: Monitorizare și Alertare

1. Configurați logging pe Mosquitto
2. Porniți sniffer-ul: `ex_03_packet_sniffer.py`
3. Simulați un atac de scanare
4. Analizați alertele generate

---

## Referințe

1. MQTT Security Best Practices: https://mqtt.org/security/
2. NIST SP 800-183: Networks of Things
3. IEC 62443: Industrial Cybersecurity Standard
4. CIS Controls for IoT
5. OWASP IoT Security Verification Standard

---

*Document generat pentru Săptămâna 13 - Rețele de Calculatoare, ASE-CSIE*
*Autor: Colectivul de Tehnologii Web*
