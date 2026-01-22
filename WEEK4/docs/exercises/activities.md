# Activități Complementare – Săptămâna 4

> **Disciplină:** Rețele de Calculatoare  
> **Săptămâna:** 4  
> **Scop:** Consolidare concepte fără a scrie cod de la zero

Aceste activități completează exercițiile de implementare. Cercetările arată că studenții învață mai eficient când alternează între scriere de cod și alte tipuri de activități (Parsons et al., 2006; Lopez et al., 2008).

**Timp total estimat:** 45-60 minute

---

## Partea A: Parsons Problems (Reordonare Cod)

Parsons Problems îți cer să reordonezi linii de cod amestecate. Nu scrii nimic – doar aranjezi liniile în ordine corectă.

**De ce funcționează:** Te forțează să gândești la structura programului fără overhead-ul de sintaxă.

---

### 🧩 Parsons #1: Funcția recv_exact()

**Context:** Această funcție citește exact `n` bytes dintr-un socket TCP. E fundamentală pentru protocoale binare.

**Cerință:** Reordonează liniile (A-H) pentru a obține implementarea corectă.

```python
# LINII AMESTECATE:

A)     return data
B)     while len(data) < n:
C) def recv_exact(sock, n):
D)         chunk = sock.recv(n - len(data))
E)     data = b""
F)         if not chunk:
G)             raise ConnectionError("Connection closed")
H)         data += chunk
```

**Spațiu de lucru:**
```
Ordinea ta: ___ → ___ → ___ → ___ → ___ → ___ → ___ → ___
```

<details>
<summary>✅ Verifică soluția</summary>

**Ordine corectă: C → E → B → D → F → G → H → A**

```python
def recv_exact(sock, n):           # C - definiție funcție
    data = b""                      # E - inițializare buffer gol
    while len(data) < n:            # B - buclă până avem n bytes
        chunk = sock.recv(n - len(data))  # D - citim ce mai lipsește
        if not chunk:               # F - verificare conexiune închisă
            raise ConnectionError("Connection closed")  # G - eroare
        data += chunk               # H - adăugăm la buffer
    return data                     # A - returnăm rezultatul
```

**Greșeli comune:**
- A pus la început (return înainte de calcul)
- F-G puse în afara while-ului
- E pus în interiorul while (resetează buffer-ul!)

</details>

---

### 🧩 Parsons #2: Împachetare mesaj binar

**Context:** Funcția construiește un mesaj binar cu header și CRC.

**Cerință:** Reordonează liniile pentru implementarea corectă.

```python
# LINII AMESTECATE:

A) def pack_message(msg_type, payload, seq):
B)     return header + payload
C)     header = struct.pack(HEADER_FMT, MAGIC, VERSION, msg_type, len(payload), seq, crc)
D)     crc = zlib.crc32(header_no_crc + payload) & 0xFFFFFFFF
E)     MAGIC, VERSION = b"NP", 1
F)     header_no_crc = struct.pack("!2sBBHI", MAGIC, VERSION, msg_type, len(payload), seq)
```

**Spațiu de lucru:**
```
Ordinea ta: ___ → ___ → ___ → ___ → ___ → ___
```

<details>
<summary>✅ Verifică soluția</summary>

**Ordine corectă: A → E → F → D → C → B**

```python
def pack_message(msg_type, payload, seq):  # A - definiție
    MAGIC, VERSION = b"NP", 1               # E - constante
    header_no_crc = struct.pack("!2sBBHI", MAGIC, VERSION, msg_type, len(payload), seq)  # F
    crc = zlib.crc32(header_no_crc + payload) & 0xFFFFFFFF  # D - CRC peste header + payload
    header = struct.pack(HEADER_FMT, MAGIC, VERSION, msg_type, len(payload), seq, crc)  # C
    return header + payload                 # B - rezultat final
```

**Logica:** Trebuie să calculezi CRC-ul ÎNAINTE de a construi header-ul complet, pentru că CRC-ul face parte din header.

