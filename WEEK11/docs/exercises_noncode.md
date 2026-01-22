# Exerciții Non-Cod – Săptămâna 11

Aceste exerciții dezvoltă înțelegerea conceptelor fără a scrie cod de la zero. Sunt utile pentru:
- Verificarea înțelegerii structurilor de date și protocoale
- Dezvoltarea abilităților de debugging
- Pregătirea pentru examene practice

---

## Exerciții Trace (Urmărire Execuție)

### T1: Trace DNS Packet 🔍

**Nivel**: Intermediar  
**Timp**: 10-15 minute

#### Context
Ai rulat `ex_11_03_dns_client.py --query ase.ro --type A -v` și ai primit acest hexdump al pachetului trimis:

```
[DEBUG] Query packet (28 bytes):
  0000  AB CD 01 00 00 01 00 00  00 00 00 00 03 61 73 65  .............ase
  0010  02 72 6F 00 00 01 00 01                          .ro.....
```

#### Task
Completează tabelul identificând fiecare câmp din pachetul DNS:

| Offset | Bytes (hex) | Valoare (decimal/text) | Câmp DNS | Explicație |
|--------|-------------|------------------------|----------|------------|
| 0x0000 | AB CD | 0xABCD = 43981 | Transaction ID | _________________ |
| 0x0002 | 01 00 | ? | ? | _________________ |
| 0x0004 | 00 01 | ? | ? | _________________ |
| 0x0006 | 00 00 | ? | ? | _________________ |
| 0x0008 | 00 00 | ? | ? | _________________ |
| 0x000A | 00 00 | ? | ? | _________________ |
| 0x000C | 03 | ? | ? | _________________ |
| 0x000D-0x000F | 61 73 65 | ? | ? | _________________ |
| 0x0010 | 02 | ? | ? | _________________ |
| 0x0011-0x0012 | 72 6F | ? | ? | _________________ |
| 0x0013 | 00 | ? | ? | _________________ |
| 0x0014-0x0015 | 00 01 | ? | ? | _________________ |
| 0x0016-0x0017 | 00 01 | ? | ? | _________________ |

#### Hints
- Header DNS = primii 12 bytes (6 câmpuri × 2 bytes)
- Flags 0x0100 = doar bitul RD (Recursion Desired) setat
- QNAME folosește format "label": 1 byte lungime + N bytes text, terminat cu 0x00
- QTYPE: A=1, AAAA=28, MX=15, NS=2
- QCLASS: IN (Internet) = 1

---

### T1 – Soluție (pentru instructor)

| Offset | Bytes | Valoare | Câmp DNS | Explicație |
|--------|-------|---------|----------|------------|
| 0x0000 | AB CD | 43981 | Transaction ID | Identificator unic pentru a potrivi query cu response |
| 0x0002 | 01 00 | 0x0100 | Flags | QR=0 (query), RD=1 (recursion desired) |
| 0x0004 | 00 01 | 1 | QDCOUNT | 1 întrebare în secțiunea Question |
| 0x0006 | 00 00 | 0 | ANCOUNT | 0 răspunsuri (e query, nu response) |
| 0x0008 | 00 00 | 0 | NSCOUNT | 0 înregistrări authority |
| 0x000A | 00 00 | 0 | ARCOUNT | 0 înregistrări additional |
| 0x000C | 03 | 3 | Label length | Următoarele 3 bytes sunt primul label |
| 0x000D-0x000F | 61 73 65 | "ase" | Label text | ASCII: a=0x61, s=0x73, e=0x65 |
| 0x0010 | 02 | 2 | Label length | Următoarele 2 bytes sunt al doilea label |
| 0x0011-0x0012 | 72 6F | "ro" | Label text | ASCII: r=0x72, o=0x6F |
| 0x0013 | 00 | 0 | QNAME terminator | Marchează sfârșitul numelui de domeniu |
| 0x0014-0x0015 | 00 01 | 1 | QTYPE | A record (IPv4 address) |
| 0x0016-0x0017 | 00 01 | 1 | QCLASS | IN (Internet) |

---

### T2: Trace TCP Handshake pentru FTP 🔍

**Nivel**: Începător  
**Timp**: 10 minute

#### Context
Captura tshark pentru o conectare FTP la un server public:

