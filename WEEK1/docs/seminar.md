# Seminar 1: Analiză de Rețea cu Wireshark, tshark și netcat

## Informații generale

| Disciplină | Rețele de Calculatoare |
|------------|------------------------|
| Săptămâna | 1 |
| Tip activitate | Seminar (exerciții practice asistate) |
| Durată | 2 ore (100 minute) |
| Locație | Laborator cu calculatoare și acces Internet |

---

## Ce vom învăța

La finalul acestui seminar, studenții vor fi capabili să:

1. **Utilizeze** comenzile de diagnostic de rețea: `ping`, `ip`, `ss`
2. **Creeze** servere și clienți TCP/UDP simpli cu `netcat`
3. **Captureze** trafic de rețea folosind `tshark` (Wireshark CLI)
4. **Analizeze** capturi de pachete și să identifice handshake-ul TCP
5. **Interpreteze** diferențele practice dintre TCP și UDP

---

## De ce contează pentru un programator

Abilitatea de a analiza traficul de rețea este utilă pentru:

- **Debugging**: înțelegerea de ce o conexiune eșuează sau e lentă
- **Securitate**: identificarea traficului suspect sau nencriptat
- **Optimizare**: măsurarea latenței și throughput-ului real
- **Dezvoltare**: testarea protocoalelor implementate

---

## Prerechizite

### Tehnice
- Acces la terminal Linux (VM, WSL, sau nativ)
- Starterkit S1 descărcat și dezarhivat
- Comenzi `make verify` executate cu succes

### Conceptuale
- Modelul client-server
- Diferența dintre TCP (connection-oriented) și UDP (connectionless)
- Conceptul de port și socket

**Analogie socket:** Un socket e ca un telefon cu număr de interior. Adresa IP e numărul principal al companiei, portul e extensia internă. Ca să suni pe cineva, ai nevoie de ambele.

---

## Structura seminarului

### Partea I: Explorare și diagnosticare (25 min)

#### 1.1 Interfețe de rețea

```bash
# Listare interfețe cu adrese IP
ip addr show

# Vizualizare simplificată
ip -4 -brief addr

# Tabela de rutare
ip route show
```

**De observat:**
- `lo` = loopback (127.0.0.1) - comunicație locală
- `eth0`/`enp0s3`/`ens33` = interfață fizică/virtuală
- Adresa IP și masca de rețea (ex: 192.168.1.100/24)

#### 1.2 Testare conectivitate cu ping

**🎯 PREDICȚIE înainte de execuție:**
> Cât credeți că va fi RTT-ul pentru ping către 127.0.0.1? Dar către 8.8.8.8? De ce diferența?

```bash
# Ping loopback (testare stivă TCP/IP locală)
ping -c 4 127.0.0.1

# Ping gateway (testare LAN)
ping -c 4 $(ip route | grep default | awk '{print $3}')

# Ping extern (testare Internet)
ping -c 4 8.8.8.8
```

**Interpretare rezultate:**
- RTT (Round-Trip Time): timp dus-întors în ms
- Packet loss: procentul de pachete pierdute
- TTL: Time To Live (hop-uri rămase)

#### 1.3 Porturi și conexiuni active

```bash
# Porturi TCP în ascultare
ss -tlnp

# Conexiuni TCP stabilite
ss -tnp

# Toate socket-urile (inclusiv UDP)
ss -anp
```

**Flag-uri ss:**
- `-t`: TCP
- `-u`: UDP
- `-l`: listen (doar servere)
- `-n`: numeric (fără rezoluție DNS)
- `-p`: process (afișează PID/nume)

---

### 🗳️ PEER INSTRUCTION #1: Bind Address

**Scenariu:** Un server Python face `bind(("0.0.0.0", 9999))`.

**Întrebare:** Ce înseamnă adresa `0.0.0.0`?

| Opțiune | Răspuns |
|---------|---------|
| **A** | Serverul nu ascultă pe niciun port |
| **B** | Serverul ascultă pe toate interfețele de rețea |
| **C** | Serverul ascultă doar pe interfața loopback |
| **D** | Eroare - adresa este invalidă |

