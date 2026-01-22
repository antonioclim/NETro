# Seminar 4: Implementarea Protocoalelor Text și Binare Custom

## Subiectele seminarului

Hai să implementăm protocoale de comunicare custom peste TCP și UDP. O să vedem de ce TCP nu garantează delimitarea mesajelor și cum rezolvăm problema asta prin framing.

**⏱️ Durată totală:** 90-120 minute

## Context și relevanță

Majoritatea protocoalelor aplicație (HTTP, SMTP, DNS) construiesc peste TCP sau UDP. Dacă înțelegi cum se proiectează un protocol custom, poți:
- Să debugezi probleme de comunicare (și o să ai)
- Să optimizezi transferuri de date
- Să înțelegi ce se întâmplă "sub capotă" la protocoalele existente

---

## Prerechizite

Din săptămânile anterioare ar trebui să știi:
- Cum creezi socket-uri TCP și UDP în Python
- Diferența conceptuală TCP (stream) vs UDP (datagrame)
- Funcțiile de bază: `socket()`, `bind()`, `listen()`, `accept()`, `connect()`, `send()`, `recv()`

### Recapitulare ultra-scurtă

```python
import socket

# TCP Server
srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
srv.bind(("0.0.0.0", 5400))
srv.listen()
conn, addr = srv.accept()
data = conn.recv(1024)
conn.send(b"Response")
conn.close()

# TCP Client
cli = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
cli.connect(("localhost", 5400))
cli.send(b"Hello")
response = cli.recv(1024)
cli.close()

# UDP
udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp.sendto(b"Hello", ("localhost", 5402))
data, addr = udp.recvfrom(1024)
```

---

## Problema de bază: TCP e un stream

**TCP nu păstrează granițele mesajelor.** Punct.

Dacă trimiți:
```python
conn.send(b"Hello")
conn.send(b"World")
```

Receptorul poate primi:
- `b"HelloWorld"` (totul într-un singur recv)
- `b"Hel"` apoi `b"loWorld"` (fragmentat aiurea)
- `b"Hello"` apoi `b"World"` (cum ai trimis - dar nu-i garantat!)

### Vizualizare: TCP Stream vs UDP Datagrame

```
TCP STREAM (fără granițe între mesaje):
┌─────────────────────────────────────────────────────┐
│ H e l l o W o r l d G o o d b y e │ ← un flux continuu
└─────────────────────────────────────────────────────┘
  ↓ recv() poate returna oricât
  "Hel" | "loWorldGo" | "odbye"    ← fragmentare imprevizibilă

UDP DATAGRAME (granițe păstrate):
┌─────────┐  ┌─────────┐  ┌─────────┐
│ Hello   │  │ World   │  │ Goodbye │  ← datagrame separate
└─────────┘  └─────────┘  └─────────┘
  ↓ recvfrom() returnează exact un datagram
  "Hello" | "World" | "Goodbye"   ← mesaje complete
```

**Analogie:** TCP e ca un flux de apă dintr-un furtun – împarți cum vrei. UDP e ca pachete poștale separate – fiecare vine întreg sau deloc.

---

### 🗳️ Peer Instruction: Ce primește recv()?

**⏱️ Timp:** 5 minute (1 min vot → 2 min discuție → 1 min revot → 1 min explicație)

**Răspunde singur (30 secunde), apoi discută cu colegul:**

Un client trimite:
```python
sock.send(b"ABC")
sock.send(b"DEF")
```

Serverul face:
```python
data = sock.recv(1024)
print(data)
```

**Ce poate afișa serverul?**

| Opțiune | Răspuns |
|---------|---------|
| A | Exact `b"ABC"` (primul send) |
| B | Exact `b"ABCDEF"` (totul concatenat) |
| C | `b"AB"` (parțial, doar 2 bytes) |
| D | Oricare din variantele de mai sus |

**Proces:**
1. Votează individual (ridică mâna pentru A/B/C/D)
2. Discută 2 minute cu colegul
3. Revotează

