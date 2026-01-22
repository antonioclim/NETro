# Expected Outputs — Starterkit S3

Acest document conține output-urile așteptate pentru fiecare exemplu, util pentru validare și debugging.

---

## ex01_udp_broadcast.py

### Receiver (h2/h3)
```
$ python3 ex01_udp_broadcast.py recv --port 5007 --count 3

[2025-03-10 14:32:01] Ascult broadcast pe 0.0.0.0:5007...
[2025-03-10 14:32:02] De la 10.0.0.1:54321 → "HELLO_BCAST"
[2025-03-10 14:32:02] De la 10.0.0.1:54321 → "HELLO_BCAST"
[2025-03-10 14:32:03] De la 10.0.0.1:54321 → "HELLO_BCAST"
[INFO] Primit 3 mesaje. Închidere.
```

### Sender (h1)
```
$ python3 ex01_udp_broadcast.py send --dst 255.255.255.255 --port 5007 \
    --message "HELLO_BCAST" --count 3 --interval 0.5

[2025-03-10 14:32:02] Trimit broadcast: 255.255.255.255:5007 ← "HELLO_BCAST"
[2025-03-10 14:32:02] Trimit broadcast: 255.255.255.255:5007 ← "HELLO_BCAST"
[2025-03-10 14:32:03] Trimit broadcast: 255.255.255.255:5007 ← "HELLO_BCAST"
[INFO] Trimise 3 mesaje.
```

### tcpdump
```
$ tcpdump -ni h1-eth0 -c 3 'udp port 5007'

14:32:02.123456 IP 10.0.0.1.54321 > 255.255.255.255.5007: UDP, length 11
14:32:02.623456 IP 10.0.0.1.54321 > 255.255.255.255.5007: UDP, length 11
14:32:03.123456 IP 10.0.0.1.54321 > 255.255.255.255.5007: UDP, length 11
```

---

## ex02_udp_multicast.py

### Receiver abonat (h2)
```
$ python3 ex02_udp_multicast.py recv --group 239.1.1.1 --port 5001 --count 3

[2025-03-10 14:35:01] Join la grup multicast 239.1.1.1 pe port 5001...
[2025-03-10 14:35:02] De la 10.0.0.1:54322 (grup 239.1.1.1) → "HELLO_MCAST"
[2025-03-10 14:35:02] De la 10.0.0.1:54322 (grup 239.1.1.1) → "HELLO_MCAST"
[2025-03-10 14:35:03] De la 10.0.0.1:54322 (grup 239.1.1.1) → "HELLO_MCAST"
[INFO] Primit 3 mesaje. Leave grup și închidere.
```

### Sender (h1)
```
$ python3 ex02_udp_multicast.py send --group 239.1.1.1 --port 5001 \
    --message "HELLO_MCAST" --count 3 --ttl 1

[2025-03-10 14:35:02] Trimit multicast: 239.1.1.1:5001 (TTL=1) ← "HELLO_MCAST"
[2025-03-10 14:35:02] Trimit multicast: 239.1.1.1:5001 (TTL=1) ← "HELLO_MCAST"
[2025-03-10 14:35:03] Trimit multicast: 239.1.1.1:5001 (TTL=1) ← "HELLO_MCAST"
[INFO] Trimise 3 mesaje.
```

### Verificare grup (h2)
```
$ ip maddr show dev h2-eth0

2:      h2-eth0
        link  33:33:00:00:00:01
        link  01:00:5e:00:00:01
        link  33:33:ff:xx:xx:xx
        inet  239.1.1.1
        inet6 ff02::1
```

---

## ex03_tcp_tunnel.py

### Server țintă (b1)
```
$ python3 ex04_echo_server.py --listen 0.0.0.0:8080

[2025-03-10 14:40:01] Echo server pornit pe 0.0.0.0:8080
[2025-03-10 14:40:10] Conexiune nouă de la 10.0.1.254:54000
[2025-03-10 14:40:10] Primit: "hello\n", trimis: "HELLO\n"
[2025-03-10 14:40:10] Client 10.0.1.254:54000 deconectat
```

### Tunnel (r1)
```
$ python3 ex03_tcp_tunnel.py --listen 0.0.0.0:9090 --target 10.0.2.1:8080

[2025-03-10 14:40:05] TCP Tunnel pornit: 0.0.0.0:9090 → 10.0.2.1:8080
[2025-03-10 14:40:10] Conexiune de la 10.0.1.1:54123
[2025-03-10 14:40:10] Conectat la țintă 10.0.2.1:8080
[2025-03-10 14:40:10] Forward activ (2 threads)
[2025-03-10 14:40:10] Sesiune închisă pentru 10.0.1.1:54123
```

### Client (a1)
```
$ echo "hello" | nc 10.0.1.254 9090

HELLO
```

---

## ex04_echo_server.py

