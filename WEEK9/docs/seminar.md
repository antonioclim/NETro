# Seminar 9 – Protocoale de Fișiere: Server FTP Custom și Testare Multi-Client

## Ce vom învăța

Construim un server pseudo-FTP de la zero: autentificare cu sesiune, header-e binare cu CRC-32, testare multi-client în Docker. La final aveți un protocol funcțional pe care îl analizați cu tshark.

### Obiective specifice

1. **Arhitectura FTP**: Distincția între canalul de control (port 21) și canalul de date (port 20 sau porturi efemere), modurile activ și pasiv, ciclul de viață al unei sesiuni autentificate.

2. **Protocol binar custom**: Header-e binare (magic bytes, lungime, checksum CRC-32) — principiile nivelului prezentare în practică.

3. **Gestionarea sesiunilor**: Stare utilizator (autentificat/neautentificat, director curent, permisiuni) pe parcursul mai multor comenzi — funcțiile nivelului sesiune.

4. **Testare cu Docker**: Orchestrare server + clienți în containere izolate pentru validarea comportamentului concurent.

5. **Analiza traficului**: Captură și interpretare pachete cu tshark pentru a vizualiza handshake-ul și răspunsurile protocolului.

---

## De ce contează

Transferul de fișiere e una dintre cele mai vechi aplicații de rețea. Deși SFTP, SCP sau HTTPS au înlocuit FTP-ul clasic în producție, mecanismele de bază sunt aceleași:

- **Depanare aplicații distribuite**: Când un microserviciu nu poate descărca configurații, cunoașterea protocolului accelerează identificarea problemei.

- **Proiectare API-uri binare**: Modbus, MQTT cu payload binar, protocoale IoT custom — toate folosesc aceleași principii: magic bytes, lungimi explicite, checksum-uri.

- **Securitate și audit**: Analiza traficului pentru detectarea exfiltrării de date necesită înțelegerea structurii protocoalelor la nivel de octeți.

- **Abilități refolosibile**: Citirea specificațiilor de protocol, implementarea parserelor binare, testarea sistemelor distribuite — valoroase indiferent de limbaj sau platformă.

> **De ce pseudo-FTP și nu FTP real?** FTP-ul din RFC 959 are prea multe comenzi și moduri pentru 100 de minute. Protocolul nostru păstrează esența — control separat de date, sesiune autentificată — dar e suficient de simplu pentru a fi implementat de la zero într-un seminar.

---

## Prerechizite

### Cunoștințe necesare

- **Săptămâna 8**: Nivelul transport (TCP/UDP), conceptul de socket, modelul client-server
- **Săptămâna 4**: Programare pe socket-uri în Python (conexiuni, send/recv)
- **Săptămâna 6**: Noțiuni de SDN și topologii simulate (Mininet)

### Configurație tehnică

| Componentă | Cerință minimă | Recomandare |
|------------|----------------|-------------|
| Python | 3.8+ | 3.10+ |
| Docker | 20.10+ | 24.0+ cu Compose v2 |
| Wireshark/tshark | 3.x | 4.x |
| RAM disponibil | 2 GB | 4 GB |
| Spațiu disk | 500 MB | 1 GB |

### Fișiere necesare din starterkit

```
starterkit_s9/
├── python/
│   ├── demos/
│   │   └── ex_9_02_pseudo_ftp.py
│   └── exercises/
│       └── ex_9_01_endianness.py
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── server-files/           # Fișiere pentru transfer
└── client-files/           # Destinație transferuri
```

---

## Partea I: Concepte Fundamentale

### 1.1 Nivelul Sesiune (L5) în Contextul FTP

Nivelul sesiune gestionează dialogul între aplicații:

**Stabilirea și terminarea sesiunilor**
- În FTP, o sesiune începe cu comanda `USER` și se încheie cu `QUIT`
- Sesiunea persistă chiar dacă transferul de date folosește conexiuni TCP separate
- Server-ul menține un context (utilizator, director curent, mod de transfer)

