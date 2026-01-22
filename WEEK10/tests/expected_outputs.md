# Expected Outputs - Săptămâna 10

## Artefacte Generate de `run_all.sh`

După rularea cu succes a `scripts/run_all.sh`, directorul `artifacts/` trebuie să conțină:

### 1. `demo.log`

**Dimensiune minimă:** ~5-10 KB  
**Conținut așteptat:**

```
# Demo Log - Săptămâna 10
# Timestamp: [data curentă]
# Porturi: DNS=5353 SSH=2222 FTP=2121 HTTP=8000

[HH:MM:SS] [STEP] Verificare prerequisite...
[HH:MM:SS] [INFO] Docker funcțional
[HH:MM:SS] [STEP] Pornire infrastructură Docker...
[HH:MM:SS] [INFO] Containere pornite
[HH:MM:SS] [STEP] ═══════════════════════════════════════
[HH:MM:SS] [STEP]          TEST DNS SERVER
[HH:MM:SS] [INFO] ✓ DNS implicit funcționează
[HH:MM:SS] [INFO] ✓ DNS custom răspunde: 10.10.10.10
...
```

**Marcaje obligatorii:**
- `TEST DNS SERVER`
- `TEST SSH SERVER`
- `TEST FTP SERVER`
- `TEST WEB SERVER`

---

### 2. `demo.pcap`

**Dimensiune minimă:** >24 bytes (header PCAP)  
**Dimensiune tipică:** 10-100 KB

**Conținut așteptat (vizualizabil cu tshark/Wireshark):**
- Pachete DNS pe port UDP 5353
- Conexiuni TCP pe porturile 2222 (SSH), 2121 (FTP), 8000 (HTTP)
- Handshake-uri TCP (SYN, SYN-ACK, ACK)

**Verificare rapidă:**
```bash
tshark -r artifacts/demo.pcap -c 10
```

**Output exemplu:**
```
    1   0.000000 172.20.0.200 → 172.20.0.53  DNS 75 Standard query 0x1234 A myservice.lab.local
    2   0.001234 172.20.0.53 → 172.20.0.200 DNS 91 Standard query response ...
    3   0.002000 172.20.0.200 → 172.20.0.22  TCP 74 [SYN] Seq=0 ...
```

**Notă:** Dacă `tshark`/`tcpdump` nu este instalat, fișierul poate fi gol (doar header) sau lipsă. Aceasta NU este o eroare critică.

---

### 3. `validation.txt`

**Format:** Perechi cheie:rezultat, una per linie

**Conținut așteptat (succes complet):**
```
# Validation Results - Week 10
# Timestamp: [data curentă]

dns_implicit:PASS
dns_custom:PASS:10.10.10.10
dns_host:PASS
ssh_port:PASS
ssh_banner:PASS
ssh_paramiko:PASS
ftp_port:PASS
ftp_banner:PASS
ftp_list:PASS
http_host:PASS
http_docker_dns:PASS

# Sumar - [data]
TOTAL_TESTS=11
PASSED=11
FAILED=0
```

**Rezultate posibile:**
- `PASS` - Test trecut
- `FAIL` - Test eșuat
- `PARTIAL` - Test parțial trecut (funcționalitate de bază OK, dar nu completă)

**Teste critice (trebuie să fie PASS):**
- `dns_implicit` - DNS implicit Docker funcționează
- `ssh_port` - Port SSH deschis
- `ftp_port` - Port FTP deschis
- `http_host` - HTTP accesibil de pe host

---

## Verificare cu Smoke Test

```bash
./tests/smoke_test.sh
```

