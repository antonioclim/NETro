# Starterkit Săptămâna 5 – Nivelul Rețea: Adresare IP

## Kit Complet pentru Curs + Seminar + Laborator

**Disciplina:** Rețele de Calculatoare  
**Instituție:** Academia de Studii Economice din București – CSIE  
**Versiune:** 3.0 Ultimate  
**Actualizat:** Decembrie 2025

---

## Ce vei ști după săptămâna asta

1. **Identifici** rolul și funcțiile nivelului rețea în modelele OSI și TCP/IP
2. **Explici** diferențele între adresarea MAC (L2) și IP (L3)
3. **Recunoști** câmpurile din antetele IPv4 și IPv6
4. **Calculezi** manual și programatic: adresa de rețea, broadcast, interval hosturi
5. **Aplici** tehnici de subnetting FLSM și VLSM pentru scenarii reale
6. **Configurezi** o infrastructură multi-subnet cu rutare statică

## De ce contează

Layer 3 e locul unde se ia decizia: pachetul ăsta încotro merge? Fără subnetting corect, pachetele se rătăcesc sau ajung unde nu trebuie. 

Fără înțelegerea adresării IP, configurarea rețelelor enterprise, depanarea problemelor de conectivitate și proiectarea infrastructurilor scalabile devin imposibile. Aceste competențe sunt esențiale pentru orice inginer de rețea, administrator de sistem sau dezvoltator de aplicații distribuite.

---

## Structura Kit-ului

```
starterkit_s5/
├── README.md                           # Acest fișier
├── Makefile                            # Automatizare completă
├── requirements.txt                    # Dependențe Python (minimale)
│
├── artifacts/                          # Artefacte generate
│   ├── demo.log                        # Log demo automat
│   ├── demo.pcap                       # Captură pachete
│   └── validation.txt                  # Raport validare
│
├── docs/
│   ├── cheatsheet.md                   # Referință rapidă CLI
│   ├── peer_instruction_week5.md       # Întrebări pentru discuții în grup
│   ├── exercitii_variate_week5.md      # Parsons, trace, debugging
│   ├── curs/
│   │   ├── curs.md                     # Note de curs complete
│   │   └── checklist.md                # Checklist cadru didactic
│   ├── seminar/
│   │   └── seminar.md                  # Ghid seminar
│   └── lab/
│       └── lab.md                      # Ghid laborator Mininet
│
├── python/
│   ├── apps/
│   │   ├── subnet_calc.py              # Calculator subnetting
│   │   └── udp_echo.py                 # Server UDP demo
│   ├── exercises/
│   │   ├── ex_5_01_cidr_flsm.py        # Analiză CIDR + FLSM
│   │   ├── ex_5_02_vlsm_ipv6.py        # VLSM + utilitare IPv6
│   │   └── ex_5_03_quiz_generator.py   # Generator quiz interactiv
│   └── utils/
│       └── net_utils.py                # Funcții reutilizabile
│
├── mininet/
│   ├── topologies/
│   │   ├── topo_5_base.py              # 2 subrețele + 1 router
│   │   └── topo_5_extended.py          # VLSM + IPv6 opțional
│   └── scenarios/
│       └── (scenarii practice)
│
├── scripts/
│   ├── setup.sh                        # Instalare dependențe
│   ├── run_all.sh                      # Demo automat complet
│   ├── cleanup.sh                      # Curățare mediu
│   ├── capture.sh                      # Ghid captură pachete
│   └── verify.sh                       # Verificare configurare
│
├── tests/
│   ├── smoke_test.sh                   # Teste rapide validare
│   └── expected_outputs.md             # Output-uri așteptate
│
├── slides/
│   ├── curs_slides_outline.txt         # Outline pentru PowerPoint
│   └── seminar_slides_outline.txt      # Outline seminar
│
└── solutions/
    └── exercitii_solutii.md            # Soluții complete
```

---

## Cerințe Sistem

### Hardware Minim
- 2 vCPU, 2 GB RAM
- 5 GB spațiu disk

### Software Necesar