**Sincronizarea și punctele de control**
- FTP suportă reluarea transferurilor întrerupte (comanda `REST`)
- Serverul confirmă fiecare comandă, permițând clientului să sincronizeze starea

**Gestionarea excepțiilor**
- Timeout-uri pentru sesiuni inactive
- Mecanisme de recuperare după erori de rețea

> **Din experiența mea:** Studenții confundă frecvent "conexiune" cu "sesiune". Cel mai bun mod de a clarifica: conexiunea e socket-ul (IP:port ↔ IP:port), sesiunea e *cine* vorbește și *ce* a făcut până acum. Poți avea 10 conexiuni TCP și o singură sesiune logică, sau invers.

### 1.2 Nivelul Prezentare (L6) în Contextul Protocolului Custom

Nivelul prezentare se ocupă de reprezentarea datelor:

**Codificarea datelor**
- Protocolul nostru pseudo-FTP folosește Big Endian pentru numerele din header
- Numele fișierelor sunt codificate UTF-8
- Conținutul binar este transmis as-is

**Compresia**
- Opțional, datele pot fi comprimate cu zlib înainte de transfer
- Header-ul indică dacă payload-ul este comprimat

**Integritatea**
- CRC-32 pentru verificarea integrității fiecărui mesaj
- Magic bytes pentru identificarea tipului de protocol

### 1.3 Structura Protocolului Pseudo-FTP

```
┌──────────────────────────────────────────────────────────────┐
│                    HEADER (16 bytes)                         │
├──────────────┬──────────────┬──────────────┬────────────────┤
│ Magic (4B)   │ Length (4B)  │ CRC-32 (4B)  │ Flags (4B)     │
│ 0x46545043   │ Big Endian   │ Big Endian   │ Bit 0: Compr.  │
└──────────────┴──────────────┴──────────────┴────────────────┘
┌──────────────────────────────────────────────────────────────┐
│                    PAYLOAD (variable)                        │
│   Comandă/Răspuns + Date (dacă există)                       │
└──────────────────────────────────────────────────────────────┘
```

**Câmpurile header-ului:**

| Câmp | Offset | Dimensiune | Descriere |
|------|--------|------------|-----------|
| Magic | 0 | 4 bytes | `0x46545043` ("FTPC" în ASCII) |
| Length | 4 | 4 bytes | Lungimea payload-ului în bytes |
| CRC-32 | 8 | 4 bytes | Checksum-ul payload-ului |
| Flags | 12 | 4 bytes | Bit 0: 1=comprimat, 0=necomprimat |

### Analogie: Header-ul ca plic poștal

Gândește-te la un plic:
- **Expeditor pe plic** = Magic bytes ("de unde vine acest pachet")
- **Greutate scrisă** = Length (câți bytes sunt înăuntru)
- **Cod de bare tracking** = CRC-32 (verificare că n-a fost deschis/modificat)
- **Ștampilă "fragil"** = Flags (comprimat, urgent, etc.)

Când deschizi plicul (parsezi header-ul), știi deja ce să aștepți înăuntru.

### Analogie: CRC-ul ca sumă de control la magazin

Când cumperi 5 produse:
- Casiera scanează: 12.50 + 8.00 + 3.50 + 15.00 + 1.00 = **40.00**
- Dacă totalul de pe bon nu e 40.00, știi că ceva e greșit

CRC-ul face similar: calculează o "sumă" din toți bytes. Dacă un singur bit se schimbă, "suma" diferă și detectezi eroarea.

---

## 🗳️ Întrebări Peer Instruction

### PI-1: Endianness și interpretare greșită

**Scenariu:**
Serverul (big-endian) trimite un pachet cu `Length = 256`.
Reprezentare bytes: `00 00 01 00`

Clientul (little-endian, fără conversie) citește acești bytes.

**Ce valoare vede clientul pentru Length?**

