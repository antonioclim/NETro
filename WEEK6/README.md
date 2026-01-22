# Starterkit Săptămâna 6 – Rețele de Calculatoare

## NAT/PAT, ARP, DHCP, NDP, ICMP & SDN (Software-Defined Networking)

**Disciplina:** Rețele de calculatoare  
**Program:** Informatică economică, ASE-CSIE  
**Săptămâna:** 6 (Semestrul 2, An III)  
**Anul universitar:** 2025-2026

---

## Prezentare generală

Acest kit integrează materialele teoretice și practice pentru **Cursul 6** (NAT/PAT, ARP, DHCP, NDP, ICMP) și **Seminarul 6** (SDN, topologii simulate, analiză trafic). Structura progresivă permite studenților să construiască cunoștințe solide înainte de aplicarea lor în exerciții practice simulate cu Mininet și controllere OpenFlow.

### Obiective de învățare

După parcurgerea acestui modul, studentul va fi capabil să:

**Cunoștințe fundamentale:**
1. Recunoască și definească mecanismele de suport la nivelul rețea (NAT, ARP, DHCP, NDP, ICMP)
2. Explice de ce epuizarea IPv4 a condus la adoptarea NAT/PAT și compromisurile implicate

**Înțelegere conceptuală:**
3. Distingă între NAT static, NAT dinamic și PAT (NAT overload) – scop, mecanism, cazuri de utilizare
4. Înțeleagă separarea control plane/data plane în arhitectura SDN și implicațiile asupra flexibilității

**Aplicare practică:**
5. Aplice configurații de rutare statică într-o topologie simulată cu trei routere
6. Configureze NAT/MASQUERADE folosind iptables pe un router Linux

**Analiză:**
7. Analizeze traficul de rețea folosind instrumente CLI (tcpdump, tshark, ovs-ofctl)
8. Compare comportamentul traficului înainte și după aplicarea politicilor SDN

**Evaluare:**
9. Evalueze impactul politicilor SDN asupra conectivității (allow/block per protocol/port)
10. Aprecieze avantajele și limitările NAT/PAT în contexte reale

**Sinteză:**
11. Creeze aplicații client-server TCP/UDP pentru generare de trafic
12. Implementeze politici OpenFlow personalizate într-un controller SDN

---

## Structura kit-ului

```
starterkit_s6/
├── README.md                    # Acest fișier
├── CHANGELOG.md                 # Istoric modificări
├── Makefile                     # Automatizări principale
├── requirements.txt             # Dependențe Python
│
├── artifacts/                   # Artefacte generate (demo.log, demo.pcap, validation.txt)
│
├── python/                      # Utilități Python comune
│   └── utils/                   # Modul shared utilities
│       ├── __init__.py
│       └── network_utils.py     # Constante IP/porturi, helpers
│
├── seminar/                     # Materiale practice pentru seminar
│   ├── mininet/topologies/      # Fișiere topologie Mininet
│   │   ├── topo_nat.py          # Rețea privată + NAT router
│   │   └── topo_sdn.py          # Topologie SDN cu OpenFlow switch
│   └── python/                  # Cod Python
│       ├── apps/                # Aplicații TCP/UDP pentru trafic
│       │   ├── nat_observer.py  # Observare traducere NAT
│       │   ├── tcp_echo.py      # Echo server/client TCP (port 9090)
│       │   └── udp_echo.py      # Echo server/client UDP (port 9091)
│       ├── controllers/         # Controller SDN (OS-Ken)
│       │   └── sdn_policy_controller.py
│       └── exercises/           # Template-uri exerciții studenți
│
├── scripts/                     # Scripturi de automatizare
│   ├── setup.sh                 # Instalare completă dependențe
│   ├── cleanup.sh               # Curățare artefacte și procese
│   ├── run_all.sh               # Demo automat → artifacts/
│   ├── run_nat_demo.sh          # Lansare demo NAT
│   └── run_sdn_demo.sh          # Lansare demo SDN
│
├── docker/                      # Suport Docker
│   └── Dockerfile               # Container cu toate dependențele
│
├── pcap/                        # Capturi de pachete
│
├── docs/                        # Documentație și markdown sursă
│   ├── curs.md                  # Conținut teoretic complet
│   ├── seminar.md               # Ghid seminar
│   ├── lab.md                   # Laborator pas cu pas
│   ├── checklist.md             # Checklist cadru didactic
│   └── rubrici.md               # Criterii evaluare
│
├── slides/                      # Prezentări (outline-uri)
│
└── tests/                       # Verificări automate
    ├── smoke_test.sh            # Test de bază funcționalitate
    └── expected_outputs.md      # Referință pentru output corect
```

---

## Cerințe tehnice

### Mediu de lucru recomandat
- **SO:** Linux (Ubuntu 22.04+ sau Debian 12+)
- **Variante:** VM VirtualBox, WSL2 cu Ubuntu, container Docker
- **Python:** 3.10+ (compatibil 3.8+ pentru OS-Ken)
- **Privilegii:** sudo necesar pentru Mininet și captură de pachete

### Pachete sistem necesare
```bash
# Instalare unică
sudo apt-get update && sudo apt-get install -y \
  python3 python3-pip python3-venv \
  mininet openvswitch-switch \
  iproute2 iputils-ping traceroute \
  tcpdump tshark iptables \
  netcat-openbsd arping bridge-utils
```

### Pachete Python
```bash
pip install --break-system-packages os-ken scapy
```

---

## Instalare rapidă

