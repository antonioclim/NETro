# Exemplu complet: UDP Broadcast

Pas cu pas, cu explicații. Citește-l înainte să scrii cod.

---

## Ce vrem să facem

h1 trimite un mesaj. h2 și h3 îl primesc. Fără să știm câți sunt sau ce IP-uri au.

```
h1 (sender) ────► [toată rețeaua] ────► h2, h3 (receiveri)
```

---

## Receiver (pe h2 și h3)

```python
import socket

# 1. Creez socket UDP
# AF_INET = IPv4, SOCK_DGRAM = UDP
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# 2. Permit refolosirea portului
# Fără asta, după Ctrl+C trebuie să aștepți ~1 minut
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# 3. Mă leg de port
# '' = toate interfețele (0.0.0.0)
sock.bind(('', 5301))

print("Aștept broadcast pe :5301...")

# 4. Primesc (blocant — stau aici până vine ceva)
while True:
    data, addr = sock.recvfrom(1024)
    # data = bytes, addr = (ip, port) al sender-ului
    print(f"De la {addr[0]}: {data.decode()}")
```

**De ce recvfrom și nu recv?**
UDP nu are conexiune. recv() nu știe de unde a venit pachetul. recvfrom() îți spune și adresa sursă.

---

## Sender (pe h1)

```python
import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# OBLIGATORIU pentru broadcast!
# Fără asta: PermissionError
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

# Trimit
sock.sendto(b"Salut de la h1!", ('255.255.255.255', 5301))
print("Trimis!")

sock.close()
```

**De ce e nevoie de SO_BROADCAST?**

Sistemul te protejează să nu faci broadcast din greșeală. Imaginează-ți că ai o rețea de 10.000 de mașini și un bug în cod trimite broadcast în buclă infinită. Dezastru.

SO_BROADCAST e ca un formular pe care îl semnezi: "Da, știu ce fac, vreau să trimit la toată lumea."

---

## Ce se întâmplă în spatele scenei

```
1. h1 creează pachet UDP
   src: 10.0.3.1:54321 (port efemer)
   dst: 255.255.255.255:5301
   
2. Switch-ul vede că e broadcast
   → trimite pe TOATE porturile (flood)
   
3. h2 și h3 primesc pachetul
   Kernel-ul verifică: "am ceva pe :5301?"
   Da → livrează la socket
   
4. h1 NU primește (de obicei)
   Proprul broadcast nu se întoarce
```

---

## Greșeli frecvente

**Greșeala 1:** Uit SO_BROADCAST
```
PermissionError: [Errno 13] Permission denied
```
Fix: adaugă setsockopt înainte de sendto

**Greșeala 2:** Trimit string, nu bytes
```python
sock.sendto("text", ...)  # GREȘIT
sock.sendto(b"text", ...)  # CORECT
sock.sendto("text".encode(), ...)  # CORECT
```

**Greșeala 3:** Address already in use
```
OSError: [Errno 98] Address already in use
```
Fix: adaugă SO_REUSEADDR înainte de bind

---

## Verifică că ai înțeles

Scrie din memorie un sender broadcast. Nu te uita mai sus.

```python
# Completează:
import ______

sock = socket.socket(______, ______)
sock.______(______, ______, 1)
sock.______(b"Test", (______, 5301))
```

<details>
<summary>Verificare</summary>

```python
import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
sock.sendto(b"Test", ('255.255.255.255', 5301))
```
</details>
