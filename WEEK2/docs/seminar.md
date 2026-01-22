# Seminar 2: Analiză de Rețea și Programare Socket

**Disciplina:** Rețele de Calculatoare  
**Durată:** 2 ore (120 minute)  
**Forma:** Laborator asistat cu exerciții practice  
**Unelte:** Python 3, Mininet, Wireshark/tshark, tcpdump, netcat

---

## Scopul săptămânii

### Ce vom învăța
Vom exersa programarea de rețea folosind socket-uri Python. Vom implementa servere și clienți TCP/UDP, vom captura trafic pentru analiză și vom corela codul cu pachetele observate în captură.

### De ce contează
Orice dezvoltator de aplicații distribuite, specialist în securitate sau administrator de sisteme trebuie să știe să programeze comunicații de rețea și să diagnosticheze probleme prin analiză de trafic.

---

## Prerechizite

### Din curs (Săptămâna 2)
- Modelul OSI: cele 7 straturi și rolul lor
- Modelul TCP/IP: cele 4 straturi practice
- Diferența TCP (orientat conexiune) vs UDP (datagrame)
- Conceptul de încapsulare

### Verificare mediu de lucru
```bash
python3 --version    # >= 3.8
sudo mn --version    # Mininet 2.3+
tshark -v            # Wireshark CLI
nc -h                # netcat
```

---

## Obiective operaționale

La finalul acestui seminar, studentul va putea să:

| Cod | Obiectiv |
|-----|----------|
| **O1** | Execute comenzi de bază Mininet pentru testare conectivitate |
| **O2** | Implementeze un server TCP concurent folosind socket-uri Python |
| **O3** | Captureze trafic de rețea cu tcpdump/tshark |
| **O4** | Analizeze handshake-ul TCP și să-l identifice în captură |
| **O5** | Compare comportamentul TCP vs UDP |
| **O6** | Coreleze logurile aplicației cu pachetele din captură |

---

## Peer Instruction — Întrebări cu Discuție (15 minute distribuite)

Aceste întrebări se folosesc în momente cheie ale seminarului. Procedura:
1. **Votează individual** (1 min)
2. **Discută cu colegul de bancă** (2 min)
3. **Votează din nou** (30 sec)
4. **Discuție colectivă** (1-2 min)

### MCQ 1: După Faza 1 (Mininet warm-up)

**Un `ping` reușit între h1 și h2 în Mininet garantează că:**

- A) Serverul HTTP de pe h2 funcționează corect
- B) Conexiunea TCP între h1 și h2 va reuși sigur
- C) **Există conectivitate IP (Layer 3) între h1 și h2** ✓
- D) Portul 80 este deschis pe h2

*Misconceptie vizată: Studenții confundă conectivitatea L3 (IP/ICMP) cu funcționalitatea L7 (aplicație).*

### MCQ 2: Înainte de analiza handshake (Faza 2)

**În handshake-ul TCP, de ce sunt necesari 3 pași și nu doar 2?**

- A) Pentru a trimite mai multe date de la început
- B) Pentru că TCP e mai lent decât UDP
- C) **Fiecare parte trebuie să confirme că poate și trimite, și primi** ✓
- D) Pentru a negocia portul de comunicare

*Misconceptie vizată: Studenții cred că handshake-ul e doar o formalitate sau că transferă date.*

### MCQ 3: După comparația TCP vs UDP (Faza 3)

**Pentru un joc online multiplayer în timp real, de ce se preferă UDP?**

- A) UDP e mai sigur decât TCP
- B) UDP garantează că pachetele ajung în ordine
- C) **Latența mică e mai importantă decât pierderea ocazională de pachete** ✓
- D) UDP poate trimite mai multe date pe secundă decât TCP

*Misconceptie vizată: Studenții cred că UDP e „mai bun" în loc să înțeleagă trade-off-ul latență vs fiabilitate.*

### MCQ 4: După template-uri (Faza 4)

**Ce se întâmplă dacă serverul TCP uită să apeleze `listen()` înainte de `accept()`?**

- A) Clientul se conectează normal
- B) Conexiunea se face prin UDP în loc de TCP
- C) **`accept()` va eșua cu eroare (socket invalid pentru ascultare)** ✓
- D) Serverul va primi mesaje dar nu va putea răspunde

