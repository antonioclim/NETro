# Expected Outputs - Săptămâna 14

Acest document conține output-urile așteptate pentru demonstrațiile și testele din starterkit.

## 1. Verificare mediu (`make verify`)

### Output așteptat (succes)

```
[INFO] Verificare mediu pentru Săptămâna 14...

[CHECK] Python 3...
  ✓ Python 3.10.12

[CHECK] Mininet...
  ✓ Mininet 2.3.0

[CHECK] Open vSwitch...
  ✓ OVS 2.17.7

[CHECK] tcpdump...
  ✓ tcpdump 4.99.1

[CHECK] tshark...
  ✓ tshark 3.6.2

[CHECK] Porturi libere...
  ✓ Port 8080: liber
  ✓ Port 9090: liber
  ✓ Port 9091: liber

[INFO] Toate verificările au trecut!
```

### Output eroare (exemplu)

```
[INFO] Verificare mediu pentru Săptămâna 14...

[CHECK] Python 3...
  ✓ Python 3.10.12

[CHECK] Mininet...
  ✗ Mininet nu este instalat

[ERROR] Verificarea a eșuat. Rulează: sudo bash scripts/setup.sh
```

## 2. Smoke Test (`bash tests/smoke_test.sh`)

### Output așteptat (succes)

```
================================================================================
SMOKE TEST - Starterkit Săptămâna 14
================================================================================

[1/4] Verificare structură fișiere...
  ✓ README.md
  ✓ Makefile
  ✓ python/apps/backend_server.py
  ✓ python/apps/lb_proxy.py
  ✓ python/apps/http_client.py
  ✓ python/apps/tcp_echo_server.py
  ✓ python/apps/tcp_echo_client.py
  ✓ python/apps/run_demo.py
  ✓ python/exercises/ex_14_01.py
  ✓ python/exercises/ex_14_02.py
  ✓ mininet/topologies/topo_14_recap.py
  ✓ scripts/setup.sh
  ✓ scripts/cleanup.sh

[2/4] Verificare sintaxă Python...
  ✓ backend_server.py
  ✓ lb_proxy.py
  ✓ http_client.py
  ✓ tcp_echo_server.py
  ✓ tcp_echo_client.py
  ✓ run_demo.py
  ✓ ex_14_01.py
  ✓ ex_14_02.py
  ✓ topo_14_recap.py

[3/4] Verificare import Mininet...
  ✓ Import mininet.net OK
  ✓ Import mininet.topo OK

[4/4] Verificare permisiuni scripturi...
  ✓ setup.sh executabil
  ✓ cleanup.sh executabil

================================================================================
REZULTAT: 24/24 verificări trecute
STATUS: PASS ✓
================================================================================
```

## 3. Demo complet (`make run-demo`)

### Output așteptat (stdout)

```
================================================================================
DEMO - Săptămâna 14: Recapitulare și Integrare
================================================================================

[SETUP] Curățare Mininet anterior...
[SETUP] Creare topologie...

*** Creating network
*** Adding controller
*** Adding hosts:
h1 h2 h3 h4 
*** Adding switches:
s1 s2 
*** Adding links:
(h1, s1) (h2, s1) (h3, s2) (h4, s2) (s1, s2) 
*** Configuring hosts
h1 h2 h3 h4 
*** Starting controller
*** Starting 2 switches
s1 s2 ...

[INFO] Topologie creată cu succes

[DEMO 1] Test conectivitate (ping)...
  h1 -> h2: OK (0.5ms)
  h1 -> h3: OK (1.2ms)
  h1 -> h4: OK (1.5ms)
  Conectivitate: 100%

[DEMO 2] Pornire servere backend...
  app1 (h2:8001): started
  app2 (h3:8001): started
  Așteptare 2s pentru inițializare...

[DEMO 3] Pornire load balancer (h4:8080)...
  Load balancer: started
  Backends configurate: h2:8001, h3:8001

[DEMO 4] Pornire TCP echo server (h3:9000)...
  Echo server: started

[DEMO 5] Pornire captură pachete (interfața lb-eth0)...
  tcpdump PID: 12345
  Output: artifacts/capture_lb.pcap

[DEMO 6] Generare trafic HTTP...
  Request 1 -> 200 OK (backend: app1) 12ms
  Request 2 -> 200 OK (backend: app2) 15ms
  Request 3 -> 200 OK (backend: app1) 11ms
  Request 4 -> 200 OK (backend: app2) 13ms
  Request 5 -> 200 OK (backend: app1) 14ms
  Request 6 -> 200 OK (backend: app2) 12ms
  Request 7 -> 200 OK (backend: app1) 11ms
  Request 8 -> 200 OK (backend: app2) 16ms
  Request 9 -> 200 OK (backend: app1) 13ms
  Request 10 -> 200 OK (backend: app2) 14ms
  
  Total: 10 cereri, 10 succes, 0 erori
  Distribuție: app1=5, app2=5

[DEMO 7] Test TCP echo...
  Sent: "Hello from client"
  Received: "Hello from client"
  RTT: 2.3ms
  Status: OK

[DEMO 8] Oprire captură și analiză...
  Pachete capturate: 156
  
[ANALYZE] Sumar trafic (tshark):

=== Conversații IP ===
                                               |       <-      | |       ->      | |     Total     |
                                               | Frames  Bytes | | Frames  Bytes | | Frames  Bytes |
10.0.0.1         <-> 10.0.0.10                     38     3.2k       42     4.1k       80     7.3k
10.0.0.10        <-> 10.0.0.2                      19     1.6k       21     2.0k       40     3.6k
10.0.0.10        <-> 10.0.0.3                      18     1.5k       18     1.8k       36     3.3k

=== Cereri HTTP ===
GET / HTTP/1.1  (10 requests)
Host: 10.0.0.10:8080

=== Pachete SYN ===
10 pachete SYN detectate (10 conexiuni inițiate)

[CLEANUP] Oprire procese...
  app1: stopped
  app2: stopped
  load balancer: stopped
  echo server: stopped
  tcpdump: stopped

[CLEANUP] Curățare Mininet...

================================================================================
DEMO COMPLETAT CU SUCCES
================================================================================

Artefacte generate:
  artifacts/capture_lb.pcap (15KB)
  artifacts/tshark_summary.txt
  artifacts/http_client.log
  artifacts/report.json

Pentru analiză manuală:
  tshark -r artifacts/capture_lb.pcap -q -z conv,tcp
  tshark -r artifacts/capture_lb.pcap -Y http
```

