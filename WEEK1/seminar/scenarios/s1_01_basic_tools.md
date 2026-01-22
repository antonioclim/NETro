# Scenariul S1.01: Instrumente de Bază pentru Diagnostic

## Obiective

După parcurgerea acestui scenariu, studentul va putea:

1. Afișa și interpreta configurația interfețelor de rețea
2. Identifica gateway-ul implicit și tabelul de rutare
3. Testa conectivitatea folosind ping și interpreta rezultatele
4. Verifica porturile deschise și conexiunile active

## Context

Diagnosticarea problemelor de rețea începe întotdeauna cu verificarea configurației locale. Înainte de a căuta probleme în exterior, trebuie să confirmăm că propriul sistem este configurat corect.

**Analogie:** E ca și cum ai verifica dacă ai cheile în buzunar înainte să cauți prin toată casa. Întotdeauna verifică local întâi!

## Pași de Urmat

### Pasul 1: Verificare Interfețe (5 minute)

**🎯 PREDICȚIE:** Câte interfețe de rețea crezi că are mașina ta? Care e adresa IP a fiecăreia?

```bash
# Afișează toate interfețele
ip addr show

# Sau forma scurtă
ip a
```

**Ce observăm:**
- `lo` - interfața loopback (127.0.0.1), folosită pentru comunicare internă
- `eth0` sau `enp0s3` - interfața de rețea principală
- Adresa IPv4 în format CIDR (ex: 192.168.1.100/24)
- Starea interfeței: UP/DOWN, LOWER_UP

**Întrebări de verificare:**
- Care este adresa IP a mașinii tale?
- Ce înseamnă `/24` din adresa IP?
- Ce diferență este între `UP` și `LOWER_UP`?

### Pasul 2: Tabel de Rutare (5 minute)

**🎯 PREDICȚIE:** Ce adresă IP crezi că are gateway-ul (routerul) rețelei tale?

```bash
# Afișează rutele
ip route show

# Sau forma scurtă
ip r
```

**Ce observăm:**
- `default via X.X.X.X` - gateway-ul implicit (routerul)
- Rute specifice pentru rețele locale
- Interfața folosită pentru fiecare rută

**Exemplu output:**
```
default via 192.168.1.1 dev eth0 proto dhcp metric 100
192.168.1.0/24 dev eth0 proto kernel scope link src 192.168.1.100
```

**Interpretare:**
- Pachetele pentru Internet merg prin 192.168.1.1
- Pachetele pentru rețeaua locală (192.168.1.0/24) merg direct

### Pasul 3: Test Conectivitate cu Ping (10 minute)

**👥 PAIR PROGRAMMING:** Lucrați în perechi. Driver-ul execută comenzile, Navigator-ul verifică output-ul și notează valorile.

Testăm conectivitatea în etape, de la local la distant:

**🎯 PREDICȚIE pentru fiecare:** Care va fi RTT-ul aproximativ? (ms)

```bash
# Etapa 1: Loopback (verifică stack-ul TCP/IP)
ping -c 4 127.0.0.1
# Predicție RTT: _____ ms (hint: foarte mic!)

# Etapa 2: Propria adresă IP
ping -c 4 $(hostname -I | awk '{print $1}')
# Predicție RTT: _____ ms

# Etapa 3: Gateway-ul
ping -c 4 $(ip route | grep default | awk '{print $3}')
# Predicție RTT: _____ ms

# Etapa 4: Internet (DNS Google)
ping -c 4 8.8.8.8
# Predicție RTT: _____ ms

# Etapa 5: DNS (verifică rezoluție)
ping -c 4 google.com
# Predicție RTT: _____ ms
```

**Analiză output ping:**
```
PING 8.8.8.8 (8.8.8.8) 56(84) bytes of data.
64 bytes from 8.8.8.8: icmp_seq=1 ttl=117 time=12.3 ms
64 bytes from 8.8.8.8: icmp_seq=2 ttl=117 time=11.8 ms
...
--- 8.8.8.8 ping statistics ---
4 packets transmitted, 4 received, 0% packet loss, time 3004ms
rtt min/avg/max/mdev = 11.8/12.1/12.5/0.3 ms
```

**Metrici importante:**
- `ttl=117` - Time To Live, numărul de hopuri rămase
- `time=12.3 ms` - latența (RTT)
- `0% packet loss` - toate pachetele au ajuns
- `rtt min/avg/max/mdev` - statistici latență

### Pasul 4: Verificare Porturi (5 minute)

**🎯 PREDICȚIE:** Ce servicii crezi că ascultă pe mașina ta? (SSH? Web server? Altceva?)

```bash
# Porturi TCP în ascultare
ss -tlnp

# Conexiuni TCP active
ss -tnp

# Toate conexiunile (TCP + UDP)
ss -tunap
```

**Parametri ss:**
- `-t` - TCP
- `-u` - UDP
- `-l` - listening (în ascultare)
- `-n` - numeric (fără rezoluție DNS)
- `-p` - process (afișează PID și numele procesului)
- `-a` - all (toate stările)

