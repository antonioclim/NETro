# Laborator 9 – Ghid Practic: Implementare și Testare Server Pseudo-FTP

## Ce vom realiza

Laborator practic: configurăm serverul pseudo-FTP, testăm transferuri, captăm trafic cu tshark și rulăm scenarii multi-client în Docker. La final produceți un fișier .pcap analizat și o notă reflexivă.

### Livrabile așteptate

La finalul laboratorului, veți avea:
1. Un server pseudo-FTP funcțional, testat local
2. Capturi de trafic (.pcap) cu analize documentate
3. Mediu Docker orchestrat pentru testare concurentă
4. Opțional: topologie Mininet pentru simulări avansate
5. Notă reflexivă completată

---

## Structura timpului (estimări)

| Pas | Activitate | Durată |
|-----|-----------|--------|
| 0 | Setup mediu | 10 min |
| 1 | Endianness și Framing | 15 min |
| 2 | Server Pseudo-FTP | 10 min |
| 3 | Client Interactiv | 15 min |
| 4 | Captură Wireshark | 20 min |
| 5 | Docker Multi-Client | 15 min |
| 6 | Mininet (opțional) | 20 min |
| 7 | Verificare și predare | 10 min |
| **Total** | | **~2h** |

---

## Pas 0: Setup Mediu de Lucru

### 0.1 Structura directorului de lucru

```
starterkit_s9/
├── README.md
├── Makefile
├── requirements.txt
├── python/
│   ├── demos/
│   │   └── ex_9_02_pseudo_ftp.py
│   └── exercises/
│       └── ex_9_01_endianness.py
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── scripts/
│   ├── setup.sh
│   ├── verify.sh
│   └── capture.sh
├── server-files/
│   ├── document.txt
│   └── sample.bin
├── client-files/
└── pcap/
```

### 0.2 Instalarea dependențelor

```bash
# Navigați în directorul starterkit
cd starterkit_s9

# Instalați dependențele Python
pip install -r requirements.txt

# Verificați instalarea
python --version    # >= 3.8
docker --version    # >= 20.10
tshark --version    # >= 3.0
```

### 0.3 Verificare rapidă

```bash
make verify
```

**Output așteptat**:
```
[✓] Python 3.10.12 installed
[✓] Docker 24.0.5 available
[✓] tshark 4.0.3 ready
[✓] All dependencies satisfied
[✓] Server files present
[✓] Environment ready!
```

### 0.4 Posibile probleme

| Problemă | Soluție |
|----------|---------|
| `pip: command not found` | Instalați Python: `sudo apt install python3-pip` |
| `docker: permission denied` | Adăugați user la grupul docker: `sudo usermod -aG docker $USER` |
| `tshark: command not found` | Instalați: `sudo apt install tshark` |

**Checklist Pas 0**:
- [ ] Directorul starterkit_s9 există și conține toate fișierele
- [ ] `make verify` returnează toate check-urile verzi
- [ ] Terminal disponibil pentru comenzi

---

## Pas 1: Endianness și Framing Binar

### 1.1 Executarea demo-ului

**🔮 PREDICȚIE (notează pe hârtie înainte de a rula):**
1. Numărul `0x12345678` — scrie cei 4 bytes în Big Endian
2. Acum scrie-i în Little Endian
3. Dacă trimiți BE și citești LE, ce valoare obții?

```bash
cd python/exercises
python ex_9_01_endianness.py
```

### 1.2 Output așteptat

