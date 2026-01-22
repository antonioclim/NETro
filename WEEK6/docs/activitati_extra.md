# Activități Extra – Săptămâna 6
## Parsons Problems, Trace Exercises, Code Reading

**Disciplina:** Rețele de calculatoare  
**Săptămâna:** 6  
**Scop:** Activități complementare pentru consolidarea înțelegerii (nu doar scriere de cod)

Aceste exerciții vizează nivelurile UNDERSTAND și ANALYSE din taxonomia Bloom, oferind varietate față de exercițiile clasice de implementare.

---

## Partea A: Parsons Problems (Reordonare)

În aceste exerciții, liniile de cod/comenzi sunt date în ordine aleatorie. Scopul este să le reordonezi corect.

---

### Parsons 1: Configurare NAT pe router Linux

**Context:** Trebuie să configurezi un router Linux pentru a face NAT/MASQUERADE pentru rețeaua internă 192.168.1.0/24 către interfața externă eth1.

**Linii de reordonat:**
```
___ iptables -t nat -A POSTROUTING -s 192.168.1.0/24 -o eth1 -j MASQUERADE
___ echo 1 > /proc/sys/net/ipv4/ip_forward
___ iptables -A FORWARD -i eth0 -o eth1 -j ACCEPT
___ iptables -A FORWARD -i eth1 -o eth0 -m state --state RELATED,ESTABLISHED -j ACCEPT
```

**Ordinea corectă:** ___  ___  ___  ___

<details>
<summary>💡 Click pentru răspuns</summary>

**Ordine corectă:** 2, 1, 3, 4

```bash
# 1. Mai întâi activăm IP forwarding (altfel pachetele nu sunt rutate)
echo 1 > /proc/sys/net/ipv4/ip_forward

# 2. Apoi configurăm traducerea NAT
iptables -t nat -A POSTROUTING -s 192.168.1.0/24 -o eth1 -j MASQUERADE

# 3. Permitem traficul forward din intern spre extern
iptables -A FORWARD -i eth0 -o eth1 -j ACCEPT

# 4. Permitem răspunsurile să revină
iptables -A FORWARD -i eth1 -o eth0 -m state --state RELATED,ESTABLISHED -j ACCEPT
```

**De ce contează ordinea:** IP forwarding trebuie activat ÎNAINTE de reguli, altfel kernel-ul nu procesează pachetele care nu sunt pentru el.
</details>

---

### Parsons 2: Debugging conectivitate rețea

**Context:** Conexiunea nu funcționează. Care este ordinea corectă de diagnostic?

**Pași de reordonat:**
```
___ ping gateway-ul implicit
___ verifică interfața locală (ip addr)
___ ping serverul DNS
___ ping localhost (127.0.0.1)
___ ping adresa externă (8.8.8.8)
___ verifică rezoluția DNS (nslookup example.com)
```

**Ordinea corectă:** ___  ___  ___  ___  ___  ___

<details>
<summary>💡 Click pentru răspuns</summary>

**Ordine corectă:** 4, 2, 1, 5, 3, 6

```bash
# 1. Verifică că stack-ul TCP/IP local funcționează
ping localhost (127.0.0.1)

# 2. Verifică interfața de rețea
verifică interfața locală (ip addr)

# 3. Verifică conectivitatea la nivel L2/L3 local
ping gateway-ul implicit

# 4. Verifică conectivitatea externă
ping adresa externă (8.8.8.8)

# 5. Verifică accesul la servicii DNS
ping serverul DNS

# 6. Verifică rezoluția de nume
verifică rezoluția DNS (nslookup example.com)
```

**Principiu:** Debugging de la "aproape" la "departe", de la L1 la L7.
</details>

---

### Parsons 3: Secvența DHCP DORA

**Context:** Un client nou se conectează la rețea. Pune în ordine mesajele DHCP.

**Mesaje de reordonat:**
```
___ Client trimite DHCP Request (broadcast) confirmând alegerea
___ Server trimite DHCP Offer cu IP și parametri propuși
___ Server trimite DHCP Acknowledge confirmând lease-ul
___ Client trimite DHCP Discover (broadcast) căutând servere
```

**Ordinea corectă:** ___  ___  ___  ___

<details>
<summary>💡 Click pentru răspuns</summary>

**Ordine corectă:** 4, 2, 1, 3 (DORA)

```
D - Discover: Client → Broadcast "Există vreun server DHCP?"
O - Offer:    Server → Client "Îți ofer IP-ul X"
R - Request:  Client → Broadcast "Accept oferta de la server Y"
A - Ack:      Server → Client "Confirmat, lease 24h"
```

