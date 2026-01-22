# Curs 10: HTTP(S), REST și SOAP – Nivel Aplicație

**Disciplina:** Rețele de Calculatoare  
**Program:** Informatică Economică, ASE București  
**Semestrul:** 2, Anul 3  

---

## Ce vom învăța

Studiem **nivelul aplicație** prin prisma protocolului HTTP și a stilurilor arhitecturale REST/SOAP. Spre deosebire de cursurile anterioare de tehnologii web unde accentul cădea pe construirea de aplicații, aici ne concentrăm pe:

- Mecanismele protocolului HTTP (semantică, headere, coduri status)
- Diferențele operaționale între HTTP/1.1, HTTP/2 și WebSocket
- Principiile REST și modelul de maturitate Richardson
- Comparația REST vs SOAP în context enterprise
- Diagnosticarea și depanarea problemelor de protocol

---

## De ce contează

Un programator care înțelege HTTP la nivel de protocol poate:

1. **Diagnostica rapid** probleme de integrare („merge în Postman dar nu în browser")
2. **Optimiza performanța** prin înțelegerea caching-ului și multiplexării
3. **Proiecta API-uri corecte** care respectă semantica HTTP
4. **Depana eficient** folosind curl, tcpdump, Wireshark, DevTools
5. **Comunica precis** cu echipe de infrastructură și DevOps
6. **Anticipa probleme** de integrare cu servicii terțe înainte să apară

---

## Prerechizite

Din **Săptămânile 1-9** se presupun cunoscute:
- TCP handshake, control flux, controlul congestiei (S8)
- TLS/certificatele (menționat în context HTTPS) (S9)
- Adresarea IP, porturile, socket-urile (S3, S5)
- Experiența practică cu REST APIs din cursul de Tehnologii Web

---

## 1. HTTP în Arhitectura Internet

### Poziționarea HTTP

HTTP funcționează la **nivelul aplicație** (L7) și se bazează pe:
- **TCP** pentru transport fiabil (sau QUIC în HTTP/3)
- **TLS** pentru confidențialitate și autentificare în HTTPS
- **DNS** pentru rezolvarea numelor de domeniu

### Structura unui schimb HTTP/1.1

```
Client                                 Server
   |                                      |
   |---- TCP SYN ----------------------->|
   |<--- TCP SYN-ACK --------------------|
   |---- TCP ACK ----------------------->|  (1 RTT)
   |                                      |
   |---- TLS ClientHello --------------->|
   |<--- TLS ServerHello + Cert ---------|
   |---- TLS Finished ------------------>|  (+1-2 RTT)
   |                                      |
   |---- HTTP GET /api/users ----------->|
   |<--- HTTP 200 OK + JSON body --------|  (+1 RTT)
```

### Costul real al unei cereri HTTPS

| Component | Latență tipică |
|-----------|----------------|
| TCP Handshake | 1 RTT |
| TLS Handshake | 1-2 RTT |
| HTTP Request/Response | 1 RTT |
| **Total** | **3-4 RTT** |

Pentru RTT = 50ms, costul **minim** = 150-200ms pentru prima cerere.

---

## 2. Semantica HTTP

### Metode HTTP și proprietățile lor

| Metodă | Sigură | Idempotentă | Cacheable | Descriere |
|--------|--------|-------------|-----------|-----------|
| GET | ✓ | ✓ | ✓ | Citire resursă |
| HEAD | ✓ | ✓ | ✓ | Doar headere |
| POST | ✗ | ✗ | Condiționat | Creare/submit |
| PUT | ✗ | ✓ | ✗ | Înlocuire completă |
| PATCH | ✗ | ✗ | ✗ | Modificare parțială |
| DELETE | ✗ | ✓ | ✗ | Ștergere resursă |
| OPTIONS | ✓ | ✓ | ✗ | Capabilități server |

**Siguranța** înseamnă că cererea nu modifică starea serverului.

**Idempotența** înseamnă că rezultatul este identic indiferent de câte ori se execută cererea.

### De ce contează idempotența

- Proxy-urile și load balancer-ele pot **reîncerca automat** cererile idempotente la timeout
- Clientul poate **repeta în siguranță** un PUT sau DELETE dacă nu primește răspuns
- POST **nu** poate fi repetat automat – crearea duplicată a resursei

### Coduri de status – nuanțe importante

**Autentificare vs Autorizare:**
- `401 Unauthorized` – lipsește autentificarea („Cine ești?")
- `403 Forbidden` – autentificat, dar fără acces („Nu ai voie")

**Resurse vs Metode:**
- `404 Not Found` – resursa nu există
- `405 Method Not Allowed` – resursa există, metoda nu e permisă

**Conținut:**
- `415 Unsupported Media Type` – Content-Type necunoscut serverului
- `422 Unprocessable Entity` – format valid, dar semantică invalidă

```python
# Exemplu practic
GET /api/orders/999     → 404 (comanda 999 nu există)
DELETE /api/orders      → 405 (nu poți șterge colecția)
POST /api/orders
Content-Type: image/png → 415 (nu acceptă imagini)
POST /api/orders
{"quantity": -5}        → 422 (cantitate invalidă)
```

---

## 3. Headere HTTP critice

### Content Negotiation

Clientul specifică ce **preferă** să primească:

```http
Accept: application/json, text/html;q=0.9
Accept-Language: ro-RO, en;q=0.8
Accept-Encoding: gzip, br
```

Serverul răspunde cu ce **oferă efectiv**:

```http
Content-Type: application/json; charset=utf-8
Content-Language: ro
Content-Encoding: gzip
```

### Caching HTTP

```http
# Server indică politica de cache
Cache-Control: max-age=3600, must-revalidate
ETag: "v1.2.3-abc"
Last-Modified: Wed, 21 Oct 2024 07:28:00 GMT

# Client revalidează (cerere condițională)
If-None-Match: "v1.2.3-abc"
If-Modified-Since: Wed, 21 Oct 2024 07:28:00 GMT

# Server poate răspunde 304 Not Modified (fără body)
```

**Întrebare de verificare:** Ce economisește un 304 Not Modified?

### Cookie-uri și sesiuni

```http
# Server setează cookie-ul de sesiune
Set-Cookie: session=abc123; HttpOnly; Secure; SameSite=Strict; Path=/

# Client trimite automat în cererile ulterioare
Cookie: session=abc123
```

**Flag-uri de securitate:**
- `HttpOnly` – previne accesul din JavaScript (protecție XSS)
- `Secure` – trimis doar pe HTTPS
- `SameSite=Strict` – protecție CSRF

---

## 4. CORS – Cross-Origin Resource Sharing

### De ce există CORS?

CORS **nu** este o limitare a HTTP – este o **politică de securitate a browserului**. Protejează utilizatorii de site-uri malițioase care ar face cereri în numele lor către API-uri legitime.

### Preflight Request

Pentru cereri „nesimple" (POST cu JSON, headere custom), browserul trimite automat OPTIONS:

```http
OPTIONS /api/users HTTP/1.1
Origin: https://frontend.com
Access-Control-Request-Method: POST
Access-Control-Request-Headers: Content-Type

HTTP/1.1 204 No Content
Access-Control-Allow-Origin: https://frontend.com
Access-Control-Allow-Methods: GET, POST, PUT, DELETE
Access-Control-Allow-Headers: Content-Type
Access-Control-Max-Age: 86400
```

**Regulă de aur:** „Merge în Postman dar nu în browser" = problemă CORS

> **Din experiența de predare:** Prima întâlnire cu CORS e de obicei când faci fetch din React/Vue către un backend Flask sau Express. Frustrarea e reală, dar odată înțeles mecanismul, devine trivial de rezolvat.

---

## 5. HTTP/1.1 vs HTTP/2

### Limitările HTTP/1.1

1. **Head-of-Line Blocking** – cererile se procesează secvențial pe conexiune
2. **Headere repetate** – acelaș Host, User-Agent la fiecare cerere
3. **Conexiuni multiple** – browserele deschid 6-8 conexiuni per domeniu

### Îmbunătățiri HTTP/2

1. **Multiplexare** – multiple stream-uri pe aceeași conexiune TCP
2. **Compresie headere** (HPACK) – doar diferențele se trimit
3. **Prioritizare** – clientul indică importanța stream-urilor
4. **Server Push** – serverul anticipează resurse (opțional)

**Important:** Semantica HTTP rămâne **identică** – același GET, POST, headere, coduri.

---

## 6. WebSocket

### Problema

HTTP este inițiat **exclusiv de client**. Serverul nu poate „împinge" date nesolicitate.

### Soluția: WebSocket

Conexiunea începe ca HTTP, apoi face **upgrade** la protocol bidirecțional:

```http
GET /chat HTTP/1.1
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==

HTTP/1.1 101 Switching Protocols
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Accept: s3pPLMBiTxaQ9kYGzzhZRbK+xOo=
```

După handshake, **nu mai este HTTP** – este comunicație bidirecțională pe TCP.

| Aspect | Polling | Long Polling | WebSocket |
|--------|---------|--------------|-----------|
| Latență | Interval fix | Medie | Foarte mică |
| Overhead | Mare | Moderat | Mic |
| Server push | Nu | Parțial | Da |
| Complexitate | Simplă | Medie | Mai complexă |

---

## 7. HTTPS și TLS

### Ce asigură HTTPS

1. **Confidențialitate** – datele sunt criptate end-to-end
2. **Integritate** – modificările sunt detectate
3. **Autentificare** – serverul este verificat prin certificat

### Impact operațional

- **Inspecția traficului** devine imposibilă fără MITM
- **Proxy-uri corporative** necesită certificate proprii (breakage TLS)
- **Debugging** mai dificil – Wireshark vede doar handshake

```bash
# curl cu verbose pentru debugging HTTPS
curl -v https://api.example.com/users 2>&1 | head -30
```

---

## 8. REST – Stil arhitectural

### Principiile REST (Fielding, 2000)

1. **Client-Server** – separare clară a responsabilităților
2. **Stateless** – fiecare cerere conține tot contextul necesar
3. **Cacheable** – răspunsurile indică explicit dacă pot fi cached
4. **Uniform Interface** – resurse identificate prin URI, manipulate prin reprezentări
5. **Layered System** – clientul nu știe dacă comunică direct cu serverul
6. **Code on Demand** (opțional) – serverul poate trimite cod executabil

### Richardson Maturity Model

**Nivel 0 – Tunelul HTTP (RPC over HTTP):**
```http
POST /api
{"method": "getUser", "params": {"id": 123}}
```

**Nivel 1 – Resurse:**
```http
POST /api/users/123
{"action": "updateName", "name": "Ion"}
```

**Nivel 2 – Verbe HTTP + Status Codes:**
```http
PUT /api/users/123
Content-Type: application/json
{"name": "Ion"}

HTTP/1.1 200 OK
```

**Nivel 3 – HATEOAS (Hypermedia):**
```json
{
  "id": 123,
  "name": "Ion",
  "_links": {
    "self": {"href": "/api/users/123"},
    "orders": {"href": "/api/users/123/orders"},
    "delete": {"href": "/api/users/123", "method": "DELETE"}
  }
}
```

### Anti-patterns REST

❌ `POST /api/users/123/activate` – acțiune în URL
❌ `200 OK {"error": "Not found"}` – cod greșit pentru eroare
❌ `POST` pentru toate operațiile – pierderea semanticii
❌ `GET /api/deleteUser?id=123` – efect secundar pe GET

---

## 9. REST vs SOAP

| Aspect | REST | SOAP |
|--------|------|------|
| Format | JSON (tipic) | XML (obligatoriu) |
| Contract | OpenAPI (opțional) | WSDL (obligatoriu) |
| Transport | HTTP | HTTP, SMTP, JMS, ... |
| Stare | Stateless | Poate fi stateful |
| Caching | Nativ HTTP | Complex |
| Complexitate | Simplă | Enterprise |
| Tooling | Manual / code-gen | Generare automată din WSDL |

### Când SOAP?

- Tranzacții distribuite (WS-AtomicTransaction)
- Securitate avansată (WS-Security, WS-Trust)
- Mesagerie asincronă (WS-Addressing, WS-ReliableMessaging)
- Contracte stricte obligatorii între organizații

---

## 10. Diagnosticare HTTP

### Instrumente esențiale

**curl pentru debugging:**
```bash
# Cerere verbose
curl -v https://api.example.com/users

# Doar headere
curl -I https://api.example.com/users

# POST cu JSON
curl -X POST -H "Content-Type: application/json" \
     -d '{"name":"test"}' https://api.example.com/users

# Timing detaliat
curl -w "DNS: %{time_namelookup}s\nTCP: %{time_connect}s\nTLS: %{time_appconnect}s\nTotal: %{time_total}s\n" \
     -o /dev/null -s https://api.example.com/
```

**Browser DevTools:**
- Network tab – timeline, headere, preview body
- Console – erori CORS afișate aici
- Application – cookies, cache, storage

**tcpdump/tshark:**
```bash
# HTTP plaintext
sudo tcpdump -i any -nn port 80 -A

# Doar conexiuni noi
sudo tcpdump -i any 'tcp[tcpflags] & (tcp-syn) != 0'

# tshark cu filtre
tshark -i any -f "port 80" -Y "http.request"
```

---

## Recapitulare – Idei cheie

1. HTTP este un **protocol**, nu un framework – headerele controlează comportamentul
2. **Idempotența** permite reîncercări automate (GET, PUT, DELETE) dar nu POST
3. **CORS** protejează utilizatorii în browser – nu e bug, e feature
4. **HTTP/2** multiplexează, dar semantica rămâne aceeași
5. **WebSocket** oferă comunicație bidirecțională după upgrade
6. **REST** înseamnă folosirea corectă a HTTP, nu doar JSON over POST
7. **SOAP** rămâne relevant în contexte enterprise cu contracte stricte

---

## La ce ne ajută

Ca programator în echipă, aceste cunoștințe permit:

- **Debugging rapid** – identificarea sursei problemei (client/server/proxy/CORS)
- **API design corect** – coduri de status adecvate, idempotență, caching
- **Comunicare eficientă** – vocabular comun cu DevOps, echipă infrastructură
- **Optimizare performanță** – înțelegerea latențelor (RTT, TLS handshake)

---

## Întrebări de reflexie

1. De ce `PUT` este idempotent dar `POST` nu? Dați un exemplu concret.
2. Care este diferența funcțională între `401` și `403`? Când folosiți fiecare?
3. De ce unele cereri „merg în Postman dar nu în browser"?
4. Ce se întâmplă dacă serverul returnează `Cache-Control: max-age=3600`?
5. De ce WebSocket începe cu un handshake HTTP?
6. Când ați folosi SOAP în loc de REST în 2025?

---

## Întrebări Peer Instruction (pentru seminar)

Folosiți aceste întrebări în format Peer Instruction: vot individual → discuție în perechi → revot → explicație.

### 🗳️ PI-1: Idempotență HTTP

**Scenariu:** Un client trimite `PUT /api/users/123` cu `{"name": "Ion"}` de 3 ori consecutive din cauza timeout-urilor de rețea.

**Ce se întâmplă pe server?**

A) Se creează 3 utilizatori noi cu numele "Ion"  
B) Utilizatorul 123 are numele "Ion" (un singur rezultat)  
C) Serverul returnează eroare la al doilea și al treilea request  
D) Depinde de implementarea serverului  

