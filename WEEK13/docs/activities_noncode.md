# Activități Non-Cod — Săptămâna 13
## Parsons Problems | Code Tracing | Debugging | Code Reading

> **Scop:** Diversificarea tipurilor de învățare conform Principiului 10 Brown & Wilson  
> **Timp total:** ~45 minute (selectează 3-4 activități per sesiune)

---

# 1. PARSONS PROBLEMS (Reordonare Cod)

## Parsons #1: TCP Scanner Basic

**Context:** Funcție care scanează un singur port TCP.

**Instrucțiuni:** Reordonează liniile pentru a obține cod funcțional.

```
LINII AMESTECATE:

E) return port, "OPEN" if result == 0 else "CLOSED"
B) sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
D) result = sock.connect_ex((target, port))
A) def scan_port(target, port, timeout=1.0):
F) sock.close()
C) sock.settimeout(timeout)
```

**Scrie ordinea corectă:** `__ → __ → __ → __ → __ → __`

<details>
<summary>🔑 Vezi soluția</summary>

**Ordine corectă:** `A → B → C → D → F → E`

```python
def scan_port(target, port, timeout=1.0):           # A - definiție
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # B - creare socket
    sock.settimeout(timeout)                         # C - timeout ÎNAINTE de connect
    result = sock.connect_ex((target, port))        # D - încercare conexiune
    sock.close()                                     # F - închidere socket
    return port, "OPEN" if result == 0 else "CLOSED"  # E - return rezultat
```

**De ce această ordine:**
- Timeout trebuie setat ÎNAINTE de connect_ex()
- close() trebuie apelat ÎNAINTE de return
</details>

---

## Parsons #2: MQTT Publisher Simplu

**Context:** Cod care publică un mesaj pe un topic MQTT.

```
LINII AMESTECATE:

D) client.publish(topic, payload)
A) import paho.mqtt.client as mqtt
E) client.disconnect()
C) client.connect(broker, 1883)
B) client = mqtt.Client()
```

**Scrie ordinea corectă:** `__ → __ → __ → __ → __`

<details>
<summary>🔑 Vezi soluția</summary>

**Ordine corectă:** `A → B → C → D → E`

```python
import paho.mqtt.client as mqtt      # A - import
client = mqtt.Client()               # B - creare client
client.connect(broker, 1883)         # C - conectare
client.publish(topic, payload)       # D - publicare
client.disconnect()                  # E - deconectare
```
</details>

---

## Parsons #3: Subscriber cu Callback (Mai Dificil)

**Context:** Subscriber MQTT care afișează mesajele primite.

```
LINII AMESTECATE:

F) client.loop_forever()
C) client.on_message = on_message
A) def on_message(client, userdata, msg):
B)     print(f"Topic: {msg.topic}, Payload: {msg.payload}")
E) client.subscribe("sensors/#")
D) client.connect("localhost", 1883)
G) client = mqtt.Client()
```

**Scrie ordinea corectă:** `__ → __ → __ → __ → __ → __ → __`

<details>
<summary>🔑 Vezi soluția</summary>

**Ordine corectă:** `A → B → G → C → D → E → F`

```python
def on_message(client, userdata, msg):           # A - definim callback
    print(f"Topic: {msg.topic}, Payload: {msg.payload}")  # B - body callback

client = mqtt.Client()                           # G - creare client
client.on_message = on_message                   # C - atașare callback ÎNAINTE de connect!
client.connect("localhost", 1883)                # D - conectare
client.subscribe("sensors/#")                    # E - abonare
client.loop_forever()                            # F - loop pentru a primi mesaje
```

**Greșeală frecventă:** Callback-ul trebuie definit și atașat ÎNAINTE de connect/subscribe.
</details>

---

# 2. CODE TRACING (Urmărire Execuție)

## Tracing #1: Clasificare Porturi

```python
results = []
for port in [22, 80, 443, 8080]:
    if port < 100:
        results.append(f"{port}: privileged")
    elif port < 1024:
        results.append(f"{port}: well-known")
    else:
        results.append(f"{port}: registered")

for r in results:
    print(r)
```