```
No.  Time      Source          Destination     Protocol  Info
1    0.000000  192.168.1.100   93.184.216.34   TCP       SYN       Seq=0
2    0.045123  93.184.216.34   192.168.1.100   TCP       SYN,ACK   Seq=0 Ack=1
3    0.045456  192.168.1.100   93.184.216.34   TCP       ACK       Seq=1 Ack=1
4    0.089234  93.184.216.34   192.168.1.100   FTP       Response: 220 Welcome to FTP
5    0.123456  192.168.1.100   93.184.216.34   FTP       Request:  USER anonymous
6    0.167890  93.184.216.34   192.168.1.100   FTP       Response: 331 Please specify password
7    0.201234  192.168.1.100   93.184.216.34   FTP       Request:  PASS guest@
8    0.245678  93.184.216.34   192.168.1.100   FTP       Response: 230 Login successful
```

#### Task
Răspunde la următoarele întrebări:

1. Care e portul destinație în pachetul #1? ___________
2. Ce tip de conexiune FTP e aceasta (control sau date)? ___________
3. Cine a inițiat conexiunea TCP (client sau server)? ___________
4. Estimează latența până la server (în ms): ___________
5. De ce serverul trimite "220 Welcome" în pachetul #4 înainte ca clientul să trimită vreo comandă FTP?
   
   _____________________________________________________________

6. Ce înseamnă codul "331" din pachetul #6?
   
   _____________________________________________________________

7. Ce s-ar fi întâmplat dacă pachetul #2 ar fi fost `RST` în loc de `SYN,ACK`?
   
   _____________________________________________________________

---

### T2 – Soluție

