# Seminar 8 – Explicații Teoretice
## Servicii Internet: Server HTTP + Reverse Proxy

---

## Introducere

Acest seminar pune în practică conceptele de la Cursul 8 (nivelul transport) și pregătește terenul pentru nivelul aplicație. Vom implementa:

1. **Server HTTP minimal** – folosind socket-uri TCP
2. **Reverse Proxy** – pentru load balancing și abstractizarea backend-urilor

Aceste implementări permit observarea directă a handshake-ului TCP, a structurii HTTP și a fluxului de date între client, proxy și backend.

> **Notă din experiența predării:** Studenții care implementează manual un server HTTP 
> înțeleg mult mai bine de ce framework-urile precum Flask au anumite limitări sau 
> comportamente. E o investiție de 2 ore care se amortizează pe tot semestrul.

---

## 1. Protocolul HTTP – Recapitulare

### Analogie: Ce este un HTTP Request? (Concret → Pictorial → Abstract)

**✉️ CONCRET (Analogie scrisoare):**

Un HTTP request e ca o scrisoare oficială:
- **Request Line** = Plicul cu adresa (către cine trimiți și ce vrei)
- **Headers** = Antetul scrisorii (data, de la cine, preferințe)
- **Linie goală** = Separatorul între antet și conținut
- **Body** = Conținutul propriu-zis al scrisorii

Când trimiți o scrisoare:
1. Scrii adresa pe plic ("GET /pagina HTTP/1.1")
2. Adaugi antetul formal ("Host: server.com")
3. Lași un rând gol
4. Scrii mesajul (doar pentru POST/PUT)

**📊 PICTORIAL:**

```
┌────────────────────────────────────────┐
│ GET /index.html HTTP/1.1               │ ← Request Line (plicul)
├────────────────────────────────────────┤
│ Host: www.example.com                  │
│ User-Agent: curl/8.0                   │ ← Headers (antetul)
│ Accept: */*                            │
├────────────────────────────────────────┤
│                                        │ ← Linie goală (separator)
├────────────────────────────────────────┤
│ (body - gol pentru GET)                │ ← Body (conținutul)
└────────────────────────────────────────┘
```

**💻 ABSTRACT (Format):**

```
METHOD SP REQUEST-TARGET SP HTTP-VERSION CRLF
Header-Name: Header-Value CRLF
Header-Name: Header-Value CRLF
CRLF
[Body]
```

---

### Ce este HTTP?

**HyperText Transfer Protocol** este un protocol de nivel aplicație care:
- Rulează peste TCP (sau QUIC pentru HTTP/3)
- Folosește modelul **request-response**
- Este **stateless** (fiecare request este independent)
- Folosește format text human-readable (HTTP/1.x)

### Structura unui HTTP Request

```http
GET /index.html HTTP/1.1
Host: www.example.com
User-Agent: curl/8.0
Accept: */*

```

**Componente:**
1. **Request Line**: `METHOD SP REQUEST-TARGET SP HTTP-VERSION CRLF`
2. **Headers**: `Header-Name: Header-Value CRLF`
3. **Empty Line**: `CRLF` (separă headers de body)
4. **Body** (opțional): date pentru POST/PUT

### Structura unui HTTP Response

```http
HTTP/1.1 200 OK
Date: Wed, 25 Dec 2024 10:00:00 GMT
Server: Apache/2.4
Content-Type: text/html; charset=utf-8
Content-Length: 1234

<!DOCTYPE html>
<html>...
```

**Componente:**
1. **Status Line**: `HTTP-VERSION SP STATUS-CODE SP REASON-PHRASE CRLF`
2. **Headers**: similar cu request
3. **Empty Line**: `CRLF`
4. **Body**: conținutul resursei

### Status Codes importante

| Cod | Categorie | Semnificație |
|-----|-----------|--------------|
| 200 | 2xx Success | OK – request procesat cu succes |
| 201 | 2xx Success | Created – resursă creată |
| 301 | 3xx Redirect | Moved Permanently |
| 400 | 4xx Client Error | Bad Request – sintaxă invalidă |
| 404 | 4xx Client Error | Not Found – resursa nu există |
| 405 | 4xx Client Error | Method Not Allowed |
| 500 | 5xx Server Error | Internal Server Error |
| 502 | 5xx Server Error | Bad Gateway – upstream eșuat |

