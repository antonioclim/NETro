# Seminar 6 – SDN, Topologii Simulate, Analiză Trafic
## Laboratorul practic pentru Cursul 6

**Disciplina:** Rețele de calculatoare  
**Săptămâna:** 6 | **Durata:** 100 minute (2 ore academice)  
**Format:** Laborator hands-on cu demonstrații ghidate  
**Program:** Informatică Economică, ASE-CSIE

---

## Ce vom învăța

La finalul acestui seminar, studentul va fi capabil să:

1. **Configureze** NAT/MASQUERADE folosind iptables pe un router Linux
2. **Observe** și **interpreteze** traducerea adreselor în traficul de rețea
3. **Construiască** topologii de rețea în simulator (Mininet)
4. **Implementeze** politici SDN folosind controllere OpenFlow
5. **Analizeze** flow tables și să înțeleagă separarea control/data plane
6. **Depaneze** probleme de conectivitate folosind instrumente CLI

---

## De ce contează

Abilitățile practice din acest seminar sunt **direct transferabile** în mediul profesional:

- Configurarea NAT este standard în orice infrastructură de rețea
- SDN este adoptat masiv în data center-e și cloud (AWS, Azure, GCP)
- Analiza traficului este esențială pentru debugging și securitate
- Mininet/simulatoare sunt folosite pentru prototipare rapidă

---

## Prerechizite

**Tehnice:**
- Ubuntu 20.04+ sau VM Linux funcțională
- Starterkit-ul instalat: `make setup`
- Acces sudo pentru Mininet și captură pachete

**Conceptuale:**
- Cunoștințe din Cursul 6 (NAT, ARP, DHCP, ICMP)
- Familiaritate cu CLI Linux și Python

---

## Structura laboratorului

| Partea | Durată | Activitate |
|--------|--------|------------|
| A | 15 min | Warm-up: Verificare mediu și rutare de bază |
| B | 40 min | NAT/PAT: Configurare și observare |
| C | 35 min | SDN/OpenFlow: Control centralizat |
| D | 10 min | Reflecție și livrabile |

---

## Partea A: Warm-up și verificare (15 min)

### A.1 Verificarea mediului

**Comandă de start:**
```bash
cd starterkit_s6
make check
```

**Output așteptat:**
```
Verificare unelte necesare:
  ✓ python3
  ✓ mininet (mn)
  ✓ openvswitch
  ✓ tcpdump
  ✓ tshark
  ✓ iptables
  ✓ os-ken
```

**Dacă lipsesc unelte:** `make setup`

### A.2 Curățare artefacte anterioare

**IMPORTANT:** Înainte de fiecare exercițiu!

```bash
# Curățare completă
make clean

# Sau manual:
sudo mn -c
sudo pkill -9 -f osken-manager
```

### A.3 Topologia triunghi (opțional, pentru înțelegerea rutării)

**Comandă:**
```bash
make routing-demo
```

**Topologie:**
```
        r1 (10.0.1.1)
       /  \
      /    \
   r2 ────── r3
(10.0.2.1)  (10.0.3.1)
```

**Exerciții în CLI Mininet:**
```bash
mininet> r1 ip route
mininet> r1 traceroute -n 10.0.3.1
mininet> r1 ip link set r1-eth1 down  # dezactivează legătura directă
mininet> r1 traceroute -n 10.0.3.1    # observă ruta alternativă
```

**Întrebare de verificare:** Ce se întâmplă cu traficul când legătura r1-r3 cade?

---

## Partea B: NAT/PAT – Configurare și observare (40 min)

### B.1 Pornirea topologiei NAT

**Comandă:**
```bash
make nat-demo
```

**Topologie:**
```
┌─────────────────────┐         ┌─────────────────────┐
│    Rețea privată    │         │   "Internet"        │
│    192.168.1.0/24   │         │   203.0.113.0/24    │
│                     │         │                     │
│  h1 (192.168.1.10)  │         │  h3 (203.0.113.2)   │
│  h2 (192.168.1.20)  │         │  (server extern)    │
│         │          │         │         │          │
│         └────┬─────│         │─────────┘          │
│              │      │         │                     │
└──────────────┼──────┘         └─────────────────────┘
               │
        ┌──────┴──────┐
        │    rnat     │
        │ (Router NAT)│
        │             │
        │ eth0: 192.168.1.1
        │ eth1: 203.0.113.1
        │ MASQUERADE  │
        └─────────────┘
```