<details>
<summary>📋 Note instructor</summary>

**Răspuns corect:** B

**Analiza distractorilor:**
- **A:** Confuzie PUT cu POST - studenții care nu înțeleg diferența
- **C:** Presupunere că serverul detectează duplicate - nu e relevant pentru idempotență
- **D:** Răspuns defensiv - studenții nesiguri

**După discuție:** Subliniază că idempotența e proprietate a *rezultatului*, nu a procesării.

**Timing:** Prezentare 1 min → Vot 1 min → Discuție perechi 3 min → Revot 30 sec → Explicație 2 min
</details>

---

### 🗳️ PI-2: CORS și Securitate

**Scenariu:** Aplicația ta React pe `https://myapp.com` face:
```javascript
fetch('https://api.extern.com/data')
```
Cererea eșuează în browser cu eroare CORS, dar funcționează perfect în Postman.

**Care este cauza?**

A) API-ul extern este offline sau are probleme de rețea  
B) Browser-ul blochează cererea din motive de securitate  
C) Trebuie să folosești HTTP în loc de HTTPS  
D) Serverul a returnat 403 Forbidden  

<details>
<summary>📋 Note instructor</summary>

**Răspuns corect:** B

**Analiza distractorilor:**
- **A:** Nu verifică că Postman funcționează (dat în enunț)
- **C:** Inversează problema (HTTPS e corect)
- **D:** Confuzie între CORS și autorizare server