1. **Port destinație**: 21 (portul standard de control FTP)
2. **Tip conexiune**: Control (pe portul 21; date ar fi pe 20 sau port dinamic)
3. **Inițiator**: Client (192.168.1.100) — el trimite primul SYN
4. **Latență**: ~45ms (timpul între pachetul #1 și #2, SYN→SYN-ACK)
5. **De ce 220 înainte de comandă**: FTP e protocol "server-first" — serverul trimite banner de bun venit imediat după stabilirea conexiunii TCP, înainte ca clientul să ceară ceva
6. **Cod 331**: Răspuns intermediar pozitiv — "Username OK, dar am nevoie de parolă" (seria 3xx = continuare așteptată)
7. **Dacă RST**: Conexiunea ar fi refuzată — serverul nu ascultă pe portul 21 sau firewall-ul blochează

---

## Exerciții Parsons (Reordonare Cod)

### P1: SSH Local Port Forward 🧩

**Nivel**: Intermediar  
**Timp**: 5-8 minute

#### Context
Vrei să accesezi o bază de date PostgreSQL (port 5432) care rulează pe un server intern (`db.internal`, IP 10.0.0.50), dar tu ești în afara rețelei. Ai acces SSH la un bastion server (`bastion.company.com`).

#### Task
Ordonează fragmentele pentru a construi comanda corectă de SSH port forwarding:

```
[ ] -L 5432:db.internal:5432
[ ] user@bastion.company.com
[ ] ssh
[ ] -N
```

#### Hint
Structura generală: `ssh [opțiuni] [forward] [destinație]`

---

### P1 – Soluție

```bash
ssh -L 5432:db.internal:5432 -N user@bastion.company.com
```

**Explicație**:
- `ssh` — comanda
- `-L 5432:db.internal:5432` — local forward: localhost:5432 pe mașina ta → db.internal:5432 prin tunel
- `-N` — nu executa comandă remotă (doar menține tunelul)
- `user@bastion.company.com` — serverul SSH intermediar

**După rulare**: `psql -h localhost -p 5432` se conectează la baza de date internă prin tunel securizat.

---

### P2: Nginx Upstream Configuration 🧩

**Nivel**: Începător  
**Timp**: 5 minute

#### Task
Ordonează blocurile pentru o configurație Nginx cu load balancing weighted (web1 primește de 3 ori mai mult trafic):

```nginx
[ ] }

[ ] server web2:80 weight=1;

[ ] upstream backend_pool {

[ ] server web1:80 weight=3;

[ ] server web3:80 backup;
```

---

### P2 – Soluție

```nginx
upstream backend_pool {
    server web1:80 weight=3;
    server web2:80 weight=1;
    server web3:80 backup;
}
```

**Explicație**:
- `upstream backend_pool {` — deschide blocul de definire a pool-ului
- `server web1:80 weight=3;` — web1 primește 3× mai multe cereri
- `server web2:80 weight=1;` — web2 primește 1× (default)
- `server web3:80 backup;` — web3 e folosit doar când ceilalți sunt down
- `}` — închide blocul

**Distribuție rezultată**: 75% web1, 25% web2, 0% web3 (în condiții normale)

---

### P3: DNS Query Construction 🧩

**Nivel**: Avansat  
**Timp**: 8-10 minute

#### Task
Ordonează pașii pentru a construi manual un pachet DNS query pentru `www.google.com` tip A:

```
[ ] Adaugă QCLASS (00 01 pentru IN)
[ ] Generează Transaction ID random (2 bytes)
[ ] Encodează QNAME: \x03www\x06google\x03com\x00
[ ] Setează QDCOUNT = 1 (00 01)
[ ] Adaugă QTYPE (00 01 pentru A)
[ ] Setează Flags = 0x0100 (RD=1)
[ ] Setează ANCOUNT, NSCOUNT, ARCOUNT = 0
[ ] Concatenează Header + Question
```

---

### P3 – Soluție

Ordinea corectă:

1. **Generează Transaction ID random (2 bytes)** — primul câmp din header
2. **Setează Flags = 0x0100 (RD=1)** — al doilea câmp
3. **Setează QDCOUNT = 1 (00 01)** — avem o întrebare
4. **Setează ANCOUNT, NSCOUNT, ARCOUNT = 0** — toate zero pentru query
5. **Encodează QNAME: \x03www\x06google\x03com\x00** — începe Question section
6. **Adaugă QTYPE (00 01 pentru A)** — ce tip de record căutăm
7. **Adaugă QCLASS (00 01 pentru IN)** — clasa Internet
8. **Concatenează Header + Question** — pachetul final

---

## Exerciții Debugging

### D1: De Ce Nu Merge? — DNS Client 🐛

**Nivel**: Intermediar  
**Timp**: 10 minute

#### Cod cu probleme

```python
import socket

def dns_query(domain):
    # Creăm socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Linia A
    sock.settimeout(5)
    sock.connect(("8.8.8.8", 53))
    
    # Construim query (simplificat)
    query = build_dns_query(domain, qtype=1)
    
    # Trimitem și primim
    sock.send(query)  # Linia B
    response = sock.recv(512)
    
    return parse_response(response)
```

#### Simptom
Funcția fie dă timeout, fie returnează date invalide/incomplete.

#### Task
Identifică **2 probleme** în cod și explică de ce cauzează simptomul observat:

**Problema 1**: Linia ___, greșeala este _______________________________________________

**Problema 2**: Linia ___, greșeala este _______________________________________________

---

### D1 – Soluție

**Problema 1**: Linia A  
`SOCK_STREAM` creează socket TCP, dar DNS standard folosește UDP (`SOCK_DGRAM`).
- DNS pe UDP: query simplu, răspuns simplu, fără overhead de conexiune
- DNS pe TCP: folosit doar pentru răspunsuri >512 bytes sau zone transfers
- Cu TCP, serverul DNS s-ar putea să nu răspundă deloc sau să aștepte un format diferit

**Problema 2**: Linia B (și lipsa prefixului de lungime)  
Pentru DNS peste TCP (dacă chiar vrei TCP), pachetul trebuie prefixat cu 2 bytes care indică lungimea (RFC 1035, secțiunea 4.2.2). Fără acest prefix, serverul nu știe unde se termină mesajul.

**Corecție pentru UDP (recomandat)**:
```python
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(5)
sock.sendto(query, ("8.8.8.8", 53))
response, _ = sock.recvfrom(512)
```

---

### D2: De Ce Nu Merge? — Load Balancer IP Hash 🐛

**Nivel**: Începător  
**Timp**: 5 minute

#### Configurație Nginx

```nginx
upstream backends {
    ip_hash;
    server 10.0.0.2:8080;
    server 10.0.0.3:8080;
}

server {
    listen 80;
    location / {
        proxy_pass http://backends;
    }
}
```

#### Simptom
Testezi cu `curl http://localhost/` de 10 ori și **toate** cererile ajung la același backend (10.0.0.2), deși ambele backend-uri sunt up și funcționale.

#### Task
1. Este aceasta o problemă sau comportament așteptat? _______________
2. Explică de ce se întâmplă:
   
   _______________________________________________________________
   
3. Cum ai testa că load balancing-ul funcționează corect?
   
   _______________________________________________________________

---

### D2 – Soluție

1. **Nu e o problemă** — e comportamentul așteptat și corect!

2. **Explicație**: `ip_hash` garantează că același IP client → același backend, mereu. 
   Toate cererile `curl` vin de la `127.0.0.1` (localhost), deci hash-ul e identic → același backend.

3. **Cum testezi corect**:
   - Trimite cereri de la IP-uri diferite (alte mașini, sau `curl --interface`)
   - SAU schimbă temporar algoritmul în `round_robin` pentru a verifica că ambele backend-uri funcționează
   - SAU folosește header `X-Forwarded-For` cu IP-uri diferite (dacă Nginx e configurat să-l respecte)

---

### D3: De Ce Nu Merge? — FTP Data Connection 🐛

**Nivel**: Intermediar  
**Timp**: 8 minute

#### Scenariu
Client FTP în Python, modul activ:

```python
import socket

def ftp_list_active(host, port=21):
    # Conexiune control
    ctrl = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ctrl.connect((host, port))
    print(ctrl.recv(1024))  # 220 Welcome
    
    ctrl.send(b"USER anonymous\r\n")
    print(ctrl.recv(1024))  # 331
    
    ctrl.send(b"PASS guest@\r\n")
    print(ctrl.recv(1024))  # 230
    
    # Pregătim pentru data connection - MODUL ACTIV
    data_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    data_sock.bind(('0.0.0.0', 0))
    data_sock.listen(1)
    
    _, data_port = data_sock.getsockname()
    p1, p2 = data_port // 256, data_port % 256
    
    # Trimitem PORT cu IP-ul nostru LOCAL
    ctrl.send(f"PORT 192,168,1,100,{p1},{p2}\r\n".encode())  # Linia X
    print(ctrl.recv(1024))  # 200 PORT command successful
    
    ctrl.send(b"LIST\r\n")
    # ... timeout aici, serverul nu se conectează
```

#### Simptom
După `LIST`, clientul așteaptă la infinit — serverul nu se conectează niciodată la portul de date.

#### Task
1. De ce serverul nu se poate conecta?
   
   _______________________________________________________________

2. Ce soluție ai propune (fără a schimba la modul pasiv)?
   
   _______________________________________________________________

3. De ce modul pasiv ar rezolva automat problema?
   
   _______________________________________________________________

---

### D3 – Soluție

1. **De ce nu se conectează**: IP-ul `192.168.1.100` e o adresă privată (RFC 1918). Serverul FTP public nu poate ruta pachete către această adresă — e în spatele NAT-ului clientului. Serverul încearcă să se conecteze, dar pachetele nu ajung niciodată.

2. **Soluție fără pasiv**: 
   - Configurează port forwarding pe router: portul extern X → 192.168.1.100:data_port
   - Trimite IP-ul PUBLIC în comanda PORT, nu cel privat
   - Alternativ: folosește FTP ALG (Application Layer Gateway) pe router, dacă e disponibil

3. **De ce pasiv rezolvă**: În modul pasiv, CLIENTUL inițiază conexiunea de date către server. Clientul poate iniția conexiuni outbound prin NAT fără probleme — NAT-ul creează automat mapping-ul pentru traficul de răspuns.

---

## Sumar Exerciții

| Cod | Tip | Nivel | Timp | Concept Principal |
|-----|-----|-------|------|-------------------|
| T1 | Trace | Intermediar | 15 min | Structura pachetelor DNS |
| T2 | Trace | Începător | 10 min | TCP handshake, FTP protocol |
| P1 | Parsons | Intermediar | 8 min | SSH port forwarding |
| P2 | Parsons | Începător | 5 min | Nginx upstream config |
| P3 | Parsons | Avansat | 10 min | DNS query construction |
| D1 | Debug | Intermediar | 10 min | UDP vs TCP pentru DNS |
| D2 | Debug | Începător | 5 min | IP hash behavior |
| D3 | Debug | Intermediar | 8 min | FTP active mode + NAT |

---

*Exerciții Non-Cod – Săptămâna 11*  
*Rețele de Calculatoare, ASE-CSIE*
