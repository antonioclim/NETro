---
title: "Curs 10, Seminar 10, Laborator 10"
subtitle: "HTTP(S), REST, SOAP – Nivel Aplicație | DNS, SSH, FTP în Docker"
author: "Rețele de Calculatoare – Informatică Economică, An 3, Sem. 2"
date: "ASE București, 2025-2026"
geometry: margin=2.5cm
fontsize: 11pt
documentclass: article
header-includes:
  - \usepackage{fancyhdr}
  - \pagestyle{fancy}
  - \fancyhead[R]{Rețele de Calculatoare – Săptămâna 10}
  - \fancyfoot[C]{\thepage}
  - \fancyfoot[R]{Revolvix\&Hypotheticalandrei}
---

\newpage

# 1. Scopul Săptămânii

## Ce vom învăța

Această săptămână explorează **nivelul aplicație** al modelului OSI/TCP-IP prin două perspective complementare:

- **Curs:** HTTP(S), REST, SOAP – protocoale și stiluri arhitecturale pentru comunicația client-server
- **Seminar/Laborator:** DNS, SSH, FTP – servicii fundamentale de rețea, automatizate în containere Docker

> **📋 Notă instructor:** Timing recomandat: 20 min teorie HTTP, 15 min REST/SOAP, 25 min seminar services, 30 min laborator practic. Între sesiuni, lăsați 5 min pentru întrebări.

## De ce contează

Un programator care înțelege nivelul aplicație poate:

1. **Diagnostica rapid** probleme de integrare ("merge în Postman dar nu în browser")
2. **Optimiza performanța** prin înțelegerea caching-ului și multiplexării HTTP/2
3. **Proiecta API-uri corecte** care respectă semantica HTTP și principiile REST
4. **Automatiza infrastructura** prin scripting DNS, SSH, FTP în Python
5. **Comunica eficient** cu echipe DevOps folosind vocabular tehnic precis

> **💡 Pentru student:** Aceste competențe sunt cerute explicit în interviurile tehnice pentru poziții de backend developer și DevOps engineer.

\newpage

# 2. Prerechizite și Recapitulare

## Din săptămânile anterioare

| Săptămâna | Concept | Relevanță pentru S10 |
|-----------|---------|----------------------|
| S3-S5 | Adresare IP, porturi, socket-uri | Fundament pentru servicii TCP/UDP |
| S8 | TCP handshake, control flux | HTTP funcționează peste TCP |
| S9 | TLS/Certificate | HTTPS = HTTP + TLS |
| Teh. Web | REST APIs (practică) | Acum înțelegem protocolul |

## Recapitulare ultra-scurtă

- **TCP 3-way handshake:** SYN → SYN-ACK → ACK (1 RTT pentru stabilire conexiune)
- **TLS handshake:** ClientHello → ServerHello+Certificate → Finished (1-2 RTT adiționale)
- **Porturi well-known:** HTTP=80, HTTPS=443, SSH=22, FTP=21, DNS=53

> **📋 Notă instructor:** Dacă grupul pare nesigur pe aceste concepte, alocați 10 minute pentru recapitulare înainte de a continua.

\newpage

# 3. Curs: HTTP(S), REST și SOAP

## 3.1 HTTP în arhitectura Internet

HTTP funcționează la **nivelul aplicație (L7)** și se bazează pe:

- **TCP** pentru transport fiabil (sau QUIC în HTTP/3)
- **TLS** pentru confidențialitate și autentificare în HTTPS
- **DNS** pentru rezolvarea numelor de domeniu

### Costul real al unei cereri HTTPS

| Component | Latență tipică |
|-----------|----------------|
| TCP Handshake | 1 RTT |
| TLS Handshake | 1-2 RTT |
| HTTP Request/Response | 1 RTT |
| **TOTAL** | **3-4 RTT (~150-200ms pentru RTT=50ms)** |

> **💡 Pentru student:** Prima cerere HTTPS durează minimum 150-200ms. De aceea connection reuse și HTTP/2 sunt importante pentru performanță.

