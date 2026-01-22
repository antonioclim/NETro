# Laborator 10: Experimentare Practică cu DNS, SSH, FTP

**Disciplina:** Rețele de Calculatoare  
**Program:** Informatică Economică, ASE București  
**Durată estimată:** 90 minute  

---

## Obiectivul laboratorului

Acest laborator transformă cunoștințele teoretice în **experiență practică** prin:

- Configurarea și testarea unui server DNS custom
- Automatizarea conexiunilor SSH cu Paramiko
- Implementarea transfer de fișiere FTP programatic
- Utilizarea tunelării SSH pentru acces la servicii interne

---

## Cerințe preliminare

### Software necesar

- Docker Engine ≥ 20.10
- Docker Compose ≥ 2.20
- Python ≥ 3.9
- Terminal cu acces la bash

### Verificare mediu

```bash
# Verificare versiuni
docker --version
docker compose version
python3 --version

# Clonare/descărcare starterkit
cd ~/S10_starterkit
make check
```

---

## Step 0: Pregătire mediu

### 0.1 Structura directorului

```
S10_starterkit/
├── docker/
│   ├── docker-compose.yml
│   ├── dns-server/
│   ├── ssh-server/
│   ├── ssh-client/
│   ├── ftp-server/
│   └── debug/
├── python/
│   └── exercises/
├── scripts/
└── Makefile
```

### 0.2 Pornire infrastructură

```bash
# Metodă 1: Cu Makefile
make docker-up

# Metodă 2: Direct docker compose
cd docker/
docker compose up -d --build

# Verificare
docker compose ps
```

**Output așteptat:**
```
NAME           SERVICE       STATUS
dns-server     dns-server    running
ftp-server     ftp-server    running
ssh-client     ssh-client    running
ssh-server     ssh-server    running
debug          debug         running
web            web           running
```

### 0.3 Verificare rețea

```bash
docker network ls | grep labnet
docker network inspect docker_labnet
```

---

## Step 1: Explorare DNS Docker

> **👥 Pair Programming:** Pentru Step 1-4, lucrați în perechi. Schimbați rolurile Driver/Navigator la fiecare Step.

### 1.1 DNS implicit Docker

Conectează-te la containerul debug:

```bash
docker compose exec debug sh
```

**🔮 PREDICȚIE:** Înainte de a rula:
- Ce IP va returna `dig web +short`? Notează pe hârtie.
- Va fi un IP din range-ul 172.x.x.x? De ce?

Testează DNS-ul implicit Docker:

```bash
# Rezolvare nume serviciu → IP container
dig web +short
dig ssh-server +short
dig ftp-server +short

# Verifică serverul DNS folosit
cat /etc/resolv.conf
```

**Întrebare:** De unde știe containerul să rezolve `web` în IP-ul corect?

### 1.2 DNS custom

**🔮 PREDICȚIE:** 
- `dig @dns-server` va returna același IP ca `dig web`?
- Ce diferență fundamentală există între cele două?

Testează serverul DNS custom:

```bash
# Query către serverul nostru DNS (port 5353)
dig @dns-server -p 5353 myservice.lab.local
dig @dns-server -p 5353 api.lab.local +short

# Compară cu DNS implicit
dig @127.0.0.11 myservice.lab.local  # Nu va funcționa!
```

**Observație:** DNS-ul Docker nu știe de `myservice.lab.local` – doar serverul nostru custom.

### 1.3 Captură trafic DNS

```bash
# În containerul debug, captură pachete DNS
tcpdump -i any port 5353 -vvv &

# Generează trafic
dig @dns-server -p 5353 myservice.lab.local

# Oprește captura
pkill tcpdump
```

**What-if:** Ce se întâmplă dacă interogăm un domeniu inexistent?

```bash
dig @dns-server -p 5353 inexistent.lab.local
```

---

## Step 2: SSH și Paramiko

### 2.1 Conectare SSH manuală

**🔮 PREDICȚIE:**
- Câte secunde va dura prima conexiune SSH?
- Dar a doua conexiune (imediat după)?

Din containerul debug sau de pe host:

```bash
# De pe host (port 2222 mapat)
ssh -p 2222 labuser@localhost
# Parolă: labpass

# Sau din container debug (port intern 22)
ssh labuser@ssh-server
```

Comenzi de test:
```bash
uname -a
hostname -I
ls -la /home/labuser/
exit
```

### 2.2 Automatizare cu Paramiko

Rulează clientul Paramiko pregătit:

```bash
docker compose exec ssh-client python3 /app/paramiko_client.py
```