**Puncte cheie:**
- CORS e politică de BROWSER, nu de server
- Postman nu e browser → nu aplică CORS
- Serverul trebuie să trimită headere `Access-Control-Allow-Origin`
</details>

---

### 🗳️ PI-3: Coduri de Status

**Scenariu:** Trimiți credențiale valide (username + password) către `/api/admin/dashboard`, dar primești răspuns HTTP cu eroare.

**User-ul tău NU este admin. Ce cod de status ar trebui să returneze serverul?**

A) 401 Unauthorized  
B) 403 Forbidden  
C) 404 Not Found  
D) 400 Bad Request  

<details>
<summary>📋 Note instructor</summary>

**Răspuns corect:** B

**Analiza distractorilor:**
- **A:** Confuzie autentificare/autorizare - user e autentificat dar neautorizat
- **C:** Practică de securitate (ascunde existența resursei) - discută trade-off
- **D:** Credențialele sunt valide, nu e input greșit

**Extensie:** Discută când 404 e preferabil din motive de securitate (nu dezvăluie ce există).
</details>

---

### 🗳️ PI-4: HTTP/2 Multiplexare

**Scenariu:** Pagina ta web încarcă 10 imagini de pe același server. Compari HTTP/1.1 cu HTTP/2.

**Câte conexiuni TCP deschide browser-ul pentru HTTP/1.1 vs HTTP/2?**