**Întrebare:** Scrie exact ce va afișa programul (4 linii).

```
Linia 1: ____________________
Linia 2: ____________________
Linia 3: ____________________
Linia 4: ____________________
```

<details>
<summary>🔑 Vezi soluția</summary>

```
22: privileged
80: privileged
443: well-known
8080: registered
```

**Explicație:**
- 22 < 100 → privileged
- 80 < 100 → privileged
- 443: 100 ≤ 443 < 1024 → well-known
- 8080: ≥ 1024 → registered
</details>

---

## Tracing #2: MQTT Wildcard Matching

**Setup:**
```bash
# Terminal 1 (pornit primul):
mosquitto_sub -h broker -t "home/+/temp" -v

# Terminal 2 (după 5 secunde):
mosquitto_pub -h broker -t "home/kitchen/temp" -m "22.5"
mosquitto_pub -h broker -t "home/bedroom/humidity" -m "45"
mosquitto_pub -h broker -t "office/meeting/temp" -m "19"
mosquitto_pub -h broker -t "home/living/temp" -m "21"
```

**Întrebare:** Ce mesaje va primi și afișa Terminal 1?

```
Mesaj 1: ____________________
Mesaj 2: ____________________
(sau "nimic" dacă nu primește)
```

<details>
<summary>🔑 Vezi soluția</summary>

Terminal 1 primește:
```
home/kitchen/temp 22.5
home/living/temp 21
```

**Explicație wildcard `+`:**
- `home/+/temp` = "home" / (orice UN nivel) / "temp"
- ✅ `home/kitchen/temp` — matchează
- ❌ `home/bedroom/humidity` — humidity ≠ temp
- ❌ `office/meeting/temp` — office ≠ home
- ✅ `home/living/temp` — matchează
</details>

---

## Tracing #3: Scan Results Counter

```python
def analyze_scan(results):
    stats = {"open": 0, "closed": 0, "filtered": 0}
    
    for port, state in results:
        if state in stats:
            stats[state] += 1
    
    return stats

scan_results = [
    (22, "open"), (23, "filtered"), (25, "closed"),
    (80, "open"), (443, "open"), (8080, "closed")
]

output = analyze_scan(scan_results)
print(output)
```

**Întrebare:** Ce va afișa `print(output)`?

```
Output: ____________________
```

<details>
<summary>🔑 Vezi soluția</summary>

```
{'open': 3, 'closed': 2, 'filtered': 1}
```

**Numărătoare:**
- open: 22, 80, 443 → 3
- closed: 25, 8080 → 2
- filtered: 23 → 1
</details>

---

# 3. DEBUGGING EXERCISES (Găsește Eroarea)

## Debug #1: Scanner fără Timeout

```python
import socket

def scan_port(target, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex((target, port))
    if result == 0:
        return "OPEN"
    else:
        return "CLOSED"

print(scan_port("192.168.1.1", 22))
```

**Probleme (găsește 3):**

1. ________________________________
2. ________________________________
3. ________________________________

<details>
<summary>🔑 Vezi soluția</summary>

**Problema 1:** Lipsește `sock.settimeout()`
- Impact: Blocaj indefinit pe porturi FILTERED
- Fix: `sock.settimeout(1.0)` după creare socket

**Problema 2:** Lipsește `sock.close()`
- Impact: File descriptor leak → "Too many open files" după multe scanări
- Fix: `sock.close()` înainte de return

**Problema 3:** Nu tratează excepția `socket.timeout`
- Impact: Crash în loc de "FILTERED"
- Fix: try/except cu return "FILTERED" pe timeout

**Cod corectat:**
```python
def scan_port(target, port, timeout=1.0):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)  # FIX 1
    try:
        result = sock.connect_ex((target, port))
        sock.close()  # FIX 2
        return "OPEN" if result == 0 else "CLOSED"
    except socket.timeout:  # FIX 3
        return "FILTERED"
```
</details>

---

## Debug #2: MQTT Subscriber Silențios

