# StarterKit Săptămâna 12: Protocoale E-mail & Remote Procedure Call (RPC)

## Sinopsis

Acest kit didactic integrează **teoria și practica** pentru:
- **Cursul 12**: SMTP, POP3, IMAP, WebMail (Nivelul Aplicație)
- **Seminarul 12**: RPC – JSON-RPC, XML-RPC, gRPC/Protobuf

Materialele sunt structurate progresiv, de la înțelegerea conceptelor fundamentale până la implementarea și analiza sistemelor distribuite reale.

---

## Ce vom învăța

### Curs 12 – Protocoale E-mail
- Arhitectura sistemelor de e-mail (MUA, MTA, MDA)
- Protocolul SMTP: transfer, envelope vs message, comenzi/coduri
- POP3 vs IMAP: model descărcare vs model acces
- MIME: atașamente și tipuri de conținut
- WebMail ca interfață aplicație
- Securitate: STARTTLS, SPF, DKIM, DMARC

### Seminar 12 – Remote Procedure Call
- Conceptul RPC și diferențele față de REST
- JSON-RPC: specificație 2.0, implementare Python
- XML-RPC: precursorul web services
- Protocol Buffers și gRPC: serializare binară eficientă
- Patterns: idempotență, retry, circuit breaker

---

## Structura proiectului

```
s12_starterkit/
├── README.md                     # Acest fișier
├── Makefile                      # Automatizări centrale
├── requirements.txt              # Dependențe Python
│
├── docs/
│   ├── curs/
│   │   └── curs.md               # Material curs complet
│   ├── seminar/
│   │   ├── seminar.md            # Material seminar complet
│   │   └── lab.md                # Instrucțiuni laborator
│   └── presentations/
│       ├── theory.html           # Prezentare interactivă curs
│       ├── seminar.html          # Prezentare interactivă seminar
│       └── lab.html              # Ghid laborator interactiv
│
├── exercises/
│   ├── README.md                 # Ghid exerciții
│   ├── ex_01_smtp.py             # Exerciții SMTP (self-contained)
│   └── ex_02_rpc.py              # Exerciții RPC (self-contained)
│
├── src/
│   ├── common/
│   │   ├── __init__.py
│   │   └── net_utils.py          # Utilitare rețea partajate
│   ├── email/
│   │   ├── smtp_server.py        # Server SMTP didactic
│   │   ├── smtp_client.py        # Client SMTP
│   │   ├── pop3_server.py        # Server POP3 minimal
│   │   └── email_utils.py        # Utilități email
│   └── rpc/
│       ├── common/
│       │   └── api_functions.py  # Funcții expuse via RPC
│       ├── jsonrpc/
│       │   ├── jsonrpc_server.py
│       │   └── jsonrpc_client.py
│       ├── xmlrpc/
│       │   ├── xmlrpc_server.py
│       │   └── xmlrpc_client.py
│       └── grpc/
│           ├── calculator.proto
│           ├── grpc_server.py
│           └── grpc_client.py
│
├── scripts/
│   ├── setup.sh                  # Instalare dependențe
│   ├── run_demos.sh              # Demo-uri interactive
│   ├── capture.sh                # Captură trafic
│   ├── verify.sh                 # Verificare mediu
│   └── clean.sh                  # Curățare
│
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
│
├── mininet/
│   └── topo_s12.py               # Topologie combinată
│
├── tests/
│   ├── smoke_test.sh
│   └── test_rpc.py
│
├── pcap/
│   └── README.md                 # Exemple capturi
│
├── slides/
│   ├── curs_slides_outline.txt
│   └── seminar_slides_outline.txt
│
└── assets/
    └── images/                   # Diagrame și figuri
```

---

## Cerințe de sistem

### Software Obligatoriu

| Componentă | Versiune | Verificare |
|------------|----------|------------|
| Python | 3.10+ | `python3 --version` |
| pip | 22.0+ | `pip3 --version` |

### Software Opțional

| Componentă | Scop |
|------------|------|
| Docker + Docker Compose | Izolare mediu |
| Mininet | Simulare topologii |
| tcpdump/tshark | Analiză trafic |
| Wireshark | Analiză GUI |

