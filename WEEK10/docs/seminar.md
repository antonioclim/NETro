# Seminar 10: Servicii de Rețea în Containere Docker

## DNS, SSH, FTP – Orchestrare și Automatizare

**Disciplina:** Rețele de Calculatoare  
**Program:** Informatică Economică, ASE București  
**Semestrul:** 2, Anul 3  

---

## Ce vom învăța

La finalul acestui seminar, vei putea:

1. **Explica** mecanismul DNS intern Docker și limitările acestuia
2. **Implementa** un server DNS minimal în Python folosind biblioteca dnslib
3. **Configura** și utiliza SSH programatic prin Paramiko
4. **Demonstra** SSH port forwarding pentru acces la servicii interne
5. **Automatiza** transfer de fișiere prin FTP cu pyftpdlib
6. **Orchestra** servicii multiple cu Docker Compose pe o rețea privată

---

## De ce contează

DNS, SSH și FTP stau **la baza** infrastructurii moderne de rețea:

- **DNS** permite descoperirea serviciilor într-un cluster (Kubernetes, Docker Swarm)
- **SSH** oferă acces securizat pentru administrare și tunelare trafic
- **FTP** rămâne relevant pentru transfer bulk de fișiere în medii enterprise

Înțelegerea lor la nivel programatic este esențială pentru:
- Automatizare CI/CD și deployment
- Scripting infrastructură și provisionare
- Debugging probleme de conectivitate între servicii

---

## Prerechizite

Din **săptămânile anterioare** se presupun:
- Concepte TCP/UDP, porturi, sockets (S3-S8)
- Docker și docker-compose (noțiuni de bază)
- Python pentru scripting de rețea

---

## 1. DNS – Domain Name System

### Recapitulare conceptuală

DNS traduce **nume în adrese IP**:

```
www.example.com → 93.184.216.34
```

### Analogie: Cartea de telefon

DNS funcționează ca o **carte de telefon digitală**:
- Cartea: baza de date DNS
- Numele persoanei: domeniul (example.com)
- Numărul de telefon: adresa IP (93.184.216.34)
- Căutarea: query DNS

În Docker, fiecare container primește automat o "intrare în cartea de telefon" cu numele serviciului din docker-compose.yml.

### Tipuri de înregistrări DNS

| Tip | Descriere | Exemplu |
|-----|-----------|---------|
| **A** | Nume → IPv4 | `example.com → 93.184.216.34` |
| **AAAA** | Nume → IPv6 | `example.com → 2606:2800:...` |
| **CNAME** | Alias | `www → example.com` |
| **MX** | Mail server | `example.com → mail.example.com` |
| **NS** | Nameserver | `example.com → ns1.example.com` |
| **TXT** | Text arbitrar | SPF, DKIM, verificări |
| **SRV** | Servicii | `_http._tcp.example.com → server:80` |

### DNS în Docker

Docker oferă **DNS intern automat** pe rețelele user-defined:

```yaml
# docker-compose.yml
services:
  web:
    image: nginx
  api:
    image: python:3.11
    # Din container api: curl http://web/ funcționează!
```

**Mecanismul:**
1. Fiecare serviciu primește un nume DNS = numele serviciului
2. Serverul DNS Docker ascultă pe `127.0.0.11`
3. Rezolvarea funcționează **doar în aceeași rețea Docker**

### Limitări DNS Docker

- Nu suportă zone custom
- Nu oferă TTL configurabil
- Nu permite înregistrări MX, SRV, TXT custom

**Soluția:** Server DNS propriu pentru scenarii avansate.

> **Notă practică:** Am văzut studenți care petrec ore debugând DNS când de fapt containerul era în altă rețea Docker. Verifică ÎNTÂI `docker network ls` și `docker network inspect`.

### Server DNS minimal cu Python (dnslib)

```python
from dnslib import DNSRecord, QTYPE, RR, A
from dnslib.server import DNSServer, BaseResolver

class CustomResolver(BaseResolver):
    RECORDS = {
        "myservice.lab.local": "10.10.10.10",
        "api.lab.local": "10.10.10.20",
    }
    
    def resolve(self, request, handler):
        reply = request.reply()
        qname = str(request.q.qname).rstrip('.')
        qtype = QTYPE[request.q.qtype]
        
        if qtype == "A" and qname in self.RECORDS:
            reply.add_answer(RR(
                qname, QTYPE.A, ttl=300,
                rdata=A(self.RECORDS[qname])
            ))
        
        return reply

if __name__ == "__main__":
    resolver = CustomResolver()
    server = DNSServer(resolver, port=5353, address="0.0.0.0")
    server.start()
```

