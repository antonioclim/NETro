# Exerciții Non-Cod – Seminar 8

Aceste exerciții dezvoltă înțelegerea conceptelor fără a scrie cod de la zero.  
**Alege minimum 2** pentru a completa seminarul.

---

## TRACE-1: Urmărire Socket Server

Urmărește execuția pas cu pas și completează valorile:

```python
import socket

# Pas 1
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Ce tip de socket e creat?  TCP / UDP (încercuiește)
# server = _______________

# Pas 2
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# Ce face SO_REUSEADDR? ________________________________

# Pas 3
server.bind(('0.0.0.0', 8080))
# Pe ce adresă ascultă serverul? _______________________
# Pe ce port? _________

# Pas 4
server.listen(5)
# Ce înseamnă parametrul 5? ____________________________
# Serverul acceptă conexiuni acum? DA / NU (încercuiește)

# Pas 5
conn, addr = server.accept()
# Această linie BLOCHEAZĂ până când ____________________
# conn este: __________________________________________
# addr este: __________________________________________
# Exemplu addr: ('192.168.1.5', _____) 
#               (de ce portul clientului e mare? ________________)

# Pas 6
data = conn.recv(1024)
# Ce se întâmplă dacă clientul trimite 2000 bytes? _____
# data conține maximum _____ bytes la un apel recv()

# Pas 7
conn.sendall(b"HTTP/1.1 200 OK\r\n\r\n")
# De ce sendall() și nu send()? ________________________

# Pas 8
conn.close()
server.close()
# Putem face bind() pe 8080 imediat după close()? ______
# De ce? (hint: TIME_WAIT) _____________________________
```

---

## TRACE-2: Analiză Captură TCP (RECOMANDAT!)

Ai următoarea captură tcpdump (simplificată):

```
Nr  Timp         Sursă                  Dest                   Flags  Seq   Ack   Len
1   10:00:00.000 192.168.1.5:54321  →  10.0.0.1:80           [S]    1000  -     0
2   10:00:00.005 10.0.0.1:80        →  192.168.1.5:54321     [S.]   2000  1001  0
3   10:00:00.006 192.168.1.5:54321  →  10.0.0.1:80           [.]    1001  2001  0
4   10:00:00.007 192.168.1.5:54321  →  10.0.0.1:80           [P.]   1001  2001  50
5   10:00:00.015 10.0.0.1:80        →  192.168.1.5:54321     [.]    2001  1051  0
6   10:00:00.020 10.0.0.1:80        →  192.168.1.5:54321     [P.]   2001  1051  500
7   10:00:00.021 192.168.1.5:54321  →  10.0.0.1:80           [.]    1051  2501  0
8   10:00:00.025 192.168.1.5:54321  →  10.0.0.1:80           [F.]   1051  2501  0
9   10:00:00.026 10.0.0.1:80        →  192.168.1.5:54321     [F.]   2501  1052  0
10  10:00:00.027 192.168.1.5:54321  →  10.0.0.1:80           [.]    1052  2502  0
```

**Legendă flags:** [S]=SYN, [.]=ACK, [P]=PSH, [F]=FIN

### Completează:

| Nr | Întrebare | Răspuns |
|----|-----------|---------|
| 1 | Care este IP-ul clientului? | |
| 2 | Care este IP-ul serverului? | |
| 3 | Ce port folosește clientul? (efemer sau well-known?) | |
| 4 | Ce port folosește serverul? (ce serviciu e probabil?) | |
| 5 | Pachetele 1-3 reprezintă: | |
| 6 | Pachetul 4 conține probabil: (hint: 50 bytes, de la client) | |
| 7 | Pachetul 6 conține probabil: (hint: 500 bytes, de la server) | |
| 8 | Câți bytes de date a trimis clientul în total? | |
| 9 | Câți bytes de date a trimis serverul în total? | |
| 10 | Latența (RTT) estimată: (hint: timpul între pachetele 1 și 2) | |
| 11 | Care pachet confirmă primirea datelor din pachetul 4? | |
| 12 | Pachetele 8-10 reprezintă: | |

