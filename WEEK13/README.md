# Starterkit Săptămâna 13 — IoT și Securitate în Rețele de Calculatoare

> **Disciplina**: Rețele de Calculatoare  
> **An universitar**: 2025-2026  
> **Semestrul**: 2  
> **Autori colectiv didactic**: conf.univ.dr. TOMA Andrei, conf.univ.dr. TIMOFTE Carmen Manuela, lect.univ.dr. ILIE-NEMEDI Iulian, asist.univ. CÎMPEANU IONUȚ ALEXANDRU

> **Versiune**: 1.1.0 | **Plan IP**: 10.0.13.0/24 | Licență: MIT

---

## Viziune pedagogică

Acest kit integrează **două perspective complementare asupra securității**:

1. **Perspectiva ofensivă** — înțelegerea modului în care gândesc și acționează atacatorii
2. **Perspectiva defensivă** — implementarea măsurilor de protecție și hardening

Această abordare duală urmărește formarea unei înțelegeri complete: *nu poți apăra ceea ce nu înțelegi cum poate fi atacat*.

---

## Structura kit-ului

```
starterkit_s13/
├── README.md                           # Acest document
├── Makefile                            # Automatizări one-command
├── docker-compose.yml                  # Infrastructură container
├── requirements.txt                    # Dependențe Python
│
├── docs/
│   ├── teoria/
│   │   ├── 00_introducere_securitate.md
│   │   ├── 01_iot_fundamentals.md
│   │   ├── 02_attack_vectors.md
│   │   ├── 03_defensive_measures.md
│   │   └── 04_practical_workflow.md
│   └── slides/
│       ├── CURS_13_outline.md          # Schița pentru prezentarea de curs
│       └── SEMINAR_13_outline.md       # Schița pentru prezentarea de seminar
│
├── scripts/
│   ├── setup.sh                        # Instalare completă
│   ├── cleanup.sh                      # Curățare procese
│   ├── run_demo_offensive.sh           # Demo complet ofensiv
│   ├── run_demo_defensive.sh           # Demo complet defensiv
│   └── capture_traffic.sh              # Captură automată trafic
│
├── python/
│   ├── exercises/
│   │   ├── ex_01_port_scanner.py       # Scanner TCP avansat
│   │   ├── ex_02_mqtt_client.py        # Client MQTT (pub/sub)
│   │   ├── ex_03_packet_sniffer.py     # Analiză pachete (scapy)
│   │   └── ex_04_vuln_checker.py       # Verificator vulnerabilități
│   ├── exploits/
│   │   ├── ftp_backdoor_vsftpd.py      # Exploit CVE-2011-2523
│   │   └── banner_grabber.py           # Enumerare servicii
│   └── utils/
│       ├── net_utils.py                # Utilitare rețea
│       └── report_generator.py         # Generator rapoarte
│
├── docker/
│   ├── Dockerfile.vulnerable           # Container ținte vulnerabile
│   └── docker-compose.pentest.yml      # Stack complet pentest
│
├── mininet/
│   ├── topologies/
│   │   ├── topo_base.py                # Topologie simplă
│   │   └── topo_segmented.py           # Topologie cu segmentare
│   └── scenarios/
│       └── lab_scenario.md             # Scenarii de laborator
│
├── configs/
│   ├── mosquitto/
│   │   ├── mosquitto_plain.conf
│   │   ├── mosquitto_tls.conf
│   │   └── mosquitto_acl.acl
│   └── certs/                          # Generate de setup.sh
│
├── tests/
│   ├── smoke_test.sh                   # Verificare rapidă
│   └── expected_outputs.md             # Rezultate așteptate
│
└── html/
    ├── presentation_curs.html          # Prezentare interactivă curs
    └── presentation_seminar.html       # Prezentare interactivă seminar
```

---

## Quickstart (3 minute)

### Opțiunea A: Demo automat (recomandat pentru verificare rapidă)

```bash
# 1. Verificare mediu
./scripts/verify.sh

# 2. Demo automat (generează artefacte)
./scripts/run_all.sh --quick

# 3. Verificare artefacte
ls -la artifacts/
# Așteptat: demo.log, demo.pcap, validation.txt

# 4. Smoke test complet
./tests/smoke_test.sh
```

### Opțiunea B: Docker (recomandat pentru pentest)

```bash
# 1. Setup și pornire
make setup
make docker-up

# 2. Verificare
make test

# 3. Demo complet ofensiv
make demo-offensive

# 4. Curățare
make docker-down
```

### Opțiunea B: Mininet (recomandat pentru IoT/SDN)

```bash
# 1. Setup complet
sudo make setup-mininet

# 2. Rulare topologie
sudo make mininet-base

# 3. În CLI mininet: pingall, apoi scenarii
```

---

## Conținut detaliat

### Partea I: IoT și Protocoale (60 min)

| Activitate | Durată | Fișiere |
|------------|--------|---------|
| Fundamentele IoT | 15 min | `docs/teoria/01_iot_fundamentals.md` |
| MQTT în practică | 20 min | `python/exercises/ex_02_mqtt_client.py` |
| Captură și analiză trafic | 15 min | `scripts/capture_traffic.sh` |
| TLS și autentificare | 10 min | `configs/mosquitto/` |

### Partea II: Securitate Ofensivă (50 min)

| Activitate | Durată | Fișiere |
|------------|--------|---------|
| Scanare porturi | 15 min | `python/exercises/ex_01_port_scanner.py` |
| Enumerare vulnerabilități | 15 min | `python/exploits/banner_grabber.py` |
| Exploatare controlată | 20 min | `python/exploits/ftp_backdoor_vsftpd.py` |