*Misconceptie vizată: Studenții nu înțeleg că `listen()` marchează socket-ul ca pasiv.*

---

## Structura cronologică

### FAZA 0: Pregătire (10 minute)

#### Activitatea 0.1: Verificare mediu [3 min]

| Minut | Acțiune |
|-------|---------|
| 0-1 | Explicare ce verificăm și de ce |
| 1-3 | Studenții rulează comenzile |

```bash
# Verificare componente
python3 --version
sudo mn --version
tshark -v | head -n 2
nc -h 2>&1 | head -n 1
```

**Rezultat așteptat**: Toate comenzile returnează versiuni valide.

#### Activitatea 0.2: Curățare mediu anterior [4 min]

*Personal, rulez `sudo mn -c` de fiecare dată când intru în laborator, chiar dacă nu cred că am sesiuni vechi. M-am ars de prea multe ori cu "de ce nu merge?!" când răspunsul era o sesiune zombie din ziua anterioară.*

```bash
# Curățare sesiuni Mininet anterioare
sudo mn -c

# Navigare în directorul starterkit
cd starterkit_s2
make verify
```

#### Activitatea 0.3: Verificare scripturi Python [3 min]
```bash
# Verificare sintaxă
python3 -m py_compile seminar/python/exercises/ex_2_01_tcp.py
python3 -m py_compile seminar/python/exercises/ex_2_02_udp.py
```

---

### FAZA 1: Warm-up Mininet (15 minute)

#### Activitatea 1.1: Pornire topologie [4 min]

| Minut | Acțiune |
|-------|---------|
| 0-1 | Explicare comandă și ce face |
| 1-3 | Studenții pornesc topologia |
| 3-4 | Verificare că toți au prompt-ul Mininet |

```bash
make mininet-cli
# sau direct:
sudo python3 seminar/mininet/topologies/topo_2_base.py --cli
```

**Topologia**:
- 1 switch (s1)
- 3 hosturi (h1: 10.0.0.1, h2: 10.0.0.2, h3: 10.0.0.3)
- Toate în aceeași subrețea /24

#### Activitatea 1.2: Explorare topologie [5 min]

**🔮 PREDICȚIE înainte de `nodes`:**
> Câte noduri crezi că va afișa comanda `nodes`? (Hint: avem hosturi ȘI switch-uri)

În prompt-ul Mininet:
```
mininet> nodes
available nodes are: 
h1 h2 h3 s1

mininet> net
h1 h1-eth0:s1-eth1
h2 h2-eth0:s1-eth2
h3 h3-eth0:s1-eth3
s1 lo:  s1-eth1:h1-eth0 s1-eth2:h2-eth0 s1-eth3:h3-eth0

mininet> dump
<Host h1: h1-eth0:10.0.0.1 pid=...>
<Host h2: h2-eth0:10.0.0.2 pid=...>
<Host h3: h3-eth0:10.0.0.3 pid=...>
<OVSSwitch s1: lo:127.0.0.1 ...>

mininet> h1 ifconfig h1-eth0
```

**Întrebări de reflecție**:
- Ce adresă IP are h1?
- Ce adresă MAC are interfața h1-eth0?
- Cum sunt conectate hosturile?

#### Activitatea 1.3: Test conectivitate [6 min]

**🔮 PREDICȚIE înainte de `pingall`:**
> Ce procent de pachete crezi că se vor pierde? (Hint: suntem într-o rețea virtuală locală, perfect izolată)

```
mininet> pingall
*** Ping: testing ping reachability
h1 -> h2 h3 
h2 -> h1 h3 
h3 -> h1 h2 
*** Results: 0% dropped (6/6 received)

mininet> h1 ping -c 3 10.0.0.2
PING 10.0.0.2 (10.0.0.2) 56(84) bytes of data.
64 bytes from 10.0.0.2: icmp_seq=1 ttl=64 time=0.234 ms
...
```

**Discuție**: Un ping reușit verifică conectivitatea la nivel L3 (IP via ICMP). Nu garantează că o aplicație răspunde la nivel L7!

**→ Aplică MCQ 1 aici**

---

### FAZA 2: TCP Lab (35 minute)

#### Activitatea 2.1: Pornire server TCP [5 min]

