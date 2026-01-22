# Exerciții Variate — Săptămâna 5

Aceste exerciții completează exercițiile de cod din seminar și laborator. Nu toate implică scrierea de cod — unele testează înțelegerea prin reordonare, urmărire sau debugging.

---

## Exercițiu Parsons #1: Pașii algoritmului VLSM

### Instrucțiuni
Reordonează pașii de mai jos în ordinea corectă pentru a aplica algoritmul VLSM.

### Pași (amestecați)

```
[ ] A. Calculează prefixul necesar pentru fiecare cerință: /prefix = 32 - ⌈log₂(hosts + 2)⌉
[ ] B. Sortează cerințele descrescător după numărul de hosturi
[ ] C. Alocă primul bloc liber cu prefixul calculat
[ ] D. Marchează blocul ca utilizat și treci la următoarea cerință
[ ] E. Calculează eficiența: hosturi_folosiți / adrese_alocate × 100%
[ ] F. Verifică dacă spațiul total e suficient pentru toate cerințele
```

### Soluție

**Ordine corectă:** B → F → A → C → D → E

**Explicație:**
1. **B** — Întâi sortezi descrescător (OBLIGATORIU pentru a evita fragmentarea)
2. **F** — Verifici că ai suficient spațiu total (sumă cerințe vs. capacitate rețea)
3. **A** — Pentru fiecare cerință, calculezi prefixul minim
4. **C** — Alocarea efectivă a blocului
5. **D** — Marchezi și treci la următorul
6. **E** — La final, calculezi eficiența pentru documentare

---

## Exercițiu Parsons #2: Calculul adresei de rețea

### Instrucțiuni
Reordonează pașii pentru a calcula adresa de rețea pornind de la `192.168.10.50/26`.

### Pași (amestecați)

```
[ ] A. Rezultat: 192.168.10.0 este adresa de rețea
[ ] B. Convertește IP-ul în binar: 11000000.10101000.00001010.00110010
[ ] C. Aplică operația AND bit cu bit între IP și mască
[ ] D. Convertește masca în binar: 11111111.11111111.11111111.11000000
[ ] E. Determină masca de rețea pentru /26: 255.255.255.192
```

### Soluție

**Ordine corectă:** E → B → D → C → A

**Explicație:**
1. **E** — Prefixul /26 → determini masca zecimală (255.255.255.192)
2. **B** — Convertești IP-ul în binar
3. **D** — Convertești și masca în binar (sau știi direct că /26 = 11...11000000)
4. **C** — Aplici AND: `IP AND Mască = Rețea`
5. **A** — Interpretezi rezultatul binar ca IP zecimal

---

## Exercițiu Trace: Urmărește pachetul

### Scenariu
Topologie cu 2 subrețele conectate printr-un router:
- **Subrețea A:** 10.0.1.0/24, host h1 la 10.0.1.10
- **Subrețea B:** 10.0.2.0/24, host h2 la 10.0.2.10  
- **Router r1:** eth0=10.0.1.1, eth1=10.0.2.1
- **Gateway h1:** 10.0.1.1
- **Gateway h2:** 10.0.2.1

### Acțiune
`h1` execută comanda: `ping -c 1 10.0.2.10`

### Completează tabelul

Urmărește pachetul pas cu pas și completează valorile lipsă:

| Pas | Dispozitiv | Acțiune | IP Src | IP Dst | TTL |
|-----|------------|---------|--------|--------|-----|
| 1 | h1 | Trimite ICMP Echo Request | ? | ? | ? |
| 2 | r1 | Primește pe eth0, consultă tabela de rutare | — | — | — |
| 3 | r1 | Trimite pe eth1 către h2 | ? | ? | ? |
| 4 | h2 | Primește, trimite ICMP Echo Reply | ? | ? | ? |
| 5 | r1 | Primește reply pe eth1, rutează | — | — | — |
| 6 | r1 | Trimite reply pe eth0 către h1 | ? | ? | ? |
| 7 | h1 | Primește reply | — | — | — |

### Soluție

