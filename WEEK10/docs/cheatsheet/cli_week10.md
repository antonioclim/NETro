# CLI Cheatsheet - Săptămâna 10

## Servicii de Rețea în Containere (DNS, SSH, FTP)

### Plan Porturi

| Serviciu | Port | Protocol | Credențiale |
|----------|------|----------|-------------|
| DNS | 5353 | UDP | - |
| SSH | 2222 | TCP | labuser / labpass |
| FTP | 2121 | TCP | labftp / labftp |
| FTP PASV | 30000-30009 | TCP | - |
| HTTP | 8000 | TCP | - |

### Plan IP (Docker Network)

| Container | IP | Descriere |
|-----------|-----|-----------|
| web | 172.20.0.10 | Server HTTP simplu |
| dns-server | 172.20.0.53 | DNS custom (dnslib) |
| ftp-server | 172.20.0.21 | FTP (pyftpdlib) |
| ssh-server | 172.20.0.22 | OpenSSH |
| ssh-client | 172.20.0.100 | Client Paramiko |
| debug | 172.20.0.200 | Container diagnosticare |

---

## Docker Compose

### Pornire / Oprire

```bash
# Pornire servicii
cd docker && docker compose up -d

# Oprire servicii
cd docker && docker compose down

# Rebuild (după modificări)
cd docker && docker compose build --no-cache

# Status
docker compose ps

# Log-uri
docker compose logs -f [service_name]
```

### Intrare în Containere

```bash
# Container debug (cu toate uneltele)
docker compose exec debug sh

# SSH server
docker compose exec ssh-server bash

# DNS server
docker compose exec dns-server sh
```

---

## DNS

### Test DNS Implicit Docker

```bash
# Din containerul debug
docker compose exec debug dig +short web
# Rezultat: 172.20.0.10

docker compose exec debug dig +short dns-server
# Rezultat: 172.20.0.53
```

### Test DNS Custom

```bash
# Din containerul debug
docker compose exec debug dig @dns-server -p 5353 myservice.lab.local
# Rezultat: 10.10.10.10

docker compose exec debug dig @dns-server -p 5353 api.lab.local
# Rezultat: 10.10.10.20

# De pe host (dacă portul este expus)
dig @localhost -p 5353 myservice.lab.local +short
```

### Interogări DNS Avansate

```bash
# Query de tip ANY
dig @dns-server -p 5353 myservice.lab.local ANY

# Query cu trace
dig @dns-server -p 5353 myservice.lab.local +trace

# Reverse lookup (dacă configurat)
dig @dns-server -p 5353 -x 10.10.10.10
```

---

## SSH

### Conectare SSH Standard

```bash
# De pe host
ssh labuser@localhost -p 2222
# Parola: labpass

# Opțiuni utile
ssh -o StrictHostKeyChecking=no labuser@localhost -p 2222
ssh -v labuser@localhost -p 2222  # verbose
```

### Conectare din Container

```bash
# Din debug container
docker compose exec debug ssh labuser@ssh-server
# Parola: labpass
```

### SSH cu Paramiko (Python)

```python
import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('localhost', port=2222, username='labuser', password='labpass')

stdin, stdout, stderr = client.exec_command('ls -la')
print(stdout.read().decode())

client.close()
```

### Executare Comandă Remotă

```bash
ssh labuser@localhost -p 2222 "uname -a"
ssh labuser@localhost -p 2222 "cat /etc/os-release"
```

### SFTP

```bash
sftp -P 2222 labuser@localhost
# Comenzi SFTP: ls, get, put, cd, lcd
```

---

## FTP

### Conectare FTP CLI

```bash
# De pe host
ftp localhost 2121
# User: labftp
# Parola: labftp

# Cu lftp (mai features)
lftp -u labftp,labftp localhost:2121
```

### Conectare din Container

```bash
docker compose exec debug lftp -u labftp,labftp ftp-server:2121
```

### Comenzi FTP