</details>

---

### 🧩 Parsons #3: Server TCP simplu

**Context:** Structura de bază a unui server TCP care acceptă conexiuni.

```python
# LINII AMESTECATE:

A)         conn.close()
B)     while True:
C) server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
D)         conn, addr = server.accept()
E) server.bind(("0.0.0.0", 5400))
F)         data = conn.recv(1024)
G) server.listen(5)
H)         conn.sendall(b"OK")
I) import socket
```

**Spațiu de lucru:**
```
Ordinea ta: ___ → ___ → ___ → ___ → ___ → ___ → ___ → ___ → ___
```

<details>
<summary>✅ Verifică soluția</summary>

**Ordine corectă: I → C → E → G → B → D → F → H → A**

```python
import socket                                    # I
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # C
server.bind(("0.0.0.0", 5400))                  # E
server.listen(5)                                 # G
while True:                                      # B
    conn, addr = server.accept()                 # D
    data = conn.recv(1024)                       # F
    conn.sendall(b"OK")                          # H
    conn.close()                                 # A
```

**Ordinea obligatorie:** socket() → bind() → listen() → accept()

</details>

---

## Partea B: Code Tracing (Execuție Mentală)

Code Tracing îți cere să "rulezi" codul în cap și să prezici output-ul. Completează tabelele pas cu pas.

**De ce funcționează:** Construiește modelul mental al execuției – esențial pentru debugging.

---

### 📋 Trace #1: Procesare comenzi

**Cod de urmărit:**

```python
state = {}
commands = ["SET a 1", "SET b 2", "GET a", "SET a 3", "COUNT", "GET c"]

for cmd in commands:
    parts = cmd.split()
    if parts[0] == "SET":
        state[parts[1]] = parts[2]
        print(f"OK stored {parts[1]}")
    elif parts[0] == "GET":
        if parts[1] in state:
            print(f"OK {state[parts[1]]}")
        else:
            print("ERR not_found")
    elif parts[0] == "COUNT":
        print(f"OK {len(state)} keys")
```

**Completează tabelul:**

| Pas | cmd | parts | state după | Output |
|-----|-----|-------|------------|--------|
| 1 | SET a 1 | ['SET', 'a', '1'] | | |
| 2 | SET b 2 | | | |
| 3 | GET a | | | |
| 4 | SET a 3 | | | |
| 5 | COUNT | | | |
| 6 | GET c | | | |

<details>
<summary>✅ Verifică soluția</summary>

| Pas | cmd | parts | state după | Output |
|-----|-----|-------|------------|--------|
| 1 | SET a 1 | ['SET', 'a', '1'] | {'a': '1'} | OK stored a |
| 2 | SET b 2 | ['SET', 'b', '2'] | {'a': '1', 'b': '2'} | OK stored b |
| 3 | GET a | ['GET', 'a'] | (nemodificat) | OK 1 |
| 4 | SET a 3 | ['SET', 'a', '3'] | {'a': '3', 'b': '2'} | OK stored a |
| 5 | COUNT | ['COUNT'] | (nemodificat) | OK 2 keys |
| 6 | GET c | ['GET', 'c'] | (nemodificat) | ERR not_found |

**Observații:**
- La pasul 4, valoarea lui 'a' se suprascrie (de la '1' la '3')
- La pasul 6, 'c' nu există în state

</details>

---

### 📋 Trace #2: Parsing header binar

**Cod de urmărit:**

```python
import struct

data = b"NP\x01\x03\x00\x0bhello world"
#       ^^  ^   ^   ^^^^  ^^^^^^^^^^^
#       0-1 2   3   4-5   6+

magic = data[0:2]
version = data[2]
msg_type = data[3]
payload_len = struct.unpack("!H", data[4:6])[0]
payload = data[6:6+payload_len]

print(f"magic={magic}, ver={version}, type={msg_type}")
print(f"payload_len={payload_len}, payload={payload}")
```