## 3.2 Semantica HTTP

### Metode HTTP și proprietățile lor

| Metodă | Sigură | Idempotentă | Cacheable | Descriere |
|--------|--------|-------------|-----------|-----------|
| GET | ✓ | ✓ | ✓ | Citire resursă |
| HEAD | ✓ | ✓ | ✓ | Doar headere |
| POST | ✗ | ✗ | Condiționat | Creare/submit |
| PUT | ✗ | ✓ | ✗ | Înlocuire completă |
| PATCH | ✗ | ✗ | ✗ | Modificare parțială |
| DELETE | ✗ | ✓ | ✗ | Ștergere resursă |

- **Siguranța** înseamnă că cererea nu modifică starea serverului.
- **Idempotența** înseamnă că rezultatul este identic indiferent de câte ori se execută cererea.

> **📋 Notă instructor:** Întrebare de control: De ce PUT este idempotent dar POST nu? **Răspuns:** PUT înlocuiește complet resursa (același rezultat la repetare), POST creează resurse noi (duplicare la repetare).

### Coduri de status – nuanțe importante

**Autentificare vs Autorizare:**

- `401 Unauthorized` – lipsește autentificarea ("Cine ești?")
- `403 Forbidden` – autentificat, dar fără acces ("Nu ai voie")

**Resurse vs Conținut:**

- `404 Not Found` – resursa nu există
- `405 Method Not Allowed` – resursa există, metoda nu e permisă
- `422 Unprocessable Entity` – format valid, dar semantică invalidă (ex: cantitate negativă)

```python
# Exemplu practic
GET /api/orders/999     → 404 (comanda 999 nu există)
DELETE /api/orders      → 405 (nu poți șterge colecția)
POST /api/orders
Content-Type: image/png → 415 (nu acceptă imagini)
POST /api/orders
{"quantity": -5}        → 422 (cantitate invalidă)
```

## 3.3 Headere HTTP critice

### Content Negotiation

```http
# Clientul specifică ce preferă
Accept: application/json, text/html;q=0.9
Accept-Language: ro-RO, en;q=0.8
Accept-Encoding: gzip, br

# Serverul răspunde cu ce oferă
Content-Type: application/json; charset=utf-8
Content-Encoding: gzip
```

### Caching HTTP

```http
# Server indică politica de cache
Cache-Control: max-age=3600, must-revalidate
ETag: "v1.2.3-abc"

# Client revalidează (cerere condițională)
If-None-Match: "v1.2.3-abc"

# Server poate răspunde 304 Not Modified (fără body)
```

**Întrebare de verificare:** Ce economisește un 304 Not Modified?

## 3.4 CORS – Cross-Origin Resource Sharing

CORS **nu** este o limitare a HTTP – este o **politică de securitate a browserului**. Protejează utilizatorii de site-uri malițioase.

**Regulă de aur:** *"Merge în Postman dar nu în browser" = problemă CORS*

> **💡 Pentru student:** Postman nu este un browser și nu aplică politica same-origin. De aceea testele din Postman nu reflectă comportamentul real din aplicații web.

### Preflight Request

Pentru cereri "nesimple" (POST cu JSON, headere custom), browserul trimite automat OPTIONS:

```http
OPTIONS /api/users HTTP/1.1
Origin: https://frontend.com
Access-Control-Request-Method: POST
Access-Control-Request-Headers: Content-Type

HTTP/1.1 204 No Content
Access-Control-Allow-Origin: https://frontend.com
Access-Control-Allow-Methods: GET, POST, PUT, DELETE
Access-Control-Allow-Headers: Content-Type
```

## 3.5 HTTP/1.1 vs HTTP/2

### Limitările HTTP/1.1

1. **Head-of-Line Blocking** – cererile se procesează secvențial pe conexiune
2. **Headere repetate** – același Host, User-Agent la fiecare cerere
3. **Conexiuni multiple** – browserele deschid 6-8 conexiuni per domeniu

### Îmbunătățiri HTTP/2

