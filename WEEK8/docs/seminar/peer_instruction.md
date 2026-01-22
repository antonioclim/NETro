# Întrebări Peer Instruction – Seminar 8

Aceste întrebări sunt gândite pentru discuții în perechi/grupuri mici.  
**Format:** Vot individual → Discuție 3 min → Revot → Explicație

---

## PI-1: TCP Connection Refused

### Scenariu
Un client Python încearcă să se conecteze la `localhost:9999`, dar niciun server nu ascultă pe acel port.

```python
sock = socket.socket(AF_INET, SOCK_STREAM)
sock.connect(('localhost', 9999))
```

### Întrebare
Ce se întâmplă când rulezi acest cod?

### Opțiuni
A) Clientul primește imediat `ConnectionRefusedError` (RST de la OS)  
B) Clientul așteaptă 30 de secunde apoi primește timeout  
C) Clientul se conectează dar `send()` va eșua  
D) Kernelul creează automat un server temporar  

### Răspuns corect: A

### Distractori și misconceptii vizate
- **B:** Confuzie cu firewall DROP (care nu trimite nimic înapoi) vs port închis (care trimite RST)
- **C:** Confuzie între conectare și transfer date
- **D:** Absurd, dar testează dacă studenții înțeleg că socket-urile necesită bind explicit

### Note instructor
- Dacă <50% răspund corect, demonstrează cu `tcpdump -i lo port 9999` — se vede RST
- Întrebare follow-up: "Ce s-ar întâmpla dacă între client și server e un firewall cu DROP?"
- Timing: 5-6 minute total

---

## PI-2: Content-Length Greșit

### Scenariu
Un server HTTP trimite acest răspuns:

```http
HTTP/1.1 200 OK
Content-Type: text/plain
Content-Length: 5

Hello, World!
```

### Întrebare
Ce va afișa browser-ul/curl?

### Opțiuni
A) "Hello, World!" (complet)  
B) "Hello" (doar primele 5 caractere)  
C) Eroare de parsare HTTP  
D) "Hello, World!" dar cu warning în consolă  

### Răspuns corect: B

### Distractori și misconceptii vizate
- **A:** Nu înțeleg rolul Content-Length
- **C:** HTTP/1.1 nu validează, doar citește exact Content-Length bytes
- **D:** Browserele nu emit warning pentru asta

### Note instructor
- Demo live: modifică `demo_http_server.py` să trimită Content-Length greșit
- Întrebare bonus: "Ce se întâmplă dacă Content-Length e MAI MARE decât body-ul real?"
- Timing: 4-5 minute

---

## PI-3: Directory Traversal

### Scenariu
Server HTTP servește fișiere din `/var/www/html/`. Clientul trimite:

```http
GET /../../../etc/passwd HTTP/1.1
Host: vulnerable.com
```

Serverul folosește acest cod:
```python
filepath = www_root + request_path  # FĂRĂ normpath!
return open(filepath).read()
```

### Întrebare
Ce fișier va fi citit?

### Opțiuni
A) `/var/www/html/../../../etc/passwd` → `/etc/passwd` (VULNERABIL!)  
B) Eroare 404 pentru că path-ul nu există  
C) `/var/www/html/etc/passwd` (path-ul .. e ignorat)  
D) Eroare 400 Bad Request (.. detectat și blocat)  

### Răspuns corect: A

### Distractori și misconceptii vizate
- **B:** Nu înțeleg cum funcționează path resolution
- **C:** Cred că serverul web "curăță" automat path-ul
- **D:** Cred că Python sau OS-ul blochează automat

### Note instructor
- IMPORTANT: Demonstrează ÎNTÂI pe serverul VOSTRU (cu fix-ul dezactivat), apoi arată fix-ul
- Security mindset: "Never trust user input"
- Arată `os.path.normpath()` + verificare `startswith()`
- Timing: 6-7 minute

---

## PI-4: Round-Robin Proxy

### Scenariu
Reverse proxy cu 3 backend-uri: A, B, C. Algoritmul e round-robin.
Se trimit 5 request-uri consecutive de la același client.

### Întrebare
Care backend-uri procesează cele 5 request-uri (în ordine)?

### Opțiuni
A) A, B, C, A, B  
B) A, A, A, A, A (sticky sessions)  
C) Random, imprevizibil  
D) A, B, C, C, C (ultimul devine "default")  

### Răspuns corect: A

### Distractori și misconceptii vizate
- **B:** Confuzie cu IP hash sau sticky sessions
- **C:** Confuzie round-robin cu random
- **D:** Inventat, dar testează înțelegerea ciclicității

### Note instructor
- Demo: rulează `for i in {1..5}; do curl -s localhost:8080/ | grep X-Backend; done`
- Discuție: când ai vrea sticky sessions vs round-robin?
- Timing: 4 minute

---

## PI-5: HTTP Body pentru GET

### Scenariu
Un client trimite:

```http
GET /api/search HTTP/1.1
Host: api.example.com
Content-Type: application/json
Content-Length: 23

{"query": "networking"}
```

### Întrebare
Este acest request valid HTTP/1.1?

### Opțiuni
A) Da, GET poate avea body (deși serverele îl pot ignora)  
B) Nu, GET nu poate avea body — eroare de protocol  
C) Da, dar devine automat POST dacă are body  
D) Depinde de server — unele acceptă, altele nu  

### Răspuns corect: A (și parțial D în practică)

### Distractori și misconceptii vizate
- **B:** RFC-ul permite body pentru GET, dar "has no defined semantics"
- **C:** Metoda HTTP nu se schimbă niciodată automat
- **D:** Corect ca observație practică, dar A e răspunsul canonic

### Note instructor
- Arată RFC 7231: "A payload within a GET request message has no defined semantics"
- Exemplu practic: Elasticsearch folosea GET cu body (deprecated acum)
- Timing: 5 minute

---

## Utilizare în seminar

### Timing recomandat (pentru 75 min seminar)
| Moment | Întrebare | Durată |
|--------|-----------|--------|
| După recap | PI-1 (Connection Refused) | 5 min |
| După demo HTTP server | PI-2 (Content-Length) | 5 min |
| După explicația security | PI-3 (Directory Traversal) | 7 min |
| După demo reverse proxy | PI-4 (Round-Robin) | 4 min |
| Dacă rămâne timp | PI-5 (GET cu body) | 5 min |

### Materiale necesare
- Slides cu întrebările (sau proiectate direct din acest doc)
- Timer vizibil pentru discuții
- Opțional: Mentimeter/Kahoot pentru vot digital

### Procedură standard
1. **Afișează întrebarea** (1 min citire)
2. **Vot individual** — ridicare mâini sau digital (30 sec)
3. **Discuție în perechi** — "Convinge-l pe coleg" (2-3 min)
4. **Revot** — observă schimbările (30 sec)
5. **Explicație instructor** — focusează pe misconceptii (1-2 min)

---

*Material pentru Seminar 8, Rețele de Calculatoare, ASE București*