```bash
# În sesiune FTP
ls                  # listare
pwd                 # director curent
cd uploads          # schimbare director
lcd /tmp            # schimbare director local
put file.txt        # upload
get file.txt        # download
mput *.txt          # upload multiple
mget *.txt          # download multiple
delete file.txt     # ștergere
mkdir newdir        # creare director
quit                # ieșire
```

### FTP cu curl

```bash
# Listare
curl ftp://labftp:labftp@localhost:2121/

# Download
curl ftp://labftp:labftp@localhost:2121/file.txt -o file.txt

# Upload
curl -T file.txt ftp://labftp:labftp@localhost:2121/uploads/

# Din container
docker compose exec debug curl ftp://labftp:labftp@ftp-server:2121/
```

### FTP cu Python (ftplib)

```python
from ftplib import FTP

ftp = FTP()
ftp.connect('localhost', 2121)
ftp.login('labftp', 'labftp')

# Listare
ftp.retrlines('LIST')

# Upload
with open('file.txt', 'rb') as f:
    ftp.storbinary('STOR file.txt', f)

# Download
with open('downloaded.txt', 'wb') as f:
    ftp.retrbinary('RETR file.txt', f.write)

ftp.quit()
```

---

## HTTP

### Test HTTP

```bash
# De pe host
curl http://localhost:8000/
curl -I http://localhost:8000/  # doar headere

# Din container
docker compose exec debug curl http://web:8000/
```

---

## Diagnosticare

### Verificare Porturi

```bash
# Porturi în ascultare
ss -tulpn | grep -E "(5353|2222|2121|8000)"

# Sau cu netstat
netstat -tulpn | grep -E "(5353|2222|2121|8000)"
```

### Test Conectivitate

```bash
# TCP
nc -zv localhost 2222
nc -zv localhost 2121
nc -zv localhost 8000

# UDP (DNS)
nc -uzv localhost 5353
```

### Captură Trafic

```bash
# Cu tshark
tshark -i any -f "tcp port 2222 or tcp port 2121 or udp port 5353"

# Cu tcpdump
sudo tcpdump -i any -nn "tcp port 2222 or tcp port 2121 or udp port 5353"

# Salvare în fișier
tshark -i any -w capture.pcap -a duration:60
```

### Debug DNS

```bash
# Verbose query
dig @localhost -p 5353 myservice.lab.local +all

# DNS lookup cu nslookup
nslookup -port=5353 myservice.lab.local localhost
```

---

## Troubleshooting

### Container nu pornește

```bash
# Verificare erori
docker compose logs [service_name]

# Rebuild
docker compose build --no-cache [service_name]
docker compose up -d [service_name]
```

### Port ocupat

```bash
# Găsire proces
sudo lsof -i :2222
sudo fuser -v 2222/tcp

# Kill proces
sudo fuser -k 2222/tcp
```

### DNS nu răspunde

```bash
# Verificare că serverul DNS rulează
docker compose exec dns-server ps aux

# Test manual
docker compose exec debug nc -uzv dns-server 5353
```

### SSH connection refused

```bash
# Verificare sshd
docker compose exec ssh-server pgrep sshd

# Restart sshd
docker compose exec ssh-server /etc/init.d/ssh restart
```

### FTP passive mode issues

```bash
# Verificare porturi PASV
ss -tulpn | grep -E "3000[0-9]"

# Test explicit passive
curl --ftp-pasv ftp://labftp:labftp@localhost:2121/
```

---

## Comenzi Rapide (Makefile)

```bash
make docker-up      # Pornire
make docker-down    # Oprire
make docker-debug   # Intrare în debug container
make dns-test       # Test DNS
make ssh-test       # Test SSH
make ftp-test       # Test FTP
make verify         # Verificare completă
make demo           # Demo complet
make clean          # Curățare
make reset          # Reset complet
```

---

*Rețele de Calculatoare | ASE București | 2025-2026*
