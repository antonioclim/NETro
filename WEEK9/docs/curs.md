# Curs 9 — Nivelul Sesiune (L5) și Nivelul Prezentare (L6)

## Ce vom învăța

Săptămâna 9 tratează cele două niveluri intermediare ale modelului OSI care asigură **continuitatea logică a comunicării** (sesiune) și **reprezentarea uniformă a datelor** (prezentare). Deși în stiva TCP/IP aceste funcții sunt adesea absorbite de nivelul aplicație, înțelegerea lor separată oferă o perspectivă fundamentală asupra modului în care aplicațiile distribuite mențin starea conversațională și negociază formatele de date.

**Obiective concrete:**
1. Diferențierea între conexiune (L4) și sesiune (L5)
2. Implementarea mecanismelor de autentificare, checkpoint și reluare
3. Înțelegerea transformărilor de date: serializare, compresie, criptare
4. Construirea unui protocol text multi-comandă (pseudo-FTP)
5. Analiza traficului FTP cu Wireshark/tshark

---

## De ce contează

Într-un mediu distribuit, pierderile de conexiune sunt inevitabile. Nivelul sesiune oferă **puncte de salvare** (checkpoints) și mecanisme de **reluare din punctul de întrerupere** — utile pentru transferuri de fișiere mari sau tranzacții complexe. Nivelul prezentare asigură că datele trimise de un sistem big-endian sunt corect interpretate de unul little-endian, că textul UTF-8 ajunge intact, și că informațiile sensibile pot fi criptate transparent.

Pentru un programator, aceste concepte se manifestă în:
- **Session tokens** (JWT, cookies de sesiune)
- **Serializare** (JSON, Protocol Buffers, MessagePack)
- **Compresie** (gzip, zlib, brotli)
- **TLS/SSL** (criptare end-to-end)

---

## Prerechizite

| Săptămână | Concept necesar |
|-----------|-----------------|
| S4 | Adresare IP, subnetare |
| S8 | TCP handshake, segmentare, retransmisie |
| S3 | Socket programming de bază |

**Recapitulare ultra-scurtă:** TCP oferă un flux de octeți fiabil între două endpoint-uri. Dar TCP nu știe nimic despre „sesiuni" de utilizator, autentificare sau formatul datelor — acestea sunt responsabilitatea nivelurilor superioare.

---

## 1. Nivelul Sesiune (L5 OSI)

### 1.1 Rol și responsabilități

Nivelul sesiune gestionează **dialogul** între aplicații:

| Funcție | Descriere |
|---------|-----------|
| **Stabilire sesiune** | Inițializare parametri, autentificare |
| **Sincronizare** | Checkpoint-uri pentru reluare |
| **Control dialog** | Half-duplex vs full-duplex |
| **Terminare** | Închidere gracioasă cu confirmare |

### 1.2 Conexiune vs Sesiune

```
CONEXIUNE TCP (L4)          SESIUNE (L5)
─────────────────           ─────────────
IP:port ↔ IP:port           User_A ↔ User_B
Flux de octeți              Context semantic
Stateless semantic          Stateful (auth, history)
Timeout: sistem             Timeout: aplicație
```

**Exemplu practic:** Un utilizator se conectează la un server FTP. Conexiunea TCP se stabilește (L4). Apoi utilizatorul se autentifică (USER/PASS) — aceasta creează o **sesiune**. Dacă conexiunea se pierde, o reconectare necesită re-autentificare pentru a restaura sesiunea.

> **Din experiența mea:** Studenții confundă frecvent "conexiune" cu "sesiune". Cel mai bun mod de a clarifica: conexiunea e socket-ul (IP:port ↔ IP:port), sesiunea e *cine* vorbește și *ce* a făcut până acum. Poți avea 10 conexiuni TCP și o singură sesiune logică, sau invers — o singură conexiune TCP cu multiple sesiuni secvențiale (după logout + login).

### Analogie: Sesiunea ca relație bancară

