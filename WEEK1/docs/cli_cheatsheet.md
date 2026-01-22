# CLI Cheatsheet - Săptămâna 1

Referință rapidă comenzi pentru analiză trafic și instrumentare.

---

## Utilitare de bază

### ping - Test conectivitate ICMP
```bash
# Ping simplu (3 pachete)
ping -c 3 10.0.1.12

# Ping cu interval rapid
ping -c 5 -i 0.2 127.0.0.1

# Ping cu dimensiune custom
ping -c 3 -s 1000 localhost
```

### ip - Configurare rețea
```bash
# Afișare interfețe
ip addr show

# Afișare doar IP-uri
ip -4 addr show | grep inet

# Afișare rută default
ip route show default

# Tabel ARP
ip neigh show
```

### ss - Socket statistics
```bash
# Porturi TCP în LISTEN
ss -tln

# Porturi UDP
ss -uln

# Toate conexiunile TCP
ss -tan

# Cu PID-uri (necesită sudo)
sudo ss -tlnp

# Filtrare după port
ss -tln 'sport = :9090'
```

### netstat (alternativă legacy)
```bash
netstat -tuln        # Porturi ascultare
netstat -tan         # Conexiuni TCP
netstat -anp | grep 9090
```

---

## netcat (nc) - Cușitul elvețian al rețelelor

### Server TCP
```bash
# Server simplu care afișează mesaje
nc -l -p 9090

# Server cu verbose
nc -v -l -p 9090

# Server care salvează în fișier
nc -l -p 9090 > received.txt
```

### Client TCP
```bash
# Conectare și trimitere interactivă
nc localhost 9090

# Trimitere mesaj one-shot
echo "Hello" | nc localhost 9090

# Trimitere fișier
nc localhost 9090 < file.txt

# Cu timeout
nc -w 3 localhost 9090
```

### UDP cu netcat
```bash
# Server UDP
nc -u -l -p 9091

# Client UDP
echo "UDP packet" | nc -u -w1 localhost 9091
```

### Scanare porturi (base)
```bash
# Verificare port deschis
nc -zv localhost 9090

# Scanare range
nc -zv localhost 9090-9100
```

---

## tshark - Captură trafic CLI

### Captură live
```bash
# Captură pe loopback
sudo tshark -i lo

# Captură pe eth0 cu filtru
sudo tshark -i eth0 -f "tcp port 9090"

# Limită pachete
sudo tshark -i lo -c 10

# Limită durată (secunde)
sudo tshark -i lo -a duration:30
```

### Salvare PCAP
```bash
# Salvare în fișier
sudo tshark -i lo -w capture.pcap

# Cu filtru BPF
sudo tshark -i lo -f "port 9090 or port 9091" -w demo.pcap
```

### Citire PCAP
```bash
# Afișare conținut
tshark -r capture.pcap

# Cu display filter
tshark -r capture.pcap -Y "tcp.flags.syn==1"

# Doar HTTP
tshark -r capture.pcap -Y "http"

# Export CSV
tshark -r capture.pcap -T fields -e frame.number -e ip.src -e ip.dst -e tcp.port -E separator=,
```

### Display filters uzuale
```bash
# TCP SYN (inițiere conexiune)
-Y "tcp.flags.syn==1 and tcp.flags.ack==0"

# TCP handshake complet
-Y "tcp.flags.syn==1"

# HTTP requests
-Y "http.request"

# ICMP (ping)
-Y "icmp"

# După IP sursă
-Y "ip.src==10.0.1.11"

# După port
-Y "tcp.port==9090"
```

### Capture filters BPF
```bash
# Un singur port
-f "port 9090"

# TCP sau UDP
-f "tcp or udp"

# Exclude SSH
-f "not port 22"

# Rețea specifică
-f "net 10.0.1.0/24"
```

---

## tcpdump - Alternativă captură

```bash
# Captură loopback
sudo tcpdump -i lo

# Cu filtru
sudo tcpdump -i lo port 9090

# Salvare PCAP
sudo tcpdump -i lo -w capture.pcap

# Citire PCAP
tcpdump -r capture.pcap

# Afișare ASCII
sudo tcpdump -i lo -A port 9090
```

---

## Python socket one-liners

### Server TCP minim
```python
python3 -c "
import socket
s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
s.bind(('',9090));s.listen(1)
print('Listening :9090')
c,a=s.accept();print(f'Connected {a}')
while d:=c.recv(1024):print(d.decode())
"
```

### Client TCP minim
```python
python3 -c "
import socket
s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.connect(('localhost',9090))
s.send(b'Hello from Python\n')
s.close()
"
```

### HTTP Server simplu
```bash
# Servește directorul curent pe port 8080
python3 -m http.server 8080

# Pe interfață specifică
python3 -m http.server 8080 --bind 127.0.0.1
```

---

## Mininet comenzi

### Pornire
```bash
# Topologie minimală
sudo mn

# Topologie custom
sudo mn --topo single,3

# Cu controller
sudo mn --controller remote
```

### CLI Mininet
```
mininet> help          # Ajutor
mininet> nodes         # Listă noduri
mininet> net           # Topologie
mininet> dump          # Detalii noduri
mininet> h1 ping h2    # Ping între host-uri
mininet> h1 ifconfig   # Config interfață
mininet> pingall       # Test conectivitate
mininet> xterm h1      # Terminal pe h1
mininet> exit          # Ieșire
```

### Cleanup
```bash
sudo mn -c            # Curăță artefacte Mininet
```

---

## Porturi standard Week 1

| Serviciu | Port | Protocol |
|----------|------|----------|
| TCP App | 9090 | TCP |
| UDP App | 9091 | UDP |
| HTTP | 8080 | TCP |
| Week custom | 5100-5199 | TCP/UDP |

## Plan IP Week 1

| Element | Adresă |
|---------|--------|
| Rețea | 10.0.1.0/24 |
| Gateway | 10.0.1.1 |
| h1 | 10.0.1.11 |
| h2 | 10.0.1.12 |
| h3 | 10.0.1.13 |
| Server | 10.0.1.100 |

---

*Revolvix&Hypotheticalandrei | ASE București / CSIE*