<details>
<summary><strong>Răspuns și explicație (click după revot)</strong></summary>

**Răspuns corect: D) Oricare din variantele de mai sus**

TCP e un *stream* de bytes, nu de mesaje. Sistemul de operare poate:
- Combina mai multe `send()` într-un singur segment TCP
- Fragmenta un `send()` mare în mai multe segmente
- Returna din `recv()` oricâți bytes sunt disponibili în buffer

**De-aia avem nevoie de framing!**

**Unde greșesc studenții de obicei:**
- **A** - cred că fiecare `send()` creează un "pachet" separat
- **B** - înțeleg concatenarea dar cred că e garantată
- **C** - mai rar, dar unii cred că recv() e limitat la primul segment

</details>

---

### Soluție: Framing

Framing = delimitarea mesajelor în stream. Două variante principale:

#### 1. Length-prefix (text sau binar)
```
<LUNGIME> <PAYLOAD>
```

#### 2. Delimiter-based
```
<PAYLOAD><NEWLINE>
```

---

## Ghid pas cu pas: Protocol TEXT cu Length-Prefix

**⏱️ Timing recomandat pentru live coding:**

| Pas | Durată | Ce facem |
|-----|--------|----------|
| Setup | 2 min | Import-uri, constante |
| Pas 1 | 3 min | Format mesaj, exemplu pe tablă |
| Pas 2 | 8 min | `recv_framed()` - construcție incrementală |
| Predicție | 1 min | "Ce returnează recv(1)?" |
| Pas 3 | 3 min | `send_framed()` |
| Pas 4 | 5 min | `process_command()` |
| Test | 3 min | Rulare și demonstrație |
| **Total** | ~25 min | |

### Pasul 1: Definirea formatului

```
Format: "<LEN> <PAYLOAD>"
- LEN = numărul de bytes din payload (ASCII decimal)
- Un spațiu separator
- PAYLOAD = conținutul mesajului (UTF-8)

Exemplu: "11 SET name Alice"
         ^^  ^^^^^^^^^^^^^^
         |   payload = "SET name Alice" (11 bytes)
         lungime
```

### Pasul 2: Funcția de primire (framing)

**🔮 Predicție înainte de cod:**
> Ce returnează `conn.recv(1)` dacă conexiunea e deschisă? Dar dacă e închisă?

```python
def recv_framed(conn: socket.socket) -> str:
    """
    Primește un mesaj complet cu length-prefix framing.
    
    Pași:
    1. Citim bytes până la spațiu → obținem LEN
    2. Parsăm LEN ca integer
    3. Citim exact LEN bytes → obținem PAYLOAD
    """
    # === CITIRE_HEADER ===
    # Citim până la spațiu
    buffer = b""
    while not buffer.endswith(b" "):
        chunk = conn.recv(1)
        if not chunk:
            raise ConnectionError("Connection closed")
        buffer += chunk
    
    # === PARSARE_LUNGIME ===
    length = int(buffer[:-1].decode("ascii"))
    
    # === CITIRE_PAYLOAD ===
    # Citim exact length bytes
    payload = b""
    while len(payload) < length:
        chunk = conn.recv(length - len(payload))
        if not chunk:
            raise ConnectionError("Connection closed")
        payload += chunk
    
    return payload.decode("utf-8")
```

### Pasul 3: Funcția de trimitere

```python
def send_framed(conn: socket.socket, message: str) -> None:
    """
    Trimite un mesaj cu length-prefix framing.
    """
    # === CODARE_PAYLOAD ===
    payload = message.encode("utf-8")
    
    # === CONSTRUIRE_HEADER ===
    header = f"{len(payload)} ".encode("ascii")
    
    # === TRIMITERE_ATOMICA ===
    conn.sendall(header + payload)
```

### Pasul 4: Procesarea comenzilor

