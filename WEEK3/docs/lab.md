# Laborator 3: Implementare Broadcast, Multicast, TCP Tunnel

2 ore | Lucru individual sau în perechi

---

## Înainte să începi

### Self-check (1 minut)

Răspunde sincer:

Pot scrie un socket UDP receiver fără să mă uit în notițe?
□ Da, sigur □ Probabil □ Nu prea □ Deloc

Dacă ai răspuns "Nu prea" sau "Deloc", ține deschis `docs/templates/quick_reference.md`.

### Setup

```bash
sudo python3 mininet/topologies/topo_base.py
```

Dacă ceva nu merge: `sudo mn -c` și încearcă din nou.

---

## Partea 1: Broadcast (25 min)

### Pas 1.1: Receiver

Pe h2, creează fișierul `bcast_recv.py`:

```python
import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(('', 5301))

print("Receiver pornit, aștept broadcast...")
while True:
    data, addr = sock.recvfrom(1024)
    print(f"[{addr[0]}] {data.decode()}")
```

Rulează și lasă-l să aștepte.

### Pas 1.2: Sender

**Predicție:** Ce se întâmplă dacă trimiți FĂRĂ SO_BROADCAST?
_________________________________

Pe h1, creează `bcast_send.py`:

```python
import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# DECOMENTEAZĂ LINIA DE MAI JOS DUPĂ CE TESTEZI FĂRĂ EA
# sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
sock.sendto(b"Test broadcast", ('255.255.255.255', 5301))
print("Trimis!")
```

Rulează. Ce s-a întâmplat?
_________________________________

Acum decomentează SO_BROADCAST și rulează din nou.

### Checkpoint broadcast

□ Receiver-ul a primit mesajul
□ Am înțeles de ce SO_BROADCAST e obligatoriu
□ Pot explica ce s-ar întâmpla dacă ar fi 3 receiveri în loc de 1

---

## Partea 2: Multicast (30 min)

### Pas 2.1: Receiver cu JOIN

**Predicție:** Ce se întâmplă dacă fac bind DUPĂ JOIN?
_________________________________

Pe h2, `mcast_recv.py`:

```python
import socket
import struct

GRUP = '224.1.1.1'
PORT = 5302

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# ORDINEA CONTEAZĂ!
sock.bind(('', PORT))  # 1. bind
mreq = struct.pack("4sl", socket.inet_aton(GRUP), socket.INADDR_ANY)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)  # 2. join

print(f"În grupul {GRUP}, aștept pe :{PORT}")
while True:
    data, addr = sock.recvfrom(1024)
    print(f"[{addr[0]}] {data.decode()}")
```

### Pas 2.2: Sender

Pe h1, `mcast_send.py`:

```python
import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 1)

for i in range(5):
    msg = f"Mesaj multicast #{i}"
    sock.sendto(msg.encode(), ('224.1.1.1', 5302))
    print(f"Trimis: {msg}")
```

### Pas 2.3: Experiment — receiver fără JOIN

Pe h3, rulează un receiver care face bind pe 5302 dar NU face JOIN.

Primește mesaje? □ Da □ Nu

De ce?
_________________________________

### Checkpoint multicast

□ Receiver-ul cu JOIN primește
□ Receiver-ul fără JOIN NU primește
□ Știu că bind trebuie ÎNAINTE de JOIN
□ Pot explica diferența față de broadcast

---

## Partea 3: TCP Tunnel (35 min)

### Pas 3.1: Server țintă pe h3

```bash
# Echo server simplu
while true; do nc -l -p 8080 -c 'cat'; done
```

Sau în Python dacă preferi.

### Pas 3.2: Tunnel pe h2

**Predicție:** De ce nu merge cu un singur thread?
_________________________________

Creează `tunnel.py`:

```python
import socket
import threading

def forward(src, dst, label):
    """Transferă date dintr-o parte în alta"""
    try:
        while True:
            data = src.recv(4096)
            if not data:
                print(f"[{label}] Conexiune închisă")
                break
            dst.sendall(data)
            print(f"[{label}] {len(data)} bytes")
    except Exception as e:
        print(f"[{label}] Eroare: {e}")
    finally:
        src.close()
        dst.close()

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('', 9090))
    server.listen(5)
    
    print("Tunnel activ: :9090 -> 10.0.3.3:8080")
    
    while True:
        client, addr = server.accept()
        print(f"Client nou: {addr}")
        
        # Conectare la destinație
        target = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        target.connect(('10.0.3.3', 8080))
        
        # Două thread-uri pentru bidirecțional
        t1 = threading.Thread(target=forward, args=(client, target, "C→S"))
        t2 = threading.Thread(target=forward, args=(target, client, "S→C"))
        t1.start()
        t2.start()

if __name__ == "__main__":
    main()
```