A) 256 — valoarea corectă  
B) 1 — primul byte nenul  
C) 16777216 — bytes inversați  
D) Eroare de protocol detectată automat

<details>
<summary>📋 NOTE INSTRUCTOR (click pentru a expanda)</summary>

**Răspuns corect: C (16777216 = 0x01000000)**

**Analiza distractorilor:**
- **A (256):** Misconceptie că TCP/kernel convertește automat. Frecventă la ~40% din studenți.
- **B (1):** Confuzie cu primul byte semnificativ. ~15% din studenți.
- **C (16777216):** CORECT. Little-endian citește `00 00 01 00` ca 0x00010000.
- **D (eroare):** Crede că există validare automată. ~20% din studenți.

**Timing:** Vot 1 min → Discuție perechi 3 min → Revot 30s → Explicație 2 min

**După revot:** Demonstrează live cu `python ex_9_01_endianness.py --demo`
</details>

---

### PI-2: Sesiune vs Conexiune — Reconectare

**Scenariu:**
1. Client FTP se conectează (TCP handshake OK)
2. Trimite `USER alice`, primește `331`
3. Trimite `PASS secret`, primește `230 Logged in`
4. Conexiunea TCP se întrerupe (eroare rețea)
5. Clientul reconectează imediat (nouă conexiune TCP)

**Ce trebuie să facă clientul pentru a continua?**

A) Nimic — sesiunea e restaurată automat la reconectare  
B) Trimite din nou USER + PASS  
C) Trimite REST 0 pentru a reseta  
D) Trimite NOOP pentru a verifica starea

<details>
<summary>📋 NOTE INSTRUCTOR</summary>

**Răspuns corect: B**

**Analiza distractorilor:**
- **A:** Confuzie L4/L5 — majoritatea studenților (50%+). Cred că "conexiune" = "sesiune".
- **B:** CORECT. Sesiunea există DOAR pe conexiunea curentă. Noua conexiune = tabula rasa.
- **C:** REST e pentru offset la transfer, nu pentru autentificare.
- **D:** NOOP nu restaurează sesiunea — returnează eroare "not logged in".

**Timing:** Standard (ca PI-1)

**După revot:** Desenează pe tablă timeline cu două axe: conexiune TCP vs sesiune aplicație
</details>

---

### PI-3: CRC-32 — Detectare modificări

**Scenariu:**
Expeditor trimite:
- Payload: `"Hello"` (5 bytes)
- CRC-32 calculat: `0x3610A686`

În tranzit, un bit se modifică: `"Hello"` → `"Helmo"` (octetul `l` devine `m`)

**Ce se întâmplă la destinatar?**

A) CRC-ul rămâne identic (diferența e prea mică)  
B) CRC-ul diferă, pachetul e marcat corupt  
C) CRC-ul diferă, dar TCP retransmite automat  
D) Magic bytes invalid, pachet ignorat

<details>
<summary>📋 NOTE INSTRUCTOR</summary>

**Răspuns corect: B**

**Analiza distractorilor:**
- **A:** Nu înțelege că CRC detectează orice modificare de 1 bit. ~25% studenți.
- **B:** CORECT. CRC-32 e proiectat să detecteze modificări de 1-2 biți cu probabilitate ~100%.
- **C:** Confuzie niveluri — TCP are propriul checksum, dar CRC-ul nostru e la nivel aplicație.
- **D:** Confuzie câmpuri header — magic bytes nu se schimbă.

**Timing:** Standard

**Demo:** Modifică un byte în payload și recalculează CRC live în Python
</details>

---

### PI-4: Mod Activ vs Pasiv — Firewall

**Scenariu:**
Client FTP e în spatele unui NAT/firewall care:
- Permite conexiuni OUTBOUND (client → internet)
- Blochează conexiuni INBOUND (internet → client)

**Ce mod de transfer va funcționa?**

A) Mod activ — serverul se conectează la client  
B) Mod pasiv — clientul se conectează la server  
C) Ambele funcționează  
D) Niciunul nu funcționează

