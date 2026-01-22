# Cheatsheet: tshark (Wireshark CLI)
## Ghid rapid pentru captură și analiză avansată

**Săptămâna 4 - Nivelul Fizic și Legătura de Date**  
*Revolvix&Hypotheticalandrei*

---

## Ce este tshark?

`tshark` este versiunea command-line a Wireshark. Oferă:
- Disecție completă a protocoalelor
- Statistici avansate
- Export în multiple formate
- Integrare în scripturi

---

## Sintaxa de bază

```bash
tshark [opțiuni] [filtru captură] [-Y filtru display]
```

**Diferența importantă:**
- Filtru captură (`-f`): folosește sintaxă BPF (ca tcpdump)
- Filtru display (`-Y`): folosește sintaxă Wireshark (mai expresivă)

---

## Opțiuni esențiale

| Opțiune | Descriere | Exemplu |
|---------|-----------|---------|
| `-i <if>` | Interfață captură | `-i eth0` |
| `-f <filter>` | Filtru captură (BPF) | `-f "tcp port 80"` |
| `-Y <filter>` | Filtru display (Wireshark) | `-Y "http.request"` |
| `-c <N>` | Capturează N pachete | `-c 100` |
| `-w <file>` | Salvează în fișier | `-w capture.pcap` |
| `-r <file>` | Citește din fișier | `-r capture.pcap` |
| `-V` | Verbose (toate câmpurile) | `-V` |
| `-x` | Hex dump | `-x` |
| `-T <format>` | Format output | `-T json`, `-T fields` |
| `-e <field>` | Extrage câmp specific | `-e ip.src` |
| `-q` | Quiet (doar statistici) | `-q` |

---

## Filtre display (Wireshark syntax)

### Filtre după protocol
```bash
tshark -r capture.pcap -Y "tcp"
tshark -r capture.pcap -Y "udp"
tshark -r capture.pcap -Y "arp"
tshark -r capture.pcap -Y "icmp"
tshark -r capture.pcap -Y "eth"
```

### Filtre după adrese
```bash
# IP
tshark -Y "ip.addr == 10.0.0.1"
tshark -Y "ip.src == 10.0.0.1"
tshark -Y "ip.dst == 10.0.0.2"

# MAC
tshark -Y "eth.addr == 00:11:22:33:44:55"
tshark -Y "eth.src == 00:11:22:33:44:55"
tshark -Y "eth.dst == ff:ff:ff:ff:ff:ff"  # Broadcast
```

### Filtre după porturi
```bash
tshark -Y "tcp.port == 5400"
tshark -Y "tcp.srcport == 5400"
tshark -Y "tcp.dstport == 5401"
tshark -Y "udp.port == 5402"
```

### Filtre TCP flags
```bash
tshark -Y "tcp.flags.syn == 1"           # SYN
tshark -Y "tcp.flags.syn == 1 and tcp.flags.ack == 0"  # Doar SYN
tshark -Y "tcp.flags.fin == 1"           # FIN
tshark -Y "tcp.flags.rst == 1"           # RST
tshark -Y "tcp.flags.push == 1"          # PUSH
```

### Filtre combinate
```bash
tshark -Y "ip.src == 10.0.0.1 and tcp.port == 5400"
tshark -Y "tcp.port == 5400 or tcp.port == 5401"
tshark -Y "not arp"
tshark -Y "tcp.port == 5400 and tcp.len > 0"  # Cu payload
```

---

## Exemple practice Săptămâna 4

### Analiza ARP
```bash
# Toate pachetele ARP
tshark -i eth0 -Y "arp"

# ARP Request vs Reply
tshark -r capture.pcap -Y "arp.opcode == 1"  # Request
tshark -r capture.pcap -Y "arp.opcode == 2"  # Reply

# Extrage perechi IP-MAC
tshark -r capture.pcap -Y "arp" -T fields \
    -e arp.src.proto_ipv4 -e arp.src.hw_mac \
    -e arp.dst.proto_ipv4 -e arp.dst.hw_mac
```

### Analiza protocol TEXT (port 5400)
```bash
# Captură cu filtre
tshark -i eth0 -f "tcp port 5400" -w text_capture.pcap

# Afișare verbose
tshark -r text_capture.pcap -V

# Doar payload-ul TCP
tshark -r text_capture.pcap -Y "tcp.port == 5400" \
    -T fields -e tcp.payload

# Decodare payload ca text
tshark -r text_capture.pcap -Y "tcp.port == 5400 and tcp.len > 0" \
    -T fields -e data.text
```

### Analiza protocol BINARY (port 5401)
```bash
# Hex dump pentru header binar
tshark -r binary_capture.pcap -x

# Extrage primii 14 bytes (header)
tshark -r binary_capture.pcap -Y "tcp.port == 5401 and tcp.len >= 14" \
    -T fields -e tcp.payload | cut -c1-28

# Conversație completă
tshark -r binary_capture.pcap -Y "tcp.port == 5401" -z follow,tcp,ascii,0
```

