# Scenariul S1.03: Captură și Analiză cu tshark/Wireshark

## Obiective

După parcurgerea acestui scenariu, studentul va putea:

1. Captura trafic de rețea cu tshark
2. Aplica filtre de captură (BPF) și display filters
3. Identifica TCP handshake în capturi
4. Exporta date pentru analiză ulterioară

## Context

tshark este versiunea CLI a Wireshark - perfectă pentru automatizare, servere fără GUI, și scripturi. Aceleași capabilități, aceeași sintaxă de filtre.

**Analogie:** tshark e ca un detectiv care poate înregistra și analiza fiecare "conversație" din rețea. Poate asculta tot sau poate filtra doar anumite tipuri de trafic.

---

## Pași de Urmat

### Pasul 1: Captură de Bază (10 minute)

**🎯 PREDICȚIE:** Câte pachete crezi că vei vedea pentru comanda `ping -c 3 localhost`?

**Captură simplă:**
```bash
# Captură pe loopback (lo), toate pachetele
sudo tshark -i lo

# Captură cu filtru de port
sudo tshark -i lo -f "port 9999"

# Captură limitată la N pachete
sudo tshark -i lo -c 10
```

**Opțiuni importante:**
- `-i INTERFACE` - interfața de captură (lo, eth0, any)
- `-f "FILTER"` - filtru de captură BPF (la nivel kernel)
- `-c N` - oprește după N pachete
- `-a duration:SEC` - oprește după SEC secunde

### Pasul 2: Salvare și Citire PCAP (5 minute)

**Salvare:**
```bash
# Salvează captura în fișier PCAP
sudo tshark -i lo -f "port 9999" -w captura.pcap

# Cu limită de timp
sudo tshark -i lo -f "port 9999" -a duration:30 -w captura.pcap
```

**Citire:**
```bash
# Afișează conținutul
tshark -r captura.pcap

# Cu display filter (nu necesită sudo!)
tshark -r captura.pcap -Y "tcp.flags.syn==1"
```

### Pasul 3: Experiment Complet - TCP Handshake (15 minute)

**👥 PAIR PROGRAMMING:** Lucrați în perechi, fiecare cu propriul terminal.

**🎯 PREDICȚIE:** În ce ordine vor apărea flag-urile TCP?

**Setup (3 terminale):**

**Terminal 1 (Driver) - Captură:**
```bash
sudo tshark -i lo -f "port 9999" -w handshake.pcap
# Lasă să ruleze!
```

**Terminal 2 (Navigator) - Server:**
```bash
nc -l -p 9999
```

**Terminal 3 - Client:**
```bash
echo "Test message" | nc localhost 9999
```

**Oprire și analiză:**
```bash
# Terminal 1: Ctrl+C pentru oprire captură

# Analiză
tshark -r handshake.pcap
```

**Output așteptat:**
```
1 0.000000 127.0.0.1→127.0.0.1 TCP 52345→9999 [SYN] Seq=0
2 0.000012 127.0.0.1→127.0.0.1 TCP 9999→52345 [SYN,ACK] Seq=0 Ack=1
3 0.000019 127.0.0.1→127.0.0.1 TCP 52345→9999 [ACK] Seq=1 Ack=1
4 0.000087 127.0.0.1→127.0.0.1 TCP 52345→9999 [PSH,ACK] Len=13
...
```

---

## 🗳️ PEER INSTRUCTION: Interpretare Captură

**Output tshark:**
```
1 0.000000 127.0.0.1→127.0.0.1 TCP 52000→9999 [SYN] Seq=0
2 0.000010 127.0.0.1→127.0.0.1 TCP 9999→52000 [RST,ACK] Seq=0 Ack=1
```

**Întrebare:** Ce indică această captură?

| Opțiune | Răspuns |
|---------|---------|
| **A** | Conexiune TCP stabilită cu succes |
| **B** | Serverul nu ascultă pe portul 9999 |
| **C** | Firewall a blocat conexiunea |
| **D** | Timeout la client |

