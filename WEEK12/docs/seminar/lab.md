# Laborator 12: Experimente Email & RPC

> **Disciplină:** Rețele de Calculatoare  
> **Săptămâna:** 12 din 14  
> **Durata:** 2 ore  
> **Autor:** Revolvix&Hypotheticalandrei

---

## Obiective

După parcurgerea acestui laborator, veți putea:
1. Rula și analiza o sesiune SMTP completă
2. Captura și interpreta traficul email cu tshark
3. Implementa și testa apeluri JSON-RPC
4. Compara performanța JSON-RPC vs XML-RPC
5. Identifica și rezolva erori comune

---

## Cerințe preliminare

- Python 3.8+
- Wireshark/tshark instalat
- Starterkit-ul dezarhivat
- Cunoștințe TCP/HTTP din săptămânile anterioare

---

## Step 0: Setup mediu

### 0.1 Structura starterkit

```
s12_starterkit/
├── Makefile              # Automatizări
├── README.md             # Documentație
├── requirements.txt      # Dependențe Python
├── src/
│   ├── email/           # SMTP server/client
│   │   ├── smtp_server.py
│   │   └── smtp_client.py
│   └── rpc/
│       ├── jsonrpc/     # JSON-RPC implementation
│       └── xmlrpc/      # XML-RPC implementation
├── exercises/           # Exerciții self-contained
├── scripts/             # Shell scripts
└── docs/                # Prezentări HTML
```

### 0.2 Instalare dependențe

```bash
cd s12_starterkit

# Verifică Python
python3 --version

# Instalează dependențele
make setup

# Verifică instalarea
make verify
```

**Output așteptat:**
```
✓ Python 3.x detected
✓ tshark available
✓ All dependencies installed
✓ Environment ready
```

---

## Step 1: Server SMTP educațional

> 💡 **Sfat:** Deschideți toate cele 3 terminale de la început și aranjați-le tile (unul lângă altul). Veți vedea conversația SMTP în timp real — e mult mai clar decât să comutați între ferestre.

### 1.1 Pornire server

Deschideți **Terminal 1**:

```bash
python src/email/smtp_server.py --port 1025 --verbose
```

**Output așteptat:**
```
[INFO] SMTP Server starting on localhost:1025
[INFO] Verbose mode enabled
[INFO] Waiting for connections...
```

### 1.2 Ce face serverul

- Ascultă pe portul 1025 (non-privileged, nu necesită sudo)
- Implementează comenzile SMTP esențiale (EHLO, MAIL FROM, RCPT TO, DATA, QUIT)
- Afișează conversația completă în mod verbose
- Stochează mesajele în memorie (pentru demonstrație)

### 1.3 Opțiuni disponibile

| Opțiune | Descriere | Default |
|---------|-----------|---------|
| `--port` | Port de ascultare | 1025 |
| `--host` | Adresă de bind | localhost |
| `--verbose` | Afișează conversația | False |
| `--maildir` | Director pentru stocare | ./mailbox |

---

## Step 2: Client SMTP

### 2.1 Trimitere email simplu

În **Terminal 2**:

> 🔮 **PREDICȚIE înainte de a rula:**
> - Câte linii de output va afișa clientul? (3? 5? 10?)
> - Ce cod de răspuns SMTP te aștepți să vezi la final?
> - Votați prin ridicare de mână: 220? 250? 354? 221?

```bash
python src/email/smtp_client.py \
    --server localhost \
    --port 1025 \
    --from alice@test.local \
    --to bob@test.local \
    --subject "Test SMTP Laborator" \
    --body "Acesta este un mesaj de test pentru laboratorul de rețele."
```

**Output așteptat:**
```
[INFO] Connecting to localhost:1025
[INFO] EHLO sent, server capabilities: SIZE, 8BITMIME
[INFO] MAIL FROM accepted
[INFO] RCPT TO accepted
[INFO] DATA accepted
[INFO] Message queued successfully (ID: abc123)
[INFO] Connection closed
```

### 2.2 Verificare pe server

În Terminal 1, veți vedea:

```
[CLIENT] Connected from 127.0.0.1:54321
[RECV] EHLO localhost
[SEND] 250-smtp.test.local Hello localhost
[SEND] 250-SIZE 10485760
[SEND] 250 8BITMIME
[RECV] MAIL FROM:<alice@test.local>
[SEND] 250 OK
[RECV] RCPT TO:<bob@test.local>
[SEND] 250 OK
[RECV] DATA
[SEND] 354 Start mail input; end with <CRLF>.<CRLF>
[RECV] From: alice@test.local
[RECV] To: bob@test.local
[RECV] Subject: Test SMTP Laborator
[RECV] 
[RECV] Acesta este un mesaj de test pentru laboratorul de rețele.
[RECV] .
[SEND] 250 OK id=msg_001
[RECV] QUIT
[SEND] 221 Bye
[CLIENT] Disconnected
```

