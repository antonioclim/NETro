# Curs 1: Fundamentele Rețelelor de Calculatoare

## Informații generale

| Disciplină | Rețele de Calculatoare |
|------------|------------------------|
| Săptămâna | 1 |
| Tip activitate | Curs (prelegere) |
| Durată | 2 ore (100 minute) |
| Locație | Sală cu acces Internet și echipament multimedia |

---

## Ce vom învăța

La finalul acestui curs, studenții vor fi capabili să:

1. **Definească** conceptele fundamentale: rețea, LAN, WAN, Internet, protocol
2. **Identifice** componentele unei rețele și rolul fiecăreia (de la NIC la router)
3. **Explice** diferențele dintre modelele OSI și TCP/IP, precum și procesul de încapsulare
4. **Interpreteze** parametrii de performanță ai unei rețele (bandwidth, latență, jitter)

---

## De ce contează

Pentru un programator, înțelegerea rețelelor reprezintă fundamentul dezvoltării aplicațiilor moderne. Aproape orice aplicație contemporană comunică prin rețea: de la aplicații web și mobile, la microservicii și sisteme distribuite, până la dispozitive IoT.

Cunoașterea modului în care funcționează rețelele ajută programatorul să:
- Diagnosticheze probleme de conectivitate și performanță
- Optimizeze transferul de date între componente
- Implementeze comunicarea între procese și servicii
- Înțeleagă implicațiile de securitate ale deciziilor de arhitectură

---

## Structura cursului

### Partea I: Introducere și concepte de bază (30 min)

#### 1.1 Ce este o rețea de calculatoare?

O **rețea de calculatoare** reprezintă un ansamblu de dispozitive interconectate care pot comunica și partaja resurse. Elementele definitorii includ:

- **Noduri** (hosts): calculatoare, telefoane, servere, dispozitive IoT
- **Legături** (links): cabluri, fibră optică, conexiuni wireless
- **Protocoale**: reguli de comunicare între dispozitive
- **Servicii de rețea**: partajare fișiere, email, web, mesagerie

**Analogie concretă:** Gândește-te la o rețea ca la sistemul poștal. Ai expeditori și destinatari (noduri), drumuri și căi ferate (legături), reguli de adresare și livrare (protocoale), și diverse servicii (scrisori, colete, expres).

#### 1.2 Clasificarea rețelelor

| Tip | Acoperire | Exemple | Tehnologii |
|-----|-----------|---------|------------|
| **PAN** | < 10m | Dispozitive personale | Bluetooth, USB |
| **LAN** | Clădire/campus | Rețea de birou | Ethernet, Wi-Fi |
| **MAN** | Oraș | Rețea metropolitană | Fibră optică |
| **WAN** | Global | Internet | MPLS, legături dedicate |

#### 1.3 Topologii de rețea

- **Stea (Star)**: toate nodurile conectate la un nod central; ușor de administrat, SPOF
- **Inel (Ring)**: noduri conectate circular; latență predictibilă, vulnerabil la întreruperi
- **Bus**: toate nodurile pe un cablu comun; simplu, coliziuni frecvente
- **Plasă (Mesh)**: conexiuni multiple între noduri; redundant, complex

**Reprezentări vizuale:**

```
STEA (Star)                    INEL (Ring)
                               
    [H1]                           [H1]
      \                           /    \
       \                         /      \
    [H2]--[SW]--[H3]          [H4]      [H2]
       /                         \      /
      /                           \    /
    [H4]                           [H3]
                               
  Avantaj: ușor de administrat   Avantaj: latență predictibilă
  Dezavantaj: SPOF pe switch     Dezavantaj: vulnerabil la întreruperi


BUS                              PLASĂ (Mesh)
                               
═══════════════════════              [H1]────[H2]
 │     │     │     │                  │ \  / │
[H1]  [H2]  [H3]  [H4]               │  \/  │
                                     │  /\  │
  Avantaj: simplu, ieftin           [H3]────[H4]
  Dezavantaj: coliziuni          
                                 Avantaj: redundanță maximă
                                 Dezavantaj: complex, costisitor
```

**Alegerea topologiei depinde de:** buget, dimensiune rețea, cerințe de fiabilitate, ușurința administrării.

---

### Partea II: Parametri de transmisie (20 min)

#### 2.1 Bandwidth (lățime de bandă)