Gândește-te la relația ta cu banca:
- **Conexiunea** = fiecare vizită la ghișeu sau apel telefonic
- **Sesiunea** = relația ta cu banca: cont deschis, istoric tranzacții, limite de credit

Dacă închizi telefonul (conexiunea se pierde), relația cu banca (sesiunea) nu dispare. Dar dacă suni din nou, trebuie să te autentifici pentru a "restaura" sesiunea.

### 1.3 Sincronizare și Checkpoints

În protocoale de transfer fișiere, punctele de sincronizare permit:
- Reluarea transferului de la ultima poziție confirmată
- Verificarea integrității parțiale (CRC pe blocuri)
- Rollback în caz de eroare

```python
# Pseudo-cod: checkpoint în transfer
def transfer_with_checkpoints(file, block_size=8192):
    checkpoint = 0
    while True:
        block = file.read(block_size)
        if not block:
            break
        send_block(block, seq=checkpoint)
        ack = wait_ack()
        if ack.seq == checkpoint:
            checkpoint += 1
            save_checkpoint(checkpoint)
```

### 1.4 Moduri de dialog

| Mod | Descriere | Exemplu |
|-----|-----------|---------|
| Simplex | Unidirecțional | Streaming video |
| Half-duplex | Alternativ | Walkie-talkie, HTTP/1.0 |
| Full-duplex | Simultan | Telnet, SSH, WebSocket |

---

## 2. Nivelul Prezentare (L6 OSI)

### 2.1 Rol și responsabilități

Nivelul prezentare se ocupă de **sintaxa** datelor:

| Funcție | Descriere |
|---------|-----------|
| **Serializare** | Conversie structuri → octeți |
| **Traducere** | Big-endian ↔ little-endian |
| **Compresie** | Reducere dimensiune |
| **Criptare** | Confidențialitate |

### 2.2 Problema ordinii octeților (Endianness)

```
Valoarea: 0x12345678 (hex)

Big-endian (network byte order):
┌──────┬──────┬──────┬──────┐
│  12  │  34  │  56  │  78  │
└──────┴──────┴──────┴──────┘
Adresă: 0      1      2      3

Little-endian (x86):
┌──────┬──────┬──────┬──────┐
│  78  │  56  │  34  │  12  │
└──────┴──────┴──────┴──────┘
Adresă: 0      1      2      3
```

**Regula de aur:** Protocolele de rețea folosesc **network byte order** (big-endian). Funcțiile `htons()`, `htonl()`, `ntohs()`, `ntohl()` asigură conversiile necesare.

### Analogie: Endianness ca scrierea numerelor

Gândește-te cum scriem noi numerele vs. cum le scriu arabii:
- **Big-endian** = scriere europeană: "douăzeci și trei" → scrii 2 apoi 3 (cel mai semnificativ primul)
- **Little-endian** = scriere inversă: scrii 3 apoi 2 (cel mai puțin semnificativ primul)

Dacă un european trimite "23" unui arab care citește invers, arabul vede "32". Exact asta se întâmplă când trimiți un număr big-endian și îl citești little-endian.

### 2.3 Serializare: de la structură la octeți

```python
import struct

# Serializare header binar
def pack_header(magic, version, length, checksum):
    # >: big-endian, I: unsigned int (4B), H: unsigned short (2B)
    return struct.pack('>IIHH', magic, version, length, checksum)

# Deserializare
def unpack_header(data):
    magic, version, length, checksum = struct.unpack('>IIHH', data[:12])
    return {'magic': magic, 'version': version, 
            'length': length, 'checksum': checksum}
```

### 2.4 Compresie transparentă

```python
import zlib

def compress_payload(data):
    """Compresie cu zlib nivel 6 (echilibru viteză/rată)"""
    return zlib.compress(data, level=6)

def decompress_payload(compressed):
    return zlib.decompress(compressed)

# Exemplu de câștig
original = b"A" * 10000  # 10KB repetitiv
compressed = compress_payload(original)
ratio = len(original) / len(compressed)
print(f"Rată compresie: {ratio:.1f}x")  # ~1000x pentru date repetitive
```

