# Curs 11: Protocoale de Aplicație – FTP, DNS, SSH

## Prezentare Generală

**Săptămâna**: 11 din 14  
**Durata**: 2 ore curs  
**Tema fișei disciplinei**: Nivelul aplicație – FTP, DNS, SSH

---

## 1. Ce Vom Învăța

Trei protocoale fundamentale ale nivelului aplicație susțin infrastructura modernă a Internetului:

- **FTP (File Transfer Protocol)** – transferul de fișiere între sisteme
- **DNS (Domain Name System)** – traducerea numelor în adrese IP
- **SSH (Secure Shell)** – acces securizat la sisteme remote

Fiecare protocol ilustrează un model diferit de comunicare: FTP folosește conexiuni multiple (control + date), DNS funcționează predominant pe UDP cu mesaje structurate, iar SSH stabilește canale criptate multiplexate.

## 2. De Ce Contează

| Protocol | Relevanță Practică |
|----------|-------------------|
| **FTP** | Deployment aplicații, backup, transfer date între servere |
| **DNS** | Baza navigării web, service discovery, configurare CDN |
| **SSH** | Administrare servere, tunneling securizat, Git over SSH |

Ca programator sau inginer DevOps, vei folosi aceste protocoale zilnic: debugging probleme de rețea, configurare infrastructură, dezvoltare aplicații distribuite.

---

## 3. Prerechizite

Din săptămânile anterioare:
- Model OSI/TCP-IP (S2)
- Programare pe socket-uri TCP/UDP (S3-S4)
- Adresare IP, subnetting (S5-S6)
- Nivelul transport: TCP, UDP, TLS (S8)
- HTTP și servicii web (S10)

**Recapitulare rapidă**: TCP garantează livrarea în ordine și controlul fluxului, făcându-l potrivit pentru FTP și SSH. UDP oferă latență redusă pentru interogări simple precum DNS.

---

## 4. FTP – File Transfer Protocol

### 4.1 Introducere

FTP este unul dintre cele mai vechi protocoale de Internet (RFC 959, 1985), conceput pentru transferul eficient de fișiere între sisteme heterogene.

> 💡 **Din experiența mea**: Studenții confundă des FTP cu SFTP — sunt protocoale complet diferite! FTP e din '85, SFTP e bazat pe SSH și apărut mult mai târziu. Când cineva zice "SFTP" de obicei se referă la SSH File Transfer Protocol, nu la "Secure FTP".

**Caracteristici principale**:
- Funcționează peste TCP
- Folosește două conexiuni separate: **control** (port 21) și **date** (port 20 sau dinamic)
- Suportă autentificare (user/password) și acces anonim
- Operează în mod text (comenzi ASCII) și binar (pentru fișiere)

### Analogie: FTP ca Telefon + Fax

Imaginează-ți că suni un coleg (conexiunea de **control**) și îi spui ce documente vrei. El le trimite prin fax (conexiunea de **date**). Telefonul rămâne deschis pentru instrucțiuni noi, dar faxul se închide după fiecare document.

- **Modul activ**: Tu îi dai numărul tău de fax și el te sună înapoi (problematic dacă ai secretară care blochează apelurile externe = NAT/firewall)
- **Modul pasiv**: El îți dă numărul lui de fax și tu inițiezi transferul (funcționează mereu)

### 4.2 Arhitectura FTP

```
┌─────────────────┐                 ┌─────────────────┐
│     Client      │                 │     Server      │
│                 │                 │                 │
│  ┌───────────┐  │   Control :21   │  ┌───────────┐  │
│  │ Protocol  │◄─┼────────────────►│  │ Protocol  │  │
│  │Interpreter│  │   (comenzi)     │  │Interpreter│  │
│  └───────────┘  │                 │  └───────────┘  │
│                 │                 │                 │
│  ┌───────────┐  │   Date :20/X    │  ┌───────────┐  │
│  │  Data     │◄─┼────────────────►│  │  Data     │  │
│  │ Transfer  │  │   (fișiere)     │  │ Transfer  │  │
│  └───────────┘  │                 │  └───────────┘  │
│                 │                 │                 │
│  ┌───────────┐  │                 │  ┌───────────┐  │
│  │   File    │  │                 │  │   File    │  │
│  │  System   │  │                 │  │  System   │  │
│  └───────────┘  │                 │  └───────────┘  │
└─────────────────┘                 └─────────────────┘
```

