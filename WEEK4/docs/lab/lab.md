# Laborator 4: Protocoale Custom TEXT și BINARY peste TCP/UDP

## Ce exersăm

Laboratorul 4 pune în practică ce-am discutat despre nivelul fizic și legătura de date. Concret: proiectăm și implementăm un protocol text cu delimitare prin lungime, construim un protocol binar cu header fix și CRC32, și facem un sistem de colectare date de la senzori prin UDP.

**⏱️ Durată totală:** 2-3 ore (depinde de ritm)

## De ce merită efortul

Protocolul aplicației e contractul dintre componente. Ca programator, trebuie să înțelegi nu doar abstractizările oferite de framework-uri, ci și fundamentele: cum fluxul TCP necesită framing, cum UDP oferă datagrame fără garanții, și cum structurile binare reduc traficul față de text. Diferența între cineva care debugează probleme de rețea și cineva care doar copiază soluții de pe Stack Overflow stă fix în înțelegerea asta.

## Prerechizite

Din Laboratoarele 1-3:
- Socket-uri TCP și UDP (connect, bind, listen, accept)
- Analiza traficului cu Wireshark/tshark
- Python: module socket, struct

## Structura laboratorului

### Pasul 0: Pregătirea mediului

**⏱️ Timp:** 5 minute

```bash
# Clonare/descărcare starterkit
cd ~/starterkit_s4

# Verificare dependențe
./scripts/setup.sh

# Validare mediu
make verify
```

**Rezultat așteptat**: Toate verificările trec (Python 3.x disponibil, module importabile).

### Pasul 1: Protocol TEXT peste TCP

**⏱️ Timp:** 20 minute

#### 1.1 Pornire server

```bash
# Terminal 1: Server
python3 python/apps/text_proto_server.py --host 0.0.0.0 --port 5400
```

**Output așteptat**:
```
[INFO] Server TEXT pornit pe 0.0.0.0:5400
[INFO] Aștept conexiuni...
```

#### 1.2 Test client interactiv

```bash
# Terminal 2: Client
python3 python/apps/text_proto_client.py --host localhost --port 5400
```

**🔮 Predicție:** Înainte să rulezi fiecare comandă, scrie ce crezi că returnează serverul.

**Comenzi de testat**:
```
> PING
< PONG

> SET user Alice
< OK

> GET user
< Alice

> COUNT
< 1

> KEYS
< user

> DEL user
< DELETED
```

#### 1.3 Captură și analiză

```bash
# Terminal 3: Captură pachete
sudo tcpdump -i lo -w captures/text_proto.pcap port 5400

# După test, analizează:
tshark -r captures/text_proto.pcap -V | less
```

**Ce observăm**: Formatul `<LEN> <PAYLOAD>` în datele TCP. Exemplu: `"4 PING"` – lungimea 4, comanda PING.

### Pasul 2: Protocol BINARY peste TCP

**⏱️ Timp:** 25 minute

#### 2.1 Pornire server binar

```bash
# Terminal 1: Server binar
python3 python/apps/binary_proto_server.py --host 0.0.0.0 --port 5401
```

#### 2.2 Client binar

```bash
# Terminal 2: Client
python3 python/apps/binary_proto_client.py --host localhost --port 5401
```

**Teste**:
```python
# Mod interactiv sau comenzi:
python3 python/apps/binary_proto_client.py -c "echo:TestMessage" -c "put:key1:value1" -c "get:key1"
```

#### 2.3 Analiză header binar

**Structura header (14 octeți)**:
| Offset | Lungime | Câmp | Descriere |
|--------|---------|------|-----------|
| 0 | 2 | magic | `0x4E50` ("NP") |
| 2 | 1 | version | 1 |
| 3 | 1 | type | Tip mesaj (1-255) |
| 4 | 2 | payload_len | Lungime payload |
| 6 | 4 | seq | Număr secvență |
| 10 | 4 | crc32 | Sumă control |

**Vizualizare cu tshark**:
```bash
tshark -r captures/binary_proto.pcap -x | head -50
```

### Pasul 3: Protocol UDP pentru senzori

**⏱️ Timp:** 20 minute

#### 3.1 Pornire server colector

