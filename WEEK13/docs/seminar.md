# Seminar 13 — Securitate în Rețele: Scanare și Testare

## Obiective Operaționale

La finalul acestui seminar, studenții vor fi capabili să:
1. Configureze un mediu de testare izolat (Docker + Mininet)
2. Implementeze un scanner de porturi TCP pas cu pas
3. Identifice servicii prin banner grabbing
4. Analizeze trafic MQTT cu tshark
5. Demonstreze un exploit controlat (CVE-2011-2523)

**Timp total:** 100 minute (planificat pentru 90 efective)

---

## Faza 1: Setup Mediu (15 min)

### [3 min] Verificare prerechizite

```bash
python3 --version  # >= 3.8
docker --version   # >= 20.10
which tshark       # trebuie instalat
```

> 🔮 **PREDICȚIE:** Ce versiuni aveți instalate? Cineva are versiune mai veche?

### [7 min] Pornire mediu

```bash
cd starterkit_s13
make setup       # Instalează dependențe
make docker-up   # Pornește containerele
```

Din experiența de laborator, `make setup` poate dura 2-3 minute prima dată (descarcă imagini Docker).

### [5 min] Verificare funcționalitate

```bash
make verify
```

> 🔮 **PREDICȚIE:** Câte verificări vor trece? Care ar putea eșua?

**Expected output:**
```
[✓] Docker running
[✓] Mosquitto container up
[✓] Port 1883 open
[✓] Python dependencies OK
```

**Dacă ceva eșuează:** Vezi secțiunea Troubleshooting din `docs/lab.md`

---

## Faza 2: Scanare Porturi (30 min)

### [5 min] Pregătire conceptuală

#### Analogie: Porturile ca Uși 🚪

Imaginează-ți un coridor cu uși numerotate:
- **OPEN** = Ușă deschisă, cineva te întâmpină ("Bună, cu ce te ajut?")
- **CLOSED** = Ușă închisă dar neblocată, bați și primești "Nu-s acasă!" (RST)
- **FILTERED** = Bodyguard care te ignoră complet (DROP silențios)

```
┌────────┐  ┌────────┐  ┌────────┐
│  OPEN  │  │ CLOSED │  │FILTERED│
│   🚪   │  │   🚪   │  │   🚪   │
│  👋    │  │   ✗    │  │   🔇   │
│(SYN-ACK│  │ (RST)  │  │(nimic) │
└────────┘  └────────┘  └────────┘
```

### [12 min] Live Coding — Scanner TCP

**Lucru în perechi:** Un student e Driver (scrie), celălalt Navigator (revizuiește).

#### Pas 1: Schelet funcție [2 min]

```python
import socket

def scan_port(target, port, timeout=1.0):
    """Scanează un singur port TCP."""
    pass  # Completăm împreună
```

> 💡 **ÎNTREBARE pentru Navigator:** Ce parametri are funcția? De ce avem timeout?

#### Pas 2: Creare socket [3 min]

```python
def scan_port(target, port, timeout=1.0):
    # Cream socket TCP (SOCK_STREAM = TCP, SOCK_DGRAM = UDP)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    # Continuăm...
```

**Schimb roluri!** Navigator devine Driver.

#### Pas 3: Conectare și interpretare [4 min]

```python
def scan_port(target, port, timeout=1.0):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        # connect_ex returnează cod eroare (0 = succes)
        # connect() ar arunca excepție
        result = sock.connect_ex((target, port))
        sock.close()
        return port, "OPEN" if result == 0 else "CLOSED"
    except socket.timeout:
        return port, "FILTERED"
```

> 🔮 **PREDICȚIE:** De ce `connect_ex()` și nu `connect()`?

#### Pas 4: Test rapid [3 min]

```bash
python3 -c "
import socket
def scan_port(target, port, timeout=1.0):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        result = sock.connect_ex((target, port))
        sock.close()
        return port, 'OPEN' if result == 0 else 'CLOSED'
    except socket.timeout:
        return port, 'FILTERED'

print(scan_port('localhost', 22))
print(scan_port('localhost', 1883))
print(scan_port('localhost', 9999))
"
```

> 🔮 **PREDICȚIE înainte de Enter:**
> - Port 22 (SSH): _______
> - Port 1883 (MQTT): _______  
> - Port 9999 (nimic): _______

### [6 min] 🗳️ Peer Instruction: Port States

**Vezi `docs/peer_instruction.md` → PI-2**

Secvența:
1. Afișează întrebarea (1 min)
2. Vot individual (1 min)
3. Discuție în perechi (2 min)
4. Revot (30 sec)
5. Explicație (1.5 min)

### [7 min] Exercițiu practic: Scanare completă

```bash
python3 python/exercises/ex_01_port_scanner.py \
    --target localhost \
    --ports 1-1024 \
    --timeout 0.5
```

> 🔮 **Estimează înainte:** 
> - Câte porturi OPEN vei găsi?
> - Cât va dura scanarea 1024 porturi?

**Eroare frecventă:** Timeout prea mic (0.1s) → totul pare FILTERED

---

## Faza 3: Demo MQTT (25 min)

### [5 min] Pregătire conceptuală

#### Analogie: MQTT ca Tabloid de Anunțuri 📋

Imaginează-ți un tabloid de anunțuri într-un cămin:
- **Broker** = Tabloidul (locul central)
- **Topic** = Secțiunea (Vânzări, Evenimente, etc.)
- **Publisher** = Cel care lipește anunțul
- **Subscriber** = Cel care verifică secțiunea

