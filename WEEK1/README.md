# 🌐 Rețele de Calculatoare – Starterkit Săptămâna 1
## Fundamente ale Rețelelor: Concepte, Componente, Clasificări

> **Disciplina:** Rețele de Calculatoare (25.0205IF3.2-0003)  
> **Program:** Informatică Economică, Anul 3, Semestrul 2  
> **Credite ECTS:** 5  
> **Instituție:** Academia de Studii Economice din București, CSIE  
> **Versiune:** 3.1 Integrat (consolidat din 4 arhive)

---

## Cuprins

1. [Ce vom învăța](#-ce-vom-învăța)
2. [De ce contează](#de-ce-contează)
3. [Structura Kit-ului](#structura-kit-ului)
4. [Cerințe de Mediu](#cerințe-de-mediu)
5. [Instalare Rapidă](#-pornire-rapidă-10-comenzi)
6. [Ghid Makefile](#ghid-makefile)
7. [Ghid Curs (Teorie)](#ghid-curs-teorie)
8. [Ghid Seminar (Practică)](#ghid-seminar-practică)
9. [Ghid Laborator](#ghid-laborator)
10. [Exerciții Python](#-exerciții-python)
11. [Mininet – Rețele Simulate](#-mininet--rețele-simulate)
12. [Docker – Alternativă Portabilă](#docker--alternativă-portabilă)
13. [Evaluare și Livrabile](#evaluare-și-livrabile)
14. [Troubleshooting](#troubleshooting)
15. [Bibliografie](#bibliografie)

---

## 🎯 Ce vom învăța

### Nivel I – Termeni și Definiții Fundamentale
La finalul acestei săptămâni, studentul poate:
- Defini conceptul de rețea de calculatoare și să enumere componentele fundamentale
- Identifica modelele arhitecturale (OSI, TCP/IP) și straturile acestora
- Recunoaște dispozitivele de rețea (NIC, hub, switch, router) și rolul fiecăruia
- Enumera tipurile de topologii și mediile de transmisie

### Nivel II – Înțelegere și Interpretare
- Explica diferențele dintre LAN, WAN și Internet
- Interpreta parametrii de transmisie (bandwidth, latency, jitter, loss)
- Distinge între comutarea de circuit și comutarea de pachete
- Compara comportamentul TCP vs UDP la nivel observațional
- Descrie procesul de încapsulare și rolul fiecărui strat

### Nivel III – Aplicare și Implementare
- Utiliza utilitare de diagnostic (`ping`, `netstat`, `nslookup`, `nc`, `tshark`)
- Configura și rula topologii simple în Mininet
- Captura și analiza trafic de rețea folosind filtre PCAP și display filters
- Implementa calcule de întârziere de transmisie (L/R) în Python
- Crea servere și clienți TCP/UDP folosind sockets sau netcat

### Nivel IV – Analiză și Evaluare
- Analiza structura unui cadru Ethernet și a unui pachet IPv4
- Compara Round-Trip Time (RTT) cu latența one-way
- Interpreta secvența TCP three-way handshake în capturile tshark
- Evalua impactul parametrilor de link (bandwidth, delay, loss) asupra performanței
- Diagnostica probleme de conectivitate pe baza output-urilor uneltelor de rețea

---

## De ce contează

Înțelegerea fundamentelor rețelelor reprezintă baza pentru orice programator modern. Indiferent dacă dezvolți aplicații web, servicii cloud, sisteme distribuite sau IoT, vei interacționa constant cu infrastructura de rețea.

**Pentru un viitor programator:**
- Debugging-ul eficient al aplicațiilor distribuite necesită înțelegerea comportamentului TCP/UDP
- Optimizarea performanței depinde de cunoașterea latențelor și bandwidth-ului
- Securitatea aplicațiilor presupune înțelegerea fluxului de date în rețea
- Arhitectura microserviciilor se bazează pe protocoale de comunicare fiabile
- Alegerea corectă între TCP și UDP poate face diferența între o aplicație responsive și una lentă
- Diagnosticarea problemelor de rețea economisește ore de debugging în producție

**Unde se aplică în practică:**
- API REST și comunicare HTTP/HTTPS
- WebSockets pentru aplicații real-time
- Containerizare și orchestrare (Docker, Kubernetes)
- Cloud computing (AWS, Azure, GCP)

---

## Structura Kit-ului

```
WEEK1/
├── README.md                          # Acest fișier
├── CHANGELOG.md                       # Istoric modificări
├── Makefile                           # Automatizări
│
├── scripts/                           # Scripturi automatizare
│   ├── setup.sh                       # Instalare dependențe
│   ├── run_all.sh                     # Demo automat → artifacts/
│   ├── cleanup.sh                     # Curățare mediu
│   ├── verify.sh                      # Verificare instalare
│   └── capture_demo.sh                # Generator capturi PCAP
│
├── tests/                             # Validare
│   ├── smoke_test.sh                  # Test artefacte demo
│   └── expected_outputs.md            # Documentație output-uri
│
├── artifacts/                         # Output-uri generate (gitignore)
│   ├── demo.log                       # Log execuție
│   ├── demo.pcap                      # Captură trafic
│   └── validation.txt                 # Rezultate validare
│
├── python/                            # Cod Python
│   ├── exercises/                     # Exerciții practice
│   │   ├── ex_1_01_ping_latency.py
│   │   ├── ex_1_02_tcp_server_client.py
│   │   ├── ex_1_03_parse_csv.py
│   │   └── ex_1_04_pcap_stats.py
│   └── utils/                         # Utilitare comune
│       └── net_utils.py               # Constante, helpers
│
├── mininet/                           # Topologii simulate
│   ├── topologies/
│   │   └── topo_simple.py             # Topologie 3 host-uri
│   └── scenarios/                     # Scenarii documentate
│
├── seminar/                           # Materiale seminar
│   ├── scenarios/                     # Ghiduri pas cu pas
│   │   ├── s1_01_basic_tools.md
│   │   ├── s1_02_netcat_tcp.md
│   │   └── s1_03_wireshark_analysis.md
│   └── tasks/
│       └── livrabile_S1.md            # Cerințe livrabil
│
├── docs/                              # Documentație auxiliară
│   ├── cli_cheatsheet.md              # Referință rapidă comenzi
│   ├── checklist.md
│   ├── curs.md
│   ├── rubrici.md
│   └── seminar.md
│
├── pcap/                              # Capturi exemplu
│   └── README.md
│
├── slides/                            # Outline prezentări
│   ├── curs_slides_outline.txt
│   └── seminar_slides_outline.txt
│
└── docker/                            # Container alternativ
    ├── Dockerfile
    └── docker-compose.yml
```

**Plan IP Week 1:** `10.0.1.0/24` | Gateway: `10.0.1.1` | Hosts: `.11-.13` | Server: `.100`

**Porturi standard:** TCP=9090, UDP=9091, HTTP=8080, Custom=5100-5199

---

## Cerințe de Mediu

### Sistem de Operare
- **Linux** (recomandat: Debian 12 / Ubuntu 22.04+ Server)
- VM în VirtualBox/VMware cu minim **2 GB RAM**, **10 GB disk**
- Acces `sudo` (Mininet și capturile necesită privilegii root)
- **Alternativă:** Docker pentru medii non-Linux

### Pachete Software

| Pachet | Scop | Verificare |
|--------|------|------------|
| `python3` (3.10+) | Exerciții și scripturi | `python3 --version` |
| `mininet` | Simulare rețele | `mn --version` |
| `openvswitch-switch` | Switch virtual | `ovs-vsctl --version` |
| `tshark` | Captură și analiză CLI | `tshark -v` |
| `tcpdump` | Captură alternativă | `tcpdump --version` |
| `netcat-openbsd` | Generator trafic | `nc -h` |
| `iproute2` | Utilitare IP moderne | `ip -V` |
| `make` | Automatizare | `make --version` |

### Resurse minime VM
- **CPU:** 1 core (2 recomandat)
- **RAM:** 2 GB (4 GB recomandat pentru Docker)
- **Disk:** 10 GB
- **Rețea:** NAT sau Bridge pentru acces Internet

---

## 🚀 Pornire Rapidă (10 comenzi)

```bash
# 1. Dezarhivare și intrare în director
unzip WEEK1.zip && cd WEEK1

# 2. Instalare dependențe (o singură dată)
sudo bash scripts/setup.sh

# 3. Verificare instalare
bash scripts/verify.sh

# 4. Rulare demo automat (generează artifacts/)
bash scripts/run_all.sh

# 5. Validare artefacte
bash tests/smoke_test.sh

# 6. Examinare captură
tshark -r artifacts/demo.pcap | head -20

# 7. Cleanup când termini
bash scripts/cleanup.sh
```

### Verificare rapidă
```bash
ls artifacts/          # Trebuie: demo.log, demo.pcap, validation.txt
cat artifacts/validation.txt | grep PASS  # Minim 5 linii PASS
```

### Variante alternative
```bash
# Docker (fără Mininet)
cd docker && docker-compose up -d && docker exec -it netlab bash

# Makefile shortcuts
make setup && make demo && make verify
```

---

## Ghid Makefile

```bash
# Instalare și verificare
make setup              # Instalează dependențele
make verify             # Verifică instalarea
make check-python       # Verifică Python

# Demonstrații
make demo               # Demo complet
make demo-python        # Doar Python
make demo-mininet       # Doar Mininet (sudo)
make demo-capture       # Demo captură (sudo)

# Curățare
make clean              # Fișiere temporare
make clean-mininet      # Artefacte Mininet
make clean-outputs      # Director outputs/

# Docker
make docker-build       # Construiește imagine
make docker-run         # Pornește container
make docker-shell       # Acces container

# Documentație
make slides             # Deschide prezentarea
make help               # Ajutor complet
```

---

## Ghid Curs (Teorie)

### Structura Cursului 1: Fundamente ale Rețelelor

**Durată estimată:** 2 ore (prelegere + dialog)

| # | Temă | Durată | Concepte cheie |
|---|------|--------|----------------|
| 1 | Introducere și motivație | 15 min | Ce este o rețea, de ce contează |
| 2 | Clasificări ale rețelelor | 20 min | LAN, WAN, Internet |
| 3 | Topologii și componente | 25 min | Stea, inel, plasă; NIC, hub, switch, router |
| 4 | Medii de transmisie | 15 min | Cupru, fibră, wireless |
| 5 | Mecanisme de transmisie | 20 min | Circuit vs pachete, broadcast vs unicast |
| 6 | Protocoale și încapsulare | 25 min | Protocol, stivă, PDU |
| 7 | Recapitulare | 10 min | Întrebări, pregătire seminar |

### Materiale disponibile
- `curs/C1_fundamente_retele.md` – Conținut complet
- `curs/slides/C1_slides_outline.md` – Structură prezentare
- `curs/assets/` – Diagrame și imagini

---

## Ghid Seminar (Practică)

### Structura Seminarului 1: Analiză de Rețea

**Durată estimată:** 2 ore (exerciții asistate)

| Etapă | Durată | Conținut | Fișier |
|-------|--------|----------|--------|
| 0. Setup | 10 min | Verificare mediu | - |
| 1. Utilitare bază | 25 min | ping, netstat, nslookup | `01_basic_tools.md` |
| 2. Netcat TCP/UDP | 35 min | Server/client | `02_netcat_tcp_udp.md` |
| 3. Captură tshark | 40 min | Filtre, export | `03_wireshark_tshark.md` |
| 4. Wrap-up | 10 min | Livrabil, întrebări | `livrabile_S1.md` |

### Rulare rapidă

```bash
# Demo complet
make demo

# Server TCP (Terminal 1)
nc -l -p 9100

# Client TCP (Terminal 2)
echo "Hello Network!" | nc localhost 9100

# Captură (Terminal 3)
sudo tshark -i lo -f "tcp port 9100" -a packets:10
```

---

## Ghid Laborator

Laboratorul extinde seminarul cu experimente controlate:

1. **Experiment RTT:** Măsurare ping pe diferite distanțe
2. **Experiment TCP vs UDP:** Observare handshake și datagrame
3. **Experiment Mininet:** Topologie cu degradare controlată
4. **Challenge:** Server HTTP minimal cu netcat

Detalii în `laborator/lab_guide.md`.

---

## 🐍 Exerciții Python

### Ex 1.01: Calcule de Întârziere (L/R)

```bash
python3 python/exercises/ex_1_01_transmission_delay.py
python3 python/exercises/ex_1_01_transmission_delay.py --self-test
```

### Ex 1.02: Sniffer Didactic

```bash
sudo python3 python/exercises/ex_1_02_sniffer_didactic.py --count 5
```

### Ex 1.03: Analizor ARP

```bash
sudo python3 python/exercises/ex_1_03_arp_analyzer.py --interface eth0 --count 10
```

### Ex 1.04: Demo TCP/UDP

```bash
python3 python/exercises/ex_1_04_tcp_udp_demo.py --mode tcp
python3 python/exercises/ex_1_04_tcp_udp_demo.py --mode udp
```

---

## 🌐 Mininet – Rețele Simulate

### Topologie de bază

```
h1 (10.0.0.1) ─── s1 ─── h2 (10.0.0.2)
```

```bash
sudo python3 mininet/topologies/topo_1_base.py --cli

mininet> net
mininet> h1 ping -c 3 h2
mininet> exit
```

### Topologie extinsă (cu degradare)

```bash
sudo python3 mininet/topologies/topo_1_extended.py --bw 10 --delay 50ms --loss 1
```

---

## Bibliografie

### Cărți principale
1. Kurose, J.F., Ross, K.W. (2021). *Computer Networking: A Top-Down Approach*, 8th Ed. Pearson.
2. Rhodes, B., Goerzen, J. (2014). *Foundations of Python Network Programming*, 3rd Ed. Apress.

### Standarde și specificații
- [RFC Index](https://www.rfc-editor.org/)
- [IEEE 802 Standards](https://www.ieee802.org/)
- [Wireshark Documentation](https://www.wireshark.org/docs/)
- [Mininet Walkthrough](http://mininet.org/walkthrough/)

---

*Revolvix&Hypotheticalandrei | ASE București / CSIE*  
*Licență: MIT | Versiune: 3.1 | Ianuarie 2026*
