# Seminar 8 – Sarcini Practice
## Server HTTP + Reverse Proxy

---

## Pregătire

### Verificare dependențe

```bash
# Verifică Python
python3 --version

# Verifică curl
curl --version

# Verifică tcpdump (necesită sudo)
which tcpdump

# (Opțional) Verifică Docker
docker --version
```

### Structură directoare

```bash
cd starterkit_s8
chmod +x scripts/*.sh scenarios/*/*.sh
./tests/smoke_test.sh
```

---

## Mod de lucru: Pair Programming

Exercițiile din acest seminar sunt gândite pentru lucru în perechi.

### Roluri

| Rol | Responsabilitate | Ce face |
|-----|------------------|---------|
| **Driver** | Tastatura | Scrie codul, execută comenzi |
| **Navigator** | Strategie | Verifică documentația, detectează erori, gândește pasul următor |

### Reguli

1. **Rotație la fiecare 15 minute** sau la finalul fiecărui Task
2. **Navigator-ul NU atinge tastatura** — comunică verbal
3. **Driver-ul explică ce face** — gândește cu voce tare
4. **Ambii sunt responsabili** pentru codul rezultat

### Semnal de rotație

Când auziți "ROTAȚIE!" de la instructor:
1. Driver-ul face commit/save
2. Schimbați locurile fizic
3. Noul Driver continuă de unde s-a rămas

### Pentru Task-urile din acest seminar

| Task | Driver începe cu | Navigator verifică |
|------|------------------|-------------------|
| 1.1 Demo server | Cel din stânga | Output-ul curl |
| 1.2 Captură TCP | Cel din dreapta | Flags-urile TCP |
| 1.3 Implementare | Cel din stânga | s8_explanation.md |
| 2.1 Demo proxy | Cel din dreapta | Alternarea backend-urilor |
| 2.2 Captură proxy | Cel din stânga | Cele 2 conexiuni TCP |
| 2.3 Implementare | Cel din dreapta | Documentația funcțiilor |

---

> 📖 **Întrebări pentru discuție:** Vezi [peer_instruction.md](peer_instruction.md) 
> pentru întrebări de tip Peer Instruction care vor fi folosite în seminar.

---

## Partea I: Server HTTP (45 min)

### Task 1.1: Rulare demo server (10 min)

**Obiectiv**: Înțelegerea funcționării serverului HTTP minimal.

**👥 Pair Programming:**
- Driver: Execută comenzile
- Navigator: Verifică output-ul și notează răspunsurile

**🔮 PREDICȚIE (notează ÎNAINTE de a rula):**
1. Ce status code vei primi pentru `/`? _____
2. Ce status code pentru `/not-found`? _____
3. Ce header crezi că indică serverul? _____

*Discută cu colegul de bancă 30 secunde, apoi rulează comenzile.*

```bash
# Terminal 1: Pornește serverul
cd python/demos
python3 demo_http_server.py --host 127.0.0.1 --port 8080 --www ../../www

# Terminal 2: Teste cu curl
curl -v http://127.0.0.1:8080/
curl -v http://127.0.0.1:8080/index.html
curl -v http://127.0.0.1:8080/hello.txt
curl -v http://127.0.0.1:8080/not-found
```

**Verificare predicții:**

| Întrebare | Predicție | Realitate | Corect? |
|-----------|-----------|-----------|---------|
| Status `/` | | | |
| Status `/not-found` | | | |
| Header server | | | |

**Întrebări suplimentare:**
1. De ce `/` returnează același conținut ca `/index.html`?
2. Ce header arată dimensiunea răspunsului?

---

### Task 1.2: Captură TCP handshake (15 min)

**Obiectiv**: Vizualizarea three-way handshake în traficul real.

**👥 Pair Programming:**
- Driver: Execută tcpdump și curl
- Navigator: Identifică pachetele în captură

**🔮 PREDICȚIE (completează ÎNAINTE de a rula tcpdump):**

Câte pachete TCP estimezi că vor apărea pentru UN SINGUR request GET?

| Fază | Pachete estimate |
|------|------------------|
| Handshake (SYN, SYN-ACK, ACK) | ___ |
| Request HTTP | ___ |
| Response HTTP | ___ |
| Închidere conexiune | ___ |
| **TOTAL** | ___ |