### 4.3 Conexiunea de Control

- **Port**: 21 (server ascultă)
- **Funcție**: transmiterea comenzilor și a răspunsurilor
- **Format**: text ASCII, fiecare comandă terminată cu CRLF
- **Persistență**: rămâne deschisă pe durata sesiunii

**Comenzi principale**:

| Comandă | Funcție |
|---------|---------|
| `USER` | Specifică numele utilizatorului |
| `PASS` | Specifică parola |
| `PWD` | Afișează directorul curent |
| `CWD` | Schimbă directorul |
| `LIST` | Listează conținutul directorului |
| `RETR` | Descarcă un fișier |
| `STOR` | Încarcă un fișier |
| `TYPE` | Setează tipul de transfer (A=ASCII, I=Binary) |
| `PORT` | Specifică adresa pentru mod activ |
| `PASV` | Solicită mod pasiv |
| `QUIT` | Încheie sesiunea |

**Coduri de răspuns** (primele 3 cifre):

| Cod | Semnificație |
|-----|--------------|
| 1xx | Răspuns preliminar pozitiv |
| 2xx | Succes |
| 3xx | Răspuns intermediar (continuare așteptată) |
| 4xx | Eroare temporară |
| 5xx | Eroare permanentă |

### 4.4 Modurile de Transfer: Activ vs. Pasiv

**Mod Activ (PORT)**:
1. Clientul deschide un port local și trimite `PORT ip,ip,ip,ip,port_hi,port_lo`
2. Serverul inițiază conexiunea de date din portul 20 către portul clientului
3. **Problemă**: Firewall-ul clientului poate bloca conexiunile incoming

```
Client                              Server
  │                                   │
  │ ──── PORT 192,168,1,100,200,45 ──►│ (clientul ascultă pe 51245)
  │                                   │
  │ ◄──── Conectare de la :20 ────────│ (serverul inițiază conexiunea)
  │                                   │
```

**Mod Pasiv (PASV)**:
1. Clientul trimite `PASV`
2. Serverul răspunde cu `227 Entering Passive Mode (ip,ip,ip,ip,port_hi,port_lo)`
3. Clientul inițiază conexiunea de date către portul specificat
4. **Avantaj**: Clientul inițiază AMBELE conexiuni – funcționează cu NAT/firewall

```
Client                              Server
  │                                   │
  │ ────────────── PASV ─────────────►│
  │                                   │
  │ ◄─── 227 (209,51,188,116,234,56) ─│ (serverul ascultă pe 60024)
  │                                   │
  │ ──── Conectare la :60024 ────────►│ (clientul inițiază conexiunea)
  │                                   │
```

### 4.5 Considerații de Securitate

FTP transmite credențiale în clar. Alternative securizate:
- **FTPS** (FTP over TLS) – adaugă criptare la conexiunile de control și date
- **SFTP** (SSH File Transfer Protocol) – protocol complet diferit, bazat pe SSH
- **SCP** (Secure Copy) – transfer simplu prin SSH

---

## 5. DNS – Domain Name System

### 5.1 Introducere

DNS traduce numele de domenii (ex: `www.example.com`) în adrese IP (ex: `93.184.216.34`). Fără DNS, utilizatorii ar trebui să memoreze adrese numerice.

### Analogie: DNS ca Serviciul de Informații Telefonice

Vrei să suni pe cineva dar știi doar numele, nu numărul. Suni la Informații (resolver). Operatorul nu știe direct, dar știe pe cine să întrebe:
1. Întreabă la "Informații Internaționale" (.com, .ro) → primește referință
2. Întreabă la "Informații Locale" (ase.ro) → primește numărul final

TTL = cât timp ții minte numărul înainte să suni iar la Informații.

**Caracteristici**:
- Bază de date distribuită și ierarhică
- Folosește predominant UDP pe portul 53 (TCP pentru transferuri de zonă sau răspunsuri mari)
- Caching pe multiple niveluri pentru performanță
- Sistem de delegare: fiecare nivel cunoaște nivelul imediat inferior

### 5.2 Ierarhia DNS

