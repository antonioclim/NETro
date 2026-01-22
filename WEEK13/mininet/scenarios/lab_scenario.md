# Ghid Complet: Scenarii de Laborator - Săptămâna 13
## Securitatea în Rețelele de Calculatoare: IoT și Pentest

**Durată estimată**: 120 minute (2 ore)  
**Nivel dificultate**: Intermediar-Avansat  
**Curs**: Rețele de Calculatoare, ASE-CSIE, 2025-2026

---

## Cuprins

1. [Pregătire și Verificare Mediu](#1-pregătire-și-verificare-mediu)
2. [Scenariul A: Perspectiva Ofensivă (Red Team)](#2-scenariul-a-perspectiva-ofensivă-red-team)
3. [Scenariul B: Perspectiva Defensivă (Blue Team)](#3-scenariul-b-perspectiva-defensivă-blue-team)
4. [Scenariul C: MQTT și IoT](#4-scenariul-c-mqtt-și-iot)
5. [Scenariul D: Segmentare și Firewall](#5-scenariul-d-segmentare-și-firewall)
6. [Exerciții Individuale](#6-exerciții-individuale)
7. [Generare Raport](#7-generare-raport)
8. [Troubleshooting](#8-troubleshooting)

---

## 1. Pregătire și Verificare Mediu

### 1.1 Cerințe Sistem

```bash
# Verificare versiuni
python3 --version    # >= 3.8
docker --version     # >= 20.10
docker-compose --version  # >= 1.29

# Verificare utilizator în grupul docker
groups | grep -q docker && echo "OK: docker group" || echo "WARN: add user to docker group"
```

### 1.2 Instalare și Pornire

```bash
# Navigare în directorul starterkit
cd starterkit_s13

# Instalare completă (dependențe Python + Docker images)
make setup

# Verificare instalare
make check
```

**Output Așteptat**:
```
[✓] Python 3.x detected
[✓] Docker running
[✓] Docker Compose available
[✓] Required Python packages installed
[✓] Docker images available
```

### 1.3 Pornire Infrastructură

```bash
# Varianta completă (toate serviciile)
make start-all

# Sau selectiv:
make docker-up      # Doar containere vulnerabile
make mininet-base   # Doar topologie Mininet simplă
make mqtt-start     # Doar broker MQTT
```

### 1.4 Verificare Servicii Active

```bash
# Verificare containere
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Test conectivitate
curl -s http://localhost:8888 | head -5    # DVWA
curl -s http://localhost:8080 | head -5    # WebGoat
nc -vz localhost 2121                       # vsftpd
nc -vz localhost 1883                       # MQTT plain
```

**Topologia Completă**:
```
┌─────────────────────────────────────────────────────────────────────────┐
│                         INFRASTRUCTURĂ LAB S13                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   ┌─────────────────┐                      ┌─────────────────────┐      │
│   │  ATTACKER HOST  │                      │    MININET TOPO     │      │
│   │  (Terminal)     │                      │  ┌───────────────┐  │      │
│   │  Python scripts │                      │  │   Controller  │  │      │
│   └────────┬────────┘                      │  └───────┬───────┘  │      │
│            │                               │          │          │      │
│   ┌────────┴───────────────────────────────┼──────────┘          │      │
│   │           DOCKER NETWORK               │                     │      │
│   │           pentestnet                   │    ┌─────┐ ┌─────┐  │      │
│   │           172.20.0.0/24                │    │ s1  │ │ s2  │  │      │
│   └───────────────┬────────────────────────┼────┴──┬──┴─┴──┬──┴──│      │
│                   │                        │       │       │     │      │
│     ┌─────────────┼─────────────┐          │    ┌──┴──┐ ┌──┴──┐  │      │
│     │             │             │          │    │ h1  │ │ h2  │  │      │
│  ┌──┴───┐   ┌────┴───┐   ┌────┴───┐       │    │IoT  │ │MGMT │  │      │
│  │ DVWA │   │WebGoat │   │ vsftpd │       │    └─────┘ └─────┘  │      │
│  │:8888 │   │ :8080  │   │ :2121  │       └─────────────────────┘      │
│  │ SQLi │   │ OWASP  │   │CVE-2011│                                    │
│  │ XSS  │   │Lessons │   │ -2523  │       ┌─────────────────────┐      │
│  └──────┘   └────────┘   └────────┘       │   MQTT ECOSYSTEM    │      │
│                                           │  ┌───────────────┐  │      │
│  ┌──────────────────────────────────┐     │  │  Mosquitto    │  │      │
│  │         ATTACKER TOOLS           │     │  │  :1883 plain  │  │      │
│  │  • Port Scanner                  │     │  │  :8883 TLS    │  │      │
│  │  • Banner Grabber                │     │  └───────┬───────┘  │      │
│  │  • Packet Sniffer                │     │          │          │      │
│  │  • Vuln Checker                  │     │   ┌──────┼──────┐   │      │
│  │  • FTP Backdoor Exploit          │     │   │ Pub  │ Sub  │   │      │
│  └──────────────────────────────────┘     │   └──────┴──────┘   │      │
│                                           └─────────────────────┘      │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Scenariul A: Perspectiva Ofensivă (Red Team)

### Obiectiv
Identificați și exploatați vulnerabilități în infrastructura de test folosind metodologia de penetration testing în 4 faze.

### Faza A.1: Recunoaștere (15 minute)

#### A.1.1 Descoperire Hosturi

```bash
# Scanare rețea pentru descoperire
python python/exercises/ex_01_port_scanner.py 172.20.0.0/24 \
    --discovery \
    --timeout 0.5
```

#### A.1.2 Scanare Porturi

```bash
# Scanare completă pe target-uri identificate
python python/exercises/ex_01_port_scanner.py 172.20.0.10 \
    -p 1-1024 \
    --threads 50 \
    -o results/scan_dvwa.json

python python/exercises/ex_01_port_scanner.py 172.20.0.12 \
    -p 21,22,80,443,6200 \
    -o results/scan_vsftpd.json
```

**Output de Analizat**:
```
[*] Scanning 172.20.0.12 (5 ports)
[+] 172.20.0.12:21     OPEN   (ftp)
[+] 172.20.0.12:6200   OPEN   (unknown)
[-] 172.20.0.12:22     CLOSED
[-] 172.20.0.12:80     CLOSED
[-] 172.20.0.12:443    CLOSED

Scan completed in 2.34s
```

**Întrebare**: Ce semnifică portul 6200 deschis pe serverul FTP?

#### A.1.3 Banner Grabbing

```bash
# Extragere informații versiuni
python python/exploits/banner_grabber.py 172.20.0.12 -p 21
python python/exploits/banner_grabber.py 172.20.0.10 -p 80
python python/exploits/banner_grabber.py 172.20.0.11 -p 8080
```

**Colectare Rezultate**:
| Target | Port | Banner | Versiune |
|--------|------|--------|----------|
| 172.20.0.12 | 21 | 220 (vsFTPd 2.3.4) | 2.3.4 |
| 172.20.0.10 | 80 | Apache/2.4.xx | 2.4.xx |
| 172.20.0.11 | 8080 | WebGoat | N/A |

### Faza A.2: Evaluare Vulnerabilități (15 minute)

#### A.2.1 Verificare CVE

```bash
# Verificare automată vulnerabilități cunoscute
python python/exercises/ex_04_vuln_checker.py \
    --targets 172.20.0.10,172.20.0.11,172.20.0.12 \
    --ports 21,80,8080 \
    --check-cve \
    -o results/vuln_report.json
```

#### A.2.2 Analiză Manuală

```bash
# Verificare specifică vsftpd
python python/exercises/ex_04_vuln_checker.py \
    --target 172.20.0.12 \
    --service ftp \
    --version "2.3.4" \
    --verbose
```

**Output Așteptat**:
```
[CRITICAL] CVE-2011-2523 detected!
Service: vsftpd 2.3.4
Type: Backdoor (smiley face trigger)
CVSS Score: 10.0 (CRITICAL)
Impact: Remote Code Execution as root
Exploit Available: YES

Recommendation: Upgrade to vsftpd >= 2.3.5 immediately
```

### Faza A.3: Exploatare (20 minute)

⚠️ **ATENȚIE**: Această secțiune este DOAR pentru medii de laborator controlate!

#### A.3.1 Demonstrație Exploit vsftpd

```bash
# Terminal 1: Pornire captură trafic
make capture-start IF=docker0 FILTER="port 21 or port 6200"

# Terminal 2: Execuție exploit
python python/exploits/ftp_backdoor_vsftpd.py 172.20.0.12 \
    --port 2121 \
    --command "id && hostname && uname -a"
```

**Explicație Tehnică**:
1. Exploit-ul trimite `USER test:)` (observați `:)` - trigger-ul backdoor)
2. vsftpd 2.3.4 deschide un shell pe portul 6200
3. Atacatorul se conectează pe 6200 și primește acces root

#### A.3.2 Analiză Captură

```bash
# Oprire captură
make capture-stop

# Analiză
./scripts/capture_traffic.sh --analyze captures/capture_latest.pcap
```

**Identificați în Wireshark**:
1. Pachetul FTP cu `USER test:)` (filtru: `ftp.request.command == "USER"`)
2. Conexiunea nouă pe portul 6200 (filtru: `tcp.port == 6200`)
3. Comenzile executate în shell (Follow TCP Stream)

### Faza A.4: Post-Exploatare (10 minute)

#### A.4.1 Demonstrație Acces

```bash
# Ce poate face un atacator cu acces root?
python python/exploits/ftp_backdoor_vsftpd.py 172.20.0.12 \
    --port 2121 \
    --command "cat /etc/shadow | head -3"

python python/exploits/ftp_backdoor_vsftpd.py 172.20.0.12 \
    --port 2121 \
    --command "netstat -tlnp"
```

#### A.4.2 Documentare Găsiri

Completați în raport:
- Vulnerabilități identificate
- Pași de reproducere
- Dovezi (screenshots, outputs)
- Severitate (CVSS)
- Recomandări

---

## 3. Scenariul B: Perspectiva Defensivă (Blue Team)

### Obiectiv
Implementați și verificați măsuri de securitate pentru a preveni atacurile demonstrate în Scenariul A.

### Faza B.1: Hardening vsftpd (15 minute)

#### B.1.1 Configurație Securizată

```bash
# Vizualizare configurație actuală (vulnerabilă)
cat configs/vsftpd/vsftpd.conf

# Aplicare configurație hardened
cat > configs/vsftpd/vsftpd_secure.conf << 'EOF'
# vsftpd Hardened Configuration
# ============================

# Dezactivare acces anonim
anonymous_enable=NO
local_enable=YES

# Restricții scriere
write_enable=NO
anon_upload_enable=NO
anon_mkdir_write_enable=NO

# Chroot utilizatori în home
chroot_local_user=YES
allow_writeable_chroot=NO

# Logging extensiv
xferlog_enable=YES
xferlog_std_format=NO
log_ftp_protocol=YES
syslog_enable=YES

# Timeout-uri agresive
idle_session_timeout=60
data_connection_timeout=30

# Banner neutru (fără versiune)
ftpd_banner=FTP Server Ready

# Restricții conexiuni
max_clients=10
max_per_ip=3

# Dezactivare PASV (sau restricționare range)
pasv_enable=NO
# pasv_min_port=50000
# pasv_max_port=50100

# SSL/TLS obligatoriu
ssl_enable=YES
force_local_data_ssl=YES
force_local_logins_ssl=YES
ssl_tlsv1=YES
ssl_sslv2=NO
ssl_sslv3=NO
rsa_cert_file=/etc/ssl/certs/vsftpd.pem
rsa_private_key_file=/etc/ssl/private/vsftpd.key
EOF
```

#### B.1.2 Upgrade Versiune (Soluția Reală)

```bash
# În producție, soluția corectă este upgrade
# vsftpd >= 2.3.5 nu are backdoor-ul

# Verificare versiune nouă
apt-cache policy vsftpd
```

### Faza B.2: Configurare Firewall (15 minute)

#### B.2.1 Reguli iptables

```bash
# Salvare reguli existente
iptables-save > /tmp/iptables_backup

# Aplicare reguli restrictive
cat > /tmp/firewall_rules.sh << 'EOF'
#!/bin/bash
# Firewall rules pentru mediu lab

# Flush reguli existente
iptables -F
iptables -X

# Politică implicită: DROP
iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT ACCEPT

# Permitere trafic loopback
iptables -A INPUT -i lo -j ACCEPT

# Permitere conexiuni stabilite
iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

# SSH doar din subnet-ul de management
iptables -A INPUT -p tcp --dport 22 -s 10.0.1.0/24 -j ACCEPT

# HTTP/HTTPS pentru aplicații web
iptables -A INPUT -p tcp --dport 80 -j ACCEPT
iptables -A INPUT -p tcp --dport 443 -j ACCEPT

# FTP restricționat (doar din rețeaua internă)
iptables -A INPUT -p tcp --dport 21 -s 172.20.0.0/24 -j ACCEPT

# MQTT TLS permis, plain blocat
iptables -A INPUT -p tcp --dport 8883 -j ACCEPT
iptables -A INPUT -p tcp --dport 1883 -j DROP

# Blocare port backdoor
iptables -A INPUT -p tcp --dport 6200 -j DROP
iptables -A OUTPUT -p tcp --dport 6200 -j DROP

# Logging pachete blocate
iptables -A INPUT -j LOG --log-prefix "IPTables-Dropped: "

echo "Firewall rules applied"
EOF

chmod +x /tmp/firewall_rules.sh
```

#### B.2.2 Verificare Reguli

```bash
# Listare reguli active
iptables -L -n -v

# Test că portul 6200 e blocat
nc -vz localhost 6200  # Ar trebui să eșueze
```

### Faza B.3: Implementare TLS pentru MQTT (15 minute)

#### B.3.1 Generare Certificate

```bash
# Generare CA și certificate
make mqtt-certs

# Structura rezultată:
# configs/certs/
# ├── ca.crt          # Certificate Authority
# ├── ca.key          # CA private key
# ├── server.crt      # Certificat server Mosquitto
# ├── server.key      # Cheie privată server
# ├── client.crt      # Certificat client
# └── client.key      # Cheie privată client
```

#### B.3.2 Configurare Mosquitto cu TLS

```bash
# Pornire broker cu TLS
make mqtt-secure

# Verificare că portul plain e dezactivat
nc -vz localhost 1883  # Ar trebui să eșueze
nc -vz localhost 8883  # Ar trebui să reușească
```

#### B.3.3 Test Client TLS

```bash
# Publicare securizată
python python/exercises/ex_02_mqtt_client.py \
    --broker localhost \
    --port 8883 \
    --tls \
    --ca-cert configs/certs/ca.crt \
    --mode sensor \
    --topic "iot/sensor/temp"

# Abonare securizată (alt terminal)
python python/exercises/ex_02_mqtt_client.py \
    --broker localhost \
    --port 8883 \
    --tls \
    --ca-cert configs/certs/ca.crt \
    --mode dashboard \
    --topic "iot/sensor/#"
```

### Faza B.4: Monitorizare și Detecție (10 minute)

#### B.4.1 Activare Logging

```bash
# Configurare logging extins Mosquitto
cat > configs/mosquitto/logging.conf << 'EOF'
# Logging Configuration
log_dest file /var/log/mosquitto/mosquitto.log
log_dest stdout
log_type error
log_type warning
log_type notice
log_type information
log_type subscribe
log_type unsubscribe
connection_messages true
log_timestamp true
EOF
```

#### B.4.2 Pornire Sniffer IDS

```bash
# Monitorizare în timp real pentru anomalii
python python/exercises/ex_03_packet_sniffer.py \
    --interface docker0 \
    --filter "tcp port 21 or tcp port 6200" \
    --alert-on "USER.*:)" \
    --log results/ids_alerts.log
```

---

## 4. Scenariul C: MQTT și IoT

### Obiectiv
Înțelegerea securității protocoalelor IoT prin practică cu MQTT.

### Faza C.1: MQTT Plain (Vulnerabil) - 10 minute

#### C.1.1 Pornire Mediu

```bash
# Pornire broker fără securitate
make mqtt-plain

# Verificare
mosquitto_pub -h localhost -p 1883 -t "test" -m "hello"
```

#### C.1.2 Interceptare Trafic

```bash
# Terminal 1: Captură
./scripts/capture_traffic.sh --protocol mqtt-plain --duration 60

# Terminal 2: Generare trafic
python python/exercises/ex_02_mqtt_client.py \
    --broker localhost --port 1883 \
    --mode sensor --count 10
```

#### C.1.3 Analiză

```bash
# Vizualizare payload în clar
./scripts/capture_traffic.sh --analyze captures/mqtt_plain_*.pcap

# În Wireshark: Filtru "mqtt"
# Observați: topic-uri și mesaje vizibile plaintext
```

### Faza C.2: MQTT TLS (Securizat) - 10 minute

#### C.2.1 Pornire Securizată

```bash
# Pornire broker cu TLS
make mqtt-secure

# Verificare conexiune TLS
openssl s_client -connect localhost:8883 -CAfile configs/certs/ca.crt
```

#### C.2.2 Captură și Comparație

```bash
# Terminal 1: Captură
./scripts/capture_traffic.sh --protocol mqtt-tls --duration 60

# Terminal 2: Generare trafic TLS
python python/exercises/ex_02_mqtt_client.py \
    --broker localhost --port 8883 \
    --tls --ca-cert configs/certs/ca.crt \
    --mode sensor --count 10
```

#### C.2.3 Observații

```bash
# Analiză
./scripts/capture_traffic.sh --analyze captures/mqtt_tls_*.pcap

# În Wireshark: Filtru "tcp.port == 8883"
# Observați: payload CRIPTAT, doar handshake TLS vizibil
```

### Faza C.3: Autentificare și ACL - 10 minute

#### C.3.1 Configurare Utilizatori

```bash
# Vizualizare ACL
cat configs/mosquitto/acl.acl

# Structura:
# user sensor1: poate publica pe iot/sensor/+
# user controller: poate subscrie la iot/# și publica pe iot/actuator/#
# user admin: acces complet
```

#### C.3.2 Test Permisiuni

```bash
# Test ca sensor (ar trebui să reușească)
mosquitto_pub -h localhost -p 8883 \
    --cafile configs/certs/ca.crt \
    -u sensor1 -P sensor1pass \
    -t "iot/sensor/temp" -m "25.5"

# Test ca sensor pe topic neautorizat (ar trebui să eșueze)
mosquitto_pub -h localhost -p 8883 \
    --cafile configs/certs/ca.crt \
    -u sensor1 -P sensor1pass \
    -t "iot/actuator/relay" -m "ON"
# Error: Not authorized
```

---

## 5. Scenariul D: Segmentare și Firewall

### Obiectiv
Implementarea principiului Defense in Depth prin segmentare de rețea cu Mininet.

### Faza D.1: Topologie Simplă - 10 minute

```bash
# Pornire topologie bază
make mininet-base

# În CLI Mininet:
mininet> nodes
mininet> net
mininet> pingall
```

### Faza D.2: Topologie Segmentată - 15 minute

```bash
# Pornire topologie cu firewall
make mininet-segmented

# Testare segmentare:
mininet> h1 ping -c 2 h3    # IoT -> IoT: PERMIS
mininet> h1 ping -c 2 h5    # IoT -> MGMT: BLOCAT
mininet> h5 ping -c 2 h1    # MGMT -> IoT: PERMIS (admin)
```

### Faza D.3: Demonstrație Firewall - 10 minute

```bash
# Rulare demo interactiv
./scripts/run_demo_defensive.sh --scenario all --interactive

# Scenarii demonstrate:
# 1. Izolare zonă IoT
# 2. Prevenire mișcare laterală
# 3. Acces administrare controlat
# 4. Blocare port scan
```

---

## 6. Exerciții Individuale

### Exercițiu 1: Port Scanner Personalizat (15 minute)

**Cerință**: Modificați `ex_01_port_scanner.py` pentru a adăuga:
1. Detectare sistem de operare prin TTL
2. Export rezultate în format XML (nmap-style)

**Pași**:
```bash
# Deschideți fișierul
vim python/exercises/ex_01_port_scanner.py

# Găsiți secțiunea TODO pentru studenți
# Implementați funcția os_fingerprint()

# Test
python python/exercises/ex_01_port_scanner.py 172.20.0.10 \
    -p 80 --os-detect -o results/scan_os.xml --format xml
```

### Exercițiu 2: Detector Backdoor (15 minute)

**Cerință**: Creați un script care detectează tentative de exploatare vsftpd.

**Template**:
```python
#!/usr/bin/env python3
"""
Detector pentru tentative de exploatare vsftpd 2.3.4
Monitorizează traficul FTP pentru pattern-ul ":)"
"""

from scapy.all import sniff, TCP, Raw
import re

def detect_backdoor(packet):
    """Callback pentru detectare pattern backdoor."""
    if packet.haslayer(Raw):
        payload = packet[Raw].load.decode('utf-8', errors='ignore')
        # TODO: Implementați detectarea pattern-ului "USER.*:)"
        # TODO: Alertă dacă se detectează și conexiune pe portul 6200
        pass

if __name__ == "__main__":
    print("[*] Starting backdoor detector...")
    sniff(filter="tcp port 21", prn=detect_backdoor)
```

### Exercițiu 3: Raport de Securitate (15 minute)

**Cerință**: Generați un raport complet folosind tool-ul de raportare.

```bash
# Colectare date
python python/utils/report_generator.py \
    --scan-results results/scan_*.json \
    --vuln-results results/vuln_report.json \
    --captures captures/*.pcap \
    --output results/security_report \
    --format all \
    --template professional
```

---

## 7. Generare Raport

### 7.1 Structura Raportului Final

```bash
# Generare raport HTML interactiv
python python/utils/report_generator.py \
    --title "Raport Securitate Lab S13" \
    --author "[Numele vostru]" \
    --date "$(date +%Y-%m-%d)" \
    --scan-results results/ \
    --output results/RAPORT_FINAL \
    --format html,md,pdf
```

### 7.2 Conținut Obligatoriu

```markdown
# Raport Securitate - Seminar 13

## 1. Sumar Executiv
- Scope: [Ce a fost testat]
- Metodologie: [Cum a fost testat]
- Găsiri principale: [Top 3 vulnerabilități]

## 2. Găsiri Detaliate

### 2.1 Vulnerabilitate Critică: vsftpd Backdoor
- **Severitate**: CRITICĂ (CVSS 10.0)
- **CVE**: CVE-2011-2523
- **Descriere**: [...]
- **Dovadă**: [Screenshot/output]
- **Remediere**: Upgrade la vsftpd >= 2.3.5

### 2.2 Vulnerabilitate Medie: MQTT fără TLS
- **Severitate**: MEDIE (CVSS 5.3)
- **Descriere**: [...]
- **Remediere**: Activare TLS, configurare ACL

## 3. Recomandări
1. [Prioritate 1 - Critică]
2. [Prioritate 2 - Ridicată]
3. [Prioritate 3 - Medie]

## 4. Anexe
- Scanări complete
- Capturi trafic
- Configurații propuse
```

### 7.3 Export Final

```bash
# Arhivare pentru predare
make package-results

# Verificare conținut
ls -la results/SUBMISSION_S13_*.zip
unzip -l results/SUBMISSION_S13_*.zip
```

---

## 8. Troubleshooting

### 8.1 Probleme Frecvente

| Simptom | Cauză Probabilă | Soluție |
|---------|-----------------|---------|
| `Connection refused` la Docker | Containere nefuncționale | `make docker-restart` |
| `Permission denied` la scan | Lipsă drepturi | `sudo` sau adăugare la grup docker |
| `Module not found` Python | Dependențe lipsă | `make setup` |
| Mininet nu pornește | Procese reziduale | `sudo mn -c && make mininet-base` |
| MQTT connection timeout | Broker oprit | `make mqtt-start` |
| TLS handshake failed | Certificate invalide | `make mqtt-certs` (regenerare) |
| Port 6200 nu răspunde | vsftpd resetat | `docker-compose restart vsftpd` |

### 8.2 Comenzi de Diagnosticare

```bash
# Verificare completă
make check

# Stare containere
docker ps -a
docker-compose logs --tail=50

# Verificare porturi
ss -tlnp | grep -E "21|80|1883|8080|8883"

# Verificare rețea Docker
docker network inspect pentestnet

# Curățare completă și repornire
make clean-all && make start-all
```

### 8.3 Reset Complet

```bash
# Dacă nimic nu funcționează
./scripts/cleanup.sh --all --force
docker system prune -a --volumes
make setup
make start-all
```

---

## Anexă: Referințe Rapide

### Comenzi Make Esențiale

```bash
make setup          # Instalare inițială
make start-all      # Pornire completă
make docker-up      # Doar containere
make mqtt-start     # Doar MQTT
make mininet-base   # Topologie simplă
make scan TARGET=X  # Scanare rapidă
make capture-start  # Pornire tcpdump
make report         # Generare raport
make clean-all      # Curățare completă
make help           # Lista completă
```

### Adrese IP

| Serviciu | IP | Port(uri) |
|----------|----|----|
| DVWA | 172.20.0.10 | 80 (intern), 8888 (extern) |
| WebGoat | 172.20.0.11 | 8080 |
| vsftpd | 172.20.0.12 | 21 (intern), 2121 (extern), 6200 (backdoor) |
| Mosquitto | 172.20.0.100 | 1883 (plain), 8883 (TLS) |

### Credențiale

| Serviciu | Username | Password |
|----------|----------|----------|
| DVWA | admin | password |
| WebGoat | (register) | (register) |
| vsftpd | anonymous | (any) |
| MQTT sensor1 | sensor1 | sensor1pass |
| MQTT admin | admin | adminpass |

---

*Document actualizat pentru Seminar 13 - Rețele de Calculatoare*  
*ASE București, CSIE, 2025-2026*