*După captură, compară cu realitatea și notează diferențele.*

```bash
# Terminal 1: Captură
sudo tcpdump -i lo port 8080 -nn -c 20

# Terminal 2: Server (dacă nu rulează deja)
python3 demo_http_server.py --port 8080

# Terminal 3: Client
curl http://127.0.0.1:8080/
```

**Ce trebuie să observi:**
- Pachet SYN (flag [S])
- Pachet SYN-ACK (flag [S.])
- Pachet ACK (flag [.])
- Pachete de date (flag [P.])
- Pachete FIN (flag [F.])

**Completează:**
```
Handshake:
  1. Client → Server: SYN, Seq=_____
  2. Server → Client: SYN-ACK, Seq=_____, Ack=_____
  3. Client → Server: ACK, Seq=_____, Ack=_____

Total pachete observate: _____ (estimat: _____)

Diferențe față de predicție:
_________________________________________________
```

---

### Task 1.3: Implementare exercițiu HTTP server (20 min)

**Obiectiv**: Completarea serverului HTTP din exerciții.

**👥 Pair Programming:**
- Driver: Scrie codul în `ex01_http_server.py`
- Navigator: Ține deschis `s8_explanation.md` și verifică logica
- **Rotație:** După funcția `parse_request()`, schimbați rolurile

Deschide fișierul `python/exercises/ex01_http_server.py` și completează secțiunile marcate cu `# TODO`.

```python
# În ex01_http_server.py

def handle_client(conn, addr, www_root, backend_id):
    """
    TODO 1: Citește request-ul de la client
    Hint: folosește read_until() din utils
    """
    raw = # TODO: apelează read_until
    
    """
    TODO 2: Parsează request-ul
    Hint: folosește parse_http_request() din utils
    """
    req = # TODO: apelează parse_http_request
    
    """
    TODO 3: Validează metoda (doar GET și HEAD permise)
    Hint: dacă metoda nu e validă, trimite 405
    """
    if req.method not in ("GET", "HEAD"):
        # TODO: trimite răspuns 405
        pass
    
    """
    TODO 4: Mapează target la cale fișier
    Hint: folosește safe_map_target_to_path()
    """
    filepath, error = # TODO: apelează safe_map_target_to_path
    
    # Restul implementării...
```

**Verificare:**
```bash
python3 ex01_http_server.py --selftest
```

---

## Partea II: Reverse Proxy (45 min)

### Task 2.1: Demo reverse proxy (10 min)

**Obiectiv**: Înțelegerea fluxului client → proxy → backend.

**👥 Pair Programming:**
- Driver: Pornește serverele și execută curl
- Navigator: Observă care backend răspunde

**🔮 PREDICȚIE:**
Dacă trimiți 4 request-uri consecutive, în ce ordine vor fi procesate de backend-uri?

| Request | Backend prezis | Backend real |
|---------|----------------|--------------|
| 1 | | |
| 2 | | |
| 3 | | |
| 4 | | |

*Rulează bucla și verifică cu `grep X-Backend`.*

```bash
# Terminal 1: Backend A
python3 python/demos/demo_http_server.py --port 8001 --id backend-A

# Terminal 2: Backend B
python3 python/demos/demo_http_server.py --port 8002 --id backend-B

# Terminal 3: Reverse Proxy
python3 python/demos/demo_reverse_proxy.py --listen-port 8080 \
    --backends 127.0.0.1:8001,127.0.0.1:8002

# Terminal 4: Client (test round-robin)
for i in 1 2 3 4; do
    curl -s -D - http://127.0.0.1:8080/ -o /dev/null | grep X-Backend
done
```

**Întrebări:**
1. În ce ordine sunt selectate backend-urile? De ce?
2. Ce header arată care backend a procesat request-ul?
3. Ce header este adăugat de proxy pentru identificarea clientului original?

---

### Task 2.2: Captură proxy în tcpdump (15 min)

**Obiectiv**: Vizualizarea celor două conexiuni TCP.

**🔮 PREDICȚIE:**
Câte conexiuni TCP distincte vor apărea în captură pentru UN request client→proxy→backend?

Estimare: ___ conexiuni TCP

*Hint: Gândește-te la cine vorbește cu cine.*