**De ce Request e broadcast?** Pentru că pot fi mai multe servere DHCP, iar clientul anunță pe toți care ofertă a acceptat.
</details>

---

### Parsons 4: Instalare flow OpenFlow

**Context:** Controller-ul SDN instalează un flow pentru a permite traficul de la h1 la h2.

**Pași de reordonat:**
```
___ Controller trimite FlowMod către switch
___ Switch adaugă regula în flow table
___ Controller primește PacketIn pentru pachet necunoscut
___ Pachetele ulterioare h1→h2 sunt procesate direct de switch
___ Pachet ajunge la switch, nu există flow potrivit
___ Controller decide: permite traficul, calculează portul de ieșire
```

**Ordinea corectă:** ___  ___  ___  ___  ___  ___

<details>
<summary>💡 Click pentru răspuns</summary>

**Ordine corectă:** 5, 3, 6, 1, 2, 4

```
1. Pachet ajunge la switch, nu există flow potrivit → table-miss
2. Controller primește PacketIn pentru pachet necunoscut
3. Controller decide: permite traficul, calculează portul de ieșire
4. Controller trimite FlowMod către switch (instalează regula)
5. Switch adaugă regula în flow table
6. Pachetele ulterioare h1→h2 sunt procesate direct de switch
```

**Observație:** Primul pachet e lent (latență controller), următoarele sunt rapide.
</details>

---

## Partea B: Trace Exercises (Urmărire Execuție)

În aceste exerciții, urmărești un pachet sau o comandă și completezi valorile lipsă.

---

### Trace 1: Pachet HTTP prin NAT

**Configurație:**
- h1: 192.168.1.50 (client, rețea privată)
- Router NAT: eth0=192.168.1.1 (intern), eth1=203.0.113.1 (extern)
- Server web: 93.184.216.34:80

**Completează tabelul pentru un pachet HTTP de la h1:**

| Punct | IP Sursă | Port Sursă | IP Dest | Port Dest |
|-------|----------|------------|---------|-----------|
| 1. h1 trimite | 192.168.1.50 | 54321 | _________ | 80 |
| 2. După NAT (ieșire) | _________ | _________ | 93.184.216.34 | 80 |
| 3. Răspuns server | 93.184.216.34 | 80 | _________ | _________ |
| 4. După NAT (intrare) | 93.184.216.34 | 80 | _________ | _________ |

<details>
<summary>💡 Click pentru răspuns</summary>

| Punct | IP Sursă | Port Sursă | IP Dest | Port Dest |
|-------|----------|------------|---------|-----------|
| 1. h1 trimite | 192.168.1.50 | 54321 | **93.184.216.34** | 80 |
| 2. După NAT (ieșire) | **203.0.113.1** | **40001** (alocat de NAT) | 93.184.216.34 | 80 |
| 3. Răspuns server | 93.184.216.34 | 80 | **203.0.113.1** | **40001** |
| 4. După NAT (intrare) | 93.184.216.34 | 80 | **192.168.1.50** | **54321** |

**Observații:**
- NAT modifică IP-ul sursă și portul sursă la ieșire
- Destinația rămâne neschimbată
- La intrare, procesul invers
</details>

---

### Trace 2: Rezoluție ARP

**Configurație:**
- h1: 192.168.1.10, MAC aa:aa:aa:aa:aa:aa
- h2: 192.168.1.20, MAC bb:bb:bb:bb:bb:bb
- Gateway: 192.168.1.1, MAC cc:cc:cc:cc:cc:cc

**Scenariu:** h1 vrea să comunice cu h2 (prima dată, ARP cache gol)

**Completează câmpurile lipsă:**

```
Pas 1: h1 trimite ARP Request
  Sender MAC: aa:aa:aa:aa:aa:aa
  Sender IP:  192.168.1.10
  Target MAC: _________________  (ce valoare?)
  Target IP:  _________________
  Destination MAC (L2): _________________  (broadcast sau unicast?)

Pas 2: h2 răspunde cu ARP Reply
  Sender MAC: _________________
  Sender IP:  _________________
  Target MAC: aa:aa:aa:aa:aa:aa
  Target IP:  192.168.1.10
  Destination MAC (L2): _________________  (broadcast sau unicast?)
```

<details>
<summary>💡 Click pentru răspuns</summary>