<details>
<summary>📋 NOTE INSTRUCTOR</summary>

**Răspuns corect: B**

**Analiza distractorilor:**
- **A:** În mod activ, SERVERUL inițiază conexiunea de date → blocat de firewall.
- **B:** CORECT. În mod pasiv, CLIENTUL inițiază → funcționează prin NAT.
- **C:** Nu — mod activ e blocat de firewall-ul clientului.
- **D:** Mod pasiv merge.

**Timing:** Standard

**După revot:** Desenează diagrama cu firewall, arată care săgeți trec
</details>

### Analogie: Mod Activ/Pasiv — Cine sună pe cine?

**Mod Activ:** Serverul sună clientul
- Tu (client) îi dai numărul tău de telefon serverului
- Serverul te sună pentru a trimite datele
- Problemă: dacă ești în spatele unui firewall, apelul nu intră

**Mod Pasiv:** Clientul sună serverul
- Serverul îți dă un număr de telefon temporar
- Tu îl suni pentru a primi datele
- Funcționează prin firewall pentru că TU inițiezi apelul

---

### PI-5: Header Protocol — Câmpuri

**Scenariu:**
Primim un pachet cu header (16 bytes în hex):
```
46 54 50 43 | 00 00 00 20 | AB CD 12 34 | 00 00 00 01
```

**Ce lungime are payload-ul?**

A) 16 bytes (dimensiunea header-ului)  
B) 32 bytes (0x20 în decimal)  
C) 2882343476 bytes (câmpul CRC)  
D) 1 byte (ultimul câmp)

<details>
<summary>📋 NOTE INSTRUCTOR</summary>

**Răspuns corect: B (32 bytes)**

**Analiza distractorilor:**
- **A:** Confuzie header vs payload.
- **B:** CORECT. `00 00 00 20` în big-endian = 32 decimal.
- **C:** Confuzie între câmpul Length și CRC.
- **D:** Confuzie între Length și Flags.

**Timing:** Standard

**Exercițiu follow-up:** Studenții parsează alt header manual
</details>

---

## Partea II: Demonstrații Practice

### Demo 1: Înțelegerea Endianness

**Scop**: Diferența între Big Endian și Little Endian și impactul asupra protocoalelor de rețea.

**🔮 PREDICȚIE (înainte de a rula):**
- Numărul `0x12345678` — scrie pe hârtie cei 4 bytes în Big Endian
- Acum scrie-i în Little Endian
- Ce se întâmplă dacă trimiți BE și citești LE?

**Execuție**:
```bash
cd starterkit_s9/python/exercises
python ex_9_01_endianness.py --demo
```

**Rezultat așteptat**:
```
=== Demonstrație Endianness ===
Numărul: 0x12345678

Big Endian (Network Byte Order):
  Bytes: 12 34 56 78
  Ordinea: MSB primul (cel mai semnificativ byte)

Little Endian (x86/x64):
  Bytes: 78 56 34 12
  Ordinea: LSB primul (cel mai puțin semnificativ byte)

Conversie cu struct:
  pack('>I', 0x12345678) = b'\x12\x34\x56\x78'
  pack('<I', 0x12345678) = b'\x78\x56\x34\x12'
```

**Compară predicția cu rezultatul.** Unde ai greșit și de ce?

### Demo 2: Server Pseudo-FTP

**Scop**: Pornirea serverului și testarea comenzilor.

**🔮 PREDICȚIE:**
- Pe ce port va asculta serverul?
- Ce mesaj va afișa la pornire?
- Ce se întâmplă dacă portul e deja ocupat?

**Terminal 1 - Server**:
```bash
cd starterkit_s9/python/demos
python ex_9_02_pseudo_ftp.py --mode server --port 9021
```

> **Truc util:** Dacă serverul nu pornește, verifică mai întâi cu `ss -tlnp | grep 9021`. 9 din 10 cazuri e un proces vechi care n-a murit.