**Output așteptat:**
```
[INFO] Connecting to ssh-server:22...
[INFO] Connected successfully
[INFO] Executing: uname -a
Linux ssh-server 5.15.0...
[INFO] Executing: hostname -I
172.20.0.4
[INFO] SFTP: Uploading test file...
[INFO] SFTP: Verifying upload...
[SUCCESS] File uploaded and verified
```

### 2.3 Exercițiu: Script SSH propriu

Creează un script Python pe host:

```python
#!/usr/bin/env python3
"""Exercițiu: Conectare SSH și listare fișiere"""

import paramiko

def main():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        # Conectare
        client.connect(
            hostname="localhost",
            port=2222,
            username="labuser",
            password="labpass"
        )
        print("[OK] Connected")
        
        # Execută comandă
        stdin, stdout, stderr = client.exec_command("ls -la /home/labuser/")
        output = stdout.read().decode()
        print(output)
        
    finally:
        client.close()

if __name__ == "__main__":
    main()
```

Rulează:
```bash
python3 my_ssh_script.py
```

---

## Step 3: Port Forwarding SSH

### 3.1 Problema

Serviciul `web` rulează pe portul 8000, dar **nu este expus** pe host (verifică `docker compose ps`).

### 3.2 Soluția: Local Forward

**🔮 PREDICȚIE:**
- Ce va returna `curl http://localhost:9000/` dacă tunelul SSH e activ?
- Ce eroare vei primi dacă tunelul NU e activ?

```bash
# Terminal 1: Crează tunel
ssh -L 9000:web:8000 -p 2222 labuser@localhost -N
# Parolă: labpass
# -N = nu executa comandă, doar tunelul
```

```bash
# Terminal 2: Testează
curl http://localhost:9000/
curl http://localhost:9000/api/users
```

**Explicație:**
- `localhost:9000` → tunel SSH → `ssh-server` → `web:8000`
- Traficul este criptat între tine și ssh-server

### 3.3 Captură trafic prin tunel

```bash
# În containerul debug
tcpdump -i any host web and port 8000 -A &

# De pe host, prin tunel
curl http://localhost:9000/

# Observă cererea HTTP în captură
```

**What-if:** Ce se întâmplă dacă oprești tunelul și încerci curl?

---

## Step 4: FTP Transfer

### 4.1 Test cu client FTP linie de comandă

```bash
# De pe host
ftp localhost 2121
# User: labftp
# Pass: labftp

ftp> ls
ftp> pwd
ftp> cd uploads
ftp> bye
```

### 4.2 Transfer programatic Python

**🔮 PREDICȚIE:**
- Vei vedea parola în captură tcpdump? În ce format?
- Ce comenzi FTP vor apărea (USER, PASS, ...)?

Creează scriptul `ftp_test.py`:

```python
#!/usr/bin/env python3
"""Exercițiu: Transfer FTP programatic"""

from ftplib import FTP
import io

def main():
    ftp = FTP()
    ftp.connect('localhost', 2121)
    ftp.login('labftp', 'labftp')
    
    print(f"Director curent: {ftp.pwd()}")
    print(f"Conținut: {ftp.nlst()}")
    
    # Upload test
    content = f"Test creat la {__import__('datetime').datetime.now()}\n"
    data = io.BytesIO(content.encode())
    ftp.storbinary('STOR uploads/my_test.txt', data)
    print("[OK] Fișier uploadat")
    
    # Verificare
    print(f"Conținut uploads/: {ftp.nlst('uploads')}")
    
    ftp.quit()

if __name__ == "__main__":
    main()
```

### 4.3 Captură trafic FTP

```bash
# În containerul debug
tcpdump -i any port 2121 -A 2>&1 | head -100 &

# De pe host
python3 ftp_test.py
```

**Observație:** Comenzile FTP sunt vizibile în plaintext (USER, PASS, STOR).

**What-if:** Cum ar arăta traficul dacă am folosi FTPS (FTP over TLS)?

---

## Step 5: Integrare completă

### 5.1 Script de automatizare

Creează `lab10_integration.py`:

```python
#!/usr/bin/env python3
"""
Laborator 10: Script de integrare
Demonstrează: DNS query, SSH exec, FTP transfer
"""

import socket
import paramiko
from ftplib import FTP
import json

def test_dns():
    """Test DNS custom"""
    print("\n=== Test DNS ===")
    try:
        # Query UDP către DNS server
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(2.0)
        
        # Construire query DNS simplu pentru A record
        # (în practică, folosește dnspython sau dnslib)
        result = socket.gethostbyname("localhost")
        print(f"[OK] DNS resolution working: localhost → {result}")
        return True
    except Exception as e:
        print(f"[FAIL] DNS: {e}")
        return False

def test_ssh():
    """Test SSH + SFTP"""
    print("\n=== Test SSH ===")
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect("localhost", 2222, "labuser", "labpass")
        
        stdin, stdout, stderr = client.exec_command("hostname")
        hostname = stdout.read().decode().strip()
        print(f"[OK] SSH connected, hostname: {hostname}")
        
        client.close()
        return True
    except Exception as e:
        print(f"[FAIL] SSH: {e}")
        return False

def test_ftp():
    """Test FTP"""
    print("\n=== Test FTP ===")
    try:
        ftp = FTP()
        ftp.connect('localhost', 2121)
        ftp.login('labftp', 'labftp')
        
        files = ftp.nlst()
        print(f"[OK] FTP connected, files: {files}")
        
        ftp.quit()
        return True
    except Exception as e:
        print(f"[FAIL] FTP: {e}")
        return False

def main():
    results = {
        "dns": test_dns(),
        "ssh": test_ssh(),
        "ftp": test_ftp()
    }
    
    print("\n=== Sumar ===")
    print(json.dumps(results, indent=2))
    
    if all(results.values()):
        print("\n✓ Toate testele au trecut!")
        return 0
    else:
        print("\n✗ Unele teste au eșuat")
        return 1

if __name__ == "__main__":
    exit(main())
```

### 5.2 Rulare și verificare

```bash
python3 lab10_integration.py
```

---

## Step 6: Exerciții Non-Cod

Aceste exerciții dezvoltă înțelegerea conceptuală **fără a scrie cod**.

### 6.1 Parsons Problem: SSH Handshake

**Instrucțiuni:** Ordonează corect pașii unui handshake SSH (fără a scrie cod):

```
[ ] Serverul trimite cheia sa publică
[ ] Clientul verifică fingerprint-ul cheii
[ ] Se stabilește canalul criptat
[ ] Clientul inițiază conexiunea TCP pe port 22
[ ] Se negociază algoritmii de criptare
[ ] Clientul trimite credențialele (user/pass sau cheie)
[ ] Serverul verifică credențialele
[ ] Sesiunea interactivă începe
```

<details>
<summary>✅ Ordine corectă</summary>

1. Clientul inițiază conexiunea TCP pe port 22
2. Se negociază algoritmii de criptare
3. Serverul trimite cheia sa publică
4. Clientul verifică fingerprint-ul cheii
5. Se stabilește canalul criptat
6. Clientul trimite credențialele
7. Serverul verifică credențialele
8. Sesiunea interactivă începe
</details>

---

### 6.2 Trace Exercise: Captură DNS

**Instrucțiuni:** Analizează această captură Wireshark și răspunde:

```
Frame 1: 74 bytes on wire
Ethernet II: Src: 02:42:ac:14:00:02, Dst: 02:42:ac:14:00:03
IPv4: Src: 172.20.0.2, Dst: 172.20.0.3
UDP: Src Port: 54321, Dst Port: 5353
DNS: Standard query 0x1234 A myservice.lab.local

Frame 2: 90 bytes on wire
Ethernet II: Src: 02:42:ac:14:00:03, Dst: 02:42:ac:14:00:02
IPv4: Src: 172.20.0.3, Dst: 172.20.0.2
UDP: Src Port: 5353, Dst Port: 54321
DNS: Standard query response 0x1234 A myservice.lab.local A 10.10.10.10
```

**Întrebări:**
1. Care este IP-ul clientului DNS?
2. Care este IP-ul serverului DNS?
3. Ce tip de înregistrare a fost cerută?
4. Care este răspunsul?
5. De ce portul sursă al clientului (54321) e diferit de portul destinație (5353)?

<details>
<summary>✅ Răspunsuri</summary>

1. 172.20.0.2 (sursa în Frame 1)
2. 172.20.0.3 (destinația în Frame 1, sursa în Frame 2)
3. A (IPv4 address)
4. 10.10.10.10
5. Portul sursă e efemer (ales aleatoriu de client), portul destinație e well-known (5353 pentru DNS custom)
</details>

---

### 6.3 Debugging Exercise: SSH Connection Failed

**Scenariu:** Colegul tău primește această eroare și îți cere ajutor:

```
$ ssh -p 2222 labuser@localhost
ssh: connect to host localhost port 2222: Connection refused
```