```
                        . (root)
                           │
         ┌─────────────────┼─────────────────┐
         ▼                 ▼                 ▼
       .com              .org              .ro
         │                 │                 │
    ┌────┴────┐           ▼            ┌────┴────┐
    ▼         ▼       wikipedia       ▼         ▼
  google   example                  ase      digi
    │         │                       │
    ▼         ▼                       ▼
   www      mail                    www
```

**Componente**:
1. **Root servers** (13 seturi, replicați global) – cunosc serverele TLD
2. **TLD servers** (.com, .org, .ro) – cunosc serverele autoritative
3. **Authoritative servers** – conțin înregistrările finale
4. **Recursive resolvers** (ex: 8.8.8.8) – interogări în cascadă pentru clienți

### 5.3 Tipuri de Înregistrări

| Tip | Funcție | Exemplu |
|-----|---------|---------|
| **A** | Adresă IPv4 | `example.com → 93.184.216.34` |
| **AAAA** | Adresă IPv6 | `example.com → 2606:2800:220:1::` |
| **MX** | Mail exchanger | `example.com → 10 mail.example.com` |
| **CNAME** | Alias (canonical name) | `www.example.com → example.com` |
| **NS** | Nameserver autoritativ | `example.com → ns1.example.com` |
| **TXT** | Text arbitrar | SPF, DKIM, verificări |
| **SOA** | Start of Authority | Informații despre zonă |
| **PTR** | Reverse lookup | IP → nume |

### 5.4 Structura Pachetului DNS (RFC 1035)

```
Header (12 bytes):
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|                      ID                       |
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|QR|   Opcode  |AA|TC|RD|RA|   Z    |   RCODE   |
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|                    QDCOUNT                    |
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|                    ANCOUNT                    |
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|                    NSCOUNT                    |
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|                    ARCOUNT                    |
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+

Question Section:
  QNAME:  variabil (labels: length+chars, terminat cu 0)
          ex: 03www06google03com00
  QTYPE:  16 biți (A=1, AAAA=28, MX=15, etc.)
  QCLASS: 16 biți (IN=1)
```

**Flags**:
- **QR** (1 bit): 0=query, 1=response
- **RD** (1 bit): Recursion Desired
- **RA** (1 bit): Recursion Available
- **RCODE** (4 biți): 0=no error, 3=NXDOMAIN

### 5.5 TTL și Caching

**TTL (Time To Live)** specifică durata de viață a unei înregistrări în cache:
- TTL scurt (300s) – actualizări frecvente, trafic mai mare la autoritativ
- TTL lung (86400s) – performanță mai bună, propagare lentă a schimbărilor

**Niveluri de cache**:
1. Browser cache
2. OS cache (resolver local)
3. Router/gateway cache
4. ISP recursive resolver cache

### 5.6 DNSSEC

DNSSEC adaugă autenticitate și integritate răspunsurilor DNS prin semnături criptografice, protejând împotriva atacurilor de tip DNS spoofing.

---

## 6. SSH – Secure Shell

### 6.1 Introducere

SSH (RFC 4251-4254) oferă acces securizat la sisteme remote, înlocuind protocoalele necriptate precum Telnet și rsh.

### Analogie: SSH ca Tunel Securizat prin Munte

Imaginează-ți că vrei să trimiți mesaje între două sate separate de un munte plin de bandiți. SSH:
1. **Schimb de chei**: Cei doi primari se întâlnesc în secret și stabilesc un cod (Diffie-Hellman)
2. **Verificare identitate**: Fiecare primar își arată sigiliul (host key)
3. **Tunelul**: Construiesc un tunel prin care trec toate mesajele, criptate cu codul stabilit
4. **Canale**: Prin același tunel pot trece și mesaje, și pachete, și bani (multiplexare)

Port forwarding = construiești o extensie a tunelului până la un sat vecin.

**Funcționalități**:
- Autentificare (password, chei publice, certificate)
- Criptare (AES, ChaCha20)
- Integritate (HMAC)
- Tuneluri (port forwarding)
- Transfer fișiere (SCP, SFTP)

### 6.2 Arhitectura SSH

