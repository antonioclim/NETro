# Laborator 5: Configurarea practică a adresării IP și rutării statice

## Scopul laboratorului

Parcurgem împreună configurarea completă a unei infrastructuri de rețea cu multiple subrețele, de la proiectarea schemei de adresare până la verificarea conectivității end-to-end. Folosim exclusiv unelte CLI și simulatorul Mininet.

> **💡 Lucru în echipă:** Formați perechi. Unul rulează comenzile (Driver), celălalt verifică output-ul și consultă cheatsheet-ul (Navigator). Schimbați rolurile după fiecare experiment.

---

## Pregătire

### Verificarea mediului de lucru

```bash
cd /path/to/starterkit_s5
make verify
```

**Output așteptat:**
```
[OK] Python 3.10+ instalat
[OK] Mininet disponibil
[OK] Open vSwitch activ
[OK] Modulul ipaddress funcțional
[OK] Permisiuni sudo disponibile
```

### Structura fișierelor utilizate

```
starterkit_s5/
├── python/
│   ├── exercises/
│   │   ├── ex_5_01_cidr_flsm.py   ← Calculatoare CIDR/FLSM
│   │   ├── ex_5_02_vlsm_ipv6.py   ← Planificator VLSM, IPv6
│   │   └── ex_5_03_quiz_generator.py
│   └── utils/
│       └── net_utils.py           ← Bibliotecă de funcții
└── mininet/
    └── topologies/
        ├── topo_5_base.py         ← Topologie simplă
        └── topo_5_extended.py     ← Topologie VLSM + IPv6
```

---

## Experiment 1: Analiza CIDR cu Python

### Obiectiv
Calculul programatic al tuturor parametrilor unei rețele IPv4.

### Pași

**Pasul 1.1** — Analizarea unei adrese simple.

> **🎯 Predicție:** Pentru 192.168.1.100/24, câte hosturi utilizabile crezi că va raporta? Notează răspunsul.

```bash
cd python/exercises
python ex_5_01_cidr_flsm.py analyze 192.168.1.100/24
```

**Output așteptat:**
```
╔══════════════════════════════════════════════════════════════╗
║                    Analiză CIDR: 192.168.1.100/24            ║
╠══════════════════════════════════════════════════════════════╣
║  Adresă IP:        192.168.1.100                             ║
║  Prefix:           /24                                       ║
║  Mască rețea:      255.255.255.0                             ║
║  Adresă rețea:     192.168.1.0                               ║
║  Broadcast:        192.168.1.255                             ║
║  Prima gazdă:      192.168.1.1                               ║
║  Ultima gazdă:     192.168.1.254                             ║
║  Total gazde:      254                                       ║
╚══════════════════════════════════════════════════════════════╝
```

Ai ghicit 254? Dacă ai zis 256, ai uitat să scazi adresa de rețea și broadcast.

**Pasul 1.2** — Vizualizarea reprezentării binare.

> **🎯 Predicție:** Pentru 172.16.50.12/21, care va fi adresa de rețea? Calculează manual (AND între IP și mască), apoi verifică.

```bash
python ex_5_01_cidr_flsm.py analyze 172.16.50.12/21 --verbose
```

**Output așteptat (parțial):**
```
Reprezentare binară:
  IP:    10101100.00010000.00110010.00001100
  Mască: 11111111.11111111.11111000.00000000
  Rețea: 10101100.00010000.00110000.00000000 (172.16.48.0)
```

**Pasul 1.3** — Export în format JSON (pentru procesare automată).

```bash
python ex_5_01_cidr_flsm.py analyze 10.0.0.1/8 --json > rezultat.json
cat rezultat.json
```

### Ce observăm
Scriptul aplică operația AND bit cu bit între adresa IP și mască pentru a obține adresa de rețea, apoi completează cu 1 biții de host pentru broadcast.

---

## Experiment 2: Partiționare FLSM

### Obiectiv
Împărțirea unei rețele în subrețele de dimensiuni egale.

### Scenariu
Rețeaua `10.10.0.0/16` trebuie împărțită pentru 4 departamente egale.

**Pasul 2.1** — Generarea subrețelelor.

> **🎯 Predicție:** Pentru 4 subrețele din /16, ce prefix nou va rezulta? (Hint: câți biți împrumuți pentru 4?)