```bash
python3 python/apps/udp_sensor_server.py --host 0.0.0.0 --port 5402
```

#### 3.2 Simulare senzori

```bash
# Un singur pachet
python3 python/apps/udp_sensor_client.py --host localhost --port 5402 \
    --sensor-id 1 --temperature 23.5 --location "Lab1"

# Mod continuu (1 pachet/secundă)
python3 python/apps/udp_sensor_client.py --host localhost --port 5402 \
    --sensor-id 2 --mode continuous --interval 1.0

# Rafală de 10 pachete
python3 python/apps/udp_sensor_client.py --host localhost --port 5402 \
    --sensor-id 3 --mode burst --count 10
```

#### 3.3 Testare corupție

```bash
# Trimite pachet cu CRC invalid
python3 python/apps/udp_sensor_client.py --host localhost --port 5402 \
    --sensor-id 99 --corrupt
```

**Ce observăm**: Serverul detectează și raportează pachetul corupt.

### Pasul 4: Mininet – topologie și test

**⏱️ Timp:** 15 minute

#### 4.1 Pornire topologie

```bash
sudo python3 mininet/topologies/topo_4_base.py
```

#### 4.2 Test inter-host

```bash
# În CLI Mininet:
mininet> h1 python3 /path/to/text_proto_server.py &
mininet> h2 python3 /path/to/text_proto_client.py --host 10.0.0.1
```

### Pasul 5: Exerciții practice

**⏱️ Timp:** 40-60 minute (inclusiv Pair Programming)

#### Exercițiu 4.1: Implementare comandă LIST (Basic)

Modifică `python/templates/text_server_template.py` pentru a implementa comanda `LIST` care returnează toate perechile cheie-valoare.

**Input**: `LIST`
**Output așteptat**: `key1=value1;key2=value2;...`

#### Exercițiu 4.2: Timeout client UDP (Intermediar)

Implementează un timeout de 2 secunde în clientul UDP. Dacă nu primește confirmare, retrimite de maximum 3 ori.

#### Exercițiu 4.3: Statistici server (Avansat)

Adaugă la serverul binar o comandă `STATS` care returnează:
- Număr total de cereri procesate
- Număr cereri pe tip (ECHO, PUT, GET)
- Timp mediu de procesare

#### Exercițiu 4.4: Protocol hibrid (Challenge)

Proiectează un protocol care combină:
- Handshake text (pentru debugging ușor)
- Payload binar (pentru eficiență)
- Negociere versiune

#### Exercițiu 4.5: Evaluare și Justificare Design (EVALUATE)

**Scenariu:** Ești consultat pentru o aplicație de gaming online. Echipa de dev a propus două variante de protocol:

**Varianta A: Full TCP**
- Toate mesajele (input jucător, stare joc, chat) pe o singură conexiune TCP
- Simplu de implementat
- 100% fiabilitate

**Varianta B: Hibrid**  
- Input jucător: UDP (latență minimă)
- Stare joc critică: TCP (sincronizare garantată)
- Chat: TCP (fiabilitate, poate fi întârziat)

**Task:**
1. Evaluează cele două variante
2. Scrie un mini-raport (10-15 rânduri) în care:
   - Identifici avantajele și dezavantajele fiecărei variante
   - Recomanzi una dintre ele cu justificare
   - Menționezi ce compromisuri acceptă soluția ta

**Criterii evaluare:**
- Argumentele sunt tehnic corecte (nu opinii fără suport)
- Ia în considerare latența, fiabilitatea, complexitatea
- Recomandarea e coerentă cu analiza

---

### Pasul 6: Lucru în perechi (Pair Programming)

**⏱️ Timp:** Inclus în exercițiile de mai sus

Pentru exercițiile 4.1-4.3, lucrați în perechi. Tehnica asta e folosită în industrie și chiar funcționează – îmbunătățește calitatea codului și accelerează învățarea.

#### Rolurile

| Rol | Ce faci |
|-----|---------|
| **Driver** | Scrii codul, ai tastatura și mouse-ul |
| **Navigator** | Revizuiești codul live, gândești strategia, cauți documentație, observi erori |

#### Reguli de aur