```python
def process_command(state: dict, line: str) -> str:
    """
    Procesează o comandă și returnează răspunsul.
    """
    # === PARSARE_INPUT ===
    parts = line.strip().split()
    if not parts:
        return "ERR empty"
    
    cmd = parts[0].upper()
    
    # === DISPATCH_COMENZI ===
    if cmd == "PING":
        return "OK pong"
    
    if cmd == "SET":
        if len(parts) < 3:
            return "ERR usage: SET <key> <value>"
        key, value = parts[1], " ".join(parts[2:])
        state[key] = value
        return f"OK stored {key}"
    
    if cmd == "GET":
        if len(parts) != 2:
            return "ERR usage: GET <key>"
        key = parts[1]
        return f"OK {state.get(key, '')}" if key in state else "ERR not_found"
    
    return "ERR unknown_command"
```

---

## Ghid pas cu pas: Protocol BINAR cu Header Fix

**⏱️ Timing recomandat:**

| Pas | Durată | Ce facem |
|-----|--------|----------|
| Teorie | 5 min | Avantaje binar, analogie plic |
| Pas 1 | 5 min | Definire header cu struct |
| Pas 2 | 3 min | CRC32 - explicație și cod |
| Pas 3 | 5 min | Împachetare mesaj |
| Pas 4 | 5 min | Despachetare și validare |
| PI | 5 min | Peer Instruction: CRC mismatch |
| **Total** | ~28 min | |

### De ce binar?
- Parsing predictibil (știi exact câți bytes citești)
- Overhead mai mic pentru date mari
- Include CRC pentru detecție erori

### Pasul 1: Definirea header-ului cu struct

```python
import struct

# Header: magic(2) + version(1) + type(1) + payload_len(2) + seq(4) + crc(4)
# Total: 14 bytes
HEADER_FORMAT = "!2sBBHII"
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)  # = 14

# "!" = network byte order (big-endian)
# "2s" = 2 bytes string
# "B" = unsigned byte (0-255)
# "H" = unsigned short (0-65535)
# "I" = unsigned int (0-4294967295)
```

Header-ul binar e ca un plic poștal standardizat. Poștașul știe exact unde să caute: colțul din stânga-sus = expeditor, centru = destinatar, dreapta = timbru. Nu trebuie să deschidă plicul ca să știe unde să-l livreze.

### Pasul 2: Calculul CRC32

```python
import zlib

def crc32(data: bytes) -> int:
    """
    CRC32 pentru verificarea integrității.
    Masca & 0xFFFFFFFF asigură rezultat unsigned pe 32 biți.
    """
    return zlib.crc32(data) & 0xFFFFFFFF
```

CRC-ul funcționează ca suma de control de pe un bon fiscal. Aduni toate articolele, compari cu totalul tipărit. Dacă nu se potrivește, știi că ceva e greșit – dar nu știi exact ce. La fel, CRC-ul detectează erori, nu le corectează.

### Pasul 3: Împachetarea unui mesaj

**🔮 Predicție înainte de cod:**
> În ce ordine construim header-ul? Putem calcula CRC-ul la final?

```python
def pack_message(msg_type: int, payload: bytes, seq: int) -> bytes:
    """
    Construiește mesajul complet: header + payload
    """
    MAGIC = b"NP"
    VERSION = 1
    
    # === HEADER_PARTIAL ===
    # Header fără CRC (pentru calcul CRC)
    header_no_crc = struct.pack("!2sBBHI", MAGIC, VERSION, msg_type, len(payload), seq)
    
    # === CALCUL_CRC ===
    # CRC peste header + payload
    full_crc = crc32(header_no_crc + payload)
    
    # === HEADER_COMPLET ===
    header = struct.pack(HEADER_FORMAT, MAGIC, VERSION, msg_type, len(payload), seq, full_crc)
    
    return header + payload
```

### Pasul 4: Despachetarea

```python
def unpack_header(data: bytes) -> tuple:
    """
    Extrage câmpurile din header.
    """
    magic, ver, mtype, plen, seq, crc = struct.unpack(HEADER_FORMAT, data)
    return magic, ver, mtype, plen, seq, crc

def validate_message(header_bytes: bytes, payload: bytes, received_crc: int) -> bool:
    """
    Verifică CRC-ul mesajului.
    """
    # === EXCLUDE_CRC_DIN_CALCUL ===
    header_no_crc = header_bytes[:10]  # Header fără câmpul CRC
    
    # === RECALCULEAZA_CRC ===
    computed_crc = crc32(header_no_crc + payload)
    
    return computed_crc == received_crc
```