---

## 2. Server HTTP cu Socket-uri

### Analogie: Ce este un Socket? (Concret → Pictorial → Abstract)

**🏢 CONCRET (Analogie telefon de birou):**

Imaginează-ți un socket ca un telefon de birou într-o clădire de birouri:
- **IP-ul** = numărul de telefon al clădirii (ex: 021-xxx-xxxx)
- **Portul** = extensia internă (ex: extensia 8080 = biroul IT)
- **Socket-ul** = aparatul telefonic din birou care permite conversația

Când suni la o companie:
1. Formezi numărul clădirii (IP)
2. Spui extensia (Port)
3. Cineva ridică telefonul (accept)
4. Vorbiți (send/recv)
5. Închideți (close)

**📊 PICTORIAL:**

```
┌─────────────────────────────────┐       ┌─────────────────────────────────┐
│         CLIENT                  │       │         SERVER                  │
│  ┌─────────────────────────┐    │       │    ┌─────────────────────────┐  │
│  │  IP: 192.168.1.100      │    │       │    │  IP: 10.0.0.1           │  │
│  │  Port: 54321 (efemer)   │    │  TCP  │    │  Port: 8080 (fix)       │  │
│  │  ┌─────────────────┐    │◄──────────►│    │  ┌─────────────────┐    │  │
│  │  │    SOCKET       │    │    │       │    │  │    SOCKET       │    │  │
│  │  │  (telefonul)    │    │    │       │    │  │  (telefonul)    │    │  │
│  │  └─────────────────┘    │    │       │    │  └─────────────────┘    │  │
│  └─────────────────────────┘    │       │    └─────────────────────────┘  │
└─────────────────────────────────┘       └─────────────────────────────────┘
         Tu (browser)                              Serverul web
```

**💻 ABSTRACT (Cod Python):**

```python
# Server: "Biroul care așteaptă apeluri"
server_socket = socket.socket(AF_INET, SOCK_STREAM)  # creează telefonul
server_socket.bind(('0.0.0.0', 8080))                # setează extensia
server_socket.listen(5)                              # pornește să asculte
conn, addr = server_socket.accept()                  # ridică telefonul

# Client: "Cel care sună"
client_socket = socket.socket(AF_INET, SOCK_STREAM)  # creează telefonul
client_socket.connect(('10.0.0.1', 8080))            # formează numărul
```

---

### De ce implementăm de la zero?

Bibliotecile moderne (Flask, Django, Express) abstractizează complet protocolul HTTP. Implementând manual, înțelegem:

1. **Cum arată un request HTTP real** (bytes pe fir)
2. **De ce este nevoie de Content-Length** (delimitare body)
3. **Cum funcționează status line** (200 OK, 404 Not Found)
4. **Procesul de servire fișiere statice**

### Algoritm Server HTTP

```
1. Crează socket TCP (AF_INET, SOCK_STREAM)
2. Bind pe (host, port)
3. Listen (accept conexiuni)
4. Loop:
   a. Accept conexiune client → (conn, addr)
   b. Citește request până la CRLFCRLF
   c. Parsează request line (METHOD, TARGET, VERSION)
   d. Validează (doar GET/HEAD acceptate)
   e. Mapează TARGET la cale fișier
   f. Verifică directory traversal (securitate!)
   g. Citește fișierul sau generează 404
   h. Construiește și trimite response
   i. Închide conexiunea
```

### Parsing HTTP Request

```python
def parse_http_request(raw: bytes) -> HttpRequest:
    text = raw.decode("iso-8859-1")  # HTTP/1.x: ISO-8859-1
    
    # Separator headers/body
    head, body = text.split("\r\n\r\n", 1)
    lines = head.split("\r\n")
    
    # Request line: "GET /path HTTP/1.1"
    method, target, version = lines[0].split()
    
    # Headers: "Key: Value"
    headers = {}
    for line in lines[1:]:
        key, value = line.split(":", 1)
        headers[key.strip().lower()] = value.strip()
    
    return HttpRequest(method, target, version, headers, raw)
```