1. **Schimbați rolurile la 10-15 minute** – pune un timer
2. **Navigator-ul NU dictează cod** caracter cu caracter – sugerează direcția, nu implementarea exactă
3. **Discutați abordarea ÎNAINTE** – 2 minute de planificare economisesc 10 minute de refactoring
4. **Când Driver-ul se blochează**, Navigator-ul poate sugera, dar nu preia tastatura

#### Timing pentru Exercițiul 4.1

| Interval | Ce faceți |
|----------|-----------|
| 0-2 min | Citiți împreună cerința, clarificați ce trebuie făcut |
| 2-5 min | Discutați abordarea: unde adăugăm codul? ce format are output-ul? |
| 5-15 min | **Runda 1**: Persoana A = Driver, Persoana B = Navigator |
| 15-25 min | **Runda 2**: Inversare roluri |
| 25-30 min | Testare împreună, debugging dacă e nevoie |

#### De ce merge Pair Programming

- **Prinzi erori devreme** – două perechi de ochi văd mai mult
- **Înveți reciproc** – explicând codul, îl înțelegi mai bine
- **Cod mai curat** – gândirea în voce tare forțează claritate
- **Stai focusat** – greu să te pierzi pe telefon când cineva se uită

#### Anti-patterns de evitat

| Greșeală | Consecință | Soluție |
|----------|------------|---------|
| Navigator dictează caracter cu caracter | Driver-ul n-are ce învăța | Navigator sugerează concepte, nu cod |
| Nu schimbați rolurile | O persoană domină | Timer strict |
| Navigator pe telefon | Solo programming cu spectator | Telefoanele jos |
| Driver ignoră Navigator-ul | Se pierd sugestii bune | Pauză, discuție, reset |

Sfat din sesiunile de laborator anterioare: echipele care pun timer-ul pentru schimbarea rolurilor chiar funcționează mai bine. Altfel, invariabil unul domină și celălalt devine spectator.

---

## Strategia de debugging în 5 pași

Când ceva nu merge, urmează ordinea asta. Sistematic, nu la întâmplare.

### Pasul 1: Verifică bazele (30 secunde)

**Checklist rapid:**
- [ ] Serverul rulează? `pgrep -a python`
- [ ] Portul e corect? `ss -tlnp | grep 5400`
- [ ] Ești în directorul corect? `pwd`
- [ ] Fișierul există? `ls -la python/apps/`

```bash
# Comandă rapidă all-in-one
pgrep -a python | grep proto && ss -tlnp | grep -E "540[0-2]"
```

### Pasul 2: Simplifică problema (1 minut)

**Elimină variabilele:**
- Merge cu `netcat`? 
  ```bash
  echo "4 PING" | nc localhost 5400
  ```
- Merge cu localhost explicit?
  ```bash
  python3 client.py --host 127.0.0.1  # în loc de localhost
  ```
- Merge cu date minimale?
  ```bash
  # Cel mai simplu mesaj posibil
  python3 -c "import socket; s=socket.socket(); s.connect(('127.0.0.1',5400)); s.send(b'4 PING'); print(s.recv(100))"
  ```

### Pasul 3: Print debugging (2 minute)

**Adaugă print-uri strategice:**

```python
# La intrarea în funcții
def recv_framed(conn):
    print(f"DEBUG recv_framed: starting")
    
    # După fiecare operație critică
    chunk = conn.recv(1)
    print(f"DEBUG: received {len(chunk)} bytes: {chunk!r}")
    
    # La ieșire
    print(f"DEBUG recv_framed: returning {result!r}")
    return result
```

**Regula:** Print-urile trebuie să arate CE funcție rulează, CE date a primit, CE returnează.

### Pasul 4: Verifică tipurile (1 minut)

**Cele mai comune erori:**

```python
# Verificare tip
print(f"DEBUG: type={type(data)}, value={data!r}")

# Erori tipice:
# - Aștepți str, primești bytes → .decode()
# - Aștepți bytes, primești str → .encode()
# - Aștepți int, primești str → int()
```

**Pattern de verificare:**
```python
assert isinstance(data, bytes), f"Expected bytes, got {type(data)}"
```

### Pasul 5: Captură trafic (5 minute)

**Când print-urile nu ajută:**