**Output așteptat (succes):**
```
╔═══════════════════════════════════════════════════════════════════════════════╗
║  SMOKE TEST - SĂPTĂMÂNA 10 - SERVICII DE REȚEA                                ║
║  Verificare artefacte și structură                                            ║
╚═══════════════════════════════════════════════════════════════════════════════╝

═══════════════════════════════════════════
  Verificare: Structură directoare
═══════════════════════════════════════════
[PASS] Director scripts/ există
[PASS] Director docker/ există
[PASS] Director python/ există
[PASS] Director artifacts/ există
[PASS] Director docs/ există
[PASS] Fișier scripts/setup.sh există
[PASS] Fișier scripts/run_all.sh există
...

═══════════════════════════════════════════
  Verificare: demo.log
═══════════════════════════════════════════
[PASS] demo.log există (8234 bytes)
[PASS] demo.log are conținut substanțial (156 linii)
[PASS] demo.log conține teste DNS
[PASS] demo.log conține teste SSH
[PASS] demo.log conține teste FTP

═══════════════════════════════════════════
  Verificare: demo.pcap
═══════════════════════════════════════════
[PASS] demo.pcap există (45678 bytes)
[PASS] demo.pcap are date capturate (45678 bytes)

═══════════════════════════════════════════
  Verificare: validation.txt
═══════════════════════════════════════════
[PASS] validation.txt există (512 bytes)
[PASS] validation.txt conține 11 teste PASS
[PASS] validation.txt conține sumar

╔═══════════════════════════════════════════════════════════════════════════════╗
║                           SUMAR SMOKE TEST                                    ║
╚═══════════════════════════════════════════════════════════════════════════════╝

  Total teste:  18
  Trecute:      18
  Eșuate:       0

╔═══════════════════════════════════════════════════════════════════════════════╗
║  ✓ SMOKE TEST TRECUT - TOATE VERIFICĂRILE OK                                  ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

---

## Comportament în Caz de Erori

### DNS custom nu răspunde

**Cauză probabilă:** Container `dns-server` nu a pornit corect  
**Diagnostic:**
```bash
docker compose -f docker/docker-compose.yml logs dns-server
docker compose -f docker/docker-compose.yml exec debug dig @dns-server -p 5353 myservice.lab.local
```

**validation.txt va conține:**
```
dns_custom:FAIL
```

### SSH connection refused

**Cauză probabilă:** `sshd` nu rulează în container  
**Diagnostic:**
```bash
docker compose -f docker/docker-compose.yml exec ssh-server pgrep sshd
docker compose -f docker/docker-compose.yml logs ssh-server
```

**validation.txt va conține:**
```
ssh_port:FAIL
ssh_banner:FAIL
ssh_paramiko:FAIL
```

### FTP banner lipsește

**Cauză probabilă:** `pyftpdlib` a eșuat la pornire  
**Diagnostic:**
```bash
docker compose -f docker/docker-compose.yml logs ftp-server
nc -v localhost 2121
```

### Captură PCAP goală

**Cauze posibile:**
1. `tshark`/`tcpdump` nu este instalat
2. Permisiuni insuficiente (necesită sudo pentru tcpdump)
3. Interfața de rețea nu a capturat trafic

**Aceasta NU este o eroare critică** - captura este opțională pentru verificare.

---

## Criterii de Evaluare Automată

| Criteriu | Pondere | Verificare |
|----------|---------|------------|
| Artefacte generate | 20% | Existența demo.log, demo.pcap, validation.txt |
| DNS funcțional | 20% | dns_implicit:PASS, dns_custom:PASS |
| SSH funcțional | 20% | ssh_port:PASS, ssh_paramiko:PASS |
| FTP funcțional | 20% | ftp_port:PASS, ftp_list:PASS |
| HTTP funcțional | 20% | http_host:PASS, http_docker_dns:PASS |

**Notă minimă de trecere:** 50% (minim 5 teste PASS din 10 critice)

---

## Notă

Aceste output-uri sunt generate automat de `scripts/run_all.sh`. Pentru reproducerea exactă:

1. Asigurați-vă că Docker rulează
2. Nu există alte servicii pe porturile 5353, 2222, 2121, 8000
3. Rulați din directorul rădăcină al kit-ului

```bash
cd /path/to/WEEK10
./scripts/run_all.sh
./tests/smoke_test.sh
```
