# Scenarii Mininet – Săptămâna 10

## Prezentare generală

Acest document descrie experimente de rețea folosind Mininet pentru a demonstra conceptele din Săptămâna 10: servicii de nivel aplicație (DNS, HTTP, SSH-like communication).

**Durată estimată:** 45-60 minute

---

## Scenariul 1: Topologie Client-Server HTTP

### Obiectiv
Demonstrarea comunicării HTTP între un client și un server pe o topologie Mininet simplă.

### Topologie
```
    h1 (client)
        |
       s1 (switch)
        |
    h2 (server)
```

### Pași de execuție

1. **Pornire topologie:**
```bash
cd mininet/topologies/
sudo python3 topo_10_base.py
```

2. **În terminalul Mininet, pornește serverul HTTP pe h2:**
```bash
mininet> h2 python3 -m http.server 8000 &
```

3. **Test conectivitate:**
```bash
mininet> h1 ping -c 3 h2
```

4. **Cerere HTTP de la h1 la h2:**
```bash
mininet> h1 curl -v http://10.0.0.2:8000/
```

5. **Captură trafic HTTP:**
```bash
mininet> h1 tcpdump -i h1-eth0 port 8000 -w /tmp/http_capture.pcap &
mininet> h1 curl http://10.0.0.2:8000/
```

### Rezultate așteptate
- Ping: 0% packet loss
- curl: Răspuns HTTP 200 cu listing director
- PCAP: Pachete TCP pe portul 8000

### Întrebări What-if
1. Ce se întâmplă dacă serverul nu este pornit?
2. Cum afectează latența (adăugată cu `tc`) timpul de răspuns?

---

## Scenariul 2: Simulare DNS cu Multiple Hosturi

### Obiectiv
Înțelegerea rezoluției DNS într-o rețea simulată.

### Topologie
```
    h1 (client)       h2 (dns-server)
        \                 /
         \               /
          s1 (switch)
         /               \
        /                 \
    h3 (web-server)   h4 (debug)
```

### Pași de execuție

1. **Pornire topologie extinsă:**
```bash
sudo python3 topo_10_services.py
```

2. **Configurare DNS simplu pe h2:**
```bash
# În terminalul h2 (simular cu dnsmasq)
mininet> h2 python3 /path/to/simple_dns.py &
```

3. **Test DNS de la h1:**
```bash
mininet> h1 dig @10.0.0.2 webserver.lab.local
```

4. **Acces web server folosind numele:**
```bash
# Configurare manuală /etc/hosts pe h1
mininet> h1 echo "10.0.0.3 webserver.lab.local" >> /etc/hosts
mininet> h1 curl http://webserver.lab.local:8000/
```

### Rezultate așteptate
- DNS query returnează 10.0.0.3
- curl accesează webserver-ul prin nume

---

## Scenariul 3: Analiza latență HTTP

### Obiectiv
Măsurarea impactului latențelor de rețea asupra performanței HTTP.

### Setup
Folosim topologia de bază și adăugăm latență artificială.

### Pași de execuție

1. **Pornire topologie și server:**
```bash
sudo python3 topo_10_base.py
mininet> h2 python3 -m http.server 8000 &
```

2. **Măsurare baseline (fără latență):**
```bash
mininet> h1 time curl -o /dev/null -s http://10.0.0.2:8000/
```

3. **Adăugare latență 50ms:**
```bash
mininet> h1 tc qdisc add dev h1-eth0 root netem delay 50ms
```

4. **Măsurare cu latență:**
```bash
mininet> h1 time curl -o /dev/null -s http://10.0.0.2:8000/
```

5. **Simulare RTT variabil:**
```bash
mininet> h1 tc qdisc change dev h1-eth0 root netem delay 100ms 20ms
```

### Rezultate așteptate

| Condiție | Timp estimat |
|----------|--------------|
| Baseline | ~10ms |
| +50ms latency | ~160ms (TCP+HTTP) |
| +100ms latency | ~310ms |