A) HTTP/1.1: 1 conexiune | HTTP/2: 10 conexiuni  
B) HTTP/1.1: 10 conexiuni | HTTP/2: 1 conexiune  
C) HTTP/1.1: 6-8 conexiuni | HTTP/2: 1 conexiune  
D) Ambele folosesc 1 conexiune, diferă doar viteza  

<details>
<summary>📋 Note instructor</summary>

**Răspuns corect:** C

**Analiza distractorilor:**
- **A:** Inversează complet comportamentul
- **B:** Aproape corect, dar HTTP/1.1 are limită browser de 6-8
- **D:** Nu înțelege multiplexarea

**Demonstrație:** Arată în DevTools Network tab - grupare pe conexiuni.
</details>

---

### 🗳️ PI-5: REST Maturity Levels

**Scenariu:** API-ul tău are endpoint-ul:
```
POST /api
Body: {"action": "deleteUser", "userId": 123}
```

**La ce nivel Richardson se află acest API?**

A) Nivel 0 (RPC over HTTP)  
B) Nivel 1 (Resurse)  
C) Nivel 2 (Verbe HTTP)  
D) Nivel 3 (HATEOAS)  

<details>
<summary>📋 Note instructor</summary>

**Răspuns corect:** A

**Analiza distractorilor:**
- **B:** Are resurse în body, dar nu în URL
- **C:** Folosește POST pentru tot, nu DELETE
- **D:** Cel mai avansat, evident nu

