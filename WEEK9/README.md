# Starterkit Săptămâna 9 – Rețele de calculatoare

## Nivelul Sesiune (L5), Nivelul Prezentare (L6) & Protocoale de Fișiere

**Disciplina:** Rețele de calculatoare  
**Facultatea:** Cibernetică, Statistică și Informatică Economică (ASE București)  
**Programul de studii:** Informatică economică, anul 3, semestrul 2  
**Săptămâna:** 9 din 14  
**Tehnologii:** Python 3.10+, Docker, Mininet (opțional)

---

## Ce vom învăța

Două nivele OSI care nu au protocoale separate în Internet, dar ale căror funcții (sesiune, prezentare) apar în orice aplicație distribuită: JWT, JSON, gzip, TLS.

> **De ce pseudo-FTP și nu FTP real?** FTP-ul din RFC 959 are prea multe comenzi și moduri pentru 100 de minute. Protocolul nostru păstrează esența — control separat de date, sesiune autentificată — dar e suficient de simplu pentru a fi implementat de la zero într-un seminar.

### Obiective de cunoaștere
- Explicarea rolului nivelurilor sesiune (L5) și prezentare (L6) în modelul OSI
- Diferențierea conexiunii TCP (L4) de sesiunea logică (L5)
- Identificarea funcțiilor de sesiune și prezentare în sistemele moderne

### Obiective de aplicare
- Implementarea unui protocol binar cu framing (header + payload)
- Construirea unui server/client cu gestiune de sesiune
- Utilizarea conexiunilor separate pentru control și transfer de date

### Obiective de analiză și evaluare
- Analiza traficului de rețea folosind tcpdump/Wireshark
- Compararea modurilor activ și pasiv pentru transfer de fișiere
- Evaluarea impactului latenței asupra protocoalelor

---

## De ce contează

În sisteme distribuite și API-uri, înțelegerea conceptuală a nivelurilor sesiune și prezentare e importantă pentru proiectarea corectă:

- **Autentificare și autorizare** (JWT, OAuth) – concepte L5
- **Serializare date** (JSON, Protocol Buffers) – concepte L6
- **Compresie și encoding** (gzip, Base64) – concepte L6
- **Gestiunea stării** (cookies, sesiuni) – concepte L5

Un programator care nu înțelege aceste concepte va scrie cod care funcționează, dar care nu scalează și nu poate fi întreținut.

---

## Structura kitului

```
starterkit_s9_final/
├── README.md                      # Acest fișier
├── Makefile                       # Automatizări principale
├── requirements.txt               # Dependențe Python
│
├── curs/                          # Materialele de curs (C9)
│   └── c9_sesiune_prezentare.md   # Conținut curs complet
│
├── seminar/                       # Materialele de seminar (S9)
│   ├── stage1_intro/              # Introducere protocoale fișiere
│   ├── stage2_pseudo_ftp/         # Implementare pseudo-FTP
│   ├── stage3_multi_client/       # Testare multi-client Docker
│   └── stage4_mininet/            # Scenarii Mininet avansate
│
├── python/
│   ├── exercises/
│   │   ├── ex_9_01_endianness.py  # Exercițiu L6: framing binar
│   │   ├── ex_9_02_pseudo_ftp.py  # Server/client pseudo-FTP complet
│   │   ├── ftp_demo_server.py     # Server FTP real (pyftpdlib)
│   │   └── ftp_demo_client.py     # Client FTP real (ftplib)
│   └── utils/
│       └── net_utils.py           # Utilitare: framing, hashing, compresie
│
├── mininet/
│   ├── topologies/
│   │   ├── topo_base.py           # 1 server + 1 client
│   │   └── topo_extended.py       # 1 server + 3 clienți
│   └── scenarios/
│       └── lab_tasks.md           # Sarcini ghidate
│
├── docker/
│   └── docker-compose.yml         # Multi-client FTP testing
│
├── scripts/
│   ├── setup.sh                   # Instalare dependențe
│   ├── cleanup.sh                 # Curățare resurse
│   ├── run_demo.sh                # Demo complet automatizat
│   └── capture_traffic.sh         # Script tcpdump helper
│
├── tests/
│   ├── smoke_test.sh              # Verificare rapidă
│   └── verify.sh                  # Validare mediu
│
├── docs/
│   ├── curs.md                    # Markdown sursă curs
│   ├── seminar.md                 # Markdown sursă seminar
│   ├── lab.md                     # Markdown sursă laborator
│   ├── checklist.md               # Checklist cadru didactic
│   └── rubrici.md                 # Criterii evaluare
│
├── slides/
│   ├── curs_outline.txt           # Outline curs pentru export
│   └── seminar_outline.txt        # Outline seminar pentru export
│
├── html_prezentari/
│   ├── theory.html                # Prezentare teorie interactivă
│   ├── seminar.html               # Seminar super-interactiv
│   └── lab.html                   # Laborator pas cu pas
│
├── assets/
│   ├── images/                    # Imagini generate
│   └── puml/                      # Surse PlantUML
│
├── pcap/                          # Capturi exemplu
├── server-files/                  # Director server
└── client-files/                  # Director client
```