| Minut | Acțiune |
|-------|---------|
| 0-1 | Explicare parametri (bind, port, mode) |
| 1-2 | Demonstrație comandă |
| 2-4 | Studenții rulează pe propriile mașini |
| 4-5 | Verificare că toți au serverul pornit |

**Pair Programming — Formați perechi:**
- **Driver**: tastează comenzile
- **Navigator**: verifică, gândește, sugerează
- Schimbați rolurile la fiecare 10 minute

*Am observat că perechile care schimbă rolurile efectiv învață mai bine — Driver-ul se concentrează pe execuție, Navigator-ul pe înțelegere. Când schimbi, transferi și perspectiva.*

În Mininet:
```
mininet> h1 python3 -u seminar/python/exercises/ex_2_01_tcp.py server --bind 10.0.0.1 --port 9999 --mode threaded &
```

**Parametri explicați**:
- `--bind 10.0.0.1`: Ascultă doar pe interfața h1
- `--port 9999`: Portul de ascultare
- `--mode threaded`: Un thread per conexiune (server concurent)
- `&`: Rulare în background

**Verificare**:
```
mininet> jobs
[1]+ Running    python3 -u ... &
```

#### Activitatea 2.2: Pornire captură trafic [3 min]

| Minut | Acțiune |
|-------|---------|
| 0-1 | Explicare filtru BPF |
| 1-3 | Studenții pornesc captura |

```
mininet> h2 tcpdump -i h2-eth0 -w seminar/captures/tcp_demo.pcap 'tcp port 9999' &
```

**Explicație filtru BPF**:
- `-i h2-eth0`: Interfața de captură
- `-w ...pcap`: Salvare în format PCAP
- `'tcp port 9999'`: Doar pachete TCP pe portul 9999

*Preferința mea: tcpdump pentru captură, tshark pentru analiză. Tcpdump e mai lightweight și nu pierzi pachete sub load. Tshark e mai puternic pentru disecție.*

#### Activitatea 2.3: Trimitere mesaje [7 min]

| Minut | Acțiune |
|-------|---------|
| 0-1 | **MCQ 2** - vot individual |
| 1-3 | Discuție în perechi |
| 3-4 | Revot și discuție |
| 4-7 | Trimitere mesaje și observare output |

**→ Aplică MCQ 2 înainte de a trimite primul mesaj**

**🔮 PREDICȚIE înainte de primul client:**
> Câte pachete TCP crezi că vor apărea în captură pentru UN singur mesaj "Hello"?
> A) 2 (request + response)
> B) 5-6 pachete
> C) 9+ pachete
> 
> Votează cu mâna ridicată!

**Client de pe h2**:
```
mininet> h2 python3 seminar/python/exercises/ex_2_01_tcp.py client --host 10.0.0.1 --port 9999 --message "Hello from h2"
[14:32:15.123][CLIENT] RX 17B în 2.3ms: b'OK: HELLO FROM H2'
```

**Client de pe h3**:
```
mininet> h3 python3 seminar/python/exercises/ex_2_01_tcp.py client --host 10.0.0.1 --port 9999 --message "Hello from h3"
```

**Test cu netcat** (pentru a demonstra interoperabilitatea):
```
mininet> h2 sh -c 'echo "netcat test" | nc 10.0.0.1 9999'
OK: NETCAT TEST
```

*Netcat (`nc`) e tool-ul meu preferat pentru teste rapide — e ca un "cuțit elvețian" pentru rețelistică. Dacă nu funcționează cu netcat, problema e aproape sigur în server, nu în clientul tău custom.*

**Observații în log-ul serverului**:
- Timestamp precis
- Thread ID pentru fiecare conexiune
- IP:Port client
- Mesaj primit și răspuns trimis

#### Activitatea 2.4: Oprire captură și analiză [10 min]

| Minut | Acțiune |
|-------|---------|
| 0-1 | Oprire captură |
| 1-4 | Analiză handshake cu tshark |
| 4-8 | Discuție colectivă - identificare SYN/SYN-ACK/ACK |
| 8-10 | Vizualizare payload |

**Oprire captură**:
```
mininet> jobs
[1]+ Running    python3 ... server ...
[2]+ Running    tcpdump ...

mininet> kill %2
```

