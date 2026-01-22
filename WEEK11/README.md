# Săptămâna 11 – Starter Kit: Protocoale de Aplicație și Aplicații Distribuite

## 📋 Cuprins

- [Prezentare Generală](#prezentare-generală)
- [Structura Kit-ului](#structura-kit-ului)
- [Cerințe de Sistem](#cerințe-de-sistem)
- [Instalare Rapidă](#instalare-rapidă)
- [Ghid de Utilizare](#ghid-de-utilizare)
- [Troubleshooting](#troubleshooting)

---

## Prezentare Generală

### Ce vom învăța

**CURS 11 – Protocoale de Aplicație: FTP, DNS, SSH**
- Arhitectura și funcționarea FTP (control vs data, activ vs pasiv)
- DNS: rezoluție ierarhică, TTL, caching, DNSSEC
- SSH: autentificare, canale, port forwarding, automatizare

**SEMINAR 11 – Aplicații Distribuite cu Load Balancing**
- Reverse proxy: concept și implementare cu Nginx
- Algoritmi de load balancing: Round-Robin, Least Connections, IP Hash
- Orchestrare containere cu Docker Compose
- Implementare LB custom în Python

### De ce contează

Protocoalele FTP, DNS și SSH reprezintă fundamentele operaționale ale Internetului modern. Load balancing-ul și proxy-urile inverse sunt esențiale pentru scalabilitatea aplicațiilor web. Orice programator care lucrează cu sisteme distribuite folosește zilnic aceste concepte.

---

## Structura Kit-ului

```
starterkit/
├── README.md              # Acest fișier
├── Makefile               # Automatizare comenzi (make help)
├── requirements.txt       # Dependențe Python
│
├── scripts/               # Shell scripts pentru setup și demo-uri
│   ├── setup.sh           # Instalare dependențe
│   ├── cleanup.sh         # Curățare mediu
│   ├── verify.sh          # Verificare instalare
│   └── capture.sh         # Captură trafic
│
├── python/
│   ├── utils/
│   │   └── net_utils.py   # Utilitare rețea comune
│   └── exercises/
│       ├── ex_11_01_backend.py       # Server HTTP simplu
│       ├── ex_11_02_loadbalancer.py  # LB custom cu 3 algoritmi
│       ├── ex_11_03_dns_client.py    # Client DNS didactic
│       └── ex_11_04_ftp_client.py    # Client FTP demonstrativ
│
├── mininet/
│   ├── topologies/
│   │   ├── topo_11_base.py      # Topologie LB cu 3 backends
│   │   └── topo_11_extended.py  # Topologie cu failover
│   └── scenarios/
│       └── scenario_11_tasks.md # Sarcini Mininet
│
├── docker/
│   ├── nginx_compose/     # Stack Nginx + 3 backends
│   ├── custom_lb_compose/ # Stack LB Python custom
│   ├── ftp_demo/          # Demo FTP activ/pasiv
│   ├── dns_demo/          # Demo DNS TTL/caching
│   └── ssh_demo/          # Demo SSH provisioning
│
├── docs/
│   ├── curs.md            # Material curs complet
│   ├── seminar.md         # Material seminar complet
│   ├── lab.md             # Ghid laborator
│   ├── rubrici.md         # Criterii evaluare
│   ├── checklist.md       # Checklist cadru didactic
│   └── slide_outlines/    # Outline-uri pentru prezentări
│
├── teoria/                # Explicații teoretice detaliate
│   ├── 01_ftp_protocol.md
│   ├── 02_dns_protocol.md
│   ├── 03_ssh_protocol.md
│   ├── 04_reverse_proxy.md
│   └── 05_load_balancing.md
│
├── pcap/                  # Capturi exemplu
│   └── README.md
│
└── assets/                # Resurse vizuale
    └── logo.svg
```

---

## Cerințe de Sistem

### Mediu Recomandat
- **OS**: Ubuntu 22.04+ (VirtualBox VM CLI-only recomandat)
- **RAM**: minim 2GB (4GB pentru toate demo-urile simultan)
- **Disk**: 5GB liber
- **Rețea**: Acces Internet pentru pull imagini Docker

### Software Necesar

| Component | Versiune | Verificare |
|-----------|----------|------------|
| Python | 3.10+ | `python3 --version` |
| Docker | 24.0+ | `docker --version` |
| Docker Compose | 2.20+ | `docker compose version` |
| Mininet | 2.3+ | `mn --version` |
| Wireshark/tshark | 4.0+ | `tshark --version` |
| netcat | orice | `nc -h` |
| curl | orice | `curl --version` |

---

## Instalare Rapidă

```bash
# 1. Clonare / dezarhivare kit
cd /path/to/starterkit

# 2. Setup automat (necesită sudo)
make setup

# 3. Verificare instalare
make verify

# 4. Vedere comenzi disponibile
make help
```

### Instalare Manuală (dacă e necesar)

```bash
# Python deps
pip3 install --break-system-packages -r requirements.txt

# Mininet (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install -y mininet openvswitch-switch

# Docker (dacă nu e instalat)
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER
```

---

## Ghid de Utilizare

### Demo-uri Rapide

```bash
# Demo Nginx Load Balancer
make demo-nginx

# Demo Load Balancer custom Python
make demo-custom-lb

# Demo Mininet (necesită sudo)
make demo-mininet

# Demo DNS didactic
make demo-dns

# Toate demo-urile secvențial
make demo-all
```

### Exerciții Python Standalone

```bash
# Pornire 3 backends
make backends-start

# Pornire load balancer (round-robin)
make lb-start

# Testare
curl http://localhost:8080/
curl http://localhost:8080/
curl http://localhost:8080/

# Oprire
make backends-stop
make lb-stop
```

### Captură Trafic

```bash
# Captură pe portul 8080
make capture-traffic

# Sau manual cu tshark
tshark -i any -f "tcp port 8080" -c 20
```

### Benchmark

```bash
# Apache Bench (1000 req, 10 concurent)
make benchmark

# Heavy benchmark
make benchmark-heavy
```

---

## Troubleshooting

### Probleme Comune

#### "Permission denied" la Docker
```bash
sudo usermod -aG docker $USER
# Logout și login din nou
```

#### "Connection refused" la containere
```bash
# Verifică dacă containerele rulează
docker ps

# Restart stack
make clean
make demo-nginx
```

#### Mininet nu pornește
```bash
# Curățare stare anterioară
sudo mn -c

# Verificare OVS
sudo service openvswitch-switch restart
```

#### Port deja în uz
```bash
# Identificare proces
sudo lsof -i :8080

# Sau curățare completă
make clean
```

### Verificare Mediu

```bash
# Rulează toate verificările
make verify

# Output așteptat:
# [OK] Python 3.x
# [OK] Docker running
# [OK] Mininet available
# [OK] tshark available
```

---

## Legătura cu Proiectul de Echipă

### Artefact Incremental Săptămâna 11

Echipele trebuie să livreze:
1. **Arhitectură cu LB**: Diagrama topologiei cu reverse proxy
2. **Configurare Nginx**: `nginx.conf` funcțional pentru proiectul echipei
3. **Script de deployment**: Docker Compose pentru pornirea întregii stive

### Integrare în Proiect

Componentele acestei săptămâni se integrează astfel:
- Reverse proxy-ul devine punctul de intrare în aplicația echipei
- Load balancing-ul permite scalarea componentelor backend
- Cunoștințele DNS sunt utile pentru configurări custom de rețea

---

## Resurse Suplimentare

### Documentație Oficială
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Docker Compose Reference](https://docs.docker.com/compose/)
- [Mininet Walkthrough](http://mininet.org/walkthrough/)
- [RFC 959 - FTP](https://tools.ietf.org/html/rfc959)
- [RFC 1035 - DNS](https://tools.ietf.org/html/rfc1035)
- [RFC 4251 - SSH Architecture](https://tools.ietf.org/html/rfc4251)

### Bibliografie Curs
- Kurose & Ross, "Computer Networking: A Top-Down Approach", 8th Ed.
- Rhodes & Goetzen, "Foundations of Python Network Programming"

---

*Revolvix&Hypotheticalandrei*