### Analiza UDP senzori (port 5402)
```bash
# Captură UDP
tshark -i eth0 -f "udp port 5402" -w udp_capture.pcap

# Statistici per sursă
tshark -r udp_capture.pcap -Y "udp.port == 5402" -z endpoints,udp

# Extrage datagramele
tshark -r udp_capture.pcap -Y "udp.port == 5402" \
    -T fields -e ip.src -e udp.payload
```

### Analiza Ethernet/L2
```bash
# Toate frame-urile cu adrese MAC
tshark -r capture.pcap -T fields -e eth.src -e eth.dst -e eth.type

# Doar broadcast
tshark -r capture.pcap -Y "eth.dst == ff:ff:ff:ff:ff:ff"

# Distribuție tipuri Ethernet
tshark -r capture.pcap -z io,stat,0,"COUNT(eth.type)"
```

---

## Statistici avansate (-z)

### Statistici generale
```bash
# Ierarhie protocoale
tshark -r capture.pcap -q -z io,phs

# Conversații TCP
tshark -r capture.pcap -q -z conv,tcp

# Conversații IP
tshark -r capture.pcap -q -z conv,ip

# Endpoints
tshark -r capture.pcap -q -z endpoints,tcp
```

### Statistici I/O
```bash
# Pachete pe interval de timp
tshark -r capture.pcap -q -z io,stat,1

# Bytes per secundă
tshark -r capture.pcap -q -z io,stat,1,"BYTES()"

# Filtrare statistici
tshark -r capture.pcap -q -z io,stat,1,"COUNT() tcp.port==5400"
```

### Follow stream
```bash
# Follow TCP stream (conversație completă)
tshark -r capture.pcap -z follow,tcp,ascii,0

# Follow stream ca hex
tshark -r capture.pcap -z follow,tcp,hex,0

# Follow UDP
tshark -r capture.pcap -z follow,udp,ascii,0
```

---

## Export în formate diverse

### JSON
```bash
tshark -r capture.pcap -T json > output.json
tshark -r capture.pcap -Y "tcp" -T json > tcp_only.json
```

### CSV (câmpuri specifice)
```bash
tshark -r capture.pcap -T fields \
    -e frame.time -e ip.src -e ip.dst -e tcp.port \
    -E header=y -E separator=, > output.csv
```

### EK (Elasticsearch compatible)
```bash
tshark -r capture.pcap -T ek > output.json
```

### PDML (XML detaliat)
```bash
tshark -r capture.pcap -T pdml > output.xml
```

---

## Extragere câmpuri specifice

### Sintaxă
```bash
tshark -r file.pcap -T fields -e <field1> -e <field2> ...
```

### Câmpuri comune
```bash
# IP și porturi
tshark -r capture.pcap -T fields \
    -e ip.src -e ip.dst -e tcp.srcport -e tcp.dstport

# MAC adrese
tshark -r capture.pcap -T fields \
    -e eth.src -e eth.dst

# TCP details
tshark -r capture.pcap -T fields \
    -e tcp.seq -e tcp.ack -e tcp.flags -e tcp.len

# Timestamps
tshark -r capture.pcap -T fields \
    -e frame.time -e frame.time_delta -e frame.len
```

### Opțiuni formatare
```bash
-E header=y          # Include header cu numele câmpurilor
-E separator=,       # Separator (implicit TAB)
-E quote=d           # Quotes duble pentru strings
-E occurrence=a      # Toate aparițiile (nu doar prima)
```

---

## Disecție protocoale custom

### Decodare forțată
```bash
# Decodează portul 5400 ca HTTP
tshark -r capture.pcap -d tcp.port==5400,http

# Decodează ca data generică
tshark -r capture.pcap -d tcp.port==5401,data
```

### Lua scripting (avansat)
```bash
# Cu script Lua custom
tshark -r capture.pcap -X lua_script:my_dissector.lua
```

---

## Comparație tcpdump vs tshark

| Aspect | tcpdump | tshark |
|--------|---------|--------|
| Viteză captură | Mai rapid | Mai lent |
| Disecție protocoale | Minimală | Completă |
| Statistici | Limitate | Extensive |
| Export formate | Doar pcap/text | JSON, CSV, XML, etc. |
| Memorie | Eficient | Mai mult overhead |
| Scripturi | BPF simplu | Wireshark + Lua |
| Utilizare tipică | Captură rapidă | Analiză detaliată |

**Recomandare:** Capturați cu tcpdump, analizați cu tshark/Wireshark.

---

## Troubleshooting

### Erori comune

| Eroare | Cauză | Soluție |
|--------|-------|---------|
| "Couldn't run dumpcap" | Permisiuni | Rulați cu sudo |
| "No such device" | Interfață greșită | `tshark -D` pentru listă |
| "Display filter invalid" | Sintaxă greșită | Verificați în Wireshark GUI |

### Verificare
```bash
# Lista interfețe
tshark -D

# Versiune și protocoale suportate
tshark -v

# Verificare filtru display valid
tshark -Y "tcp.port == 80" -r /dev/null
```

---

## Resurse

- Manual: `man tshark`
- Wiki: https://wiki.wireshark.org/TShark
- Display filters: https://wiki.wireshark.org/DisplayFilters
- Sample captures: https://wiki.wireshark.org/SampleCaptures