<details>
<summary>🎯 Răspuns</summary>

**Corect: B** - RST (Reset) imediat după SYN indică că NICIUN proces nu ascultă pe portul destinație.

- Dacă ar fi firewall DROP, nu am vedea RST deloc (nu am vedea pachetul 2)
- Dacă ar fi timeout, am vedea retransmisii SYN, nu RST
- Conexiunea NU s-a stabilit - RST e opusul!
</details>

---

### Pasul 4: Display Filters (10 minute)

Display filters se aplică pe capturi existente (diferit de capture filters):

```bash
# Doar pachete SYN (inițiere conexiune)
tshark -r handshake.pcap -Y "tcp.flags.syn==1 and tcp.flags.ack==0"

# Doar SYN sau SYN-ACK (toate pachetele de handshake)
tshark -r handshake.pcap -Y "tcp.flags.syn==1"

# Pachete cu date (len > 0)
tshark -r handshake.pcap -Y "tcp.len > 0"

# Combinații
tshark -r handshake.pcap -Y "tcp.port==9999 and tcp.flags.push==1"
```

**Filtre utile:**

| Filtru | Scop |
|--------|------|
| `tcp.flags.syn==1` | Pachete SYN |
| `tcp.flags.fin==1` | Pachete FIN (închidere) |
| `tcp.flags.rst==1` | Pachete RST (reset forțat) |
| `tcp.port==9999` | Trafic pe portul 9999 |
| `ip.src==10.0.1.11` | Sursă specifică |
| `tcp.len > 0` | Pachete cu date |
| `http` | Trafic HTTP |
| `dns` | Trafic DNS |

### Pasul 5: Extragere Câmpuri (5 minute)

**Format tabelar:**
```bash
tshark -r handshake.pcap -T fields \
  -e frame.number \
  -e frame.time_relative \
  -e ip.src \
  -e tcp.srcport \
  -e tcp.dstport \
  -e tcp.flags.str \
  -e tcp.len
```

**Export CSV:**
```bash
tshark -r handshake.pcap -T fields \
  -E header=y \
  -E separator=, \
  -e frame.number \
  -e frame.time_relative \
  -e tcp.srcport \
  -e tcp.dstport \
  -e tcp.flags.str \
  > analiza.csv
```

---

## 📝 PARSONS PROBLEM: Script de Analiză Automată

**Sarcină:** Ordonează comenzile pentru a crea un script care capturează trafic TCP, îl analizează și generează un raport.

**Comenzi amestecate:**
```
E) tshark -r $PCAP -Y "tcp.flags.syn==1" | wc -l
F) echo "Conexiuni TCP noi: $CONNECTIONS"
B) PCAP="traffic_$(date +%H%M%S).pcap"
D) CONNECTIONS=$(tshark -r $PCAP -Y "tcp.flags.syn==1 and tcp.flags.ack==0" | wc -l)
C) sudo tshark -i lo -a duration:10 -w $PCAP
A) #!/bin/bash
```

<details>
<summary>✅ Soluție</summary>

**Ordinea corectă:** A → B → C → D → F

```bash
#!/bin/bash                                          # A
PCAP="traffic_$(date +%H%M%S).pcap"                  # B
sudo tshark -i lo -a duration:10 -w $PCAP            # C
CONNECTIONS=$(tshark -r $PCAP -Y "tcp.flags.syn==1 and tcp.flags.ack==0" | wc -l)  # D
echo "Conexiuni TCP noi: $CONNECTIONS"               # F
```

**Notă:** Linia E nu e necesară - e redundantă cu D (care e mai precisă pentru SYN pur).
</details>

---

## 🔍 TRACING EXERCISE: Identificare Handshake