```
╔══════════════════════════════════════════════════════════════╗
║           DEMONSTRAȚIE ENDIANNESS ȘI FRAMING                 ║
╚══════════════════════════════════════════════════════════════╝

═══ Partea 1: Endianness ═══

Numărul de test: 0x12345678 (305419896 în decimal)

Big Endian (Network Byte Order):
  Reprezentare bytes: 12 34 56 78
  MSB (Most Significant Byte) primul
  Folosit în: protocoale de rețea, formatul network

Little Endian (Host Byte Order pe x86):
  Reprezentare bytes: 78 56 34 12
  LSB (Least Significant Byte) primul
  Folosit în: procesoare Intel/AMD, ARM (configurabil)

═══ Partea 2: Împachetare cu struct ═══

pack('>I', 0x12345678) = b'\x12\x34\x56\x78'  # Big Endian
pack('<I', 0x12345678) = b'\x78\x56\x34\x12'  # Little Endian
pack('!I', 0x12345678) = b'\x12\x34\x56\x78'  # Network (= Big)

═══ Partea 3: Header Protocol Custom ═══

Structura header (16 bytes):
┌────────────┬────────────┬────────────┬────────────┐
│ Magic (4B) │ Length(4B) │ CRC-32(4B) │ Flags (4B) │
└────────────┴────────────┴────────────┴────────────┘

Exemplu header:
  Magic:  0x46545043 ("FTPC")
  Length: 0x00000100 (256 bytes)
  CRC-32: 0xABCD1234
  Flags:  0x00000001 (comprimat)

Bytes rezultați: 46 54 50 43 00 00 01 00 AB CD 12 34 00 00 00 01
```

**După rulare:** Compară predicția cu rezultatul. Unde ai greșit și de ce?

### 1.3 Experimentare

Modificați următoarele în script și observați rezultatele:

```python
# Schimbați numărul de test
TEST_NUMBER = 0xDEADBEEF

# Încercați cu numere negative
SIGNED_NUMBER = -1

# Testați string-uri de diferite lungimi
TEST_STRING = "Rețele de Calculatoare"
```

### 1.4 Întrebare de control

> Ce s-ar întâmpla dacă serverul folosește Big Endian iar clientul Little Endian pentru câmpul Length, fără conversie?

**Răspuns**: Dacă serverul trimite Length = 256 (0x00000100 în BE), clientul care citește în LE va interpreta ca 0x00010000 = 65536. Va aștepta 65536 bytes în loc de 256, blocând transferul.

**Checklist Pas 1**:
- [ ] Script-ul rulează fără erori
- [ ] Înțeleg diferența dintre Big/Little Endian
- [ ] Am experimentat cu valori diferite

---

## Pas 2: Pornirea Serverului Pseudo-FTP

### 2.1 Pornirea serverului

**🔮 PREDICȚIE:**
- Pe ce port va asculta serverul?
- Ce mesaj va afișa la pornire?
- Ce se întâmplă dacă portul e deja ocupat?

```bash
cd ../demos
python ex_9_02_pseudo_ftp.py --mode server --port 9021
```

### 2.2 Output așteptat

```
╔══════════════════════════════════════════════════════════════╗
║             PSEUDO-FTP SERVER v1.0                           ║
╚══════════════════════════════════════════════════════════════╝

[2025-01-01 10:00:00] [INFO] Server configuration:
  - Host: 0.0.0.0
  - Port: 9021
  - Files directory: ./server-files
  - Max connections: 10

[2025-01-01 10:00:00] [INFO] Server started, listening on 0.0.0.0:9021
[2025-01-01 10:00:00] [INFO] Press Ctrl+C to stop
```

> **Problemă des întâlnită:** Studenții uită să oprească serverul înainte de a-l reporni. Rezultat: "Address already in use". Soluție: `pkill -f pseudo_ftp` sau `kill $(lsof -t -i:9021)`.

### 2.3 Verificarea serverului (terminal separat)

```bash
# Verifică că serverul ascultă
netstat -tlnp | grep 9021
# sau
ss -tlnp | grep 9021
```

**Output așteptat**:
```
tcp   LISTEN  0       10       0.0.0.0:9021      0.0.0.0:*    users:(("python",pid=1234,fd=3))
```

### 2.4 Analiza codului (fragmente cheie)

**Structura header-ului**:
```python
HEADER_FORMAT = '>4sIII'  # magic(4s), length(I), crc(I), flags(I)
HEADER_SIZE = 16
MAGIC = b'FTPC'
```

