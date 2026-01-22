# Cheatsheet: tcpdump
## Ghid rapid pentru captură și analiză pachete

**Săptămâna 4 - Nivelul Fizic și Legătura de Date**  
*Revolvix&Hypotheticalandrei*

---

## Sintaxa de bază

```bash
tcpdump [opțiuni] [expresie filtru]
```

---

## Opțiuni esențiale

| Opțiune | Descriere | Exemplu |
|---------|-----------|---------|
| `-i <if>` | Interfața de captură | `-i eth0`, `-i any` |
| `-n` | Nu rezolva nume DNS | `-n` (mai rapid) |
| `-nn` | Nu rezolva nici porturi | `-nn` |
| `-c <N>` | Capturează N pachete | `-c 100` |
| `-w <file>` | Salvează în fișier pcap | `-w capture.pcap` |
| `-r <file>` | Citește din fișier pcap | `-r capture.pcap` |
| `-v`, `-vv`, `-vvv` | Verbose (detalii) | `-vv` |
| `-X` | Hex + ASCII dump | `-X` |
| `-xx` | Include header Ethernet | `-xx` |
| `-A` | Doar ASCII (pentru HTTP) | `-A` |
| `-s <len>` | Snaplen (bytes capturat) | `-s 1500` |
| `-e` | Afișează header L2 (MAC) | `-e` |
| `-q` | Output minimal | `-q` |

---

## Expresii de filtru comune

### După protocol
```bash
tcpdump -i eth0 tcp           # Doar TCP
tcpdump -i eth0 udp           # Doar UDP
tcpdump -i eth0 icmp          # Doar ICMP (ping)
tcpdump -i eth0 arp           # Doar ARP
tcpdump -i eth0 ip            # Doar IPv4
tcpdump -i eth0 ip6           # Doar IPv6
```

### După port
```bash
tcpdump -i eth0 port 80                    # Port 80 (orice protocol)
tcpdump -i eth0 tcp port 443               # TCP port 443
tcpdump -i eth0 udp port 53                # UDP port 53 (DNS)
tcpdump -i eth0 portrange 5400-5402        # Range de porturi
tcpdump -i eth0 'tcp port 5400 or 5401'    # Porturi multiple
```

### După adresă IP
```bash
tcpdump -i eth0 host 192.168.1.100         # Sursă SAU destinație
tcpdump -i eth0 src host 10.0.0.1          # Doar sursă
tcpdump -i eth0 dst host 10.0.0.2          # Doar destinație
tcpdump -i eth0 net 192.168.1.0/24         # Întreaga rețea
```

### După adresă MAC
```bash
tcpdump -i eth0 ether host 00:11:22:33:44:55
tcpdump -i eth0 ether src 00:11:22:33:44:55
tcpdump -i eth0 ether broadcast            # Broadcast frames
```

### Combinații (operatori)
```bash
tcpdump -i eth0 'host 10.0.0.1 and port 80'
tcpdump -i eth0 'tcp and (port 80 or port 443)'
tcpdump -i eth0 'not port 22'              # Exclude SSH
tcpdump -i eth0 'src net 10.0.0.0/8 and dst port 5400'
```

---

## Exemple practice pentru Săptămâna 4

### Captură ARP
```bash
# Toate pachetele ARP
sudo tcpdump -i eth0 -nn arp

# ARP cu detalii și MAC-uri
sudo tcpdump -i eth0 -e -nn arp

# Salvare pentru analiză ulterioară
sudo tcpdump -i eth0 -w arp_capture.pcap arp
```

### Captură protocol TEXT (port 5400)
```bash
# Captură și afișare ASCII
sudo tcpdump -i eth0 -A -nn tcp port 5400

# Captură cu hex dump
sudo tcpdump -i eth0 -X -nn tcp port 5400

# Doar primele 10 pachete
sudo tcpdump -i eth0 -c 10 -nn tcp port 5400
```