<details>
<summary>🎯 Note instructor (click pentru a expanda)</summary>

**Răspuns corect:** B

**Analiza distractorilor:**
- **A:** Misconceptie că 0.0.0.0 = "nimic" sau "nowhere"
- **C:** Confuzie cu 127.0.0.1 (loopback specific)
- **D:** Lipsă cunoștințe despre wildcard address

**Target:** ~50% corect la primul vot

**După discuție:** Demonstrați cu `ss -tlnp` diferența între bind pe 0.0.0.0 vs 127.0.0.1

**Timing:** Prezentare 1 min → Vot 1 min → Discuție perechi 3 min → Revot 30 sec → Explicație 2 min
</details>

---

### Partea II: Server și client cu netcat (25 min)

#### 👥 PAIR PROGRAMMING: Server TCP simplu

**Instrucțiuni pentru lucru în perechi:**
- **Driver** (cel care tastează): Scrie comenzile în terminal
- **Navigator** (cel care ghidează): Verifică sintaxa, sugerează pași
- **Schimbați rolurile la fiecare 10 minute**

**Terminal 1 (Server) - Driver:**
```bash
# Pornire server pe port 9999
nc -l -p 9999
```

**Terminal 2 (Client) - Navigator devine Driver:**
```bash
# Conectare la server
nc localhost 9999
```

După conectare, mesajele tastate în oricare terminal apar în celălalt (comunicare bidirecțională).

#### 2.2 Verificare port deschis

**🎯 PREDICȚIE:**
> Ce va afișa comanda `ss -tlnp | grep 9999` ÎNAINTE de a conecta clientul? Dar DUPĂ ce clientul s-a conectat?

```bash
# Înainte de conectarea clientului
ss -tlnp | grep 9999

# Output așteptat:
# LISTEN  0  1  0.0.0.0:9999  0.0.0.0:*  users:(("nc",pid=...,fd=3))
```

#### 2.3 Trimitere date automatizată

```bash
# Trimitere mesaj simplu
echo "Hello Server!" | nc localhost 9999

# Trimitere fișier
cat README.md | nc localhost 9999

# Trimitere cu timeout
echo "Test" | nc -w 2 localhost 9999
```

#### 2.4 Server și client UDP

```bash
# Server UDP (Terminal 1)
nc -u -l -p 8888

# Client UDP (Terminal 2)
nc -u localhost 8888
```

**Diferențe observabile:**
- Nu există conexiune persistentă
- Fiecare mesaj este independent
- Nu există confirmare de primire

---

### 🗳️ PEER INSTRUCTION #2: TCP vs UDP Packets

**Scenariu:** Trimiteți mesajul "Hi" (2 bytes + newline) prin TCP și prin UDP.

**Întrebare:** Câte pachete va trimite TCP pentru acest mesaj simplu?

| Opțiune | Răspuns |
|---------|---------|
| **A** | 1 pachet (la fel ca UDP) |
| **B** | 3 pachete (câte unul per caracter) |
| **C** | Minim 7-8 pachete (handshake + date + terminare) |
| **D** | Depinde de MTU |

<details>
<summary>🎯 Note instructor</summary>

**Răspuns corect:** C

**Detaliere:**
- 3 pachete handshake (SYN, SYN-ACK, ACK)
- 1-2 pachete date (PSH-ACK) + ACK
- 2-4 pachete terminare (FIN-ACK în ambele direcții)

**Analiza distractorilor:**
- **A:** Confuzie TCP/UDP, nu înțelege overhead-ul conexiunii
- **B:** Confuzie cu caractere, nu înțelege segmentarea
- **D:** Parțial corect pentru date mari, dar irelevant pentru 3 bytes

**Demo:** Capturați ambele și comparați cu `tshark -r tcp.pcap | wc -l` vs `tshark -r udp.pcap | wc -l`
</details>

---