### Construire HTTP Response

```python
def build_response(status: int, body: bytes, content_type: str) -> bytes:
    reasons = {200: "OK", 404: "Not Found", ...}
    
    response = f"HTTP/1.1 {status} {reasons[status]}\r\n"
    response += f"Content-Type: {content_type}\r\n"
    response += f"Content-Length: {len(body)}\r\n"
    response += f"Connection: close\r\n"
    response += "\r\n"
    
    return response.encode("iso-8859-1") + body
```

### Securitate: Directory Traversal

**Problemă**: Un client rău intenționat poate cere:
```
GET /../../../etc/passwd HTTP/1.1
```

**Soluție**: Normalizare și validare cale:
```python
def safe_path(target: str, www_root: str) -> str:
    # Decodare %2e%2e → ..
    path = urllib.parse.unquote(target)
    
    # Normalizare (rezolvă ../)
    normalized = os.path.normpath(path)
    
    # Cale absolută
    full_path = os.path.join(www_root, normalized)
    
    # VERIFICARE CRITICĂ
    if not full_path.startswith(www_root):
        raise SecurityError("Directory traversal detected!")
    
    return full_path
```

---

## 3. Reverse Proxy

### Analogie: Ce este un Reverse Proxy? (Concret → Pictorial → Abstract)

**🏨 CONCRET (Analogie hotel):**

Reverse proxy-ul e ca un **recepționer de hotel**:
- Tu (clientul) vii la recepție și ceri o cameră
- Recepționerul NU îți dă el camera — el contactează housekeeping (backend)
- Housekeeping pregătește camera și confirmă recepționerului
- Recepționerul îți dă cheia

Tu nu știi (și nu trebuie să știi) care membru din housekeeping ți-a pregătit camera.

**Beneficii ale recepționerului:**
- Știe care camere sunt libere (load balancing)
- Verifică actele tale o singură dată (SSL termination)
- Își amintește preferințele tale (caching)
- Protejează housekeeping-ul de hoți (security)

**📊 PICTORIAL:**

```
                                    ┌─────────────┐
                                 ┌──│ Backend A   │
┌──────────┐      ┌───────────┐  │  │ (camera 101)│
│  Client  │      │  Reverse  │  │  └─────────────┘
│  (oaspete│ ───► │  Proxy    │──┤
│          │      │ (recepție)│  │  ┌─────────────┐
└──────────┘      └───────────┘  └──│ Backend B   │
                                    │ (camera 102)│
                                    └─────────────┘
```

**💻 ABSTRACT (Flux):**

```
Client ──[GET /]──► Proxy ──[GET / + X-Forwarded-For]──► Backend A
Client ◄──[200 OK]── Proxy ◄──────[200 OK]─────────────── Backend A
```

---

### Ce este un Reverse Proxy?

Un **reverse proxy** este un server intermediar care:
- Primește request-uri de la clienți
- Le transmite către unul sau mai multe backend-uri
- Returnează răspunsul către client

```
┌────────┐         ┌─────────────┐         ┌───────────┐
│ Client │ ──────→ │ Rev. Proxy  │ ──────→ │ Backend A │
└────────┘         │             │         └───────────┘
                   │  (nginx,    │         ┌───────────┐
                   │   HAProxy)  │ ──────→ │ Backend B │
                   └─────────────┘         └───────────┘
```

### De ce Reverse Proxy?

1. **Load Balancing** – distribuie sarcina între servere
2. **SSL Termination** – gestionează certificatele central
3. **Caching** – reduce load pe backend
4. **Security** – ascunde structura internă
5. **Compression** – reduce bandwidth

> **De ce round-robin și nu random?** În practică, round-robin e preferabil pentru 
> debugging — poți prezice care backend va primi următorul request. Random pare mai 
> "fair" dar face troubleshooting-ul un coșmar.

### Algoritmi de Load Balancing