```python
import paho.mqtt.client as mqtt

client = mqtt.Client()
client.connect("localhost", 1883)
client.subscribe("sensors/#")

def on_message(client, userdata, msg):
    print(f"Received: {msg.payload}")

client.on_message = on_message

while True:
    pass
```

**Simptom:** Subscriber-ul se conectează dar NU primește niciun mesaj.

**Problema:** ________________________________

**Fix:** ________________________________

<details>
<summary>🔑 Vezi soluția</summary>

**Problema:** Lipsește `client.loop_start()` sau `client.loop_forever()`

Fără network loop, callback-urile NU sunt procesate!

**Fix corect:**
```python
import paho.mqtt.client as mqtt

def on_message(client, userdata, msg):  # Definește ÎNAINTE
    print(f"Received: {msg.payload}")

client = mqtt.Client()
client.on_message = on_message  # Atașează ÎNAINTE de connect
client.connect("localhost", 1883)
client.subscribe("sensors/#")
client.loop_forever()  # SAU loop_start() pentru non-blocking
```

**Greșeli secundare în codul original:**
- `on_message` definit DUPĂ subscribe (minor, dar bad practice)
- `while True: pass` consumă CPU inutil
</details>

---

## Debug #3: Banner Grabbing Eșuat

```python
def grab_banner(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    banner = sock.recv(1024)
    return banner.decode()
```

**Simptom:** Funcția blochează la `recv()` și nu returnează nimic.

**De ce?** ________________________________

**Fix:** ________________________________

<details>
<summary>🔑 Vezi soluția</summary>

**De ce blochează:**
Unele servicii (ex: SMTP, FTP) trimit banner automat, dar altele (ex: HTTP) așteaptă cerere de la client.

**Fix-uri:**
```python
def grab_banner(host, port, timeout=3.0):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)  # FIX 1: Timeout
    try:
        sock.connect((host, port))
        sock.send(b"\r\n")  # FIX 2: Stimulează răspuns
        banner = sock.recv(1024)
        return banner.decode(errors='replace')  # FIX 3: Handle encoding
    except (socket.timeout, ConnectionRefusedError):
        return None
    finally:
        sock.close()  # FIX 4: Cleanup
```
</details>

---

# 4. CODE READING (Explicare Cod)

## Reading #1: Parser Header MQTT

```python
def parse_mqtt_header(data: bytes) -> dict:
    if len(data) < 2:
        return {"error": "too short"}
    
    msg_type = (data[0] & 0xF0) >> 4
    flags = data[0] & 0x0F
    remaining = data[1]
    
    return {
        "type": msg_type,
        "flags": flags,
        "remaining_length": remaining
    }
```

**Întrebări:**

1. Ce protocol parsează această funcție?
   
   Răspuns: ____________________

2. Ce face operația `& 0xF0` urmată de `>> 4`?
   
   Răspuns: ____________________

3. Ce reprezintă valorile posibile pentru `msg_type`?
   
   Răspuns: ____________________

<details>
<summary>🔑 Vezi soluția</summary>

1. **MQTT** — structura header-ului fix MQTT

2. **Extrage cei 4 biți superiori (high nibble):**
   - `& 0xF0` = mască care păstrează biții 7-4, pune 0 pe 3-0
   - `>> 4` = shift right cu 4 poziții → valoare 0-15
   - Echivalent: `data[0] // 16`

3. **Tipuri mesaje MQTT:**
   - 1 = CONNECT
   - 2 = CONNACK
   - 3 = PUBLISH
   - 4 = PUBACK
   - 8 = SUBSCRIBE
   - 9 = SUBACK
   - 12 = PINGREQ
   - 14 = DISCONNECT
</details>

---

## Reading #2: Port Range Generator

```python
def parse_ports(spec: str) -> list:
    ports = []
    for part in spec.split(','):
        if '-' in part:
            start, end = map(int, part.split('-'))
            ports.extend(range(start, end + 1))
        else:
            ports.append(int(part))
    return sorted(set(ports))
```

**Întrebări:**

1. Ce returnează `parse_ports("22,80,100-103")`?
   
   Răspuns: ____________________