**Terminal 2 - Client**:
```bash
python ex_9_02_pseudo_ftp.py --mode client --host localhost --port 9021
```

**🔮 PREDICȚIE (înainte de AUTH):**
- Ce răspuns aștepți cu credențiale corecte (`admin:secret123`)?
- Dar cu credențiale greșite?

**Secvență de comenzi**:
```
> AUTH admin:parola123
[OK] Autentificare reușită
> PWD
[OK] /
> LIST
[OK] Fișiere: document.txt (1024 bytes), imagine.png (2048 bytes)
> GET document.txt
[OK] Transfer complet: 1024 bytes, CRC: 0xA1B2C3D4
> PUT test.txt
[OK] Fișier încărcat: test.txt (512 bytes)
> QUIT
[OK] Sesiune închisă
```

### Demo 3: Testare Multi-Client cu Docker

**Scop**: Verificarea comportamentului serverului sub sarcină concurentă.

**🔮 PREDICȚIE:**
- Câți clienți se vor conecta simultan?
- În ce ordine vor primi răspunsurile?
- Ce se întâmplă dacă doi clienți cer același fișier?

**Execuție**:
```bash
cd starterkit_s9/docker
docker compose up -d
docker compose logs -f
```

**Rezultat așteptat**:
```
ftp-server  | [INFO] Server pornit pe 0.0.0.0:9021
client-1    | [INFO] Conectare la ftp-server:9021
client-2    | [INFO] Conectare la ftp-server:9021
client-3    | [INFO] Conectare la ftp-server:9021
client-1    | [OK] AUTH reușit
client-2    | [OK] AUTH reușit
client-3    | [OK] AUTH reușit
client-1    | [OK] GET test1.txt completat
client-2    | [OK] GET test2.txt completat
client-3    | [OK] PUT upload.txt completat
```

**Cleanup**:
```bash
docker compose down -v
```

---

## Partea III: Captură și Analiză Wireshark

### 3.1 Pregătirea Capturii

**Pornirea capturii cu tshark**:
```bash
# Terminal separat
tshark -i lo -f "tcp port 9021" -w capture_s9.pcap
```

### 3.2 Generarea Traficului

Rulați demo-ul 2 (server + client) în timp ce tshark capturează.

### 3.3 Analiza Capturii

**🔮 PREDICȚIE (înainte de analiză):**
- Câte pachete va avea handshake-ul TCP?
- În ce pachet apare primul "FTPC" (magic bytes)?
- Care pachet conține răspunsul la AUTH?

**Vizualizare generală**:
```bash
tshark -r capture_s9.pcap -Y "tcp.port == 9021" | head -20
```

**Output exemplu**:
```
  1   0.000000    127.0.0.1 → 127.0.0.1    TCP 74 52486 → 9021 [SYN]
  2   0.000015    127.0.0.1 → 127.0.0.1    TCP 74 9021 → 52486 [SYN, ACK]
  3   0.000025    127.0.0.1 → 127.0.0.1    TCP 66 52486 → 9021 [ACK]
  4   0.000150    127.0.0.1 → 127.0.0.1    TCP 82 52486 → 9021 [PSH, ACK] Len=16
  5   0.000201    127.0.0.1 → 127.0.0.1    TCP 82 9021 → 52486 [PSH, ACK] Len=16
```

**Extragerea payload-ului binar**:
```bash
tshark -r capture_s9.pcap -Y "tcp.port == 9021 && tcp.len > 0" \
    -T fields -e data
```

**Interpretarea header-ului** (pentru primul pachet cu date):
```
46545043 00000010 a1b2c3d4 00000000
│        │        │        │
│        │        │        └── Flags: 0 (necomprimat)
│        │        └── CRC-32: 0xA1B2C3D4
│        └── Length: 16 bytes
└── Magic: "FTPC"
```

### 3.4 Filtre Utile Wireshark