| Component | Versiune | Scop |
|-----------|----------|------|
| Python | >= 3.10 | Exerciții, scripturi |
| Mininet | >= 2.3.0 | Simulare rețea |
| Open vSwitch | >= 2.17 | Switch virtual |
| tcpdump/tshark | orice | Captură pachete |
| Make | >= 4.0 | Automatizare |

### Verificare Rapidă
```bash
python3 --version          # >= 3.10
mn --version               # Mininet instalat
sudo mn --test pingall     # Test conectivitate
tshark --version           # Captură pachete
make --version             # Automatizare
```

---

## Instalare Rapidă

```bash
# 1. Navigare în directorul kit-ului
cd starterkit_s5

# 2. Setup complet (cu sudo pentru Mininet)
make setup

# 3. Verificare instalare
make test

# 4. Rulare demo automat (generează artefacte)
make run-all

# 5. Sau demo-uri individuale
make demo
```

### Demo Automat cu Artefacte

```bash
# Rulează demo complet și generează:
# - artifacts/demo.log
# - artifacts/demo.pcap  
# - artifacts/validation.txt
./scripts/run_all.sh

# Validare artefacte
make test-artifacts
```

---

## Ghid de Utilizare

### Comenzi Rapide (Makefile)

```bash
# Ajutor
make help

# Demo complet Python
make demo

# Demo-uri individuale
make demo-cidr          # Analiză CIDR
make demo-flsm          # Subnetting FLSM
make demo-vlsm          # Alocare VLSM
make demo-ipv6          # Conversii IPv6

# Quiz interactiv
make quiz

# Laborator Mininet (necesită sudo)
sudo make mininet-base           # Topologie simplă
sudo make mininet-extended       # VLSM
sudo make mininet-extended-ipv6  # Cu dual-stack

# Curățare
make clean
make reset              # Clean + mininet-clean
```

### Exerciții Python

#### 1. Analiză CIDR

```bash
# Analizează o adresă cu prefix
python3 python/exercises/ex_5_01_cidr_flsm.py analyze 192.168.10.14/26

# Cu explicații detaliate
python3 python/exercises/ex_5_01_cidr_flsm.py analyze 192.168.10.14/26 --verbose

# Output JSON
python3 python/exercises/ex_5_01_cidr_flsm.py analyze 192.168.10.14/26 --json
```

#### 2. Subnetting FLSM

```bash
# Împarte rețeaua în 4 subrețele egale
python3 python/exercises/ex_5_01_cidr_flsm.py flsm 192.168.100.0/24 4

# Împarte în 8 subrețele
python3 python/exercises/ex_5_01_cidr_flsm.py flsm 10.0.0.0/24 8
```

#### 3. Alocare VLSM

```bash
# Alocă pentru 60, 20, 10, 2 hosturi
python3 python/exercises/ex_5_02_vlsm_ipv6.py vlsm 172.16.0.0/24 60 20 10 2

# Scenariul complex
python3 python/exercises/ex_5_02_vlsm_ipv6.py vlsm 10.10.0.0/22 200 100 50 25 10 2 2 2
```

#### 4. Utilitare IPv6

```bash
# Comprimare adresă
python3 python/exercises/ex_5_02_vlsm_ipv6.py ipv6 2001:0db8:0000:0000:0000:0000:0000:0001

# Generare subrețele /64
python3 python/exercises/ex_5_02_vlsm_ipv6.py ipv6-subnets 2001:db8:10::/48 64 10

# Referință tipuri
python3 python/exercises/ex_5_02_vlsm_ipv6.py ipv6-types
```

### Laborator Mininet

#### Topologie Bază (2 Subrețele)

```bash
# Pornire cu CLI interactiv
sudo python3 mininet/topologies/topo_5_base.py --cli
```

Arhitectură (Week 5):
```
    10.0.5.0/25              10.0.5.128/25
        |                        |
       h1 -------- r1 -------- h2
    .11    .1          .129    .140
```

Comenzi utile în CLI:
```text
mininet> nodes                    # Listare noduri
mininet> net                      # Vizualizare topologie
mininet> h1 ip addr               # Adrese h1
mininet> h1 ip route              # Tabela rutare h1
mininet> h1 ping -c 3 10.0.5.140  # Test conectivitate
mininet> r1 tcpdump -ni r1-eth0 icmp &  # Captură ICMP
```