**Completează:**

| Variabilă | Slice/Operație | Valoare |
|-----------|----------------|---------|
| magic | data[0:2] | |
| version | data[2] | |
| msg_type | data[3] | |
| payload_len | unpack("!H", data[4:6]) | |
| payload | data[6:6+?] | |

<details>
<summary>✅ Verifică soluția</summary>

| Variabilă | Slice/Operație | Valoare |
|-----------|----------------|---------|
| magic | data[0:2] | b"NP" |
| version | data[2] | 1 (0x01) |
| msg_type | data[3] | 3 (0x03 = PUT_REQ) |
| payload_len | unpack("!H", data[4:6]) | 11 (0x000b) |
| payload | data[6:17] | b"hello world" |

**Explicație `!H`:**
- `!` = network byte order (big-endian)
- `H` = unsigned short (2 bytes)
- `\x00\x0b` = 0×256 + 11 = 11

</details>

---

### 📋 Trace #3: CRC și validare

**Cod de urmărit:**

```python
import zlib

def crc32(data):
    return zlib.crc32(data) & 0xFFFFFFFF

# Sender
original = b"test"
sent_crc = crc32(original)
print(f"Sent CRC: {sent_crc:08x}")

# Receiver - pachet OK
received_ok = b"test"
check_ok = crc32(received_ok)
print(f"Check OK: {check_ok:08x}, Valid: {check_ok == sent_crc}")

# Receiver - pachet corupt (un byte modificat)
received_bad = b"tEst"  # 'e' înlocuit cu 'E'
check_bad = crc32(received_bad)
print(f"Check BAD: {check_bad:08x}, Valid: {check_bad == sent_crc}")
```

**Predicții (fără a rula codul):**

1. `sent_crc` și `check_ok` vor fi: ☐ Egale ☐ Diferite
2. `check_bad == sent_crc` va fi: ☐ True ☐ False
3. De ce CRC-ul diferă pentru "test" vs "tEst"?

<details>
<summary>✅ Verifică soluția</summary>

1. **Egale** - aceleași date produc același CRC
2. **False** - date diferite produc CRC diferit
3. **Explicație:** Caracterul 'e' (0x65) vs 'E' (0x45) sunt bytes diferiți. CRC-ul se calculează pe bytes, nu pe sensul semantic.

**Output real:**
```
Sent CRC: d87f7e0c
Check OK: d87f7e0c, Valid: True
Check BAD: 5cc2cb1a, Valid: False
```

</details>

---

## Partea C: Debugging Exercises (Găsește Bug-urile)

Codul de mai jos conține erori intenționate. Găsește-le FĂRĂ să rulezi codul.

**De ce funcționează:** Antrenează pattern recognition pentru erori comune.

---

### 🐛 Debug #1: send_framed() – 3 bug-uri

**Cod cu bug-uri:**

```python
def send_framed(sock, message):
    """Trimite mesaj cu length-prefix framing."""
    payload = message                           # Linia 1
    header = f"{len(message)} "                 # Linia 2
    sock.send(header + payload)                 # Linia 3
```

**Găsește cele 3 bug-uri:**

| Bug # | Linia | Problema | Fix |
|-------|-------|----------|-----|
| 1 | | | |
| 2 | | | |
| 3 | | | |

<details>
<summary>✅ Verifică soluția</summary>

| Bug # | Linia | Problema | Fix |
|-------|-------|----------|-----|
| 1 | 1 | `message` e string, dar socket-ul vrea bytes | `payload = message.encode("utf-8")` |
| 2 | 2 | `len(message)` numără caractere, nu bytes (problemă pentru non-ASCII) | `len(payload)` după encode |
| 3 | 3 | `send()` nu garantează trimiterea totală; concatenare string+bytes | `sock.sendall(header.encode("ascii") + payload)` |

