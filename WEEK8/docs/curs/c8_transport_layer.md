# Curs 8 – Nivelul Transport
## TCP, UDP, TLS, QUIC

---

## Obiective

La finalul cursului, studentul va putea:

- Explica rolul nivelului transport în arhitectura de rețea
- Descrie mecanismul porturilor și multiplexarea proceselor
- Detalia funcționarea protocolului TCP (handshake, control flux, fiabilitate)
- Compara TCP și UDP din perspectiva cerințelor aplicației
- Înțelege rolul TLS/DTLS în securizarea transportului
- Aprecia motivația apariției QUIC și impactul asupra HTTP/3

---

## 1. Rolul Nivelului Transport

### Poziție în stiva TCP/IP

```
┌─────────────────────────────┐
│       Aplicație             │ ← HTTP, FTP, DNS, SMTP...
├─────────────────────────────┤
│       Transport             │ ← TCP, UDP (acest curs)
├─────────────────────────────┤
│       Rețea (Internet)      │ ← IP, ICMP, routing
├─────────────────────────────┤
│       Legătură de date      │ ← Ethernet, Wi-Fi
├─────────────────────────────┤
│       Fizic                 │ ← Cablu, unde radio
└─────────────────────────────┘
```

### Funcții principale

1. **Identificarea proceselor** – mecanismul porturilor
2. **Multiplexarea comunicațiilor** – mai multe aplicații pe același host
3. **Controlul fluxului** – adaptarea la capacitatea receptorului
4. **Fiabilitate** (opțional) – garantarea livrării și ordinii

---

## 2. Mecanismul Porturilor

### Ce este un port?

- Identificator numeric (16 biți): 0–65535
- Identifică un capăt al comunicației (proces/serviciu)
- **Tuplu de 5 elemente** definește unic o conexiune:
  - IP sursă, Port sursă, IP destinație, Port destinație, Protocol

### Clasificare porturi

| Interval | Tip | Exemple |
|----------|-----|---------|
| 0–1023 | Well-known | HTTP (80), HTTPS (443), SSH (22), FTP (21) |
| 1024–49151 | Registered | MySQL (3306), PostgreSQL (5432) |
| 49152–65535 | Ephemeral | Porturi client (alocate dinamic) |

### Client vs Server

- **Server**: ascultă pe port **fix** (ex: 80 pentru HTTP)
- **Client**: folosește port **efemer** (alocat de OS)

---

## 3. Protocolul TCP

### Caracteristici fundamentale

- **Orientat pe conexiune** – necesită handshake înainte de transfer
- **Fiabil** – garantează livrarea și ordinea
- **Stream de bytes** – nu există noțiunea de "mesaj"
- **Full-duplex** – comunicare bidirecțională simultană

### Header-ul TCP (20+ bytes)

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
├─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┤
│          Source Port          │       Destination Port        │
├───────────────────────────────┴───────────────────────────────┤
│                        Sequence Number                        │
├───────────────────────────────────────────────────────────────┤
│                    Acknowledgment Number                      │
├───────┬───────┬─┬─┬─┬─┬─┬─┬───────────────────────────────────┤
│  Off  │ Res   │U│A│P│R│S│F│            Window                 │
│       │       │R│C│S│S│Y│I│                                   │
│       │       │G│K│H│T│N│N│                                   │
├───────┴───────┴─┴─┴─┴─┴─┴─┴───────────────────────────────────┤
│           Checksum            │         Urgent Pointer        │
├───────────────────────────────┴───────────────────────────────┤
│                    Options (if any)                           │
└───────────────────────────────────────────────────────────────┘
```

### Flag-uri TCP

| Flag | Nume | Rol |
|------|------|-----|
| SYN | Synchronize | Inițiere conexiune |
| ACK | Acknowledge | Confirmarea primirii |
| FIN | Finish | Închidere controlată |
| RST | Reset | Închidere forțată/eroare |
| PSH | Push | Livrare imediată la aplicație |
| URG | Urgent | Date prioritare |

---

## 4. Three-Way Handshake

### Întrebare de gândire

Înainte de a vedea diagrama: **de ce crezi că sunt necesari EXACT 3 pași pentru a stabili o conexiune TCP?** De ce nu 2 sau 4?

*Gândește 30 secunde, apoi continuă.*

---

### Analogie: Handshake ca o prezentare formală

**🤝 CONCRET (Conversație umană):**

TCP handshake e ca atunci când te prezinți formal cuiva:

```
Tu:        "Bună, eu sunt Ana." (SYN - îți spun cine sunt și că vreau să vorbim)
Cealaltă:  "Bună Ana, eu sunt Maria. Încântată!" (SYN-ACK - confirm că te-am auzit + mă prezint și eu)  
Tu:        "Încântată de cunoștință, Maria!" (ACK - confirm că am înțeles-o și pe ea)
```

**De ce 3 pași și nu 2?**
- Cu 2 pași, Maria nu ar fi sigură că Ana a auzit-o prezentându-se
- Cu 3 pași, **AMBELE părți știu că cealaltă e atentă și a primit mesajul**

**📊 PICTORIAL:** Vezi diagrama de mai jos

**💻 ABSTRACT:** Numerele de secvență (ISN) sunt sincronizate în ambele direcții

---

### Stabilirea conexiunii TCP

```
Client                                Server
   │                                     │
   │ ─────── SYN, Seq=x ──────────────→  │
   │         (1. Cerere conectare)       │
   │                                     │
   │ ←────── SYN-ACK, Seq=y, Ack=x+1 ──  │
   │         (2. Acceptare + ISN)        │
   │                                     │
   │ ─────── ACK, Seq=x+1, Ack=y+1 ───→  │
   │         (3. Confirmare finală)      │
   │                                     │
   │ ═══════ ESTABLISHED ════════════════│