### Testare DNS

**🔮 Întreabă studenții ÎNAINTE de a rula:**
- "Ce IP estimați pentru `dig web`?"
- "Dar pentru `dig @dns-server myservice.lab.local`?"
- Colectează răspunsuri (show of hands / poll).

```bash
# dig - instrument recomandat
dig @localhost -p 5353 myservice.lab.local
dig +short @8.8.8.8 example.com

# nslookup - alternativă simplă
nslookup example.com 8.8.8.8
```

---

## 2. SSH – Secure Shell

### Recapitulare conceptuală

SSH oferă:
- **Conexiune securizată** la servere remote
- **Execuție comenzi** la distanță
- **Transfer fișiere** (SFTP, SCP)
- **Tunelare trafic** (port forwarding)

### Conectare SSH de bază

```bash
# Conectare interactivă
ssh user@host

# Cu port non-standard
ssh -p 2222 user@host

# Execuție comandă (neinteractiv)
ssh user@host "uname -a && df -h"
```

### Autentificare cu chei SSH

```bash
# Generare pereche de chei
ssh-keygen -t ed25519 -C "email@example.com"

# Copiere cheie publică pe server
ssh-copy-id user@host

# Conectare fără parolă
ssh user@host
```

### Port Forwarding (Tunelare)

### Analogie: Tunelul secret

SSH Port Forwarding e ca un **tunel secret prin munți**:
- Intrarea tunelului: portul tău local (localhost:9000)
- Ieșirea tunelului: serviciul destinație (web:8000)
- Garda de la intrare: ssh-server (verifică credențialele)
- Tot ce trece prin tunel e **criptat** - nimeni din exterior nu poate vedea

```
[Tu] ---(tunel criptat)---> [ssh-server] ---(rețea internă)---> [web:8000]
       localhost:9000                                            
```

**Local forward** (`-L`): Acces la serviciu remote ca și cum ar fi local

```bash
# localhost:9000 → server:8080 (prin tunel SSH)
ssh -L 9000:localhost:8080 user@server
# Acum: curl http://localhost:9000 accesează server:8080
```

**Remote forward** (`-R`): Expune serviciu local pe server remote

```bash
# server:9000 → localhost:3000
ssh -R 9000:localhost:3000 user@server
# Pe server: curl http://localhost:9000 accesează mașina ta pe :3000
```

**Dynamic forward** (`-D`): Proxy SOCKS5

```bash
ssh -D 1080 user@server
# Configurezi browser-ul să folosească SOCKS5 localhost:1080
```

### SSH programatic cu Paramiko

**🔮 Predicție colectivă:**
- "Cât va dura execuția Paramiko? 1s? 5s? 30s?"
- "Ce output va apărea primul?"

```python
import paramiko

# Conectare cu parolă
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect("ssh-server", port=22, username="labuser", password="labpass")

# Execuție comandă
stdin, stdout, stderr = client.exec_command("uname -a")
print(stdout.read().decode())

# Transfer SFTP
sftp = client.open_sftp()
sftp.put("local_file.txt", "/remote/path/file.txt")
sftp.get("/remote/path/file.txt", "downloaded.txt")
sftp.close()

client.close()
```

---

## 3. FTP – File Transfer Protocol

### Recapitulare conceptuală

FTP folosește **două conexiuni**:
- **Port 21**: Canal de control (comenzi)
- **Port 20** sau porturi pasive: Canal de date

### Mod activ vs mod pasiv

### Analogie: Pizza delivery

**Mod activ (problematic):**
- Tu (clientul) suni la pizzerie și zici: "Vino la adresa mea să-mi aduci pizza"
- Dar stai într-un bloc cu interfon (NAT) - delivery-ul nu poate intra

**Mod pasiv (funcțional):**
- Tu suni și pizzeria zice: "Vino tu la noi la ghișeul X să ridici"
- Tu poți ieși din bloc fără probleme

În FTP: modul activ cere serverului să se conecteze la client → NAT blochează.
Modul pasiv: clientul se conectează la server → funcționează prin NAT.

**Mod activ:**
1. Clientul trimite PORT cu adresa sa
2. Serverul se conectează la client pentru date
3. **Problemă:** NAT/firewall blochează conexiunea inversă

**Mod pasiv (recomandat):**
1. Clientul trimite PASV
2. Serverul deschide port și trimite adresa
3. Clientul se conectează pentru date
4. **Funcționează** prin NAT

### Server FTP cu pyftpdlib