### Partea III: Captură pachete cu tshark (30 min)

#### 3.1 Captură de bază

**🎯 PREDICȚIE:**
> Câte pachete credeți că vor apărea pentru o singură conexiune TCP în care trimitem "Test"?

```bash
# Captură pe loopback, filtru pentru port 9999
tshark -i lo -f "port 9999"

# Salvare în fișier PCAP
tshark -i lo -f "port 9999" -w captura.pcap

# Limitare la N pachete
tshark -i lo -f "port 9999" -c 20
```

**Experiment complet (3 terminale):**

1. **T1 - Captură:** `tshark -i lo -f "port 9999" -w handshake.pcap`
2. **T2 - Server:** `nc -l -p 9999`
3. **T3 - Client:** `echo "Test" | nc localhost 9999`
4. **T1:** Ctrl+C pentru oprire captură

#### 3.2 Citire și analiză captură

```bash
# Afișare simplă
tshark -r handshake.pcap

# Filtrare doar TCP SYN
tshark -r handshake.pcap -Y "tcp.flags.syn==1"

# Filtrare handshake complet
tshark -r handshake.pcap -Y "tcp.flags.syn==1 or tcp.flags.fin==1"
```

#### 3.3 Extragere câmpuri specifice

```bash
# Format tabelar cu câmpuri selectate
tshark -r handshake.pcap -T fields \
  -e frame.number \
  -e frame.time_relative \
  -e ip.src \
  -e ip.dst \
  -e tcp.srcport \
  -e tcp.dstport \
  -e tcp.flags.str \
  -e tcp.len
```

#### 3.4 Export CSV pentru analiză

```bash
# Export cu header
tshark -r handshake.pcap -T fields -E header=y -E separator=, \
  -e frame.number \
  -e frame.time_relative \
  -e tcp.srcport \
  -e tcp.dstport \
  -e tcp.len \
  > analiza.csv
```

---

### Partea IV: Analiză TCP Handshake (20 min)

#### 4.1 Three-Way Handshake

**Analogie concretă:** Handshake-ul TCP e ca o conversație telefonică formală:
- Client: "Bună, sunt Ion, vreau să vorbesc" (SYN)
- Server: "Bună Ion, te aud, sunt Maria" (SYN-ACK)
- Client: "Perfect Maria, te aud și eu" (ACK)
- Acum pot vorbi!

Secvența de stabilire a conexiunii TCP:

```
Client                    Server
   |                        |
   |------ SYN (seq=x) ---->|    Pasul 1: Client inițiază
   |                        |
   |<--- SYN-ACK (seq=y, ---|    Pasul 2: Server confirmă
   |      ack=x+1)          |             și trimite propriul SYN
   |                        |
   |------ ACK (seq=x+1, -->|    Pasul 3: Client confirmă
   |       ack=y+1)         |             SYN-ul serverului
   |                        |
   |    Conexiune stabilită |
```

#### 4.2 Identificare în captură

Output tshark tipic:
```
1  0.000000  127.0.0.1 → 127.0.0.1  TCP 54321→9999 [SYN] Seq=0
2  0.000015  127.0.0.1 → 127.0.0.1  TCP 9999→54321 [SYN,ACK] Seq=0 Ack=1
3  0.000023  127.0.0.1 → 127.0.0.1  TCP 54321→9999 [ACK] Seq=1 Ack=1
4  0.000089  127.0.0.1 → 127.0.0.1  TCP 54321→9999 [PSH,ACK] Len=5
```

**Flag-uri TCP importante:**
| Flag | Semnificație |
|------|-------------|
| SYN | Synchronize - inițiere conexiune |
| ACK | Acknowledge - confirmare |
| PSH | Push - datele trebuie livrate imediat |
| FIN | Finish - închidere conexiune |
| RST | Reset - întrerupere forțată |

---

### 🗳️ PEER INSTRUCTION #3: Connection Refused

**Scenariu:** Clientul trimite SYN către portul 9999, dar NICIUN server nu ascultă pe acel port.