### 2.3 Listare mesaje

```bash
python src/email/smtp_client.py --list
```

---

## Step 3: Captură trafic SMTP

### 3.1 Pornire captură

În **Terminal 3** (înainte de a trimite email):

```bash
sudo tshark -i lo -f "port 1025" -Y smtp -V 2>&1 | head -100
```

Sau salvare în fișier:

```bash
sudo tshark -i lo -f "port 1025" -w smtp_capture.pcap
```

### 3.2 Trimitere email (în alt terminal)

```bash
python src/email/smtp_client.py \
    --server localhost --port 1025 \
    --from sender@demo.local \
    --to receiver@demo.local \
    --subject "Captured Email" \
    --body "This email was captured with tshark"
```

### 3.3 Analiza capturii

Opriți tshark (Ctrl+C) și analizați:

```bash
# Afișează conversația SMTP
tshark -r smtp_capture.pcap -Y smtp -T fields \
    -e frame.number -e smtp.req.command -e smtp.response.code

# Follow TCP stream
tshark -r smtp_capture.pcap -z "follow,tcp,ascii,0"
```

**Ce să observați:**
- Secvența de comenzi (EHLO → MAIL FROM → RCPT TO → DATA → QUIT)
- Codurile de răspuns (220, 250, 354, 221)
- Diferența între envelope (MAIL FROM) și headers (From:)

---

## 👥 LUCRU ÎN PERECHI: Exercițiu SMTP

**Timp:** 15 minute | **Formează perechi** de câte 2 studenți

### Roluri
- **Driver:** Scrie comenzile, rulează codul
- **Navigator:** Verifică output-ul, sugerează corecții, ține timing-ul

### Task
Trimiteți un email cu **MAIL FROM diferit de Header From** (simulare spoofing educațional):
- Envelope: `MAIL FROM:<secret@hidden.local>`
- Header: `From: Public Name <public@visible.local>`

### Pași
1. **[Driver]** Pornește serverul SMTP în Terminal 1 (dacă nu rulează deja)
2. **[Navigator]** Dictează comanda de client cu parametrii modificați:
   ```bash
   python src/email/smtp_client.py \
       --server localhost --port 1025 \
       --from public@visible.local \
       --envelope-from secret@hidden.local \
       --to receiver@test.local \
       --subject "Test Envelope vs Header"
   ```
3. **[Driver]** Rulează comanda
4. **[Navigator]** Verifică în log-ul serverului că envelope ≠ headers
5. **SCHIMB ROLURI** (după 7 minute)
6. **[Noul Driver]** Rulează `python exercises/ex_01_smtp.py analyze --spool ./spool_s12`
7. **[Noul Navigator]** Explică partenerului de ce contează această diferență pentru securitate

### Verificare
- [ ] Emailul a fost trimis cu succes?
- [ ] În log-ul serverului apare `MAIL FROM:<secret@hidden.local>`?
- [ ] Header-ul `From:` din mesaj arată `public@visible.local`?
- [ ] Ați identificat de ce SPF/DKIM/DMARC sunt necesare?

> **Discuție finală în grup:** Ce implicații de securitate are această diferență? Cum vă puteți proteja?

---

## Step 4: Server JSON-RPC

### 4.1 Pornire server

În **Terminal 1**:

> 🔮 **PREDICȚIE:** Serverul va afișa lista de metode disponibile.
> - Câte metode credeți că sunt expuse? (3? 5? 10?)
> - Există o metodă `system.listMethods` ca la XML-RPC?

```bash
python src/rpc/jsonrpc/jsonrpc_server.py --port 8000 --verbose
```

**Output:**
```
[INFO] JSON-RPC 2.0 Server starting on http://localhost:8000
[INFO] Available methods: add, subtract, multiply, divide, echo, system.listMethods
[INFO] Press Ctrl+C to stop
```

### 4.2 Metode disponibile

| Metodă | Parametri | Descriere |
|--------|-----------|-----------|
| `add` | a, b | Returnează a + b |
| `subtract` | a, b | Returnează a - b |
| `multiply` | a, b | Returnează a * b |
| `divide` | a, b | Returnează a / b |
| `echo` | message | Returnează mesajul primit |
| `system.listMethods` | - | Listează metodele disponibile |