### Analogie: CRC-ul ca sumă de control la supermarket

Când cumperi 5 produse:
- Casiera scanează: 12.50 + 8.00 + 3.50 + 15.00 + 1.00 = **40.00**
- Dacă totalul de pe bon nu e 40.00, știi că ceva e greșit

CRC-ul face similar: calculează o "sumă" matematică din toți bytes. Dacă un singur bit se schimbă în tranzit, "suma" diferă și detectezi eroarea. E mai sofisticat decât o sumă simplă (folosește polinoame), dar ideea e aceeași.

### 2.5 Criptare la nivel prezentare

În TLS/SSL, nivelul prezentare criptează datele înainte de transmisie:

```
Aplicație: "GET /index.html HTTP/1.1"
     ↓
Prezentare (TLS): [encrypted_blob]
     ↓
Transport (TCP): segmente cu blob criptat
```

---

## 3. FTP — Studiu de caz integrat

File Transfer Protocol demonstrează clar separarea L5/L6:

### 3.1 Arhitectura FTP

```
┌─────────────────────────────────────────────────┐
│                   CLIENT FTP                     │
├────────────────────┬────────────────────────────┤
│   User Interface   │      Protocol Engine       │
├────────────────────┴────────────────────────────┤
│  Control Connection (port 21)    Data Connection │
│  ─────────────────────────       (port 20/dyn)  │
│  Comenzi text: USER, PASS,       Transfer binar/ │
│  CWD, LIST, RETR, STOR, QUIT     ASCII          │
└─────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────┐
│                   SERVER FTP                     │
├────────────────────┬────────────────────────────┤
│  Command Handler   │       File System          │
└────────────────────┴────────────────────────────┘
```

### 3.2 Sesiune FTP (L5)

```
Client                          Server
   │                               │
   │───── TCP SYN ────────────────▶│
   │◀──── TCP SYN-ACK ────────────│
   │───── TCP ACK ────────────────▶│  ← Conexiune (L4)
   │                               │
   │◀──── 220 Welcome ────────────│
   │───── USER alice ─────────────▶│
   │◀──── 331 Password required ──│
   │───── PASS secret ────────────▶│
   │◀──── 230 Logged in ──────────│  ← Sesiune (L5) stabilită
   │                               │
   │───── PWD ────────────────────▶│
   │◀──── 257 "/" ────────────────│
   │                               │
   │───── QUIT ───────────────────▶│
   │◀──── 221 Goodbye ────────────│  ← Sesiune închisă
```

### 3.3 Moduri transfer (L6)

| Mod | Cod | Utilizare |
|-----|-----|-----------|
| ASCII | TYPE A | Text, cod sursă |
| Binary | TYPE I | Executabile, imagini |

```
# Comanda TYPE în FTP
TYPE A  → Conversie line endings (CR LF ↔ LF)
TYPE I  → Transfer octet-cu-octet, fără modificări
```

### 3.4 Moduri conexiune date

| Mod | Inițiator | Firewall-friendly |
|-----|-----------|-------------------|
| Active | Server → Client:20 | ✗ |
| Passive | Client → Server:dyn | ✓ |

### Analogie: Mod Activ/Pasiv — Cine sună pe cine?

**Mod Activ:** Serverul sună clientul
- Tu (client) îi dai numărul tău de telefon serverului
- Serverul te sună pentru a trimite datele
- Problemă: dacă ești într-un birou cu centrală telefonică (firewall/NAT), apelul extern nu intră

**Mod Pasiv:** Clientul sună serverul
- Serverul îți dă un număr de telefon temporar (port dinamic)
- Tu îl suni pentru a primi datele
- Funcționează prin firewall pentru că TU inițiezi apelul

---

## 4. Implementare practică: Server pseudo-FTP

