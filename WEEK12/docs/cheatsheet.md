# Cheatsheet CLI - Săptămâna 12: Email & RPC

## Configurare Week 12

```
WEEK=12
IP_BASE=10.0.12.0/24
PORT_BASE=6200
```

## Porturi

| Serviciu | Port | Utilizare |
|----------|------|-----------|
| SMTP | 1025 | Server email didactic |
| JSON-RPC | 6200 | HTTP + JSON |
| XML-RPC | 6201 | HTTP + XML |
| gRPC | 6251 | HTTP/2 + Protobuf |

## Quickstart

```bash
# Setup
./scripts/setup.sh

# Demo complet
./scripts/run_all.sh

# Validare
./tests/smoke_test.sh

# Cleanup
./scripts/cleanup.sh
```

## Server SMTP

```bash
# Pornire server
python3 src/email/smtp_server.py --port 1025 --spool ./spool

# Test cu netcat
echo -e "EHLO test\r\nQUIT\r\n" | nc localhost 1025

# Test cu telnet
telnet localhost 1025

# Client Python
python3 src/email/smtp_client.py \
    --server localhost --port 1025 \
    --from "sender@test.local" --to "receiver@test.local" \
    --subject "Test" --body "Hello"
```

### Comenzi SMTP

| Comandă | Descriere | Cod răspuns |
|---------|-----------|-------------|
| HELO/EHLO | Salut | 250 |
| MAIL FROM:<addr> | Expeditor envelope | 250 |
| RCPT TO:<addr> | Destinatar | 250 |
| DATA | Început mesaj | 354 |
| . (singur pe linie) | Final mesaj | 250 |
| QUIT | Închidere | 221 |
| RSET | Reset tranzacție | 250 |
| NOOP | No operation | 250 |

## Server JSON-RPC

```bash
# Pornire server
python3 src/rpc/jsonrpc/jsonrpc_server.py --port 6200

# Test cu curl
curl -X POST http://localhost:6200/ \
    -H "Content-Type: application/json" \
    -d '{"jsonrpc":"2.0","method":"add","params":[5,3],"id":1}'

# Răspuns așteptat
{"jsonrpc":"2.0","result":8,"id":1}
```

### Metode disponibile

| Metodă | Parametri | Descriere |
|--------|-----------|-----------|
| add | [a, b] | Adunare |
| subtract | [a, b] | Scădere |
| multiply | [a, b] | Înmulțire |
| divide | [a, b] | Împărțire |
| echo | ["msg"] | Echo |
| get_time | [] | Timestamp server |
| get_server_info | [] | Info server |
| sort_list | [items, reverse?] | Sortare |

### Batch request

```bash
curl -X POST http://localhost:6200/ \
    -H "Content-Type: application/json" \
    -d '[
        {"jsonrpc":"2.0","method":"add","params":[1,2],"id":1},
        {"jsonrpc":"2.0","method":"multiply","params":[3,4],"id":2}
    ]'
```

## Server XML-RPC

```bash
# Pornire server
python3 src/rpc/xmlrpc/xmlrpc_server.py --port 6201

# Test cu curl
curl -X POST http://localhost:6201/ \
    -H "Content-Type: text/xml" \
    -d '<?xml version="1.0"?>
<methodCall>
  <methodName>add</methodName>
  <params>
    <param><value><int>15</int></value></param>
    <param><value><int>25</int></value></param>
  </params>
</methodCall>'

# Introspection
python3 -c "
import xmlrpc.client
proxy = xmlrpc.client.ServerProxy('http://localhost:6201/')
print(proxy.system.listMethods())
"
```

## Captură trafic

```bash
# Cu tcpdump
sudo tcpdump -i lo -w capture.pcap port 1025 or port 6200

# Vizualizare
tcpdump -r capture.pcap -A | head -50

# Cu tshark
tshark -i lo -f "port 1025 or port 6200" -w capture.pcap

# Analiză HTTP
tshark -r capture.pcap -Y http
```

## Mininet

```bash
# Pornire topologie
sudo python3 mininet/topo_email_rpc_base.py

# Comenzi CLI
mininet> nodes
mininet> net
mininet> pingall
mininet> xterm client server
mininet> client ping -c 3 10.0.12.100
mininet> exit

# Cleanup
sudo mn -c
```

## Troubleshooting rapid

```bash
# Port ocupat?
ss -lntp | grep :6200
lsof -i :6200

# Proces Python?
ps aux | grep python

# Kill toate serverele
pkill -f "smtp_server.py|jsonrpc_server|xmlrpc_server"

# Cleanup complet
./scripts/cleanup.sh --full
```

## Erori comune JSON-RPC

| Cod | Mesaj | Cauză |
|-----|-------|-------|
| -32700 | Parse error | JSON invalid |
| -32600 | Invalid Request | Lipsește jsonrpc sau method |
| -32601 | Method not found | Metodă inexistentă |
| -32602 | Invalid params | Parametri incorecți |
| -32603 | Internal error | Eroare server |

## Referințe rapide

- RFC 5321: SMTP
- JSON-RPC 2.0: https://www.jsonrpc.org/specification
- XML-RPC: http://xmlrpc.com/spec.md
- Protobuf: https://protobuf.dev/