```
Pas 1: h1 trimite ARP Request
  Sender MAC: aa:aa:aa:aa:aa:aa
  Sender IP:  192.168.1.10
  Target MAC: 00:00:00:00:00:00  (necunoscut - de aceea întreabă!)
  Target IP:  192.168.1.20
  Destination MAC (L2): ff:ff:ff:ff:ff:ff  (BROADCAST)

Pas 2: h2 răspunde cu ARP Reply
  Sender MAC: bb:bb:bb:bb:bb:bb
  Sender IP:  192.168.1.20
  Target MAC: aa:aa:aa:aa:aa:aa
  Target IP:  192.168.1.10
  Destination MAC (L2): aa:aa:aa:aa:aa:aa  (UNICAST direct la h1)
```

**Observații:**
- ARP Request: broadcast (toți primesc)
- ARP Reply: unicast (doar cine a întrebat)
</details>

---

### Trace 3: Flow table SDN

**Configurație:**
- h1: 10.0.10.1, port 1
- h2: 10.0.10.2, port 2
- h3: 10.0.10.3, port 3

**Flow table inițială:**
```
priority=0   match=*                    actions=CONTROLLER
priority=10  match=ip,dst=10.0.10.2     actions=output:2
priority=10  match=ip,dst=10.0.10.1     actions=output:1
priority=30  match=ip,dst=10.0.10.3     actions=drop
```

**Completează ce se întâmplă cu fiecare pachet:**

| Pachet | Sursă | Dest | Regula potrivită | Acțiune |
|--------|-------|------|------------------|---------|
| A | 10.0.10.1 | 10.0.10.2 | _______ | _______ |
| B | 10.0.10.1 | 10.0.10.3 | _______ | _______ |
| C | 10.0.10.2 | 8.8.8.8 | _______ | _______ |
| D | 10.0.10.3 | 10.0.10.1 | _______ | _______ |

<details>
<summary>💡 Click pentru răspuns</summary>

| Pachet | Sursă | Dest | Regula potrivită | Acțiune |
|--------|-------|------|------------------|---------|
| A | 10.0.10.1 | 10.0.10.2 | priority=10, dst=10.0.10.2 | **output:2** (PERMIT) |
| B | 10.0.10.1 | 10.0.10.3 | priority=30, dst=10.0.10.3 | **drop** (BLOCK) |
| C | 10.0.10.2 | 8.8.8.8 | priority=0, * | **CONTROLLER** (necunoscut) |
| D | 10.0.10.3 | 10.0.10.1 | priority=10, dst=10.0.10.1 | **output:1** (PERMIT) |

**Observații:**
- Regula cu priority mai mare câștigă
- Pachetul C nu are flow specific, merge la controller
- h3 poate trimite CĂTRE h1, dar nu poate primi (asimetrie)
</details>

---

## Partea C: Code Reading (Analiză Cod Existent)

---

### Code Reading 1: Ce face acest cod?

```python
import socket

def mystery(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(2)
    try:
        sock.sendto(b"ping", (host, port))
        data, addr = sock.recvfrom(1024)
        return True, addr
    except socket.timeout:
        return False, None
    finally:
        sock.close()
```

**Întrebări:**
1. Ce tip de socket folosește? TCP sau UDP?
2. Ce face funcția `mystery`?
3. De ce are timeout?
4. Ce returnează dacă serverul nu răspunde?

<details>
<summary>💡 Click pentru răspuns</summary>

1. **UDP** (SOCK_DGRAM)
2. Trimite un mesaj "ping" la host:port și așteaptă răspuns - este un **UDP ping simplu**
3. Timeout-ul previne blocarea infinită dacă serverul nu răspunde (UDP nu are ACK implicit)
4. Returnează `(False, None)` - indică că nu s-a primit răspuns
</details>

---

### Code Reading 2: Găsește bug-ul

```python
def start_server(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('0.0.0.0', port))
    
    while True:
        conn, addr = sock.accept()
        data = conn.recv(1024)
        conn.send(data)  # echo
        conn.close()
```

**Întrebări:**
1. Ce face acest server?
2. Ce lipsește pentru ca serverul să funcționeze?
3. Ce se întâmplă dacă repornești serverul imediat după oprire?

<details>
<summary>💡 Click pentru răspuns</summary>

1. Este un **echo server TCP** - primește date și le trimite înapoi
2. Lipsește `sock.listen(N)` între `bind()` și `accept()` - va da eroare!
3. Va da eroare "Address already in use" - lipsește `sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)`

**Cod corectat:**
```python
def start_server(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # FIX 1
    sock.bind(('0.0.0.0', port))
    sock.listen(5)  # FIX 2
    
    while True:
        conn, addr = sock.accept()
        data = conn.recv(1024)
        conn.send(data)
        conn.close()
```
</details>

---

