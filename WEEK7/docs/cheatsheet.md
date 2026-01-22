# Fișă rapidă — captură și filtrare (Săptămâna 7)

## Comenzi rapide (rețea)

Afișează interfețe și adrese:

```bash
ip -br a
ip link show
ip route
```

Conexiuni și socket-uri:

```bash
ss -tulpn            # TCP/UDP listening, cu procese
ss -tan              # Toate conexiunile TCP
ss -uan              # Toate conexiunile UDP
```

Test conectivitate:

```bash
ping -c 3 10.0.7.200
traceroute -n 10.0.7.200
nc -zv 10.0.7.200 9090      # Test port TCP
nc -uzv 10.0.7.200 9091     # Test port UDP
```

## Captură cu tcpdump

Captură pe o interfață (salvare în pcap):

```bash
sudo tcpdump -i any -w artifacts/demo.pcap
sudo tcpdump -i eth0 -w capture.pcap
```

Captură cu filtre:

```bash
# TCP către portul aplicației
sudo tcpdump -i any 'tcp port 9090' -nn -w tcp.pcap

# UDP către portul aplicației
sudo tcpdump -i any 'udp port 9091' -nn -w udp.pcap

# Doar SYN (începuturi de conexiune)
sudo tcpdump -i any 'tcp[tcpflags] & tcp-syn != 0' -nn

# Trafic de la/către un host specific
sudo tcpdump -i any 'host 10.0.7.11' -nn
```

Afișare live (fără salvare):

```bash
sudo tcpdump -i any 'tcp port 9090' -nn -vv
```

## Analiză cu tshark

Citire pcap:

```bash
tshark -r artifacts/demo.pcap
tshark -r artifacts/demo.pcap | head -20
tshark -r artifacts/demo.pcap | wc -l
```

Filtre display (cele mai utile):

```bash
# Handshake TCP (SYN)
tshark -r demo.pcap -Y 'tcp.flags.syn == 1'

# Doar SYN fără ACK (inițiere conexiune)
tshark -r demo.pcap -Y 'tcp.flags.syn == 1 and tcp.flags.ack == 0'

# RST (reset)
tshark -r demo.pcap -Y 'tcp.flags.reset == 1'

# FIN (închidere)
tshark -r demo.pcap -Y 'tcp.flags.fin == 1'

# UDP către port specific
tshark -r demo.pcap -Y 'udp.dstport == 9091'

# Trafic între două IP-uri
tshark -r demo.pcap -Y 'ip.addr == 10.0.7.11 and ip.addr == 10.0.7.200'

# O anumită conexiune TCP (stream)
tshark -r demo.pcap -Y 'tcp.stream == 0'
```

Extragere câmpuri specifice:

```bash
tshark -r demo.pcap -T fields -e frame.time -e ip.src -e ip.dst -e tcp.flags -e tcp.dstport
```

Statistici:

```bash
tshark -r demo.pcap -z io,phs -q       # Protocol hierarchy
tshark -r demo.pcap -z conv,tcp -q     # Conversații TCP
tshark -r demo.pcap -z endpoints,ip -q # Endpoint-uri IP
```

## iptables (firewall)

Afișează reguli:

```bash
sudo iptables -S                           # Format script
sudo iptables -L -n -v                     # Format tabel cu contoare
sudo iptables -L FORWARD -n -v --line-numbers  # Doar FORWARD, cu numere
```

Operații de bază:

```bash
# Adaugă regulă
sudo iptables -A FORWARD -p tcp --dport 9090 -j ACCEPT
sudo iptables -A FORWARD -p tcp --dport 22 -j REJECT
sudo iptables -A FORWARD -p udp --dport 9091 -j DROP

# Șterge regulă după număr
sudo iptables -D FORWARD 3

# Setează politică implicită
sudo iptables -P FORWARD DROP
sudo iptables -P FORWARD ACCEPT
```

Reset complet (atenție!):

```bash
sudo iptables -F                  # Flush toate regulile
sudo iptables -P INPUT ACCEPT
sudo iptables -P FORWARD ACCEPT
sudo iptables -P OUTPUT ACCEPT
```

Folosește kitul:

```bash
sudo python3 python/apps/firewallctl.py --profile baseline
sudo python3 python/apps/firewallctl.py --profile block_tcp_9090
sudo python3 python/apps/firewallctl.py --profile block_udp_9091
sudo python3 python/apps/firewallctl.py --dry-run --profile baseline  # Vezi fără să aplici
```

## Diferențe cheie

| Acțiune | Comportament | Când folosești |
|---------|--------------|----------------|
| DROP | Ignoră silențios, client timeout | Securitate (nu dezvălui firewall) |
| REJECT | Trimite RST/ICMP, client eroare rapidă | Debugging, UX |
| ACCEPT | Lasă să treacă | Trafic permis |

| Chain | Trafic | Exemplu |
|-------|--------|---------|
| INPUT | Destinat acestui host | SSH către firewall |
| OUTPUT | Generat de acest host | Firewall face DNS query |
| FORWARD | Trece prin acest host | h1 → fw → h2 |

## Validare rapidă

Rulează demo-ul automat și verifică:

```bash
./scripts/run_all.sh
./tests/smoke_test.sh
cat artifacts/validation.txt
```

Verifică că totul e curat la final:

```bash
./scripts/cleanup.sh
ss -tulpn | grep -E '9090|9091'   # Ar trebui să fie gol
```