---

## Cerințe și instalare

### Cerințe minime
- **OS:** Ubuntu 22.04+ / Debian 12+ (sau WSL2 pe Windows)
- **Python:** 3.10+ (verificați cu `python3 --version`)
- **Docker:** 24.0+ (opțional, pentru multi-client)
- **Mininet:** 2.3.0+ (opțional, pentru lab avansat)

### Instalare rapidă (o singură comandă)
```bash
make setup
```

### Instalare manuală pas cu pas
```bash
# 1. Instalare pachete sistem
sudo apt update
sudo apt install -y python3-pip tcpdump net-tools

# 2. Dependențe Python
python3 -m pip install --break-system-packages -r requirements.txt

# 3. (Opțional) Docker
sudo apt install -y docker.io docker-compose
sudo usermod -aG docker $USER

# 4. (Opțional) Mininet
sudo apt install -y mininet openvswitch-switch
```

---

## Rulare rapidă (Quick Start)

### Demo automat complet (fără input interactiv):
```bash
# Instalare + demo + validare într-o singură comandă
./scripts/setup.sh && ./scripts/run_all.sh
```

Aceasta produce:
- `artifacts/demo.log` – jurnal complet
- `artifacts/demo.pcap` – captură trafic
- `artifacts/validation.txt` – rezultate validare

### Demo manual în 3 terminale:
```bash
# Terminal 1: Server pseudo-FTP (port 5900)
make server

# Terminal 2: Client
make client-list
make client-get FILE=hello.txt

# Terminal 3 (opțional): Captură trafic
make capture
```

### Verificare rezultate:
```bash
./tests/smoke_test.sh
```

### Curățare:
```bash
./scripts/cleanup.sh      # Păstrează artefacte
./scripts/cleanup.sh --all # Șterge tot
```

---

## Fluxul de lucru recomandat

### Pentru curs (90 minute):
1. Prezentare slide-uri (`slides/curs_outline.txt` → PowerPoint)
2. Demo live: `make demo-encoding` (demonstrează L6)
3. Discuție: conexiune vs sesiune
4. Teaser pentru seminar

### Pentru seminar (100 minute):

| Etapă | Durată | Activitate | Comandă |
|-------|--------|------------|---------|
| 1 | 15 min | Intro + setup | `make setup` |
| 2 | 20 min | Exercițiu L6 (endianness) | `make ex1` |
| 3 | 35 min | Pseudo-FTP local | `make server` + `make client` |
| 4 | 20 min | Docker multi-client | `make docker-up` |
| 5 | 10 min | Recapitulare | Discuție |

### Pentru laborator avansat (opțional, 60 min extra):
```bash
sudo make mininet-test
```

---

## Conținut detaliat

### Nivelul sesiune (L5) – Concepte cheie

**Ce rezolvă L5?**
- Identificarea unei conversații logice (nu doar a unei conexiuni TCP)
- Menținerea stării între mesaje multiple
- Controlul dialogului (cine vorbește când)
- Timeout, expirare, reluare

**Diferența conexiune vs sesiune:**

| Aspect | Conexiune (L4) | Sesiune (L5) |
|--------|----------------|--------------|
| Ce este | Socket TCP/UDP deschis | Context logic al interacțiunii |
| Durată | Cât socket-ul e deschis | Poate supraviețui mai multor conexiuni |
| Exemplu | `connect()` → `close()` | Login → multiple requests → logout |
| Stare | Secvență numere TCP | User, CWD, permisiuni |

> **Din experiența mea:** Studenții confundă frecvent "conexiune" cu "sesiune". Cel mai bun mod de a clarifica: conexiunea e socket-ul (IP:port ↔ IP:port), sesiunea e *cine* vorbește și *ce* a făcut până acum.