### report.json așteptat

```json
{
  "timestamp": "2025-01-15T10:30:45",
  "demo_version": "14.0",
  "topology": {
    "hosts": ["h1", "h2", "h3", "h4"],
    "switches": ["s1", "s2"],
    "links": 5
  },
  "connectivity": {
    "h1_to_h2": {"status": "ok", "rtt_ms": 0.5},
    "h1_to_h3": {"status": "ok", "rtt_ms": 1.2},
    "h1_to_h4": {"status": "ok", "rtt_ms": 1.5}
  },
  "http_test": {
    "total_requests": 10,
    "successful": 10,
    "failed": 0,
    "avg_latency_ms": 13.1,
    "distribution": {
      "app1": 5,
      "app2": 5
    }
  },
  "tcp_echo_test": {
    "status": "ok",
    "rtt_ms": 2.3,
    "data_verified": true
  },
  "capture": {
    "file": "artifacts/capture_lb.pcap",
    "packets": 156,
    "duration_seconds": 12.5
  }
}
```

## 4. Quiz recapitulare (`python3 python/exercises/ex_14_01.py`)

### Output mod interactiv

```
================================================================================
QUIZ RECAPITULARE - REȚELE DE CALCULATOARE
================================================================================

Mod: Interactiv (self-test)
Întrebări: 21 disponibile

Apasă Enter pentru a începe sau 'q' pentru a ieși...

--------------------------------------------------------------------------------
Întrebarea 1/21:

Care este stratul OSI responsabil pentru rutarea pachetelor?

  A) Stratul Legătură de Date
  B) Stratul Rețea
  C) Stratul Transport
  D) Stratul Fizic

Răspunsul tău (A/B/C/D): B

✓ CORECT!

Explicație: Stratul Rețea (Layer 3) se ocupă de adresarea logică (IP) și 
rutarea pachetelor între rețele diferite. Routerele operează la acest nivel.

--------------------------------------------------------------------------------
Întrebarea 2/21:
...
```

### Output mod generare quiz

```bash
$ python3 python/exercises/ex_14_01.py --generate 10 --output quiz.json
```

```
Quiz generat cu 10 întrebări în: quiz.json

Sumar:
  - Straturi OSI: 2 întrebări
  - Adresare: 2 întrebări
  - TCP/UDP: 2 întrebări
  - Rutare: 1 întrebare
  - HTTP: 2 întrebări
  - Diagnostic: 1 întrebare
```

## 5. Harness verificare proiect (`python3 python/exercises/ex_14_02.py`)

### Output cu proiect funcțional

