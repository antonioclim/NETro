# Rețele de Calculatoare – Kituri de Laborator (SĂPTĂMÂNILE 1–14)

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![Mininet](https://img.shields.io/badge/Mininet-2.3.0-green?style=flat)](http://mininet.org)
[![Docker](https://img.shields.io/badge/Docker-24.0+-2496ED?style=flat&logo=docker&logoColor=white)](https://docker.com)
[![Ubuntu](https://img.shields.io/badge/Ubuntu-24.04_LTS-E95420?style=flat&logo=ubuntu&logoColor=white)](https://ubuntu.com)
[![Licență](https://img.shields.io/badge/Licență-MIT-yellow?style=flat)](LICENCE)

**Disciplină:** Rețele de Calculatoare (25.0205IF3.2-0003)  
**Program de studiu:** Informatică Economică, Anul III, Semestrul 2  
**Instituție:** Academia de Studii Economice din București (ASE), Facultatea de Cibernetică, Statistică și Informatică Economică (CSIE)  
**An universitar:** 2025–2026  

---

## 📋 Cuprins

- [Prezentare generală](#prezentare-generală)
- [Structura repository-ului](#structura-repository-ului)
- [Tematici săptămânale](#tematici-săptămânale)
- [Cerințe de sistem](#cerințe-de-sistem)
- [Pornire rapidă](#pornire-rapidă)
- [Clonare săptămâni individuale](#clonare-săptămâni-individuale)
- [Clonare repository complet](#clonare-repository-complet)
- [Statistici repository](#statistici-repository)
- [Plan de adresare IP](#plan-de-adresare-ip)
- [Tehnologii utilizate](#tehnologii-utilizate)
- [Autori și colaboratori](#autori-și-colaboratori)
- [Licență](#licență)
- [Anexă: Ghid de instalare Ubuntu Server](#anexă-ghid-de-instalare-ubuntu-server-2404-lts)

---

## Prezentare generală

Acest repository conține kituri complete pentru disciplina **Rețele de Calculatoare**, acoperind toate cele 14 săptămâni ale semestrului. Fiecare kit săptămânal oferă:

- **Conținut teoretic** în documente Markdown structurate
- **Exerciții practice Python** cu soluții
- **Medii Docker Compose** pentru demonstrații reproductibile
- **Topologii de rețea Mininet** pentru simulare
- **Scripturi de testare automată** pentru validare
- **Exemple de capturi de pachete** (fișiere PCAP)

Materialele sunt concepute pentru un mediu **VM Linux minimal doar CLI** (Ubuntu Server 24.04 LTS) rulând în VirtualBox și urmează o abordare progresivă de învățare de la concepte de bază ale rețelelor până la sisteme distribuite avansate.

---

## Structura repository-ului

```
netEN/
├── PREREQ/                    # Cerințe preliminare și configurare mediu
├── APPENDIX(week0)/           # Materiale suplimentare și referințe
│
├── WEEK1/                     # Fundamente ale rețelelor
├── WEEK2/                     # Modele OSI/TCP-IP și programare cu socket-uri
├── WEEK3/                     # UDP Broadcast/Multicast și tunelare TCP
├── WEEK4/                     # Nivelul fizic, legătură de date și protocoale personalizate
├── WEEK5/                     # Nivelul rețea: adresare IP și subnetare
├── WEEK6/                     # NAT/PAT, ARP, DHCP, NDP, ICMP și SDN
├── WEEK7/                     # Captură de pachete, filtrare și scanare defensivă
├── WEEK8/                     # Nivelul transport, server HTTP și reverse proxy
├── WEEK9/                     # Nivelurile sesiune/prezentare și protocoale de fișiere
├── WEEK10/                    # HTTP/HTTPS, REST, SOAP și servicii de rețea
├── WEEK11/                    # Protocoale aplicație și aplicații distribuite
├── WEEK12/                    # Protocoale e-mail și Remote Procedure Call (RPC)
├── WEEK13/                    # IoT și securitate în rețele
├── WEEK14/                    # Recapitulare integrată și evaluare proiect
│
└── README.md                  # Acest fișier
```

### Structura standard a kitului săptămânal

Fiecare director `WEEK<N>/` urmează o organizare consistentă:

```
WEEK<N>/
├── README.md              # Prezentare săptămână și ghid de pornire rapidă
├── Makefile               # Automatizare build (make setup, make demo, make clean)
├── requirements.txt       # Dependențe Python
│
├── docs/                  # Documentație
│   ├── seminar.md         # Ghid seminar
│   ├── checklist.md       # Lista de verificare cadru didactic
│   └── cheatsheet.md      # Referință rapidă comenzi
│
├── python/                # Cod sursă Python
│   ├── exercises/         # Exerciții practice
│   ├── apps/              # Aplicații complete
│   ├── utils/             # Module utilitare
│   └── templates/         # Șabloane de cod pentru studenți
│
├── mininet/               # Simulare rețea
│   ├── topologies/        # Definiții topologii Mininet
│   └── scenarios/         # Scripturi scenarii laborator
│
├── docker/                # Containerizare
│   ├── Dockerfile         # Definiție imagine container
│   └── docker-compose.yml # Orchestrare multi-container
│
├── scripts/               # Scripturi de automatizare
│   ├── setup.sh           # Configurare mediu
│   ├── run_all.sh         # Execuție toate demonstrațiile
│   ├── cleanup.sh         # Curățare fișiere generate
│   └── capture_traffic.sh # Automatizare captură pachete
│
├── tests/                 # Testare automată
│   ├── smoke_test.sh      # Validare rapidă
│   └── expected_outputs.md# Referință rezultate așteptate
│
├── configs/               # Fișiere de configurare
├── artifacts/             # Rezultate generate (log-uri, capturi)
└── pcap/                  # Fișiere captură pachete
```

---

## Tematici săptămânale

| Săpt. | Temă | Tehnologii cheie |
|:-----:|------|------------------|
| **1** | Fundamente ale rețelelor: concepte, componente și clasificări | `ping`, `traceroute`, `netstat`, `ss`, `tcpdump` |
| **2** | Modele arhitecturale OSI/TCP-IP și programare cu socket-uri | Socket-uri Python, `scapy`, `dpkt`, servere concurente |
| **3** | UDP Broadcast/Multicast și tunelare TCP | Socket-uri UDP, grupuri multicast, port forwarding |
| **4** | Nivelul fizic, legătură de date și protocoale personalizate | Protocoale binare, `struct`, CRC32, cadre Ethernet |
| **5** | Nivelul rețea: adresare IP și subnetare | CIDR, FLSM, VLSM, IPv6, calculatoare de subrețele |
| **6** | NAT/PAT, ARP, DHCP, NDP, ICMP și SDN | `iptables`, Open vSwitch, controller `os-ken` |
| **7** | Captură de pachete, filtrare și scanare defensivă | `tcpdump`, `tshark`, Wireshark, `nmap`, `scapy` |
| **8** | Nivelul transport, server HTTP și reverse proxy | Handshake TCP, HTTP/1.1, Nginx, load balancing |
| **9** | Nivelurile sesiune/prezentare și protocoale de fișiere | FTP activ/pasiv, `pyftpdlib`, încadrare binară |
| **10** | HTTP/HTTPS, REST, SOAP și servicii de rețea | TLS, DNS, SSH (`paramiko`), niveluri API REST |
| **11** | Protocoale aplicație și aplicații distribuite | Cache DNS, algoritmi LB Nginx, verificări de sănătate |
| **12** | Protocoale e-mail și Remote Procedure Call (RPC) | SMTP, POP3, IMAP, JSON-RPC, XML-RPC, gRPC |
| **13** | IoT și securitate în rețele | MQTT (`paho`), Mosquitto, scanare vulnerabilități |
| **14** | Recapitulare integrată și evaluare proiect | Integrare full-stack, metodologie de depanare |

---

## Cerințe de sistem

### Hardware minim

| Componentă | Minim | Recomandat |
|------------|-------|------------|
| RAM | 4 GB | 8 GB |
| Nuclee CPU | 2 | 4 |
| Spațiu disc | 25 GB | 50 GB |
| Rețea | NAT + Host-Only | NAT + Host-Only |

### Cerințe software

| Software | Versiune | Scop |
|----------|----------|------|
| **Ubuntu Server** | 24.04 LTS | Sistem de operare gazdă |
| **Python** | 3.10+ | Limbaj de programare |
| **Docker CE** | 24.0+ | Containerizare |
| **Mininet** | 2.3.0+ | Simulare rețea |
| **Open vSwitch** | 3.1+ | Rețele definite prin software |
| **Git** | 2.40+ | Control versiuni |

### Setări recomandate VirtualBox

- **Tip:** Linux / Ubuntu (64-bit)
- **RAM:** 4096–8192 MB
- **CPU:** 4 nuclee cu PAE/NX și VT-x/AMD-V activate
- **Disc:** 25–50 GB alocat dinamic VDI
- **Adaptor rețea 1:** NAT (acces internet)
- **Adaptor rețea 2:** Host-Only Adapter (SSH de pe gazdă)

---

## Pornire rapidă

### Opțiunea 1: Clonare repository complet

```bash
# Clonează repository-ul complet
git clone https://github.com/antonioclim/netEN.git

# Navighează la săptămâna dorită
cd netEN/WEEK1

# Rulează setup și demo
make setup
make demo
```

### Opțiunea 2: Clonare săptămână specifică (Sparse Checkout)

```bash
# Exemplu: Clonează doar WEEK3
cd ~ && git clone --filter=blob:none --sparse https://github.com/antonioclim/netEN.git WEEK3 \
  && cd WEEK3 && git sparse-checkout set WEEK3 \
  && shopt -s dotglob && mv WEEK3/* . && rmdir WEEK3 \
  && find . -type f \( -name "*.sh" -o -name "*.py" \) -exec chmod +x {} \;
```

### Opțiunea 3: Descărcare arhivă ZIP

Descarcă săptămâni individuale din interfața web GitHub sau folosește:

```bash
# Descarcă și extrage săptămâna specifică
wget https://github.com/antonioclim/netEN/archive/refs/heads/main.zip
unzip main.zip
mv netEN-main/WEEK5 ~/WEEK5
```

---

## Clonare săptămâni individuale

Fiecare săptămână poate fi clonată independent folosind Git sparse checkout. Înlocuiește `<N>` cu numărul săptămânii (1–14):

### Comandă într-o singură linie

```bash
cd ~ && git clone --filter=blob:none --sparse https://github.com/antonioclim/netEN.git WEEK<N> \
  && cd WEEK<N> && git sparse-checkout set WEEK<N> \
  && shopt -s dotglob && mv WEEK<N>/* . && rmdir WEEK<N> \
  && find . -type f \( -name "*.sh" -o -name "*.py" \) -exec chmod +x {} \;
```

### Comenzi pas cu pas

```bash
# 1. Navighează la directorul home
cd ~

# 2. Clonează repository-ul cu sparse checkout (descarcă inițial doar metadate)
git clone --filter=blob:none --sparse https://github.com/antonioclim/netEN.git WEEK<N>

# 3. Intră în directorul clonat
cd WEEK<N>

# 4. Configurează sparse checkout pentru a prelua doar săptămâna dorită
git sparse-checkout set WEEK<N>

# 5. Aplatizează structura directoarelor
shopt -s dotglob
mv WEEK<N>/* .
rmdir WEEK<N>

# 6. Face scripturile executabile
find . -type f -name "*.sh" -exec chmod +x {} \;
find . -type f -name "*.py" -exec chmod +x {} \;

# 7. Verifică setup-ul
ls -la
./scripts/setup.sh
```

---

## Clonare repository complet

```bash
# Clonare completă cu istoric complet
git clone https://github.com/antonioclim/netEN.git
cd netEN

# Face toate scripturile executabile
find . -type f -name "*.sh" -exec chmod +x {} \;
find . -type f -name "*.py" -exec chmod +x {} \;

# Navighează la săptămâna specifică
cd WEEK1
make setup
make verify
make demo
```

---

## Statistici repository

| Metrică | Număr |
|---------|-------|
| **Kituri săptămânale** | 14 |
| **Fișiere Python** | 187 |
| **Scripturi Shell** | 88 |
| **Documente Markdown** | 146 |
| **Fișiere Docker Compose** | 21 |
| **Topologii Mininet** | 37 |
| **Dockerfile-uri** | 17 |
| **Dimensiune totală (necomprimată)** | ~5,2 MB |

### Distribuție pe limbaje

- **Python:** 55,2%
- **Shell:** 22,3%
- **JavaScript:** 7,9%
- **Makefile:** 7,4%
- **HTML:** 5,3%
- **CSS:** 1,0%
- **Dockerfile:** 0,9%

---

## Plan de adresare IP

Fiecare săptămână folosește o schemă consistentă de adresare IP derivată din numărul săptămânii pentru a evita conflictele:

| Săpt. | Rețea | Gateway | Interval gazde | Porturi |
|:-----:|-------|---------|----------------|---------|
| 1 | 10.0.1.0/24 | 10.0.1.1 | 10.0.1.2–254 | 5100–5199 |
| 2 | 10.0.2.0/24 | 10.0.2.1 | 10.0.2.2–254 | 5200–5299 |
| 3 | 10.0.3.0/24 | 10.0.3.1 | 10.0.3.2–254 | 5300–5399 |
| 4 | 10.0.4.0/24 | 10.0.4.1 | 10.0.4.2–254 | 5400–5499 |
| 5 | 10.0.5.0/24 | 10.0.5.1 | 10.0.5.2–254 | 5500–5599 |
| 6 | 10.0.6.0/24 | 10.0.6.1 | 10.0.6.2–254 | 5600–5699 |
| 7 | 10.0.7.0/24 | 10.0.7.1 | 10.0.7.2–254 | 5700–5799 |
| 8 | 10.0.8.0/24 | 10.0.8.1 | 10.0.8.2–254 | 8080, 9001–9003 |
| 9 | 10.0.9.0/24 | 10.0.9.1 | 10.0.9.2–254 | 2121, 60000–60100 |
| 10 | 10.0.10.0/24 | 10.0.10.1 | 10.0.10.2–254 | 5353, 2222 |
| 11 | 10.0.11.0/24 | 10.0.11.1 | 10.0.11.2–254 | 8080 |
| 12 | 10.0.12.0/24 | 10.0.12.1 | 10.0.12.2–254 | 1025, 8080, 50051 |
| 13 | 10.0.13.0/24 | 10.0.13.1 | 10.0.13.2–254 | 1883, 8080 |
| 14 | 172.20.0.0/24 | 172.20.0.1 | 172.20.0.2–254 | 8080, 9000 |

---

## Tehnologii utilizate

### Tehnologii de bază

| Tehnologie | Versiune | Scop |
|------------|----------|------|
| **Python** | 3.10+ | Limbaj principal de programare |
| **Mininet** | 2.3.0 | Emulare și simulare rețea |
| **Docker** | 24.0+ | Orchestrare containere |
| **Open vSwitch** | 3.1+ | Rețele definite prin software |
| **os-ken** | 2.4+ | Controller SDN (fork Ryu) |

### Biblioteci Python

| Bibliotecă | Scop |
|------------|------|
| `scapy` | Manipulare și analiză pachete |
| `dpkt` | Parsare pachete la nivel jos |
| `flask` | Framework server HTTP |
| `requests` | Bibliotecă client HTTP |
| `paramiko` | Implementare client SSH |
| `pyftpdlib` | Implementare server FTP |
| `dnslib` | Implementare protocol DNS |
| `dnspython` | Toolkit DNS |
| `paho-mqtt` | Client MQTT pentru IoT |
| `grpcio` | Framework gRPC |
| `protobuf` | Serializare Protocol Buffers |

### Instrumente de rețea

| Instrument | Scop |
|------------|------|
| `tcpdump` | Captură pachete (CLI) |
| `tshark` | Interfață CLI Wireshark |
| `nmap` | Scanare și enumerare rețea |
| `netcat` | Utilitar TCP/UDP |
| `iperf3` | Testare performanță rețea |
| `curl` | Client HTTP |
| `dig` | Utilitar interogare DNS |

---

## Autori și colaboratori

### Materiale de curs

- **Conf. univ. dr. TOMA Andrei** – Coordonator curs
- **Conf. univ. dr. TIMOFTE Carmen Manuela** – Titular curs
- **Lect. univ. dr. ILIE-NEMEDI Iulian** – Coordonator laborator
- **Asist. univ. drd. CÎMPEANU Ionuț Alexandru** – Asistent laborator

### Dezvoltare cod

- **Revolvix** – Dezvoltare kit-uri și automatizare
- **Hypotheticalandrei** – Medii Docker și testare

---

## Licență

Acest repository este licențiat sub **Licența MIT** pentru componentele de cod. Materialele educaționale rămân proprietatea intelectuală a ASE-CSIE și a cadrelor didactice.

```
Licența MIT

Copyright (c) 2025 ASE-CSIE Cursul de Rețele de Calculatoare

Prin prezenta se acordă gratuit permisiunea oricărei persoane care obține o copie
a acestui software și a fișierelor de documentație asociate („Software"), de a
utiliza Software-ul fără restricții, inclusiv, fără limitare, drepturile de a
folosi, copia, modifica, îmbina, publica, distribui, sublicenția și/sau vinde
copii ale Software-ului și de a permite persoanelor cărora le este furnizat
Software-ul să facă același lucru, sub rezerva următoarelor condiții:

Avizul de copyright de mai sus și această notificare de permisiune vor fi incluse
în toate copiile sau porțiunile substanțiale ale Software-ului.

SOFTWARE-UL ESTE FURNIZAT „CA ATARE", FĂRĂ GARANȚIE DE NICIUN FEL, EXPRESĂ SAU
IMPLICITĂ, INCLUSIV, DAR FĂRĂ A SE LIMITA LA, GARANȚIILE DE VANDABILITATE,
ADECVARE PENTRU UN ANUMIT SCOP ȘI NEÎNCĂLCARE. ÎN NICIUN CAZ AUTORII SAU
DEȚINĂTORII DREPTURILOR DE AUTOR NU VOR FI RĂSPUNZĂTORI PENTRU NICIO PRETENȚIE,
DAUNE SAU ALTĂ RĂSPUNDERE, FIE ÎN ACȚIUNE CONTRACTUALĂ, DELICTUALĂ SAU ALTFEL,
CARE DECURGE DIN, DIN SAU ÎN LEGĂTURĂ CU SOFTWARE-UL SAU UTILIZAREA SAU ALTE
TRANZACȚII ÎN SOFTWARE.
```

---

## Depanare

### Probleme frecvente

| Problemă | Soluție |
|----------|---------|
| Permisiune refuzată la rularea scripturilor | `chmod +x scripts/*.sh` |
| Permisiune Docker refuzată | `sudo usermod -aG docker $USER` apoi logout/login |
| Mininet nu pornește | `sudo mn -c` pentru a curăța rulările anterioare |
| Modul Python negăsit | `pip install -r requirements.txt --break-system-packages` |
| Port deja în uz | `sudo ss -tulpn | grep <port>` apoi oprește procesul |
| Permisiune TShark refuzată | `sudo usermod -aG wireshark $USER` |

### Comenzi utile

```bash
# Curăță starea Mininet
sudo mn -c

# Elimină toate containerele și imaginile Docker
docker system prune -a --volumes

# Golește cache-ul pip
pip cache purge

# Verifică porturile deschise
sudo ss -tulpn

# Vizualizează log-urile de sistem
journalctl -xe --no-pager | tail -50

# Monitorizează interfețele de rețea
watch -n 1 'ip -s link'
```

---

## Contact și suport

- **Probleme repository:** [https://github.com/antonioclim/netEN/issues](https://github.com/antonioclim/netEN/issues)
- **Platforma cursului:** ASE CSIE e-Learning
- **Cadre didactice:** Contact prin e-mail universitar

---

# Anexă: Ghid de instalare Ubuntu Server 24.04 LTS

## Ghid complet de instalare pentru laboratorul de Rețele de Calculatoare

**Mediu țintă:** Ubuntu Server 24.04 LTS (doar CLI) ca guest VirtualBox  
**Scop:** Pregătirea unui laborator de rețele complet funcțional pentru SĂPTĂMÂNILE 1–14  
**Generat:** Ianuarie 2026

---

## Cuprins

1. [Configurare inițială VirtualBox](#1-configurare-inițială-virtualbox)
2. [Actualizare sistem și pachete esențiale](#2-actualizare-sistem-și-pachete-esențiale)
3. [Instrumente de rețea](#3-instrumente-de-rețea)
4. [Python și biblioteci](#4-python-și-biblioteci)
5. [Docker și Docker Compose](#5-docker-și-docker-compose)
6. [Mininet și Open vSwitch](#6-mininet-și-open-vswitch)
7. [Wireshark/TShark](#7-wiresharktshark)
8. [Configurări suplimentare](#8-configurări-suplimentare)
9. [Transfer și organizare materiale](#9-transfer-și-organizare-materiale)
10. [Script de verificare](#10-script-de-verificare)
11. [Depanare](#11-depanare)

---

## 1. Configurare inițială VirtualBox

### 1.1 Setări mașină virtuală

Creează o nouă VM cu următoarea configurație:

| Setare | Valoare |
|--------|---------|
| **Nume** | Ubuntu-Networks |
| **Tip** | Linux |
| **Versiune** | Ubuntu (64-bit) |
| **RAM** | 4096–8192 MB |
| **CPU** | 4 nuclee |
| **Disc** | 25–50 GB (alocat dinamic) |

### 1.2 Adaptoare de rețea

Configurează două adaptoare de rețea:

**Adaptor 1 (NAT):**
- Atașat la: NAT
- Scop: Acces internet pentru instalarea pachetelor

**Adaptor 2 (Host-Only):**
- Atașat la: Host-Only Adapter
- Nume: vboxnet0 (creează dacă este necesar)
- IP: interval 192.168.56.x

### 1.3 Activare virtualizare nested (opțional)

Necesară pentru rularea VM-urilor nested sau scenarii avansate cu containere:

```bash
# PowerShell (gazdă Windows) - rulează ca Administrator
# Înlocuiește "Ubuntu-Networks" cu numele VM-ului tău
& "C:\Program Files\Oracle\VirtualBox\VBoxManage.exe" modifyvm "Ubuntu-Networks" --nested-hw-virt on
```

```bash
# Gazdă Linux/macOS
VBoxManage modifyvm "Ubuntu-Networks" --nested-hw-virt on
```

### 1.4 Instalare Guest Additions

#### Metoda A: De pe imaginea CD VirtualBox

```bash
# Montează CD-ul Guest Additions prin meniul VirtualBox: Devices → Insert Guest Additions CD
sudo mount /dev/cdrom /mnt
sudo /mnt/VBoxLinuxAdditions.run
sudo reboot
```

#### Metoda B: Din repository-urile Ubuntu (Recomandat)

```bash
sudo apt update
sudo apt install -y virtualbox-guest-utils virtualbox-guest-dkms
sudo reboot
```

### 1.5 Configurare port forwarding SSH

Pentru acces SSH prin adaptorul NAT:

```bash
# PowerShell (gazdă Windows)
& "C:\Program Files\Oracle\VirtualBox\VBoxManage.exe" modifyvm "Ubuntu-Networks" --natpf1 "SSH,tcp,,2222,,22"
```

Apoi conectează-te de pe gazdă:

```bash
ssh -p 2222 username@127.0.0.1
```

---

## 2. Actualizare sistem și pachete esențiale

### 2.1 Actualizare completă sistem

```bash
sudo apt update && sudo apt upgrade -y && sudo apt dist-upgrade -y
sudo apt autoremove -y && sudo apt autoclean
```

### 2.2 Instrumente build și pachete de dezvoltare

```bash
sudo apt install -y \
    build-essential \
    gcc \
    g++ \
    make \
    cmake \
    pkg-config \
    dkms \
    linux-headers-$(uname -r) \
    git \
    curl \
    wget \
    vim \
    nano \
    htop \
    tree \
    unzip \
    jq \
    ca-certificates \
    gnupg \
    lsb-release \
    software-properties-common \
    apt-transport-https
```

### 2.3 Configurare fus orar

```bash
sudo timedatectl set-timezone Europe/Bucharest
timedatectl
```

### 2.4 Server SSH

```bash
sudo apt install -y openssh-server
sudo systemctl enable ssh
sudo systemctl start ssh
```

---

## 3. Instrumente de rețea

### 3.1 Diagnosticare rețea

```bash
sudo apt install -y \
    iputils-ping \
    iputils-tracepath \
    iproute2 \
    net-tools \
    dnsutils \
    bind9-dnsutils \
    traceroute \
    mtr-tiny \
    whois \
    host
```

### 3.2 Conectivitate rețea

```bash
sudo apt install -y \
    netcat-openbsd \
    socat \
    curl \
    wget \
    lftp \
    openssh-client \
    telnet
```

### 3.3 Monitorizare trafic

```bash
sudo apt install -y \
    tcpdump \
    iftop \
    nethogs \
    nload \
    bmon \
    iptraf-ng \
    vnstat
```

### 3.4 Securitate și scanare

```bash
sudo apt install -y \
    nmap \
    hping3 \
    iperf3 \
    arping \
    fping
```

### 3.5 Instrumente firewall

```bash
sudo apt install -y \
    iptables \
    iptables-persistent \
    conntrack \
    ufw
```

### 3.6 Bridging și VLAN

```bash
sudo apt install -y \
    bridge-utils \
    vlan \
    arptables \
    ebtables
```

### 3.7 Configurare permisiuni captură pachete

```bash
# Permite utilizatorilor non-root să captureze pachete
sudo setcap cap_net_raw,cap_net_admin+eip /usr/bin/tcpdump
sudo setcap cap_net_raw,cap_net_admin+eip /usr/bin/dumpcap 2>/dev/null || true
```

---

## 4. Python și biblioteci

### 4.1 Instalare Python

Ubuntu 24.04 include Python 3.12 implicit:

```bash
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    python3-setuptools \
    python3-wheel
```

Verifică instalarea:

```bash
python3 --version
pip3 --version
```

### 4.2 Instalare biblioteci Python

> **Important:** Ubuntu 24.04 folosește PEP 668 (mediu gestionat extern). Folosește flag-ul `--break-system-packages` sau creează un mediu virtual.

```bash
# Instalează toate bibliotecile necesare
pip3 install --break-system-packages --ignore-installed \
    scapy \
    dpkt \
    pyshark \
    netifaces \
    flask \
    requests \
    dnslib \
    dnspython \
    paramiko \
    pyftpdlib \
    paho-mqtt \
    grpcio \
    grpcio-tools \
    protobuf \
    os-ken \
    PyYAML \
    colorama \
    tabulate \
    psutil \
    pytest \
    python-docx
```

### 4.3 Biblioteci pe săptămâni

| Săpt. | Biblioteci necesare |
|:-----:|---------------------|
| 1–2 | `scapy`, `dpkt`, `pyshark`, `netifaces` |
| 3–4 | `struct` (built-in), `socket` (built-in), `scapy` |
| 5 | `ipaddress` (built-in), biblioteci calcul subrețele |
| 6–7 | `scapy`, `os-ken`, `netifaces` |
| 8 | `flask`, `requests`, biblioteci HTTP |
| 9 | `pyftpdlib`, `ftplib` (built-in) |
| 10 | `dnslib`, `dnspython`, `paramiko`, `requests` |
| 11 | `requests`, biblioteci DNS |
| 12 | `grpcio`, `grpcio-tools`, `protobuf` |
| 13 | `paho-mqtt`, `scapy` |
| 14 | Toate cele de mai sus |

### 4.4 Verificare instalare Python

```bash
python3 -c "
import scapy.all
import flask
import requests
import paramiko
import dns.resolver
import paho.mqtt.client
print('Toate bibliotecile de bază importate cu succes!')
"
```

---

## 5. Docker și Docker Compose

### 5.1 Adăugare repository oficial Docker

```bash
# Elimină versiunile vechi
sudo apt remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true

# Adaugă cheia GPG Docker
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Adaugă repository-ul Docker
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

### 5.2 Instalare Docker Engine

```bash
sudo apt update
sudo apt install -y \
    docker-ce \
    docker-ce-cli \
    containerd.io \
    docker-buildx-plugin \
    docker-compose-plugin
```

### 5.3 Configurare Docker pentru utilizator non-root

```bash
sudo usermod -aG docker $USER
newgrp docker

# Verifică (după logout/login)
docker run hello-world
```

### 5.4 Activare serviciu Docker

```bash
sudo systemctl enable docker
sudo systemctl enable containerd
sudo systemctl start docker
```

### 5.5 Verificare instalare Docker

```bash
docker --version
docker compose version
docker run --rm hello-world
```

---

## 6. Mininet și Open vSwitch

### 6.1 Instalare Mininet

```bash
sudo apt install -y mininet
```

### 6.2 Instalare Open vSwitch

```bash
sudo apt install -y \
    openvswitch-switch \
    openvswitch-common \
    openvswitch-testcontroller
```

### 6.3 Activare serviciu OVS

```bash
sudo systemctl enable openvswitch-switch
sudo systemctl start openvswitch-switch
```

### 6.4 Verificare instalare

```bash
# Verifică starea OVS
sudo ovs-vsctl show

# Testează Mininet
sudo mn --test pingall

# Curăță
sudo mn -c
```

### 6.5 Instalare controller SDN os-ken

```bash
pip3 install --break-system-packages os-ken
```

---

## 7. Wireshark/TShark

### 7.1 Instalare TShark (CLI)

```bash
sudo apt install -y tshark
```

În timpul instalării, selectează „Da" pentru a permite utilizatorilor non-superuser să captureze pachete.

### 7.2 Configurare permisiuni

```bash
sudo usermod -aG wireshark $USER
sudo setcap cap_net_raw,cap_net_admin+eip /usr/bin/dumpcap
```

### 7.3 Verificare instalare

```bash
tshark --version
# Test captură (scurt)
sudo timeout 5 tshark -i any -c 10 2>/dev/null || echo "Test captură complet"
```

---

## 8. Configurări suplimentare

### 8.1 Activare IP Forwarding

Necesar pentru scenarii NAT și rutare:

```bash
# Temporar (efect imediat)
sudo sysctl -w net.ipv4.ip_forward=1
sudo sysctl -w net.ipv6.conf.all.forwarding=1

# Permanent (supraviețuiește reboot-ului)
echo "net.ipv4.ip_forward=1" | sudo tee -a /etc/sysctl.conf
echo "net.ipv6.conf.all.forwarding=1" | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

### 8.2 Dezactivare systemd-resolved (opțional)

Necesar dacă apar conflicte pe portul 53:

```bash
sudo systemctl stop systemd-resolved
sudo systemctl disable systemd-resolved
sudo rm /etc/resolv.conf
echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf
echo "nameserver 8.8.4.4" | sudo tee -a /etc/resolv.conf
```

### 8.3 Configurare reguli firewall UFW

```bash
# Permite porturile comune utilizate de exercițiile de laborator
sudo ufw allow 22/tcp      # SSH
sudo ufw allow 8080/tcp    # Demo-uri HTTP
sudo ufw allow 3333/tcp    # Protocoale personalizate
sudo ufw allow 4444/tcp    # Protocoale personalizate
sudo ufw allow 5555/tcp    # Protocoale personalizate
sudo ufw allow 1025/tcp    # Demo SMTP
sudo ufw allow 2121/tcp    # Demo FTP
sudo ufw allow 1883/tcp    # MQTT

# Activează firewall (opțional)
# sudo ufw enable
```

### 8.4 Creare structură directoare

```bash
mkdir -p ~/networking/{seminars,pcap,logs,scripts,docs}
mkdir -p ~/networking/seminars/{WEEK{1..14}}
```

### 8.5 Configurare Git

```bash
git config --global user.name "Nume Student"
git config --global user.email "student@example.com"
git config --global init.defaultBranch main
```

### 8.6 Alias-uri Bash utile

Adaugă în `~/.bashrc`:

```bash
cat >> ~/.bashrc << 'EOF'

# Alias-uri Docker
alias dps='docker ps'
alias dpsa='docker ps -a'
alias dimg='docker images'
alias dprune='docker system prune -af'
alias dc='docker compose'
alias dcup='docker compose up -d'
alias dcdown='docker compose down'
alias dclogs='docker compose logs -f'

# Alias-uri Mininet
alias mnc='sudo mn -c'
alias mnt='sudo mn --test pingall'

# Alias-uri rețea
alias ports='sudo ss -tulpn'
alias myip='ip -4 addr show | grep inet'
alias pingg='ping -c 4 8.8.8.8'
alias routes='ip route show'

# Navigare rapidă
alias week='cd ~/networking/seminars'
EOF

source ~/.bashrc
```

---

## 9. Transfer și organizare materiale

### 9.1 Clonare din repository

```bash
cd ~/networking/seminars
git clone https://github.com/antonioclim/netEN.git
```

### 9.2 Alternativă: SCP de pe gazdă

```bash
# De pe mașina gazdă
scp -P 2222 -r ./WEEK* username@127.0.0.1:~/networking/seminars/
```

### 9.3 Alternativă: Foldere partajate VirtualBox

```bash
# În VM
sudo mount -t vboxsf nume_folder_partajat /mnt/shared
cp -r /mnt/shared/WEEK* ~/networking/seminars/
```

### 9.4 Setare permisiuni

```bash
cd ~/networking/seminars
find . -name "*.sh" -exec chmod +x {} \;
find . -name "*.py" -exec chmod +x {} \;
```

---

## 10. Script de verificare

Creează și rulează acest script pentru a verifica instalarea completă:

```bash
#!/bin/bash
# verify_installation.sh - Verifică toate componentele

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

ERRORS=0

check() {
    if eval "$2" &>/dev/null; then
        echo -e "${GREEN}✓${NC} $1"
    else
        echo -e "${RED}✗${NC} $1"
        ((ERRORS++))
    fi
}

check_warn() {
    if eval "$2" &>/dev/null; then
        echo -e "${GREEN}✓${NC} $1"
    else
        echo -e "${YELLOW}○${NC} $1 (opțional)"
    fi
}

echo "═══════════════════════════════════════════════════════════"
echo "   Ubuntu Server 24.04 LTS - Verificare instalare"
echo "═══════════════════════════════════════════════════════════"
echo ""

echo "▶ Informații sistem"
echo "  Hostname: $(hostname)"
echo "  Ubuntu: $(lsb_release -d | cut -f2)"
echo "  Kernel: $(uname -r)"
echo ""

echo "▶ Componente de bază"
check "Python 3.10+" "python3 --version | grep -E 'Python 3\.(1[0-9]|[2-9][0-9])'"
check "pip3" "pip3 --version"
check "Git" "git --version"
check "curl" "curl --version"
check "wget" "wget --version"
echo ""

echo "▶ Docker"
check "Docker Engine" "docker --version"
check "Docker Compose" "docker compose version"
check "Daemon Docker" "docker info"
check_warn "Docker (non-root)" "docker ps"
echo ""

echo "▶ Simulare rețea"
check "Mininet" "which mn"
check "Open vSwitch" "sudo ovs-vsctl show"
check_warn "os-ken" "python3 -c 'import os_ken'"
echo ""

echo "▶ Instrumente rețea"
check "tcpdump" "which tcpdump"
check "tshark" "which tshark"
check "nmap" "which nmap"
check "iperf3" "which iperf3"
check "netcat" "which nc"
echo ""

echo "▶ Biblioteci Python"
check "scapy" "python3 -c 'import scapy.all'"
check "flask" "python3 -c 'import flask'"
check "requests" "python3 -c 'import requests'"
check "paramiko" "python3 -c 'import paramiko'"
check "pyftpdlib" "python3 -c 'import pyftpdlib'"
check "paho-mqtt" "python3 -c 'import paho.mqtt.client'"
check "dnspython" "python3 -c 'import dns.resolver'"
check "grpcio" "python3 -c 'import grpc'"
echo ""

echo "▶ Servicii"
check "Server SSH" "systemctl is-active ssh"
check "Serviciu Docker" "systemctl is-active docker"
check "Serviciu OVS" "systemctl is-active openvswitch-switch"
echo ""

echo "▶ Permisiuni"
check_warn "Utilizator în grupul docker" "groups | grep -q docker"
check_warn "Utilizator în grupul wireshark" "groups | grep -q wireshark"
check_warn "IP forwarding activat" "sysctl net.ipv4.ip_forward | grep -q '= 1'"
echo ""

echo "═══════════════════════════════════════════════════════════"
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}Toate componentele necesare instalate cu succes!${NC}"
else
    echo -e "${RED}$ERRORS componentă(e) necesară(e) lipsă sau configurată(e) greșit.${NC}"
fi
echo "═══════════════════════════════════════════════════════════"

exit $ERRORS
```

Salvează și rulează:

```bash
chmod +x verify_installation.sh
./verify_installation.sh
```

---

## 11. Depanare

### Probleme frecvente și soluții

| Problemă | Soluție |
|----------|---------|
| **Permisiune Docker refuzată** | `sudo usermod -aG docker $USER` apoi logout/login |
| **Eroare Mininet: Exception** | `sudo mn -c` pentru a curăța apoi reîncearcă |
| **Permisiune TShark refuzată** | `sudo usermod -aG wireshark $USER` și `sudo setcap cap_net_raw,cap_net_admin+eip /usr/bin/dumpcap` |
| **Python externally-managed-environment** | Folosește flag-ul `--break-system-packages` sau creează venv |
| **Eroare pip RECORD file** | Folosește flag-ul `--ignore-installed` |
| **Portul 53 deja în uz** | Dezactivează systemd-resolved (vezi secțiunea 8.2) |
| **Procesele Mininet nu sunt curățate** | `sudo mn -c` urmat de `sudo killall -9 ovs-testcontroller` |

### Comenzi de diagnostic

```bash
# Verifică porturile deschise
sudo ss -tulpn

# Verifică starea Docker
docker info
docker ps -a

# Verifică starea OVS
sudo ovs-vsctl show

# Vizualizează log-urile de sistem
journalctl -xe --no-pager | tail -50

# Verifică spațiul pe disc
df -h

# Verifică utilizarea memoriei
free -h

# Listează interfețele de rețea
ip link show

# Verifică tabela de rutare
ip route show
```

### Script de instalare completă

Pentru instalare automată, folosește acest script all-in-one:

```bash
#!/bin/bash
# install_networking_lab.sh
# Script complet de instalare pentru laboratorul de Rețele de Calculatoare

set -e

echo "Se începe instalarea completă..."

# Actualizare sistem
sudo apt update && sudo apt upgrade -y

# Pachete esențiale
sudo apt install -y build-essential git curl wget vim nano htop tree unzip jq \
    ca-certificates gnupg lsb-release software-properties-common apt-transport-https

# Instrumente de rețea
sudo apt install -y iputils-ping iproute2 net-tools dnsutils traceroute mtr-tiny \
    whois netcat-openbsd socat tcpdump iftop nethogs nload nmap hping3 iperf3 \
    iptables iptables-persistent bridge-utils vlan tshark

# Python
sudo apt install -y python3 python3-pip python3-venv python3-dev

# Biblioteci Python
pip3 install --break-system-packages --ignore-installed \
    scapy dpkt flask requests dnslib dnspython paramiko pyftpdlib \
    paho-mqtt grpcio grpcio-tools protobuf os-ken PyYAML colorama psutil

# Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo usermod -aG docker $USER

# Mininet și OVS
sudo apt install -y mininet openvswitch-switch openvswitch-common

# Activare servicii
sudo systemctl enable docker openvswitch-switch ssh
sudo systemctl start docker openvswitch-switch ssh

# Permisiuni
sudo setcap cap_net_raw,cap_net_admin+eip /usr/bin/tcpdump
sudo setcap cap_net_raw,cap_net_admin+eip /usr/bin/dumpcap 2>/dev/null || true
sudo usermod -aG wireshark $USER 2>/dev/null || true

# IP forwarding
echo "net.ipv4.ip_forward=1" | sudo tee -a /etc/sysctl.conf
sudo sysctl -p

# Structură directoare
mkdir -p ~/networking/{seminars,pcap,logs,scripts,docs}

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "Instalare completă! Te rugăm să faci logout și login din nou"
echo "pentru ca modificările de membership în grupuri să aibă efect."
echo "═══════════════════════════════════════════════════════════"
```

---

## Sumar cerințe spațiu disc

| Componentă | Dimensiune |
|------------|------------|
| Ubuntu Server 24.04 LTS (minimal) | ~3,5 GB |
| Pachete și instrumente de sistem | ~2,0 GB |
| Python și biblioteci | ~0,4 GB |
| Imagini Docker (toate săptămânile) | ~3,8 GB |
| Materiale curs (SĂPTĂMÂNA 1–14) | ~10 MB |
| Spațiu de lucru pentru artefacte | ~0,7 GB |
| **Total recomandat** | **25 GB** |

---

*Acest ghid a fost generat pentru cursul de Rețele de Calculatoare de la ASE-CSIE București. Pentru actualizări și corecturi, consultați repository-ul cursului.*