| Algoritm | Descriere | Când se folosește |
|----------|-----------|-------------------|
| Round-Robin | Rotație secvențială | Backend-uri identice |
| Weighted RR | Cu ponderi | Servere cu capacități diferite |
| Least Connections | Cel mai puțin ocupat | Sesiuni lungi |
| IP Hash | Același client → același server | Session affinity |

### Implementare Round-Robin în Python

```python
class RoundRobinBalancer:
    def __init__(self, backends: List[Backend]):
        self.backends = backends
        self._index = 0
        self._lock = threading.Lock()
    
    def next(self) -> Backend:
        with self._lock:
            backend = self.backends[self._index]
            self._index = (self._index + 1) % len(self.backends)
            return backend
```

### Header-uri Proxy

Când proxy-ul transmite request-ul către backend, adaugă header-uri informative:

| Header | Descriere |
|--------|-----------|
| `X-Forwarded-For` | IP-ul clientului original |
| `X-Forwarded-Proto` | Protocolul original (http/https) |
| `X-Forwarded-Host` | Host-ul original |
| `Via` | Identificator proxy (pentru debugging) |

**Exemplu transformare request:**

```http
# Request original de la client
GET /api/data HTTP/1.1
Host: myapp.com
User-Agent: curl/8.0

# Request transmis la backend
GET /api/data HTTP/1.1
Host: backend-1:8001
User-Agent: curl/8.0
X-Forwarded-For: 192.168.1.100
X-Forwarded-Host: myapp.com
Via: ASE-S8-Proxy
Connection: close
```

---

## 4. Observare în tcpdump

### Captură server HTTP simplu

```bash
# Terminal 1: Captură
sudo tcpdump -i lo port 8080 -nn -A

# Terminal 2: Server
python3 demo_http_server.py --port 8080

# Terminal 3: Client
curl http://127.0.0.1:8080/
```

**Ce observăm:**
1. **SYN** → SYN-ACK → ACK (three-way handshake)
2. **PSH-ACK** cu request HTTP (GET / HTTP/1.1...)
3. **PSH-ACK** cu response (HTTP/1.1 200 OK...)
4. **FIN** → ACK → FIN → ACK (închidere conexiune)

### Captură Reverse Proxy

```bash
sudo tcpdump -i lo '(port 8080 or port 8001)' -nn
```

**Ce observăm:**
- **Conexiune 1**: Client (port efemer) → Proxy (8080)
- **Conexiune 2**: Proxy (port efemer) → Backend (8001)
- Două handshake-uri TCP distincte!

---

## 5. nginx ca Reverse Proxy

### Configurare minimală

```nginx
http {
    upstream backend_pool {
        server 127.0.0.1:8001;
        server 127.0.0.1:8002;
    }
    
    server {
        listen 80;
        
        location / {
            proxy_pass http://backend_pool;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }
    }
}
```

### Testare nginx

```bash
# Pornire
sudo nginx -c /path/to/nginx.conf

# Test (observă alternarea backend-urilor)
for i in {1..4}; do
    curl -s -D - http://localhost/ -o /dev/null | grep X-Backend
done

# Oprire
sudo nginx -s stop
```

---

## 6. Docker pentru orchestrare

### docker-compose.yml simplu

```yaml
version: '3'
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - backend-a
      - backend-b

  backend-a:
    build: .
    command: python3 demo_http_server.py --port 8000 --id backend-A
    
  backend-b:
    build: .
    command: python3 demo_http_server.py --port 8000 --id backend-B
```

### Comenzi utile

```bash
# Pornire stack
docker-compose up -d

# Logs
docker-compose logs -f

# Test
curl http://localhost/

# Oprire
docker-compose down
```

---

## Rezumat

| Concept | Implementare | Observație |
|---------|--------------|------------|
| HTTP Request | Parsing request line + headers | Text format, CRLF delimitare |
| HTTP Response | Status line + headers + body | Content-Length obligatoriu |
| Server HTTP | Socket TCP + loop accept | Un thread per client |
| Reverse Proxy | Forward + modificare headers | Două conexiuni TCP |
| Load Balancing | Round-robin, least-conn | Thread-safe selection |
| Security | Path normalization | Previne directory traversal |

---

*Material pentru Seminar 8, Rețele de Calculatoare, ASE București*
