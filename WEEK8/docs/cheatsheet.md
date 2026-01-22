# Cheatsheet CLI – Săptămâna 8

Referință rapidă pentru comenzile utilizate în laboratorul de Server HTTP și Reverse Proxy.

---

## Comenzi Make

```bash
# Setup și verificare
make setup              # Instalare dependențe
make verify             # Verificare mediu

# Demo automat (produce artefacte)
make run-all            # Demo complet + captură
make run-all-quick      # Demo rapid (fără pcap)

# Demo-uri manuale
make demo-http          # Demo server HTTP
make demo-proxy         # Demo reverse proxy

# Servere individuale
make http-server        # Server HTTP (port 8080)
make backend-a          # Backend A (port 9001)
make backend-b          # Backend B (port 9002)
make proxy-server       # Reverse proxy (port 8888)

# Capturi
make capture-handshake  # Captură TCP handshake
make capture-proxy      # Captură client→proxy→backend

# Teste și cleanup
make smoke-test         # Test rapid funcționalitate
make clean              # Curățare temporare
make kill-servers       # Oprire toate serverele
make reset              # Reset complet
```

---

## Python Scripts

```bash
# Server HTTP
python3 python/demos/demo_http_server.py --port 8080 --www www
python3 python/demos/demo_http_server.py --host 0.0.0.0 --port 80 --id backend-A
python3 python/demos/demo_http_server.py --selftest

# Reverse Proxy
python3 python/demos/demo_reverse_proxy.py --listen-port 8888 \
    --backends 127.0.0.1:9001,127.0.0.1:9002
python3 python/demos/demo_reverse_proxy.py --selftest
```

---

## curl – Testare HTTP

```bash
# GET simplu
curl http://localhost:8080/

# Cu headers verbose
curl -v http://localhost:8080/

# Doar headers (HEAD)
curl -I http://localhost:8080/

# Headers în output, body separat
curl -D - http://localhost:8080/ -o /dev/null

# POST cu date
curl -X POST -d "key=value" http://localhost:8080/api

# JSON
curl -H "Content-Type: application/json" -d '{"key":"val"}' http://localhost:8080/api

# Follow redirects
curl -L http://localhost:8080/redirect

# Timeout
curl --connect-timeout 5 --max-time 10 http://localhost:8080/
```

---

## netcat – Debug TCP

```bash
# Client TCP simplu
echo -e "GET / HTTP/1.1\r\nHost: localhost\r\n\r\n" | nc localhost 8080

# Server TCP simplu
nc -l 9000

# Verificare port deschis
nc -zv localhost 8080

# Timeout
nc -w 5 localhost 8080
```

---

## tcpdump – Captură Pachete

```bash
# Captură pe loopback
sudo tcpdump -i lo port 8080 -nn

# Cu conținut ASCII
sudo tcpdump -i lo port 8080 -nn -A

# Cu conținut hex
sudo tcpdump -i lo port 8080 -nn -X

# Salvare în fișier
sudo tcpdump -i lo port 8080 -nn -w capture.pcap

# Citire din fișier
sudo tcpdump -r capture.pcap -nn

# Multiple porturi
sudo tcpdump -i lo '(port 8080 or port 9001)' -nn

# Doar SYN packets (conexiuni noi)
sudo tcpdump -i lo 'tcp[tcpflags] & tcp-syn != 0' -nn
```

---

## tshark – Analiză Wireshark CLI

```bash
# Captură live
sudo tshark -i lo -f "port 8080"

# Filtru HTTP
tshark -r capture.pcap -Y "http"

# Extract fields
tshark -r capture.pcap -Y "http" -T fields -e ip.src -e http.request.uri

# Statistics
tshark -r capture.pcap -q -z http,stat
tshark -r capture.pcap -q -z io,stat,1

# Follow TCP stream
tshark -r capture.pcap -q -z follow,tcp,ascii,0
```

---

## Verificare Porturi

```bash
# Procese pe port
sudo lsof -i :8080
sudo fuser 8080/tcp

# Porturi în ascultare
netstat -tlnp | grep LISTEN
ss -tlnp

# Verificare conectivitate
nc -zv localhost 8080

# Kill process pe port
sudo fuser -k 8080/tcp
```

---

## Docker (opțional)

```bash
# Build și run
make docker-build
make docker-up
make docker-down
make docker-logs

# Manual
docker-compose -f docker/docker-compose.yml up -d
docker-compose -f docker/docker-compose.yml logs -f
docker-compose -f docker/docker-compose.yml down
```

---

## Structura Directoare

```
WEEK8/
├── artifacts/          # Output demo (demo.log, demo.pcap, validation.txt)
├── python/
│   ├── demos/          # Demo-uri complete
│   ├── exercises/      # Exerciții de completat
│   └── utils/          # Funcții comune
├── scripts/
│   ├── setup.sh        # Configurare mediu
│   ├── run_all.sh      # Demo automat
│   └── cleanup.sh      # Curățare
├── tests/
│   └── smoke_test.sh   # Test rapid
├── www/                # Fișiere statice
└── docs/               # Documentație
```

---

## Porturi Standard (WEEK=8)

| Serviciu | Port | Descriere |
|----------|------|-----------|
| HTTP | 8080 | Server HTTP principal |
| Proxy | 8888 | Reverse proxy |
| Backend A | 9001 | Server backend 1 |
| Backend B | 9002 | Server backend 2 |
| Week Base | 5800 | WEEK_PORT_BASE |

---

## Sfaturi Securitate

```bash
# Nu expune servere pe 0.0.0.0 în producție
# Folosește 127.0.0.1 pentru test local

# Verifică directory traversal
curl http://localhost:8080/../../../etc/passwd  # Trebuie să returneze 400/403

# Verifică metode HTTP
curl -X DELETE http://localhost:8080/  # Trebuie să returneze 405
```

---

*Material pentru Seminar 8, Rețele de Calculatoare, ASE București*