### B.2 Verificare configurare NAT

**În CLI Mininet, pe router:**
```bash
mininet> rnat iptables -t nat -L -n -v
```

**Output așteptat:**
```
Chain POSTROUTING (policy ACCEPT)
target     prot opt source        destination
MASQUERADE all  --  192.168.1.0/24  0.0.0.0/0
```

**Verificare IP forwarding:**
```bash
mininet> rnat sysctl net.ipv4.ip_forward
# Trebuie să fie = 1
```

### B.3 Test conectivitate de bază

**🔮 PREDICȚIE înainte de execuție:**
> h1 are IP-ul 192.168.1.10 (privat). h3 este pe "Internet" la 203.0.113.2.
> Credeți că ping-ul va funcționa? De ce da sau de ce nu?

**Pas 1: Ping de la h1 către h3**
```bash
mininet> h1 ping -c 3 203.0.113.2
```

**Verificare predicție:** A funcționat? Router-ul NAT traduce adresa sursă din 192.168.1.10 în 203.0.113.1

### B.4 Observarea traducerii – NAT Observer

**Pas 1:** Pornește serverul pe h3
```bash
mininet> h3 python3 seminar/python/apps/nat_observer.py server \
    --bind 203.0.113.2 --port 5000
```

**🔮 PREDICȚIE:** Ce adresă IP sursă va vedea serverul h3 pentru conexiunile de la h1 și h2?
- □ 192.168.1.10 și 192.168.1.20 (IP-urile reale)
- □ 203.0.113.1 pentru ambele (IP-ul NAT)
- □ Altceva

**Pas 2:** Conectează-te din h1 și h2
```bash
mininet> h1 python3 seminar/python/apps/nat_observer.py client \
    --host 203.0.113.2 --port 5000 --msg "mesaj de la h1"

mininet> h2 python3 seminar/python/apps/nat_observer.py client \
    --host 203.0.113.2 --port 5000 --msg "mesaj de la h2"
```

**Verificare predicție - Observă output-ul serverului:**
- Ambele conexiuni apar ca venind de la **203.0.113.1**
- Dar cu **porturi sursă diferite** – aceasta este esența PAT!

### B.5 Captură și analiză trafic

**🔮 PREDICȚIE:** În captura tcpdump de pe h3, se va vedea adresa 192.168.1.10?
- □ Da, tcpdump vede tot traficul original
- □ Nu, tcpdump vede doar ce ajunge efectiv la h3

**Pornește captura pe h3:**
```bash
mininet> h3 tcpdump -ni h3-eth0 -c 10 icmp or tcp port 5000
```

**În paralel, generează trafic:**
```bash
mininet> h1 ping -c 3 203.0.113.2
```

**Verificare predicție - Analizează output-ul tcpdump:**
- Ce adresă IP sursă vezi? (203.0.113.1, nu 192.168.1.10!)
- De ce? NAT modifică pachetele ÎNAINTE să ajungă la h3

### B.6 Inspectarea tabelei NAT

```bash
mininet> rnat conntrack -L 2>/dev/null || rnat cat /proc/net/nf_conntrack
```

**Sau folosind iptables counters:**
```bash
mininet> rnat iptables -t nat -L -n -v --line-numbers
```

---

## 🗳️ PEER INSTRUCTION: NAT și porturi sursă

### Scenariu

h1 (192.168.1.10) și h2 (192.168.1.20) trimit **simultan** pachete HTTP către același server extern (93.184.216.34:80) prin NAT. Ambele hosturi folosesc **portul sursă local 54321**.

### Întrebare

Ce se întâmplă cu cele două conexiuni?

**A)** Conexiunile eșuează – conflict de porturi pe router  
**B)** NAT alocă porturi externe DIFERITE pentru fiecare conexiune  
**C)** Pachetele se amestecă și ajung la host-ul greșit  
**D)** Router-ul refuză să facă traducerea pentru al doilea host  

---