```
┌────────────────────────────────────────────────────┐
│                 SSH Connection                      │
│  ┌────────────────────────────────────────────────┐│
│  │            SSH User Auth Layer                 ││
│  │  ┌────────────────────────────────────────────┐││
│  │  │         SSH Transport Layer                │││
│  │  │  ┌────────────────────────────────────────┐│││
│  │  │  │              TCP                        ││││
│  │  │  └────────────────────────────────────────┘│││
│  │  └────────────────────────────────────────────┘││
│  └────────────────────────────────────────────────┘│
└────────────────────────────────────────────────────┘
```

**Straturi**:
1. **Transport Layer** – criptare, integritate, schimb de chei
2. **User Authentication Layer** – verificarea identității
3. **Connection Layer** – canale multiplexate (shell, forwarding)

### 6.3 Schimbul de Chei (Key Exchange)

La conectare, clientul și serverul negociază:
1. Versiunea protocolului
2. Algoritmii de criptare
3. Cheile de sesiune (prin Diffie-Hellman)
4. Verificarea identității serverului (host key)

```
Client                                 Server
   │                                      │
   │ ──── SSH-2.0-OpenSSH_8.9 ──────────►│
   │ ◄──── SSH-2.0-OpenSSH_8.9 ─────────│
   │                                      │
   │ ──── Key Exchange Init ────────────►│
   │ ◄──── Key Exchange Init ───────────│
   │                                      │
   │ ◄──── DH Key Exchange ─────────────►│
   │                                      │
   │ ◄──── Server Host Key + Sig ───────│
   │       (verificare: ~/.ssh/known_hosts)
   │                                      │
   │ ═════════ Canal criptat ═══════════│
```

### 6.4 Autentificare

**Metode** (în ordinea preferinței):
1. **Publickey** – cheia privată semnează un challenge
2. **Password** – transmisă criptat prin canal securizat
3. **Keyboard-interactive** – 2FA, TOTP
4. **GSSAPI** – Kerberos

**Generare chei**:
```bash
ssh-keygen -t ed25519 -C "user@example.com"
# Rezultat: ~/.ssh/id_ed25519 (privată) + ~/.ssh/id_ed25519.pub (publică)
```

### 6.5 Canale și Port Forwarding

SSH multiplexează mai multe canale logice pe o singură conexiune TCP.

**Local Port Forwarding** (`-L`):
```
ssh -L 8080:remote-db:3306 user@bastion
# Conectare la localhost:8080 → tunel → remote-db:3306
```

**Remote Port Forwarding** (`-R`):
```
ssh -R 9000:localhost:80 user@public-server
# public-server:9000 → tunel → localhost:80
```

**Dynamic Port Forwarding** (`-D`):
```
ssh -D 1080 user@proxy
# SOCKS5 proxy pe localhost:1080
```

---

## 7. Întrebări de Verificare

1. De ce FTP folosește două conexiuni separate pentru control și date?
2. Care este avantajul modului pasiv FTP față de cel activ în prezența NAT?
3. Ce rol au serverele root în ierarhia DNS?
4. De ce TTL-ul afectează viteza de propagare a schimbărilor DNS?
5. Cum protejează SSH împotriva atacurilor man-in-the-middle?
6. Ce este un "known_hosts" și de ce este important?

---

## 8. Ce Am Învățat

- FTP: protocol de transfer fișiere cu arhitectură dual-conexiune
- DNS: sistem ierarhic distribuit pentru rezoluția numelor
- SSH: canal securizat pentru acces remote și tunneling
- Importanța criptării și autentificării în protocoalele moderne

---

## 9. Bibliografie

| Referință | DOI/Link |
|-----------|----------|
| J. Kurose, K. Ross - Computer Networking: A Top-Down Approach, 8th Ed., Pearson, 2021 | ISBN: 978-0135928615 |
| B. Rhodes, J. Goetzen - Foundations of Python Network Programming, 3rd Ed., Apress, 2014 | DOI: 10.1007/978-1-4302-5855-1 |

**Standarde și Specificații** (fără DOI):
- RFC 959 – File Transfer Protocol (FTP)
- RFC 1035 – Domain Names - Implementation and Specification
- RFC 4251-4254 – The Secure Shell (SSH) Protocol Architecture
- RFC 4253 – SSH Transport Layer Protocol

---

*Document generat pentru Cursul 11 – Rețele de Calculatoare*  
*Revolvix&Hypotheticalandrei*