**Follow-up:** "Cum ar arăta la nivel 2?" → `DELETE /api/users/123`
</details>

---

## Bibliografie

### Referințe academice

| Autori | Titlu | Publicație | DOI |
|--------|-------|------------|-----|
| Fielding, R.T. | Architectural Styles and the Design of Network-based Software Architectures | UCI Dissertation, 2000 | N/A (teză) |
| Berners-Lee, T., Fielding, R., Masinter, L. | Uniform Resource Identifier (URI): Generic Syntax | RFC 3986, 2005 | 10.17487/RFC3986 |
| Fielding, R., Reschke, J. | Hypertext Transfer Protocol (HTTP/1.1): Semantics and Content | RFC 7231, 2014 | 10.17487/RFC7231 |
| Belshe, M., Peon, R., Thomson, M. | Hypertext Transfer Protocol Version 2 (HTTP/2) | RFC 7540, 2015 | 10.17487/RFC7540 |
| Richardson, L., Ruby, S. | RESTful Web Services | O'Reilly Media, 2007 | ISBN: 978-0596529260 |

### Standarde și specificații

- RFC 7230-7235: HTTP/1.1 (Message Syntax, Semantics, Caching, Authentication)
- RFC 7540: HTTP/2
- RFC 6455: WebSocket Protocol
- RFC 8446: TLS 1.3
- OpenAPI Specification 3.1: https://spec.openapis.org/oas/v3.1.0
- Martin Fowler – Richardson Maturity Model: https://martinfowler.com/articles/richardsonMaturityModel.html

---

*Material elaborat pentru disciplina Rețele de Calculatoare, ASE București, 2025-2026*