```bash
python ex_5_01_cidr_flsm.py flsm 10.10.0.0/16 4
```

**Output așteptat:**
```
╔══════════════════════════════════════════════════════════════╗
║         Partiționare FLSM: 10.10.0.0/16 → 4 subrețele        ║
╠══════════════════════════════════════════════════════════════╣
║  Prefix nou: /18 (biți împrumutați: 2)                       ║
║  Gazde per subrețea: 16382                                   ║
╠══════════════════════════════════════════════════════════════╣
║  #  │ Rețea          │ Prima gazdă    │ Ultima gazdă   │ BC  ║
╠═════╪════════════════╪════════════════╪════════════════╪═════╣
║  0  │ 10.10.0.0/18   │ 10.10.0.1      │ 10.10.63.254   │ ... ║
║  1  │ 10.10.64.0/18  │ 10.10.64.1     │ 10.10.127.254  │ ... ║
║  2  │ 10.10.128.0/18 │ 10.10.128.1    │ 10.10.191.254  │ ... ║
║  3  │ 10.10.192.0/18 │ 10.10.192.1    │ 10.10.255.254  │ ... ║
╚══════════════════════════════════════════════════════════════╝
```

**Pasul 2.2** — Testarea cu 16 subrețele.

> **🎯 Predicție:** Pentru 16 subrețele din /24, ce prefix rezultă?

```bash
python ex_5_01_cidr_flsm.py flsm 192.168.0.0/24 16
```

### Întrebare de verificare
Câți biți trebuie împrumutați pentru exact 16 subrețele? Ce prefix rezultă din `/24`?

Răspuns: 4 biți (2^4 = 16), prefix nou = /28

---

## Experiment 3: Planificare VLSM

### Obiectiv
Alocarea eficientă a spațiului de adrese pentru cerințe neuniforme.

### Scenariu
Compania necesită:
- Departament tehnic: 100 stații
- Departament vânzări: 50 stații
- Management: 20 stații
- Link WAN: 2 adrese

Rețea disponibilă: `192.168.10.0/24`

**Pasul 3.1** — Generarea planului VLSM.

> **🎯 Predicție:** Ce eficiență crezi că va avea planul? Peste 80%? Peste 70%?

```bash
cd python/exercises
python ex_5_02_vlsm_ipv6.py vlsm 192.168.10.0/24 100 50 20 2
```

**Output așteptat:**
```
╔══════════════════════════════════════════════════════════════╗
║             Plan VLSM pentru 192.168.10.0/24                 ║
╠══════════════════════════════════════════════════════════════╣
║  Cerințe sortate descrescător: 100, 50, 20, 2                ║
╠══════════════════════════════════════════════════════════════╣
║  #  │ Necesar │ Prefix │ Rețea               │ Eficiență     ║
╠═════╪═════════╪════════╪═════════════════════╪═══════════════╣
║  1  │ 100     │ /25    │ 192.168.10.0/25     │ 79.4% (126)   ║
║  2  │ 50      │ /26    │ 192.168.10.128/26   │ 80.6% (62)    ║
║  3  │ 20      │ /27    │ 192.168.10.192/27   │ 66.7% (30)    ║
║  4  │ 2       │ /30    │ 192.168.10.224/30   │ 100.0% (2)    ║
╠══════════════════════════════════════════════════════════════╣
║  Eficiență totală: 172/220 = 78.2%                           ║
║  Spațiu rămas: 192.168.10.228/26 (32 adrese)                 ║
╚══════════════════════════════════════════════════════════════╝
```

**Pasul 3.2** — Verificarea lipsei suprapunerilor.

Observă că fiecare subrețea începe exact acolo unde se termină precedenta. Asta previne conflictele de adresare.

### Ce observăm
VLSM produce eficiență mai mare decât FLSM când cerințele sunt neuniforme — fiecare subrețea primește exact spațiul necesar.

---

## Experiment 4: Operații IPv6

### Obiectiv
Manipularea adreselor IPv6: comprimare, expandare, identificare tip.

**Pasul 4.1** — Comprimarea unei adrese.

> **🎯 Predicție:** Comprimă manual `2001:0db8:0000:0000:0000:0000:0000:0001`. Scrie răspunsul, apoi verifică.

