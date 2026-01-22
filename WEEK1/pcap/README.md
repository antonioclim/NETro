# 📁 Capturi de Rețea - Exemple

Acest director conține fișiere de captură `.pcap` pentru analiză și studiu.

## Fișiere Incluse

| Fișier | Descriere | Pachete | Generare |
|--------|-----------|---------|----------|
| `example_tcp_handshake.pcap` | TCP 3-way handshake complet | ~10 | Automată |
| `example_udp_dns.pcap` | Interogare DNS (UDP) | ~4 | Automată |
| `example_http_request.pcap` | Request HTTP simplu | ~15 | Automată |
| `example_mixed_traffic.pcap` | Trafic mixt demonstrativ | ~100 | Automată |

## Generare Automată

Rulează script-ul de captură demonstrativă:

```bash
# Din directorul starterkit
./scripts/capture_demo.sh

# Sau cu make
make capture-demo
```

Script-ul va genera automat toate fișierele `.pcap` de mai sus.

## Generare Manuală

### TCP Handshake

```bash
# Terminal 1: Pornește captura
tshark -i lo -f "port 9999" -w pcap/example_tcp_handshake.pcap &
TSHARK_PID=$!

# Terminal 2: Server
nc -l -p 9999 &
NC_SERVER_PID=$!
sleep 1

# Terminal 3: Client - conectare și mesaj
echo "Hello TCP" | nc localhost 9999
sleep 1

# Oprire captură
kill $TSHARK_PID $NC_SERVER_PID 2>/dev/null
```

### UDP (DNS Query)

```bash
# Captură DNS
tshark -i any -f "port 53" -c 10 -w pcap/example_udp_dns.pcap &
sleep 1

# Generează query DNS
dig google.com
dig +short github.com

# Așteaptă captură
sleep 2
```

### HTTP Request

```bash
# Captură HTTP (necesită server local)
tshark -i lo -f "port 8080" -w pcap/example_http_request.pcap &
TSHARK_PID=$!

# Server HTTP simplu (Python)
python3 -m http.server 8080 &
HTTP_PID=$!
sleep 1

# Request
curl http://localhost:8080/
sleep 1

kill $TSHARK_PID $HTTP_PID 2>/dev/null
```

## Analiză Capturi

### Vizualizare conținut

```bash
# Citire simplă
tshark -r pcap/example_tcp_handshake.pcap

# Cu detalii
tshark -r pcap/example_tcp_handshake.pcap -V

# Doar TCP flags
tshark -r pcap/example_tcp_handshake.pcap -T fields -e frame.number -e tcp.flags.str

# Export CSV
tshark -r pcap/example_tcp_handshake.pcap -T fields -e frame.number -e frame.time_relative -e ip.src -e ip.dst -e tcp.srcport -e tcp.dstport -e tcp.flags.str -E header=y -E separator=, > analysis.csv
```

### Filtrare

```bash
# Doar SYN packets
tshark -r pcap/example_tcp_handshake.pcap -Y "tcp.flags.syn==1"

# Doar DNS responses
tshark -r pcap/example_udp_dns.pcap -Y "dns.flags.response==1"

# HTTP GET requests
tshark -r pcap/example_http_request.pcap -Y "http.request.method==GET"
```

## Structura unui PCAP Valid

Un fișier `.pcap` pentru laborator trebuie să conțină:

1. **Minim 50 pachete** pentru analiză statistică
2. **Cel puțin 2 protocoale diferite** (ex: TCP + UDP)
3. **O conversație completă** (handshake → date → close)
4. **Timestamp-uri valide** pentru calcul latență

## Verificare Integritate

```bash
# Verifică fișier valid
capinfos pcap/example_tcp_handshake.pcap

# Output așteptat:
# File name:           pcap/example_tcp_handshake.pcap
# File type:           Wireshark - pcapng
# Number of packets:   X
# File size:           Y bytes
```

## Utilizare în Exerciții Python

```python
# Citire cu scapy
from scapy.all import rdpcap

packets = rdpcap('pcap/example_tcp_handshake.pcap')
print(f"Pachete: {len(packets)}")

for pkt in packets:
    if pkt.haslayer('TCP'):
        flags = pkt['TCP'].flags
        print(f"TCP Flags: {flags}")
```

## Note Importante

⚠️ **Permisiuni**: Captura pe interfețe reale necesită permisiuni root sau membru grup `wireshark`.

⚠️ **Interfață loopback**: Pentru exerciții locale folosim `-i lo` (loopback), nu interfața de rețea externă.

⚠️ **Filtre BPF**: Filtrele de captură (`-f`) sunt diferite de filtrele de afișare (`-Y`).

---

*Generat pentru Rețele de Calculatoare - Săptămâna 1*
*Revolvix&Hypotheticalandrei*
