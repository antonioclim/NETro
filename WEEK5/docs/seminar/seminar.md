# Seminar 5: Adresare și Rutare — Subnetting, IPv4/IPv6

## 1. Obiective

### Ce vei ști să faci după seminar
- Calculezi parametrii critici ai oricărei rețele IPv4 (adresă de rețea, broadcast, interval gazde)
- Împarți spațiul de adrese folosind FLSM și VLSM
- Comprimați și expandezi adrese IPv6
- Configurezi rutare statică într-un simulator (Mininet)

### De ce contează

Dacă nu știi să faci subnetting, vei pierde ore întregi debugând probleme de conectivitate care se rezolvă în 5 minute cu o schemă corectă de adresare. În cloud sau microservicii, prefixul greșit înseamnă că aplicația nu scalează sau că traficul ajunge unde nu trebuie.

---

## 2. Ce trebuie să știi deja

### Cunoștințe necesare
- Reprezentarea binară a numerelor (conversii bază 10 ↔ bază 2)
- Operații pe biți: AND, OR, NOT
- Bazele stivei TCP/IP (seminarele 1–4)
- Linia de comandă Linux

### Recapitulare rapidă

**Conversia zecimal-binar:** Fiecare octet din adresa IPv4 se exprimă pe 8 biți.

| Zecimal | Binar |
|---------|-------|
| 192 | 1100 0000 |
| 168 | 1010 1000 |
| 255 | 1111 1111 |
| 0 | 0000 0000 |

**Formula numărului de gazde:** Pentru prefix `/n`, hosturi disponibile = `2^(32-n) - 2` (scădem adresa de rețea și broadcast).

---

## 3. Organizare și parcurs practic

### Mod de lucru: Pair Programming

Pentru exercițiile practice, lucrați în perechi:
- **Driver:** Scrie codul/comenzile, controlează tastatura
- **Navigator:** Verifică, sugerează, consultă documentația
- **Schimbare roluri:** La fiecare 10-15 minute sau la fiecare parte nouă

De ce pair programming? Erorile se prind mai repede, înveți din modul de gândire al colegului, și discuțiile clarifică conceptele.

> **📋 Material suplimentar:** Vezi `docs/peer_instruction_week5.md` pentru întrebări de discuție în grupuri și `docs/exercitii_variate_week5.md` pentru exerciții Parsons și debugging.

---

### Partea A: Analiza CIDR fundamentală

**Scenariu:** Primiți adresa `172.16.50.12/21`. Determinați toți parametrii relevanți.

> **🎯 Predicție:** Înainte să calculezi, estimează: cam câte hosturi crezi că are o rețea /21? Notează răspunsul.

**Pas 1:** Convertirea prefixului în mască de rețea.

```
Prefix /21 → primii 21 biți sunt 1, restul 0
11111111.11111111.11111000.00000000 = 255.255.248.0
```

**Pas 2:** Calculul adresei de rețea (operație AND bit cu bit).

```
172.16.50.12  = 10101100.00010000.00110010.00001100
255.255.248.0 = 11111111.11111111.11111000.00000000
────────────────────────────────────────────────────
Rețea         = 10101100.00010000.00110000.00000000 = 172.16.48.0
```

**Pas 3:** Calculul adresei de broadcast (inversarea biților de host).

```
Wildcard mask: 0.0.7.255 (inversul măștii)
Broadcast = Rețea OR Wildcard = 172.16.48.0 | 0.0.7.255 = 172.16.55.255
```

**Pas 4:** Intervalul de gazde valide.

```
Prima gazdă:  172.16.48.1
Ultima gazdă: 172.16.55.254
Total gazde:  2^(32-21) - 2 = 2046
```

> **Verificare predicție:** Ai estimat în jur de 2000? Bravo! Dacă ai zis 2048, ai uitat să scazi 2.

**Verificare cu Python:**

```bash
cd python/exercises
python ex_5_01_cidr_flsm.py analyze 172.16.50.12/21 --verbose
```

> **🎯 Predicție:** Ce va afișa scriptul pentru "Total gazde"? Ar trebui să fie exact ce ai calculat manual.

