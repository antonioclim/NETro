# Laborator 2: Ghid Pas-cu-Pas

**Exerciții practice pentru Săptămâna 2**

---

## Step 0: Pregătirea mediului

### 0.1 Verificare sistem

```bash
# Navighează în directorul kit-ului
cd starterkit_s2

# Verificare automată
make verify
```

**Output așteptat**:
```
[VERIFY] Verificare mediu de lucru...
  Python3:    Python 3.10.12
  Mininet:    2.3.0
  tshark:     TShark (Wireshark) 3.6.2
  tcpdump:    tcpdump version 4.99.1
  
  ✓ ex_2_01_tcp.py
  ✓ ex_2_02_udp.py
  ✓ topo_2_base.py
[VERIFY] ✓ Complet
```

### 0.2 Dacă lipsesc dependințe

```bash
make setup
```

### 0.3 Curățare sesiuni anterioare

*Personal, rulez `sudo mn -c` de fiecare dată când intru în laborator, chiar dacă nu cred că am sesiuni vechi. M-am ars de prea multe ori cu "de ce nu merge?!" când răspunsul era o sesiune Mininet zombie din ziua anterioară.*

```bash
sudo mn -c
make clean
```

---

## Concepte cheie — Analogii concrete

Înainte de a scrie cod, înțelege conceptele prin analogii:

### Socket = Telefonul tău mobil

| Concept | Analogie |
|---------|----------|
| Socket | Telefonul (dispozitivul de comunicare) |
| IP Address | Numărul tău de telefon |
| Port | Extensia internă (identifică aplicația) |
| `bind()` | Activezi cartela SIM pe un număr |
| `listen()` | Ții telefonul deschis, aștepți să sune |
| `connect()` | Formezi un număr și aștepți răspuns |
| `accept()` | Ridici receptorul când sună |
| `send()/recv()` | Vorbești și asculți |

**⚠️ Capcană frecventă:**
> Mulți confundă `bind()` cu `listen()`. Gândește-te așa: `bind()` îți dă numărul de telefon, dar telefonul e închis. `listen()` îl deschide și începe să sune când cineva te caută.

### TCP Handshake = Conversație telefonică

```
Client:  „Bună, mă auzi?"        → SYN
Server:  „Da, te aud! Tu mă auzi?" → SYN-ACK  
Client:  „Da, perfect! Hai să vorbim." → ACK
```

### Încapsulare = Plicuri în plicuri

Când trimiți un mesaj prin rețea:
1. Scrii mesajul pe hârtie → **Date aplicație**
2. Pui hârtia în plic cu nr. apartament → **+ Header TCP (port)**
3. Pui plicul în plic mai mare cu adresa clădirii → **+ Header IP**
4. Pui totul în plic de curierat cu adresa fizică → **+ Header Ethernet (MAC)**
5. Curierul transportă fizic → **Biți pe fir**

---

## Step 1: Demo TCP rapid

### 1.1 Pornire server (Terminal 1)

```bash
make tcp-server
```

**Output așteptat**:
```
[TCP-SERVER] Pornire pe 0.0.0.0:9999...
[14:30:00.123][SERVER] TCP pe 0.0.0.0:9999 | mod=threaded
[14:30:00.124][SERVER] Așteptare conexiuni... (Ctrl+C oprire)
```

### 1.2 Trimitere mesaj (Terminal 2)

```bash
make tcp-client MSG="Salut Server"
```

**Output așteptat**:
```
[TCP-CLIENT] Trimitere către 127.0.0.1:9999...
[14:30:05.456][CLIENT] RX 16B în 1.2ms: b'OK: SALUT SERVER'
```

### 1.3 Observare log server

În Terminal 1, apare:
```
[14:30:05.455][MAIN] Conexiune nouă: 127.0.0.1:54321
[14:30:05.456][Worker-54321] RX   12B de la 127.0.0.1:54321: b'Salut Server'
[14:30:05.456][Worker-54321] TX   16B către 127.0.0.1:54321: b'OK: SALUT SERVER'
```