```python
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

# Autorizare
authorizer = DummyAuthorizer()
authorizer.add_user("labftp", "labftp", "/srv/ftp", perm="elradfmw")
authorizer.add_anonymous("/srv/ftp/public", perm="elr")

# Handler
handler = FTPHandler
handler.authorizer = authorizer
handler.passive_ports = range(30000, 30010)

# Server
server = FTPServer(("0.0.0.0", 2121), handler)
server.serve_forever()
```

### Client FTP în Python

```python
from ftplib import FTP

ftp = FTP()
ftp.connect('localhost', 2121)
ftp.login('labftp', 'labftp')

# Listare
print(ftp.nlst())

# Download
with open('downloaded.txt', 'wb') as f:
    ftp.retrbinary('RETR remote_file.txt', f.write)

# Upload
with open('local_file.txt', 'rb') as f:
    ftp.storbinary('STOR uploads/file.txt', f)

ftp.quit()
```

---

## 4. Infrastructura Docker pentru Seminar

### Arhitectura

```
┌──────────────────────────────────────────────────────────────┐
│                   Rețea Docker (labnet)                      │
│                      172.20.0.0/24                           │
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐      │
│  │   web    │  │   dns-   │  │   ssh-   │  │   ftp-  │      │
│  │  :8000   │  │  server  │  │  server  │  │  server │      │
│  │ (Flask)  │  │  :5353   │  │   :22    │  │  :2121  │      │
│  └──────────┘  └──────────┘  └──────────┘  └─────────┘      │
│                                                              │
│  ┌──────────┐  ┌──────────┐                                  │
│  │   ssh-   │  │  debug   │                                  │
│  │  client  │  │ (tools)  │                                  │
│  └──────────┘  └──────────┘                                  │
└──────────────────────────────────────────────────────────────┘
       │              │              │              │
       │              │              │              │
    Host ports:    :5353/udp       :2222          :2121
```

### Pornire infrastructură

```bash
cd docker/
docker compose up -d --build

# Verificare servicii
docker compose ps

# Logs
docker compose logs -f dns-server
```

### Intrare în container debug

```bash
docker compose exec debug sh

# Acum ai la dispoziție: dig, curl, ssh, ftp, tcpdump, python3
```

---

## 5. Lucru în perechi (Pair Programming)

### Organizare

Pentru sarcinile practice din acest seminar, lucrați în **perechi** cu roluri alternante:

| Rol | Responsabilitate | Durata |
|-----|------------------|--------|
| **Driver** | Tastează codul, execută comenzi | 10-15 min |
| **Navigator** | Gândește strategia, verifică erori, consultă documentație | 10-15 min |

### Reguli

1. **Schimbați rolurile** la fiecare sarcină sau la fiecare 15 minute
2. **Navigatorul NU tastează** - doar ghidează verbal
3. **Driver-ul explică** ce face în timp ce tastează
4. **Întrebările** se adresează mai întâi partenerului, apoi instructorului

### Atribuire perechi

```
Perechea 1: Student A (Driver) + Student B (Navigator)
Perechea 2: Student C (Driver) + Student D (Navigator)
...
```

### Sarcini pentru Pair Programming

| Sarcină | Driver începe cu | Timp total |
|---------|------------------|------------|
| DNS exploration | Studentul cu laptopul mai rapid | 15 min |
| SSH + Paramiko | Studentul care NU a folosit SSH înainte | 20 min |
| Port Forwarding | Alternați la mijloc | 15 min |
| FTP transfer | Studentul cu experiență Python | 15 min |

### Checkpoint perechi

La finalul fiecărei sarcini, ambii parteneri trebuie să poată răspunde:
- "Ce comandă am rulat?"
- "Ce output am obținut?"
- "De ce a funcționat/nu a funcționat?"

---

## 6. Sarcini practice

> **👥 Pair Programming:** Pentru sarcinile 1-4, lucrați în perechi. Schimbați rolurile Driver/Navigator la fiecare sarcină.

### Sarcina 1: Testare DNS

**Obiectiv:** Înțelegerea DNS implicit Docker vs DNS custom.

**🔮 PREDICȚIE:** Înainte de a rula:
- Ce IP va returna `dig web +short`? Notează.
- Va fi din range-ul 172.x.x.x? De ce?

```bash
# În containerul debug
docker compose exec debug sh

# Test DNS implicit (nume serviciu → IP container)
dig web
dig ssh-server

# Test DNS custom (zone proprii)
dig @dns-server -p 5353 myservice.lab.local
dig @dns-server -p 5353 api.lab.local +short
```