---

### 🗳️ Peer Instruction: CRC Mismatch

**⏱️ Timp:** 5 minute

**Răspunde singur, apoi discută:**

Serverul primește un pachet binar și raportează "CRC mismatch". Care dintre următoarele **NU** poate fi o cauză?

| Opțiune | Cauză potențială |
|---------|------------------|
| A | Pachetul a fost corupt în tranzit (bit flip) |
| B | Clientul a calculat CRC pe date diferite față de server |
| C | Serverul folosește little-endian, clientul big-endian |
| D | Conexiunea TCP a pierdut pachete pe drum |

**Proces:**
1. Votează individual
2. Discută 2 minute
3. Revotează

<details>
<summary><strong>Răspuns și explicație (click după revot)</strong></summary>

**Răspuns corect: D) Conexiunea TCP a pierdut pachete pe drum**

TCP **garantează** livrarea și ordinea. Dacă un segment se pierde, TCP îl retransmite automat. Aplicația ta nu vede niciodată pachete pierdute – fie primești datele complete, fie conexiunea se rupe.

**Cauzele reale de CRC mismatch:**
- **A** - Corupție în memorie sau pe magistrală (rar)
- **B** - Bug clasic: calculezi CRC pe `header + payload` la sender dar doar pe `payload` la receiver
- **C** - Endianness diferit: `struct.pack("I", ...)` vs `struct.pack("!I", ...)`

**Greșeala tipică:** Mulți confundă fiabilitatea TCP (garantează livrare) cu integritatea (CRC detectează corupție). Sunt lucruri diferite.

</details>

---

## Ghid pas cu pas: Protocol UDP pentru Senzori

**⏱️ Timing recomandat:**

| Pas | Durată | Ce facem |
|-----|--------|----------|
| Teorie | 3 min | Diferențe TCP vs UDP |
| PI | 4 min | De ce UDP pentru senzori? |
| Pas 1 | 3 min | Structura datagramului |
| Pas 2 | 4 min | Împachetare |
| Pas 3 | 4 min | Despachetare și validare |
| Demo | 4 min | Test cu corupție |
| **Total** | ~22 min | |

### Diferențe față de TCP:
- Nu există conexiune (connectionless)
- Fiecare `sendto()` = un datagram
- Datagramele pot ajunge în altă ordine sau deloc
- Dar: granițele mesajelor sunt păstrate!

---

### 🗳️ Peer Instruction: UDP vs TCP pentru Senzori

**⏱️ Timp:** 4 minute

**Întrebare rapidă:**

De ce folosim UDP (nu TCP) pentru senzori IoT care trimit temperatură la fiecare secundă?

| Opțiune | Motiv |
|---------|-------|
| A | UDP e mai sigur decât TCP |
| B | UDP are overhead mai mic și o citire pierdută nu e critică |
| C | TCP nu funcționează pe rețele wireless |
| D | UDP e mai rapid pentru că comprimă datele |

<details>
<summary><strong>Răspuns</strong></summary>

**Răspuns corect: B)**

Pentru senzori cu citiri frecvente:
- Pierzi o citire? Nu-i bai, următoarea vine în 1 secundă
- Overhead TCP (handshake, ACK-uri) e nejustificat pentru 23 bytes
- Latența redusă contează mai mult decât garanția livrării

TCP NU e "nesigur" (A e fals), funcționează pe wireless (C e fals), și UDP nu comprimă nimic (D e fals).

</details>

---

### Pasul 1: Structura datagramului

```python
# Datagram: version(1) + sensor_id(4) + temp(4) + location(10) + crc(4)
# Total: 23 bytes
UDP_FORMAT = "!BIf10sI"
UDP_SIZE = struct.calcsize(UDP_FORMAT)  # = 23
```

