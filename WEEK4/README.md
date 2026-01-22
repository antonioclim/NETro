# Starterkit Săptămâna 4: Nivelul Fizic, Legătură de Date & Protocoale Custom

> **Curs:** Rețele de Calculatoare  
> **Program:** Informatică Economică, Anul III, Semestrul 2  
> **Instituție:** Academia de Studii Economice București - CSIE  
> **Săptămâna:** 4 din 14

---

## Cuprins

1. [Obiective de Învățare](#obiective-de-învățare)
2. [Structura Starterkit](#structura-starterkit)
3. [Cerințe Sistem](#cerințe-sistem)
4. [Instalare Rapidă](#instalare-rapidă)
5. [Ghid de Utilizare](#ghid-de-utilizare)
6. [Protocoale Implementate](#protocoale-implementate)
7. [Exerciții Practice](#exerciții-practice)
8. [Depanare](#depanare)
9. [Resurse și Referințe](#resurse-și-referințe)

---

## Obiective de Învățare

La final, ar trebui să poți:

### Nivel Cognitiv - Înțelegere
- Descrii rolul și limitările nivelului fizic
- Explici TEXT vs BINARY – când folosești fiecare
- Înțelegi de ce TCP necesită framing suplimentar (stream vs mesaje delimitate)
- Identifici la ce ajută CRC32

### Nivel Aplicativ - Implementare
- Implementezi servere TCP concurente cu threading
- Construiești protocoale custom peste TCP și UDP
- Folosești `struct` pentru serializare binară
- Calculezi și verifici CRC32

### Nivel Analitic - Investigare
- Capturezi și analizezi trafic cu tcpdump/tshark
- Compari overhead-ul TEXT vs BINARY
- Diagnostichezi probleme de comunicare la nivel de bytes

---

## Structura Starterkit

```
starterkit_s4/
│
├── README.md                       # Acest fișier
├── Makefile                        # Automatizare (make help)
│
├── python/
│   ├── apps/                       # Aplicații complete
│   │   ├── text_proto_server.py    # Server TCP protocol text
│   │   ├── text_proto_client.py    # Client TCP protocol text
│   │   ├── binary_proto_server.py  # Server TCP protocol binar
│   │   ├── binary_proto_client.py  # Client TCP protocol binar
│   │   ├── udp_sensor_server.py    # Server UDP senzori
│   │   └── udp_sensor_client.py    # Client/simulator senzori
│   ├── utils/                      # Utilități partajate
│   │   ├── io_utils.py             # recv_exact, recv_until
│   │   └── proto_common.py         # Definiții protocoale, CRC32
│   ├── templates/                  # Template-uri pentru exerciții
│   │   └── text_server_template.py # TODO: implementare COUNT
│   └── solutions/                  # Soluții (pentru cadre didactice)
│
├── scripts/
│   ├── setup.sh                    # Instalare dependențe
│   └── run_all.sh                  # Demo complet
│
├── tests/
│   └── smoke_test.sh               # Verificare rapidă
│
├── docs/                           # Documentație Markdown
│   ├── curs/curs.md               # Material curs
│   ├── seminar/seminar.md         # Ghid seminar cu timing
│   ├── lab/lab.md                 # Instrucțiuni laborator
│   └── exercises/activities.md    # Activități complementare
│
├── assets/images/                  # Diagrame PNG
├── results/                        # Loguri generate (gitignore)
└── pcap/                           # Capturi de rețea (gitignore)
```

---

## Cerințe Sistem

### Obligatorii
| Component | Versiune Minimă | Verificare |
|-----------|-----------------|------------|
| Python | 3.8+ | `python3 --version` |

### Recomandate (pentru capturi și analiză)
| Component | Scop | Instalare |
|-----------|------|-----------|
| tcpdump | Captură pachete | `sudo apt install tcpdump` |
| tshark | Analiză avansată | `sudo apt install tshark` |
| netcat | Test manual | `sudo apt install netcat` |

Toate modulele Python necesare sunt din biblioteca standard: socket, struct, zlib, threading. Nu trebuie să instalezi nimic extra.

---

## Instalare Rapidă

```bash
# 1. Dezarhivare
unzip starterkit_s4.zip
cd starterkit_s4

# 2. Setup
chmod +x scripts/*.sh tests/*.sh
./scripts/setup.sh

# 3. Verificare
make verify

# 4. Demo rapid
make run-demo
```

Dacă ceva nu merge, vezi secțiunea Depanare.

---

## Ghid de Utilizare

### Comenzi Make Principale

```bash
make help           # Afișează toate opțiunile
make verify         # Verifică mediul (Python, porturi)
make check          # Verifică sintaxa Python
make test           # Rulează smoke test

make server-text    # Pornește server TEXT (port 5400)
make server-binary  # Pornește server BINAR (port 5401)
make server-udp     # Pornește server UDP (port 5402)

make run-demo       # Demo complet (toate protocoalele)
make capture        # Captură trafic pe loopback
make clean          # Curățare fișiere temporare
make reset          # Reset complet (oprire servere + curățare)
```

### Testare Manuală Protocol TEXT

```bash
# Terminal 1: pornire server
make server-text

# Terminal 2: client interactiv
python3 python/apps/text_proto_client.py --host localhost --port 5400

# Sau comenzi batch:
python3 python/apps/text_proto_client.py --host localhost --port 5400 \
    -c "SET name Alice" -c "GET name" -c "COUNT"
```

### Testare Manuală Protocol BINAR

```bash
# Terminal 1: pornire server
make server-binary

# Terminal 2: client interactiv
python3 python/apps/binary_proto_client.py --host localhost --port 5401

# Comenzi disponibile: echo, put, get, count, keys, quit
```

### Testare Senzori UDP

```bash
# Terminal 1: pornire server
make server-udp

# Terminal 2: simulare senzori
python3 python/apps/udp_sensor_client.py --host localhost --port 5402 \
    --sensor-id 1 --temp 23.5 --location "Lab1"

# Mod continuu (un pachet pe secundă)
python3 python/apps/udp_sensor_client.py --host localhost --port 5402 \
    --sensor-id 1 --location "Lab1" --continuous --interval 1.0

# Testare detecție erori (pachet corupt)
python3 python/apps/udp_sensor_client.py --host localhost --port 5402 \
    --sensor-id 99 --temp 0.0 --location "Test" --corrupt
```

---

## Protocoale Implementate

### 1. Protocol TEXT over TCP (Port 5400)

**Framing:** Length-prefix
```
<LEN> <PAYLOAD>

Exemplu: "11 SET name Alice"
         ^^  ^^^^^^^^^^^^^^
         |   payload (11 bytes)
         lungime payload
```

**Comenzi:**
| Comandă | Descriere | Exemplu |
|---------|-----------|---------|
| PING | Test conectivitate | `PING` → `OK pong` |
| SET | Stochează valoare | `SET key value` → `OK stored key` |
| GET | Citește valoare | `GET key` → `OK key value` |
| DEL | Șterge cheie | `DEL key` → `OK deleted` |
| COUNT | Număr chei | `COUNT` → `OK 3 keys` |
| KEYS | Lista chei | `KEYS` → `OK key1 key2 key3` |
| QUIT | Deconectare | `QUIT` → `OK bye` |

### 2. Protocol BINAR over TCP (Port 5401)

**Header fix (14 bytes):**
```
+--------+--------+--------+------------+--------+--------+
| magic  |version | type   |payload_len |  seq   | crc32  |
| 2B     | 1B     | 1B     | 2B         |  4B    | 4B     |
+--------+--------+--------+------------+--------+--------+
  "NP"      1     1-255     0-65535     uint32   uint32
```

Gândește-te la header ca la un plic poștal standardizat. Poștașul știe exact unde să caute adresa, greutatea, codul poștal – fără să deschidă plicul. La fel, serverul știe că primii 2 bytes sunt "NP", următorul e versiunea, și tot așa.

**Tipuri mesaje:**
- ECHO_REQ (1) / ECHO_RESP (2)
- PUT_REQ (3) / PUT_RESP (4)  
- GET_REQ (5) / GET_RESP (6)
- COUNT_REQ (9) / COUNT_RESP (10)
- KEYS_REQ (7) / KEYS_RESP (8)
- ERROR (255)

### 3. Protocol UDP Senzori (Port 5402)

**Datagram fix (23 bytes):**
```
+--------+-----------+--------+----------+--------+
|version | sensor_id |  temp  | location | crc32  |
| 1B     | 4B        | 4B(f)  | 10B      | 4B     |
+--------+-----------+--------+----------+--------+
```

---

## Exerciții Practice

### Exercițiul 1: Implementare COUNT (Template)

**Fișier:** `python/templates/text_server_template.py`

**Obiectiv:** Completează implementarea comenzii COUNT.

```bash
# Editează fișierul
nano python/templates/text_server_template.py

# Găsește TODO-ul și implementează COUNT
# Hint: len(state) returnează numărul de chei

# Testare
python3 python/templates/text_server_template.py
# În alt terminal:
python3 python/apps/text_proto_client.py -c "SET a 1" -c "SET b 2" -c "COUNT"
# Așteptat: OK 2 keys
```

### Exercițiul 2: Captură și Analiză Trafic

```bash
# Terminal 1: pornire server
make server-text

# Terminal 2: pornire captură
sudo tcpdump -i lo -w capture.pcap port 5400

# Terminal 3: generare trafic
python3 python/apps/text_proto_client.py -c "SET name Alice" -c "GET name"

# Oprire captură (Ctrl+C în Terminal 2)

# Analiză
tcpdump -r capture.pcap -X | head -50
# sau cu tshark:
tshark -r capture.pcap -V
```

### Exercițiul 3: Comparație Overhead TEXT vs BINARY

Calculează overhead-ul pentru aceeași valoare:

```python
# TEXT: "11 SET name Alice"
# = 2 (lungime) + 1 (spațiu) + 3 (SET) + 1 (spațiu) + 4 (name) + 1 (spațiu) + 5 (Alice)
# = 17 bytes

# BINARY: header(14) + payload
# payload = key_len(1) + key(4) + value(5) = 10 bytes
# Total = 14 + 10 = 24 bytes

# Pentru mesaje mici, TEXT câștigă. Pentru mesaje mari, BINARY.
```

### Activități Complementare

Pentru consolidare fără a scrie cod, vezi **docs/exercises/activities.md**:
- Parsons Problems – reordonare linii de cod
- Code Tracing – execuție mentală pas cu pas
- Debugging Exercises – găsește bug-uri în cod dat
- Code Reading – înțelege și explică cod existent

---

## Depanare

### Port deja în uz
```bash
# Găsire proces
sudo lsof -i :5400
# Oprire
sudo kill -9 <PID>
# Sau reset complet
make reset
```

### Connection refused
```bash
# Verificare server rulează
pgrep -a python | grep proto

# Pornire manuală cu verbose
python3 python/apps/text_proto_server.py --verbose
```

### Module not found
```bash
# Verificare structură
ls -la python/utils/

# Rulare din directorul corect
cd starterkit_s4
python3 python/apps/text_proto_server.py
```

Pentru o strategie de debugging pas cu pas, vezi **docs/lab/lab.md**.

---

## Resurse și Referințe

### Bibliografie
1. Kurose, J. & Ross, K. (2016). *Computer Networking: A Top-Down Approach*, 7th Ed.
2. Rhodes, B. & Goerzen, J. (2014). *Foundations of Python Network Programming*

### Documentație Python
- [socket — Low-level networking interface](https://docs.python.org/3/library/socket.html)
- [struct — Interpret bytes as packed binary data](https://docs.python.org/3/library/struct.html)
- [zlib — Compression compatible with gzip](https://docs.python.org/3/library/zlib.html)

### RFC-uri Relevante
- [RFC 826 - ARP](https://tools.ietf.org/html/rfc826)
- [RFC 793 - TCP](https://tools.ietf.org/html/rfc793)
- [RFC 768 - UDP](https://tools.ietf.org/html/rfc768)

---

## Licență

Material didactic pentru uzul studenților ASE-CSIE.  
© 2025 Catedra de Informatică și Cibernetică Economică

---

*Ultima actualizare: Ianuarie 2026*  
*Revolvix&Hypotheticalandrei*