**🔮 PREDICȚIE înainte de tshark:**
> Care va fi primul flag TCP din captură? (SYN? ACK? PSH?)

**Analiză cu tshark** (în terminal separat, nu Mininet):
```bash
tshark -r seminar/captures/tcp_demo.pcap -Y "tcp.port==9999" -T fields \
  -e frame.number -e ip.src -e tcp.srcport -e ip.dst -e tcp.dstport -e tcp.flags.str
```

*Eu prefer `tshark` în loc de Wireshark GUI pentru analiză rapidă — output-ul text e mai ușor de copiat în rapoarte și nu trebuie să dai click prin meniuri. Dar pentru explorare inițială sau când cauți ceva și nu știi exact ce, GUI-ul Wireshark e imbatabil.*

**Output așteptat** (pentru o sesiune):
```
1   10.0.0.2   45678   10.0.0.1   9999   ··········S·    # SYN
2   10.0.0.1   9999    10.0.0.2   45678  ·······A··S·    # SYN-ACK
3   10.0.0.2   45678   10.0.0.1   9999   ·······A····    # ACK
4   10.0.0.2   45678   10.0.0.1   9999   ·······AP···    # DATA (PSH+ACK)
5   10.0.0.1   9999    10.0.0.2   45678  ·······A····    # ACK
6   10.0.0.1   9999    10.0.0.2   45678  ·······AP···    # RESPONSE
7   10.0.0.2   45678   10.0.0.1   9999   ·······A····    # ACK
...
```

*Ăsta e momentul "aha" pentru mulți studenți — când văd că pentru UN mesaj de 5 bytes, TCP a generat 9+ pachete. "Deci de-aia e UDP mai rapid!" Da, exact.*

**Întrebări de analiză**:
1. Identificați cele 3 pachete de handshake (SYN → SYN-ACK → ACK)
2. Câte sesiuni TCP distincte observați? (4-tuple unic)
3. Unde apare payload-ul aplicației?

**Vizualizare payload**:
```bash
tshark -r seminar/captures/tcp_demo.pcap -Y "tcp.port==9999 and data" -T fields \
  -e frame.number -e ip.src -e ip.dst -e tcp.payload
```

---

### FAZA 3: UDP Lab (25 minute)

#### Activitatea 3.1: Pornire server UDP [3 min]

| Minut | Acțiune |
|-------|---------|
| 0-1 | Oprire server TCP anterior |
| 1-3 | Pornire server UDP |

Mai întâi, oprire server TCP:
```
mininet> jobs
mininet> kill %1
```

Pornire server UDP:
```
mininet> h1 python3 -u seminar/python/exercises/ex_2_02_udp.py server --bind 10.0.0.1 --port 9998 &
```

#### Activitatea 3.2: Pornire captură UDP [2 min]

```
mininet> h2 tcpdump -i h2-eth0 -w seminar/captures/udp_demo.pcap 'udp port 9998' &
```

#### Activitatea 3.3: Client UDP interactiv [8 min]

| Minut | Acțiune |
|-------|---------|
| 0-1 | Pornire client interactiv |
| 1-6 | Test comenzi protocol |
| 6-8 | Observare statistici |

**🔮 PREDICȚIE înainte de clientul UDP:**
> Dacă trimiți comanda "ping" și serverul răspunde "PONG", câte pachete UDP vor apărea în captură?
> A) 1 pachet
> B) 2 pachete
> C) 3+ pachete

```
mininet> h2 python3 seminar/python/exercises/ex_2_02_udp.py client --host 10.0.0.1 --port 9998 --interactive
```

**Comenzi de test** (protocol aplicație custom):
```
> ping
PONG (RTT: 0.8ms)

> upper:hello world
HELLO WORLD (RTT: 0.9ms)

> abc
UNKNOWN COMMAND (RTT: 0.7ms)

> exit
--- Stats: sent=3, received=3, timeouts=0 ---
```

#### Activitatea 3.4: Comparație TCP vs UDP [12 min]

| Minut | Acțiune |
|-------|---------|
| 0-1 | Oprire captură |
| 1-4 | Analiză UDP cu tshark |
| 4-10 | Completare tabel comparativ - discuție |
| 10-12 | **MCQ 3** |

**Oprire captură**:
```
mininet> kill %<job_number_tcpdump>
```