```

### De ce trei pași?

1. **Sincronizare ISN** (Initial Sequence Number) – ambele părți își comunică numărul de secvență inițial
2. **Prevenire pachete vechi** – evită confuzia cu conexiuni anterioare
3. **Confirmare bidirecțională** – ambele părți știu că cealaltă este activă

---

## 5. Terminarea Conexiunii TCP

### Four-Way Termination

```
Client                                Server
   │                                     │
   │ ─────── FIN, Seq=u ──────────────→  │
   │         (1. Vreau să închid)        │
   │                                     │
   │ ←────── ACK, Ack=u+1 ────────────── │
   │         (2. OK, am primit)          │
   │                                     │
   │ ←────── FIN, Seq=v ──────────────── │
   │         (3. Și eu vreau să închid)  │
   │                                     │
   │ ─────── ACK, Ack=v+1 ─────────────→ │
   │         (4. Confirmare finală)      │
   │                                     │
   │          TIME_WAIT (2×MSL)          │
   │                                     │
```

### Stările socketului TCP

- LISTEN → SYN_RECEIVED → ESTABLISHED
- ESTABLISHED → FIN_WAIT_1 → FIN_WAIT_2 → TIME_WAIT → CLOSED
- ESTABLISHED → CLOSE_WAIT → LAST_ACK → CLOSED

---

## 6. Opțiuni TCP

### MSS (Maximum Segment Size)

- Dimensiunea maximă a datelor într-un segment
- MSS + header TCP + header IP ≤ MTU
- Negociată în SYN (evită fragmentarea IP)

### SACK (Selective Acknowledgment)

- TCP clasic: ACK cumulativ (doar "am primit până la X")
- SACK: permite confirmarea intervalelor discontinue
- **Reduce retransmisiile inutile**

### Window Scaling

- Câmpul Window din header: 16 biți (max 65535)
- Window scaling: factor de multiplicare (negociat în SYN)
- Permite ferestre de milioane de bytes (necesar pentru rețele rapide)

### TCP Timestamps

- Estimare precisă RTT (Round-Trip Time)
- PAWS (Protection Against Wrapped Sequences)

---

## 7. Protocolul UDP

### Caracteristici

- **Fără conexiune** – nu există handshake
- **Best-effort** – fără garanții de livrare
- **Datagrame** – fiecare mesaj este independent
- **Overhead minim** – header de doar 8 bytes

### Header-ul UDP

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
├─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┤
│          Source Port          │       Destination Port        │
├───────────────────────────────┼───────────────────────────────┤
│            Length             │           Checksum            │
├───────────────────────────────┴───────────────────────────────┤
│                            Data ...                           │
└───────────────────────────────────────────────────────────────┘
```

### Când se folosește UDP?

- **DNS** – query-uri scurte, răspunsuri rapide
- **DHCP** – bootstrap, nu există conexiune
- **Streaming** – toleranță la pierderi, latență minimă
- **Gaming** – stare curentă mai importantă decât istoric
- **VoIP** – real-time, pierderea unui pachet < întârzierea

---

## 8. TCP vs UDP – Comparație

### Predicție

Pentru fiecare aplicație, ghicește ce protocol e mai potrivit (TCP sau UDP):

| Aplicație | Predicția ta | Răspuns corect |
|-----------|--------------|----------------|
| Streaming video live | ___ | |
| Transfer fișier important | ___ | |
| Query DNS simplu | ___ | |
| Joc multiplayer FPS | ___ | |
| Email (SMTP) | ___ | |
| Videoconferință | ___ | |