**Întrebare:** Ce se întâmplă?

| Opțiune | Răspuns |
|---------|---------|
| **A** | Clientul primește RST (reset) de la server |
| **B** | Clientul așteaptă până la timeout fără răspuns |
| **C** | Conexiunea se stabilește dar fără date |
| **D** | Sistemul de operare trimite automat SYN-ACK |

<details>
<summary>🎯 Note instructor</summary>

**Răspuns corect:** A

**Explicație:** Când portul e închis (niciun proces în LISTEN), kernel-ul răspunde automat cu RST.

**Analiza distractorilor:**
- **B:** Comportament de firewall cu DROP, nu port închis
- **C:** Imposibil fără handshake complet
- **D:** Confuzie fundamentală - SYN-ACK vine doar de la proces în LISTEN

**Demo:** 
```bash
# Terminal 1 - captură
tshark -i lo -f "port 9999"
# Terminal 2 - conexiune eșuată
nc localhost 9999
# Observați: SYN → RST
```
</details>

---

#### 4.3 Comparație TCP vs UDP

| Aspect | TCP | UDP |
|--------|-----|-----|
| Pachete pentru "Hello" | ~8 (handshake + date + termination) | 1 singur |
| Confirmare | Da (ACK pentru fiecare segment) | Nu |
| Ordine garantată | Da (sequence numbers) | Nu |
| Overhead header | 20+ bytes | 8 bytes |

---

## 📝 PARSONS PROBLEM: Ordonare comenzi captură

**Sarcină:** Aranjați comenzile de mai jos în ordinea corectă pentru a captura un TCP handshake complet.

**Comenzi de ordonat (amestecate):**
```
D) echo "Test" | nc localhost 9999
A) tshark -i lo -f "port 9999" -w cap.pcap
C) nc -l -p 9999 &
B) sleep 2
E) pkill tshark
F) tshark -r cap.pcap
```

<details>
<summary>✅ Soluție corectă</summary>

**Ordinea corectă:** A → B → C → D → E → F

1. **A** - Pornește captura (trebuie să ruleze ÎNAINTE de trafic)
2. **B** - Așteaptă să pornească tshark
3. **C** - Pornește serverul în background
4. **D** - Clientul se conectează și trimite date
5. **E** - Oprește captura
6. **F** - Analizează rezultatul

**De ce contează ordinea:**
- Dacă pornești serverul înainte de captură, pierzi SYN inițial
- Dacă nu aștepți (`sleep`), tshark poate să nu fie gata
</details>

---

## 🔍 TRACING EXERCISE: Urmărire execuție

**Cod de analizat:**

```python
import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Linia 1
sock.bind(("0.0.0.0", 5000))                              # Linia 2
sock.listen(1)                                            # Linia 3
print("Server pornit")                                    # Linia 4
conn, addr = sock.accept()                                # Linia 5
print(f"Client conectat: {addr}")                         # Linia 6
data = conn.recv(1024)                                    # Linia 7
print(f"Primit: {data}")                                  # Linia 8
conn.close()                                              # Linia 9
sock.close()                                              # Linia 10
```

**Întrebări:**

1. După execuția liniei 3, ce va afișa `ss -tlnp | grep 5000`?
2. Pe ce linie se blochează programul așteptând un client?
3. Dacă clientul trimite "Hello", ce tip de date conține variabila `data` la linia 8?
4. Ce se întâmplă dacă omitem linia 9 și clientul trimite alt mesaj?

<details>
<summary>✅ Răspunsuri</summary>

1. **După linia 3:** `LISTEN 0 1 0.0.0.0:5000 0.0.0.0:* users:(("python3",...))` - socket în stare LISTEN
2. **Linia 5** - `accept()` este blocantă, așteaptă conexiune
3. **Tip `bytes`** - `b'Hello'`, nu string! Trebuie `.decode()` pentru string
4. **Mesajul se pierde** sau eroare - socket-ul client (`conn`) e închis, dar `sock` rămâne deschis
</details>

---