| Pas | IP Src | IP Dst | TTL |
|-----|--------|--------|-----|
| 1 | 10.0.1.10 | 10.0.2.10 | 64 |
| 3 | 10.0.1.10 | 10.0.2.10 | 63 |
| 4 | 10.0.2.10 | 10.0.1.10 | 64 |
| 6 | 10.0.2.10 | 10.0.1.10 | 63 |

**Observații cheie:**
- IP-urile sursă și destinație NU se schimbă la rutare (rămân end-to-end)
- TTL scade cu 1 la fiecare hop (router)
- Reply-ul are TTL nou (64), setat de h2
- Adresele MAC se schimbă la fiecare segment (dar nu le-am cerut aici)

---

## Exercițiu Debugging: Găsește eroarea

### Scenariu
Topologia funcționa ieri, azi ping-ul între h1 și h2 eșuează.

### Configurație curentă (cu o eroare ascunsă)

```
h1:
  IP: 10.0.1.10/24
  Gateway: 10.0.1.1

h2:
  IP: 10.0.2.10/24
  Gateway: 10.0.2.1

r1-eth0: 10.0.1.1/24
r1-eth1: 10.0.2.2/24    ← VERIFICĂ ASTA
```

### Simptom
```bash
h1$ ping 10.0.2.10
PING 10.0.2.10 (10.0.2.10) 56(84) bytes of data.
From 10.0.1.10 icmp_seq=1 Destination Host Unreachable
From 10.0.1.10 icmp_seq=2 Destination Host Unreachable
```

### Întrebări

1. Care este problema?
2. De ce ping-ul eșuează cu "Destination Host Unreachable"?
3. Cum rezolvi problema? (două soluții posibile)

### Soluție

**Problema:** r1-eth1 are IP `10.0.2.2` dar h2 are gateway configurat `10.0.2.1`.

**De ce eșuează:**
- h1 trimite pachetul către r1 (gateway funcționează)
- r1 rutează pachetul către subrețeaua 10.0.2.0/24 prin eth1
- Pachetul ajunge la h2
- h2 vrea să răspundă, trimite către gateway-ul său (10.0.2.1)
- DAR 10.0.2.1 nu există! r1-eth1 e pe 10.0.2.2
- h2 face ARP pentru 10.0.2.1, nu primește răspuns
- Reply-ul nu poate fi trimis → "Destination Host Unreachable"

**Soluții:**
1. Schimbă IP-ul lui r1-eth1 în 10.0.2.1:
   ```bash
   r1$ ip addr del 10.0.2.2/24 dev r1-eth1
   r1$ ip addr add 10.0.2.1/24 dev r1-eth1
   ```

2. SAU schimbă gateway-ul lui h2 în 10.0.2.2:
   ```bash
   h2$ ip route del default
   h2$ ip route add default via 10.0.2.2
   ```

**Lecție:** Gateway-ul unui host TREBUIE să fie o adresă IP care există pe acel segment de rețea.

---

## Exercițiu Code Reading: Ce face acest cod?

### Cod de analizat

```python
def mystery(ip_cidr):
    from ipaddress import ip_network
    net = ip_network(ip_cidr, strict=False)
    return list(net.hosts())[-1]
```

### Întrebări

1. Ce returnează `mystery("192.168.1.0/24")`?
2. De ce folosește `strict=False`?
3. Ce se întâmplă dacă apelezi `mystery("192.168.1.0/32")`?
4. Dar `mystery("192.168.1.100/24")`?

### Soluție

**1. Ce returnează pentru /24?**
```python
>>> mystery("192.168.1.0/24")
IPv4Address('192.168.1.254')
```
Returnează **ultimul host valid** din subrețea (înainte de broadcast).

**2. De ce `strict=False`?**
Permite să pasezi o adresă de host cu prefix, nu doar adresa de rețea exactă.
- Cu `strict=True`: `ip_network("192.168.1.100/24")` → **ValueError** (100 nu e adresa de rețea)
- Cu `strict=False`: Acceptă și calculează automat rețeaua (192.168.1.0/24)

**3. Ce se întâmplă cu /32?**
```python
>>> mystery("192.168.1.0/32")
# IndexError: list index out of range
```
O rețea /32 nu are hosturi valizi (e o singură adresă). `list(net.hosts())` returnează listă goală, și `[-1]` pe listă goală dă eroare.