Capacitatea maximă teoretică a unei legături, măsurată în **biți per secundă** (bps).

**Analogie concretă:** Bandwidth-ul e ca lățimea unei autostrăzi – câte benzi are. O autostradă cu 4 benzi poate transporta mai multe mașini simultan decât una cu 2 benzi, dar asta nu înseamnă că mașinile merg mai repede.

| Tehnologie | Bandwidth tipic |
|------------|-----------------|
| Ethernet 100BASE-TX | 100 Mbps |
| Gigabit Ethernet | 1 Gbps |
| WiFi 6 (802.11ax) | până la 9.6 Gbps (teoretic) |
| Fibră (FTTH) | 1-10 Gbps |

#### 2.2 Latența (delay)

Timpul necesar ca datele să parcurgă distanța de la sursă la destinație. Componente:

**Analogie concretă:** Latența e ca timpul de călătorie pe autostradă – cât durează să ajungi din punct A în punct B. Poți avea o autostradă lată (bandwidth mare) dar cu multe semafoare (delay de procesare) și ambuteiaje (delay de coadă).

1. **Delay de transmisie** = L/R (dimensiune pachet / bandwidth)
2. **Delay de propagare** = d/s (distanță / viteză în mediu)
3. **Delay de procesare** = timp de procesare în routere/switch-uri
4. **Delay de coadă** = așteptare în buffer-e

**Exemplu concret:**
- Pachet de 1500 bytes pe legătură de 1 Gbps
- Delay transmisie = (1500 × 8) / 10⁹ = 12 μs
- Delay propagare pe 1000 km fibră = 5 ms

#### 2.3 Jitter și Packet Loss

- **Jitter**: variația latentei între pachete consecutive; critic pentru streaming
- **Packet Loss**: procentul de pachete pierdute; afectează TCP prin retransmisii

---

### Partea III: Dispozitive de rețea (20 min)

#### 3.1 Nivelul 1 (Fizic)

- **NIC (Network Interface Card)**: conectează host-ul la rețea
- **Hub**: regenerează semnalul; broadcast la toate porturile; coliziuni
- **Repeater**: extinde distanța fizică a semnalului

#### 3.2 Nivelul 2 (Legătură de date)

- **Switch**: comută cadre pe baza adresei MAC; tabel de forwarding
- **Bridge**: conectează segmente de rețea; filtrează trafic

**Analogie concretă:** Un switch e ca un portar inteligent într-un bloc de apartamente – știe în ce apartament locuiește fiecare și livrează coletele doar la ușa corectă. Un hub e ca un portar care strigă în tot blocul "A venit colet pentru Ion!" – toată lumea aude, dar doar Ion ia coletul.

**Comparație Hub vs Switch:**

```
HUB (Layer 1)                    SWITCH (Layer 2)
                               
Cadru de la H1 → H3              Cadru de la H1 → H3
                               
    ┌───────────┐                    ┌───────────┐
    │    HUB    │                    │   SWITCH  │
    └─┬──┬──┬──┬┘                    └─┬──┬──┬──┬┘
      │  │  │  │                       │  │  │  │
     H1 H2 H3 H4                      H1 H2 H3 H4
     ↑  ↑  ↑  ↑                       ↑     ↑   
     BROADCAST                        UNICAST
     (toți primesc)                   (doar H3)
```

#### 3.3 Nivelul 3 (Rețea)

- **Router**: rutează pachete între rețele; folosește adrese IP
- **Gateway**: traduce între protocoale diferite

**Analogie concretă:** Routerul e ca un oficiu poștal care sortează scrisorile pe coduri poștale și le trimite spre destinația finală prin diverse căi.

#### 3.4 Dispozitive de securitate

- **Firewall**: filtrează trafic pe baza regulilor
- **IDS/IPS**: detectează și previne intruziuni

---

### Partea IV: Modele arhitecturale (20 min)

#### 4.1 Modelul OSI (Open Systems Interconnection)

Dezvoltat de ISO, model de referință cu 7 niveluri:

| # | Nivel | Funcție | Exemple protocoale |
|---|-------|---------|-------------------|
| 7 | Aplicație | Interfață utilizator | HTTP, SMTP, DNS |
| 6 | Prezentare | Format, criptare | SSL/TLS, JPEG |
| 5 | Sesiune | Gestiune conexiuni | NetBIOS, RPC |
| 4 | Transport | Livrare end-to-end | TCP, UDP |
| 3 | Rețea | Rutare | IP, ICMP |
| 2 | Legătură date | Acces mediu, adresare | Ethernet, WiFi |
| 1 | Fizic | Biți pe mediu | Cabluri, conectori |

