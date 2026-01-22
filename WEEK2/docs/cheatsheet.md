# CLI Cheatsheet - Săptămâna 2: Socket Programming

## Comenzi Rapide

### Pornire Demo Complet
```bash
# Demo automat (produce artefacte)
./scripts/run_all.sh

# Verificare artefacte
./tests/smoke_test.sh
```

### Servere TCP/UDP Manual

```bash
# Server TCP (threaded)
python3 seminar/python/exercises/ex_2_01_tcp.py server --port 9090

# Server UDP
python3 seminar/python/exercises/ex_2_02_udp.py server --port 9091
```

### Clienți TCP/UDP

```bash
# Client TCP
python3 seminar/python/exercises/ex_2_01_tcp.py client \
    --host 127.0.0.1 --port 9090 --message "Hello"

# Client UDP (o comandă)
python3 seminar/python/exercises/ex_2_02_udp.py client \
    --host 127.0.0.1 --port 9091 --once "ping"

# Client UDP (interactiv)
python3 seminar/python/exercises/ex_2_02_udp.py client \
    --host 127.0.0.1 --port 9091 --interactive
```

### Load Testing

```bash
# 10 clienți TCP concurenți
python3 seminar/python/exercises/ex_2_01_tcp.py load \
    --host 127.0.0.1 --port 9090 --clients 10
```

---

## Capturi și Analiză

### Captură cu tcpdump

```bash
# Captură TCP pe loopback
sudo tcpdump -i lo -w capture_tcp.pcap tcp port 9090

# Captură UDP
sudo tcpdump -i lo -w capture_udp.pcap udp port 9091

# Captură combinată
sudo tcpdump -i lo -w capture_all.pcap '(tcp port 9090) or (udp port 9091)'
```

### Analiză cu tshark

```bash
# Afișare toate pachetele
tshark -r capture.pcap

# Filtrare TCP
tshark -r capture.pcap -Y "tcp"

# Filtrare handshake TCP
tshark -r capture.pcap -Y "tcp.flags.syn==1"

# Câmpuri specifice
tshark -r capture.pcap -T fields \
    -e frame.number -e ip.src -e tcp.srcport \
    -e ip.dst -e tcp.dstport -e tcp.flags.str

# Statistici conversații
tshark -r capture.pcap -z conv,tcp
```

### Netcat pentru debugging

```bash
# Server TCP simplu
nc -l -p 9090

# Client TCP
echo "test" | nc localhost 9090

# Server UDP
nc -u -l -p 9091

# Client UDP
echo "ping" | nc -u localhost 9091
```

---

## Mininet

### Comenzi de bază

```bash
# Pornire CLI cu topologie bază
sudo python3 seminar/mininet/topologies/topo_2_base.py --cli

# Pornire CLI cu topologie extinsă
sudo python3 seminar/mininet/topologies/topo_2_extended.py --cli

# Test automat
sudo python3 seminar/mininet/topologies/topo_2_base.py --test

# Curățare sesiuni anterioare
sudo mn -c
```

### Comenzi în CLI Mininet

```
nodes              # Lista noduri
net                # Topologia
dump               # Detalii noduri
pingall            # Test conectivitate
h1 ping h2         # Ping între hosturi
h1 ifconfig        # Configurare interfață
xterm h1           # Terminal pentru h1
```

### Demo TCP în Mininet

```
# În CLI Mininet:
h1 python3 /path/to/ex_2_01_tcp.py server --bind 10.0.0.1 --port 9090 &
h2 python3 /path/to/ex_2_01_tcp.py client --host 10.0.0.1 --port 9090 -m "test"
```

---

## Debugging

### Verificare porturi

```bash
# Porturi în ascultare
ss -tuln

# Verificare port specific
ss -tuln | grep 9090

# Procese pe port
lsof -i :9090

# Kill proces pe port
fuser -k 9090/tcp
```

### Verificare conexiuni

```bash
# Conexiuni active
ss -tn

# Statistici socket
ss -s

# Monitorizare în timp real
watch -n 1 'ss -tn | grep 9090'
```

### Log și debugging Python

```bash
# Rulare cu output unbuffered
python3 -u script.py

# Cu verbose
python3 script.py --verbose 2>&1 | tee log.txt
```

---

## Plan IP WEEK 2

| Entitate | IP | Notă |
|----------|-----|------|
| Rețea | 10.0.2.0/24 | WEEK 2 |
| Gateway | 10.0.2.1 | Router |
| h1 | 10.0.2.11 | Server |
| h2 | 10.0.2.12 | Client |
| h3 | 10.0.2.13 | Client |
| Server aplicație | 10.0.2.100 | TCP/UDP |

## Plan Porturi WEEK 2

| Serviciu | Port | Protocol |
|----------|------|----------|
| TCP App | 9090 | TCP |
| UDP App | 9091 | UDP |
| HTTP | 8080 | TCP |
| Proxy | 8888 | TCP |
| Week Base | 5200-5299 | Custom |

---

## Troubleshooting Rapid

| Problemă | Comandă verificare | Soluție |
|----------|-------------------|---------|
| Port ocupat | `ss -tuln \| grep 9090` | `fuser -k 9090/tcp` |
| Server nu răspunde | `ping localhost` | Verifică firewall |
| Captură goală | `tcpdump -D` | Interfața corectă |
| Mininet blocat | `ps aux \| grep mininet` | `sudo mn -c` |
| Permission denied | `ls -la script.py` | `chmod +x script.py` |

---

*WEEK 2 - Socket Programming TCP/UDP*
*ASE București, CSIE*