```
================================================================================
VERIFICARE PROIECT - NETWORKING
================================================================================

Configurație încărcată din: project_config.json
Verificări definite: 8

[1/8] Verificare ping h1 -> h2...
  Comandă: ping -c 3 10.0.0.2
  Rezultat: 3/3 pachete primite
  Status: PASS ✓

[2/8] Verificare ping h1 -> h3...
  Comandă: ping -c 3 10.0.0.3
  Rezultat: 3/3 pachete primite
  Status: PASS ✓

[3/8] Verificare TCP port 8001 pe h2...
  Comandă: nc -zv 10.0.0.2 8001
  Rezultat: Connection succeeded
  Status: PASS ✓

[4/8] Verificare TCP port 8001 pe h3...
  Comandă: nc -zv 10.0.0.3 8001
  Rezultat: Connection succeeded
  Status: PASS ✓

[5/8] Verificare TCP port 8080 pe h4...
  Comandă: nc -zv 10.0.0.10 8080
  Rezultat: Connection succeeded
  Status: PASS ✓

[6/8] Verificare HTTP GET /...
  Comandă: curl -s http://10.0.0.10:8080/
  Rezultat: HTTP 200, body non-empty
  Status: PASS ✓

[7/8] Verificare HTTP GET /health...
  Comandă: curl -s http://10.0.0.10:8080/health
  Rezultat: HTTP 200, body contains "healthy"
  Status: PASS ✓

[8/8] Verificare HTTP GET /lb-status...
  Comandă: curl -s http://10.0.0.10:8080/lb-status
  Rezultat: HTTP 200, JSON valid
  Status: PASS ✓

================================================================================
SUMAR VERIFICARE
================================================================================

Total verificări: 8
  PASS: 8 ✓
  FAIL: 0 ✗

Scor: 100%
Status: PROIECT FUNCȚIONAL ✓

Raport salvat în: verification_report.json
```

### Output cu erori

```
[3/8] Verificare TCP port 8001 pe h2...
  Comandă: nc -zv 10.0.0.2 8001
  Rezultat: Connection refused
  Status: FAIL ✗
  Sugestie: Verifică dacă serverul backend rulează pe h2:8001

[6/8] Verificare HTTP GET /...
  Comandă: curl -s http://10.0.0.10:8080/
  Rezultat: curl: (7) Failed to connect
  Status: FAIL ✗
  Sugestie: Verifică dacă load balancer-ul rulează și are backends configurate

================================================================================
SUMAR VERIFICARE
================================================================================

Total verificări: 8
  PASS: 5 ✓
  FAIL: 3 ✗

Scor: 62.5%
Status: PROIECT NECESITĂ CORECȚII ✗

Probleme identificate:
  1. Backend server h2:8001 nu răspunde
  2. Load balancer nu poate face forward
  3. ...
```

## 6. Captură tcpdump (`make capture`)

### Output terminal

```
[INFO] Captură pachete pe interfața eth0...
[INFO] Durată: 30 secunde (sau Ctrl+C pentru oprire)
[INFO] Output: pcap/capture_manual.pcap

tcpdump: listening on eth0, link-type EN10MB (Ethernet), capture size 262144 bytes
^C
45 packets captured
45 packets received by filter
0 packets dropped by kernel

[INFO] Captură salvată în: pcap/capture_manual.pcap
[INFO] Pentru analiză: tshark -r pcap/capture_manual.pcap
```

## 7. Analiză tshark - Comenzi utile și output

### Conversații TCP

```bash
$ tshark -r artifacts/capture_lb.pcap -q -z conv,tcp
```

```
================================================================================
TCP Conversations
Filter:<No Filter>
                                               |       <-      | |       ->      | |     Total     |    Rel    |   Duration  |
                                               | Frames  Bytes | | Frames  Bytes | | Frames  Bytes |   Start   |             |
10.0.0.1:45678     <-> 10.0.0.10:8080             19     1.6k      21     2.0k      40     3.6k     0.000000         3.2
10.0.0.10:34567    <-> 10.0.0.2:8001               9      800      10      920      19     1.7k     0.001234         1.5
10.0.0.10:34568    <-> 10.0.0.3:8001               9      800       9      880      18     1.6k     0.102345         1.4
================================================================================
```

### Cereri HTTP

```bash
$ tshark -r artifacts/capture_lb.pcap -Y http.request -T fields -e http.request.method -e http.host -e http.request.uri
```

```
GET	10.0.0.10:8080	/
GET	10.0.0.10:8080	/
GET	10.0.0.10:8080	/health
GET	10.0.0.10:8080	/
GET	10.0.0.10:8080	/
```

### Doar pachete SYN

```bash
$ tshark -r artifacts/capture_lb.pcap -Y "tcp.flags.syn==1 && tcp.flags.ack==0"
```

```
  1   0.000000 10.0.0.1 → 10.0.0.10 TCP 74 45678 → 8080 [SYN]
  5   0.001234 10.0.0.10 → 10.0.0.2 TCP 74 34567 → 8001 [SYN]
 11   0.102345 10.0.0.1 → 10.0.0.10 TCP 74 45679 → 8080 [SYN]
```

---

## Note

1. **Valorile exacte variază** - Timestamp-uri, RTT-uri și PID-uri vor fi diferite la fiecare rulare
2. **Ordinea backend-urilor** - Round-robin, dar prima cerere poate merge la oricare
3. **Dimensiuni pachete** - Depind de payload și opțiunile TCP
4. **Erori posibile** - Dacă porturile sunt ocupate sau Mininet nu e instalat corect

---
*Revolvix&Hypotheticalandrei*