**Cod corectat:**
```python
def send_framed(sock, message):
    payload = message.encode("utf-8")
    header = f"{len(payload)} ".encode("ascii")
    sock.sendall(header + payload)
```

</details>

---

### 🐛 Debug #2: recv_until() – 2 bug-uri

**Cod cu bug-uri:**

```python
def recv_until(sock, delimiter):
    """Citește până la delimiter (inclusiv)."""
    buffer = ""                                 # Linia 1
    while delimiter not in buffer:              # Linia 2
        chunk = sock.recv(1024)                 # Linia 3
        buffer += chunk                         # Linia 4
    return buffer                               # Linia 5
```

**Hints:**
- Ce se întâmplă dacă serverul închide conexiunea?
- Ce tip de date returnează `recv()`?

<details>
<summary>✅ Verifică soluția</summary>

| Bug # | Linia | Problema | Fix |
|-------|-------|----------|-----|
| 1 | 1, 4 | `buffer` e string, dar `recv()` returnează bytes | `buffer = b""`, `delimiter` trebuie să fie bytes |
| 2 | 3-4 | Nu verifică dacă `chunk` e gol (conexiune închisă) → buclă infinită | Adaugă `if not chunk: raise ConnectionError()` |

**Cod corectat:**
```python
def recv_until(sock, delimiter):
    buffer = b""
    while delimiter not in buffer:
        chunk = sock.recv(1024)
        if not chunk:
            raise ConnectionError("Connection closed")
        buffer += chunk
    return buffer
```

</details>

---

### 🐛 Debug #3: validate_crc() – 2 bug-uri subtile

**Cod cu bug-uri:**

```python
def validate_crc(header, payload, received_crc):
    """Verifică integritatea mesajului."""
    # Header: magic(2) + ver(1) + type(1) + len(2) + seq(4) + crc(4) = 14 bytes
    header_for_crc = header[:14]                # Linia 1
    computed = zlib.crc32(header_for_crc + payload)  # Linia 2
    return computed == received_crc             # Linia 3
```

**Hint:** CRC-ul din header face parte din... header. Gândește-te la ce date s-au folosit la calcul inițial.

<details>
<summary>✅ Verifică soluția</summary>

| Bug # | Linia | Problema | Fix |
|-------|-------|----------|-----|
| 1 | 1 | Include CRC-ul în datele pentru calcul CRC (greșit!) | `header_for_crc = header[:10]` (fără ultimii 4 bytes = CRC) |
| 2 | 2 | `zlib.crc32()` poate returna negativ pe unele platforme | `& 0xFFFFFFFF` pentru unsigned |

**Cod corectat:**
```python
def validate_crc(header, payload, received_crc):
    header_for_crc = header[:10]  # Exclude CRC din calcul
    computed = zlib.crc32(header_for_crc + payload) & 0xFFFFFFFF
    return computed == received_crc
```

**Explicație:** La trimitere, CRC-ul se calculează pe header FĂRĂ câmpul CRC. Dacă incluzi CRC-ul în calcul, obții alt CRC!

</details>

---

## Partea D: Code Reading (Înțelegere fără scriere)

Citește codul și răspunde la întrebări. NU scrie cod – doar explică.

**De ce funcționează:** Antrenează înțelegerea codului scris de alții (skill esențial în echipe).

---

### 📖 Reading #1: Ce face această funcție?

```python
def mystery_a(data, offset=0):
    if len(data) < offset + 4:
        return None, offset
    value = struct.unpack("!I", data[offset:offset+4])[0]
    return value, offset + 4
```

**Întrebări:**

1. Ce reprezintă `!I` în struct.unpack?
2. De ce returnează un tuple `(value, offset+4)`?
3. Când returnează `(None, offset)`?
4. Dă un nume mai descriptiv funcției.
5. Pentru ce tip de protocol ar fi utilă?

<details>
<summary>✅ Răspunsuri</summary>