| Filtru | Scop |
|--------|------|
| `tcp.port == 9021` | Tot traficul pe portul serverului |
| `tcp.flags.syn == 1` | Doar pachetele SYN (noi conexiuni) |
| `tcp.len > 0` | Pachete cu payload (exclude ACK-uri goale) |
| `frame contains "FTPC"` | Pachete care conțin magic bytes |

---

## Mod de lucru: Pair Programming

Pentru exercițiile din Partea IV, lucrați în **perechi**:

| Rol | Responsabilitate | Durată |
|-----|------------------|--------|
| **Driver** | Tastează codul, execută comenzi | 10 min |
| **Navigator** | Dictează, verifică, caută documentație | 10 min |

**Reguli:**
1. Navigatorul NU atinge tastatura
2. Schimbați rolurile la fiecare 10 minute (folosiți timer pe telefon)
3. Discutați ÎNAINTE de a tasta — Navigator propune, Driver confirmă sau întreabă

---

## Partea IV: Exerciții Gradate

### Exercițiu 1: Comanda INFO (⭐)

**Cerință**: Adăugați comanda `INFO` care returnează informații despre server: versiune, uptime, număr de sesiuni active.

**Puncte de pornire**:
- Funcția `handle_command()` din server
- Dicționar cu statistici globale

**Rezultat așteptat**:
```
> INFO
[OK] Version: 1.0.0, Uptime: 125s, Sessions: 3
```

### Exercițiu 2: LIST cu Wildcard (⭐⭐)

**Cerință**: Modificați comanda `LIST` pentru a accepta pattern-uri glob (ex: `LIST *.txt`).

**Indicii**:
- Modulul `fnmatch` din Python
- Parserul de comandă trebuie să extragă argumentul opțional

**Rezultat așteptat**:
```
> LIST *.txt
[OK] document.txt (1024), notes.txt (512)
> LIST *.png
[OK] imagine.png (2048)
```

### Exercițiu 3: Comanda MKDIR (⭐⭐)

**Cerință**: Implementați `MKDIR <dirname>` pentru a crea directoare pe server.

**Considerente**:
- Validarea numelui (fără caractere speciale)
- Verificarea permisiunilor (utilizator autentificat)
- Gestionarea erorilor (director existent)

### Exercițiu 4: Reluarea Transferurilor (⭐⭐⭐)

**Cerință**: Implementați comenzile `REST <offset>` și `RETR <filename>` pentru a relua transferuri întrerupte.

**Algoritmul**:
1. Clientul trimite `REST <bytes_deja_descărcați>`
2. Serverul memorează offset-ul pentru sesiunea curentă
3. La `RETR`, serverul începe citirea de la offset

### Exercițiu 5: Rate Limiting (⭐⭐⭐)

**Cerință**: Adăugați limitare de viteză pentru transferuri (ex: 100 KB/s per client).

**Tehnici**:
- Token bucket algorithm
- Sleep între chunk-uri de date
- Configurare prin parametru la pornirea serverului

### Exercițiu 6: Analiza Anomalii în Captură (⭐⭐⭐)

**Cerință**: Primești un fișier `suspicious.pcap` cu o sesiune pseudo-FTP. Identifică:
1. Câte comenzi a trimis clientul?
2. Care comandă a eșuat și de ce?
3. Există pachete retransmise? Cum le identifici?

**Indicii**:
- `tshark -r suspicious.pcap -Y "tcp.analysis.retransmission"`
- Caută răspunsuri care încep cu `4xx` sau `5xx`

### Exercițiu 7: Evaluare Design Protocol (⭐⭐⭐)

**Cerință**: Compară protocolul nostru pseudo-FTP cu FTP real (RFC 959):

| Aspect | Pseudo-FTP | FTP Real | Ce e mai bun și de ce? |
|--------|------------|----------|------------------------|
| Canale | 1 | 2 (control + date) | ? |
| Format comenzi | Text | Text | ? |
| Format transfer | Binar cu header | Binar raw | ? |
| Checksum | CRC-32 per mesaj | Niciunul (TCP) | ? |