### Code Reading 3: Analiza regulă iptables

```bash
iptables -t nat -A PREROUTING -i eth0 -p tcp --dport 80 -j REDIRECT --to-port 8080
```

**Întrebări:**
1. Pe ce tabelă acționează?
2. Pe ce chain?
3. Ce trafic potrivește?
4. Ce efect are regula?
5. Unde ar fi utilă această regulă?

<details>
<summary>💡 Click pentru răspuns</summary>

1. **Tabela nat** (-t nat)
2. **Chain PREROUTING** - procesează pachetele ÎNAINTE de decizia de rutare
3. **TCP către portul 80** care intră pe interfața eth0
4. **Redirecționează traficul local** de pe portul 80 la portul 8080
5. Util pentru:
   - Transparent proxy (ex: squid)
   - Rulare server web ca non-root (8080) dar accesibil pe portul standard (80)
   - Interceptarea traficului HTTP pentru inspecție
</details>

---

## Partea D: Debugging Exercises

---

### Debug 1: NAT nu funcționează

**Simptome:** h1 (192.168.1.10) nu poate face ping la serverul extern (8.8.8.8)

**Output diagnostic:**

```bash
# Pe h1:
$ ping -c 1 192.168.1.1
PING 192.168.1.1: 64 bytes, time=0.5ms  # OK

$ ping -c 1 8.8.8.8
PING 8.8.8.8: Request timeout  # FAIL

# Pe router:
$ ip addr
eth0: 192.168.1.1/24
eth1: 203.0.113.1/24

$ sysctl net.ipv4.ip_forward
net.ipv4.ip_forward = 0

$ iptables -t nat -L -n
Chain POSTROUTING (policy ACCEPT)
target   prot  source         destination
MASQUERADE  all  192.168.1.0/24  0.0.0.0/0
```

**Întrebare:** Care este problema și cum o rezolvi?

<details>
<summary>💡 Click pentru răspuns</summary>

**Problema:** `ip_forward = 0` - IP forwarding este DEZACTIVAT!

Chiar dacă regula MASQUERADE există, kernel-ul nu forwardează pachetele care nu sunt pentru el.

**Soluție:**
```bash
sysctl -w net.ipv4.ip_forward=1
# sau
echo 1 > /proc/sys/net/ipv4/ip_forward
```

**Permanent (în /etc/sysctl.conf):**
```
net.ipv4.ip_forward = 1
```
</details>

---

### Debug 2: SDN - pachete pierdute

**Simptome:** h1 poate comunica cu h2, dar primul ping durează 2-3 secunde

**Output diagnostic:**

```bash
# Flow table:
$ ovs-ofctl dump-flows s1
priority=0  actions=CONTROLLER

# Controller log:
PacketIn: 10.0.10.1 → 10.0.10.2 (ICMP)
Installing flow: 10.0.10.1 → 10.0.10.2, output:2
PacketIn: 10.0.10.2 → 10.0.10.1 (ICMP)
Installing flow: 10.0.10.2 → 10.0.10.1, output:1
```

**Întrebare:** De ce primul ping e lent dar următoarele sunt rapide?

<details>
<summary>💡 Click pentru răspuns</summary>

**Cauza:** Comportament normal pentru SDN reactiv!

1. **Primul pachet:** Nu există flow → PacketIn către controller → Controller decide → FlowMod instalat → Pachetul este trimis
2. **Pachetele ulterioare:** Flow există în switch → procesare rapidă (data plane only)

**Latența primului pachet** include:
- Timpul de trimitere PacketIn la controller
- Procesarea în controller (decizie, lookup)
- Timpul de trimitere FlowMod înapoi
- Instalarea flow-ului în switch

**Nu e bug, e feature!** Dar pentru aplicații sensibile la latență, se pot pre-instala flow-uri (proactiv în loc de reactiv).
</details>

---

## Sumar: Cum să folosești aceste exerciții

| Tip exercițiu | Ce dezvoltă | Când să-l folosești |
|---------------|-------------|---------------------|
| Parsons | Înțelegerea secvenței și dependențelor | După prezentarea conceptului, înainte de implementare |
| Trace | Capacitatea de a urmări execuția pas cu pas | Pentru concepte cu multiple transformări (NAT, SDN) |
| Code Reading | Analiza și înțelegerea codului existent | Înainte de debugging, pentru code review |
| Debugging | Diagnosticare sistematică | După ce studenții au încercat implementarea |

**Timp estimat:** 30-45 minute pentru toate exercițiile (sau selectează subset-ul relevant)

---

*Revolvix&Hypotheticalandrei*