### Pasul 2: Împachetarea

```python
def pack_sensor_reading(sensor_id: int, temp: float, location: str) -> bytes:
    """
    Împachetează o citire de senzor în format binar.
    """
    VERSION = 1
    
    # === PADDING_LOCATION ===
    # Padding locație la exact 10 bytes
    loc_bytes = location.encode("utf-8")[:10].ljust(10, b"\x00")
    
    # === DATAGRAM_FARA_CRC ===
    data_no_crc = struct.pack("!BIf10s", VERSION, sensor_id, temp, loc_bytes)
    
    # === ADAUGARE_CRC ===
    crc = crc32(data_no_crc)
    
    return struct.pack(UDP_FORMAT, VERSION, sensor_id, temp, loc_bytes, crc)
```

### Pasul 3: Despachetarea și validarea

```python
def unpack_sensor_reading(data: bytes) -> tuple:
    """
    Despachetează și validează o citire de senzor.
    """
    # === VALIDARE_DIMENSIUNE ===
    if len(data) != UDP_SIZE:
        raise ValueError(f"Invalid size: {len(data)}")
    
    # === EXTRAGERE_CAMPURI ===
    ver, sensor_id, temp, loc_bytes, received_crc = struct.unpack(UDP_FORMAT, data)
    
    # === VERIFICARE_CRC ===
    data_no_crc = struct.pack("!BIf10s", ver, sensor_id, temp, loc_bytes)
    if crc32(data_no_crc) != received_crc:
        raise ValueError("CRC mismatch")
    
    # === DECODARE_LOCATION ===
    location = loc_bytes.decode("utf-8").rstrip("\x00")
    return ver, sensor_id, temp, location
```

---

## Rezultate așteptate

**🔮 Predicție înainte de rulare:**
> Pentru fiecare test, scrie ce crezi că va afișa. Apoi rulează și compară.

### Test Protocol TEXT

```bash
$ python3 text_proto_client.py -c "PING" -c "SET name Alice" -c "GET name" -c "COUNT"
```

**Predicția ta:** _______________

<details>
<summary>Output real</summary>

```
OK pong
OK stored name
OK name Alice
OK 1 keys
```

</details>

### Test Protocol BINAR

```bash
$ python3 binary_proto_client.py -c "echo test" -c "put name Bob" -c "get name"
```

**Predicția ta:** _______________

<details>
<summary>Output real</summary>

```
ECHO: test
OK
Bob
```

</details>

### Test UDP Senzori

```bash
$ python3 udp_sensor_client.py --sensor-id 1 --temp 23.5 --location "Lab1"
$ python3 udp_sensor_client.py --sensor-id 99 --temp 0.0 --location "Test" --corrupt
```

**Predicție pentru pachetul corupt:** _______________

<details>
<summary>Output real</summary>

```
[UDP] > localhost:5402 [Sensor 0001] Lab1: +23.5°C
[UDP] > localhost:5402 [Sensor 0099] Test: +0.0°C (CORRUPTED)
# Server va loga: CRC mismatch
```

</details>

---

## Greșeli frecvente și cum le depistezi

### 1. Nu citești toți bytes (TCP)
**Simptom:** mesaje tăiate, erori de parsing
**Cauză:** `recv(n)` poate returna mai puțin de n bytes
**Soluție:** buclă până primești tot

### 2. Encoding mismatch
**Simptom:** UnicodeDecodeError
**Cauză:** trimiți bytes, aștepți string sau invers
**Soluție:** `.encode()` la trimitere, `.decode()` la primire

### 3. Endianness greșit
**Simptom:** numere ciudate (ex: 1 devine 16777216)
**Cauză:** big-endian vs little-endian
**Soluție:** folosește `!` în struct (network byte order)

### 4. CRC calculat greșit
**Simptom:** toate pachetele par corupte
**Cauză:** CRC calculat pe date diferite la sender vs receiver
**Soluție:** verifică să calculezi CRC pe exact aceiași bytes

### Debugging cu tshark