**🔮 PREDICȚIE:** 
- `dig @dns-server` va returna același IP ca `dig web`?
- Ce diferență fundamentală există?

**Întrebări:**
1. Ce IP returnează `dig web`?
2. Ce IP returnează query-ul către dns-server pentru `myservice.lab.local`?
3. Care este diferența fundamentală între cele două?

### Sarcina 2: Automatizare SSH cu Paramiko

**Obiectiv:** Conectare SSH și automatizare operații.

**🔮 PREDICȚIE:**
- Câte secunde va dura prima conexiune SSH?
- Dar a doua conexiune imediat după?

```bash
# Conectare manuală (test)
ssh -p 2222 labuser@localhost
# Parola: labpass

# Automatizare cu Paramiko
docker compose exec ssh-client python3 /app/paramiko_client.py

# Verificare rezultate
docker compose exec ssh-server ls -la /home/labuser/storage/
```

### Sarcina 3: Transfer FTP programatic

**Obiectiv:** Upload/download fișiere prin FTP.

```python
# Script Python pe host
from ftplib import FTP

ftp = FTP()
ftp.connect('localhost', 2121)
ftp.login('labftp', 'labftp')

# Listare
print("Director curent:", ftp.pwd())
print("Fișiere:", ftp.nlst())

# Upload test
import io
data = io.BytesIO(b"Test content\n")
ftp.storbinary('STOR uploads/test.txt', data)

ftp.quit()
```

### Sarcina 4: Port Forwarding SSH

**Obiectiv:** Acces la serviciu intern prin tunel SSH.

Serviciul `web` (port 8000) **nu este expus** pe host. Îl accesăm prin tunel:

**🔮 PREDICȚIE:**
- Ce va returna `curl http://localhost:9000/` cu tunelul activ?
- Ce eroare vei primi fără tunel?

```bash
# Terminal 1: Creare tunel
ssh -L 9000:web:8000 -p 2222 labuser@localhost
# Parola: labpass

# Terminal 2: Test acces
curl http://localhost:9000/
```

---

## 7. Întrebări Peer Instruction

Folosiți aceste întrebări în format PI: vot individual → discuție perechi → revot → explicație.

### 🗳️ PI-S1: DNS Docker

**Întrebare:** Din containerul `debug`, rulezi `dig web`. De unde știe Docker să rezolve acest nume?

A) Din fișierul `/etc/hosts` al containerului  
B) De la serverul DNS intern Docker (127.0.0.11)  
C) De la serverul DNS custom pe port 5353  
D) Din variabile de mediu Docker  

<details>
<summary>📋 Note instructor</summary>

**Răspuns corect:** B

**Explicație:** Docker injectează un resolver local pe 127.0.0.11 care știe toate serviciile din docker-compose. Verifică cu `cat /etc/resolv.conf` în container.

**Distractori:**
- **A:** /etc/hosts conține doar hostname-ul propriu, nu alte servicii
- **C:** DNS-ul custom e pentru zone proprii, nu pentru servicii Docker
- **D:** Variabilele de mediu nu conțin mapări DNS
</details>

---

### 🗳️ PI-S2: SSH Tunneling

**Scenariu:** Rulezi: `ssh -L 9000:web:8000 -p 2222 labuser@localhost`

**Ce se întâmplă când accesezi `http://localhost:9000` din browser?**

A) Browser-ul se conectează direct la containerul `web`  
B) Traficul trece prin tunelul SSH și ajunge la `web:8000`  
C) SSH-ul deschide portul 8000 pe mașina ta locală  
D) Primești eroare pentru că `web` nu e un hostname valid  

<details>
<summary>📋 Note instructor</summary>

**Răspuns corect:** B

**Flow complet:** Browser → localhost:9000 → tunel SSH criptat → ssh-server → web:8000

**Distractori:**
- **A:** Nu direct - trece prin SSH
- **C:** Portul local e 9000, nu 8000
- **D:** `web` e valid în rețeaua Docker unde e ssh-server
</details>

---

### 🗳️ PI-S3: FTP Mod Pasiv

**De ce folosim mod pasiv FTP în Docker și nu mod activ?**

A) Modul pasiv este mai rapid  
B) Modul activ necesită ca serverul să inițieze conexiunea către client, ceea ce nu funcționează prin NAT  
C) Modul activ nu este implementat în pyftpdlib  
D) Docker nu suportă modul activ  

<details>
<summary>📋 Note instructor</summary>

**Răspuns corect:** B