1. `!` = network byte order (big-endian), `I` = unsigned int (4 bytes)
2. Returnează și noul offset pentru a putea citi următorul câmp (pattern "cursor")
3. Când nu sunt suficienți bytes în `data` (buffer incomplet)
4. `read_uint32()` sau `unpack_uint32_with_offset()`
5. Protocoale binare cu câmpuri multiple – citești secvențial fără să recalculezi offsetul manual

</details>

---

### 📖 Reading #2: Analizează serverul

```python
def handle_client(conn, addr, state, lock):
    try:
        while True:
            raw = recv_framed(conn)
            if not raw:
                break
            with lock:
                response = process_command(state, raw)
            send_framed(conn, response)
    except ConnectionError:
        pass
    finally:
        conn.close()
        print(f"[-] {addr} disconnected")
```

**Întrebări:**

1. De ce primește `lock` ca parametru?
2. Ce se întâmplă dacă `recv_framed` aruncă excepție?
3. De ce `conn.close()` e în `finally`?
4. Este acest server single-threaded sau multi-threaded? De unde știi?
5. Ce problemă ar apărea FĂRĂ `with lock`?

<details>
<summary>✅ Răspunsuri</summary>

1. `lock` (mutex) protejează `state` împotriva accesului concurent din mai multe threaduri
2. Excepția e prinsă de `except ConnectionError`, se iese din funcție curat
3. `finally` garantează că socket-ul se închide INDIFERENT cum se termină funcția (normal sau excepție)
4. **Multi-threaded** - prezența `lock`-ului indică acces partajat la `state` din mai multe threaduri
5. **Race condition**: două threaduri ar putea modifica `state` simultan, corupând datele (ex: două SET-uri pe aceeași cheie)

</details>

---

### 📖 Reading #3: Protocol state machine

```python
STATES = {"INIT": 0, "HANDSHAKE": 1, "READY": 2, "ERROR": 3}

def transition(current_state, event):
    transitions = {
        ("INIT", "connect"):      "HANDSHAKE",
        ("HANDSHAKE", "ack"):     "READY",
        ("HANDSHAKE", "timeout"): "ERROR",
        ("READY", "request"):     "READY",
        ("READY", "disconnect"):  "INIT",
        ("ERROR", "reset"):       "INIT",
    }
    return transitions.get((current_state, event), "ERROR")
```

**Întrebări:**

1. Desenează diagrama de stări (4 stări, săgețile dintre ele)
2. Ce se întâmplă pentru un eveniment neașteptat? (ex: "request" în starea "INIT")
3. Poate protocolul să ajungă în "READY" direct din "INIT"?
4. Cum ai extinde pentru a adăuga timeout și în starea "READY"?

<details>
<summary>✅ Răspunsuri</summary>

1. **Diagramă:**
```
    ┌──────────────────────────────────────────┐
    │                                          │
    ▼            connect         ack           │
  [INIT] ──────────────► [HANDSHAKE] ────► [READY]
    ▲                         │               │ │
    │         reset           │ timeout       │ │ request
    └───────── [ERROR] ◄──────┘               │ │ (self-loop)
    │                                         │ │
    └─────────────── disconnect ──────────────┘ │
                                                │
```

2. Returnează "ERROR" (default din `.get()`)
3. **Nu** - trebuie obligatoriu prin HANDSHAKE (connect → ack)
4. Adaugi: `("READY", "timeout"): "ERROR"` sau `("READY", "timeout"): "HANDSHAKE"` pentru reconectare

</details>

---

## Partea E: Code Review (Evaluare Cod Coleg)

Code Review e o competență profesională esențială. Evaluezi cod scris de altcineva și oferi feedback constructiv.

---

### 👀 Review #1: Evaluează această implementare recv_framed()

Un coleg a scris această funcție. Identifică **3 probleme** și propune soluții.

```python
def recv_framed(sock):
    # citeste pana la spatiu
    buf = ""
    while " " not in buf:
        buf += sock.recv(1)
    
    # extrage lungimea
    length = int(buf)
    
    # citeste payload
    payload = sock.recv(length)
    
    return payload
```

