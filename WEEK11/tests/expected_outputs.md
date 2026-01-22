# Ieșiri Așteptate – Săptămâna 11

## Artefacte generate de `run_all.sh`

### `artifacts/demo.log`

Fișier de log care conține:
- Timestamp-uri pentru fiecare pas
- Output-ul cererilor HTTP către load balancer
- Distribuția cererilor între backend-uri (B1, B2, B3)
- Rezultatul health check

**Exemplu conținut minim:**
```
[2025-01-02 10:00:00] [INFO] Demo automat pentru WEEK 11
[2025-01-02 10:00:01] [1/6] Verificare Docker...
[2025-01-02 10:00:02] [OK] Docker disponibil.
...
=== TEST ROUND-ROBIN ===
Request 1: Backend 1 | Host: s11_backend_1 | Time: ...
Request 2: Backend 2 | Host: s11_backend_2 | Time: ...
Request 3: Backend 3 | Host: s11_backend_3 | Time: ...
...
```

### `artifacts/demo.pcap`

Captură de trafic care conține:
- Pachete TCP pe portul 8080
- Cereri HTTP GET către Nginx
- Răspunsuri HTTP de la backend-uri

**Verificare:**
```bash
# Afișare statistici
tshark -r artifacts/demo.pcap -q -z conv,tcp

# Afișare cereri HTTP
tshark -r artifacts/demo.pcap -Y "http.request" -T fields -e http.host -e http.request.uri
```

**Așteptări:**
- Minim 9 conexiuni TCP (câte una per cerere)
- Toate conexiunile către `localhost:8080`

### `artifacts/validation.txt`

Raport de validare care conține:
- Status containere Docker
- Statistici distribuție load balancing
- Verificări PASS/FAIL/WARN

**Exemplu conținut:**
```
=== VALIDATION REPORT - WEEK 11 ===
Timestamp: 2025-01-02 10:00:15

--- Docker Status ---
NAME                IMAGE         STATUS
s11_nginx_lb        nginx:alpine  Up 10 seconds
s11_backend_1       nginx:alpine  Up 12 seconds
s11_backend_2       nginx:alpine  Up 12 seconds
s11_backend_3       nginx:alpine  Up 12 seconds

--- Load Balancing Distribution ---
Backend 1: 3 requests
Backend 2: 3 requests
Backend 3: 3 requests

--- Validation Checks ---
PASS: Toate backend-urile au primit cereri
PASS: Total cereri corect (9)
PASS: Health check endpoint funcțional
```

## Comportament așteptat

### Round-Robin Distribution

Cu 9 cereri și 3 backend-uri, așteptăm:
- Backend 1: ~3 cereri
- Backend 2: ~3 cereri
- Backend 3: ~3 cereri

Distribuția trebuie să fie echilibrată (±1 cerere diferență acceptabilă din cauza timing-ului).

### Health Check

Endpoint-ul `/health` trebuie să returneze:
```
HTTP/1.1 200 OK
Content-Type: text/plain
OK
```

### Smoke Test Exit Codes

| Cod | Semnificație |
|-----|--------------|
| 0   | Toate verificările au trecut |
| 1-9 | Număr de erori găsite |

---

*Revolvix&Hypotheticalandrei*
