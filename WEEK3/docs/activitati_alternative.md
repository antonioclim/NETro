# Activități alternative

Pentru cine învață mai bine altfel decât scriind cod de la zero.

---

## Parsons Problems

Liniile sunt amestecate. Pune-le în ordine.

### P1: Broadcast receiver

```
A) data, addr = sock.recvfrom(1024)
B) sock.bind(('', 5301))
C) import socket
D) sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
E) sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
F) print(data.decode())
```

Ordine: ___ ___ ___ ___ ___ ___

<details>
<summary>Răspuns</summary>
C, D, E, B, A, F

Logica: import → creare socket → opțiuni → bind → primire → afișare
</details>

### P2: Multicast receiver

```
A) sock.bind(('', 5302))
B) mreq = struct.pack("4sl", socket.inet_aton(GRUP), socket.INADDR_ANY)
C) import socket, struct
D) sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
E) GRUP = '224.1.1.1'
F) sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
G) data = sock.recvfrom(1024)
```

Ordine: ___ ___ ___ ___ ___ ___ ___

<details>
<summary>Răspuns</summary>
C, E, F, A, B, D, G

ATENȚIE: A (bind) vine ÎNAINTE de D (JOIN). Asta-i capcana.
</details>

### P3: Forward function pentru tunnel

```
A) dst.sendall(data)
B) def forward(src, dst):
C)     while True:
D)         data = src.recv(4096)
E)         if not data: break
F)     src.close()
G)     dst.close()
```

Ordine: ___ ___ ___ ___ ___ ___ ___

<details>
<summary>Răspuns</summary>
B, C, D, E, A, F, G

Ordinea în buclă: recv → verifică dacă gol → send. Close-urile la final.
</details>

---

## Tracing

Urmărește execuția și determină ce se afișează.

### T1: Ce afișează?

```python
import socket
s1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print(s1.type, s2.type)
```

Răspuns: ___ ___

<details>
<summary>Răspuns</summary>
2 1

SOCK_DGRAM = 2 (UDP), SOCK_STREAM = 1 (TCP)
</details>

### T2: Cine primește ce?

Timeline:
```
0:00  h2 pornește receiver, bind :5302
0:01  h2 face JOIN 224.1.1.1
0:02  h1 trimite "A" la 224.1.1.1:5302
0:03  h3 pornește receiver, bind :5302 (FĂRĂ JOIN)
0:04  h1 trimite "B"
0:05  h3 face JOIN
0:06  h1 trimite "C"
```

h2 primește: ___
h3 primește: ___

<details>
<summary>Răspuns</summary>
h2: A, B, C (toate — era în grup de la început)
h3: doar C (a făcut JOIN la 0:05, deci A și B s-au pierdut)
</details>

### T3: Output tunnel

```python
def forward(src, dst, name):
    while True:
        data = src.recv(4096)
        print(f"[{name}] got: {len(data) if data else 0}")
        if not data: break
        dst.sendall(data)
```

Clientul trimite "Hello" (5 bytes) și apoi închide conexiunea.

Ce se afișează?
```
[C->S] got: ___
[C->S] got: ___
```

<details>
<summary>Răspuns</summary>
```
[C->S] got: 5
[C->S] got: 0
```

Prima iterație: primește "Hello" (5 bytes)
A doua iterație: conexiune închisă → recv returnează b'' → len = 0 → break
</details>

---

## Debugging

Fiecare cod are bug-uri. Găsește-le.

### D1: Broadcast sender

```python
import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.sendto(b"Test", ('255.255.255.255', 5301))
```

Bug: _______________
Fix: _______________

<details>
<summary>Răspuns</summary>
Bug: Lipsește SO_BROADCAST
Fix: Adaugă `sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)` înainte de sendto
</details>

### D2: Multicast receiver

```python
import socket, struct
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
mreq = struct.pack("4sl", socket.inet_aton('224.1.1.1'), socket.INADDR_ANY)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
sock.bind(('', 5302))
data = sock.recvfrom(1024)
```

Bug: _______________
Fix: _______________

<details>
<summary>Răspuns</summary>
Bug: bind() e DUPĂ JOIN, ar trebui să fie invers
Fix: Mută `sock.bind(('', 5302))` ÎNAINTE de setsockopt pentru JOIN
</details>

### D3: Server TCP

```python
import socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('', 9090))
server.listen(5)
# După Ctrl+C și repornire: "Address already in use"
```

Bug: _______________
Fix: _______________

<details>
<summary>Răspuns</summary>
Bug: Lipsește SO_REUSEADDR
Fix: Adaugă `server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)` înainte de bind
</details>

### D4: Tunnel cu un thread

```python
def tunnel_broken(client, server):
    while True:
        data = client.recv(1024)
        server.sendall(data)
        response = server.recv(1024)
        client.sendall(response)
```

Bug: _______________
Simptom: _______________
Fix: _______________

<details>
<summary>Răspuns</summary>
Bug: Un singur thread pentru comunicare bidirecțională
Simptom: Se blochează dacă server-ul trimite înainte ca clientul să trimită
Fix: Folosește 2 thread-uri separate, unul pentru fiecare direcție
</details>

---

## Completare diagrame

### Completează opțiunile socket

```
Broadcast sender:  setsockopt(SOL_SOCKET, __________, 1)
Multicast sender:  setsockopt(IPPROTO_IP, __________, ttl)
Multicast recv:    setsockopt(IPPROTO_IP, __________, mreq)
TCP reuse:         setsockopt(SOL_SOCKET, __________, 1)
```

<details>
<summary>Răspunsuri</summary>
SO_BROADCAST
IP_MULTICAST_TTL
IP_ADD_MEMBERSHIP
SO_REUSEADDR
</details>

### Completează fluxul

```
BROADCAST:  socket → ________ → sendto(255.255.255.255)

MULTICAST RECV: socket → ________ → ________ → recvfrom

TCP TUNNEL: accept → connect_to_target → start __ threads
```

<details>
<summary>Răspunsuri</summary>
SO_BROADCAST
bind, JOIN (IP_ADD_MEMBERSHIP)
2
</details>

---

## Quick match

Trage linii între problemă și cauză:

```
PermissionError la broadcast     •     • Ordinea bind/JOIN greșită
Nu primesc multicast             •     • Lipsește SO_BROADCAST
Address already in use           •     • Un singur thread pentru bidirecțional
Tunnel blocat                    •     • Lipsește SO_REUSEADDR
```

<details>
<summary>Răspunsuri</summary>
PermissionError → SO_BROADCAST
Nu primesc multicast → Ordinea bind/JOIN
Address already in use → SO_REUSEADDR
Tunnel blocat → Un singur thread
</details>

---

## Bifează ce ai completat

□ Parsons P1, P2, P3
□ Tracing T1, T2, T3
□ Debug D1, D2, D3, D4
□ Diagrame
□ Quick match

Dacă ai făcut toate, ar trebui să te simți confortabil la laborator.

---

Exerciții pentru studenții care preferă să analizeze cod existent înainte să scrie de la zero.