1. **Multiplexare** – multiple stream-uri pe aceeași conexiune TCP
2. **Compresie headere** (HPACK) – doar diferențele se trimit
3. **Prioritizare** – clientul indică importanța stream-urilor
4. **Server Push** – serverul anticipează resurse (opțional)

**Important:** Semantica HTTP rămâne **identică** – același GET, POST, headere, coduri.

## 3.6 Richardson Maturity Model

Modelul măsoară "RESTfulness" unui API:

- **Nivel 0:** RPC over HTTP (toate cererile POST /api)
- **Nivel 1:** Resurse identificate (/api/users/123)
- **Nivel 2:** Verbe HTTP + coduri de status corecte
- **Nivel 3:** HATEOAS – hypermedia controls în răspunsuri

### Anti-patterns REST

❌ `POST /api/users/123/activate` – acțiune în URL  
❌ `200 OK {"error": "Not found"}` – cod greșit pentru eroare  
❌ `GET /api/deleteUser?id=123` – efect secundar pe GET

## 3.7 REST vs SOAP

| Aspect | REST | SOAP |
|--------|------|------|
| Format | JSON (tipic) | XML (obligatoriu) |
| Contract | OpenAPI (opțional) | WSDL (obligatoriu) |
| Transport | HTTP | HTTP, SMTP, JMS... |
| Caching | Nativ HTTP | Complex, manual |
| Complexitate | Simplă | Enterprise |

**Când SOAP?** Tranzacții distribuite, securitate avansată (WS-Security), contracte stricte între organizații.

\newpage

# 4. Seminar: DNS, SSH, FTP în Docker

## 4.1 Arhitectura infrastructurii

Seminarul folosește **6 containere Docker** pe o rețea privată (172.20.0.0/24):

```
┌──────────────────────────────────────────────────────────────┐
│                   Rețea Docker (labnet)                      │
│                      172.20.0.0/24                           │
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐      │
│  │   web    │  │   dns-   │  │   ssh-   │  │   ftp-  │      │
│  │  :8000   │  │  server  │  │  server  │  │  server │      │
│  │ (Flask)  │  │  :5353   │  │   :22    │  │  :2121  │      │
│  └──────────┘  └──────────┘  └──────────┘  └─────────┘      │
│                                                              │
│  ┌──────────┐  ┌──────────┐                                  │
│  │   ssh-   │  │  debug   │                                  │
│  │  client  │  │ (tools)  │                                  │
│  └──────────┘  └──────────┘                                  │
└──────────────────────────────────────────────────────────────┘
       │              │              │              │
    Host:          :5353/udp       :2222          :2121
```

> **💡 Pentru student:** Pornire rapidă: `cd docker/ && docker compose up -d --build`. Verifică cu: `docker compose ps`.

## 4.2 DNS – Domain Name System

### Recapitulare conceptuală

DNS traduce **nume în adrese IP**:

| Tip | Descriere | Exemplu |
|-----|-----------|---------|
| **A** | Nume → IPv4 | `example.com → 93.184.216.34` |
| **AAAA** | Nume → IPv6 | `example.com → 2606:2800:...` |
| **CNAME** | Alias | `www → example.com` |
| **MX** | Mail server | `example.com → mail.example.com` |

### DNS în Docker

Docker oferă **DNS intern automat** pe rețelele user-defined, dar nu suportă zone custom sau înregistrări MX/SRV/TXT.

### Demonstrație pas cu pas

1. Intră în containerul debug: `docker compose exec debug sh`
2. Test DNS Docker implicit: `dig web +short` (returnează IP container)
3. Test DNS custom: `dig @dns-server -p 5353 myservice.lab.local +short`

### Rezultate așteptate

```bash
$ dig @dns-server -p 5353 myservice.lab.local +short
10.10.10.10

$ dig @dns-server -p 5353 api.lab.local +short
10.10.10.20
```

> **📋 Notă instructor:** Întrebare de verificare: Care este diferența între `dig web` și `dig @dns-server myservice.lab.local`? (DNS Docker vs DNS custom)