**⏱️ Procedură (7 min total):**
1. (1 min) Citește scenariul
2. (1 min) Votează individual (ridică mâna pentru A/B/C/D)
3. (3 min) Discută cu colegul de bancă – argumentează alegerea
4. (30 sec) Revotează
5. (2 min) Explicația corectă

---

### 📋 NOTE INSTRUCTOR (nu pentru studenți)

**Răspuns corect:** B

**Analiza distractorilor:**
- **A:** Misconceptie: porturile locale contează pentru unicitate în NAT
- **C:** Misconceptie: NAT nu menține state (de fapt, tabela NAT e stateful)
- **D:** Misconceptie: NAT verifică unicitatea porturilor locale

**Explicație:** NAT/PAT menține o tabelă de corespondențe. Chiar dacă h1 și h2 folosesc același port sursă local, NAT alocă porturi EXTERNE diferite (ex: 40001, 40002). Identificarea unică se face prin tuplul (IP extern, port extern, IP destinație, port destinație, protocol).

**Target:** ~50% corect la primul vot

---

## Partea C: SDN cu OpenFlow (35 min)

### C.1 Concepte SDN

**Software-Defined Networking** separă:
- **Control Plane** – logica de decizie (controller)
- **Data Plane** – forwarding efectiv (switch-uri)

**Avantaje:**
- Vizibilitate centralizată
- Politici programabile
- Automatizare și orchestrare

### C.2 Pornirea controller-ului OS-Ken

**Terminal 1** (lasă deschis pe toată durata):
```bash
cd starterkit_s6
osken-manager seminar/python/controllers/sdn_policy_controller.py
```

Așteptați mesajul de inițializare. **Nu închideți acest terminal!**

### C.3 Pornirea topologiei SDN

**Terminal 2:**
```bash
sudo mn -c
sudo python3 seminar/mininet/topologies/topo_sdn.py --cli
```

**Topologie:**
```
h1 (10.0.10.1) ────┐
                   │
h2 (10.0.10.2) ────┼──── s1 (OVS) ←───── Controller
                   │          ↑
h3 (10.0.10.3) ────┘      OpenFlow 1.3
```

După conectare, ar trebui să vedeți în logurile controller-ului:
```
Table-miss installed on dpid=1
```

### C.4 Teste ICMP și inspectare flow table

**🔮 PREDICȚIE înainte de teste:**
Politica controller-ului este: h1↔h2 PERMIT, *→h3 DROP.

- Ping h1 → h2: □ Va funcționa □ Va eșua
- Ping h1 → h3: □ Va funcționa □ Va eșua

**În CLI Mininet:**

```bash
# Test 1: h1 → h2 (trebuie să meargă)
mininet> h1 ping -c 3 10.0.10.2

# Test 2: h1 → h3 (trebuie să fie blocat)
mininet> h1 ping -c 3 10.0.10.3

# Inspectare flow table
mininet> sh ovs-ofctl -O OpenFlow13 dump-flows s1
```

**Verificare predicții:**
- Care ping reușește și care nu?
- Ce reguli vedeți în flow table?
- Ce înseamnă `actions=drop` vs `actions=output:X`?

### C.5 Analiza flow-urilor

**Structura unui flow OpenFlow:**
```
cookie=0x0, duration=5.123s, table=0, n_packets=3, n_bytes=294,
priority=10, ip, nw_src=10.0.10.1, nw_dst=10.0.10.2
actions=output:2
```

| Câmp | Semnificație |
|------|--------------|
| priority | Regulile cu prioritate mai mare se verifică întâi |
| match fields | ip, nw_src, nw_dst, tp_dst etc. |
| actions | output:port, drop (lista goală), controller |
| n_packets | Contor pachete potrivite |

### C.6 Trafic de aplicație (TCP/UDP)

**TCP permis între h1 și h2:**
```bash
# Pe h2 (server)
mininet> h2 python3 seminar/python/apps/tcp_echo.py server \
    --bind 10.0.10.2 --port 5000

# Pe h1 (client)
mininet> h1 python3 seminar/python/apps/tcp_echo.py client \
    --dst 10.0.10.2 --port 5000 --message "test TCP"
```