**4. Dar cu "192.168.1.100/24"?**
```python
>>> mystery("192.168.1.100/24")
IPv4Address('192.168.1.254')
```
Funcționează identic — `strict=False` ignoră că 100 nu e adresa de rețea și calculează corect.

---

## Exercițiu Code Reading #2: Validare prefix

### Cod de analizat

```python
def validate_hosts(prefix, required_hosts):
    available = (2 ** (32 - prefix)) - 2
    return available >= required_hosts

def find_prefix(required_hosts):
    for p in range(30, 7, -1):  # de la /30 la /8
        if validate_hosts(p, required_hosts):
            return p
    return None
```

### Întrebări

1. Ce returnează `find_prefix(100)`?
2. Ce returnează `find_prefix(2)`?
3. De ce bucla merge de la 30 la 8 (descrescător)?
4. Ce returnează `find_prefix(20000000)`?

### Soluție

**1. find_prefix(100)?**
```python
>>> find_prefix(100)
25
```
/25 oferă 126 hosturi (2^7 - 2), primul prefix care acoperă 100.

**2. find_prefix(2)?**
```python
>>> find_prefix(2)
30
```
/30 oferă exact 2 hosturi — perfect pentru link-uri point-to-point.

**3. De ce descrescător?**
Căutăm cel mai mic prefix (adică cel mai mare număr) care încă satisface cerința. Mergând de la /30 spre /8, primul care returnează `True` e prefixul optim (cel mai mic bloc care încape).

**4. find_prefix(20000000)?**
```python
>>> find_prefix(20000000)
None
```
Nici /8 (16 milioane hosturi) nu e suficient. Funcția returnează `None`.

---

## Exercițiu de sinteză: Proiectează și validează

### Scenariu
Compania ABC are rețeaua `172.20.0.0/22` și necesită:
- Sediu central: 400 hosturi
- Sucursală Nord: 100 hosturi
- Sucursală Sud: 50 hosturi
- Datacenter: 200 hosturi
- 4 link-uri WAN (câte 2 hosturi fiecare)

### Cerințe

1. Verifică dacă rețeaua are suficient spațiu
2. Proiectează schema VLSM (sortează, alocă, documentează)
3. Calculează eficiența totală
4. Identifică spațiul rămas pentru extindere

### Soluție

**1. Verificare spațiu:**
- /22 oferă: 2^(32-22) - 2 = 1022 hosturi
- Total necesar: 400 + 100 + 50 + 200 + 4×2 = 758 hosturi
- ✅ Încape (758 < 1022)

**2. Schema VLSM:**

| Departament | Necesar | Prefix | Adrese | Rețea alocată | Interval hosturi |
|-------------|---------|--------|--------|---------------|------------------|
| Sediu central | 400 | /23 | 510 | 172.20.0.0/23 | .1 – .510 |
| Datacenter | 200 | /24 | 254 | 172.20.2.0/24 | .1 – .254 |
| Sucursală Nord | 100 | /25 | 126 | 172.20.3.0/25 | .1 – .126 |
| Sucursală Sud | 50 | /26 | 62 | 172.20.3.128/26 | .129 – .190 |
| WAN 1 | 2 | /30 | 2 | 172.20.3.192/30 | .193 – .194 |
| WAN 2 | 2 | /30 | 2 | 172.20.3.196/30 | .197 – .198 |
| WAN 3 | 2 | /30 | 2 | 172.20.3.200/30 | .201 – .202 |
| WAN 4 | 2 | /30 | 2 | 172.20.3.204/30 | .205 – .206 |

**3. Eficiență:**
- Total alocat: 512 + 256 + 128 + 64 + 4×4 = 976 adrese
- Total necesar: 758 hosturi
- Eficiență: 758/976 = **77.7%**

**4. Spațiu rămas:**
- 172.20.3.208/28 până la 172.20.3.255 → aproximativ 48 adrese libere
- Suficient pentru încă 2-3 link-uri WAN sau o subrețea mică

---

*Exerciții variate pentru Săptămâna 5 — Rețele de calculatoare, ASE-CSIE*