## 4.3 SSH – Secure Shell

SSH oferă:

- **Conexiune securizată** la servere remote
- **Execuție comenzi** la distanță
- **Transfer fișiere** (SFTP, SCP)
- **Tunelare trafic** (port forwarding)

### Port Forwarding

**Local forward (-L):** Acces la serviciu remote ca și cum ar fi local

```bash
ssh -L 9000:web:8000 -p 2222 labuser@localhost
# Acum: curl http://localhost:9000 accesează web:8000 prin tunel
```

**Remote forward (-R):** Expune serviciu local pe server remote

```bash
ssh -R 9000:localhost:3000 user@server
# Pe server: localhost:9000 accesează mașina ta pe :3000
```

**Dynamic forward (-D):** Proxy SOCKS5

```bash
ssh -D 1080 user@server
# Configurezi browser-ul să folosească SOCKS5 localhost:1080
```

> **💡 Pentru student:** Port forwarding este util când serviciul intern (web:8000) nu este expus pe host. Tunelul SSH criptează tot traficul.

## 4.4 FTP – File Transfer Protocol

FTP folosește **două conexiuni**:

- **Port 21:** Canal de control (comenzi)
- **Port 20** sau porturi pasive: Canal de date

### Mod activ vs mod pasiv

| Mod | Funcționare | NAT/Firewall |
|-----|-------------|--------------|
| **Activ** | Serverul se conectează la client | Problematic (conexiune inversă) |
| **Pasiv** (recomandat) | Clientul se conectează la server | Funcționează |

> **📋 Notă instructor:** Demonstrați observarea traficului FTP cu tcpdump – comenzile (USER, PASS, STOR) sunt în plaintext!

\newpage

# 5. Laborator Practic

## 5.1 Setup mediu (10 min)

```bash
# Instalează dependențe Python
make setup

# Pornește infrastructura Docker
make docker-up

# Verifică că toate serviciile răspund
make verify
```

**Output așteptat:**
```
NAME           SERVICE       STATUS
dns-server     dns-server    running
ftp-server     ftp-server    running
ssh-server     ssh-server    running
debug          debug         running
web            web           running
```

## 5.2 Explorare DNS (15 min)

**Task:** Compară DNS implicit Docker cu DNS custom.

```bash
docker compose exec debug sh
dig web +short           # DNS Docker implicit
dig @dns-server -p 5353 myservice.lab.local  # DNS custom
```

**What-if:** Ce se întâmplă dacă modifici TTL-ul în serverul DNS? Observă diferența în răspunsuri repetate.

## 5.3 SSH cu Paramiko (20 min)

**Task:** Automatizează conexiunea SSH și execută comenzi.

```bash
# Conectare manuală (test)
ssh -p 2222 labuser@localhost  # Parolă: labpass

# Automatizare Paramiko
docker compose exec ssh-client python3 /app/paramiko_client.py
```

**Script Python exemplu:**

```python
import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect("localhost", 2222, "labuser", "labpass")

stdin, stdout, stderr = client.exec_command("uname -a")
print(stdout.read().decode())

client.close()
```

## 5.4 Port Forwarding (15 min)

**Task:** Accesează serviciul web (neexpus) prin tunel SSH.

```bash
# Terminal 1: Crează tunel
ssh -L 9000:web:8000 -p 2222 labuser@localhost -N

# Terminal 2: Test acces
curl http://localhost:9000/
```

**Explicație:** `localhost:9000` → tunel SSH → `ssh-server` → `web:8000`

**What-if:** Ce se întâmplă dacă oprești tunelul și încerci curl?

## 5.5 Transfer FTP (15 min)

**Task:** Upload și download fișiere prin FTP programatic.

```python
from ftplib import FTP
import io

ftp = FTP()
ftp.connect('localhost', 2121)
ftp.login('labftp', 'labftp')

# Listare
print(f"Director curent: {ftp.pwd()}")
print(f"Conținut: {ftp.nlst()}")

# Upload test
content = "Test content\n"
data = io.BytesIO(content.encode())
ftp.storbinary('STOR uploads/test.txt', data)
print("[OK] Fișier uploadat")

ftp.quit()
```