### 1.4 Oprire server

În Terminal 1: `Ctrl+C`

---

## Step 2: Demo UDP rapid

### 2.1 Pornire server UDP (Terminal 1)

```bash
make udp-server
```

### 2.2 Client interactiv (Terminal 2)

```bash
make udp-client
```

**Sesiune interactivă**:
```
[UDP-CLIENT] Client interactiv către 127.0.0.1:9998...
> ping
PONG (RTT: 0.5ms)

> upper:hello world
HELLO WORLD (RTT: 0.6ms)

> exit
--- Stats: sent=2, received=2, timeouts=0 ---
```

*Netcat (`nc`) e tool-ul meu preferat pentru teste rapide — e ca un "cuțit elvețian" pentru rețelistică. Dacă ceva nu funcționează cu netcat, problema e aproape sigur în codul tău, nu în tool.*

---

## Step 3: Demo complet cu captură

### 3.1 Rulare demo complet

```bash
make demo-all
```

Acest target:
1. Pornește server TCP
2. Pornește captură tcpdump pentru TCP
3. Trimite mesaje TCP
4. Oprește captură și server TCP
5. Repetă pentru UDP

### 3.2 Analiză captură TCP

```bash
make analyze-tcp
```

**Output așteptat**:
```
[ANALYZE] Analiză captură TCP...

  Frame | IP Sursă     | Port | IP Dest      | Port | Flags
  ------|--------------|------|--------------|------|------
  1     127.0.0.1     45678  127.0.0.1     9999  ··········S·
  2     127.0.0.1     9999   127.0.0.1     45678 ·······A··S·
  3     127.0.0.1     45678  127.0.0.1     9999  ·······A····
  ...

[ANALYZE] Handshake-ul TCP (SYN, SYN-ACK, ACK) identificabil în primele 3 pachete
```

*Eu prefer `tshark` în loc de Wireshark GUI pentru analiză rapidă — output-ul text e mai ușor de copiat în rapoarte. Dar pentru explorare inițială, când nu știi exact ce cauți, GUI-ul e mai intuitiv.*

### 3.3 Analiză captură UDP

```bash
make analyze-udp
```

**Observație**: UDP nu are handshake - doar request și response direct. Ăsta e momentul când diferența devine vizibilă: TCP are ~9 pachete pentru un mesaj, UDP are doar 2.

---

## Step 4: Laborator Mininet

### 4.1 Pornire topologie

```bash
make mininet-cli
```

**⚠️ Dacă primești erori:**
> Cel mai probabil ai o sesiune Mininet veche. Rulează `sudo mn -c` și încearcă din nou.

### 4.2 Explorare

```
mininet> nodes
mininet> net
mininet> pingall
```

### 4.3 Server TCP în Mininet

```
mininet> h1 python3 -u seminar/python/exercises/ex_2_01_tcp.py server --bind 10.0.0.1 --port 9999 &
mininet> h2 python3 seminar/python/exercises/ex_2_01_tcp.py client --host 10.0.0.1 --port 9999 -m "Test Mininet"
```

**⚠️ Capcană frecventă:**
> Dacă primești `Connection refused`, verifică cu `jobs` că serverul chiar rulează. 80% din problemele "nu merge" sunt de fapt "am uitat să pornesc serverul".

### 4.4 Captură în Mininet

```
mininet> h1 tcpdump -i h1-eth0 -w /tmp/mininet_tcp.pcap 'tcp port 9999' &
mininet> h2 python3 seminar/python/exercises/ex_2_01_tcp.py client --host 10.0.0.1 --port 9999 -m "Cu captură"
mininet> kill %2
```

Analiză după ieșire din Mininet:
```bash
tshark -r /tmp/mininet_tcp.pcap -Y tcp
```