---

### Partea B: Partiționare FLSM (Fixed-Length Subnet Mask)

**Scenariu:** Rețeaua `10.20.0.0/16` trebuie împărțită în 8 subrețele egale.

> **🎯 Predicție:** Câți biți trebuie să împrumuți pentru 8 subrețele? Ce prefix nou va rezulta?

**Analiză:**
- Pentru 8 subrețele → împrumutăm 3 biți (2³ = 8)
- Prefix nou: /16 + 3 = /19
- Gazde per subrețea: 2^(32-19) - 2 = 8190

**Calculul subrețelelor:**

| Subrețea | Adresă rețea | Interval gazde | Broadcast |
|----------|--------------|----------------|-----------|
| 0 | 10.20.0.0/19 | 10.20.0.1 – 10.20.31.254 | 10.20.31.255 |
| 1 | 10.20.32.0/19 | 10.20.32.1 – 10.20.63.254 | 10.20.63.255 |
| 2 | 10.20.64.0/19 | 10.20.64.1 – 10.20.95.254 | 10.20.95.255 |
| 3 | 10.20.96.0/19 | 10.20.96.1 – 10.20.127.254 | 10.20.127.255 |
| 4 | 10.20.128.0/19 | 10.20.128.1 – 10.20.159.254 | 10.20.159.255 |
| 5 | 10.20.160.0/19 | 10.20.160.1 – 10.20.191.254 | 10.20.191.255 |
| 6 | 10.20.192.0/19 | 10.20.192.1 – 10.20.223.254 | 10.20.223.255 |
| 7 | 10.20.224.0/19 | 10.20.224.1 – 10.20.255.254 | 10.20.255.255 |

**Verificare cu Python:**

```bash
python ex_5_01_cidr_flsm.py flsm 10.20.0.0/16 8
```

---

### Partea C: Partiționare VLSM (Variable-Length Subnet Mask)

**Scenariu:** Proiectați un plan de adresare pentru compania TechCorp:

| Departament | Gazde necesare |
|-------------|----------------|
| R&D | 120 |
| Sales | 55 |
| HR | 25 |
| Management | 12 |
| Link P2P (×2) | 2 (fiecare) |

**Rețea alocată:** `192.168.100.0/24` (254 gazde totale)

> **Pont din experiență:** Eu prefer să desenez pe hârtie schema înainte să o implementez în Python. Văd mai clar unde se termină un bloc și unde începe următorul. Încearcă și tu — ia 2 minute să schițezi pe foaie.

**Algoritm VLSM:**
1. Sortare descrescătoare după numărul de gazde (OBLIGATORIU!)
2. Alocare secvențială începând cu cea mai mare cerință
3. Selectarea celui mai mic prefix care acoperă necesarul + 2

> **🎯 Predicție:** Ce prefix vei aloca pentru R&D (120 gazde)? Dar pentru link-urile P2P?

**Calcul detaliat:**

| Departament | Necesar | Prefix | Adrese | Utilizare | Rețea alocată |
|-------------|---------|--------|--------|-----------|---------------|
| R&D | 120 | /25 | 126 | 95.2% | 192.168.100.0/25 |
| Sales | 55 | /26 | 62 | 88.7% | 192.168.100.128/26 |
| HR | 25 | /27 | 30 | 83.3% | 192.168.100.192/27 |
| Management | 12 | /28 | 14 | 85.7% | 192.168.100.224/28 |
| Link P2P 1 | 2 | /30 | 2 | 100% | 192.168.100.240/30 |
| Link P2P 2 | 2 | /30 | 2 | 100% | 192.168.100.244/30 |

**Eficiență globală:** 216 gazde necesare / 238 alocate = 90.8%

**Adrese rămase:** 192.168.100.248/29 (6 adrese libere pentru extindere)

**Verificare cu Python:**

```bash
python ex_5_02_vlsm_ipv6.py vlsm 192.168.100.0/24 120 55 25 12 2 2
```

> **🎯 Predicție:** Eficiența calculată de script va fi exact 90.8%? Rulează și verifică.