**Captură dată:**
```
1  0.000000 10.0.1.11→10.0.1.12 TCP 45000→80 [SYN] Seq=1000
2  0.001234 10.0.1.12→10.0.1.11 TCP 80→45000 [SYN,ACK] Seq=2000 Ack=1001
3  0.001456 10.0.1.11→10.0.1.12 TCP 45000→80 [ACK] Seq=1001 Ack=2001
4  0.002000 10.0.1.11→10.0.1.12 TCP 45000→80 [PSH,ACK] Seq=1001 Ack=2001 Len=100
5  0.003000 10.0.1.12→10.0.1.11 TCP 80→45000 [ACK] Seq=2001 Ack=1101
6  0.004000 10.0.1.12→10.0.1.11 TCP 80→45000 [PSH,ACK] Seq=2001 Ack=1101 Len=500
```

**Întrebări:**

1. Care este adresa IP a clientului?
2. Care este adresa IP a serverului? De ce știm asta?
3. Ce serviciu rulează probabil pe server? (hint: port)
4. Cine a trimis primul date efective (nu handshake)?
5. Câți bytes de date a trimis clientul?
6. Câți bytes de date a trimis serverul?

<details>
<summary>✅ Răspunsuri</summary>

1. **10.0.1.11** - a trimis primul SYN
2. **10.0.1.12** - a răspuns cu SYN-ACK; serverul ascultă pe port 80
3. **HTTP** (port 80) - web server
4. **Clientul** (pachetul 4) - primul PSH după handshake
5. **100 bytes** (Len=100 în pachetul 4)
6. **500 bytes** (Len=500 în pachetul 6)

**Observație:** Seq crește cu numărul de bytes trimiși:
- Client: 1001 + 100 = 1101 (Ack în pachetul 5)
- Server: 2001 + 500 = 2501 (ar fi Ack-ul următor)
</details>

---

## Comparație TCP vs UDP în Captură

**Experiment:**

**TCP:**
```bash
# Terminal 1
sudo tshark -i lo -f "port 9999" -w tcp_test.pcap &

# Terminal 2
nc -l -p 9999 &

# Terminal 3
echo "Hello" | nc localhost 9999

# Oprire captură
pkill tshark
tshark -r tcp_test.pcap | wc -l
```

**UDP:**
```bash
# Terminal 1
sudo tshark -i lo -f "udp port 8888" -w udp_test.pcap &

# Terminal 2
nc -u -l -p 8888 &

# Terminal 3
echo "Hello" | nc -u localhost 8888

# Oprire captură
pkill tshark
tshark -r udp_test.pcap | wc -l
```

**🎯 PREDICȚIE:** Care captură va avea mai multe pachete? Cu cât?

<details>
<summary>✅ Răspuns</summary>

**TCP: ~8-10 pachete** (handshake + date + terminare)
**UDP: 1-2 pachete** (doar datagramele)

Diferența: overhead-ul de conexiune TCP!
</details>

---

## Debugging Frecvent

| Simptom | Cauză | Soluție |
|---------|-------|---------|
| "Permission denied" | Lipsă sudo | `sudo tshark ...` |
| Nu apar pachete | Interfață greșită | Folosește `-i lo` pentru loopback |
| Filtru nu funcționează | Sintaxă greșită | Verifică cu `-Y` (display) vs `-f` (capture) |
| PCAP gol | Captură oprită prea devreme | Folosește `-a duration:N` |

---

## Recapitulare

| Comandă | Scop |
|---------|------|
| `tshark -i lo` | Captură live pe loopback |
| `tshark -f "port X"` | Filtru de captură (BPF) |
| `tshark -w file.pcap` | Salvare în fișier |
| `tshark -r file.pcap` | Citire din fișier |
| `tshark -Y "filter"` | Display filter |
| `tshark -T fields -e X` | Extragere câmpuri specifice |

---

## Ce Urmează

În săptămâna 2 vom implementa servere și clienți TCP/UDP în Python folosind modulul `socket`.

---

*Timp estimat: 30 minute*
*Nivel: Mediu*