## 🐛 DEBUG CHALLENGE: Găsește erorile

**Cod cu 3 erori - găsește-le!**

```python
def broken_server(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Eroare 1?
    sock.bind("localhost", port)                              # Eroare 2?
    sock.listen(5)                                            # Eroare 3?
    conn, addr = sock.accept()
    return conn
```

<details>
<summary>✅ Soluție</summary>

**Eroarea 1:** `SOCK_DGRAM` = UDP, dar `listen()` și `accept()` sunt pentru TCP!
- Fix: `socket.SOCK_STREAM`

**Eroarea 2:** `bind()` primește un TUPLE, nu două argumente separate!
- Fix: `sock.bind(("localhost", port))`

**Eroarea 3:** După corectarea la TCP, `listen(5)` e corect, DAR...
- Dacă rămâne UDP, `listen()` va da eroare pentru că UDP nu are conceptul de "listen"
</details>

---

## Exerciții

### Exercițiu 1: Diagnostic rețea (ușor)
Rulați `ping` către loopback, gateway și 8.8.8.8. Notați RTT-ul mediu pentru fiecare.

### Exercițiu 2: Server TCP (ușor) 👥
**Lucru în perechi:** Creați un server netcat pe portul 5000 și conectați-vă de la alt terminal. Schimbați rolurile driver/navigator.

### Exercițiu 3: Captură handshake (mediu)
Capturați un TCP handshake complet și identificați cele 3 pachete SYN/SYN-ACK/ACK.

### Exercițiu 4: TCP vs UDP (mediu)
Comparați numărul de pachete pentru același mesaj trimis via TCP și UDP.

### Exercițiu 5: Export CSV (mediu-avansat)
Exportați o captură în CSV și calculați durata handshake-ului.

### Exercițiu 6: Calculator throughput (avansat)
Măsurați throughput-ul real transferând 10MB prin netcat și calculând timpul.

### Challenge: Mini HTTP Server
Creați un server HTTP minimal folosind doar netcat și bash.

---

## Debugging frecvent

| Problemă | Cauză | Soluție |
|----------|-------|---------|
| "Address already in use" | Port ocupat | `ss -tlnp \| grep PORT` și opriți procesul |
| "Connection refused" | Server nu rulează | Verificați că serverul ascultă |
| "Permission denied" (tshark) | Lipsesc permisiuni | `sudo` sau adăugare la grupul wireshark |
| tshark nu vede pachete | Interfață greșită | Folosiți `-i lo` pentru loopback |

---

## Misconceptii frecvente

❌ **"UDP e nesigur, deci nu-l folosim niciodată"**
→ UDP e perfect pentru streaming video, gaming, DNS - unde viteza contează mai mult decât 100% reliability

❌ **"Un socket e același lucru cu un port"**
→ Socket = IP + Port + Protocol. Poți avea multiple socket-uri pe același port (ex: server cu mulți clienți)

❌ **"TCP garantează că datele ajung instant"**
→ TCP garantează ordinea și livrarea, NU viteza. Retransmisiile pot adăuga delay semnificativ.

❌ **"Dacă ping merge, aplicația mea ar trebui să meargă"**
→ Ping folosește ICMP, nu TCP/UDP. Un firewall poate bloca TCP dar permite ICMP.

---

## Ce am învățat

- Comenzile `ip`, `ss`, `ping` pentru diagnostic de rețea
- Crearea serverelor TCP/UDP cu `netcat`
- Captura și analiza traficului cu `tshark`
- Identificarea TCP handshake în capturi
- Diferențele practice dintre TCP și UDP

---

## Pregătire pentru săptămâna viitoare

Seminar 2: Programare pe socket-uri

- Revedeți modulul Python `socket`
- Studiați diferența dintre `SOCK_STREAM` și `SOCK_DGRAM`
- Pregătiți exercițiile Python din starterkit (`ex_1_02_tcp_server_client.py`)

---

*Revolvix&Hypotheticalandrei • Rețele de Calculatoare • ASE București*