**Trimiterea unui mesaj**:
```python
def send_message(sock, payload, compressed=False):
    crc = zlib.crc32(payload) & 0xffffffff
    flags = 1 if compressed else 0
    header = struct.pack(HEADER_FORMAT, MAGIC, len(payload), crc, flags)
    sock.sendall(header + payload)
```

**Checklist Pas 2**:
- [ ] Serverul pornește fără erori
- [ ] Portul 9021 este în starea LISTEN
- [ ] Am înțeles structura header-ului

---

## Mod de lucru: Pair Programming

Pentru pașii 3-5, lucrați în **perechi**:

| Rol | Responsabilitate | Durată |
|-----|------------------|--------|
| **Driver** | Tastează codul, execută comenzi | 10 min |
| **Navigator** | Dictează, verifică, caută documentație | 10 min |

**Reguli:**
1. Navigatorul NU atinge tastatura
2. Schimbați rolurile la fiecare 10 minute (folosiți timer pe telefon)
3. Discutați ÎNAINTE de a tasta — Navigator propune, Driver confirmă sau întreabă

**La Pas 3 (client interactiv):**
- Driver: tastează comenzile în terminal client
- Navigator: verifică output-ul și compară cu "Output așteptat"

**La Pas 4 (captură):**
- Driver: execută tshark și comenzile de analiză
- Navigator: identifică magic bytes și explică ce vede

---

## Pas 3: Client Interactiv

### 3.1 Pornirea clientului (terminal nou)

```bash
python ex_9_02_pseudo_ftp.py --mode client --host localhost --port 9021
```

### 3.2 Sesiune interactivă

**🔮 PREDICȚIE (înainte de fiecare comandă):**
- Ce răspuns aștepți pentru AUTH cu credențiale corecte (`admin:secret123`)?
- Dar cu credențiale greșite?
- Ce returnează LIST dacă nu ești autentificat?

Introduceți comenzile în ordinea indicată:

```
pseudo-ftp> AUTH admin:secret123
[OK] Authentication successful. Welcome, admin!

pseudo-ftp> PWD
[OK] Current directory: /

pseudo-ftp> LIST
[OK] Directory listing:
  document.txt    1024 bytes   2025-01-01 09:00
  sample.bin      2048 bytes   2025-01-01 09:00

pseudo-ftp> GET document.txt
[OK] Transfer complete: 1024 bytes
    CRC-32: 0xA1B2C3D4
    Saved to: ./client-files/document.txt

pseudo-ftp> PUT test_upload.txt
[INFO] Reading local file: test_upload.txt
[OK] Upload complete: 512 bytes
    CRC-32: 0xE5F6A7B8

pseudo-ftp> QUIT
[OK] Session closed. Goodbye!
```

### 3.3 Verificarea transferurilor

**🔮 PREDICȚIE:**
- Ce dimensiune va avea fișierul descărcat?
- Hash-urile MD5 vor fi identice?

```bash
# Verifică fișierul descărcat
ls -la ../client-files/
cat ../client-files/document.txt

# Verifică integritatea
md5sum ../server-files/document.txt ../client-files/document.txt
```

**Output așteptat**:
```
d41d8cd98f00b204e9800998ecf8427e  ../server-files/document.txt
d41d8cd98f00b204e9800998ecf8427e  ../client-files/document.txt
```

### 3.4 Testarea erorilor

Testați următoarele scenarii:

```
# Autentificare greșită
pseudo-ftp> AUTH wrong:credentials
[ERROR] Authentication failed

# Comandă fără autentificare (restart client)
pseudo-ftp> LIST
[ERROR] Not authenticated. Use AUTH first.

# Fișier inexistent
pseudo-ftp> GET nonexistent.txt
[ERROR] File not found: nonexistent.txt

# Comandă necunoscută
pseudo-ftp> INVALID
[ERROR] Unknown command: INVALID
```

**Checklist Pas 3**:
- [ ] Autentificare reușită cu credențiale corecte
- [ ] GET și PUT funcționează
- [ ] Erorile sunt gestionate corect
- [ ] Fișierul descărcat are conținut identic cu originalul