### Quickstart (10 comenzi)

```bash
# 1. Extrage și navighează
cd starterkit_s6

# 2. Setup (prima dată)
make setup

# 3. Verifică uneltele
make check

# 4. Demo automat (produce artifacts/)
sudo make run-all

# 5. Verifică artefactele
ls -la artifacts/
cat artifacts/validation.txt

# 6. Demo NAT interactiv
make nat-demo

# 7. Demo SDN interactiv
make sdn-demo

# 8. Rulează smoke test
make smoke-test

# 9. Curățare
make clean

# 10. Reset complet
make reset
```

### Plan IP Week 6

| Resursă | Adresă |
|---------|--------|
| Subnet SDN | 10.0.6.0/24 |
| Gateway | 10.0.6.1 |
| h1 | 10.0.6.11 |
| h2 | 10.0.6.12 |
| h3 | 10.0.6.13 |
| Server | 10.0.6.100 |

### Plan porturi

| Port | Utilizare |
|------|-----------|
| 9090 | TCP App (echo server/client) |
| 9091 | UDP App (echo server/client) |
| 6633 | Controller SDN (OpenFlow) |
| 5600-5699 | Porturi custom Week 6 |

### Varianta 1: Makefile (recomandat)
```bash
# Extrage kit-ul și intră în director
cd starterkit_s6

# Rulează setup complet
make setup

# Verificare
make check
```

### Varianta 2: Manual
```bash
cd starterkit_s6

# Instalare pachete sistem
sudo apt-get install -y python3 python3-pip mininet openvswitch-switch tcpdump tshark

# Instalare pachete Python
pip3 install --break-system-packages os-ken scapy

# Verificare
make check
```

---

## Flux de lucru recomandat

### Pentru Curs (100 minute)

| Segment | Durată | Conținut |
|---------|--------|----------|
| Context & IPv4 | 15 min | Epuizarea adreselor, RFC1918, problema globală |
| NAT/PAT | 30 min | Static vs. dinamic vs. PAT, tabele, compromisuri |
| ARP / Proxy ARP | 15 min | Rezoluție IP→MAC, broadcast vs. unicast |
| DHCP | 15 min | Pașii DORA, lease, relay |
| NDP (IPv6) | 15 min | Neighbor/Router Discovery, SLAAC |
| ICMP | 10 min | Ping, traceroute, mesaje de eroare |

### Pentru Seminar (100 minute)

| Segment | Durată | Conținut |
|---------|--------|----------|
| Warm-up verificare | 15 min | Check mediu, rutare de bază |
| NAT/PAT | 40 min | Topologie NAT, observare MASQUERADE |
| SDN & OpenFlow | 35 min | Controller, politici, flow tables |
| Reflecție | 10 min | Livrabile, întrebări |

### Comenzi rapide demo

```bash
# Demo NAT
make nat-demo

# Demo SDN (pornește controller automat)
make sdn-demo

# Verificare status controller
make controller-status

# Curățare
make clean
```

---

## Livrabile studenți

| Livrabil | Pondere | Descriere |
|----------|---------|-----------|
| `nat_output.txt` | 30% | Output comenzi + observații PAT |
| `sdn_output.txt` | 40% | Flow table dumps + analiză control/data plane |
| `reflectie.txt` | 20% | Principii end-to-end, comparație SDN vs. tradițional |
| `routing_output.txt` | 10% bonus | Traceroute înainte/după modificare rute |

---

## Troubleshooting rapid

| Problemă | Cauză probabilă | Soluție |
|----------|-----------------|---------|
| `mn: command not found` | Mininet neinstalat | `sudo apt install mininet` |
| OVS nu pornește | Serviciu oprit | `sudo systemctl restart openvswitch-switch` |
| Controller nu se conectează | Port blocat/alt proces | Verifică portul 6633: `ss -ltn \| grep 6633` |
| Ping SDN foarte lent | Lipsă flow-uri | Verifică cu `ovs-ofctl dump-flows` |
| NAT nu funcționează | IP forwarding dezactivat | `sysctl -w net.ipv4.ip_forward=1` |
| Permission denied tcpdump | Lipsă privilegii | Folosește `sudo` |
| Artefacte din rulări anterioare | Interfețe/procese rămase | `make clean` sau `sudo mn -c` |
| `os_ken` import fail | Modul neinstalat | `pip install os-ken` |

---

## Referințe bibliografice

1. **Kurose, J., Ross, K.** (2016). *Computer Networking: A Top-Down Approach*, 7th Edition. Pearson.
2. **Rhodes, B., Goetzen, J.** (2014). *Foundations of Python Network Programming*. Apress.
3. **RFC 1918** – Address Allocation for Private Internets
4. **RFC 5737** – IPv4 Address Blocks Reserved for Documentation
5. **RFC 4861** – Neighbor Discovery for IP version 6 (IPv6)
6. **OpenFlow Specification 1.3** – Open Networking Foundation

---

## Legături utile

- [Mininet Walkthrough](http://mininet.org/walkthrough/)
- [OS-Ken Documentation](https://osrg.github.io/os-ken/)
- [Open vSwitch Manual](https://docs.openvswitch.org/)
- [Wireshark Display Filter Reference](https://www.wireshark.org/docs/dfref/)

---

## Licență și utilizare

Material didactic pentru uz intern ASE-CSIE.  
Autori materiale: **Revolvix&Hypotheticalandrei**

---

*Generat pentru anul universitar 2025-2026 – Săptămâna 6*
