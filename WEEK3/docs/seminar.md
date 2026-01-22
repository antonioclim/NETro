# Seminar 3: Demonstrații practice — Broadcast, Multicast, Tunnel

2 ore | Demonstrații live + experimente ghidate

---

## Cum funcționează seminarul

Fiecare experiment urmează același pattern:
1. Faci o predicție ÎNAINTE să rulezi
2. Rulezi și observi
3. Compari cu predicția
4. Reflectezi ce te-a surprins

De ce? Pentru că învățarea pasivă ("am văzut cum merge") nu se lipește. Când faci predicții și greșești, asta rămâne în memorie.

---

## Check-in rapid (2 min)

Înainte să începem:

Cât de confortabil ești cu socket-uri? (încercuiește)
```
1         2         3         4         5
Nu am     Am citit  Am făcut  Merg      Pot să
folosit   despre    un        bine      scriu din
niciodată ele       tutorial            memorie
```

Ai lucrat cu threading în Python? □ Da □ Nu

Asta mă ajută să știu unde să insist.

---

## Setup

```bash
cd ~/WEEK3
sudo python3 mininet/topologies/topo_base.py
```

Topologia: h1 (10.0.3.1) — switch — h2 (10.0.3.2) — h3 (10.0.3.3)

Verificare: `pingall` în prompt-ul mininet.

---

## Experimentul 1: Broadcast

### Predicție #1

Scrie răspunsul ÎNAINTE să rulezi.

> h1 trimite broadcast la 255.255.255.255:5301. Câte host-uri primesc?

- [ ] A) Niciunul (broadcast dezactivat implicit)
- [ ] B) Doar h2 (primul vecin)
- [ ] C) h2 și h3 (toată subrețeaua)
- [ ] D) h1, h2, h3 (inclusiv sender-ul)

Răspunsul meu: ____

### Rulare

Terminal h2:
```python
import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(('', 5301))
print("Aștept...")
data, addr = sock.recvfrom(1024)
print(f"Primit de la {addr}: {data}")
```

Terminal h3: același cod.

Terminal h1:
```python
import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
sock.sendto(b"Hello!", ('255.255.255.255', 5301))
```

### Verificare

Răspuns corect: **C** — h2 și h3 primesc.

Ai ghicit? □ Da □ Nu

Dacă nu, de ce crezi că ai greșit?
_________________________________

---

### Predicție #2

> Ce se întâmplă dacă NU pui SO_BROADCAST pe sender?

- [ ] A) Funcționează normal
- [ ] B) PermissionError
- [ ] C) Mesajul ajunge doar local
- [ ] D) Timeout

Răspunsul meu: ____

### Experiment

Comentează linia cu SO_BROADCAST și rulează din nou.

Răspuns corect: **B** — PermissionError.

### Reflecție Broadcast (2 min)

Ce m-a surprins la broadcast:
_________________________________

Ce credeam înainte și s-a dovedit greșit:
_________________________________

---

## Experimentul 2: Multicast

### Predicție #3

> h3 NU face JOIN la grupul 224.1.1.1, doar bind pe port. h2 face JOIN. Cine primește mesajele?

- [ ] A) Ambii (sunt pe același port)
- [ ] B) Doar h2 (e în grup)
- [ ] C) Niciunul
- [ ] D) Depinde de TTL

Răspunsul meu: ____

### Rulare receiver h2 (cu JOIN)

```python
import socket, struct
MCAST = '224.1.1.1'
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(('', 5302))
mreq = struct.pack("4sl", socket.inet_aton(MCAST), socket.INADDR_ANY)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
print("În grup, aștept...")
data, addr = sock.recvfrom(1024)
print(f"Primit: {data}")
```

### Rulare receiver h3 (FĂRĂ JOIN)

```python
import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(('', 5302))
print("Aștept pe port (fără JOIN)...")
data, addr = sock.recvfrom(1024)  # va aștepta la infinit
```

### Sender h1

```python
import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 1)
sock.sendto(b"Multicast!", ('224.1.1.1', 5302))
```

### Verificare

Răspuns corect: **B** — doar h2 primește.

Ai ghicit? □ Da □ Nu

### Predicție #4

> Dacă faci JOIN ÎNAINTE de bind, ce se întâmplă?

- [ ] A) Merge la fel
- [ ] B) Poate pierde mesaje
- [ ] C) Eroare imediată
- [ ] D) JOIN eșuează silențios

Răspunsul meu: ____

### Experiment

Inversează ordinea în cod și testează.

Răspuns: **B** — poate funcționa uneori, dar nu e garantat. Kernel-ul nu știe sigur unde să livreze.

### Reflecție Multicast (2 min)