## 5.6 Integrare completă (20 min)

**Task:** Creează script care verifică toate serviciile și generează raport JSON.

Vezi fișierul `python/exercises/lab10_integration.py` din starterkit.

**Output așteptat:**

```json
{
  "timestamp": "2025-01-15T10:30:00Z",
  "dns": {"status": "ok", "response": "10.10.10.10"},
  "ssh": {"status": "ok", "hostname": "ssh-server"},
  "ftp": {"status": "ok", "files": ["welcome.txt", "uploads"]}
}
```

\newpage

# 6. Greșeli Frecvente și Debugging

## Tabel probleme comune

| Problemă | Cauză | Soluție |
|----------|-------|---------|
| `Connection refused` | Serviciu nepornit | `docker compose up -d` |
| `Name not resolved` | DNS greșit sau rețea diferită | `docker network ls` |
| `Permission denied (SSH)` | Credențiale greșite | Verifică user/parolă în compose |
| `Passive mode failed (FTP)` | Porturi pasive neexpuse | Adaugă port range 30000-30009 |
| `Host key verification` | Cheie SSH schimbată | `ssh-keygen -R localhost` |
| `CORS error în browser` | Politică same-origin | Configurează headere CORS pe server |

## Instrumente de debugging

```bash
# Verifică logurile serviciului
docker compose logs <service>

# Captură pachete pe portul X
tcpdump -i any port X -A

# Debugging HTTP verbose
curl -v URL

# Debugging SSH verbose
ssh -v user@host
```

> **📋 Notă instructor:** La debugging, întrebați studenții: Ce ai încercat? Ce eroare ai primit? La ce pas s-a blocat? Ghidați-i spre diagnoză sistematică.

\newpage

# 7. Exerciții de Consolidare

## Nivel Începător

**Ex. 1: DNS Query Manual.** Folosește `dig` pentru a interoga serverul DNS custom pentru domeniul `api.lab.local`. Notează TTL-ul din răspuns.

**Ex. 2: SSH Manual.** Conectează-te SSH la `ssh-server`, execută `uname -a` și `df -h`, apoi deconectează-te.

## Nivel Intermediar

**Ex. 3: Paramiko Script.** Scrie un script Python care se conectează SSH, creează un fișier pe server, apoi îl descarcă prin SFTP.

**Ex. 4: Port Forwarding Complex.** Creează un tunel SSH care permite accesul la serverul FTP (port 2121) prin SSH. Testează cu `ftp localhost <port_local>`.

## Nivel Avansat

**Ex. 5: Health Check Automat.** Creează un script Python care verifică periodic (la 30s) disponibilitatea DNS, SSH, FTP și trimite alertă (print) dacă unul dintre servicii nu răspunde.

## Challenge

**Ex. 6: FTP Mirror prin SSH Tunnel.** Implementează un script care:
1. Creează tunel SSH către FTP server
2. Se conectează FTP prin tunel
3. Sincronizează un director local cu serverul FTP

> **💡 Pentru student:** Pentru challenge, vei avea nevoie de threading pentru tunelul SSH și ftplib pentru transfer. Consideră biblioteca `sshtunnel` pentru simplificare.

\newpage

# 8. Mini-Reflecție

## Ce am învățat

- HTTP nu este doar "ce trimite browser-ul" – are semantică precisă (metode, coduri, headere)
- REST înseamnă folosirea corectă a HTTP, nu doar "JSON over POST"
- CORS protejează utilizatorii – nu e bug, e feature
- DNS, SSH, FTP sunt fundamente pe care se construiesc sisteme complexe
- Automatizarea cu Python face operațiunile repetabile și scalabile

## Unde se folosește în practică

- **Backend Development:** Design API REST, integrare cu servicii externe
- **DevOps:** Automatizare deployment, configurare servicii, monitoring
- **Security:** Audit trafic, configurare tuneluri securizate
- **Cloud Engineering:** Orchestrare containere, service discovery