### Calcul teoretic
- TCP handshake: 1 RTT
- HTTP request: 1 RTT
- Total: 2 RTT + transfer data

Pentru RTT=50ms → minim 100ms overhead

---

## Scenariul 4: Port Scanning și Discovery

### Obiectiv
Simularea discovery de servicii într-o rețea.

### Topologie
4 hosturi cu servicii diferite pe porturi diferite.

### Pași de execuție

1. **Pornire servicii pe hosturi diferite:**
```bash
mininet> h2 python3 -m http.server 80 &
mininet> h3 python3 -m http.server 8080 &
mininet> h4 nc -l -p 22 &
```

2. **Scan de la h1 folosind netcat:**
```bash
# Test port 80 pe h2
mininet> h1 nc -zv 10.0.0.2 80

# Test port 8080 pe h3
mininet> h1 nc -zv 10.0.0.3 8080

# Test port 22 pe h4
mininet> h1 nc -zv 10.0.0.4 22
```

3. **Script Python pentru discovery:**
```python
import socket

def port_scan(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    result = sock.connect_ex((host, port))
    sock.close()
    return result == 0

# Test
for h in range(2, 5):
    for p in [22, 80, 8080]:
        ip = f"10.0.0.{h}"
        status = "OPEN" if port_scan(ip, p) else "closed"
        print(f"{ip}:{p} - {status}")
```

### Rezultate așteptate
```
10.0.0.2:22 - closed
10.0.0.2:80 - OPEN
10.0.0.2:8080 - closed
10.0.0.3:22 - closed
10.0.0.3:80 - closed
10.0.0.3:8080 - OPEN
10.0.0.4:22 - OPEN
10.0.0.4:80 - closed
10.0.0.4:8080 - closed
```

---

## Scenariul 5: Captură și Analiză Protocol

### Obiectiv
Capturarea și analiza traficului HTTP în Mininet.

### Pași de execuție

1. **Setup:**
```bash
sudo python3 topo_10_base.py
mininet> h2 python3 -m http.server 8000 &
```

2. **Captură pe switch:**
```bash
# În alt terminal (nu în Mininet CLI)
sudo tcpdump -i s1-eth1 -w /tmp/s1_capture.pcap
```

3. **Generare trafic:**
```bash
mininet> h1 curl http://10.0.0.2:8000/
mininet> h1 curl http://10.0.0.2:8000/index.html
mininet> h1 curl -X POST -d "test=data" http://10.0.0.2:8000/
```

4. **Analiză cu tshark:**
```bash
# După oprire captură
tshark -r /tmp/s1_capture.pcap -Y "http.request"
tshark -r /tmp/s1_capture.pcap -Y "http.response"
tshark -r /tmp/s1_capture.pcap -q -z http,stat
```

### Rezultate așteptate
- Cereri HTTP GET și POST vizibile
- Response codes (200, 404, etc.)
- Statistici HTTP (requests, responses)

---

## Exerciții independente

### Exercițiul 1: Latență variabilă
Modificați scenariul 3 pentru a testa latențe de 10ms, 50ms, 100ms, 200ms și creați un grafic al timpului de răspuns.

### Exercițiul 2: Multiple cereri concurente
Folosind `curl` sau Python `requests`, trimiteți 10 cereri simultane și măsurați throughput-ul.

### Exercițiul 3: Simulare timeout
Adăugați latență de 5 secunde și observați comportamentul cu `curl --max-time 2`.

### Exercițiul 4: Packet loss
```bash
tc qdisc add dev h1-eth0 root netem loss 10%
```
Observați retransmisiile TCP în captură.

---

## Cleanup

După experimente:
```bash
mininet> exit
sudo mn -c
```

---

## Referințe

- Mininet Documentation: http://mininet.org/walkthrough/
- tc netem manual: `man tc-netem`
- tshark documentation: https://www.wireshark.org/docs/man-pages/tshark.html

---

*Material elaborat pentru disciplina Rețele de Calculatoare, ASE București, 2025-2026*

*Revolvix&Hypotheticalandrei*