**Exemplu interpretare:**
```
State    Recv-Q   Send-Q   Local Address:Port   Peer Address:Port   Process
LISTEN   0        128      0.0.0.0:22           0.0.0.0:*           sshd
ESTAB    0        0        192.168.1.100:22     192.168.1.50:54321  sshd
```
- Serverul SSH ascultă pe toate interfețele (:22)
- O conexiune SSH este stabilită din 192.168.1.50

---

## 🗳️ PEER INSTRUCTION: Interpretare ss output

**Output:**
```
LISTEN   0   128   127.0.0.1:5432   0.0.0.0:*   postgres
```

**Întrebare:** Poate un client de pe alt calculator să se conecteze la acest server PostgreSQL?

| Opțiune | Răspuns |
|---------|---------|
| **A** | Da, portul 5432 este deschis |
| **B** | Nu, serverul ascultă doar pe loopback (127.0.0.1) |
| **C** | Depinde de firewall |
| **D** | Da, dar trebuie să folosească adresa 127.0.0.1 |

<details>
<summary>🎯 Răspuns</summary>

**Corect: B** - `127.0.0.1` înseamnă că serverul acceptă conexiuni DOAR de pe mașina locală. Pentru acces extern trebuie să asculte pe `0.0.0.0` sau pe IP-ul extern specific.
</details>

---

## Exerciții Practice

### Exercițiul 1.1 - Documentare Configurație (Începător)

Creează un fișier `config_retea.txt` cu:
```bash
echo "=== Configurație Rețea ===" > config_retea.txt
echo "Data: $(date)" >> config_retea.txt
echo "" >> config_retea.txt
echo "--- Interfețe ---" >> config_retea.txt
ip addr >> config_retea.txt
echo "" >> config_retea.txt
echo "--- Rutare ---" >> config_retea.txt
ip route >> config_retea.txt
```

### Exercițiul 1.2 - Test Conectivitate Complet (Mediu) 👥

**Lucru în perechi:** Scrie un script bash care:
1. Testează loopback
2. Testează gateway
3. Testează Internet
4. Afișează PASS/FAIL pentru fiecare

```bash
#!/bin/bash
# test_connectivity.sh

test_ping() {
    if ping -c 1 -W 2 "$1" &>/dev/null; then
        echo "[PASS] $2"
        return 0
    else
        echo "[FAIL] $2"
        return 1
    fi
}

echo "=== Test Conectivitate ==="
test_ping 127.0.0.1 "Loopback"
test_ping "$(ip route | grep default | awk '{print $3}')" "Gateway"
test_ping 8.8.8.8 "Internet"
test_ping google.com "DNS"
```

### Exercițiul 1.3 - Analiză Latență (Avansat)

Măsoară latența către 5 destinații și creează un tabel:

| Destinație | Min (ms) | Avg (ms) | Max (ms) | Loss (%) |
|------------|----------|----------|----------|----------|
| Gateway    |          |          |          |          |
| 8.8.8.8    |          |          |          |          |
| 1.1.1.1    |          |          |          |          |
| ...        |          |          |          |          |

---

## 📝 PARSONS PROBLEM: Script de diagnostic

**Sarcină:** Ordonează liniile pentru a crea un script valid care testează conectivitatea și salvează rezultatul.

**Linii amestecate:**
```
E) ping -c 3 8.8.8.8 >> $OUTPUT
B) OUTPUT="diagnostic_$(date +%Y%m%d).txt"
D) echo "=== Test Gateway ===" >> $OUTPUT
A) #!/bin/bash
F) echo "=== Test Internet ===" >> $OUTPUT
C) ping -c 3 $(ip route | grep default | awk '{print $3}') >> $OUTPUT
G) echo "Diagnostic salvat în $OUTPUT"
```

<details>
<summary>✅ Ordinea corectă</summary>

**A → B → D → C → F → E → G**

```bash
#!/bin/bash                                                    # A
OUTPUT="diagnostic_$(date +%Y%m%d).txt"                       # B
echo "=== Test Gateway ===" >> $OUTPUT                        # D
ping -c 3 $(ip route | grep default | awk '{print $3}') >> $OUTPUT  # C
echo "=== Test Internet ===" >> $OUTPUT                       # F
ping -c 3 8.8.8.8 >> $OUTPUT                                  # E
echo "Diagnostic salvat în $OUTPUT"                           # G
```
</details>

---

## Debugging

| Simptom | Cauză Probabilă | Soluție |
|---------|-----------------|---------|
| ping loopback eșuează | Stack TCP/IP corupt | Repornește serviciul network |
| ping gateway eșuează | Cablu deconectat sau IP greșit | Verifică fizic, rulează dhclient |
| ping IP funcționează, DNS nu | Server DNS incorect | Verifică /etc/resolv.conf |
| TTL foarte mic | Multe hopuri, posibil routing loop | Verifică cu traceroute |

## Recapitulare

- `ip addr` - configurație interfețe
- `ip route` - tabel rutare
- `ping` - test conectivitate ICMP
- `ss` - statistici socket-uri

## Ce Urmează

În scenariul următor vom folosi `netcat` pentru a crea comunicare TCP și UDP între procese.

---

*Timp estimat: 25 minute*
*Nivel: Începător*