**Răspuns:** 10-15 rânduri argumentate.

### Exercițiu CHALLENGE: Transfer Multi-Fișier (🏆)

**Cerință**: Implementați `MGET <pattern>` și `MPUT <pattern>` pentru transferuri multiple.

**Componente**:
1. Expandarea pattern-ului pe server/client
2. Transfer secvențial cu raportare progres
3. Rollback în caz de eroare (opțional)
4. Raport final: fișiere reușite/eșuate

---

## Partea V: Debugging și Probleme Frecvente

> **Problemă des întâlnită în laborator:** Studenții uită să oprească serverul înainte de a-l reporni. Rezultat: "Address already in use". Soluție: `pkill -f pseudo_ftp` sau `kill $(lsof -t -i:9021)`.

### Problema 1: Connection Refused

**Simptome**: Clientul nu se poate conecta la server.

**Cauze posibile**:
- Serverul nu rulează
- Port greșit
- Firewall blocând conexiunea

**Diagnostic**:
```bash
# Verifică dacă serverul ascultă
netstat -tlnp | grep 9021
# sau
ss -tlnp | grep 9021
```

### Problema 2: Magic Bytes Invalide

**Simptome**: Server returnează "Invalid protocol magic".

**Cauze posibile**:
- Client vechi/incompatibil
- Corupție date în tranzit
- Byte order greșit la împachetare

**Diagnostic**:
```bash
# Inspectează primii bytes trimiși
tshark -r capture.pcap -Y "tcp.port == 9021" -x | head -20
```

### Problema 3: CRC Mismatch

**Simptome**: Transfer aparent reușit dar fișierul este corupt.

**Cauze posibile**:
- Calculul CRC pe date comprimate vs. necomprimate
- Trunchiere la recepție
- Buffer incomplet

**Diagnostic**:
```python
import zlib
data = open('fisier.bin', 'rb').read()
print(f"CRC-32: {zlib.crc32(data) & 0xffffffff:08X}")
```

### Problema 4: Autentificare Eșuată

**Simptome**: "Authentication failed" deși credențialele par corecte.

**Cauze posibile**:
- Spații în username/parolă
- Encoding greșit (UTF-8 vs. ASCII)
- Timeout sesiune expirată

### Problema 5: Transfer Blocat

**Simptome**: GET/PUT pornește dar nu se finalizează.

**Cauze posibile**:
- Deadlock (ambele părți așteaptă să citească)
- Buffer TCP plin
- Fișier foarte mare fără streaming

**Diagnostic**:
```bash
# Verifică starea conexiunilor
ss -tnp | grep 9021
```

### Problema 6: Docker Port Conflict

**Simptome**: `docker compose up` eșuează cu "port already in use".

**Soluție**:
```bash
# Găsește procesul care folosește portul
sudo lsof -i :9021
# Oprește containerele vechi
docker compose down
# Sau schimbă portul în docker-compose.yml
```

---

## Exerciții Suplimentare (Non-Cod)

### Exercițiu A: Parsons Problem — Ordinea handshake-ului FTP

**Instrucțiuni:** Reordonează liniile pentru a obține secvența corectă a unei sesiuni FTP:

```
___ 230 Login successful
___ QUIT
___ 220 Welcome to FTP server
___ PASS secret123
___ USER alice
___ 221 Goodbye
___ 331 Password required
___ [conexiune TCP stabilită]
```

<details>
<summary>Soluție</summary>

```
1. [conexiune TCP stabilită]
2. 220 Welcome to FTP server
3. USER alice
4. 331 Password required
5. PASS secret123
6. 230 Login successful
7. QUIT
8. 221 Goodbye
```
</details>

---

### Exercițiu B: Code Tracing — Ce face acest cod?

**Urmărește execuția pas cu pas și completează valorile:**