**Sarcină:** Scrie **5 comenzi de diagnostic** pe care le-ai rula, în ordine, și ce informații aștepți de la fiecare.

| # | Comandă | Ce verifici |
|---|---------|-------------|
| 1 | | |
| 2 | | |
| 3 | | |
| 4 | | |
| 5 | | |

<details>
<summary>✅ Răspunsuri posibile</summary>

| # | Comandă | Ce verifici |
|---|---------|-------------|
| 1 | `docker compose ps` | Containerul ssh-server rulează? |
| 2 | `docker compose logs ssh-server` | Erori la pornire sshd? |
| 3 | `ss -tulpn \| grep 2222` | Portul e în LISTEN pe host? |
| 4 | `nc -zv localhost 2222` | Conectivitate TCP la port? |
| 5 | `ssh -v -p 2222 labuser@localhost` | Detalii handshake SSH |

**Alte comenzi valide:** `docker network ls`, `docker network inspect`, `ping`, `telnet`
</details>

---

### 6.4 Code Reading: Ce face acest script?

**Instrucțiuni:** Citește codul și răspunde fără a-l rula:

```python
import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.sendto(b'\x12\x34\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00'
            b'\x03www\x07example\x03com\x00\x00\x01\x00\x01',
            ('8.8.8.8', 53))
data, addr = sock.recvfrom(512)
print(f"Response from {addr}: {len(data)} bytes")
```

**Întrebări:**
1. Ce protocol de transport folosește? (TCP/UDP)
2. La ce serviciu se conectează?
3. Ce domeniu interogează?
4. De ce buffer-ul de primire e 512 bytes?

<details>
<summary>✅ Răspunsuri</summary>

1. **UDP** (SOCK_DGRAM)
2. **DNS** (port 53, server 8.8.8.8 - Google DNS)
3. **www.example.com** (encoded în format DNS: lungime + label)
4. **512 bytes** e limita tradițională pentru răspunsuri DNS over UDP (RFC 1035)
</details>

---

## Step 7: Cleanup

### 7.1 Oprire servicii

```bash
# Cu Makefile
make docker-down

# Sau direct
cd docker/
docker compose down -v
```

### 7.2 Verificare cleanup

```bash
docker ps
docker network ls | grep labnet
```

---

## Rezultate așteptate

### DNS
```
$ dig @dns-server -p 5353 myservice.lab.local +short
10.10.10.10
```

### SSH
```
$ ssh -p 2222 labuser@localhost "uname -a"
Linux ssh-server 5.15.0-91-generic #101-Ubuntu SMP...
```

### FTP
```
>>> ftp.nlst()
['welcome.txt', 'uploads']
```

### Port Forward
```
$ curl http://localhost:9000/
{"message": "Welcome to lab web server"}
```

---

## Troubleshooting

### "Connection refused"
```bash
# Verifică că serviciile rulează
docker compose ps
docker compose logs <service-name>
```

### "Name resolution failed"
```bash
# Verifică rețeaua Docker
docker network inspect docker_labnet
```

### SSH "Host key verification failed"
```bash
ssh-keygen -R localhost
ssh-keygen -R "[localhost]:2222"
```

### FTP "Passive mode failed"
```bash
# Verifică maparea porturilor pasive în docker-compose.yml
# Porturile 30000-30009 trebuie expuse
```

---

## Evaluare și livrabile

### Livrabil: `lab10_report.md`

Creați un raport markdown cu:

1. **Capturi ecran** ale output-urilor pentru fiecare step
2. **Răspunsuri** la întrebările "What-if"
3. **Scriptul** `lab10_integration.py` funcțional
4. **Exercițiile non-cod** (Step 6) completate
5. **Observații** personale și dificultăți întâmpinate

### Criterii notare

| Criteriu | Puncte |
|----------|--------|
| DNS funcțional + query custom | 2 |
| SSH + Paramiko automation | 2 |
| FTP transfer programatic | 2 |
| Port forwarding demonstrat | 2 |
| Raport complet și corect | 2 |
| **Total** | **10** |

---

## Extensii opționale (bonus)

1. **DNS recursiv**: Modifică serverul DNS să forwardeze query-uri necunoscute către 8.8.8.8
2. **SFTP upload/download**: Adaugă la script transfer fișiere prin SFTP
3. **FTP over TLS**: Configurează FTPS și observă diferența în captură
4. **Multi-hop tunnel**: SSH prin două servere în cascadă

---

*Material elaborat pentru disciplina Rețele de Calculatoare, ASE București, 2025-2026*

*Revolvix&Hypotheticalandrei*