**⚠️ Dacă captura e goală:**
> Verifică interfața! În Mininet, hosturile au interfețe proprii (`h1-eth0`, `h2-eth0`), nu `eth0` sau `lo`.

### 4.5 Ieșire și curățare

```
mininet> exit
```
```bash
sudo mn -c
```

---

## Step 5: Topologie extinsă (router)

### 5.1 Pornire

```bash
make mininet-extended
```

### 5.2 Verificare comunicare între subrețele

```
mininet> h1 ping -c 2 10.0.2.3
mininet> h1 traceroute -n 10.0.2.3
```

**Observație importantă**: Uită-te la TTL — scade cu 1 la fiecare hop prin router. Asta e dovada că pachetul a trecut prin L3.

### 5.3 Server între subrețele

```
mininet> h1 python3 -u seminar/python/exercises/ex_2_01_tcp.py server --bind 10.0.1.1 --port 9999 &
mininet> h3 python3 seminar/python/exercises/ex_2_01_tcp.py client --host 10.0.1.1 --port 9999 -m "Cross-subnet"
```

---

## Step 6: Exerciții de înțelegere (NU doar cod!)

*Din experiența mea, exercițiile astea par "ușoare" dar dezvăluie goluri de înțelegere pe care scrierea de cod le maschează. Mulți studenți pot copy-paste un server funcțional, dar nu pot ordona corect pașii când îi văd amestecați.*

### 6.1 Parsons Problem — Ordonează codul

Liniile de mai jos sunt amestecate. Pune-le în ordinea corectă pentru un server TCP:

```python
conn.close()
sock.listen(5)
data = conn.recv(1024)
conn, addr = sock.accept()
sock.bind(('0.0.0.0', 9999))
conn.sendall(b"OK: " + data.upper())
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
```

**⚠️ Capcană frecventă:**
> Mulți pun `listen()` după `accept()`. Gândește-te: poți ridica telefonul (accept) dacă nu l-ai pus pe "mod recepție" (listen)?

**Ordinea corectă** (verifică după ce încerci):
1. `sock = socket.socket(...)` — CREATE
2. `sock.bind(...)` — BIND
3. `sock.listen(5)` — LISTEN
4. `conn, addr = sock.accept()` — ACCEPT
5. `data = conn.recv(1024)` — RECEIVE
6. `conn.sendall(...)` — SEND
7. `conn.close()` — CLOSE

**Reține pattern-ul:** CREATE → BIND → LISTEN → ACCEPT → RECEIVE → SEND → CLOSE

### 6.2 Trace Exercise — Ce afișează?

```python
import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.sendto(b"ping", ("10.0.0.1", 9998))
data, addr = sock.recvfrom(1024)
print(f"Răspuns de la {addr[0]}:{addr[1]} = {data.decode()}")
```

**Întrebări:**
1. Ce tip de socket e? → **UDP** (SOCK_DGRAM)
2. Apelează connect()? → **Nu** (UDP folosește sendto/recvfrom)
3. Ce se afișează dacă serverul răspunde `b"PONG"`? → `Răspuns de la 10.0.0.1:9998 = PONG`

**⚠️ Capcană frecventă:**
> Studenții care au văzut doar TCP se așteaptă să vadă `connect()`. La UDP, nu există conexiune — `sendto()` și `recvfrom()` fac totul într-un singur apel.

### 6.3 Debugging — Găsește bug-ul

```python
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(('0.0.0.0', 9999))
# BUG: lipsește sock.listen(5)
conn, addr = sock.accept()  # VA EȘUA AICI
```

**Bug**: Lipsește `sock.listen()` înainte de `accept()`. Socket-ul nu e marcat ca pasiv.

*Greșeala mea preferată de demonstrat live: șterg `listen()` și întreb "De ce nu merge?" Mesajul de eroare e criptic (`Invalid argument`), dar cauza e simplă odată ce înțelegi fluxul bind → listen → accept.*