### Captură protocol BINARY (port 5401)
```bash
# Hex dump pentru analiza header-ului binar
sudo tcpdump -i eth0 -xx -nn tcp port 5401

# Verbose pentru a vedea detalii TCP
sudo tcpdump -i eth0 -vv -nn tcp port 5401
```

### Captură UDP senzori (port 5402)
```bash
# UDP pe portul senzorilor
sudo tcpdump -i eth0 -nn udp port 5402

# Cu hex dump pentru structura datagramei
sudo tcpdump -i eth0 -X -nn udp port 5402
```

### Captură Ethernet frames
```bash
# Afișare adrese MAC
sudo tcpdump -i eth0 -e -nn

# Doar broadcast/multicast
sudo tcpdump -i eth0 -e 'ether broadcast or ether multicast'
```

---

## Analiza TCP flags

### Filtrare după TCP flags
```bash
# Doar SYN (inițiere conexiune)
tcpdump -i eth0 'tcp[tcpflags] & tcp-syn != 0'

# Doar SYN-ACK
tcpdump -i eth0 'tcp[tcpflags] == tcp-syn|tcp-ack'

# Doar FIN (închidere conexiune)
tcpdump -i eth0 'tcp[tcpflags] & tcp-fin != 0'

# Doar RST (reset)
tcpdump -i eth0 'tcp[tcpflags] & tcp-rst != 0'

# Doar PUSH (date urgente)
tcpdump -i eth0 'tcp[tcpflags] & tcp-push != 0'
```

### Afișare flags în output
```bash
# Verbose pentru a vedea flags-urile
tcpdump -i eth0 -vv tcp port 5400
```

Flags în output:
- `S` = SYN
- `S.` = SYN-ACK
- `F` = FIN
- `R` = RST
- `P` = PUSH
- `.` = ACK
- `U` = URG

---

## Citire și analiza fișiere pcap

```bash
# Citire simplă
tcpdump -r capture.pcap

# Cu filtre
tcpdump -r capture.pcap tcp port 5400

# Statistici (primul și ultimul pachet)
tcpdump -r capture.pcap -c 1
tcpdump -r capture.pcap -c 1 -tt

# Export în format text
tcpdump -r capture.pcap -nn > output.txt
```

---

## Troubleshooting comun

### Erori și soluții

| Eroare | Cauză | Soluție |
|--------|-------|---------|
| "Permission denied" | Lipsă sudo | Rulați cu `sudo` |
| "No such device" | Interfață greșită | Verificați cu `ip link` |
| "packet dropped by kernel" | Buffer plin | Măriți cu `-B <size>` |
| "can't parse filter" | Sintaxă greșită | Verificați ghilimelele |

### Verificare interfețe disponibile
```bash
tcpdump -D                    # Lista interfețe
ip link show                  # Alternativă
```

### Verificare permisiuni
```bash
# Verificați dacă utilizatorul are permisiuni
getcap /usr/bin/tcpdump

# Adăugare capability (alternativă la sudo)
sudo setcap cap_net_raw,cap_net_admin=eip /usr/bin/tcpdump
```

---

## One-liners utile

```bash
# Cele mai active IP-uri (top 10)
tcpdump -r capture.pcap -nn | awk '{print $3}' | cut -d. -f1-4 | sort | uniq -c | sort -rn | head

# Conversații TCP unice
tcpdump -r capture.pcap -nn tcp | awk '{print $3, $5}' | sort -u

# Dimensiuni pachete
tcpdump -r capture.pcap -nn -q | awk '{print $NF}' | sort -n | uniq -c

# Timestamp diferențe (latență)
tcpdump -r capture.pcap -nn -ttt
```

---

## Resurse adiționale

- Manual: `man tcpdump`
- Expresii de filtru: `man pcap-filter`
- Wireshark (GUI): poate deschide fișiere .pcap create de tcpdump