---

### Partea D: Adresare IPv6

**Scenariu:** Analizați și normalizați următoarele adrese IPv6.

**Adresa completă:**
```
2001:0db8:0000:0000:0000:0000:0000:0001
```

**Reguli de comprimare:**
1. Zero-urile de la începutul fiecărui grup se elimină
2. O singură secvență de grupuri consecutive de zerouri se înlocuiește cu `::`

> **🎯 Predicție:** Comprimă adresa de mai sus. Scrie răspunsul înainte să citești mai departe.

**Forme succesive:**
```
2001:0db8:0000:0000:0000:0000:0000:0001  → formă completă
2001:db8:0:0:0:0:0:1                     → eliminare zerouri de început
2001:db8::1                              → comprimare maximă
```

**Tipuri de adrese IPv6:**

| Tip | Prefix | Exemplu | Utilizare |
|-----|--------|---------|-----------|
| Global Unicast | 2000::/3 | 2001:db8:1234::5678 | Adrese rutabile Internet |
| Link-Local | fe80::/10 | fe80::1 | Comunicare pe segment local |
| Unique Local | fc00::/7 | fd00:1234::1 | Rețele private (analog RFC1918) |
| Loopback | ::1/128 | ::1 | Localhost |
| Multicast | ff00::/8 | ff02::1 | Difuzare selectivă |

**Verificare cu Python:**

```bash
python ex_5_02_vlsm_ipv6.py ipv6 2001:0db8:0000:0000:0000:0000:0000:0001
python ex_5_02_vlsm_ipv6.py ipv6-expand 2001:db8::1
python ex_5_02_vlsm_ipv6.py ipv6-types
```

---

### Partea E: Simulare în Mininet

**Scenariu:** Configurarea și testarea unei topologii cu două subrețele interconectate printr-un router.

#### Analogie: Routerul ca agent de circulație

Routerul e ca un polițist la o intersecție mare:
- Vede de unde vine pachetul (adresa sursă)
- Se uită în "instrucțiuni" (tabela de rutare)
- Indică pe ce stradă să o ia (interfața de ieșire)
- Ștampilează biletul (decrementează TTL)

Fără router, pachetele din subrețele diferite nu știu cum să ajungă unele la altele.

**Pas 1:** Pornirea topologiei de bază.

```bash
cd mininet/topologies
sudo python topo_5_base.py --cli
```

**Pas 2:** Explorarea configurației.

```
mininet> nodes
mininet> net
mininet> h1 ip addr
mininet> h2 ip addr
mininet> r1 ip route
```

**Pas 3:** Testarea conectivității.

> **🎯 Predicție:** Ping-ul de la h1 la h2 (10.0.2.10) va reuși? Gândește: ce condiții trebuie îndeplinite?

```
mininet> h1 ping -c 3 10.0.2.10
```

**Rezultat așteptat:**
```
PING 10.0.2.10 (10.0.2.10) 56(84) bytes of data.
64 bytes from 10.0.2.10: icmp_seq=1 ttl=63 time=0.523 ms
64 bytes from 10.0.2.10: icmp_seq=2 ttl=63 time=0.089 ms
64 bytes from 10.0.2.10: icmp_seq=3 ttl=63 time=0.082 ms
```

**Pas 4:** Capturarea și analiza traficului.

```
mininet> r1 tcpdump -i r1-eth0 -c 10 -n &
mininet> h1 ping -c 3 10.0.2.10
```

> **🎯 Predicție:** Ce TTL va avea pachetul când ajunge la h2? (Hint: a trecut prin câte routere?)

**Observații cheie:**
- TTL scade cu 1 la fiecare hop (64 → 63)
- Pachetele ICMP trec prin router
- Adresele MAC sunt diferite pe fiecare segment

**Pas 5:** Topologia extinsă cu VLSM.

```bash
sudo python topo_5_extended.py --cli --ipv6
```

---

## 4. Exerciții de consolidare