```
     Publisher                              Subscriber
    (Senzor)                               (Controller)
        │                                       │
        │ CONNECT                               │ CONNECT
        ├────────────────►┌──────┐◄─────────────┤
        │                 │      │              │
        │ PUBLISH         │Broker│   SUBSCRIBE  │
        │ topic: iot/temp │      │   topic: #   │
        ├────────────────►│      │◄─────────────┤
        │                 │      │              │
        │                 │      │   PUBLISH    │
        │                 │      ├─────────────►│
        │                 └──────┘              │
```

### [10 min] Demo pub/sub

**Lucru în perechi:** Un student = Publisher, celălalt = Subscriber

#### Terminal 1: Subscriber (Controller)

```bash
mosquitto_sub -h localhost -t "iot/#" -v
```

> 🔮 **PREDICȚIE:** Ce înseamnă `#` în topic? Ce mesaje va primi?

#### Terminal 2: Publisher (Senzor)

```bash
mosquitto_pub -h localhost -t "iot/temp" -m '{"value": 23.5, "unit": "C"}'
mosquitto_pub -h localhost -t "iot/humidity" -m '{"value": 65, "unit": "%"}'
mosquitto_pub -h localhost -t "office/light" -m '{"state": "on"}'
```

> 🔮 **PREDICȚIE:** Care din cele 3 mesaje va primi Subscriber-ul? De ce?

**Schimb roluri și repetă cu topic diferit!**

### [5 min] 🗳️ Peer Instruction: QoS

**Vezi `docs/peer_instruction.md` → PI-1**

### [5 min] Exercițiu: QoS comparison

```bash
# Terminal 1: Subscriber cu QoS 1
mosquitto_sub -h localhost -t "test/qos" -q 1 -v

# Terminal 2: Publish cu QoS 0 vs QoS 1
mosquitto_pub -h localhost -t "test/qos" -q 0 -m "QoS 0 message"
mosquitto_pub -h localhost -t "test/qos" -q 1 -m "QoS 1 message"
```

> 🔮 **Observă:** Ce diferență vezi în comportament?

---

## Faza 4: Captură Trafic (20 min)

### [3 min] 🗳️ Peer Instruction: Securitate MQTT

**Vezi `docs/peer_instruction.md` → PI-3**

### [7 min] Demo: MQTT în clar (plaintext)

```bash
# Terminal 1: Captură
sudo tshark -i any -f "port 1883" -Y mqtt

# Terminal 2: Generează trafic
mosquitto_pub -h localhost -t "iot/secret" -m "parola123"
```

> ⚠️ **Observă:** Mesajul "parola123" e vizibil în captură! De aceea TLS e important.

### [10 min] Filtre tshark utile

```bash
# Doar PUBLISH
sudo tshark -i any -f "port 1883" -Y "mqtt.msgtype == 3"

# Topic specific
sudo tshark -i any -f "port 1883" -Y 'mqtt.topic contains "sensor"'

# Salvare în fișier
sudo tshark -i any -f "port 1883" -w capture.pcap -a duration:30
```

> 🔮 **PREDICȚIE:** Pentru UN mesaj MQTT publicat, câte pachete vei vedea în captură?
> Hint: CONNECT, CONNACK, PUBLISH, (PUBACK pentru QoS≥1), DISCONNECT...

---

## Faza 5: Recap și Exerciții (10 min)

### Verificare înțelegere rapidă

1. Ce returnează scannerul pentru un port cu firewall DROP? ___________
2. Ce QoS folosești pentru alerte critice? ___________
3. De ce vedem payload-ul MQTT în Wireshark? ___________

### Exerciții pentru acasă

Vezi fișierul `docs/activities_noncode.md` pentru:
- Parsons Problems (reordonare cod)
- Code Tracing (predicție output)
- Debugging Exercises (găsește eroarea)

### Activitate opțională: Exploit vsftpd

Pentru cei care termină mai devreme:

```bash
# Doar în mediul de laborator controlat!
python3 python/exploits/ftp_backdoor_vsftpd.py --target localhost --ftp-port 2121
```

---

## Lucru în Perechi — Reguli

| Rol | Responsabilități |
|-----|------------------|
| **Driver** | Scrie codul, controlează tastatura |
| **Navigator** | Revizuiește, sugerează, verifică documentația |

**Reguli:**
1. Schimbați rolurile la fiecare **10 minute**
2. Navigator-ul NU atinge tastatura
3. Driver-ul verbalizează ce face
4. Ambii sunt responsabili de rezultat

---

## Troubleshooting Rapid

| Simptom | Cauză probabilă | Fix |
|---------|-----------------|-----|
| "Connection refused" MQTT | Container oprit | `make docker-up` |
| Toate porturile FILTERED | Timeout prea mic | Mărește la 2.0s |
| "Permission denied" tshark | Lipsă capabilities | `sudo tshark ...` |
| Module Python lipsă | pip incomplete | `pip3 install -r requirements.txt --break-system-packages` |

---

## Materiale Suplimentare

- `docs/peer_instruction.md` — Întrebări PI complete cu note instructor
- `docs/activities_noncode.md` — Parsons, Tracing, Debugging
- `docs/cheatsheet.md` — Comenzi rapide
- `docs/lab.md` — Ghid pas cu pas detaliat

---

*Seminar 13 — IoT și Securitate*  
*ASE-CSIE | Rețele de Calculatoare | 2025-2026*
