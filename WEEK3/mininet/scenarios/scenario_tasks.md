# Scenarii și Exerciții Practice pentru Mininet - S3 Socket Programming

## Cuprins

1. [Prezentare Generală](#1-prezentare-generală)
2. [Scenariul 1: Broadcast Discovery](#2-scenariul-1-broadcast-discovery)
3. [Scenariul 2: Chat Multi-Subnet](#3-scenariul-2-chat-multi-subnet)
4. [Scenariul 3: Multicast Streaming](#4-scenariul-3-multicast-streaming)
5. [Scenariul 4: TCP Tunnel prin Router](#5-scenariul-4-tcp-tunnel-prin-router)
6. [Scenariul 5: Load Balancing Simplu](#6-scenariul-5-load-balancing-simplu)
7. [Scenariul 6: Packet Capture și Analiză](#7-scenariul-6-packet-capture-și-analiză)
8. [Scenariul 7: Network Partition și Recovery](#8-scenariul-7-network-partition-și-recovery)
9. [Exerciții de Autoevaluare](#9-exerciții-de-autoevaluare)
10. [Grile de Verificare](#10-grile-de-verificare)

---

## 1. Prezentare Generală

### Obiective Educaționale

Aceste scenarii vă ghidează prin experimente practice de rețea folosind Mininet, permițând:

- Observarea directă a comportamentului protocoalelor de rețea
- Înțelegerea diferențelor dintre broadcast, multicast și unicast
- Analiza traficului în timp real cu `tcpdump` și Wireshark
- Depanarea problemelor comune de conectivitate
- Proiectarea și testarea arhitecturilor client-server

### Pregătire Inițială

```bash
# Clonarea kit-ului și instalare dependențe
cd ~/S3_Starterkit_Combined
make setup

# Verificare funcționalitate Mininet
sudo mn --test pingall

# Pornire topologie de bază
sudo python3 mininet/topologies/topo_base.py
```

### Convenții în Documente

| Simbol | Semnificație |
|--------|--------------|
| `mininet>` | Prompt în CLI Mininet |
| `h1>`, `h2>` | Terminal pentru host specific |
| `r1>` | Terminal pentru router |
| `$` | Terminal local (în afara Mininet) |
| 📋 | Task de completat |
| ✅ | Verificare corectitudine |
| ⚠️ | Avertisment sau potențială eroare |
| 💡 | Sugestie sau hint |

---

## 2. Scenariul 1: Broadcast Discovery

### Context

Într-o rețea locală, dispozitivele pot descoperi servicii prin mesaje broadcast. Acest scenariu simulează un protocol simplu de service discovery.

### Topologie

```
    Subnet 10.0.0.0/24
    ┌─────────────────────────────────────┐
    │                                     │
  [h1]──────[s1]──────[h2]──────[h3]     │
 10.0.0.1        10.0.0.2    10.0.0.3    │
 (server)        (client)    (client)    │
    │                                     │
    └─────────────────────────────────────┘
         Broadcast: 10.0.0.255
```

### Exercițiul 1.1: Observarea Broadcast-ului UDP

📋 **Pas 1**: Porniți topologia de bază

```bash
sudo python3 mininet/topologies/topo_base.py
```

📋 **Pas 2**: Deschideți terminale pentru toate host-urile

```
mininet> xterm h1 h2 h3
```

📋 **Pas 3**: Pe h2 și h3, porniți receptori broadcast

```bash
# În terminalul h2:
h2> python3 python/examples/ex01_broadcast_receiver.py

# În terminalul h3:
h3> python3 python/examples/ex01_broadcast_receiver.py
```

📋 **Pas 4**: Pe h1, transmiteți mesaje broadcast

```bash
h1> python3 python/examples/ex01_broadcast_sender.py
```

✅ **Verificare**: Ambele receptoare (h2, h3) primesc mesajele?

📋 **Pas 5**: Capturați traficul pe switch

```bash
# Într-un terminal nou pentru s1:
mininet> s1 tcpdump -i s1-eth1 -n udp port 12345
```

💡 **Hint**: Observați că broadcast-ul ajunge la TOATE porturile switch-ului.

### Exercițiul 1.2: Limitarea Broadcast-ului

📋 **Întrebare de reflecție**: Ce se întâmplă dacă adăugăm un router între două subrețele? Broadcast-ul trece?

📋 **Task**: Modificați `ex01_broadcast_sender.py` pentru a trimite către o adresă directed broadcast (10.0.0.255) în loc de 255.255.255.255.

**Completați codul**:

```python
# TODO: Schimbați adresa de destinație
BROADCAST_ADDR = "______"  # Care este adresa corectă?
```

✅ **Răspuns așteptat**: Directed broadcast (10.0.0.255) funcționează doar în subrețeaua locală.

### Exercițiul 1.3: Service Discovery Protocol

📋 **Design challenge**: Proiectați un protocol simplu de service discovery cu următoarele caracteristici:

1. Serverul răspunde la cereri broadcast cu informații despre serviciu
2. Clienții colectează răspunsuri de la mai multe servere
3. Clientul alege serverul cu cel mai mic timp de răspuns

**Schelet de implementare** (completați lipsurile):

```python
# Service Discovery Client
import socket
import time

def discover_services(timeout=2.0):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(timeout)
    
    # TODO: Trimiteți cerere de discovery
    discovery_msg = "DISCOVER:SERVICE_TYPE"
    sock.sendto(discovery_msg.encode(), ("255.255.255.255", 12345))
    
    servers = []
    start = time.time()
    
    while time.time() - start < timeout:
        try:
            # TODO: Primiți răspunsuri și măsurați RTT
            data, addr = sock.recvfrom(1024)
            rtt = ______  # Cum calculați RTT?
            servers.append({"addr": addr, "rtt": rtt, "info": data.decode()})
        except socket.timeout:
            break
    
    # TODO: Returnați serverul cu cel mai mic RTT
    return sorted(servers, key=lambda s: ______)
```

---

## 3. Scenariul 2: Chat Multi-Subnet

### Context

Comunicarea între subrețele diferite necesită rutare. Acest scenariu testează funcționarea unui server de chat când clienții sunt în subrețele separate.

### Topologie Extinsă

```
   Subnet A: 10.0.1.0/24          Subnet B: 10.0.2.0/24
   ┌──────────────────┐           ┌──────────────────┐
   │                  │           │                  │
 [h1]──────[s1]─────[r1]────────[s2]──────[h3]      │
10.0.1.1            │ │                  10.0.2.1   │
 (server)      10.0.1.100           10.0.2.100     │
   │              │   │              (gateway)      │
 [h2]─────────────┘   └─────────────────[h4]       │
10.0.1.2                              10.0.2.2     │
 (client)                             (client)     │
   └──────────────────────────────────────────────┘
```

### Exercițiul 2.1: Configurare Server Chat Cross-Subnet

📋 **Pas 1**: Porniți topologia extinsă

```bash
sudo python3 mininet/topologies/topo_extended.py
```

📋 **Pas 2**: Verificați conectivitatea de bază

```
mininet> pingall
```

⚠️ **Rezultat așteptat**: h1 și h2 comunică între ele; h3 și h4 comunică între ele. 
Cross-subnet (h1 ↔ h3) necesită rutare!

📋 **Pas 3**: Verificați rutele pe fiecare host

```
mininet> h1 ip route
mininet> h3 ip route
```

📋 **Întrebare**: Ce rute lipsesc? Cum le adăugați?

**Completați comenzile**:

```bash
# Pe h1 și h2 (pentru a ajunge la 10.0.2.0/24):
h1> ip route add _______ via _______ dev h1-eth0

# Pe h3 și h4 (pentru a ajunge la 10.0.1.0/24):
h3> ip route add _______ via _______ dev h3-eth0
```

### Exercițiul 2.2: Server Chat pe h1, Clienți pe h2 și h3

📋 **Pas 4**: Porniți serverul de chat pe h1

```bash
h1> python3 python/examples/ex02_tcp_chat_server.py
```

📋 **Pas 5**: Conectați clienți din ambele subrețele

```bash
# Din aceeași subrețea (h2):
h2> python3 python/examples/ex02_tcp_chat_client.py 10.0.1.1 12346

# Din subrețeaua diferită (h3):
h3> python3 python/examples/ex02_tcp_chat_client.py 10.0.1.1 12346
```

✅ **Verificare**: Pot ambii clienți să trimită mesaje? Văd fiecare mesajele celuilalt?

📋 **Pas 6**: Capturați traficul pe router

```bash
r1> tcpdump -i any -n port 12346
```

💡 **Observație**: Notați adresele sursă și destinație. Care sunt IP-urile implicate?

### Exercițiul 2.3: Simularea unei Întreruperi de Legătură

📋 **Pas 7**: În timp ce chat-ul funcționează, dezactivați legătura

```
mininet> link s1 r1 down
```

📋 **Întrebări**:
1. Ce se întâmplă cu conexiunile existente?
2. h2 poate trimite în continuare mesaje către h1?
3. h3 poate trimite mesaje?

📋 **Pas 8**: Reactivați legătura

```
mininet> link s1 r1 up
```

📋 **Întrebare**: Conexiunile TCP se refac automat?

---

## 4. Scenariul 3: Multicast Streaming

### Context

Multicast permite transmiterea eficientă a datelor către mai mulți receptori simultan. Acest scenariu simulează un stream de date (ex: prețuri bursiere) către mai mulți clienți.

### Topologie

```
         [sender]
        10.0.0.1
            │
       ┌────┴────┐
       │   s1    │
       └────┬────┘
      ╱     │     ╲
   [r1]   [r2]   [r3]
  10.0.0.2  .3    .4
     │      │      │
  (join) (join) (no join)
  
  Multicast Group: 239.1.2.3
```

### Exercițiul 3.1: Configurare Multicast Basic

📋 **Pas 1**: Pornire topologie de bază

```bash
sudo python3 mininet/topologies/topo_base.py
```

📋 **Pas 2**: Pe h2 și h3, porniți receptori multicast

```bash
# h2 se alătură grupului:
h2> python3 python/examples/ex03_multicast_receiver.py

# h3 se alătură grupului:
h3> python3 python/examples/ex03_multicast_receiver.py
```

📋 **Pas 3**: Pe h1, porniți emițătorul multicast

```bash
h1> python3 python/examples/ex03_multicast_sender.py
```

✅ **Verificare**: Ambii receptori primesc mesajele?

### Exercițiul 3.2: Multicast vs. Broadcast - Comparație Trafic

📋 **Pas 4**: Capturați traficul pe switch în timpul multicast

```bash
s1> tcpdump -i s1-eth1 -c 20 -n
```

📋 **Întrebare**: Comparați numărul de pachete văzute cu scenariul broadcast. Ce diferență observați?

📋 **Task**: Completați tabelul comparativ:

| Caracteristică | Broadcast | Multicast |
|----------------|-----------|-----------|
| Adresă IP destinație | 255.255.255.255 | _________ |
| Adresă MAC destinație | ff:ff:ff:ff:ff:ff | _________ |
| Traversează routere? | _____ | _____ |
| Receptori trebuie să se înregistreze? | _____ | _____ |

### Exercițiul 3.3: Filtrare Mesaje Multicast

📋 **Pas 5**: Folosiți template-ul de filtrare

```bash
h2> python3 python/templates/tpl_multicast_receiver.py --prefix ALERT,ERROR --stats
```

📋 **Modificați sender-ul** pentru a trimite mesaje cu prefixe diferite:

```python
# În ex03_multicast_sender.py, modificați mesajele:
messages = [
    "ALERT:Server overloaded!",
    "INFO:System running normally",
    "ERROR:Connection lost",
    "DEBUG:Variable x = 42",
    "METRIC:CPU=85%"
]
```

✅ **Verificare**: Receptorul afișează doar mesajele cu prefixele filtrate?

---

## 5. Scenariul 4: TCP Tunnel prin Router

### Context

Un TCP tunnel permite encapsularea conexiunilor, util pentru traversarea firewall-urilor sau adăugarea unui layer de securitate.

### Topologie

```
   [client]                [proxy]                [server]
   10.0.1.1               10.0.1.100              10.0.2.1
      │                   / Router \                  │
      │                  /          \                 │
      └────────────[s1]──────[r1]────────[s2]────────┘
                        10.0.1.100  10.0.2.100
                        
   Client ──[TCP]──▶ Proxy ──[TCP]──▶ Server
        (tunel)           (conexiune)
```

### Exercițiul 4.1: Configurare Tunnel Simplu

📋 **Pas 1**: Porniți topologia extinsă

```bash
sudo python3 mininet/topologies/topo_extended.py
```

📋 **Pas 2**: Pe h3 (server final), porniți un echo server

```bash
h3> python3 python/examples/ex05_tcp_echo_server.py 12349
```

📋 **Pas 3**: Pe r1 (router/proxy), porniți tunnel-ul

```bash
r1> python3 python/examples/ex04_tcp_tunnel.py --mode proxy \
    --listen-port 12348 --target 10.0.2.1:12349
```

📋 **Pas 4**: De pe h1 (client), conectați-vă prin tunnel

```bash
h1> python3 python/examples/ex04_tcp_tunnel.py --mode client \
    --proxy 10.0.1.100:12348
```

✅ **Verificare**: Mesajele ajung la server și răspunsurile se întorc?

### Exercițiul 4.2: Analiza Traficului Tunnel

📋 **Pas 5**: Capturați trafic pe ambele segmente

```bash
# Pe segmentul client-proxy (s1):
mininet> s1 tcpdump -i s1-eth3 -n port 12348 -w /tmp/segment1.pcap &

# Pe segmentul proxy-server (s2):
mininet> s2 tcpdump -i s2-eth1 -n port 12349 -w /tmp/segment2.pcap &
```

📋 **Întrebări**:
1. Care sunt adresele IP sursă/destinație pe fiecare segment?
2. Cum se modifică header-ele TCP?

**Completați diagrama**:

```
Segment 1 (client → proxy):
   Src IP: _______     Dst IP: _______
   Src Port: _____     Dst Port: _____

Segment 2 (proxy → server):
   Src IP: _______     Dst IP: _______
   Src Port: _____     Dst Port: _____
```

### Exercițiul 4.3: Tunnel cu Logging

📋 **Task avansată**: Modificați proxy-ul pentru a loga toate mesajele care trec prin el.

```python
# În ex04_tcp_tunnel.py, adăugați logging în forward_data():
def forward_data(src_sock, dst_sock, direction_label):
    data = src_sock.recv(4096)
    if data:
        # TODO: Adăugați logging cu timestamp
        log_entry = f"[{______}] {direction_label}: {len(data)} bytes"
        print(log_entry)
        
        # Opțional: salvați în fișier
        with open("/tmp/tunnel.log", "a") as f:
            f.write(log_entry + "\n")
        
        dst_sock.sendall(data)
```

---

## 6. Scenariul 5: Load Balancing Simplu

### Context

Distribuirea cererilor între mai multe servere îmbunătățește performanța și disponibilitatea.

### Topologie

```
                    ┌────────┐
                    │ client │
                    │10.0.0.1│
                    └───┬────┘
                        │
                   ┌────┴────┐
                   │   s1    │
                   └────┬────┘
                        │
               ┌────────┼────────┐
               │        │        │
          ┌────┴───┐ ┌──┴───┐ ┌──┴───┐
          │server-A│ │srv-B │ │srv-C │
          │10.0.0.2│ │.0.0.3│ │.0.0.4│
          └────────┘ └──────┘ └──────┘
```

### Exercițiul 5.1: Round-Robin Manual

📋 **Pas 1**: Porniți topologia și serverele

```bash
sudo python3 mininet/topologies/topo_base.py

# Porniți 3 servere echo pe porturi diferite:
h2> python3 -c "
import socket
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('', 12350))
s.listen(5)
while True:
    c, a = s.accept()
    c.send(b'Response from SERVER-A\n')
    c.close()
" &

# Similar pentru h3 și h4...
```

📋 **Pas 2**: Implementați un client round-robin

```python
# load_balance_client.py - Completați
import socket

SERVERS = [
    ("10.0.0.2", 12350),
    ("10.0.0.3", 12350),
    ("10.0.0.4", 12350),
]

current_index = 0

def get_next_server():
    global current_index
    server = SERVERS[______]  # Care este indexul?
    current_index = ______    # Cum actualizați pentru round-robin?
    return server

def make_request():
    server = get_next_server()
    sock = socket.socket()
    sock.connect(server)
    response = sock.recv(1024)
    sock.close()
    return server, response

# Test: 9 cereri ar trebui distribuite 3-3-3
for i in range(9):
    srv, resp = make_request()
    print(f"Request {i+1}: {srv} -> {resp.decode().strip()}")
```

### Exercițiul 5.2: Health Checking

📋 **Task**: Adăugați verificare de sănătate înainte de a trimite cereri

```python
def is_server_healthy(server, timeout=0.5):
    """Verifică dacă serverul răspunde."""
    try:
        sock = socket.socket()
        sock.settimeout(timeout)
        sock.connect(server)
        sock.close()
        return True
    except:
        return False

def get_next_healthy_server():
    """Returnează următorul server sănătos (sau None)."""
    for _ in range(len(SERVERS)):
        server = get_next_server()
        if is_server_healthy(server):
            return server
    return None  # Toate serverele sunt down
```

📋 **Test**: Opriți unul dintre servere și verificați că traficul este redistribuit.

---

## 7. Scenariul 6: Packet Capture și Analiză

### Context

Abilitatea de a captura și analiza pachete este esențială pentru debugging și înțelegerea protocoalelor.

### Exercițiul 6.1: Captura TCP Handshake

📋 **Pas 1**: Pregătiți captura

```bash
# Pe switch sau host:
mininet> s1 tcpdump -i s1-eth1 -n tcp port 12346 -w /tmp/handshake.pcap &
```

📋 **Pas 2**: Inițiați o conexiune TCP

```bash
# Server:
h2> python3 -c "import socket; s=socket.socket(); s.bind(('',12346)); s.listen(); s.accept()"

# Client (în alt terminal):
h1> python3 -c "import socket; s=socket.socket(); s.connect(('10.0.0.2',12346))"
```

📋 **Pas 3**: Analizați captura

```bash
$ tcpdump -r /tmp/handshake.pcap -n
```

✅ **Identificați**:

| Pachet # | Flags | Seq | Ack | Descriere |
|----------|-------|-----|-----|-----------|
| 1 | _____ | X | 0 | Client → Server |
| 2 | _____ | Y | X+1 | Server → Client |
| 3 | _____ | X+1 | Y+1 | Client → Server |

### Exercițiul 6.2: Comparație TCP vs UDP

📋 **Task**: Capturați trafic UDP și comparați cu TCP

```bash
# UDP - doar datagram-uri, fără handshake
mininet> s1 tcpdump -i s1-eth1 -n udp port 12345 -c 5

# Trimiteți un mesaj UDP:
h1> echo "test" | nc -u 10.0.0.2 12345
```

📋 **Completați tabelul**:

| Aspect | TCP | UDP |
|--------|-----|-----|
| Pachete pentru stabilire conexiune | ____ | ____ |
| Overhead per mesaj | ____ bytes | ____ bytes |
| Garanție livrare | _____ | _____ |
| Ordine păstrată | _____ | _____ |

---

## 8. Scenariul 7: Network Partition și Recovery

### Context

Rețelele pot suferi întreruperi. Înțelegerea comportamentului aplicațiilor în astfel de situații este crucială.

### Exercițiul 7.1: Simularea unei Partiții

📋 **Pas 1**: Porniți topologia și stabiliți conexiuni

```bash
sudo python3 mininet/topologies/topo_extended.py

# Server pe h3:
h3> python3 python/examples/ex02_tcp_chat_server.py

# Client pe h1:
h1> python3 python/examples/ex02_tcp_chat_client.py 10.0.2.1 12346
```

📋 **Pas 2**: Creați partiția de rețea

```
mininet> link s1 r1 down
```

📋 **Pas 3**: Observați comportamentul

```bash
# Încercați să trimiteți un mesaj:
# Ce se întâmplă?
```

📋 **Întrebări**:
1. Conexiunea TCP este întreruptă imediat?
2. După cât timp expiră?
3. Ce eroare primește clientul?

📋 **Pas 4**: Restaurați legătura

```
mininet> link s1 r1 up
```

📋 **Întrebare**: Conexiunea existentă se recuperează?

### Exercițiul 7.2: Implementare Reconnect Logic

📋 **Task**: Modificați clientul pentru a încerca reconectarea

```python
# Adăugați în client:
import time

MAX_RETRIES = 5
RETRY_DELAY = 2  # secunde

def connect_with_retry(host, port):
    for attempt in range(MAX_RETRIES):
        try:
            sock = socket.socket()
            sock.connect((host, port))
            print(f"Connected on attempt {attempt + 1}")
            return sock
        except ConnectionRefusedError:
            print(f"Attempt {attempt + 1} failed, retrying in {RETRY_DELAY}s...")
            time.sleep(RETRY_DELAY)
    raise Exception("Could not connect after max retries")
```

---

## 9. Exerciții de Autoevaluare

### Nivel 1: Fundamentale

**E1.1**: Ce opțiune socket este necesară pentru a trimite broadcast UDP?

```python
sock.setsockopt(socket.SOL_SOCKET, socket._______, 1)
```

**E1.2**: Care este diferența între `bind()` și `connect()` pentru un socket UDP?

**E1.3**: De ce trebuie un server TCP să apeleze `listen()` înainte de `accept()`?

### Nivel 2: Aplicație

**E2.1**: Implementați un "ping-pong" TCP unde:
- Serverul răspunde cu "PONG" la orice mesaj "PING"
- Clientul trimite 10 mesaje PING și măsoară RTT-ul fiecăruia

**E2.2**: Modificați ex03_multicast pentru a implementa un sistem de vot:
- Sender-ul întreabă "Care e limbajul favorit: Python, Java, C++?"
- Receiverii răspund cu alegerea lor (tot pe multicast)
- La final, sender-ul afișează rezultatele

### Nivel 3: Avansate

**E3.1**: Implementați un protocol de heartbeat:
- Serverul trimite mesaje periodice "ALIVE" pe multicast
- Clienții detectează când un server "dispare" (3 mesaje lipsă)

**E3.2**: Creați un sistem de chat P2P (fără server central):
- Fiecare participant ascultă pe multicast pentru mesaje
- Descoperirea participanților prin broadcast periodic
- Mesajele directe via unicast TCP

---

## 10. Grile de Verificare

### Checklist Pre-Laborator

- [ ] Mininet instalat și funcțional (`sudo mn --test pingall`)
- [ ] Python 3.8+ disponibil
- [ ] tcpdump/tshark instalat
- [ ] Fișierele exemplu accesibile

### Checklist Post-Scenariu

După fiecare scenariu, verificați că puteți:

**Scenariul 1**:
- [ ] Explica diferența broadcast vs. unicast
- [ ] Configura SO_BROADCAST pe un socket UDP
- [ ] Identifica adresa broadcast a unei subrețele

**Scenariul 2**:
- [ ] Configura rute statice între subrețele
- [ ] Depana probleme de conectivitate cross-subnet
- [ ] Înțelege rolul gateway-ului implicit

**Scenariul 3**:
- [ ] Alătura un socket la un grup multicast
- [ ] Explica avantajele multicast față de broadcast
- [ ] Identifica o adresă MAC multicast

**Scenariul 4**:
- [ ] Implementa un proxy TCP simplu
- [ ] Analiza traficul pe segmente diferite
- [ ] Înțelege conceptul de NAT (similar cu tunnel)

**Scenariul 5**:
- [ ] Implementa round-robin load balancing
- [ ] Adăuga health checks pentru servere
- [ ] Gestiona failover când un server cade

**Scenariul 6**:
- [ ] Captura pachete cu tcpdump
- [ ] Identifica fazele TCP handshake
- [ ] Compara overhead TCP vs UDP

**Scenariul 7**:
- [ ] Simula o întrerupere de rețea în Mininet
- [ ] Observa comportamentul TCP la timeout
- [ ] Implementa logic de reconectare

---

## Anexă: Comenzi Utile

### Mininet

```bash
# Pornire cu cleanup automat:
sudo mn -c && sudo python3 topo_base.py

# Afișare informații topologie:
mininet> net
mininet> dump

# Deschidere terminal pentru host:
mininet> xterm h1

# Execuție comandă pe host:
mininet> h1 ping -c 3 h2

# Manipulare legături:
mininet> link s1 s2 down   # Dezactivare
mininet> link s1 s2 up     # Reactivare

# Ieșire:
mininet> exit
```

### tcpdump

```bash
# Capturare tot traficul pe interfață:
tcpdump -i eth0

# Filtrare după port:
tcpdump -i eth0 port 12345

# Filtrare după protocol:
tcpdump -i eth0 tcp
tcpdump -i eth0 udp

# Afișare conținut pachete:
tcpdump -i eth0 -X

# Salvare în fișier:
tcpdump -i eth0 -w capture.pcap

# Citire din fișier:
tcpdump -r capture.pcap
```

### Python Socket Debugging

```python
# Afișare opțiuni socket:
import socket
sock = socket.socket()
print(sock.getsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR))

# Verificare port ocupat:
import socket
def is_port_free(port):
    sock = socket.socket()
    try:
        sock.bind(('', port))
        sock.close()
        return True
    except OSError:
        return False
```

---

## Contribuții și Feedback

Acest document este parte din kit-ul S3 pentru cursul "Rețele de Calculatoare" la ASE-CSIE. Pentru sugestii sau corecturi, contactați echipa didactică.

**Versiune**: 1.0
**Ultima actualizare**: Decembrie 2025