```bash
# Terminal dedicat pentru captură
sudo tcpdump -i lo -X port 5400

# Sau cu tshark pentru detalii
sudo tshark -i lo -f "port 5400" -O tcp -V
```

**Ce cauți:**
- Datele ajung la server? (vezi pachete incoming)
- Serverul răspunde? (vezi pachete outgoing)
- Formatul e corect? (verifică hex dump)

### Flowchart debugging

```
Start
  │
  ▼
┌─────────────────┐
│ Serverul rulează?│──No──► Pornește serverul
└────────┬────────┘
         │Yes
         ▼
┌─────────────────┐
│ Portul e liber? │──No──► kill -9 <PID> sau alt port
└────────┬────────┘
         │Yes
         ▼
┌─────────────────┐
│ netcat merge?   │──No──► Problemă server, vezi loguri
└────────┬────────┘
         │Yes
         ▼
┌─────────────────┐
│ Client-ul trimite?│──No──► Adaugă print() la send()
└────────┬────────┘
         │Yes
         ▼
┌─────────────────┐
│ Tipuri corecte? │──No──► .encode()/.decode()
└────────┬────────┘
         │Yes
         ▼
┌─────────────────┐
│ Captură trafic  │──────► Analizează hex dump
└─────────────────┘
```

---

## Greșeli frecvente și debugging

### Problemă: "Connection refused"

**Cauză**: Serverul nu rulează sau portul e ocupat.

**Diagnostic**:
```bash
lsof -i :5400
# sau
ss -tlnp | grep 5400
```

### Problemă: Date incomplete

**Cauză**: `recv()` nu citește tot payload-ul.

**Soluție**: Folosește bucle de citire sau `recv_exact()` din `io_utils.py`.

### Problemă: CRC mismatch

**Cauză**: Ordine bytes incorectă sau date modificate.

**Diagnostic**:
```python
import zlib
calculated = zlib.crc32(header_without_crc + payload) & 0xFFFFFFFF
print(f"Expected: {expected_crc:08x}, Calculated: {calculated:08x}")
```

### Problemă: UDP pachete pierdute

**E normal.** UDP nu garantează livrarea.

**Test**:
```bash
# Simulează pierderi cu tc (traffic control)
sudo tc qdisc add dev lo root netem loss 10%
# Rulează testele, apoi curăță:
sudo tc qdisc del dev lo root
```

---

## Ce am învățat

După lab, ar trebui să poți:
1. Implementa protocoale text cu delimitare prin lungime
2. Construi protocoale binare cu header fix și validare CRC
3. Folosi UDP pentru colectare date
4. Diagnostica probleme de comunicare cu tshark/tcpdump
5. Proiecta soluții pentru erori (timeout, retransmisie)
6. Lucra în perechi cu Pair Programming
7. Aplica debugging sistematic

## La ce ajută

- Dezvoltare backend (microservicii, IoT gateways)
- Debugging producție (analiză capturi, diagnosticare latență)
- Integrări sisteme (protocoale proprietare, reverse engineering)
- Optimizare performanță (alegere text vs binar)
- Colaborare în echipe

## Contribuția la proiect

**Artefact livrabil**: Implementare protocol custom pentru comunicarea dintre componentele proiectului – protocol mesagerie internă, sincronizare date, sau comandă-control pentru dispozitive IoT.

**Recomandare**: Folosiți Pair Programming când proiectați protocolul echipei. Deciziile de design luate împreună sunt mai solide.

## Activități complementare

Pentru consolidare prin alte metode decât scrierea de cod, vezi **docs/exercises/activities.md**:
- Parsons Problems – reordonare cod (fără a scrie)
- Code Tracing – execuție mentală pas cu pas
- Debugging Exercises – găsește bug-uri în cod
- Code Reading – înțelegere și explicare cod

## Resurse suplimentare

- RFC 793 (TCP) – https://www.rfc-editor.org/rfc/rfc793
- RFC 768 (UDP) – https://www.rfc-editor.org/rfc/rfc768
- Python struct – https://docs.python.org/3/library/struct.html
- Wireshark User's Guide – https://www.wireshark.org/docs/wsug_html/
- Pair Programming Guide – https://martinfowler.com/articles/on-pair-programming.html