## Întrebări de autoevaluare

1. Poți explica diferența între 401 și 403?
2. Știi de ce PUT este idempotent dar POST nu?
3. Poți crea un tunel SSH pentru a accesa un serviciu intern?
4. Poți scrie un script Python care se conectează SSH și transferă fișiere?

> **📋 Notă instructor:** Dacă studenții răspund "da" la toate întrebările, obiectivele săptămânii au fost atinse.

\newpage

# 9. Contribuția la Proiectul de Echipă

## Artefact livrabil S10

**`lab10_automation.py`** – Script de automatizare servicii

### Cerințe funcționale

1. Verifică disponibilitatea serviciilor (DNS, SSH, FTP)
2. Execută query DNS pentru un domeniu configurat
3. Se conectează SSH și execută o comandă de diagnostic
4. Transferă un fișier de test prin FTP
5. Generează raport JSON cu toate rezultatele

## Rubrica de evaluare

| Criteriu | Puncte | Observații |
|----------|--------|------------|
| Verificare disponibilitate servicii | 2p | Toate 3 serviciile verificate |
| Query DNS funcțional | 1.5p | Folosește dnspython sau socket |
| Conectare SSH + execuție comandă | 2p | Paramiko cu tratare erori |
| Transfer FTP programatic | 1.5p | ftplib cu upload/download |
| Raport JSON structurat | 1p | Include timestamp, status |
| Cod documentat și tratare erori | 2p | Docstrings + try/except |
| **TOTAL** | **10p** | |

> **💡 Pentru student:** Scriptul poate fi integrat în proiectul final ca modul de health checking pentru infrastructura echipei.

\newpage

# 10. Bibliografie și Resurse

## Referințe academice (cu DOI)

| Autori | Titlu / Publicație | DOI |
|--------|-------------------|-----|
| Fielding, R.T., Reschke, J. | HTTP/1.1: Semantics and Content (RFC 7231) | 10.17487/RFC7231 |
| Belshe, M., Peon, R., Thomson, M. | HTTP/2 (RFC 7540) | 10.17487/RFC7540 |
| Berners-Lee, T., Fielding, R., Masinter, L. | URI: Generic Syntax (RFC 3986) | 10.17487/RFC3986 |
| Fette, I., Melnikov, A. | WebSocket Protocol (RFC 6455) | 10.17487/RFC6455 |
| Rescorla, E. | TLS 1.3 (RFC 8446) | 10.17487/RFC8446 |
| Mockapetris, P. | DNS Implementation (RFC 1035) | 10.17487/RFC1035 |
| Ylonen, T., Lonvick, C. | SSH Protocol Architecture (RFC 4251) | 10.17487/RFC4251 |
| Postel, J., Reynolds, J. | FTP (RFC 959) | 10.17487/RFC959 |

## Standarde și specificații

- RFC 7230-7235: HTTP/1.1 Complete Specification
- OpenAPI Specification 3.1: https://spec.openapis.org/oas/v3.1.0
- Richardson Maturity Model: https://martinfowler.com/articles/richardsonMaturityModel.html
- Docker Networking: https://docs.docker.com/network/

## Documentație biblioteci Python

- Paramiko: https://docs.paramiko.org/
- pyftpdlib: https://pyftpdlib.readthedocs.io/
- dnslib: https://pypi.org/project/dnslib/
- requests: https://docs.python-requests.org/

## Cărți recomandate

- *Kurose, J., Ross, K.* Computer Networking: A Top-Down Approach, 8th Ed. Pearson, 2021.
- *Rhodes, B., Goerzen, J.* Foundations of Python Network Programming, 3rd Ed. Apress, 2014.
- *Richardson, L., Ruby, S.* RESTful Web Services. O'Reilly Media, 2007.

---

*Material elaborat pentru disciplina Rețele de Calculatoare*  
*Academia de Studii Economice București, CSIE, 2025-2026*  
*Revolvix&Hypotheticalandrei*