#### 4.2 Modelul TCP/IP (Internet)

Model practic cu 4 niveluri, derivat din implementarea ARPANET:

| Nivel TCP/IP | Corespondență OSI | Protocoale |
|--------------|-------------------|------------|
| Aplicație | 5-7 | HTTP, FTP, DNS, SSH |
| Transport | 4 | TCP, UDP |
| Internet | 3 | IP, ICMP, ARP |
| Acces rețea | 1-2 | Ethernet, WiFi, PPP |

#### 4.3 Încapsularea datelor

La traversarea stivei de protocoale, fiecare nivel adaugă un header (și uneori trailer):

**Analogie concretă:** E ca și cum ai pune o scrisoare într-un plic (nivel aplicație), plicul într-un plic mai mare cu adresa destinatarului (nivel transport), apoi într-o cutie cu eticheta poștală (nivel rețea), și în final într-un sac de transport (nivel legătură).

```
[Date aplicație]
[Header TCP][Date aplicație]                    → Segment
[Header IP][Header TCP][Date aplicație]         → Pachet/Datagramă
[Header Eth][Header IP][Header TCP][Date][FCS]  → Cadru (Frame)
```

---

### Partea V: Protocoale și standarde (10 min)

#### 5.1 Ce este un protocol?

Un **protocol** definește:
- **Sintaxa**: formatul mesajelor (câmpuri, ordine bytes)
- **Semantica**: semnificația câmpurilor și acțiunile corespunzătoare
- **Sincronizarea**: ordinea mesajelor și timing-ul

**Exemplu: HTTP**
```
GET /index.html HTTP/1.1
Host: www.example.com
```

#### 5.2 Organisme de standardizare

| Organism | Focus | Standarde |
|----------|-------|-----------|
| **IEEE** | Tehnologii fizice | 802.3 (Ethernet), 802.11 (WiFi) |
| **IETF** | Protocoale Internet | TCP, IP, HTTP (via RFC) |
| **W3C** | Web | HTML, CSS, WebSocket |
| **ISO** | General | Model OSI |

---

## Întrebări de verificare

1. Care sunt diferențele principale între LAN și WAN?
2. Ce rol are un switch comparativ cu un hub?
3. De ce modelul TCP/IP are mai puține niveluri decât OSI?
4. Ce se întâmplă cu un pachet când traversează un router?
5. Cum se calculează delay-ul total de transmisie?

---

## Ce am învățat

- Rețelele permit comunicarea și partajarea resurselor între dispozitive
- Clasificăm rețelele după dimensiune (PAN, LAN, MAN, WAN)
- Parametrii cheie sunt bandwidth, latență, jitter și packet loss
- Dispozitivele operează la diferite niveluri (hub L1, switch L2, router L3)
- Modelele OSI și TCP/IP descriu stratificarea protocoalelor
- Încapsularea adaugă headers la fiecare nivel

---

## Pregătire pentru seminar

Pentru seminarul din această săptămână:

1. **Instalați** mediul de lucru conform README.md din starterkit
2. **Verificați** că aveți acces la comenzile: `ping`, `ip`, `ss`, `nc`, `tshark`
3. **Rulați** `make verify` pentru validarea mediului
4. **Revedeți** conceptele: TCP vs UDP, adrese IP, porturi

---

## Bibliografie selectivă

| Autori | Titlu | Editura | An |
|--------|-------|---------|-----|
| J. Kurose, K. Ross | Computer Networking: A Top-Down Approach (8th ed.) | Pearson | 2021 |
| A. Tanenbaum, D. Wetherall | Computer Networks (5th ed.) | Pearson | 2011 |
| W.R. Stevens | TCP/IP Illustrated, Vol. 1 | Addison-Wesley | 1994 |

### Standarde și specificații

- RFC 791: Internet Protocol (IP)
- RFC 793: Transmission Control Protocol (TCP)
- IEEE 802.3: Ethernet Standard
- ISO/IEC 7498-1: OSI Basic Reference Model

---

*Revolvix&Hypotheticalandrei • Rețele de Calculatoare • ASE București*