---

## Step 5: Client JSON-RPC

### 5.1 Mod demo

> 🔮 **PREDICȚIE:** Ce rezultat va returna `divide(10, 0)`?
> 
> A) `null`  
> B) `Infinity`  
> C) Eroare cu cod -32603  
> D) Crash — serverul se oprește  
>
> Votați prin ridicare de mână, apoi rulăm:

```bash
python src/rpc/jsonrpc/jsonrpc_client.py --demo
```

**Output:**
```
=== JSON-RPC 2.0 Demo ===

1. Single call: add(2, 3)
   Result: 5

2. Single call: subtract(10, 4)
   Result: 6

3. Named params: divide(dividend=20, divisor=4)
   Result: 5.0

4. Batch request: [add(1,2), multiply(3,4), divide(10,2)]
   Results: [3, 12, 5.0]

5. Error handling: divide(10, 0)
   Error: -32603 Division by zero

6. Method not found: unknown_method()
   Error: -32601 Method not found
```

### 5.2 Apeluri individuale

```bash
# Apel simplu
python src/rpc/jsonrpc/jsonrpc_client.py \
    --method add --params 42 23

# Cu parametri numiți
python src/rpc/jsonrpc/jsonrpc_client.py \
    --method divide --kwargs '{"dividend": 100, "divisor": 5}'
```

### 5.3 Batch requests

```bash
python src/rpc/jsonrpc/jsonrpc_client.py --batch \
    "add,1,2" "multiply,3,4" "subtract,10,5"
```

---

## Step 6: Server XML-RPC

### 6.1 Pornire server

În **Terminal 2**:

```bash
python src/rpc/xmlrpc/xmlrpc_server.py --port 8001
```

### 6.2 Test client

```bash
# Mod demo
python src/rpc/xmlrpc/xmlrpc_client.py --demo

# Introspecție
python src/rpc/xmlrpc/xmlrpc_client.py --list-methods
```

**Output introspecție:**
```
Available methods:
- add(a, b): Returns the sum of a and b
- subtract(a, b): Returns the difference a - b
- multiply(a, b): Returns the product of a and b
- divide(a, b): Returns the quotient a / b
- system.listMethods(): Lists all available methods
- system.methodHelp(method): Returns help for a method
```

---

## 👥 LUCRU ÎN PERECHI: JSON-RPC Error Handling

**Timp:** 10 minute | **Aceleași perechi** (roluri inversate față de exercițiul anterior)

### Task
Testați toate tipurile de erori JSON-RPC și documentați codurile returnate.

### Pași
1. **[Driver]** Trimite cerere cu JSON invalid:
   ```bash
   curl -X POST http://localhost:8000 \
       -H "Content-Type: application/json" \
       -d 'not valid json at all'
   ```
2. **[Navigator]** Notează codul de eroare din răspuns

3. **[Driver]** Trimite cerere cu metodă inexistentă:
   ```bash
   curl -X POST http://localhost:8000 \
       -H "Content-Type: application/json" \
       -d '{"jsonrpc":"2.0","method":"metoda_inexistenta","id":1}'
   ```
4. **[Navigator]** Notează codul

5. **SCHIMB ROLURI**

6. **[Noul Driver]** Trimite parametri de tip greșit:
   ```bash
   curl -X POST http://localhost:8000 \
       -H "Content-Type: application/json" \
       -d '{"jsonrpc":"2.0","method":"add","params":["text","alttext"],"id":1}'
   ```
7. **[Noul Navigator]** Completează tabelul de mai jos

### Tabel de completat

| Situație | Cod eroare așteptat | Cod obținut | Mesaj |
|----------|---------------------|-------------|-------|
| JSON invalid | -32700 | ? | ? |
| Metodă inexistentă | -32601 | ? | ? |
| Parametri greșiți | -32602 sau -32603 | ? | ? |
| Împărțire la zero | -32603 | ? | ? |

> **Verificare:** Codurile obținute corespund cu cele din specificația JSON-RPC 2.0?

---

## Step 7: Benchmark RPC

### 7.1 Rulare benchmark

> 🔮 **PREDICȚIE:** Scrieți pe hârtie estimările voastre:
> - Cu cât va fi JSON-RPC mai rapid decât XML-RPC? (10%? 50%? 2x? 5x?)
> - Care va avea payload (dimensiune cerere) mai mare?
> - De ce credeți că va fi așa?
>
> Comparați cu rezultatele după rulare!

```bash
make benchmark-rpc
```

Sau manual:

```bash
python scripts/benchmark_rpc.py --iterations 1000
```