---

## 🚀 Instalare Rapidă

### Varianta A: Script automatizat (recomandat)

```bash
chmod +x scripts/*.sh
./scripts/setup.sh
```

### Varianta B: Instalare manuală

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Varianta C: Docker

```bash
docker compose -f docker/docker-compose.yml up -d
docker exec -it s12_lab bash
```

### Verificare instalare

```bash
make verify
# sau
./scripts/verify.sh
```

---

## Ghid de utilizare

### Exerciții Autonome (Quickstart)

Fișiere self-contained, fără dependențe externe:

```bash
cd exercises/

# SMTP: Server + Client
python3 ex_01_smtp.py server --port 1025 &
python3 ex_01_smtp.py send --port 1025 --subject "Test SMTP"
python3 ex_01_smtp.py --selftest

# RPC: JSON-RPC vs XML-RPC
python3 ex_02_rpc.py jsonrpc-server --port 8080 &
python3 ex_02_rpc.py jsonrpc-client --port 8080
python3 ex_02_rpc.py --selftest
```

### Demo SMTP

**Terminal 1 – Server:**
```bash
make smtp-server
```

**Terminal 2 – Client:**
```bash
make smtp-send TO=student@example.com SUBJ="Test S12"
```

**Terminal 3 – Captură (opțional):**
```bash
make capture-smtp
```

### Demo JSON-RPC

**Terminal 1:**
```bash
make jsonrpc-server
```

**Terminal 2:**
```bash
make jsonrpc-client
```

### Demo gRPC

```bash
make proto-gen      # Generare cod din .proto
make grpc-server    # Terminal 1
make grpc-client    # Terminal 2
```

### Benchmark Comparativ

```bash
make benchmark-rpc
```

---

## Targets Makefile

| Target | Descriere |
|--------|-----------|
| `make help` | Afișează toate target-urile |
| `make setup` | Instalează dependențele |
| `make verify` | Verifică instalarea |
| `make run-demo` | Rulează demo principal |
| `make run-lab` | Rulează scenariul de laborator |
| `make capture` | Captură pachete |
| `make clean` | Curățare fișiere temporare |
| `make reset` | Reset complet mediu |
| `make smtp-server` | Server SMTP |
| `make smtp-send` | Client SMTP |
| `make jsonrpc-server/client` | JSON-RPC |
| `make xmlrpc-server/client` | XML-RPC |
| `make grpc-server/client` | gRPC |
| `make proto-gen` | Generare cod Protobuf |
| `make benchmark-rpc` | Benchmark comparativ |
| `make docker-up/down` | Gestiune containere |

---

## 🔍 Troubleshooting

### 1. Port deja în uz

```bash
# Verificare ce proces folosește portul
ss -lntp | grep :1025
lsof -i :6200

# Oprire proces
kill -9 <PID>

# Sau cleanup complet
./scripts/cleanup.sh
```

### 2. ModuleNotFoundError: calculator_pb2

```bash
# Generare cod din .proto
make proto-gen

# Sau manual
cd src/rpc/grpc
python3 -m grpc_tools.protoc --proto_path=. --python_out=. --grpc_python_out=. calculator.proto
```

### 3. Connection refused

1. Verificați dacă serverul rulează: `ps aux | grep python`
2. Verificați portul și IP-ul (127.0.0.1 vs 0.0.0.0)
3. Verificați firewall: `sudo ufw status`
4. Verificați cu netcat: `nc -zv localhost 6200`

### 4. Permission denied pe porturi < 1024

```bash
# Utilizați porturi > 1024 (configurare implicită)
# SMTP: 1025 în loc de 25
# Pentru testare cu port 25:
sudo python3 src/email/smtp_server.py --port 25
```

### 5. tcpdump: Permission denied

```bash
# Rulare cu sudo
sudo tcpdump -i lo -w artifacts/demo.pcap port 1025

# Sau adăugare utilizator în grupul wireshark
sudo usermod -aG wireshark $USER
# (necesită re-login)
```

### 6. ImportError: No module named 'src'

