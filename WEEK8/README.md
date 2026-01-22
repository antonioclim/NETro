# Săptămâna 8 – Nivelul Transport + Server HTTP + Reverse Proxy

**Rețele de Calculatoare** | ASE București - CSIE | Informatică Economică

---

## Cuprins

- [Ce vom învăța](#ce-vom-învăța)
- [De ce contează](#de-ce-contează)
- [Prerechizite](#prerechizite)
- [🚀 Start rapid](#-start-rapid)
- [Structura kit-ului](#structura-kit-ului)
- [🎮 Demo-uri](#-demo-uri)
- [🔬 Laborator](#-laborator)
- [Troubleshooting](#troubleshooting)
- [Bibliografie](#bibliografie)

---

## Ce vom învăța

### Curs (Teorie)
- **Nivelul Transport** în modelul TCP/IP
- **TCP**: Three-way handshake, flag-uri, opțiuni (MSS, SACK, Window Scaling)
- **UDP**: Caracteristici, cazuri de utilizare
- **TLS/DTLS**: Securizarea transportului
- **QUIC**: Protocolul modern de transport

### Seminar/Laborator (Practică)
- Implementarea unui **server HTTP minimal** cu socket-uri
- Implementarea unui **reverse proxy** cu load balancing round-robin
- **Capturare și analiză trafic** cu tcpdump/tshark
- Observarea **three-way handshake** în practică
- Înțelegerea header-elor HTTP și modificarea lor

---

## De ce contează

Ca programator, vei interacționa constant cu rețele:
- **API-uri REST** — necesită înțelegerea HTTP
- **Microservicii** — load balancing, reverse proxy
- **Debugging** — tcpdump, Wireshark
- **Securitate** — TLS, certificate
- **Performanță** — optimizări TCP, QUIC

Această săptămână construiește fundația pentru toate acestea.

> **Din experiența predării:** Studenții care înțeleg cum funcționează HTTP "sub capotă" 
> au un avantaj major când lucrează cu framework-uri web sau când trebuie să 
> debugeze probleme de rețea în producție.

---

## Prerechizite

### Software necesar
- Python 3.8+ (esențial)
- curl (esențial)
- netcat/nc (esențial)
- tcpdump (recomandat, pentru capturi)
- Docker (opțional, pentru scenarii avansate)

### Cunoștințe anterioare
- Săptămâna 5: Adresare IP, subnetting
- Săptămâna 6-7: Protocoale de rutare, NAT
- Bazele programării Python

---

## 🚀 Start rapid

```bash
# 1. Verifică mediul
make verify

# 2. Rulează setup-ul (dacă lipsește ceva)
make setup

# 3. Demo rapid - Server HTTP
make demo-http

# 4. Demo complet - Reverse Proxy cu Round-Robin
make demo-proxy

# 5. Vezi toate comenzile disponibile
make help
```

---

## Structura kit-ului

```
starterkit_s8/
├── README.md                    # Acest fișier
├── Makefile                     # Automatizări (make help)
│
├── python/
│   ├── demos/
│   │   ├── demo_http_server.py  # Server HTTP complet, comentat
│   │   └── demo_reverse_proxy.py # Reverse proxy cu round-robin
│   ├── exercises/
│   │   ├── ex01_http_server.py  # Exercițiu: completează TODO-urile
│   │   └── ex02_reverse_proxy.py
│   └── utils/
│       └── net_utils.py         # Funcții helper (parsing HTTP, etc.)
│
├── docs/
│   ├── curs/
│   │   └── c8_transport_layer.md
│   ├── seminar/
│   │   ├── s8_explanation.md
│   │   ├── s8_tasks.md
│   │   ├── peer_instruction.md   # Întrebări pentru discuții (NOU!)
│   │   └── exercitii_non_cod.md  # Trace, Parsons, Debug (NOU!)
│   ├── cheatsheet.md
│   └── checklist.md
│
├── www/                         # Fișiere statice pentru server
│   ├── index.html
│   ├── hello.txt
│   └── api/status.json
│
├── scenarios/                   # Scenarii demonstrative
│   ├── http-server/
│   ├── reverse-proxy/
│   ├── tcp-analysis/
│   └── tls-demo/
│
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
│
├── nginx/
│   ├── nginx.conf
│   └── conf.d/default.conf
│
├── scripts/
│   ├── setup.sh
│   ├── run_all.sh
│   └── cleanup.sh
│
├── tests/
│   ├── smoke_test.sh
│   └── expected_outputs.md
│
├── pcap/                        # Capturi (generate)
├── output/                      # Output-uri generate
├── artifacts/                   # Artefacte validare
└── slides/                      # Outline pentru prezentări
```

---

## 🎮 Demo-uri

### Demo 1: Server HTTP Minimal

```bash
# Terminal 1: Pornește serverul
make http-server

# Terminal 2: Testează cu curl
curl -v http://localhost:8080/
curl -v http://localhost:8080/hello.txt
curl -v http://localhost:8080/not-found  # → 404
```

**Ce observăm:**
- Structura request/response HTTP
- Header-ele adăugate de server (Content-Type, Content-Length)
- Status codes (200, 404, etc.)

### Demo 2: Reverse Proxy Round-Robin

```bash
# Terminal 1
make backend-a

# Terminal 2
make backend-b

# Terminal 3
make proxy-server

# Terminal 4: Test
for i in {1..6}; do
    curl -s http://localhost:8080/ -D - | grep X-Served-By
done
```

**Ce observăm:**
- Alternarea backend-urilor (A, B, A, B...)
- Header-ul `X-Forwarded-For` adăugat de proxy
- Două conexiuni TCP distincte

### Demo 3: Captură TCP Handshake

```bash
make capture-handshake
```

**Ce observăm în captură:**
- `[S]` - SYN (client inițiază)
- `[S.]` - SYN-ACK (server acceptă)
- `[.]` - ACK (client confirmă)
- `[P.]` - PSH-ACK (date HTTP)
- `[F.]` - FIN-ACK (închidere)

---

## 🔬 Laborator

### Exercițiul 1: Completare Server HTTP

Deschide `python/exercises/ex01_http_server.py` și completează secțiunile marcate cu `# TODO`:

```python
# TODO 1: Parsare request line
# TODO 2: Validare metodă HTTP
# TODO 3: Protecție directory traversal
# TODO 4: Construire răspuns HTTP
```

Test: `make test-ex1`

### Exercițiul 2: Completare Reverse Proxy

Deschide `python/exercises/ex02_reverse_proxy.py`:

```python
# TODO 1: Selectare backend (round-robin)
# TODO 2: Modificare header X-Forwarded-For
# TODO 3: Forward request către backend
# TODO 4: Tratare erori (502 Bad Gateway)
```

Test: `make test-ex2`

### Exerciții non-cod

Vezi `docs/seminar/exercitii_non_cod.md` pentru:
- **TRACE** — urmărire execuție cod pas cu pas
- **PARSONS** — reordonare linii de cod
- **DEBUG** — găsire și corectare erori

---

## Troubleshooting

### Port deja în uz

```bash
# Verifică ce folosește portul
sudo lsof -i :8080

# Oprește toate serverele
make kill-servers
```

### Permission denied pentru tcpdump

```bash
# Tcpdump necesită sudo pentru capture
sudo tcpdump -i lo port 8080 -nn
```

### Python module not found

```bash
# Verifică path-ul Python
python3 -c "import sys; print(sys.path)"

# Rulează din directorul kit-ului
cd starterkit_s8
python3 python/demos/demo_http_server.py
```

### curl: connection refused

```bash
# Verifică că serverul rulează
ps aux | grep python

# Verifică portul
netstat -tlnp | grep 8080
```

---

## Bibliografie

| Referință | Descriere |
|-----------|-----------|
| RFC 793 | TCP (Transmission Control Protocol) |
| RFC 768 | UDP (User Datagram Protocol) |
| RFC 7230-7235 | HTTP/1.1 |
| RFC 8446 | TLS 1.3 |
| RFC 9000 | QUIC |
| Kurose & Ross | Computer Networking: A Top-Down Approach |

---

## Notă pentru studenți

Acest kit conține:
- **Demo-uri complete** — pentru observare și înțelegere
- **Exerciții** — pentru practică activă
- **Automatizări** — pentru productivitate

Abordare recomandată:
1. Citește documentația din `docs/`
2. Rulează demo-urile și observă output-ul
3. Completează exercițiile pas cu pas
4. Experimentează cu variații proprii

---

*Rețele de Calculatoare - ASE București - CSIE*  
*ing. dr. Antonio Clim*
