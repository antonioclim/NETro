# Fișă rapidă — WEEK3

Printează asta și ține-o lângă tine în lab.

---

## UDP Broadcast

**Sender** (trebuie SO_BROADCAST!):
```python
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
sock.sendto(b"msg", ('255.255.255.255', 5301))
```

**Receiver**:
```python
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(('', 5301))
data, addr = sock.recvfrom(1024)
```

---

## UDP Multicast

**Sender**:
```python
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 1)
sock.sendto(b"msg", ('224.1.1.1', 5302))
```

**Receiver** (bind ÎNAINTE de JOIN!):
```python
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(('', 5302))  # PRIMUL!
mreq = struct.pack("4sl", socket.inet_aton('224.1.1.1'), socket.INADDR_ANY)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
data, addr = sock.recvfrom(1024)
```

---

## TCP Tunnel pattern

```python
def forward(src, dst):
    while True:
        data = src.recv(4096)
        if not data: break
        dst.sendall(data)
    src.close(); dst.close()

# După accept:
threading.Thread(target=forward, args=(client, target)).start()
threading.Thread(target=forward, args=(target, client)).start()
```

---

## Tabel rapid

| Scenariu | Opțiune necesară |
|----------|------------------|
| Broadcast sender | SO_BROADCAST |
| Multicast sender | IP_MULTICAST_TTL |
| Multicast receiver | IP_ADD_MEMBERSHIP |
| Server restart rapid | SO_REUSEADDR |

---

## Adrese WEEK3

- Subnet: 10.0.3.0/24
- h1=.1, h2=.2, h3=.3
- Porturi: 5300-5399
- Multicast test: 224.1.1.1

---

## Greșeli clasice

| Eroare | Cauza probabilă |
|--------|-----------------|
| PermissionError | Lipsește SO_BROADCAST |
| Nu primesc multicast | bind după JOIN sau JOIN lipsă |
| Address in use | Lipsește SO_REUSEADDR |
| Tunnel blocat | Un singur thread |

---

## Comenzi utile

```bash
sudo mn -c              # curăță Mininet blocat
ip maddr show           # vezi grupuri multicast
sudo tshark -i any -f "udp port 5301"
```