Săptămâna 9 implementăm un server simplificat care demonstrează:
- Protocolul text command-response
- Autentificare cu sesiune
- Transfer binar cu CRC
- Multi-client prin threading/async

**Comenzi suportate:**

| Comandă | Sintaxă | Descriere |
|---------|---------|-----------|
| AUTH | `AUTH user pass` | Autentificare |
| PWD | `PWD` | Director curent |
| LIST | `LIST [path]` | Listare fișiere |
| GET | `GET filename` | Download |
| PUT | `PUT filename size` | Upload |
| QUIT | `QUIT` | Deconectare |

> **Truc util la debugging:** Dacă serverul nu răspunde, verifică mai întâi cu `ss -tlnp | grep <port>`. 9 din 10 cazuri e fie serverul care nu rulează, fie un proces vechi care n-a murit și ocupă portul.

---

## 5. Întrebări de verificare

1. **Conceptual:** Care este diferența fundamentală între o conexiune TCP și o sesiune de aplicație?

2. **Practic:** De ce protocoalele de rețea folosesc big-endian, nu little-endian?

3. **Analiză:** În captura Wireshark a unei sesiuni FTP, cum identifici momentul când sesiunea (nu conexiunea) devine activă?

4. **Aplicare:** Cum ai implementa un mecanism de checkpoint pentru reluarea unui transfer întrerupt?

5. **Evaluare:** Care sunt avantajele și dezavantajele compresiei la nivelul prezentare vs. la nivelul aplicație?

---

## Rezumat

- Nivelul **sesiune (L5)** gestionează dialogul aplicație-aplicație: autentificare, sincronizare, control flux conversațional
- Nivelul **prezentare (L6)** asigură interoperabilitatea datelor: serializare, endianness, compresie, criptare
- **FTP** exemplifică clar separarea: canal de control (sesiune) vs. canal de date (prezentare/transport)
- Funcțiile `struct.pack/unpack` permit construirea de protocoale binare portabile
- `zlib` oferă compresie transparentă cu API simplu

---

## Unde se folosesc aceste tehnici

| Context | Aplicabilitate |
|---------|----------------|
| Dezvoltare API | Serializare JSON/Protobuf, versionare |
| Securitate | Înțelegerea TLS handshake |
| Cloud | Sesiuni distribuite, sticky sessions |
| DevOps | Debugging transfer fișiere, SFTP/SCP |
| IoT | Protocoale binare eficiente |

---

## Unde se așază în formarea unui programator

Un programator competent nu doar folosește biblioteci de rețea, ci **înțelege ce se întâmplă la fiecare nivel**. Când un transfer eșuează, trebuie să poți identifica dacă problema este:
- La nivel transport (conexiune refuzată, timeout)
- La nivel sesiune (autentificare invalidă, sesiune expirată)  
- La nivel prezentare (date corupte, endianness greșit)

Această săptămână construiește **vocabularul** necesar pentru diagnostic precis și soluții eficiente.

---

## Bibliografie selectivă

| Autori | Titlu | Publicație | An | DOI |
|--------|-------|------------|-----|-----|
| Kurose, Ross | Computer Networking: A Top-Down Approach | Pearson | 2021 | 10.5555/3312469 |
| Tanenbaum, Wetherall | Computer Networks | Pearson | 2011 | 10.5555/1972505 |
| Postel, Reynolds | File Transfer Protocol (FTP) | RFC 959 | 1985 | 10.17487/RFC0959 |
| Stevens, Fenner, Rudoff | UNIX Network Programming Vol.1 | Addison-Wesley | 2004 | 10.5555/1012850 |

## Standarde și specificații

| Document | Descriere |
|----------|-----------|
| RFC 959 | File Transfer Protocol |
| RFC 4217 | Securing FTP with TLS |
| RFC 2616 | HTTP/1.1 (context conexiuni persistente) |
| ISO/IEC 7498-1 | OSI Basic Reference Model |
| IEEE 754 | Floating-Point Arithmetic (endianness) |