**🔮 PREDICȚIE înainte de analiza UDP:**
> Câte pachete vei vedea pentru cele 3 comenzi trimise (ping, upper, abc)?
> Compară mental cu ce ai văzut la TCP.

**Analiză UDP**:
```bash
tshark -r seminar/captures/udp_demo.pcap -Y "udp.port==9998" -T fields \
  -e frame.number -e ip.src -e udp.srcport -e ip.dst -e udp.dstport -e frame.len
```

**Output așteptat**:
```
1   10.0.0.2   54321   10.0.0.1   9998   46
2   10.0.0.1   9998    10.0.0.2   54321   46
3   10.0.0.2   54321   10.0.0.1   9998   53
4   10.0.0.1   9998    10.0.0.2   54321   53
```

**Întrebări comparative**:

| Aspect | TCP | UDP |
|--------|-----|-----|
| Pachete pentru un mesaj | 9+ (handshake + data + ACK + FIN) | 2 (request + response) |
| Header overhead | 20+ bytes | 8 bytes |
| Handshake | Da (SYN-SYN/ACK-ACK) | Nu |
| Confirmări | Da (ACK pentru fiecare segment) | Nu |
| Numere de secvență | Da | Nu |
| Reordonare | Da | Nu |

**→ Aplică MCQ 3 aici**

---

### FAZA 4: Exerciții de Înțelegere — Nu Doar Cod (20 minute)

*Din experiență, exercițiile astea par "ușoare" dar dezvăluie goluri de înțelegere pe care scrierea de cod le maschează. Mulți studenți pot copy-paste un server funcțional, dar nu pot ordona corect pașii când îi vezi amestecați.*

#### Exercițiul 4.1: Parsons Problem — Server TCP [7 min]

| Minut | Acțiune |
|-------|---------|
| 0-1 | Explicare exercițiu |
| 1-5 | Lucru individual/perechi |
| 5-7 | Verificare soluție, discuție |

**Instrucțiuni**: Liniile de cod de mai jos sunt amestecate. Pune-le în ordinea corectă pentru a obține un server TCP funcțional. Nu trebuie să scrii cod — doar să ordonezi.

**🔮 PREDICȚIE:**
> Care linie crezi că vine PRIMA? Dar ULTIMA?

```python
# LINII AMESTECATE (ordonează-le):

conn.close()
sock.listen(5)
data = conn.recv(1024)
conn, addr = sock.accept()
sock.bind(('0.0.0.0', 9999))
conn.sendall(b"OK: " + data.upper())
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
```

**⚠️ Capcană frecventă:**
> Mulți studenți pun `listen()` după `accept()`. Gândește-te: poți ridica telefonul (accept) dacă nu l-ai pus pe "mod recepție" (listen)?

**Soluție (verifică după 5 minute):**
```python
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 1. CREATE
sock.bind(('0.0.0.0', 9999))                              # 2. BIND
sock.listen(5)                                             # 3. LISTEN
conn, addr = sock.accept()                                 # 4. ACCEPT
data = conn.recv(1024)                                     # 5. RECEIVE
conn.sendall(b"OK: " + data.upper())                       # 6. SEND
conn.close()                                               # 7. CLOSE
```

**Subgoal Labels** (etichete transferabile):
- CREATE_SOCKET → BIND → LISTEN → ACCEPT → RECEIVE → SEND → CLOSE

---

#### Exercițiul 4.2: Trace Exercise — Ce afișează codul? [6 min]

| Minut | Acțiune |
|-------|---------|
| 0-1 | Citire cod |
| 1-4 | Răspuns la întrebări |
| 4-6 | Verificare răspunsuri |

**Cod dat** (NU rulezi, doar analizezi):

**🔮 PREDICȚIE înainte de a citi întrebările:**
> Uită-te la prima linie. Ce tip de socket e? TCP sau UDP?

```python
import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.sendto(b"ping", ("10.0.0.1", 9998))
data, addr = sock.recvfrom(1024)
print(f"Răspuns de la {addr[0]}:{addr[1]} = {data.decode()}")
sock.close()
```

**Întrebări:**
1. Ce tip de socket se creează? (TCP sau UDP?)
2. Clientul apelează `connect()`?
3. Dacă serverul UDP răspunde cu `b"PONG"`, ce se afișează?

