# Săptămâna 10: HTTP/HTTPS, REST, SOAP + Servicii de Rețea (DNS, SSH, FTP)

## Rețele de Calculatoare | ASE București | 2025-2026

---

### Ce vom învăța

**Curs 10 – Nivel Aplicație: Protocoale și Semantică**
- Comportamentul real al HTTP pe conexiuni TCP/TLS
- Semantica metodelor HTTP (idempotență, siguranță, cacheable)
- Coduri de status și nuanțele lor (401 vs 403, 404 vs 405)
- REST ca stil arhitectural și nivelurile Richardson
- SOAP: când și de ce încă mai contează
- WebSocket: când HTTP nu mai este suficient

**Seminar 10 – Servicii de Rețea în Docker**
- DNS implicit Docker vs server DNS custom
- SSH programatic cu Paramiko
- FTP automatizat cu pyftpdlib
- Port forwarding pentru acces la servicii interne
- Orchestrare servicii cu Docker Compose

### De ce contează

Majoritatea problemelor din aplicațiile web sunt probleme de protocol, nu de framework. Un programator care înțelege HTTP la nivel de pachete poate diagnostica rapid erori care altfel ar consuma ore. La fel, automatizarea cu SSH/FTP și înțelegerea DNS-ului sunt competențe esențiale în DevOps și administrare sisteme.

---

## Pornire rapidă

### Cerințe sistem

| Tool | Versiune minimă | Verificare |
|------|-----------------|------------|
| Python | 3.11+ | `python3 --version` |
| Docker | 24.0+ | `docker --version` |
| Docker Compose | 2.20+ | `docker compose version` |
| openssl | 1.1+ | `openssl version` |
| curl | 7.0+ | `curl --version` |
| dig | 9.0+ | `dig -v` |

**Opțional** (pentru laboratorul avansat):
- Mininet 2.3+ (`mn --version`)
- Wireshark/tshark (`tshark --version`)

### Instalare și rulare

```bash
# Clonare/dezarhivare
cd WEEK10

# Verificare mediu
make check

# Demo complet (Docker)
make demo

# Sau pas cu pas:
make docker-up        # Pornire servicii
make dns-test         # Test DNS
make ssh-test         # Test SSH + Paramiko
make ftp-test         # Test FTP
make docker-down      # Oprire servicii
```

### Demo automat cu artefacte (Standard)

```bash
# Demo complet non-interactiv
# Generează: artifacts/demo.log, artifacts/demo.pcap, artifacts/validation.txt
make run-all

# Verificare artefacte
make smoke-test
```

Artefactele generate:
- `artifacts/demo.log` - Log complet al execuției
- `artifacts/demo.pcap` - Captură trafic (dacă tshark disponibil)
- `artifacts/validation.txt` - Rezultate teste (PASS/FAIL)

---

## Structura kit-ului

```
WEEK10/
├── README.md                    # Acest fișier
├── CHANGELOG.md                 # Istoric modificări
├── Makefile                     # Automatizări (setup, demo, run-all, smoke-test)
├── requirements.txt             # Dependențe Python
│
├── scripts/                     # Shell scripts
│   ├── setup.sh                 # Instalare dependențe
│   ├── run_all.sh               # Demo automat (generează artifacts/)
│   ├── capture.sh               # Captură trafic tshark
│   ├── verify.sh                # Verificare mediu
│   └── cleanup.sh               # Curățare completă
│
├── tests/                       # Teste și validări
│   ├── smoke_test.sh            # Verificare artefacte
│   └── expected_outputs.md      # Documentație outputs așteptate
│
├── artifacts/                   # Artefacte generate (după run_all.sh)
│   ├── demo.log                 # Log execuție
│   ├── demo.pcap                # Captură trafic
│   └── validation.txt           # Rezultate teste
│
├── python/                      # Cod Python
│   ├── exercises/               # Exerciții gradate
│   │   ├── ex_10_01_https.py    # Server HTTPS demo
│   │   └── ex_10_02_rest_levels.py  # REST maturity levels
│   ├── apps/                    # Servere demo
│   └── utils/                   # Utilitare
│       └── net_utils.py         # Helpers (timing, parsing, DNS)
│
├── docker/                      # Docker infrastructure
│   ├── docker-compose.yml       # Orchestrare servicii
│   ├── dns-server/              # Imagine DNS (dnslib)
│   ├── ssh-server/              # Imagine SSH (OpenSSH)
│   ├── ssh-client/              # Imagine client Paramiko
│   ├── ftp-server/              # Imagine FTP (pyftpdlib)
│   └── debug/                   # Container cu unelte
│
├── mininet/                     # Topologii Mininet (opțional)
│   ├── topologies/
│   │   ├── topo_10_base.py      # Topologie de bază
│   │   └── topo_10_services.py  # Topologie cu servicii
│   └── scenarios/
│       └── scenario_10_tasks.md # Exerciții Mininet
│
├── pcap/                        # Capturi de pachete
│   └── README.md                # Ghid capturi
│
├── docs/                        # Documentație Markdown
│   ├── curs.md                  # Note curs HTTP/REST/SOAP
│   ├── seminar.md               # Ghid seminar DNS/SSH/FTP
│   ├── lab.md                   # Pași laborator
│   ├── rubrici.md               # Criterii evaluare
│   ├── checklist.md             # Checklist cadru didactic
│   └── cheatsheet/
│       └── cli_week10.md        # Referință rapidă comenzi
│
├── slides/                      # Prezentări
│   ├── curs_slides_outline.txt
│   └── seminar_slides_outline.txt
│
├── assets/                      # Resurse vizuale
│   ├── css/
│   │   └── design-system.css    # Stil partajat
│   └── puml/
│       ├── fig-http-flow.puml   # Diagrame PlantUML
│       └── fig-rest-levels.puml
│
└── certs/                       # Certificate auto-generate
    ├── server.crt               # (generate automat)
    └── server.key
```