#### Topologie Extinsă (VLSM + IPv6)

```bash
# Doar IPv4
sudo python3 mininet/topologies/topo_5_extended.py --cli

# Cu IPv6 activat
sudo python3 mininet/topologies/topo_5_extended.py --cli --ipv6
```

Arhitectură VLSM:
```
    10.0.5.0/26      10.0.5.64/27     10.0.5.96/30
    (62 hosturi)     (30 hosturi)     (2 hosturi)
        |                |                |
       h1 ───────── r1 ─────────── h2 ─── h3
    .11   .1       .65   .70      .97   .98
```

---

## Troubleshooting

| # | Problemă | Cauză | Soluție |
|---|----------|-------|---------|
| 1 | `sudo mn --test pingall` eșuează | Procese Mininet rămase | `sudo mn -c && sudo systemctl restart openvswitch-switch` |
| 2 | `RTNETLINK answers: File exists` | Interfețe rămase | `sudo mn -c` |
| 3 | Ping inter-subnet nu merge | Lipsă gateway sau IP forward | Verifică `ip route` și `sysctl net.ipv4.ip_forward` |
| 4 | Time-out complet (nici ARP) | Prefix greșit sau IP duplicat | Verifică `ip addr` pe toate nodurile |
| 5 | `tshark` fără permisiuni | User nu e în grupul wireshark | `sudo usermod -aG wireshark $USER` sau rulează cu `sudo` |
| 6 | Doar ARP în captură, fără ICMP | Gateway incorect | Verifică `defaultRoute` |
| 7 | IPv6 ping nu funcționează | Forwarding IPv6 dezactivat | `sysctl -w net.ipv6.conf.all.forwarding=1` |
| 8 | `No module named mininet` | Mininet neinstalat | `sudo apt-get install mininet` |

> **Truc:** Dacă Mininet rămâne blocat și `sudo mn -c` nu ajută, oprește complet OVS: `sudo systemctl stop openvswitch-switch`, așteaptă 5 secunde, apoi pornește-l din nou.

### Resetare Completă

```bash
make reset
# sau manual:
sudo mn -c
sudo systemctl restart openvswitch-switch
rm -f /tmp/*.pcap
```

---

## Flux de Lucru Recomandat

### Pentru Curs (2 ore)

| Timp | Activitate | Resurse |
|------|------------|---------|
| 0:00-0:45 | Prezentare teoretică | `docs/curs/curs.md` |
| 0:45-1:15 | Demonstrații live Python | `make demo` |
| 1:15-1:30 | Întrebări Peer Instruction | `docs/peer_instruction_week5.md` |
| 1:30-1:45 | Exerciții interactive | `make quiz` |
| 1:45-2:00 | Rezumat și preview seminar | - |

### Pentru Seminar (2 ore)

| Timp | Activitate | Resurse |
|------|------------|---------|
| 0:00-0:15 | Recapitulare teoretică | `docs/seminar/seminar.md` |
| 0:15-0:45 | Exerciții individuale CIDR/VLSM | Părțile A-C din seminar |
| 0:45-1:30 | Laborator Mininet ghidat | `docs/lab/lab.md` |
| 1:30-1:50 | Captură și analiză trafic | tcpdump/tshark în Mininet |
| 1:50-2:00 | Validare și întrebări | `solutions/exercitii_solutii.md` |

---

## Referințe Bibliografice

### Cărți Principale
1. Kurose, J., Ross, K. (2021). *Computer Networking: A Top-Down Approach*, 8th Ed. Pearson.
2. Rhodes, B., Goetzen, J. (2014). *Foundations of Python Network Programming*. Apress.

### RFC-uri Relevante
- RFC 791 – Internet Protocol (IPv4)
- RFC 8200 – Internet Protocol, Version 6 (IPv6)
- RFC 1918 – Address Allocation for Private Internets
- RFC 4291 – IP Version 6 Addressing Architecture

### Resurse Online
- Documentația Mininet: http://mininet.org/walkthrough/
- Subnet Calculator: https://www.subnet-calculator.com/

---

## Licență

Materiale educaționale pentru uz academic.  
© 2025 Academia de Studii Economice din București – CSIE  
Departamentul de Informatică și Cibernetică Economică