*Verifică răspunsurile cu tabelul de mai jos.*

---

### Tabel comparativ

| Aspect | TCP | UDP |
|--------|-----|-----|
| Conexiune | Orientat conexiune | Fără conexiune |
| Fiabilitate | Garantată | Best-effort |
| Ordine | Păstrată | Nu e garantată |
| Control flux | Da (window) | Nu |
| Overhead | 20+ bytes header | 8 bytes header |
| Latență setup | 1 RTT (handshake) | 0 |
| Unitate transfer | Stream (bytes) | Datagrame (mesaje) |
| Utilizare | HTTP, FTP, email | DNS, VoIP, gaming |

### Răspunsuri predicție

| Aplicație | Protocol | Justificare |
|-----------|----------|-------------|
| Streaming video live | **UDP** | Latență > completitudine; un frame pierdut nu contează |
| Transfer fișier | **TCP** | Fiecare byte contează, ordinea importantă |
| Query DNS | **UDP** | Query mic, răspuns rapid, retry la nivel aplicație |
| Joc FPS | **UDP** | Poziția curentă > istoric; latență critică |
| Email | **TCP** | Mesajul complet, în ordine, fără pierderi |
| Videoconferință | **UDP** | Real-time; preferăm glitch decât delay |

---

## 9. TLS (Transport Layer Security)

### De ce TLS?

- TCP și UDP transmit date **în clar**
- Oricine pe ruta poate intercepta și citi traficul
- TLS oferă: **confidențialitate**, **integritate**, **autentificare**

### Poziție în stack

```
┌─────────────────────────────┐
│       Aplicație             │
├─────────────────────────────┤
│       TLS/SSL               │ ← Criptare (acest nivel)
├─────────────────────────────┤
│       TCP                   │
└─────────────────────────────┘
```

### TLS 1.3 – Îmbunătățiri

- **1-RTT handshake** (vs 2-RTT în TLS 1.2)
- **0-RTT** pentru conexiuni repetate
- Algoritmi deprecați eliminați
- Forward secrecy obligatoriu

### Handshake TLS 1.3 Simplificat

```
Client                                Server
   │                                     │
   │ ─── ClientHello + KeyShare ──────→  │
   │                                     │
   │ ←── ServerHello + KeyShare ──────── │
   │ ←── {EncryptedExtensions} ───────── │
   │ ←── {Certificate} ───────────────── │
   │ ←── {CertificateVerify} ──────────  │
   │ ←── {Finished} ──────────────────── │
   │                                     │
   │ ─── {Finished} ──────────────────→  │
   │                                     │
   │ ═══ Application Data (encrypted) ═══│
```

---

## 10. QUIC și HTTP/3

### De ce QUIC?

- **Head-of-line blocking** în TCP: un pachet pierdut blochează tot
- **Handshake combinat**: conexiune + criptare în 1-RTT
- **0-RTT** pentru conexiuni repetate
- **Migrare conexiune**: schimbare IP/port fără reconectare

### Arhitectură QUIC

```
┌─────────────────────────────┐
│       HTTP/3                │
├─────────────────────────────┤
│       QUIC                  │ ← Combină TCP + TLS
├─────────────────────────────┤
│       UDP                   │
└─────────────────────────────┘
```

### QUIC vs TCP+TLS

| Aspect | TCP + TLS | QUIC |
|--------|-----------|------|
| Handshake | 2-3 RTT | 1 RTT (0-RTT repeat) |
| Multiplexare | HOL blocking | Stream independent |
| Criptare | Header în clar | Header criptat |
| Migrare | Reconectare | Connection ID |

---

## 11. Recapitulare

### Concepte cheie

1. **Nivelul transport** – face legătura între rețea și aplicație
2. **Porturi** – identifică procesele, permit multiplexarea
3. **TCP** – fiabil, orientat conexiune, complex
4. **UDP** – rapid, simplu, fără garanții
5. **TLS** – securizează transportul (criptare, autentificare)
6. **QUIC** – evoluție modernă, combină avantajele TCP+TLS peste UDP

### Întrebări de verificare

1. De ce are nevoie TCP de three-way handshake?
2. Ce problemă rezolvă SACK?
3. Când ar folosi o aplicație UDP în loc de TCP?
4. Ce oferă TLS ce nu oferă TCP?
5. De ce rulează QUIC peste UDP și nu direct peste IP?

---

## Bibliografie

- Kurose, J., Ross, K. (2021). *Computer Networking: A Top-Down Approach*. Cap. 3
- RFC 793 – TCP
- RFC 768 – UDP
- RFC 8446 – TLS 1.3
- RFC 9000 – QUIC

---

*Material pentru Rețele de Calculatoare, ASE București, 2025*