---

## PARSONS-1: Construire Response HTTP

Ordonează liniile pentru a construi un răspuns HTTP valid.  
**Scrie numerele 1-6 în paranteze:**

```
[ ] return header_bytes + body

[ ] headers += f"Content-Type: {content_type}\r\n"

[ ] headers = f"HTTP/1.1 {status_code} {status_text}\r\n"

[ ] headers += "\r\n"

[ ] headers += f"Content-Length: {len(body)}\r\n"

[ ] header_bytes = headers.encode('iso-8859-1')
```

**Verificare:** Pentru `status_code=200`, `status_text="OK"`, `content_type="text/html"`, `body=b"<h1>Hi</h1>"`, rezultatul trebuie să fie:

```
HTTP/1.1 200 OK\r\n
Content-Type: text/html\r\n
Content-Length: 11\r\n
\r\n
<h1>Hi</h1>
```

---

## PARSONS-2: Implementare Round Robin

Ordonează liniile pentru un next_backend() thread-safe.  
**Scrie numerele 1-5 în paranteze:**

```
[ ] return backend

[ ] self.index = (self.index + 1) % len(self.backends)

[ ] def next_backend(self):

[ ] with self.lock:

[ ] backend = self.backends[self.index]
```

---

## DEBUG-1: Găsește Vulnerabilitatea

Acest cod are o vulnerabilitate de securitate CRITICĂ. Găsește-o:

```python
def serve_file(request_path, www_root):
    """Servește un fișier static."""
    # Construim calea completă
    filepath = www_root + request_path
    
    # Verificăm dacă fișierul există
    if not os.path.exists(filepath):
        return 404, b"Not Found"
    
    # Citim și returnăm fișierul
    with open(filepath, 'rb') as f:
        content = f.read()
    
    return 200, content
```

### Întrebări:

1. **Ce vulnerabilitate conține codul?**  
   _____________________________________________

2. **Ce request ar exploata-o?** (scrie un GET malițios)  
   `GET _________________________ HTTP/1.1`

3. **Scrie fix-ul** (max 4 linii de cod de adăugat/modificat):

```python
def serve_file(request_path, www_root):
    # FIX: Adaugă aici codul care lipsește
    
    
    
    
    filepath = www_root + request_path
    # ... restul rămâne la fel
```

---

## DEBUG-2: De ce răspunsurile sunt incomplete?

Serverul pornește, dar clienții primesc răspunsuri incomplete sau corupte:

```python
def handle_client(conn):
    request = conn.recv(1024)
    
    # Parsăm request-ul
    lines = request.decode().split('\r\n')
    method, path, version = lines[0].split(' ')
    
    # Generăm răspuns
    body = b"<html><body>Hello World!</body></html>"
    response = f"HTTP/1.1 200 OK\r\n"
    response += f"Content-Type: text/html\r\n"
    response += f"\r\n"
    
    conn.send(response.encode() + body)
    conn.close()
```

### Întrebări:

1. **Care e problema principală?**  
   _____________________________________________

2. **De ce browser-ul nu știe când s-a terminat răspunsul?**  
   _____________________________________________

3. **Scrie linia de cod care lipsește** (și unde trebuie inserată):  
   `response += ________________________________`

---

## DEBUG-3: Proxy-ul returnează 502 intermitent

Codul proxy-ului:

```python
def forward_to_backend(request, backend_host, backend_port):
    sock = socket.socket(AF_INET, SOCK_STREAM)
    sock.connect((backend_host, backend_port))
    sock.send(request)
    response = sock.recv(4096)
    sock.close()
    return response
```

Uneori funcționează, alteori returnează 502 Bad Gateway.

### Întrebări:

1. **De ce `recv(4096)` e problematic pentru răspunsuri mari?**  
   _____________________________________________

2. **Ce se întâmplă dacă răspunsul backend-ului are 10KB?**  
   _____________________________________________