```bash
# Asigurați-vă că rulați din directorul proiectului
cd /path/to/WEEK12
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Sau instalare ca pachet editable
pip install -e .
```

### 7. Mininet: RTNETLINK answers: File exists

```bash
# Cleanup Mininet
sudo mn -c

# Verificare procese rămase
ps aux | grep ovs
sudo killall ovs-vswitchd ovsdb-server controller
```

### 8. JSON-RPC: Invalid JSON / Parse error

```bash
# Verificați formatul JSON (ghilimele duble!)
# Corect:
curl -X POST -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"add","params":[1,2],"id":1}' \
  http://localhost:6200/

# Incorect (ghilimele simple):
# -d "{'jsonrpc':'2.0'..."  # NU funcționează!
```

### 9. XML-RPC: Method not found

```bash
# Listare metode disponibile (introspection)
python3 -c "
import xmlrpc.client
proxy = xmlrpc.client.ServerProxy('http://localhost:6201/')
print(proxy.system.listMethods())
"
```

### 10. Email nu ajunge / SMTP timeout

1. Verificați serverul SMTP: `nc -zv localhost 1025`
2. Testați manual:
```bash
echo -e "EHLO test\r\nQUIT\r\n" | nc localhost 1025
```
3. Verificați spool-ul: `ls -la artifacts/spool/`

### 11. Eroare la make: command not found

```bash
# Alternativă fără make
./scripts/setup.sh
./scripts/run_all.sh
./tests/smoke_test.sh
./scripts/cleanup.sh
```

### 12. Python version mismatch

```bash
# Verificare versiune
python3 --version  # Necesar: 3.10+

# Utilizare versiune specifică
python3.10 -m pip install -r requirements.txt
python3.10 src/email/smtp_server.py
```

---

## Reset complet

Pentru a reseta complet mediul de lucru:

```bash
# 1. Curățare completă (oprește procese, șterge temporare)
./scripts/cleanup.sh --full

# 2. Curățare Mininet (dacă a fost folosit)
sudo mn -c

# 3. Re-instalare dependențe
./scripts/setup.sh

# 4. Verificare mediu curat
./scripts/verify.sh

# 5. Rulare demo fresh
./scripts/run_all.sh

# 6. Validare
./tests/smoke_test.sh
```

---

## Livrabil student

### Cerințe proiect
1. Implementare client/server RPC funcțional
2. Demonstrație captură trafic (.pcap)
3. Documentație: README cu instrucțiuni de rulare
4. Cod comentat și structurat

### Criterii evaluare
| Criteriu | Pondere |
|----------|---------|
| Funcționalitate corectă | 40% |
| Calitatea codului | 20% |
| Documentație | 20% |
| Captură și analiză trafic | 20% |

### Checklist predare
- [ ] Cod funcționează pe VM minimală
- [ ] README cu quickstart
- [ ] Captură .pcap cu trafic relevant
- [ ] Fără dependențe externe nedocumentate

---

## Bibliografie

### Standarde și Specificații
- RFC 5321 – SMTP
- RFC 1939 – POP3
- RFC 3501 – IMAP
- RFC 5322 – Format mesaj e-mail
- JSON-RPC 2.0 Specification
- Protocol Buffers Language Guide v3

### Bibliografie Academică

| Autor | Titlu | Editura | An |
|-------|-------|---------|-----|
| Kurose, J., Ross, K. | Computer Networking: A Top-Down Approach, 8th Ed. | Pearson | 2021 |
| Rhodes, B., Goetzen, J. | Foundations of Python Network Programming | Apress | 2014 |
| Timofte, C. et al. | Rețele de calculatoare – Caiet de seminar | ASE | 2004 |

---

## Licență

Materiale dezvoltate pentru disciplina **Rețele de Calculatoare**, ASE-CSIE.

---

*Versiune: 1.1.0 | Data: Ianuarie 2026 | Standard Transversal aplicat*

<footer style="font-size: 0.8em; color: #888; text-align: center; margin-top: 40px;">
Rezolvix & Hypotheticalandrei | ASE-CSIE | Licență MIT
</footer>