**Explicație detaliată:**
- Activ: CLIENT trimite PORT, SERVER se conectează la CLIENT pentru date → NAT/firewall blochează conexiunea inversă
- Pasiv: CLIENT trimite PASV, CLIENT se conectează la SERVER → funcționează prin NAT

**Distractori:**
- **A:** Viteza e similară
- **C:** pyftpdlib suportă ambele moduri
- **D:** Docker suportă ambele, problema e NAT-ul
</details>

---

## 8. Debugging și troubleshooting

### DNS nu rezolvă

```bash
# Verificare serviciu DNS
docker compose logs dns-server

# Test direct
dig @127.0.0.1 -p 5353 myservice.lab.local

# Verificare rețea
docker network inspect docker_labnet
```

### SSH connection refused

```bash
# Verificare serviciu SSH
docker compose logs ssh-server

# Test conectivitate
nc -zv localhost 2222

# Verbose SSH
ssh -v -p 2222 labuser@localhost
```

### FTP passive mode issues

```bash
# Verificare porturi pasive
docker compose logs ftp-server

# Verificare porturi expuse
docker compose ps ftp-server

# Test cu lftp (suportă debug)
lftp -d -u labftp,labftp ftp://localhost:2121
```

---

## 9. Rezultate așteptate

### DNS

```
$ dig @dns-server -p 5353 myservice.lab.local +short
10.10.10.10

$ dig @dns-server -p 5353 api.lab.local +short
10.10.10.20
```

### SSH Paramiko

```
[INFO] Connecting to ssh-server:22...
[INFO] Connected successfully
[INFO] Executing: uname -a
Linux ssh-server 5.15.0-91-generic #101-Ubuntu SMP...
[INFO] Executing: hostname -I
172.20.0.4 
[INFO] SFTP: Uploading test file...
[INFO] SFTP: Download and verify...
[INFO] All operations completed successfully
```

### FTP

```
>>> ftp.nlst()
['welcome.txt', 'uploads']
>>> ftp.pwd()
'/'
```

---

## 10. Greșeli frecvente

| Problemă | Cauză | Soluție |
|----------|-------|---------|
| `Connection refused` | Serviciu nepornit | `docker compose up -d` |
| `Name not resolved` | DNS greșit sau rețea diferită | Verifică `docker network ls` |
| `Permission denied` | User/parolă greșite | Verifică credențialele în compose |
| `Passive mode failed` | Porturi pasive neexpuse | Adaugă port range în compose |
| `Host key verification` | Cheie SSH schimbată | `ssh-keygen -R localhost` |

---

## 11. Consolidare și exerciții

### Exercițiu 1: DNS custom (Începător)
Adaugă o înregistrare nouă `database.lab.local → 10.10.10.30` în serverul DNS.

### Exercițiu 2: SSH tunnel pentru web (Intermediar)
Creează un tunel SSH care permite accesul la serviciul FTP (port 2121) prin SSH.

### Exercițiu 3: Automatizare completă (Intermediar)
Scrie un script Python care: se conectează SSH, creează un fișier, îl descarcă prin SFTP.

### Exercițiu 4: DNS recursive (Avansat)
Modifică serverul DNS să facă forward pentru domenii necunoscute către 8.8.8.8.

### Exercițiu 5: Monitorizare transfer (Avansat)
Folosește tshark pentru a captura traficul FTP și a identifica comenzile transmise.

### Exercițiu Challenge: Multi-hop SSH
Configurează acces la un serviciu prin **două** tuneluri SSH în cascadă.

---

## 12. Contribuția la proiectul de echipă

### Artefact livrabil S10

Creați un script `lab10_automation.py` care:

1. Verifică disponibilitatea serviciilor (DNS, SSH, FTP)
2. Execută query DNS pentru un domeniu custom
3. Se conectează SSH și execută o comandă
4. Transferă un fișier prin FTP
5. Generează un raport JSON cu rezultatele

### Criterii de evaluare

- [ ] Funcționalitate completă (4p)
- [ ] Tratare erori (2p)
- [ ] Documentare cod (2p)
- [ ] Output structurat (2p)

---

## Resurse adiționale

- Docker Networking: https://docs.docker.com/network/
- Paramiko Documentation: https://docs.paramiko.org/
- pyftpdlib Documentation: https://pyftpdlib.readthedocs.io/
- dnslib on PyPI: https://pypi.org/project/dnslib/
- SSH Port Forwarding Explained: https://www.ssh.com/academy/ssh/tunneling

---

*Material elaborat pentru disciplina Rețele de Calculatoare, ASE București, 2025-2026*

*Revolvix&Hypotheticalandrei*