### Exercițiul S5.1 — Nivel de bază
Dată fiind adresa `10.45.128.200/18`, calculează manual:
- Adresa de rețea
- Adresa de broadcast
- Intervalul de gazde valide
- Numărul total de gazde

Apoi verifică cu scriptul Python.

### Exercițiul S5.2 — Nivel intermediar
Rețeaua `172.30.0.0/20` trebuie împărțită în 32 de subrețele egale. Determină:
- Noul prefix pentru fiecare subrețea
- Primele 5 subrețele cu intervalele lor de gazde
- Câte gazde suportă fiecare subrețea

### Exercițiul S5.3 — Nivel intermediar
Proiectează un plan VLSM pentru rețeaua `192.168.50.0/24`:
- Departamentul A: 60 gazde
- Departamentul B: 28 gazde
- Departamentul C: 14 gazde
- Departamentul D: 5 gazde
- 3 linkuri point-to-point

Calculează eficiența totală.

### Exercițiul S5.4 — Comprimare IPv6
Comprimă la forma minimă:
1. `2001:0db8:85a3:0000:0000:8a2e:0370:7334`
2. `fe80:0000:0000:0000:0000:0000:0000:0001`
3. `0000:0000:0000:0000:0000:0000:0000:0001`

### Exercițiul S5.5 — Expandare IPv6
Expandează complet:
1. `2001:db8::1`
2. `::ffff:192.168.1.1`
3. `ff02::2`

### Exercițiul S5.6 — Challenge
Organizația XYZ are prefixul IPv6 `2001:db8:abcd::/48`. Proiectează un plan care:
- Creează 4 subrețele /64 pentru departamente
- Rezervă spațiu pentru 12 subrețele viitoare
- Documentează schema de numerotare

---

## 5. Debugging și depanare

### Problemă: Ping între subrețele eșuează

**Simptome:** `Destination Host Unreachable` sau timeout

> **Atenție din practică:** Dacă ping-ul nu merge între subrețele, verifică ÎNTÂI `ip route` pe gazde și pe router. În 9 din 10 cazuri, problema e gateway-ul lipsă, nu altceva.

**Verificări:**

1. IP forwarding este activ pe router?
   ```bash
   cat /proc/sys/net/ipv4/ip_forward  # trebuie să fie 1
   ```

2. Rutele sunt configurate corect?
   ```bash
   ip route show
   ```

3. Interfețele au adrese corecte?
   ```bash
   ip addr show
   ```

### Problemă: Eroare la pornirea Mininet

**Simptome:** `Exception: Error creating interface pair`

**Soluție:**
```bash
sudo mn -c                    # cleanup
sudo service openvswitch-switch restart
```

### Problemă: Calculele VLSM nu se potrivesc

**Verificare:** Asigură-te că:
- Sortarea e descrescătoare după număr de gazde
- Prefixul selectat acoperă `necesarul + 2` (rețea + broadcast)
- Alocările nu se suprapun

---

## 6. Ce ai învățat

Acum poți:
- Calcula parametrii oricărei rețele IPv4 date în notație CIDR
- Proiecta scheme FLSM pentru cerințe uniforme
- Optimiza utilizarea spațiului de adrese cu VLSM
- Normaliza și comprima adrese IPv6
- Configura și testa rutare statică în Mininet

---

## 7. Legătura cu proiectul de echipă

**Artefact livrabil săptămâna 5:**
- Document de proiectare a schemei de adresare pentru infrastructura proiectului
- Minim 3 subrețele cu justificare pentru alegerea prefixurilor
- Topologie Mininet care demonstrează conectivitatea între subrețele

---

## 8. Bibliografie

### RFC-uri relevante
- RFC 4632 — CIDR: The Internet Address Assignment and Aggregation Plan
- RFC 6177 — IPv6 Address Assignment to End Sites
- RFC 5952 — A Recommendation for IPv6 Address Text Representation

### Resurse online
- Mininet Walkthrough: http://mininet.org/walkthrough/
- IPv6 Addressing Guide: https://www.ripe.net/publications/docs/ripe-631

---

*Material didactic ASE-CSIE — Rețele de calculatoare*