**UDP către h3 (blocat implicit):**
```bash
# Pe h3 (server)
mininet> h3 python3 seminar/python/apps/udp_echo.py server \
    --bind 10.0.10.3 --port 6000

# Pe h1 (client)
mininet> h1 python3 seminar/python/apps/udp_echo.py client \
    --dst 10.0.10.3 --port 6000 --message "test UDP"
```

---

## 🗳️ PEER INSTRUCTION: SDN și prioritatea regulilor

### Scenariu

Un switch SDN are următoarele reguli în flow table:

```
priority=0   match=*                actions=CONTROLLER
priority=10  match=ip,dst=10.0.10.2 actions=output:2
priority=30  match=ip,dst=10.0.10.3 actions=drop
```

Un pachet IP ajunge cu destinația 10.0.10.3.

### Întrebare

Ce se întâmplă cu pachetul?

**A)** Ajunge la controller (prima regulă se aplică)  
**B)** Este trimis pe portul 2  
**C)** Este aruncat (drop)  
**D)** Pachetul rămâne în switch nedecis  

---

**⏱️ Procedură (7 min total):**
1. (1 min) Citește scenariul
2. (1 min) Votează individual
3. (3 min) Discută cu colegul
4. (30 sec) Revotează
5. (2 min) Explicația corectă

---

### 📋 NOTE INSTRUCTOR

**Răspuns corect:** C

**Analiza distractorilor:**
- **A:** Misconceptie: regulile se aplică în ordinea în care sunt listate
- **B:** Misconceptie: match-ul ip,dst=10.0.10.2 se potrivește cu 10.0.10.3
- **D:** Misconceptie: switch-ul poate rămâne blocat

**Explicație:** OpenFlow evaluează regulile în ordinea priorității (descrescător). Regula cu priority=30 are cea mai mare prioritate și match-ul corespunde (ip,dst=10.0.10.3), deci pachetul este aruncat.

**Target:** ~60% corect la primul vot

---

### C.7 Modificarea politicii (exercițiu)

**Sarcină:** Editați controller-ul pentru a permite UDP către h3, menținând blocarea TCP și ICMP.

**Pași:**
1. Editați `seminar/python/controllers/sdn_policy_controller.py`:
   ```python
   ALLOW_UDP_TO_H3 = True  # schimbați din False
   ```
2. Salvați modificarea
3. Opriți controller-ul (Ctrl+C)
4. Reporniți controller-ul
5. Cleanup și repornire topologie: `sudo mn -c && sudo python3 ...`
6. Re-testați:
   - UDP către h3 → trebuie să meargă acum
   - TCP către h3 → trebuie să rămână blocat
   - ICMP către h3 → trebuie să rămână blocat

---

## 👥 Exercițiu în perechi – Pair Programming (opțional)

### Instrucțiuni pentru Pair Programming

Lucrați în perechi pentru a rezolva provocarea de mai jos.

**Roluri:**
- **Driver** (la tastatură): Execută comenzile, scrie configurațiile
- **Navigator** (observă): Verifică output, sugerează soluții, consultă documentația

**Reguli:**
- Schimbați rolurile la fiecare 10 minute
- Navigator-ul NU atinge tastatura
- Driver-ul explică ce face în timp ce lucrează

### Provocare: Debugging NAT

**Situație:** NAT nu funcționează. Pachetele de la h1 nu ajung la h3.

**Task pentru pereche:**
1. **(Driver)** Verifică dacă IP forwarding e activat
2. **(Navigator)** Pregătește comanda de verificare iptables
3. **Schimbare roluri**
4. **(Driver nou)** Inspectează regulile iptables
5. **(Navigator nou)** Identifică ce regulă lipsește

**Soluție de verificat:**
```bash
# Verificare IP forwarding
sysctl net.ipv4.ip_forward  # trebuie să fie 1

# Verificare reguli
iptables -t nat -L -n -v

# Dacă lipsește MASQUERADE:
iptables -t nat -A POSTROUTING -s 192.168.1.0/24 -o eth1 -j MASQUERADE
```

---

## Partea D: Reflecție și livrabile (10 min)

### Întrebări de reflecție

