# Expected Outputs - Săptămâna 8

Acest document descrie output-urile așteptate pentru demo-ul automat și testele de verificare.

## Artefacte Generate

După rularea `./scripts/run_all.sh`, directorul `artifacts/` trebuie să conțină:

### artifacts/demo.log

Log complet al execuției demo-ului. Conține:
- Timestamp-uri pentru fiecare operație
- Rezultatele testelor HTTP (GET /, GET /not-found)
- Distribuția round-robin a request-urilor
- Mesaje de eroare (dacă există)

**Exemplu parțial:**
```
[14:30:01] [INFO] Demo automat pornit
[14:30:01] [INFO] Configurație: WEEK=8, HTTP_PORT=8080, PROXY_PORT=8888
[14:30:02] [STEP] [1/8] Verificare precondiții...
[14:30:02] [INFO]   Precondiții OK
[14:30:03] [INFO]   Server HTTP pornit pe port 8080
[14:30:03] [INFO]   ✓ GET / → 200 OK
[14:30:03] [INFO]   ✓ GET /not-found → 404
```

### artifacts/validation.txt

Rezultatele fiecărui test în format structurat. Folosit de smoke_test.sh pentru validare.

**Format:**
```
PREREQS: PASS
HTTP_GET_ROOT: PASS
HTTP_GET_404: PASS
BACKENDS_START: PASS
PROXY_START: PASS
ROUND_ROBIN_BALANCED: PASS
X_REQUEST_ID: PASS
X_SERVED_BY: PASS
PCAP_GENERATED: PASS (1234 bytes)

===== SUMAR =====
Timestamp: 2025-01-01 14:30:05
WEEK: 8
HTTP_PORT: 8080
PROXY_PORT: 8888
BACKENDS: 9001, 9002
DEMO_COMPLETED: SUCCESS
```

### artifacts/demo.pcap

Captură de pachete conținând:
- TCP three-way handshake (SYN, SYN-ACK, ACK)
- HTTP requests și responses
- Trafic client → proxy → backend

**Analiză cu tshark:**
```bash
tshark -r artifacts/demo.pcap -Y "http" -T fields -e ip.src -e ip.dst -e http.request.uri
```

**Analiză cu tcpdump:**
```bash
tcpdump -r artifacts/demo.pcap -nn | head -20
```

## Output Smoke Test

Rezultatul așteptat pentru `./tests/smoke_test.sh`:

```
╔═══════════════════════════════════════════════════════════════════════╗
║  Smoke Test - Săptămâna 8: HTTP Server + Reverse Proxy               ║
╚═══════════════════════════════════════════════════════════════════════╝

[Precondiții]
  [1] Python 3 disponibil... ✓
  [2] Module Python necesare... ✓
  [3] curl disponibil... ✓
  [4] Fișiere kit prezente... ✓

[Server HTTP]
  [5] Server HTTP pornește... ✓
  [6] GET / → 200 OK... ✓
  [7] GET /not-found → 404... ✓
  [8] Header X-Backend prezent... ✓

[Reverse Proxy]
  [9] Backend pornește... ✓
  [10] Reverse proxy pornește... ✓
  [11] Proxy forwarding funcționează... ✓
  [12] Header X-Served-By prezent... ✓

[Artefacte]
  [13] artifacts/demo.log există... ✓
  [14] artifacts/validation.txt există... ✓
  [15] artifacts/demo.pcap există... ○ (necesită tcpdump)

═══════════════════════════════════════════════════════════════════════
Rezultate: 14 passed, 0 failed, 1 warnings
═══════════════════════════════════════════════════════════════════════
Toate testele critice au trecut!
```

## HTTP Response Headers

Server HTTP (demo_http_server.py) adaugă:
```
HTTP/1.1 200 OK
Content-Type: text/html; charset=utf-8
Content-Length: 2220
Connection: close
Server: ASE-S8-Server/1.0
X-Backend: http-demo
```

Reverse Proxy (demo_reverse_proxy.py) adaugă:
```
X-Served-By: backend-A
X-Request-ID: uuid-here
```

## Coduri de Ieșire

| Script | Exit 0 | Exit 1 |
|--------|--------|--------|
| run_all.sh | Toate testele pass | Cel puțin un test fail |
| smoke_test.sh | Toate testele critice pass | Teste critice fail |
| demo_http_server.py --selftest | Selftest pass | Selftest fail |
| demo_reverse_proxy.py --selftest | Selftest pass | Selftest fail |

## Porturi Utilizate (WEEK=8)

| Serviciu | Port | Descriere |
|----------|------|-----------|
| HTTP_PORT | 8080 | Server HTTP principal |
| PROXY_PORT | 8888 | Reverse proxy |
| BACKEND_PORT_A | 9001 | Backend A |
| BACKEND_PORT_B | 9002 | Backend B |
| WEEK_PORT_BASE | 5800 | Bază pentru porturi custom |

## Troubleshooting

### Testele eșuează cu "connection refused"
- Verifică că niciun alt proces nu folosește porturile
- `lsof -i :8080` sau `netstat -tlnp | grep 8080`

### demo.pcap gol sau lipsă
- tcpdump necesită sudo pentru captură
- Verifică permisiunile: `sudo tcpdump -D`

### Round-robin dezechilibrat
- Normal dacă există delay între requests
- Toleranța acceptată: diferență maximă 2 între backends