**⚠️ Capcană frecventă:**
> Studenții care au văzut doar TCP se așteaptă să vadă `connect()`. La UDP, nu există conexiune — `sendto()` și `recvfrom()` fac totul.

**Răspunsuri:**
1. UDP (SOCK_DGRAM)
2. Nu — UDP nu necesită `connect()`, folosește `sendto()`/`recvfrom()`
3. `Răspuns de la 10.0.0.1:9998 = PONG`

---

#### Exercițiul 4.3: Debugging Exercise — Găsește bug-ul [7 min]

| Minut | Acțiune |
|-------|---------|
| 0-1 | Citire cod |
| 1-4 | Identificare bug |
| 4-5 | Discuție răspuns |
| 5-7 | **MCQ 4** |

**Cod cu eroare** (serverul nu funcționează):

```python
import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(('0.0.0.0', 9999))
# sock.listen(5)  # <-- LINIA ACEASTA LIPSEȘTE
conn, addr = sock.accept()  # EROARE: accept() pe socket non-listening
data = conn.recv(1024)
conn.sendall(data.upper())
conn.close()
```

**Întrebare**: Ce eroare va apărea și de ce?

*Greșeala mea preferată de demonstrat live: șterg `listen()` și întreb "De ce nu merge?" Mesajul de eroare e criptic (`Invalid argument`), dar cauza e simplă odată ce înțelegi fluxul.*

**⚠️ Hint:**
> Gândește-te la analogia cu telefonul. Ce face `listen()` diferit de `bind()`?

**Răspuns**: `OSError: [Errno 22] Invalid argument` sau similar. Socket-ul nu a fost marcat ca pasiv (listening) înainte de `accept()`. Soluție: adaugă `sock.listen(5)` după `bind()`.

**→ Aplică MCQ 4 aici**

---

### FAZA 5: Template-uri de Completat (15 minute)

#### Activitatea 5.1: Template server TCP [7 min]

| Minut | Acțiune |
|-------|---------|
| 0-1 | Deschidere fișier, explicare TODO-uri |
| 1-5 | Completare cod |
| 5-7 | Test cu netcat |

**Fișier**: `seminar/python/templates/tcp_server_template.py`

**Cerințe de completat**:
1. Afișarea IP:Port al clientului la conectare
2. Afișarea lungimii mesajului primit
3. Construirea răspunsului: `b"OK: " + mesaj.upper()`
4. Trimiterea răspunsului cu `sendall()`

**🔮 PREDICȚIE înainte de test:**
> Dacă trimiți "test message", ce răspuns vei primi?

**Test**:
```bash
# Terminal 1: Server
python3 seminar/python/templates/tcp_server_template.py

# Terminal 2: Client
echo "test message" | nc 127.0.0.1 12345
# Așteptat: OK: TEST MESSAGE
```

#### Activitatea 5.2: Template server UDP [8 min]

| Minut | Acțiune |
|-------|---------|
| 0-1 | Deschidere fișier, explicare protocol |
| 1-6 | Implementare protocol |
| 6-8 | Test |

**Fișier**: `seminar/python/templates/udp_server_template.py`

**Cerințe de completat**:
1. Decodificare mesaj (bytes → string cu `.decode('utf-8')`)
2. Implementare protocol:
   - `ping` → `PONG`
   - `upper:text` → `TEXT` (uppercase)
   - altceva → `UNKNOWN COMMAND`
3. Logging cu timestamp și adresă client

**Test**:
```bash
# Terminal 1: Server
python3 seminar/python/templates/udp_server_template.py

# Terminal 2: Client
echo "ping" | nc -u 127.0.0.1 12345
# Așteptat: PONG
```

---

### FAZA 6: Extensie Opțională – Router L3 (15 minute)

#### Activitatea 6.1: Topologie cu două subrețele [5 min]

**Ieșire și curățare**:
```
mininet> exit
```
```bash
sudo mn -c
```

**Pornire topologie extinsă**:
```bash
make mininet-extended
# sau:
sudo python3 seminar/mininet/topologies/topo_2_extended.py --cli
```