---

## Pas 4: Captură și Analiză Wireshark

### 4.1 Pornirea capturii

**🔮 PREDICȚIE:**
- Câte pachete va avea handshake-ul TCP?
- În ce pachet apare primul "FTPC" (magic bytes)?
- Care pachet conține răspunsul la AUTH?

```bash
# Terminal separat - pornim captura
tshark -i lo -f "tcp port 9021" -w session_capture.pcap &
```

### 4.2 Generarea traficului (terminal client)

```bash
# Reconectare și câteva comenzi
python ex_9_02_pseudo_ftp.py --mode client --host localhost --port 9021
```

Executați:
```
AUTH admin:secret123
LIST
GET document.txt
QUIT
```

### 4.3 Oprirea capturii

```bash
# Oprește tshark
pkill tshark
sleep 1
ls -la session_capture.pcap
```

### 4.4 Analiza capturii

**Vizualizare generală**:
```bash
tshark -r session_capture.pcap | head -30
```

**Output exemplu**:
```
    1   0.000000    127.0.0.1 → 127.0.0.1    TCP 74 58294 → 9021 [SYN] Seq=0
    2   0.000012    127.0.0.1 → 127.0.0.1    TCP 74 9021 → 58294 [SYN, ACK]
    3   0.000018    127.0.0.1 → 127.0.0.1    TCP 66 58294 → 9021 [ACK]
    4   0.001234    127.0.0.1 → 127.0.0.1    TCP 98 58294 → 9021 [PSH, ACK] Len=32
    5   0.001456    127.0.0.1 → 127.0.0.1    TCP 82 9021 → 58294 [PSH, ACK] Len=16
```

**Extragere pachete cu payload**:
```bash
tshark -r session_capture.pcap -Y "tcp.len > 0" \
    -T fields -e frame.number -e tcp.srcport -e tcp.dstport -e tcp.len
```

**Vizualizare hexadecimală**:
```bash
tshark -r session_capture.pcap -Y "tcp.len > 0" -x | head -50
```

### 4.5 Identificarea elementelor protocolului

Căutați în output-ul hexadecimal:

| Element | Valoare hex | Semnificație |
|---------|-------------|--------------|
| Magic bytes | `46 54 50 43` | "FTPC" în ASCII |
| Length | `00 00 00 XX` | Lungimea payload-ului |
| Handshake TCP | SYN, SYN-ACK, ACK | Primele 3 pachete |
| Terminare | FIN, FIN-ACK, ACK | Ultimele pachete |

### 4.6 Salvarea analizei

```bash
# Creați un raport text
tshark -r session_capture.pcap > analysis_report.txt
echo "=== Statistici ===" >> analysis_report.txt
tshark -r session_capture.pcap -z io,stat,1 >> analysis_report.txt
```

**Checklist Pas 4**:
- [ ] Fișierul .pcap a fost generat
- [ ] Am identificat handshake-ul TCP (SYN, SYN-ACK, ACK)
- [ ] Am găsit magic bytes "FTPC" în payload
- [ ] Am salvat raportul de analiză

---

## Pas 5: Testare Multi-Client cu Docker

### 5.1 Verificarea configurației Docker

**🔮 PREDICȚIE:**
- Câți clienți se vor conecta simultan?
- În ce ordine vor primi răspunsurile?
- Ce se întâmplă dacă doi clienți cer același fișier?

```bash
cd ../docker
cat docker-compose.yml
```

**Structură așteptată**:
```yaml
version: '3.8'
services:
  ftp-server:
    build: .
    ports:
      - "9021:9021"
    volumes:
      - ../server-files:/data
    command: python /app/ex_9_02_pseudo_ftp.py --mode server
    
  client-1:
    build: .
    depends_on:
      - ftp-server
    command: python /app/client_test.py --host ftp-server --tasks get
    
  client-2:
    build: .
    depends_on:
      - ftp-server
    command: python /app/client_test.py --host ftp-server --tasks put
    
  client-3:
    build: .
    depends_on:
      - ftp-server
    command: python /app/client_test.py --host ftp-server --tasks mixed
```