Diferența majoră față de broadcast pe care am observat-o:
_________________________________

De ce contează ordinea bind/JOIN (în propriile cuvinte):
_________________________________

---

## Experimentul 3: TCP Tunnel

### Predicție #5

> Clientul se conectează la tunnel (h2:9090). Ce IP vede serverul (h3)?

- [ ] A) IP-ul clientului (h1)
- [ ] B) IP-ul tunnel-ului (h2)
- [ ] C) localhost
- [ ] D) Depinde de configurare

Răspunsul meu: ____

### Setup

h3 — server echo:
```bash
nc -l -p 8080 -k
```

h2 — tunnel:
```python
import socket, threading

def forward(src, dst, name):
    while True:
        data = src.recv(4096)
        if not data: break
        dst.sendall(data)
        print(f"[{name}] {len(data)} bytes")
    src.close()
    dst.close()

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(('', 9090))
server.listen(5)
print("Tunnel: :9090 -> 10.0.3.3:8080")

while True:
    client, addr = server.accept()
    print(f"Client: {addr}")
    target = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    target.connect(('10.0.3.3', 8080))
    threading.Thread(target=forward, args=(client, target, "C->S")).start()
    threading.Thread(target=forward, args=(target, client, "S->C")).start()
```

h1 — client:
```bash
nc 10.0.3.2 9090
```

### Verificare

Răspuns corect: **B** — serverul vede IP-ul tunnel-ului.

Tunnel-ul "ascunde" clientul original. Asta are implicații pentru logging, security, etc.

### Predicție #6

> De ce nu merge cu un singur thread?

- [ ] A) Python nu permite
- [ ] B) recv() blochează și nu poate primi din ambele direcții
- [ ] C) TCP e half-duplex
- [ ] D) Performanță

Răspunsul meu: ____

Răspuns: **B**

### Reflecție Tunnel (2 min)

Ce s-ar întâmpla dacă serverul trimite date ÎNAINTE ca clientul să trimită ceva, cu un singur thread?
_________________________________

---

## Exerciții EVALUATE (15 min)

Acum că ai văzut toate experimentele, hai să gândim la nivel mai înalt.

### E1: Alegere protocol

**Scenariu:** Clădire de birouri, 500 angajați. Trebuie să implementezi:
- Alertă de incendiu (TOȚI trebuie să primească)
- Notificări pentru echipa HR (30 persoane)

Ce folosești pentru fiecare și de ce?

Alertă incendiu: __________ 
Motivare (2-3 propoziții):
_________________________________
_________________________________

Notificări HR: __________
Motivare:
_________________________________
_________________________________

### E2: Critică de design

**Codul cuiva:**
```python
# "Am făcut un tunnel optimizat cu un singur thread"
while True:
    if client.recv(1, socket.MSG_PEEK):
        data = client.recv(4096)
        server.sendall(data)
    if server.recv(1, socket.MSG_PEEK):
        data = server.recv(4096)
        client.sendall(data)
```

Ce probleme vezi? (minim 2)
1. _________________________________
2. _________________________________

Cum ai îmbunătăți?
_________________________________

### E3: Trade-off analysis

Un TCP tunnel adaugă:
- ~50ms latență
- Un hop suplimentar
- Un single point of failure

Pentru care din aceste aplicații e acceptabil?

| Aplicație | Acceptabil? | De ce? |
|-----------|-------------|--------|
| Chat intern | □ Da □ Nu | |
| Trading financiar | □ Da □ Nu | |
| Backup nocturn | □ Da □ Nu | |

---

## Sumar predicții

| # | Întrebare | Corect | Ai ghicit? |
|---|-----------|--------|------------|
| 1 | Câți primesc broadcast? | C | □ |
| 2 | Fără SO_BROADCAST? | B | □ |
| 3 | Multicast fără JOIN? | B | □ |
| 4 | JOIN înainte de bind? | B | □ |
| 5 | Ce IP vede serverul? | B | □ |
| 6 | De ce 2 thread-uri? | B | □ |

Scor: __/6

Dacă ai sub 4, recitește secțiunile relevante din curs.

---

## Reflecție finală (3 min)

**Cel mai important lucru pe care l-am învățat azi:**
_________________________________

**Ceva ce credeam și s-a dovedit greșit:**
_________________________________

**O întrebare care mi-a rămas:**
_________________________________

---

## Pentru laborator

Mâine vei implementa singur. Pregătește-te:
- Recitește quick_reference.md
- Asigură-te că poți scrie receiver broadcast din memorie
- Gândește-te la un scenariu unde ai folosi multicast

---

Material seminar Rețele de Calculatoare.
Predicțiile sunt bazate pe greșelile frecvente observate în anii anteriori.