```python
import struct
import zlib

data = b"Test"
length = len(data)                    # length = ___
crc = zlib.crc32(data) & 0xFFFFFFFF   # crc = ___ (hex)
header = struct.pack('>4sII', b'FTPC', length, crc)

print(len(header))                     # output: ___
print(header[:4])                      # output: ___
print(header[4:8].hex())               # output: ___
```

<details>
<summary>Soluție</summary>

```python
length = 4
crc = 0xD87F7E0C  # (valoarea reală pentru b"Test")
# len(header) = 12 (4 + 4 + 4)
# header[:4] = b'FTPC'
# header[4:8].hex() = '00000004' (length în big-endian)
```
</details>

---

### Exercițiu C: Debugging — Găsește eroarea în captură

**Ai primit această captură hexadecimală de la un coleg. Identifică problema:**

```
46 54 50 43 00 00 00 08 12 34 56 78 00 00 00 00
48 65 6C 6C 6F 21 21 21
```

Header: `46 54 50 43` = "FTPC" ✓
Length: `00 00 00 08` = 8 bytes
CRC: `12 34 56 78`
Flags: `00 00 00 00`
Payload: `48 65 6C 6C 6F 21 21 21` = "Hello!!!" (8 bytes) ✓

**Întrebare:** Ce e greșit și cum detectezi problema?

<details>
<summary>Soluție</summary>

**CRC-ul nu se potrivește!**

Verificare:
```python
>>> import zlib
>>> zlib.crc32(b"Hello!!!") & 0xFFFFFFFF
0x36C43B5D  # nu e 0x12345678!
```

Pachetul e fie corupt, fie CRC-ul a fost calculat greșit.
</details>

---

## Rezumat

- **L5 aplicat:** AUTH cu stare, PWD, permisiuni per sesiune
- **L6 aplicat:** `struct.pack('>4sIII', ...)`, CRC-32, compresie gzip
- **Debugging:** `tshark -Y "tcp.len > 0" -x` pentru bytes raw
- **Docker:** `docker compose up` → 3 clienți concurenți pe același server

---

## Unde se folosesc aceste tehnici

- **Dezvoltare microservicii**: Proiectarea comunicației între servicii, alegerea formatelor de serializare (Protocol Buffers, MessagePack)
- **Sisteme embedded și IoT**: Protocoale lightweight pentru dispozitive cu resurse limitate
- **Securitate aplicații**: Auditarea traficului de rețea, detectarea anomaliilor de protocol
- **DevOps și SRE**: Debugging producție, analiza performanței rețelei

---

## Unde se așază în formarea unui programator

```
Săptămâna 9: Protocoale de Fișiere
         │
    ┌────┴────┐
    ▼         ▼
L5/L6      Implementare
Teorie     Practică
    │         │
    └────┬────┘
         │
         ▼
   Competență:
   Proiectarea și implementarea
   protocoalelor aplicație
```

Această săptămână face tranziția de la nivelurile inferioare ale stivei (fizic, legătură, rețea, transport) la nivelurile orientate către aplicație. E punctul în care cunoștințele teoretice despre rețele se transformă în abilitatea concretă de a construi servicii de rețea funcționale.

---

## Bibliografie

| Nr. | Autori | Titlu | Editor | An | DOI |
|-----|--------|-------|--------|-----|-----|
| 1 | Kurose, J., Ross, K. | Computer Networking: A Top-Down Approach | Pearson | 2021 | 10.5555/3312050 |
| 2 | Rhodes, B., Goerzen, J. | Foundations of Python Network Programming | Apress | 2014 | 10.1007/978-1-4302-5855-1 |
| 3 | Stevens, W.R. | TCP/IP Illustrated, Volume 1 | Addison-Wesley | 2011 | 10.5555/2070741 |
| 4 | Beaulieu, M. | Learning Docker | Packt | 2022 | 10.5555/3485829 |

### Standarde și Specificații

- RFC 959: File Transfer Protocol (FTP)
- RFC 2228: FTP Security Extensions
- RFC 3659: Extensions to FTP
- IEEE 802.3: Ethernet Standard (pentru contextul network byte order)
