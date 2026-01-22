# Starterkit Săptămâna 2: Modele OSI/TCP-IP & Programare Socket

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Mininet](https://img.shields.io/badge/Mininet-2.3.0-green.svg)](http://mininet.org)
[![License](https://img.shields.io/badge/License-Educational-yellow.svg)]()

**Disciplina:** Rețele de Calculatoare  
**Săptămâna:** 2 din 14  
**Autor:** Revolvix&Hypotheticalandrei

---

## Ce vei învăța (concret)

Săptămâna asta punem bazele: cum funcționează rețelele "sub capotă" și cum scriem cod care comunică prin ele.

### Obiective

| Nivel | Ce faci |
|-------|---------|
| **Înțelegi** | De ce avem straturi în OSI și TCP/IP, și cum se mapează între ele |
| **Aplici** | Scrii un server TCP/UDP concurent în Python |
| **Analizezi** | Capturezi trafic și identifici handshake-ul TCP în Wireshark/tshark |
| **Evaluezi** | Alegi TCP sau UDP în funcție de context |

### De ce te interesează asta

Ca viitor programator/admin, vei întâlni constant:
- **Debugging rețea**: „Aplicația nu răspunde" — e la nivel L7 (cod) sau L3 (conectivitate)?
- **Securitate**: Firewall-urile operează la L3/L4, WAF la L7
- **Arhitectură**: Alegerea TCP (fiabilitate) vs UDP (viteză) pentru aplicații financiare

---

## Ce găsești în kit

```
starterkit_s2/
├── README.md                      # Ești aici
├── Makefile                       # Automatizări (setup, demo, clean)
├── requirements.txt               # Dependințe Python
├── curs/
│   ├── c2-modele-arhitecturale.md # Conținut teoretic curs
│   └── assets/
│       ├── images/                # Diagrame PNG
│       └── puml/                  # Surse PlantUML
├── seminar/
│   ├── python/
│   │   ├── exercises/             # Exerciții complete
│   │   │   ├── ex_2_01_tcp.py     # Server/Client TCP concurent
│   │   │   └── ex_2_02_udp.py     # Server/Client UDP cu protocol custom
│   │   └── templates/             # Template-uri de completat
│   ├── mininet/
│   │   ├── topologies/            # Topologii Mininet
│   │   └── scenarios/             # Scenarii de lucru
│   └── captures/                  # Output pcap (generat)
├── docs/
│   ├── curs.md                    # Schiță detaliată curs
│   ├── seminar.md                 # Schiță detaliată seminar
│   ├── lab.md                     # Ghid laborator
│   ├── checklist.md               # Checklist cadru didactic
│   └── rubrici.md                 # Criterii evaluare
├── scripts/
│   ├── setup.sh                   # Instalare dependințe
│   ├── capture.sh                 # Pornire/oprire captură
│   ├── clean.sh                   # Curățare mediu
│   └── verify.sh                  # Verificare configurare
├── docker/
│   ├── Dockerfile                 # Container pentru rulare izolată
│   └── docker-compose.yml         # Orchestrare servicii
├── slides/
│   ├── curs_slides_outline.txt    # Outline prezentare curs
│   └── seminar_slides_outline.txt # Outline prezentare seminar
├── tests/
│   ├── smoke_test.sh              # Test rapid mediu
│   └── expected_outputs.md        # Output-uri de referință
└── assets/
    └── style.css                  # Stil comun HTML-uri
```

---

## De ce ai nevoie

### Mediu recomandat
- **OS**: Ubuntu 22.04+ / Debian 11+ (CLI-only în VirtualBox)
- **RAM**: Minim 2 GB (recomandat 4 GB)
- **Disk**: 5 GB liber
- **Python**: 3.8+

### Dependințe
```
python3, python3-pip
mininet (2.3.0+)
openvswitch-switch
tcpdump, tshark (Wireshark CLI)
netcat-openbsd
```

---

## Pornire rapidă

### 1. Setup mediu
```bash
# Clonare/dezarhivare kit
cd starterkit_s2

# Instalare automată dependințe
make setup

# Verificare mediu
make verify
```

### 2. Demo TCP în 30 de secunde
```bash
# Într-un terminal - pornire server
make tcp-server

# În alt terminal - trimitere mesaj
make tcp-client MSG="Hello World"
```

### 3. Demo Mininet
```bash
# Topologie bază (3 hosturi, 1 switch)
make mininet-cli

# În prompt-ul Mininet:
mininet> pingall
mininet> h1 python3 /path/to/ex_2_01_tcp.py server --port 9999 &
mininet> h2 python3 /path/to/ex_2_01_tcp.py client --host 10.0.0.1 --port 9999 -m "test"
```

### 4. Captură și analiză
```bash
# Pornire captură + demo + analiză
make demo-all

# Vizualizare rezultate
make analyze-tcp
make analyze-udp
```

---

## Comenzi Makefile

| Comandă | Ce face |
|---------|---------|
| `make help` | Afișare ajutor complet |
| `make setup` | Instalare dependințe sistem |
| `make verify` | Verificare mediu de lucru |
| `make demo-all` | Demo complet TCP+UDP cu capturi |
| `make demo-tcp` | Demo doar TCP |
| `make demo-udp` | Demo doar UDP |
| `make mininet-cli` | CLI Mininet topologie bază |
| `make mininet-extended` | CLI cu router (2 subrețele) |
| `make tcp-server` | Server TCP pe localhost:9999 |
| `make tcp-client MSG=x` | Client TCP cu mesaj |
| `make capture-tcp` | Pornire captură trafic TCP |
| `make capture-stop` | Oprire capturi active |
| `make analyze-tcp` | Analiză cu tshark |
| `make clean` | Curățare procese |
| `make clean-all` | Curățare completă (+ pcap, logs) |

---

## Ce faci la curs (2h)

1. **De ce modele arhitecturale?** (15 min)
   - Reducerea complexității
   - Interoperabilitate
   - Analogia cu arhitectura clădirilor

2. **Modelul OSI** (35 min)
   - Cele 7 straturi: Fizic → Aplicație
   - PDU la fiecare nivel
   - Încapsulare/Decapsulare

3. **Modelul TCP/IP** (25 min)
   - Cele 4 straturi practice
   - Comparație cu OSI
   - Protocoale reale

4. **Legătura cu programarea** (15 min)
   - Socket API ca interfață
   - Preview: seminar socket-uri

## Ce faci la seminar (2h)

1. **Warm-up Mininet** (15 min)
   - Pornire topologie
   - Verificare conectivitate

2. **TCP Lab** (35 min)
   - Server concurent (threading)
   - Handshake SYN-SYN/ACK-ACK
   - Captură și analiză

3. **UDP Lab** (25 min)
   - Server datagram
   - Protocol aplicație custom
   - Comparație overhead

4. **Exerciții de înțelegere** (20 min)
   - Parsons Problem (ordonare cod)
   - Trace Exercise (urmărire execuție)
   - Debugging Exercise

5. **Template-uri** (15 min)
   - Completare cod ghidat
   - Testare funcționalitate

---

## Când ceva nu merge

| Problemă | Soluție |
|----------|---------|
| `Address already in use` | `pkill -f ex_2_01` sau schimbă portul |
| `Connection refused` | Verifică dacă serverul rulează: `jobs` |
| Captură goală | Verifică interfața și filtrul tcpdump |
| Mininet nu pornește | `sudo mn -c` pentru curățare |
| `mn: command not found` | `sudo apt-get install mininet` |

---

## Resurse

### Bibliografie obligatorie
- Kurose, Ross — *Computer Networking: A Top-Down Approach*, Cap. 1-2
- Rhodes, Goetzen — *Foundations of Python Network Programming*, Cap. 1-3

### Specificații tehnice
- RFC 793: TCP
- RFC 768: UDP
- IEEE 802.3: Ethernet

### Materiale interactive
- `theory.html` — Teorie interactivă (25+ slide-uri)
- `seminar.html` — Dashboard seminar (8 tab-uri)
- `lab.html` — Ghid laborator pas-cu-pas

---

## Contribuția la proiectul de echipă

Această săptămână aduce următorul **artefact incremental**:

> **Modul de comunicare TCP/UDP** pentru aplicația de echipă
> - Server care acceptă conexiuni de la clienți multipli
> - Protocol aplicație de bază (request-response)
> - Logging structurat pentru debugging

---

## Licență

Material didactic pentru uz intern — ASE București, CSIE.

*Revolvix&Hypotheticalandrei*

---

## Standardizare (v2.1.0)

Acest kit respectă **Standardul Transversal** pentru materialele didactice de rețelistică.

### Demo Automat

```bash
# Rulare demo complet (produce artefacte)
./scripts/run_all.sh

# Verificare artefacte generate
./tests/smoke_test.sh

# Curățare
./scripts/cleanup.sh
```

### Artefacte Generate

După `run_all.sh`, în `artifacts/`:
- `demo.log` - Log complet al demo-ului
- `demo.pcap` - Captură trafic TCP+UDP
- `validation.txt` - Raport validare

### Plan IP Standard (WEEK 2)

| Entitate | IP |
|----------|-----|
| Rețea | 10.0.2.0/24 |
| Gateway | 10.0.2.1 |
| Server | 10.0.2.100 |

### Plan Porturi Standard

| Serviciu | Port |
|----------|------|
| TCP App | 9090 |
| UDP App | 9091 |
| Week Base | 5200-5299 |

---
