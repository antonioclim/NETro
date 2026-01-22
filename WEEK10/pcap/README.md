# Sample PCAP Files pentru Săptămâna 10

## Descriere

Acest director conține exemple de capturi de pachete pentru analiza protocoalelor DNS, SSH și FTP.

## Generare PCAP-uri

Deoarece fișierele PCAP binare nu pot fi incluse direct în repository-ul git, se oferă scripturi pentru generarea lor.

### DNS Capture

```bash
# În containerul debug sau pe host
tshark -i any -f "port 5353" -w dns_sample.pcap &
sleep 1

# Generează trafic
dig @dns-server -p 5353 myservice.lab.local
dig @dns-server -p 5353 api.lab.local

# Oprește captura
pkill tshark
```

### SSH Capture

```bash
# Captură handshake SSH
tshark -i any -f "port 2222" -w ssh_sample.pcap &
sleep 1

# Conectare SSH (handshake)
ssh -p 2222 labuser@localhost -o "StrictHostKeyChecking=no" exit

pkill tshark
```

### FTP Capture

```bash
# Captură sesiune FTP
tshark -i any -f "port 2121" -w ftp_sample.pcap &
sleep 1

# Sesiune FTP
python3 << 'EOF'
from ftplib import FTP
ftp = FTP()
ftp.connect('localhost', 2121)
ftp.login('labftp', 'labftp')
ftp.nlst()
ftp.quit()
EOF

pkill tshark
```

## Conținut așteptat

### dns_sample.pcap
- DNS Query pentru myservice.lab.local
- DNS Query pentru api.lab.local
- DNS Response cu IP-uri

### ssh_sample.pcap
- SSH Protocol Version Exchange
- SSH Key Exchange Init
- SSH New Keys

### ftp_sample.pcap
- FTP 220 Service Ready
- USER labftp
- 331 User name okay
- PASS labftp
- 230 User logged in
- NLST
- 150 Opening data connection
- 226 Transfer complete

## Analiză cu tshark

```bash
# Statistici DNS
tshark -r dns_sample.pcap -q -z dns,tree

# Statistici FTP
tshark -r ftp_sample.pcap -Y "ftp.request.command"

# Afișare conversație
tshark -r ftp_sample.pcap -z follow,tcp,ascii,0
```

## Filtre Wireshark utile

| Protocol | Filtru Display |
|----------|----------------|
| DNS queries | `dns.flags.response == 0` |
| DNS responses | `dns.flags.response == 1` |
| SSH | `ssh` |
| FTP commands | `ftp.request.command` |
| FTP responses | `ftp.response.code` |

---

*Revolvix&Hypotheticalandrei*