2. De ce folosește `sorted(set(ports))`?
   
   Răspuns: ____________________

3. Ce s-ar întâmpla dacă input-ul e `"80,22,80,22"`?
   
   Răspuns: ____________________

<details>
<summary>🔑 Vezi soluția</summary>

1. `[22, 80, 100, 101, 102, 103]`

2. **`set()`** elimină duplicatele, **`sorted()`** ordonează crescător
   - Util când user-ul specifică același port de mai multe ori

3. Returnează `[22, 80]` — duplicatele sunt eliminate de `set()`
</details>

---

# 5. DIAGRAM COMPLETION

## Completează: TCP Three-Way Handshake

```
Client                           Server
   │                                │
   │  _________ (1) _________►     │
   │        [seq = x]               │
   │                                │
   │ ◄_________ (2) _________      │
   │   [seq = y, ack = ___]         │
   │                                │
   │  _________ (3) _________►     │
   │        [ack = ___]             │
   │                                │
   │       [ ESTABLISHED ]          │
```

**Completează:**
- (1) Tipul pachetului: ___________
- (2) Tipul pachetului: ___________
- (2) ack = ___________
- (3) Tipul pachetului: ___________
- (3) ack = ___________

<details>
<summary>🔑 Vezi soluția</summary>

- (1) **SYN**
- (2) **SYN-ACK**
- (2) ack = **x + 1**
- (3) **ACK**
- (3) ack = **y + 1**

```
Client                           Server
   │                                │
   │  ───────── SYN ──────────►    │
   │        [seq = x]               │
   │                                │
   │ ◄──────── SYN-ACK ──────      │
   │   [seq = y, ack = x+1]         │
   │                                │
   │  ───────── ACK ──────────►    │
   │        [ack = y+1]             │
   │                                │
   │       [ ESTABLISHED ]          │
```
</details>

---

## Completează: MQTT QoS 1 Flow

```
Publisher                Broker               Subscriber
    │                       │                       │
    │  PUBLISH ──────────►  │                       │
    │  [QoS=1, msgId=42]    │                       │
    │                       │                       │
    │                       │  PUBLISH ──────────►  │
    │                       │  [QoS=1, msgId=42]    │
    │                       │                       │
    │                       │ ◄──── _______ ─────   │
    │                       │      [msgId=42]       │
    │                       │                       │
    │ ◄──── _______ ─────   │                       │
    │      [msgId=42]       │                       │
```

**Completează cele 2 răspunsuri (______):**

<details>
<summary>🔑 Vezi soluția</summary>

Ambele sunt **PUBACK** (Publish Acknowledgment)

```
Publisher                Broker               Subscriber
    │                       │                       │
    │  PUBLISH ──────────►  │                       │
    │  [QoS=1, msgId=42]    │                       │
    │                       │                       │
    │                       │  PUBLISH ──────────►  │
    │                       │  [QoS=1, msgId=42]    │
    │                       │                       │
    │                       │ ◄──── PUBACK ─────    │
    │                       │      [msgId=42]       │
    │                       │                       │
    │ ◄──── PUBACK ─────    │                       │
    │      [msgId=42]       │                       │
```

**La QoS 1:** "At least once" = confirmare cu PUBACK de la fiecare receptor
</details>

---

# Ghid de Utilizare

## Selectare Activități per Sesiune

| Timp disponibil | Activități recomandate |
|-----------------|------------------------|
| 15 min | 1 Parsons + 1 Tracing |
| 30 min | 2 Parsons + 1 Debug + 1 Reading |
| 45 min | Toate categoriile (1-2 din fiecare) |

## Integrare în Seminar

- **Parsons:** După live coding, ca verificare înțelegere
- **Tracing:** Înainte de execuție cod, ca predicție
- **Debug:** După ce studenții întâmpină erori reale
- **Reading:** Pentru cod mai complex, înainte de modificare

---

*Material didactic — Rețele de Calculatoare S13*  
*Conform Principiului 10 Brown & Wilson: "Nu doar cod de la zero"*