### 5.2 Pornirea orchestrației

```bash
# Construiți imaginile
docker compose build

# Porniți toate serviciile
docker compose up
```

### 5.3 Output așteptat

```
[+] Running 4/4
 ✔ Container docker-ftp-server-1  Created
 ✔ Container docker-client-1-1    Created
 ✔ Container docker-client-2-1    Created
 ✔ Container docker-client-3-1    Created

ftp-server-1  | [INFO] Server started on 0.0.0.0:9021
client-1-1    | [INFO] Connecting to ftp-server:9021...
client-2-1    | [INFO] Connecting to ftp-server:9021...
client-3-1    | [INFO] Connecting to ftp-server:9021...
ftp-server-1  | [INFO] Client connected from 172.18.0.3
ftp-server-1  | [INFO] Client connected from 172.18.0.4
ftp-server-1  | [INFO] Client connected from 172.18.0.5
client-1-1    | [OK] AUTH successful
client-2-1    | [OK] AUTH successful
client-3-1    | [OK] AUTH successful
client-1-1    | [OK] GET document.txt completed (1024 bytes)
client-2-1    | [OK] PUT test_from_client2.txt completed (512 bytes)
client-3-1    | [OK] LIST completed
client-3-1    | [OK] GET sample.bin completed (2048 bytes)
client-1-1    | [INFO] All tasks completed. Disconnecting.
client-2-1    | [INFO] All tasks completed. Disconnecting.
client-3-1    | [INFO] All tasks completed. Disconnecting.
```

### 5.4 Verificarea rezultatelor

```bash
# Verifică fișierele create pe server
docker compose exec ftp-server ls -la /data

# Verifică logurile individual
docker compose logs client-1
docker compose logs client-2
```

### 5.5 Cleanup

```bash
docker compose down -v
docker system prune -f
```

**Checklist Pas 5**:
- [ ] `docker compose build` reușește
- [ ] Toate cele 3 clienți se conectează
- [ ] Transferurile sunt complete
- [ ] Cleanup efectuat

---

## Pas 6: Topologie Mininet (Opțional)

### 6.1 Verificarea Mininet

```bash
# Verifică instalarea
sudo mn --version

# Test rapid
sudo mn --test pingall
```

### 6.2 Pornirea topologiei custom

```bash
cd ../mininet/topologies
sudo python topo_base.py
```

### 6.3 Comenzi în CLI Mininet

```
mininet> nodes
available nodes are: h1 h2 s1

mininet> h1 ifconfig
h1-eth0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>
    inet 10.0.0.1  netmask 255.0.0.0

mininet> h2 ifconfig
h2-eth0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>
    inet 10.0.0.2  netmask 255.0.0.0

mininet> pingall
*** Ping: testing ping reachability
h1 -> h2
h2 -> h1
*** Results: 0% dropped (2/2 received)
```

### 6.4 Rularea serverului în Mininet

```
mininet> h1 python /path/to/ex_9_02_pseudo_ftp.py --mode server --port 9021 &
mininet> h2 python /path/to/ex_9_02_pseudo_ftp.py --mode client --host 10.0.0.1 --port 9021
```

### 6.5 Adăugarea latenței

**🔮 PREDICȚIE:**
- Cu 50ms latență adăugată, cât va dura un ping round-trip?
- Cum va afecta asta transferul de fișiere?

```
mininet> sh tc qdisc add dev s1-eth1 root netem delay 50ms
mininet> h1 ping -c 3 h2
PING 10.0.0.2: 64 bytes icmp_seq=1 ttl=64 time=100.2 ms
```

**Checklist Pas 6** (opțional):
- [ ] Mininet pornește corect
- [ ] Ping între h1 și h2 funcționează
- [ ] Am testat serverul între hosts Mininet
- [ ] Am experimentat cu latență artificială

---

## Pas 7: Verificare Finală și Predare

### 7.1 Smoke test complet

```bash
cd ..
make clean
make setup
make run-demo
make capture
make verify
```