3. **Cum ar trebui rescris recv-ul?** (descrie algoritmul)  
   _____________________________________________

---

# SOLUȚII (pentru instructor / auto-verificare)

<details>
<summary>Click pentru a vedea soluțiile</summary>

## TRACE-1: Răspunsuri

- Pas 1: TCP (SOCK_STREAM)
- Pas 2: Permite refolosirea portului imediat după close, evitând eroarea "Address already in use"
- Pas 3: 0.0.0.0 (toate interfețele), port 8080
- Pas 4: Backlog = max 5 conexiuni în coada de așteptare; DA, acceptă conexiuni
- Pas 5: Până vine o conexiune nouă; conn = socket NOU pentru comunicare cu clientul; addr = tuplu (IP, port) al clientului; portul e mare (>49152) pentru că e efemer
- Pas 6: Primim doar primii 1024 bytes; recv poate returna mai puțin decât buffer-ul
- Pas 7: sendall() garantează că trimite TOT (re-apelează send în buclă)
- Pas 8: Nu imediat din cauza TIME_WAIT (~2 minute); SO_REUSEADDR rezolvă asta

## TRACE-2: Răspunsuri

1. 192.168.1.5
2. 10.0.0.1  
3. 54321 (efemer, >49152)
4. 80 (HTTP, well-known)
5. Three-way handshake (SYN → SYN-ACK → ACK)
6. HTTP GET request (probabil ~50 bytes de headers)
7. HTTP response (HTML, ~500 bytes)
8. 50 bytes
9. 500 bytes
10. 5 ms (diferența 10:00:00.005 - 10:00:00.000)
11. Pachetul 5 (Ack=1051 = 1001 + 50)
12. Four-way termination (FIN → ACK, FIN → ACK) sau graceful close

## PARSONS-1: Ordine corectă

```
[6] return header_bytes + body
[2] headers += f"Content-Type: {content_type}\r\n"
[1] headers = f"HTTP/1.1 {status_code} {status_text}\r\n"
[4] headers += "\r\n"
[3] headers += f"Content-Length: {len(body)}\r\n"
[5] header_bytes = headers.encode('iso-8859-1')
```

## PARSONS-2: Ordine corectă

```
[5] return backend
[4] self.index = (self.index + 1) % len(self.backends)
[1] def next_backend(self):
[2]     with self.lock:
[3]         backend = self.backends[self.index]
```

## DEBUG-1: Soluție

1. **Vulnerabilitate:** Directory traversal (path traversal)
2. **Request malițios:** `GET /../../../etc/passwd HTTP/1.1`
3. **Fix:**
```python
def serve_file(request_path, www_root):
    # Normalizează path-ul și verifică că rămâne în www_root
    safe_path = os.path.normpath(request_path.lstrip('/'))
    filepath = os.path.join(www_root, safe_path)
    
    if not filepath.startswith(os.path.abspath(www_root)):
        return 403, b"Forbidden"
    
    # ... restul codului
```

## DEBUG-2: Soluție

1. **Problema:** Lipsește header-ul Content-Length
2. **Explicație:** Browser-ul nu știe câți bytes să citească, așteaptă să se închidă conexiunea sau face timeout
3. **Linia care lipsește:** `response += f"Content-Length: {len(body)}\r\n"` (înainte de `response += "\r\n"`)

## DEBUG-3: Soluție

1. **Problema:** `recv(4096)` citește MAXIMUM 4096 bytes, dar răspunsul poate fi mai mare
2. **Pentru 10KB:** Primim doar primii 4096 bytes, răspunsul e trunchiat
3. **Algoritm corect:**
```python
response = b""
while True:
    chunk = sock.recv(4096)
    if not chunk:
        break
    response += chunk
```
Sau citește Content-Length și folosește `recv` în buclă până ai exact atâția bytes.

</details>

---

*Material pentru Seminar 8, Rețele de Calculatoare, ASE București*