### Server
```
$ python3 ex04_echo_server.py --listen 127.0.0.1:3333

[2025-03-10 14:45:01] Echo server pornit pe 127.0.0.1:3333
[2025-03-10 14:45:05] Conexiune nouă de la 127.0.0.1:54444
[2025-03-10 14:45:05] Primit: "test message", trimis: "TEST MESSAGE"
[2025-03-10 14:45:05] Client 127.0.0.1:54444 deconectat
```

### Client (netcat)
```
$ echo "test message" | nc 127.0.0.1 3333

TEST MESSAGE
```

---

## ex05_tcp_multiclient.py

### Server
```
$ python3 ex05_tcp_multiclient.py

[2025-03-10 14:50:01] Server multiclient pornit pe 0.0.0.0:3333
[2025-03-10 14:50:05] [Thread-1] Client conectat: 127.0.0.1:54001
[2025-03-10 14:50:06] [Thread-2] Client conectat: 127.0.0.1:54002
[2025-03-10 14:50:06] [Thread-1] Primit: "CLIENT_A", răspuns: "CLIENT_A"
[2025-03-10 14:50:07] [Thread-2] Primit: "CLIENT_B", răspuns: "CLIENT_B"
[2025-03-10 14:50:07] [Thread-1] Client 127.0.0.1:54001 deconectat
[2025-03-10 14:50:08] [Thread-2] Client 127.0.0.1:54002 deconectat
```

### Clienți simultani
```
Terminal 1: $ echo "CLIENT_A" | nc 127.0.0.1 3333
            CLIENT_A

Terminal 2: $ echo "CLIENT_B" | nc 127.0.0.1 3333
            CLIENT_B
```

---

## ex06_tcp_framing.py

### Server (mod delimiter)
```
$ python3 ex06_tcp_framing.py server --mode delimiter --port 4444

[2025-03-10 15:00:01] Server framing pornit (mode=delimiter) pe :4444
[2025-03-10 15:00:05] Client conectat: 127.0.0.1:55000
[2025-03-10 15:00:05] Mesaj complet primit: "MESSAGE_ONE"
[2025-03-10 15:00:05] Mesaj complet primit: "MESSAGE_TWO"
[2025-03-10 15:00:06] Client deconectat
```

### Client
```
$ python3 ex06_tcp_framing.py client --mode delimiter --port 4444 \
    --message "MESSAGE_ONE"

[2025-03-10 15:00:05] Conectat la 127.0.0.1:4444
[2025-03-10 15:00:05] Trimis: "MESSAGE_ONE\n" (12 bytes)
[2025-03-10 15:00:05] Răspuns server: OK
```

---

## ex07_udp_session_ack.py

### Server
```
$ python3 ex07_udp_session_ack.py server --port 6000

[2025-03-10 15:10:01] Server sesiuni UDP pornit pe :6000
[2025-03-10 15:10:05] HELLO de la 127.0.0.1:55001, token generat: abc123
[2025-03-10 15:10:06] MSG:abc123:test_data de la 127.0.0.1:55001
[2025-03-10 15:10:06] Trimis ACK:abc123:1
[2025-03-10 15:10:07] BYE:abc123 de la 127.0.0.1:55001, sesiune închisă
```

### Client
```
$ python3 ex07_udp_session_ack.py client --host 127.0.0.1 --port 6000

[2025-03-10 15:10:05] Trimit HELLO...
[2025-03-10 15:10:05] Token primit: abc123
[2025-03-10 15:10:06] Trimit mesaj: "test_data"
[2025-03-10 15:10:06] ACK primit pentru seq=1
[2025-03-10 15:10:07] Trimit BYE, sesiune închisă
```

---

## Mininet pingall

### Topologie bază
```
mininet> pingall
*** Ping: testing ping reachability
h1 -> h2 h3 
h2 -> h1 h3 
h3 -> h1 h2 
*** Results: 0% dropped (6/6 received)
```

### Topologie extinsă
```
mininet> pingall
*** Ping: testing ping reachability
a1 -> a2 b1 b2 r1 
a2 -> a1 b1 b2 r1 
b1 -> a1 a2 b2 r1 
b2 -> a1 a2 b1 r1 
r1 -> a1 a2 b1 b2 
*** Results: 0% dropped (20/20 received)
```

---

## Erori frecvente și soluții

### "Address already in use"
```
OSError: [Errno 98] Address already in use
```
**Soluție:** `sudo mn -c` sau `sudo bash scripts/cleanup.sh`

### "Permission denied" (broadcast)
```
OSError: [Errno 13] Permission denied
```
**Soluție:** Adăugați `sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)`

### Multicast nu funcționează
```
# Receiver nu primește nimic
```
**Soluție:** Verificați că receiver-ul face JOIN la grup înainte de a primi date.

### Tunnel timeout
```
ConnectionRefusedError: [Errno 111] Connection refused
```
**Soluție:** Verificați că serverul țintă rulează și că portul e corect.
