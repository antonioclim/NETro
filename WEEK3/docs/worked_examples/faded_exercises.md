# Exerciții progresive

Fiecare concept are 3 versiuni: complet → parțial → gol.
Începe cu ce poți și avansează.

---

## 1. Broadcast Receiver

### Versiunea A — completă (citește și înțelege)

```python
import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(('', 5301))
data, addr = sock.recvfrom(1024)
print(data.decode())
```

### Versiunea B — parțială (completează)

```python
import socket
sock = socket.socket(socket.AF_INET, socket.________)
sock.setsockopt(socket.SOL_SOCKET, socket.________, 1)
sock.bind(________)
data, addr = sock.________(1024)
print(data.decode())
```

### Versiunea C — goală (scrie tot)

```python
# Scrie un broadcast receiver pe portul 5301



```

<details>
<summary>Răspunsuri B</summary>
SOCK_DGRAM, SO_REUSEADDR, ('', 5301), recvfrom
</details>

---

## 2. Broadcast Sender

### Versiunea A — completă

```python
import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
sock.sendto(b"Test", ('255.255.255.255', 5301))
```

### Versiunea B — parțială

```python
import socket
sock = socket.socket(________, ________)
sock.setsockopt(________, ________, 1)
sock.________(b"Test", (________, 5301))
```

### Versiunea C — goală

```python
# Scrie un broadcast sender



```

<details>
<summary>Răspunsuri B</summary>
socket.AF_INET, socket.SOCK_DGRAM, socket.SOL_SOCKET, socket.SO_BROADCAST, sendto, '255.255.255.255'
</details>

---

## 3. Multicast Receiver

### Versiunea A — completă

```python
import socket, struct
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(('', 5302))
mreq = struct.pack("4sl", socket.inet_aton('224.1.1.1'), socket.INADDR_ANY)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
data, addr = sock.recvfrom(1024)
```

### Versiunea B — parțială

```python
import socket, struct
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.________(('', 5302))  # Ce vine PRIMUL?
mreq = struct.pack("4sl", socket.________(________), socket.INADDR_ANY)
sock.setsockopt(socket.________, socket.________, mreq)
data, addr = sock.recvfrom(1024)
```

### Versiunea C — goală

```python
# Multicast receiver pentru grupul 224.1.1.1:5302
# ATENȚIE: ordinea contează!



```

<details>
<summary>Răspunsuri B</summary>
bind, inet_aton, '224.1.1.1', IPPROTO_IP, IP_ADD_MEMBERSHIP
</details>

---

## 4. Forward pentru tunnel

### Versiunea A — completă

```python
def forward(src, dst, label):
    while True:
        data = src.recv(4096)
        if not data:
            break
        dst.sendall(data)
    src.close()
    dst.close()
```

### Versiunea B — parțială

```python
def forward(src, dst, label):
    while True:
        data = src.________(4096)
        if not ________:
            break
        dst.________(data)
    src.________()
    dst.________()
```

### Versiunea C — goală

```python
# Funcție care citește de la src și trimite la dst
# Se oprește când conexiunea e închisă



```

<details>
<summary>Răspunsuri B</summary>
recv, data, sendall, close, close
</details>

---

## 5. TCP Server setup

### Versiunea A — completă

```python
import socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(('', 9090))
server.listen(5)
client, addr = server.accept()
```

### Versiunea B — parțială

```python
import socket
server = socket.socket(socket.AF_INET, socket.________)
server.setsockopt(socket.________, socket.________, 1)
server.________(('', 9090))
server.________(5)
client, addr = server.________()
```

### Versiunea C — goală

```python
# Server TCP pe portul 9090



```

<details>
<summary>Răspunsuri B</summary>
SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR, bind, listen, accept
</details>

---

## Hints dacă te blochezi

### Pentru broadcast:
<details><summary>Hint 1</summary>SOCK_DGRAM pentru UDP</details>
<details><summary>Hint 2</summary>Sender-ul are nevoie de SO_BROADCAST</details>

### Pentru multicast:
<details><summary>Hint 1</summary>bind() ÎNAINTE de JOIN</details>
<details><summary>Hint 2</summary>struct.pack("4sl", ...) pentru mreq</details>

### Pentru tunnel:
<details><summary>Hint 1</summary>recv() returnează b'' când conexiunea e închisă</details>
<details><summary>Hint 2</summary>sendall() nu send()</details>

---

## Progres

□ Versiunea A citită și înțeleasă
□ Versiunea B completată corect
□ Versiunea C scrisă fără să mă uit

Când ai toate cele 3 pentru un concept, treci la următorul.