### 7.2 Output tipic

```
=== RPC Benchmark Results ===

Configuration:
  Iterations: 1000
  Method: add(random_int, random_int)

JSON-RPC Results:
  Total time: 0.89s
  Throughput: 1123 calls/sec
  Average latency: 0.89ms
  Average request size: 67 bytes
  Average response size: 45 bytes

XML-RPC Results:
  Total time: 1.34s
  Throughput: 746 calls/sec
  Average latency: 1.34ms
  Average request size: 198 bytes
  Average response size: 156 bytes

Comparison:
  JSON-RPC is 1.51x faster
  JSON-RPC requests are 66% smaller
  JSON-RPC responses are 71% smaller
```

### 7.3 Interpretare rezultate

| Metric | JSON-RPC | XML-RPC | Diferență |
|--------|----------|---------|-----------|
| Throughput | Mai mare | Mai mic | JSON ~50% mai rapid |
| Payload | Mic | Mare | XML ~3x mai mare |
| Parsing | Rapid | Lent | JSON parsing nativ în Python |

---

## Step 8: Captură trafic RPC

### 8.1 Captură JSON-RPC

```bash
# Terminal 3
sudo tshark -i lo -f "port 8000" -Y "http.request or http.response" \
    -T fields -e frame.number -e http.request.method \
    -e http.content_length -e http.response.code
```

### 8.2 Captură XML-RPC

```bash
sudo tshark -i lo -f "port 8001" -Y "http contains methodCall" -V
```

### 8.3 Ce să comparați

1. **Dimensiunea payload**: `http.content_length`
2. **Structura XML vs JSON**: Follow TCP stream pentru fiecare
3. **Overhead HTTP**: Headers sunt identice, diferă doar body-ul

---

## Step 9: Exerciții finale

### Exercițiul 1: Multi-recipient SMTP (★★☆)

Modificați comanda de trimitere pentru 3 destinatari:

```bash
python src/email/smtp_client.py \
    --server localhost --port 1025 \
    --from alice@test.local \
    --to bob@test.local carol@test.local david@test.local \
    --subject "Multi-recipient test" \
    --body "This goes to three people"
```

**Verificați:** Câte comenzi RCPT TO apar în conversație?

### Exercițiul 2: JSON-RPC Error handling (★★☆)

Testați comportamentul la erori:

```bash
# Metodă inexistentă
curl -X POST http://localhost:8000 \
    -H "Content-Type: application/json" \
    -d '{"jsonrpc":"2.0","method":"unknown","id":1}'

# JSON invalid
curl -X POST http://localhost:8000 \
    -H "Content-Type: application/json" \
    -d 'not valid json'

# Parametri greșiți
curl -X POST http://localhost:8000 \
    -H "Content-Type: application/json" \
    -d '{"jsonrpc":"2.0","method":"add","params":["a","b"],"id":1}'
```

**Documentați:** Codurile de eroare primite pentru fiecare caz.

### Exercițiul 3: Batch performance (★★★)

Comparați:
- 100 de apeluri individuale
- 10 batch-uri de câte 10 cereri

```bash
python exercises/ex_02_rpc.py --exercise batch-performance
```

### Exercițiul 4: Challenge - Email cu atașament (★★★★)

Extindeți `smtp_client.py` pentru a trimite un fișier atașat.

Hint: Folosiți `email.mime` din biblioteca standard Python.

---

## 🧩 PARSONS PROBLEM: Ordonează sesiunea SMTP

**Instrucțiuni:** Aranjează liniile în ordinea corectă pentru o sesiune SMTP validă. Poți tăia și lipi pe hârtie sau numerota mental.

### Linii amestecate:

```
C: QUIT
S: 354 Start mail input
C: DATA
S: 250 OK: queued
C: EHLO client.local
S: 220 mail.server.com ESMTP
C: MAIL FROM:<sender@test.com>
S: 250 OK
C: RCPT TO:<receiver@test.com>
S: 250 Hello client.local
C: Subject: Test
C: .
C: Hello World
S: 250 Sender OK
S: 250 Recipient OK
S: 221 Bye
```

<details>
<summary>✅ Soluție corectă (click după rezolvare)</summary>