### Pas 3.3: Test de pe h1

```bash
nc 10.0.3.2 9090
# Scrie ceva, ar trebui să primești echo
```

### Checkpoint tunnel

□ Tunnel-ul funcționează
□ Văd mesajele forward în ambele direcții
□ Înțeleg de ce sunt 2 thread-uri

---

## Partea 4: Exerciții CREATE (40 min)

Alege UNUL din cele două. Dacă termini repede, fă-l și pe celălalt.

### Opțiunea A: Protocol Heartbeat pentru Service Discovery

**Problema:** Ai mai multe servicii într-o rețea. Vrei ca fiecare să-și anunțe prezența periodic, iar un "registry" să țină evidența celor active.

**Cerințe:**
1. Fiecare serviciu trimite heartbeat la fiecare 5 secunde
2. Format mesaj: `SERVICIU|IP|PORT|TIMESTAMP`
3. Registry-ul marchează un serviciu ca "mort" dacă nu a primit heartbeat de 15 secunde
4. Decizie de design: broadcast sau multicast? Justifică.

**Structură sugerată:**

```python
# heartbeat_service.py
class ServiceAnnouncer:
    def __init__(self, name, port):
        # TODO: socket setup
        pass
    
    def start(self):
        # TODO: trimite heartbeat periodic
        pass

# heartbeat_registry.py  
class ServiceRegistry:
    def __init__(self):
        self.services = {}  # {name: {ip, port, last_seen}}
        # TODO: socket setup pentru a primi heartbeat-uri
    
    def get_active(self):
        # TODO: returnează serviciile cu last_seen < 15 sec
        pass
```

**Livrabil:** Cod funcțional + 1 paragraf justificare alegere broadcast/multicast.

### Opțiunea B: Tunnel cu Logging și Statistici

**Problema:** Extinde tunnel-ul pentru a genera statistici și log-uri.

**Cerințe:**
1. Log fiecare conexiune în JSON: timestamp, client_ip, duration, bytes_sent, bytes_received
2. Salvează în `tunnel_log.json`
3. La Ctrl+C, afișează sumar: total conexiuni, total bytes, durata medie

**Structură sugerată:**

```python
import json
import time
from datetime import datetime

class LoggingTunnel:
    def __init__(self, listen_port, target_host, target_port):
        self.stats = {
            "total_connections": 0,
            "total_bytes": 0,
            "connections": []
        }
        # TODO: restul
    
    def log_connection(self, client_ip, duration, bytes_in, bytes_out):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "client": client_ip,
            "duration_sec": duration,
            "bytes_in": bytes_in,
            "bytes_out": bytes_out
        }
        self.stats["connections"].append(entry)
        # TODO: scrie în fișier
    
    def print_summary(self):
        # TODO: afișează statistici
        pass
```

**Livrabil:** Cod funcțional + exemplu de output JSON cu 3+ conexiuni.

---

## Partea 5: Auto-evaluare finală (5 min)

Completează sincer:

### Pot face FĂRĂ să mă uit în notițe:

□ Receiver broadcast
□ Sender broadcast (cu SO_BROADCAST)
□ Receiver multicast (cu JOIN în ordine corectă)
□ Sender multicast (cu TTL)
□ Forward function pentru tunnel

### Pot EXPLICA unui coleg:

□ De ce SO_BROADCAST e obligatoriu
□ De ce bind() vine înainte de JOIN
□ De ce tunnel-ul are 2 thread-uri
□ Diferența broadcast vs multicast

### Scor auto-evaluare

Câte checkbox-uri ai bifat? __/9

- 8-9: Excelent, ești pregătit pentru examen
- 6-7: Bine, dar revizuiește punctele nebifate
- 4-5: Refă experimentele pentru punctele slabe
- <4: Programează o sesiune de consultații

---

## Muddiest Point

Care concept e ÎNCĂ cel mai confuz pentru tine?

□ SO_BROADCAST și rolul lui
□ Ordinea bind/JOIN la multicast
□ struct.pack pentru mreq
□ De ce 2 thread-uri la tunnel
□ TCP framing problem
□ Altceva: _________________

Scrie o întrebare concretă pe care vrei să o clarifici:
_________________________________

---

## Înainte de a pleca

□ Am completat auto-evaluarea
□ Am notat muddiest point
□ Am făcut git commit la codul meu (dacă e cazul)
□ Am curățat sesiunea Mininet (`sudo mn -c`)

---

Material laborator Rețele de Calculatoare.
Exercițiile CREATE sunt opționale dar recomandate pentru înțelegere profundă.