**⚠️ Hint pentru debugging:**
> Când vezi `Invalid argument` sau `OSError` la `accept()`, prima întrebare: "Am apelat `listen()`?"

---

## Step 7: Template-uri de completat

### 7.1 Template TCP Server

Deschide `seminar/python/templates/tcp_server_template.py` și completează:

```python
# TODO 1: Afișează IP:Port client
print(f"Conectat: {addr[0]}:{addr[1]}")

# TODO 2: Primește date
data = conn.recv(1024)

# TODO 3: Construiește răspuns
response = b"OK: " + data.upper()

# TODO 4: Trimite răspuns
conn.sendall(response)
```

**Test**:
```bash
python3 seminar/python/templates/tcp_server_template.py &
echo "test" | nc 127.0.0.1 12345
# Așteptat: OK: TEST
```

**⚠️ Dacă nu primești răspuns:**
> Verifică că ai folosit `sendall()` nu `send()`. La mesaje mici nu contează, dar e un obicei bun.

### 7.2 Template UDP Server

Deschide `seminar/python/templates/udp_server_template.py` și completează protocolul:

```python
# TODO: Implementează protocolul
msg = data.decode('utf-8').strip()
if msg == "ping":
    response = b"PONG"
elif msg.startswith("upper:"):
    response = msg[6:].upper().encode()
else:
    response = b"UNKNOWN COMMAND"
```

**⚠️ Capcană frecventă:**
> Nu uita `.strip()` — netcat adaugă newline la final și `"ping\n" != "ping"`.

---

## Step 8: Verificare finală

### 8.1 Checklist

- [ ] `make verify` trece fără erori
- [ ] `make demo-all` rulează complet
- [ ] `make analyze-tcp` arată handshake (SYN, SYN/ACK, ACK)
- [ ] `make analyze-udp` arată request/response direct
- [ ] Mininet `pingall` = 0% dropped
- [ ] Parsons Problem rezolvat corect
- [ ] Trace Exercise răspunsuri corecte
- [ ] Debugging Exercise bug identificat
- [ ] Template TCP funcțional
- [ ] Template UDP funcțional

### 8.2 Curățare finală

```bash
make reset
```

---

## Rezultate așteptate

### Captură TCP (handshake)

```
1. Client → Server: SYN           (Inițiere conexiune)
2. Server → Client: SYN-ACK       (Accept + confirmare)
3. Client → Server: ACK           (Confirmare finală)
4. Client → Server: PSH-ACK       (Date aplicație)
5. Server → Client: ACK           (Confirmare date)
6. Server → Client: PSH-ACK       (Răspuns)
7. Client → Server: ACK           (Confirmare răspuns)
...
n. FIN, FIN-ACK, ACK              (Închidere conexiune)
```

### Captură UDP

```
1. Client → Server: Datagramă     (Request)
2. Server → Client: Datagramă     (Response)
```

**Diferență fundamentală**: TCP are overhead pentru fiabilitate, UDP e minimal dar fără garanții. Când vezi 9 pachete vs 2 pentru același mesaj, înțelegi de ce gaming-ul preferă UDP.

---

## What-If: Modificări și efecte

| Modificare | Efect |
|------------|-------|
| `--mode iterative` la server TCP | Un singur client la un moment dat |
| Port ocupat | `Address already in use` |
| Server oprit | `Connection refused` |
| Captură pe interfață greșită | PCAP gol |
| Timeout mic la client | Pierdere mesaje |
| Buffer recv mic | Trunchiere date |
| Uiți `listen()` | `accept()` eșuează cu eroare |

*Un truc pe care l-am învățat: dacă vezi `Address already in use`, cel mai rapid fix e să schimbi portul temporar. Dacă vrei să refolosești același port imediat, trebuie `SO_REUSEADDR` — dar asta e pentru altă discuție.*

---

*Revolvix&Hypotheticalandrei*