```smtp
S: 220 mail.server.com ESMTP      # 1. Banner server
C: EHLO client.local              # 2. Client salută
S: 250 Hello client.local         # 3. Server confirmă
C: MAIL FROM:<sender@test.com>    # 4. Specifică expeditor
S: 250 Sender OK                  # 5. Confirmare
C: RCPT TO:<receiver@test.com>    # 6. Specifică destinatar
S: 250 Recipient OK               # 7. Confirmare
C: DATA                           # 8. Începe conținutul
S: 354 Start mail input           # 9. Server așteaptă
C: Subject: Test                  # 10. Headers mesaj
C: Hello World                    # 11. Corp mesaj
C: .                              # 12. Terminator (punct singur pe linie)
S: 250 OK: queued                 # 13. Mesaj acceptat
C: QUIT                           # 14. Închidere
S: 221 Bye                        # 15. Confirmare finală
```

**Greșeli comune:**
- DATA înainte de RCPT TO (trebuie să știi cui trimiți înainte de conținut)
- Punctul (`.`) înainte de conținut (punctul termină, nu începe)
- QUIT înainte de confirmarea mesajului (pierzi emailul!)
</details>

---

## 🧩 PARSONS PROBLEM: Construiește cerere JSON-RPC

**Aranjează fragmentele pentru a forma o cerere JSON-RPC 2.0 validă pentru `add(5, 3)`:**

```
"params": [5, 3]
}
"method": "add",
{
"jsonrpc": "2.0",
"id": 1
```

<details>
<summary>✅ Soluție</summary>

```json
{
    "jsonrpc": "2.0",
    "method": "add",
    "params": [5, 3],
    "id": 1
}
```

**Greșeli comune:**
- Virgulă după ultima proprietate (JSON nu permite trailing comma)
- `"jsonrpc"` scris `"json-rpc"` sau `"JSONRPC"`
- `params` ca obiect `{"a": 5, "b": 3}` în loc de array `[5, 3]` (ambele sunt valide, dar trebuie să știi diferența)
</details>

---

## 🔍 TRACE EXERCISE: Urmărește execuția JSON-RPC

**Instrucțiuni:** Pentru fiecare cerere, scrie răspunsul JSON exact pe care îl va returna serverul.

### Cerere 1:
```json
{"jsonrpc": "2.0", "method": "add", "params": [10, 5], "id": 1}
```
**Răspuns:** `____________________________________`

### Cerere 2:
```json
{"jsonrpc": "2.0", "method": "divide", "params": [10, 0], "id": 2}
```
**Răspuns:** `____________________________________`

### Cerere 3 (Notification — fără id!):
```json
{"jsonrpc": "2.0", "method": "echo", "params": ["test"]}
```
**Răspuns:** `____________________________________`

### Cerere 4 (Batch):
```json
[
    {"jsonrpc": "2.0", "method": "add", "params": [1, 2], "id": 1},
    {"jsonrpc": "2.0", "method": "multiply", "params": [3, 4], "id": 2}
]
```
**Răspuns:** `____________________________________`

<details>
<summary>✅ Răspunsuri</summary>

1. `{"jsonrpc": "2.0", "result": 15, "id": 1}`

2. `{"jsonrpc": "2.0", "error": {"code": -32603, "message": "Division by zero"}, "id": 2}`

3. **Nimic** (notifications nu primesc răspuns — serverul execută metoda dar nu trimite nimic înapoi)

4. `[{"jsonrpc": "2.0", "result": 3, "id": 1}, {"jsonrpc": "2.0", "result": 12, "id": 2}]`
   
   (Ordinea în array poate varia, dar id-urile trebuie să corespundă)
</details>

---

## Checklist final

- [ ] Server SMTP pornit și testat
- [ ] Email trimis și verificat în log
- [ ] Captură tshark realizată pentru SMTP
- [ ] Server JSON-RPC funcțional
- [ ] Client JSON-RPC testat (single, batch, errors)
- [ ] Server XML-RPC pornit
- [ ] Benchmark rulat și interpretat
- [ ] Exercițiul 1 completat
- [ ] Exercițiul 2 completat

---

## Troubleshooting

### Erori comune

| Eroare | Cauză | Soluție |
|--------|-------|---------|
| `Connection refused` | Server nu rulează | Verificați că serverul e pornit pe portul corect |
| `Permission denied` (tshark) | Lipsa privilegii | Folosiți `sudo` sau configurați capabilities |
| `Port already in use` | Alt proces pe port | Schimbați portul sau opriți procesul existent |
| `Module not found` | Dependențe lipsă | Rulați `make setup` |

### Comenzi utile

```bash
# Verifică ce ascultă pe un port
lsof -i :8000

# Oprește procesul pe port
kill $(lsof -t -i:8000)

# Verifică conectivitate
nc -zv localhost 1025
```

---

*Material didactic — Rețele de Calculatoare, ASE-CSIE*