**Topologie**:
- Subrețea 1: h1 (10.0.1.1), h2 (10.0.1.2), gateway 10.0.1.254
- Subrețea 2: h3 (10.0.2.3), h4 (10.0.2.4), gateway 10.0.2.254
- Router r1: 10.0.1.254 ↔ 10.0.2.254

#### Activitatea 6.2: Test comunicare între subrețele [5 min]

**🔮 PREDICȚIE înainte de ping cross-subnet:**
> h1 (10.0.1.1) vrea să ajungă la h3 (10.0.2.3). Câte "hop-uri" va arăta traceroute?

```
mininet> h1 ping -c 2 10.0.2.3
PING 10.0.2.3 (10.0.2.3) 56(84) bytes of data.
64 bytes from 10.0.2.3: icmp_seq=1 ttl=63 time=0.5 ms
...

mininet> h1 traceroute -n 10.0.2.3
traceroute to 10.0.2.3, 30 hops max
 1  10.0.1.254  0.1 ms
 2  10.0.2.3    0.2 ms
```

**Observație**: TTL scade cu 1 la fiecare hop prin router.

#### Activitatea 6.3: Server TCP între subrețele [5 min]

```
mininet> h1 python3 -u seminar/python/exercises/ex_2_01_tcp.py server --bind 10.0.1.1 --port 9999 &
mininet> h3 python3 seminar/python/exercises/ex_2_01_tcp.py client --host 10.0.1.1 --port 9999 --message "peste router"
```

**Întrebări**:
- Care este ruta pachetului de la h3 la h1?
- Ce rol are router-ul în termeni OSI? (L3 – Rețea)

---

### FAZA 7: Finalizare (5 minute)

#### Curățare mediu
```
mininet> exit
```
```bash
sudo mn -c
make clean
```

#### Livrabile pentru student

1. **Fișier text** cu:
   - Comenzile rulate
   - 3 observații despre diferența TCP vs UDP

2. **Capturi PCAP**:
   - `tcp_demo.pcap`
   - `udp_demo.pcap`

3. **Comenzi tshark** folosite pentru analiză

4. **Exercițiile rezolvate**:
   - Parsons Problem (ordinea corectă)
   - Trace Exercise (răspunsuri)
   - Debugging Exercise (bug-ul identificat)

---

## Mapare pe straturi – Referință rapidă

| Observabil în captură | Strat OSI | Strat TCP/IP | Câmp tshark |
|-----------------------|-----------|--------------|-------------|
| Adresă MAC | L2 | Acces Rețea | `eth.src`, `eth.dst` |
| Adresă IP | L3 | Internet | `ip.src`, `ip.dst` |
| TTL | L3 | Internet | `ip.ttl` |
| Port | L4 | Transport | `tcp.srcport`, `udp.dstport` |
| Flags TCP | L4 | Transport | `tcp.flags`, `tcp.flags.str` |
| Payload | L7 | Aplicație | `tcp.payload`, `data.data` |

---

## Erori frecvente și soluții

| Eroare | Cauză | Soluție |
|--------|-------|---------|
| `Address already in use` | Port ocupat | `pkill -f ex_2_01` sau schimbă portul |
| `Connection refused` | Server oprit | Verifică `jobs`, repornește |
| Captură goală | Filtru greșit | Verifică interfața și portul |
| `mn: command not found` | Mininet lipsă | `sudo apt-get install mininet` |
| Mininet crash | Sesiune anterioară | `sudo mn -c` |
| `Permission denied` tcpdump | Lipsă sudo | Rulează cu `sudo` |

*Un truc pe care l-am învățat după ce am pierdut o oră debuggând: dacă `Connection refused`, ÎNTOTDEAUNA verifică mai întâi dacă serverul chiar rulează. Sună banal, dar 80% din probleme sunt de fapt "am uitat să pornesc serverul".*

---

## Criterii de evaluare formativă

| Nivel | Punctaj | Cerințe |
|-------|---------|---------|
| **Minim** | 5-6 | Rulare server/client TCP și UDP, captură de bază, identificare handshake |
| **Mediu** | 7-8 | Template-uri completate funcțional, analiză detaliată cu tshark, explicare diferențe TCP/UDP |
| **Avansat** | 9-10 | Topologie extinsă funcțională, exerciții de înțelegere complete, corelație completă pe straturi |

---

*Revolvix&Hypotheticalandrei*