```bash
python ex_5_02_vlsm_ipv6.py ipv6 2001:0db8:0000:0000:0000:0000:0000:0001
```

**Output:**
```
Original:  2001:0db8:0000:0000:0000:0000:0000:0001
Comprimat: 2001:db8::1
Tip:       Global Unicast (rutabil Internet)
```

**Pasul 4.2** — Expandarea unei adrese comprimate.

```bash
python ex_5_02_vlsm_ipv6.py ipv6-expand 2001:db8::1
```

**Output:**
```
Comprimat: 2001:db8::1
Expandat:  2001:0db8:0000:0000:0000:0000:0000:0001
```

**Pasul 4.3** — Referința tipurilor de adrese.

```bash
python ex_5_02_vlsm_ipv6.py ipv6-types
```

**Pasul 4.4** — Generarea subrețelelor /64 dintr-un bloc /48.

> **🎯 Predicție:** Câte subrețele /64 poți crea dintr-un bloc /48?

```bash
python ex_5_02_vlsm_ipv6.py ipv6-subnets 2001:db8:abcd::/48 8
```

Răspuns: 2^(64-48) = 2^16 = 65.536 subrețele posibile!

---

## Experiment 5: Topologie Mininet — Rutare de bază

### Obiectiv
Configurarea și testarea conectivității între două subrețele prin rutare statică.

**Pasul 5.1** — Pornirea topologiei.

```bash
cd mininet/topologies
sudo python topo_5_base.py --cli
```

**Pasul 5.2** — Examinarea nodurilor.

```
mininet> nodes
available nodes are:
h1 h2 r1 s1 s2

mininet> net
h1 h1-eth0:s1-eth1
h2 h2-eth0:s2-eth1
r1 r1-eth0:s1-eth2 r1-eth1:s2-eth2
s1 lo:  s1-eth1:h1-eth0 s1-eth2:r1-eth0
s2 lo:  s2-eth1:h2-eth0 s2-eth2:r1-eth1
```

**Pasul 5.3** — Verificarea configurației IP.

```
mininet> h1 ip addr show h1-eth0
2: h1-eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500
    inet 10.0.1.10/24 brd 10.0.1.255 scope global h1-eth0

mininet> h2 ip addr show h2-eth0
2: h2-eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500
    inet 10.0.2.10/24 brd 10.0.2.255 scope global h2-eth0

mininet> r1 ip addr
```

**Pasul 5.4** — Verificarea tabelelor de rutare.

```
mininet> h1 ip route
default via 10.0.1.1 dev h1-eth0
10.0.1.0/24 dev h1-eth0 proto kernel scope link src 10.0.1.10

mininet> r1 ip route
10.0.1.0/24 dev r1-eth0 proto kernel scope link src 10.0.1.1
10.0.2.0/24 dev r1-eth1 proto kernel scope link src 10.0.2.1
```

**Pasul 5.5** — Testarea conectivității.

> **🎯 Predicție:** Ping-ul de la h1 la 10.0.2.10 va reuși? Ce condiții trebuie să fie îndeplinite? (Gateway configurat? IP forwarding activ? Rute corecte?)

```
mininet> h1 ping -c 4 10.0.2.10
PING 10.0.2.10 (10.0.2.10) 56(84) bytes of data.
64 bytes from 10.0.2.10: icmp_seq=1 ttl=63 time=0.652 ms
64 bytes from 10.0.2.10: icmp_seq=2 ttl=63 time=0.091 ms
...
```

**Pasul 5.6** — Capturarea traficului pe router.

În primul terminal Mininet:
```
mininet> r1 tcpdump -i r1-eth0 -n icmp &
```

În același terminal, generăm trafic:
```
mininet> h1 ping -c 2 10.0.2.10
```

> **🎯 Predicție:** Ce TTL va apărea în captură pentru pachetele de la h1? Dar pentru reply-urile de la h2?

**Output tcpdump așteptat:**
```
10.0.1.10 > 10.0.2.10: ICMP echo request, id 1234, seq 1
10.0.2.10 > 10.0.1.10: ICMP echo reply, id 1234, seq 1
```

**Pasul 5.7** — Ieșire și curățare.

```
mininet> exit
```

---

## Experiment 6: Topologie VLSM avansată

### Obiectiv
Demonstrarea unei rețele cu 3 subrețele de dimensiuni diferite și suport IPv6 opțional.