```bash
# Captură trafic TCP
sudo tshark -i lo -f "port 5400" -O tcp -V

# Hex dump
sudo tcpdump -i lo port 5400 -XX

# Analiză payload
tshark -r capture.pcap -T fields -e data
```

O chestie pe care am învățat-o pe pielea mea: când tshark nu afișează nimic, de cele mai multe ori problema e la filtru, nu la trafic. Începe fără filtru și adaugă condiții incremental.

---

### 🗳️ Peer Instruction: Alegere Protocol (EVALUATE)

**⏱️ Timp:** 5 minute

**Scenariu:**

Proiectezi un sistem de monitorizare pentru o fabrică. Ai două tipuri de date:
- **Alertă critică**: Supraîncălzire motor (trebuie să ajungă SIGUR)
- **Telemetrie**: Temperatură la fiecare 100ms (volum mare, pierderi acceptabile)

**Care e cea mai bună combinație de protocoale?**

| Opțiune | Alertă | Telemetrie |
|---------|--------|------------|
| A | TCP | TCP |
| B | UDP | UDP |
| C | TCP | UDP |
| D | UDP | TCP |

**Proces:**
1. Votează individual (30 sec)
2. Discută cu colegul (2 min) – argumentează alegerea
3. Revotează
4. Discuție în clasă

<details>
<summary><strong>Răspuns și explicație</strong></summary>

**Răspuns corect: C) TCP pentru alertă, UDP pentru telemetrie**

**Raționament:**
- **Alerta critică** trebuie să ajungă garantat → TCP (retransmisie automată)
- **Telemetria** e de volum mare și tolerantă la pierderi → UDP (overhead mic)

**De ce NU celelalte:**
- **A (TCP+TCP):** Funcționează, dar telemetria la 100ms cu TCP generează overhead excesiv
- **B (UDP+UDP):** Risc să pierzi alertele critice – inacceptabil
- **D (UDP+TCP):** Invers – pierdere alertă e gravă, overhead telemetrie e nejustificat

**Principiu:** Alege protocolul în funcție de cerințele fiecărui flux de date, nu "unul pentru tot".

</details>

---

## Consolidare: Exerciții gradate

### Nivel 1 (Înțelegere)
1. Ce se întâmplă dacă trimiți "Hello" fără framing și faci recv(3)?
2. De ce LENGTH-ul e în bytes, nu în caractere?

### Nivel 2 (Aplicare)
3. Implementează comanda KEYS (lista toate cheile)
4. Adaugă un timestamp în datagramul UDP senzor

### Nivel 3 (Analiză)
5. Compară overhead-ul TEXT vs BINAR pentru un mesaj de 100 bytes
6. Ce se întâmplă dacă un pachet UDP ajunge fragmentat?

### Nivel Challenge
7. Implementează retransmisie pentru UDP (ACK + timeout)
8. Adaugă compresie (zlib) pentru payload-uri mari în protocolul binar

---

## Ce am învățat

1. TCP e un **stream** – framing-ul e treaba noastră
2. Length-prefix e simplu și solid pentru framing
3. Protocolul binar oferă eficiență și validare CRC
4. UDP păstrează granițele dar nu garantează livrarea
5. `struct` e de bază pentru serializare binară

## La ce ne ajută

- Înțelegem cum funcționează HTTP, SMTP, DNS la nivel de bytes
- Putem diagnostica probleme de comunicare
- Putem proiecta protocoale eficiente pentru aplicații specifice

## Contribuția la proiect

Pentru proiectul de echipă, săptămâna asta oferă:
- Implementarea de bază a comunicării client-server
- Structura pentru protocolul aplicației voastre
- Funcții de framing reutilizabile

---

## Activități complementare

Pentru consolidare fără a scrie cod, vezi **docs/exercises/activities.md**:
- Parsons Problems (reordonare cod)
- Code Tracing (execuție mentală)
- Debugging Exercises (găsește bug-uri)
- Code Reading (înțelegere fără scriere)

**Timp estimat:** 45-60 minute suplimentare.