### Partea III: Securitate Defensivă (30 min)

| Activitate | Durată | Fișiere |
|------------|--------|---------|
| Segmentare rețea | 15 min | `mininet/topologies/topo_segmented.py` |
| Măsuri de hardening | 15 min | `docs/teoria/03_defensive_measures.md` |

---

## Comenzi Makefile disponibile

```bash
# === SETUP ===
make setup              # Instalare dependențe + certificate
make setup-mininet      # Setup complet pentru Mininet (sudo)

# === DOCKER ===
make docker-up          # Pornire containere vulnerabile
make docker-down        # Oprire și curățare containere
make docker-logs        # Vizualizare loguri containere

# === DEMONSTRAȚII ===
make demo-offensive     # Secvență completă: scan → enum → exploit
make demo-defensive     # Secvență: TLS → ACL → segmentare
make demo-mqtt-plain    # MQTT fără criptare (captură vizibilă)
make demo-mqtt-tls      # MQTT cu TLS (captură criptată)

# === EXERCIȚII ===
make scan TARGET=10.0.13.11        # Scanare porturi
make mqtt-pub TOPIC=home/temp      # Publicare MQTT
make mqtt-sub TOPIC=home/temp      # Abonare MQTT
make exploit-ftp                   # Exploit vsftpd

# === MININET ===
make mininet-base       # Topologie bază (sudo)
make mininet-extended   # Topologie segmentată (sudo)
make mininet-clean      # Curățare Mininet (sudo)

# === TESTE ===
make test               # Smoke test complet
make lint               # Verificare sintaxă Python

# === CURĂȚARE ===
make clean              # Curățare fișiere temporare
make clean-all          # Reset complet
```

---

## Fluxul de lucru recomandat pentru studenți

### Pas 1: Pregătire mediu (10 min)

```bash
git clone <repo> && cd starterkit_s13
make setup
make test
```

### Pas 2: Înțelegere conceptuală (15 min)

1. Citește `docs/teoria/00_introducere_securitate.md`
2. Identifică diferențele dintre abordarea ofensivă și defensivă
3. Notează 3 întrebări pentru laborator

### Pas 3: Practică ofensivă (30 min)

```bash
make docker-up
make demo-offensive
# Observă output-ul fiecărei etape
```

### Pas 4: Practică defensivă (30 min)

```bash
make demo-defensive
# Compară mqtt_plain.pcap cu mqtt_tls.pcap
```

### Pas 5: Documentare și reflecție (15 min)

Completează fișierul `REZULTATE_S13.txt` cu:
- Capturi de ecran relevante
- Răspunsuri la întrebările din fiecare exercițiu
- 3 măsuri de securitate aplicate

---

## Cerințe sistem

### Minime

- Linux (Ubuntu 22.04+ / Debian 12+)
- Python 3.10+
- Docker 24+ și Docker Compose v2
- 4 GB RAM
- 10 GB spațiu disk

### Recomandate

- 8 GB RAM (pentru Mininet + Docker simultan)
- Acces root (pentru Mininet)
- VS Code cu extensii Python și Docker

---

## Troubleshooting

| Simptom | Cauză probabilă | Soluție |
|---------|-----------------|---------|
| `docker: command not found` | Docker neinstalat | `sudo apt install docker.io docker-compose-v2` |
| `Permission denied` la Docker | User nu e în grupul docker | `sudo usermod -aG docker $USER && newgrp docker` |
| Port 8888 ocupat | Alt serviciu rulează | `sudo lsof -i :8888` și oprește serviciul |
| `mn: command not found` | Mininet neinstalat | `sudo apt install mininet` |
| OVS crash | Serviciu oprit | `sudo service openvswitch-switch restart` |
| Certificate expired | Cert-uri vechi | `rm -rf configs/certs && make setup` |
| `paho-mqtt` import error | Dependență lipsă | `pip install -r requirements.txt` |
| Mininet stale state | Procese vechi | `sudo make mininet-clean` |

---

## Referințe bibliografice

1. Kurose, J., Ross, K. (2016). *Computer Networking: A Top-Down Approach*, 7th Edition. Pearson.
2. Rhodes, B., Goetzen, J. (2014). *Foundations of Python Network Programming*. Apress.
3. Timofte, C., Constantinescu, R., Nemedi, I. (2004). *Rețele de calculatoare – caiet de seminar*. ASE.
4. OWASP IoT Security Verification Standard (ISVS). [https://owasp.org/www-project-iot-security-verification-standard/](https://owasp.org/www-project-iot-security-verification-standard/)
5. Eclipse Mosquitto Documentation. [https://mosquitto.org/documentation/](https://mosquitto.org/documentation/)

---

## Evaluare și predare

Conform fișei disciplinei, la finalul semestrului se predă:

1. **Proiect de echipă** (15% din nota finală):
   - Aplicație client-server funcțională
   - Documentație tehnică
   - Prezentare demonstrativă

2. **Teste de seminar** (15% din nota finală):
   - 3 teste scurte pe parcurs
   - Cunoștințe teoretice și practice

3. **Examen scris** (70% din nota finală):
   - La calculator
   - Concepte fundamentale de rețele

---

## Suport și contact

- **Platformă curs**: online.ase.ro
- **Email colectiv**: retele-calc@ie.ase.ro
- **Consultații**: conform orarului afișat pe platformă

---

*Ultima actualizare: Decembrie 2025*