**Completează:**

| # | Problemă | Severitate | Soluție propusă |
|---|----------|------------|-----------------|
| 1 | | | |
| 2 | | | |
| 3 | | | |

<details>
<summary>✅ Verifică răspunsurile</summary>

| # | Problemă | Severitate | Soluție |
|---|----------|------------|---------|
| 1 | `buf = ""` e string, dar `recv()` returnează bytes | **Critică** | `buf = b""` și verifică `b" "` |
| 2 | `sock.recv(length)` poate returna mai puțin | **Critică** | Buclă până citești tot: `while len(payload) < length` |
| 3 | Nu verifică dacă `recv()` returnează gol (conexiune închisă) | **Medie** | `if not chunk: raise ConnectionError()` |
| Bonus | `int(buf)` include spațiul | **Mică** | `int(buf.strip())` sau `int(buf[:-1])` |

**Cod corectat:**
```python
def recv_framed(sock):
    buf = b""
    while b" " not in buf:
        chunk = sock.recv(1)
        if not chunk:
            raise ConnectionError("closed")
        buf += chunk
    
    length = int(buf[:-1])  # exclude spațiul
    
    payload = b""
    while len(payload) < length:
        chunk = sock.recv(length - len(payload))
        if not chunk:
            raise ConnectionError("closed")
        payload += chunk
    
    return payload
```

</details>

---

### 👀 Review #2: Evaluează protocolul binar

Colegul a definit acest format pentru un protocol de chat:

```
Header (variabil):
  username: string terminat cu \0
  timestamp: 8 bytes (Unix epoch)
  message_len: 2 bytes
Payload:
  message: message_len bytes
```

**Întrebări de review:**

1. Ce problemă majoră are acest design de header?
2. Cum ar afecta performanța server-ului?
3. Propune un design îmbunătățit.

<details>
<summary>✅ Răspunsuri</summary>

**1. Problemă majoră:** Header-ul are lungime variabilă (username-ul poate fi 1 byte sau 100 bytes). Serverul nu știe câți bytes să citească pentru header fără să parseze byte cu byte.

**2. Impact performanță:** Citirea byte-cu-byte e lentă. Pentru fiecare mesaj, serverul face multe apeluri `recv(1)` în loc de un singur `recv(HEADER_SIZE)`.

**3. Design îmbunătățit:**
```
Header (fix 26 bytes):
  username_len: 1 byte
  username: 15 bytes (padding cu \0)
  timestamp: 8 bytes
  message_len: 2 bytes
  (total: 1 + 15 + 8 + 2 = 26 bytes fix)
```
SAU
```
Header (fix 4 bytes):
  total_len: 4 bytes (include tot mesajul)
Payload (variabil):
  username\0 + timestamp + message
```

**Principiu:** Header-urile fixe permit parsare eficientă. Dacă trebuie variabil, pune lungimea totală PRIMA.

</details>

---

## Verificare finală

După completarea exercițiilor, verifică:

- [ ] Am rezolvat toate cele 3 Parsons Problems
- [ ] Am completat cele 3 Trace Exercises (cu tabelele)
- [ ] Am găsit toate bug-urile în cele 3 Debug Exercises
- [ ] Am răspuns la întrebările din cele 3 Code Reading
- [ ] Am făcut cele 2 Code Review exercises

**Estimare timp:** 60-75 minute pentru toate activitățile.

---

## Resurse suplimentare

- **Parsons Problems research:** Parsons, D., & Haden, P. (2006). Parson's programming puzzles
- **Code tracing benefits:** Lopez, M., et al. (2008). Relationships between reading, tracing and writing skills
- **Why debugging exercises work:** McCauley, R., et al. (2008). Debugging: A review of the literature

---

*Activități complementare pentru Săptămâna 4 – Protocoale Custom*  
*Conform principiului P10 Brown & Wilson: "Not just code"*