**Implementări moderne:**
- Cookies HTTP (menținere sesiune în protocol stateless)
- JWT / OAuth tokens
- TLS session resumption
- WebSocket connections
- Database sessions (Redis, PostgreSQL)

### Nivelul prezentare (L6) – Concepte cheie

**Ce rezolvă L6?**
- Reprezentarea datelor (encoding)
- Serializare/deserializare
- Compresie
- (Istoric) criptare

**Implementări moderne:**
- **Formate date:** JSON, XML, Protocol Buffers
- **Codări caractere:** UTF-8, ASCII
- **Compresie:** gzip, brotli, zstd
- **Tipuri conținut:** MIME types (`text/html`, `application/json`)
- **Encoding binar:** Base64 (binar → text)

### Protocoale de fișiere – Control + Data

**FTP clasic:**
```
client ──control (port 21)──→ server   (comenzi: USER, PASS, LIST, RETR)
client ←──data (port 20/*)──→ server   (transfer efectiv fișiere)
```

**Mod activ vs pasiv:**

| Aspect | Mod activ | Mod pasiv |
|--------|-----------|-----------|
| Cine ascultă pentru date | Clientul | Serverul |
| Cine inițiază conexiunea de date | Serverul | Clientul |
| Funcționează prin NAT/firewall | ❌ Rar | ✅ Da |
| Utilizare modernă | Depășit | Standard |

---

## Automatizări disponibile

### Makefile targets principale:
```bash
make help           # Listează toate target-urile disponibile
make setup          # Instalare completă
make clean          # Curățare fișiere temporare
make reset          # Resetare la starea inițială

# Exerciții
make ex1            # Exercițiu endianness (L6)
make ex1-demo       # Demo endianness cu output verbose

# Pseudo-FTP
make server         # Pornește serverul pseudo-FTP
make client-list    # Listează fișiere pe server
make client-get FILE=hello.txt  # Descarcă un fișier

# Docker
make docker-up      # Pornește stack-ul Docker
make docker-test    # Rulează test multi-client
make docker-down    # Oprește și curăță

# Mininet (necesită sudo)
make mininet-base   # Topologie minimă
make mininet-test   # Test automatizat cu 3 clienți

# Captură trafic
make capture        # tcpdump pe port 3333
make capture-save   # Salvează în fișier .pcap

# Verificare
make verify         # Verifică că mediul e OK
make test           # Rulează toate testele
```

---

## Troubleshooting

> **Truc util:** Dacă serverul nu pornește, verifică mai întâi cu `ss -tlnp | grep <port>`. 9 din 10 cazuri e un proces vechi care n-a murit.

### Probleme frecvente:

**1. `Address already in use` (port 3333 ocupat)**
```bash
ss -lntp | grep 3333
kill <PID>
# sau folosește alt port:
make server PORT=4444
```

**2. `ModuleNotFoundError: pyftpdlib`**
```bash
python3 -m pip install pyftpdlib --break-system-packages
```

**3. `Permission denied` pentru tcpdump**
```bash
sudo tcpdump -i any "tcp port 3333" -nn
```

**4. Docker: `Cannot connect to Docker daemon`**
```bash
sudo systemctl start docker
sudo usermod -aG docker $USER
```

**5. Mininet: `Cannot find device s1`**
```bash
sudo systemctl restart openvswitch-switch
sudo mn -c
```

---

## Livrabile pentru evaluare

1. **Captură trafic** (obligatoriu): Un fișier `.pcap` care evidențiază separarea control/data
2. **Transfer reușit**: Un fișier transferat cu succes + hash-ul SHA256
3. **Notă reflexivă** (10-15 rânduri): „Unde am implementat L5? Unde am implementat L6?"

---

## Bibliografie

1. J. Kurose, K. Ross – *Computer Networking: A Top-Down Approach*, 7th Ed., Pearson, 2016
2. B. Rhodes, J. Goerzen – *Foundations of Python Network Programming*, Apress, 2014
3. C. Timofte, R. Constantinescu, I. Nemedi – *Rețele de calculatoare – caiet de seminar*, ASE, 2004

### RFC-uri relevante:
- RFC 959 – File Transfer Protocol (FTP)
- RFC 2616 – HTTP/1.1 (headers Content-Type, Content-Encoding)
- RFC 4627 – JSON Media Type
- RFC 6455 – WebSocket Protocol

---

*Revolvix&Hypotheticalandrei*  
*Ultima actualizare: Decembrie 2025*