**Pasul 6.1** — Pornirea topologiei extinse (doar IPv4).

```bash
sudo python topo_5_extended.py --cli
```

**Arhitectura:**
```
   10.0.10.0/26 (62 hosts)     10.0.20.0/28 (14 hosts)    10.0.30.0/30 (P2P)
          |                           |                          |
         h1 -------- r1 -----------  h2 ------- r1 ------------ h3
       .10    .1           .1       .10    .1           .1      .2
```

**Pasul 6.2** — Verificarea subrețelelor diferite.

```
mininet> dump
<Host h1: h1-eth0:10.0.10.10 pid=...>
<Host h2: h2-eth0:10.0.20.10 pid=...>
<Host h3: h3-eth0:10.0.30.2 pid=...>
```

**Pasul 6.3** — Test de conectivitate completă.

> **🎯 Predicție:** `pingall` va arăta 0% dropped? Toate cele 6 ping-uri vor reuși?

```
mininet> pingall
*** Ping: testing ping reachability
h1 -> h2 h3
h2 -> h1 h3
h3 -> h1 h2
*** Results: 0% dropped (6/6 received)
```

**Pasul 6.4** — Activarea IPv6 dual-stack.

```bash
sudo python topo_5_extended.py --cli --ipv6
```

```
mininet> h1 ip -6 addr show h1-eth0
    inet6 2001:db8:10::10/64 scope global
    inet6 fe80::... scope link

mininet> h1 ping6 -c 2 2001:db8:20::10
```

---

## Experiment 7: Quiz interactiv

### Obiectiv
Auto-evaluarea cunoștințelor prin întrebări generate aleator.

**Pasul 7.1** — Pornirea quiz-ului interactiv.

```bash
cd python/exercises
python ex_5_03_quiz_generator.py --interactive --count 5
```

**Pasul 7.2** — Modul batch (pentru revizuire rapidă).

```bash
python ex_5_03_quiz_generator.py --batch --count 10
```

---

## Verificare finală

### Lista de control

| Verificare | Comandă | Rezultat așteptat |
|------------|---------|-------------------|
| Analiză CIDR funcțională | `python ex_5_01_cidr_flsm.py analyze 192.168.1.1/24` | Afișează toți parametrii |
| FLSM corect | `python ex_5_01_cidr_flsm.py flsm 10.0.0.0/8 4` | 4 subrețele /10 |
| VLSM funcțional | `python ex_5_02_vlsm_ipv6.py vlsm 192.168.0.0/24 100 50` | Plan optimizat |
| Topologie Mininet pornește | `sudo python topo_5_base.py --test` | 0% packet loss |
| IPv6 operațional | `sudo python topo_5_extended.py --test --ipv6` | ping6 reușit |

### Curățare completă

```bash
sudo mn -c
make clean
```

---

## Extensii opționale

### Extensie 1: Adăugarea unui al treilea router
Modifică `topo_5_extended.py` pentru a adăuga un al doilea router și o a patra subrețea.

### Extensie 2: Capturarea în format PCAP
```bash
mininet> r1 tcpdump -i r1-eth0 -w /tmp/capture.pcap &
mininet> h1 ping -c 10 10.0.2.10
# Apoi deschide /tmp/capture.pcap în Wireshark
```

### Extensie 3: Testare de throughput
```bash
# Pe h2:
mininet> h2 iperf -s &
# Pe h1:
mininet> h1 iperf -c 10.0.2.10 -t 10
```

---

## Întrebări de reflecție

1. De ce TTL-ul scade când pachetul traversează routerul?
2. Ce s-ar întâmpla dacă am dezactiva IP forwarding pe router?
3. Care este avantajul principal al VLSM față de FLSM?
4. De ce adresele IPv6 link-local (fe80::) nu sunt rutabile?

---

## Exerciții suplimentare

Pentru consolidare, parcurge și exercițiile din `docs/exercitii_variate_week5.md`:
- 2 exerciții Parsons (reordonare pași)
- 1 exercițiu Trace (urmărire pachet)
- 1 exercițiu Debugging (găsește eroarea)
- 1 exercițiu Code Reading (ce face codul)

---

*Material didactic ASE-CSIE — Laborator Rețele de calculatoare*