**Output așteptat**:
```
=== Clean ===
[OK] Removed temporary files

=== Setup ===
[OK] Dependencies installed
[OK] Directories created

=== Run Demo ===
[OK] Server started
[OK] Client executed commands
[OK] Transfer verified

=== Capture ===
[OK] PCAP file generated (2.5 KB)

=== Verify ===
[✓] All checks passed!
```

### 7.2 Checklist final pentru predare

**Artefacte necesare**:
- [ ] `pcap/session_capture.pcap` - captură trafic
- [ ] `pcap/analysis_report.txt` - analiză documentată
- [ ] `client-files/document.txt` - fișier descărcat corect
- [ ] Capturi de ecran cu:
  - [ ] Output server pornit
  - [ ] Sesiune client interactiv
  - [ ] Docker compose logs
  - [ ] (opțional) Mininet pingall

**Notă reflexivă** (5-10 rânduri):
- Ce am învățat nou în acest laborator?
- Ce dificultăți am întâmpinat și cum le-am rezolvat?
- Cum se leagă acest laborator de alte materii sau proiecte personale?

### 7.3 Template notă reflexivă

```markdown
## Notă Reflexivă - Laborator 9

**Student**: [Nume Prenume]
**Grupa**: [Grupa]
**Data**: [Data]

### Ce am învățat
[Descrieți 2-3 concepte sau tehnici noi pe care le-ați asimilat]

### Dificultăți întâmpinate
[Menționați problemele și soluțiile găsite]

### Conexiuni
[Cum se leagă de alte discipline sau proiecte]

### Observații suplimentare
[Orice alt comentariu relevant]
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

### Exercițiu D: Diagnoză Captură — Identifică anomalii

**Primești acest output de la `tshark -r suspicious.pcap`:**

```
1   0.000000  127.0.0.1 → 127.0.0.1  TCP  [SYN]
2   0.000010  127.0.0.1 → 127.0.0.1  TCP  [SYN, ACK]
3   0.000015  127.0.0.1 → 127.0.0.1  TCP  [ACK]
4   0.001000  127.0.0.1 → 127.0.0.1  TCP  Len=32 [PSH, ACK]
5   0.001500  127.0.0.1 → 127.0.0.1  TCP  Len=16 [PSH, ACK]
6   0.002000  127.0.0.1 → 127.0.0.1  TCP  Len=32 [PSH, ACK]
7   2.002100  127.0.0.1 → 127.0.0.1  TCP  Len=32 [PSH, ACK]
8   2.002200  127.0.0.1 → 127.0.0.1  TCP  [RST]
```

**Întrebări:**
1. Ce s-a întâmplat între pachetul 6 și 7?
2. Ce indică pachetul 8 (RST)?
3. Care e problema probabilă?

<details>
<summary>Soluție</summary>

1. **Pauză de 2 secunde** — probabil un timeout sau client blocat
2. **RST (Reset)** — conexiunea a fost închisă forțat, nu graceful (fără FIN)
3. **Problema probabilă:** Clientul a așteptat un răspuns care n-a venit (timeout pe server sau deadlock), apoi a închis forțat conexiunea.
</details>

---

## Rezumat tehnic

- **Setup verificat:** `make verify` → all green
- **Protocol binar:** header 16 bytes + payload variabil
- **Captură generată:** `artifacts/demo.pcap`
- **Docker testat:** transfer simultan fără corupție

---

## Unde se folosesc aceste tehnici

- **Dezvoltare backend**: Implementarea și testarea microserviciilor
- **DevOps**: CI/CD pentru aplicații distribuite
- **Security**: Analiza și auditarea traficului de rețea
- **Embedded/IoT**: Protocoale custom pentru dispozitive

---

## Resurse suplimentare

- Documentație tshark: https://www.wireshark.org/docs/man-pages/tshark.html
- Docker Compose: https://docs.docker.com/compose/
- Mininet Walkthrough: http://mininet.org/walkthrough/
- Python struct module: https://docs.python.org/3/library/struct.html