---

## Comenzi Makefile

| Comandă | Descriere |
|---------|-----------|
| `make help` | Afișează toate comenzile disponibile |
| `make check` | Verifică dependențele |
| `make setup` | Instalare completă |
| `make demo` | Demo complet (Docker + teste) |
| `make run-all` | **Demo automat** (generează artifacts/) |
| `make smoke-test` | Verificare artefacte generate |
| `make docker-up` | Pornește serviciile Docker |
| `make docker-down` | Oprește serviciile |
| `make docker-debug` | Intră în containerul debug |
| `make dns-test` | Testează DNS |
| `make ssh-test` | Testează SSH + Paramiko |
| `make ftp-test` | Testează FTP |
| `make https-test` | Testează server HTTPS local |
| `make capture` | Captură trafic tshark |
| `make verify` | Verificare completă |
| `make clean` | Curățare |
| `make reset` | Reset complet (șterge și volume) |

---

## Troubleshooting

### 1. Docker nu pornește serviciile

```bash
# Verificare Docker daemon
sudo systemctl status docker

# Permisiuni utilizator
sudo usermod -aG docker $USER
# (necesită re-login)

# Rebuild imagini
make docker-build
```

### 2. Port ocupat

```bash
# Verificare porturi
ss -tulpn | grep -E "(5353|2222|2121)"

# Kill proces pe port
sudo fuser -k 5353/udp
sudo fuser -k 2222/tcp
sudo fuser -k 2121/tcp
```

### 3. DNS nu răspunde

```bash
# Din containerul debug
docker compose exec debug dig @dns-server -p 5353 myservice.lab.local

# Verificare log-uri
docker compose logs dns-server

# Restart serviciu
docker compose restart dns-server
```

### 4. SSH connection refused

```bash
# Verificare sshd
docker compose exec ssh-server pgrep sshd

# Manual rebuild
docker compose build --no-cache ssh-server
docker compose up -d ssh-server

# Verificare log-uri
docker compose logs ssh-server
```

### 5. FTP connection timeout

```bash
# Verificare server
docker compose logs ftp-server

# Test banner
nc -v localhost 2121

# Verificare porturi PASV
ss -tulpn | grep -E "3000[0-9]"
```

### 6. Eroare "Permission denied" la scripturi

```bash
# Adăugare permisiuni execuție
chmod +x scripts/*.sh
chmod +x tests/*.sh
```

### 7. Artefacte lipsă după run_all

```bash
# Verificare director artifacts
ls -la artifacts/

# Rulare manuală cu output detaliat
bash -x scripts/run_all.sh

# Verificare structură
make smoke-test --structure-only
```

### 8. Captură PCAP goală

```bash
# tshark nu este instalat?
sudo apt install tshark

# Permisiuni insuficiente?
sudo setcap cap_net_raw+ep $(which tshark)

# Alternativ, folosiți tcpdump
sudo tcpdump -i any -w artifacts/manual.pcap
```

### 9. Container debug nu se conectează

```bash
# Verificare rețea Docker
docker network ls
docker network inspect docker_labnet

# Rebuild rețea
docker compose down
docker network prune
docker compose up -d
```

### 10. Python venv nu se activează

```bash
# Recreare venv
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Reset complet

```bash
# Reset tot (inclusiv volume Docker)
make reset

# Sau manual
cd docker && docker compose down -v
rm -rf .venv certs/*.crt certs/*.key artifacts/*
```

---

## Resurse minime recomandate

| Resursă | Minim | Recomandat |
|---------|-------|------------|
| CPU | 2 cores | 4 cores |
| RAM | 4 GB | 8 GB |
| Disk | 5 GB | 10 GB |
| Rețea | NAT | Bridge (pentru Mininet) |

---

## Licență și atribuire

Materiale create pentru disciplina **Rețele de Calculatoare**, ASE București.

© 2025 Colectivul Rețele de Calculatoare

---

<sub>Revolvix&Hypotheticalandrei</sub>