**1. NAT/PAT și principiul end-to-end:**
Cum „încalcă" sau „modifică" NAT ideea de comunicare end-to-end? Dați un exemplu practic de aplicație afectată.

**2. Automatizare și management:**
Ce e mai ușor de automatizat și integrat în procese CI/CD: reguli iptables sau politici OpenFlow? Argumentați.

**3. Troubleshooting:**
Aveți o aplicație care nu funcționează. Ce instrumente și comenzi folosiți pentru diagnosticul problemei în fiecare caz (NAT vs. SDN)?

---

## Livrabile

### Livrabil A: `nat_output.txt` (30%)

Creați fișierul care să conțină:

1. **Comenzile rulate și output-ul lor:**
   - ping h1 → h3
   - ping h2 → h3
   - `iptables -t nat -L -n -v`
   - Log-ul serverului NAT-observer (minim 2 conexiuni)
   - Captură tcpdump (câteva linii relevante)

2. **Interpretare** (minim 8 rânduri):
   - Ce adresă sursă vede h3 pentru pachetele de la h1 și h2? De ce?
   - Ce se traduce (IP sursă, port sursă) și ce NU se traduce?
   - De ce e nevoie de mapare bidirecțională pentru răspunsuri?
   - Ce se pierde din perspectiva principiului end-to-end?

### Livrabil B: `routing_output.txt` (10% bonus)

- Output `traceroute` ÎNAINTE de modificare
- Comenzile folosite pentru schimbarea rutelor
- Output `traceroute` DUPĂ modificare

### Livrabil C: `sdn_output.txt` (40%)

Creați fișierul care să conțină:

1. **Output-uri:**
   - `h1 ping 10.0.10.2` (succes)
   - `h1 ping 10.0.10.3` (timeout)
   - `ovs-ofctl dump-flows s1` (ÎNAINTE de modificare)
   - `ovs-ofctl dump-flows s1` (DUPĂ modificarea ALLOW_UDP_TO_H3)
   - Minim 10 linii relevante din logurile controller-ului

2. **Interpretare** (minim 10 rânduri):
   - Cum se vede politica „allow h1↔h2" în flow table?
   - Ce diferențiază o regulă „allow" de una „drop"? (hint: actions)
   - Care este rolul regulii table-miss (priority=0)?
   - Ce înseamnă separarea control plane / data plane?
   - De ce primul pachet într-un flow nou e mai lent? (hint: packet_in)

### Livrabil D: `reflectie.txt` (20%)

Răspunsurile la cele 3 întrebări de reflecție (maxim 5 rânduri per întrebare).

---

## Criterii de evaluare

| Componentă | Punctaj | Cerințe minime |
|------------|---------|----------------|
| Livrabil A (NAT) | 30% | Comenzi + output + interpretare corectă |
| Livrabil B (Rutare) | 10% | Traceroute înainte/după (**bonus, opțional**) |
| Livrabil C (SDN) | 40% | Dump-flows + log + interpretare corectă |
| Livrabil D (Reflecție) | 20% | Răspunsuri argumentate și coerente |

**Notă minimă de trecere:** 50% din punctaj + prezența la seminar

---

## Troubleshooting rapid

| Problemă | Cauză probabilă | Soluție |
|----------|-----------------|---------|
| `mn: command not found` | Mininet neinstalat | `sudo apt install mininet` |
| OVS nu pornește | Serviciu oprit | `sudo systemctl restart openvswitch-switch` |
| Controller nu se conectează | Port blocat | Verifică portul 6633, oprește alte controllere |
| Ping SDN foarte lent | Lipsă flow-uri | Verifică cu `ovs-ofctl dump-flows` |
| NAT nu funcționează | IP forwarding dezactivat | `sysctl -w net.ipv4.ip_forward=1` |

---

## Sugestii pentru un livrabil de calitate

1. **Organizare clară:** Separați vizual comenzile de output și de interpretări
2. **Output selectat:** Nu copiați tot output-ul brut – selectați liniile relevante
3. **Interpretări proprii:** Evitați să copiați din curs sau de pe net
4. **Verificare înainte de predare:** Citiți fișierele și asigurați-vă că sunt complete

---

*Revolvix&Hypotheticalandrei*