```bash
# Terminal 1: Captură
sudo tcpdump -i lo '(port 8080 or port 8001)' -nn

# Restul terminalelor: server + proxy + client (ca mai sus)
```

**Completează tabelul:**

| Conexiune | IP:Port Sursă | IP:Port Destinație | Rol |
|-----------|---------------|---------------------|-----|
| 1 | | | Client → Proxy |
| 2 | | | Proxy → Backend |

**Verificare predicție:** Am văzut ___ conexiuni TCP (estimat: ___)

**Întrebare**: De ce proxy-ul folosește un port efemer (>49152) pentru conexiunea către backend?

---

### Task 2.3: Implementare exercițiu reverse proxy (20 min)

**Obiectiv**: Completarea proxy-ului din exerciții.

**👥 Pair Programming:**
- Driver: Scrie codul în `ex02_reverse_proxy.py`
- Navigator: Verifică documentația din `s8_explanation.md`
- **Rotație:** După `RoundRobinBalancer`, schimbați rolurile

Deschide `python/exercises/ex02_reverse_proxy.py` și completează:

```python
def handle_client(conn, addr, balancer):
    """
    TODO 1: Citește request de la client
    """
    raw = # TODO
    
    """
    TODO 2: Selectează backend (round-robin)
    Hint: balancer.next() returnează următorul Backend
    """
    backend = # TODO
    
    """
    TODO 3: Adaugă header-uri proxy
    Hint: X-Forwarded-For cu IP-ul clientului
    """
    forwarded = rebuild_request_with_proxy_headers(raw, addr[0])
    
    """
    TODO 4: Conectează-te la backend și trimite request
    Hint: socket.create_connection((backend.host, backend.port))
    """
    with socket.create_connection(...) as upstream:
        upstream.sendall(forwarded)
        response = recv_http_response(upstream)
    
    """
    TODO 5: Trimite răspunsul înapoi la client
    """
    conn.sendall(response)
```

---

## Partea III: nginx Reverse Proxy (30 min) – Opțional

### Task 3.1: Configurare nginx (15 min)

**Obiectiv**: Configurarea nginx ca reverse proxy.

1. Verifică configurația în `nginx/nginx.conf`
2. Modifică porturile dacă este necesar

```bash
# Pornește backend-urile Python
python3 python/demos/demo_http_server.py --port 8001 --id backend-A &
python3 python/demos/demo_http_server.py --port 8002 --id backend-B &

# Testează configurația nginx
sudo nginx -t -c $(pwd)/nginx/nginx.conf

# Pornește nginx
sudo nginx -c $(pwd)/nginx/nginx.conf

# Test
curl http://localhost/
```

---

### Task 3.2: Docker Compose (15 min)

**Obiectiv**: Orchestrare completă cu Docker.

```bash
# Construiește și pornește
docker-compose up -d

# Verifică
docker-compose ps

# Test
curl http://localhost/

# Logs
docker-compose logs -f nginx

# Oprire
docker-compose down
```

---

## Partea IV: Exerciții de înțelegere (20 min)

Aceste exerciții NU necesită scrierea de cod nou, ci înțelegerea codului existent.

**Alege DOUĂ** dintre următoarele (din [exercitii_non_cod.md](exercitii_non_cod.md)):

- [ ] **TRACE-1:** Urmărire execuție socket server — completează valorile variabilelor
- [ ] **TRACE-2:** Analiză captură TCP — interpretează o captură reală (RECOMANDAT!)
- [ ] **PARSONS-1:** Ordonare cod response HTTP — pune liniile în ordine corectă
- [ ] **PARSONS-2:** Ordonare cod round-robin — implementare thread-safe
- [ ] **DEBUG-1:** Găsește vulnerabilitatea de securitate — directory traversal
- [ ] **DEBUG-2:** De ce răspunsurile sunt incomplete? — Content-Length
- [ ] **DEBUG-3:** Proxy returnează 502 intermitent — recv incomplet

**Verificare:** Compară răspunsurile cu colegul, apoi cu soluțiile de la finalul fișierului.

---

## Partea V: Decizii de design (10 min)

### Evaluare: Alegerea protocolului

Pentru fiecare scenariu, argumentează alegerea TCP sau UDP:

**Scenariu 1: Aplicație de chat text** (WhatsApp-like)
- Alegere: TCP / UDP (încercuiește)
- Argument: ________________________________________________
- ________________________________________________

**Scenariu 2: Streaming audio live** (podcast în direct)
- Alegere: TCP / UDP (încercuiește)
- Argument: ________________________________________________
- ________________________________________________

**Scenariu 3: Sistem de logging centralizat** (trimite loguri la server)
- Alegere: TCP / UDP (încercuiește)
- Argument: ________________________________________________
- ________________________________________________

**Scenariu 4: Joc multiplayer turn-based** (șah online)
- Alegere: TCP / UDP (încercuiește)
- Argument: ________________________________________________
- ________________________________________________

**Discuție:** Compară răspunsurile cu perechea ta. Unde ați avut opinii diferite?

---

### Analiză: Debugging scenarii

**Scenariu 1:** Serverul tău HTTP funcționează perfect pe localhost, dar clienții din rețea nu se pot conecta.

Posibile cauze (bifează toate care se aplică):
- [ ] Serverul face bind pe 127.0.0.1 în loc de 0.0.0.0
- [ ] Firewall-ul blochează portul
- [ ] Clientul folosește IP greșit
- [ ] Serverul nu a apelat listen()

Cum ai diagnostica? Scrie 2 comenzi:
1. `_______________________________________________`
2. `_______________________________________________`

**Scenariu 2:** Reverse proxy-ul tău returnează intermitent 502 Bad Gateway.

Posibile cauze:
- [ ] Un backend e căzut
- [ ] Timeout prea mic la conexiunea către backend
- [ ] Backend-ul returnează răspuns invalid
- [ ] Toate cele de mai sus

Cum ai investiga? ________________________________________________

---

## Verificare finală

### Checklist

- [ ] Am rulat serverul HTTP și am observat răspunsurile pentru diferite request-uri
- [ ] Am capturat și identificat TCP three-way handshake în tcpdump
- [ ] Am observat diferența între HTTP 200 și 404
- [ ] Am rulat reverse proxy-ul și am observat round-robin
- [ ] Am identificat cele două conexiuni TCP (client→proxy, proxy→backend)
- [ ] Am completat cel puțin un exercițiu (ex01 sau ex02)
- [ ] Am făcut cel puțin 2 exerciții non-cod (TRACE/PARSONS/DEBUG)
- [ ] Am completat exercițiile de evaluare (TCP vs UDP)
- [ ] (Opțional) Am configurat nginx ca reverse proxy
- [ ] (Opțional) Am utilizat Docker pentru orchestrare

### Întrebări de verificare

1. Ce header HTTP indică lungimea body-ului?
2. De ce este important să verificăm directory traversal?
3. Ce rol are header-ul X-Forwarded-For?
4. Câte conexiuni TCP sunt implicate într-un request prin reverse proxy?
5. Ce algoritm de load balancing am folosit?

---

## Teme pentru acasă

### Tema 1: Extindere server HTTP (Mediu)
Adaugă suport pentru metoda POST în serverul HTTP. Body-ul request-ului trebuie salvat într-un fișier.

### Tema 2: Health Check (Avansat)
Implementează un mecanism de health check în reverse proxy: dacă un backend nu răspunde, să fie scos temporar din rotație.

### Tema 3: Logging (Ușor)
Adaugă logging în format Apache Combined Log Format:
```
IP - - [timestamp] "METHOD /path HTTP/1.1" status bytes
```

---

## Notă de final

Dacă ai terminat toate exercițiile și mai ai timp, încearcă una dintre temele pentru acasă. 
Exercițiul de Health Check (Tema 2) e cel mai util pentru înțelegerea arhitecturilor 
moderne de web — practic orice CDN (Cloudflare, Akamai) funcționează pe același principiu.

Cele mai frecvente greșeli pe care le văd la acest seminar:
1. Uită `\r\n\r\n` la sfârșitul header-elor HTTP
2. Confundă Content-Length cu lungimea întregului răspuns (e doar body-ul!)
3. Nu verifică directory traversal (și apoi se miră de ce "merge" `/../../../etc/passwd`)

Spor la debug!

---

*Material pentru Seminar 8, Rețele de Calculatoare, ASE București*
