# Soluții Exerciții — Săptămâna 5

> **DOCUMENT CONFIDENȚIAL**
> Doar pentru uz intern al cadrului didactic.
> Nu se distribuie studenților înainte de termenul limită.

---

## Exercițiul S5.1 — Analiză CIDR (Nivel de bază)

**Enunț:** Dată fiind adresa `10.45.128.200/18`, calculați manual și verificați cu Python.

### Soluție detaliată

**Pas 1: Conversia prefixului în mască**
```
/18 → 11111111.11111111.11000000.00000000 = 255.255.192.0
```

**Pas 2: Calculul adresei de rețea (AND)**
```
10.45.128.200 = 00001010.00101101.10000000.11001000
255.255.192.0 = 11111111.11111111.11000000.00000000
────────────────────────────────────────────────────
Rețea         = 00001010.00101101.10000000.00000000 = 10.45.128.0
```

**Pas 3: Calculul broadcast**
```
Wildcard: 0.0.63.255
Broadcast = 10.45.128.0 OR 0.0.63.255 = 10.45.191.255
```

**Pas 4: Intervalul de gazde**
```
Prima gazdă:  10.45.128.1
Ultima gazdă: 10.45.191.254
Total gazde:  2^(32-18) - 2 = 16384 - 2 = 16382
```

**Verificare:**
```bash
python ex_5_01_cidr_flsm.py analyze 10.45.128.200/18
```

---

## Exercițiul S5.2 — FLSM (Nivel intermediar)

**Enunț:** Rețeaua `172.30.0.0/20` împărțită în 32 subrețele egale.

### Soluție

**Calculul biților împrumutați:**
```
32 subrețele → log₂(32) = 5 biți împrumutați
Prefix nou: /20 + 5 = /25
```

**Gazde per subrețea:**
```
2^(32-25) - 2 = 128 - 2 = 126 gazde
```

**Primele 5 subrețele:**

| # | Rețea           | Prima gazdă      | Ultima gazdă      | Broadcast        |
|---|-----------------|------------------|-------------------|------------------|
| 0 | 172.30.0.0/25   | 172.30.0.1       | 172.30.0.126      | 172.30.0.127     |
| 1 | 172.30.0.128/25 | 172.30.0.129     | 172.30.0.254      | 172.30.0.255     |
| 2 | 172.30.1.0/25   | 172.30.1.1       | 172.30.1.126      | 172.30.1.127     |
| 3 | 172.30.1.128/25 | 172.30.1.129     | 172.30.1.254      | 172.30.1.255     |
| 4 | 172.30.2.0/25   | 172.30.2.1       | 172.30.2.126      | 172.30.2.127     |

**Verificare:**
```bash
python ex_5_01_cidr_flsm.py flsm 172.30.0.0/20 32
```

---

## Exercițiul S5.3 — VLSM (Nivel intermediar)

**Enunț:** Plan VLSM pentru `192.168.50.0/24` cu cerințele:
- Departament A: 60 gazde
- Departament B: 28 gazde
- Departament C: 14 gazde
- Departament D: 5 gazde
- 3 linkuri point-to-point

### Soluție

**Pas 1: Sortare descrescătoare**
```
60, 28, 14, 5, 2, 2, 2
```

**Pas 2: Alocare secvențială**

| Cerință | Prefix | Gazde disp. | Rețea alocată         | Eficiență |
|---------|--------|-------------|------------------------|-----------|
| 60      | /26    | 62          | 192.168.50.0/26        | 96.8%     |
| 28      | /27    | 30          | 192.168.50.64/27       | 93.3%     |
| 14      | /28    | 14          | 192.168.50.96/28       | 100%      |
| 5       | /29    | 6           | 192.168.50.112/29      | 83.3%     |
| 2       | /30    | 2           | 192.168.50.120/30      | 100%      |
| 2       | /30    | 2           | 192.168.50.124/30      | 100%      |
| 2       | /30    | 2           | 192.168.50.128/30      | 100%      |

**Pas 3: Calculul eficienței**
```
Gazde necesare: 60 + 28 + 14 + 5 + 2 + 2 + 2 = 113
Gazde alocate:  62 + 30 + 14 + 6 + 2 + 2 + 2 = 118
Eficiență: 113/118 = 95.8%
```

**Spațiu rămas:** 192.168.50.132/26 (122 adrese)

**Verificare:**
```bash
python ex_5_02_vlsm_ipv6.py vlsm 192.168.50.0/24 60 28 14 5 2 2 2
```

---

## Exercițiul S5.4 — IPv6 Comprimare (Nivel intermediar)

**Enunț:** Comprimați următoarele adrese IPv6.

### Soluții

**1. `2001:0db8:85a3:0000:0000:8a2e:0370:7334`**
```
Pas 1: Eliminare zerouri de început
2001:db8:85a3:0:0:8a2e:370:7334

Pas 2: Nu există secvență lungă de zerouri consecutive
Răspuns: 2001:db8:85a3:0:0:8a2e:370:7334
       sau: 2001:db8:85a3::8a2e:370:7334
```

**2. `fe80:0000:0000:0000:0000:0000:0000:0001`**
```
Pas 1: fe80:0:0:0:0:0:0:1
Pas 2: fe80::1
Răspuns: fe80::1
```

**3. `0000:0000:0000:0000:0000:0000:0000:0001`**
```
Pas 1: 0:0:0:0:0:0:0:1
Pas 2: ::1
Răspuns: ::1 (adresa loopback IPv6)
```

---

## Exercițiul S5.5 — IPv6 Expandare (Nivel intermediar)

**Enunț:** Expandați următoarele adrese IPv6 comprimate.

### Soluții

**1. `2001:db8::1`**
```
:: înlocuiește 6 grupuri de zerouri
Răspuns: 2001:0db8:0000:0000:0000:0000:0000:0001
```

**2. `::ffff:192.168.1.1`**
```
Aceasta este o adresă IPv4-mapped
192.168.1.1 = c0.a8.01.01 în hex
Răspuns: 0000:0000:0000:0000:0000:ffff:c0a8:0101
```

**3. `ff02::2`**
```
:: înlocuiește 6 grupuri de zerouri
Răspuns: ff02:0000:0000:0000:0000:0000:0000:0002
(Adresa multicast all-routers link-local)
```

---

## Exercițiul S5.6 — Challenge: Plan IPv6

**Enunț:** Proiectați plan pentru `2001:db8:abcd::/48` cu 4 subrețele /64 + spațiu pentru 12 viitoare.

### Soluție

**Analiză:**
- Prefix /48 permite 2^16 = 65536 subrețele /64
- Necesare acum: 4
- Necesare viitor: 12
- Total rezervat: 16 (primele)

**Plan de numerotare:**

| Departament | Subrețea /64              | Stare      |
|-------------|---------------------------|------------|
| IT          | 2001:db8:abcd:0000::/64   | Activă     |
| HR          | 2001:db8:abcd:0001::/64   | Activă     |
| Finance     | 2001:db8:abcd:0002::/64   | Activă     |
| Operations  | 2001:db8:abcd:0003::/64   | Activă     |
| Rezervată 1 | 2001:db8:abcd:0004::/64   | Planificată|
| ...         | ...                       | ...        |
| Rezervată 12| 2001:db8:abcd:000f::/64   | Planificată|

**Schemă:**
```
2001:db8:abcd:0000::/52  ← Bloc rezervat departamente (16 /64)
2001:db8:abcd:0010::/52  ← Disponibil pentru proiecte
2001:db8:abcd:0100::/56  ← Disponibil pentru servere
...
```

**Verificare:**
```bash
python ex_5_02_vlsm_ipv6.py ipv6-subnets 2001:db8:abcd::/48 16
```

---

## Criterii de evaluare

| Exercițiu | Punctaj max | Criterii principale |
|-----------|-------------|---------------------|
| S5.1      | 10          | Toți parametrii corecți |
| S5.2      | 10          | Prefix corect + primele 5 subrețele |
| S5.3      | 15          | Plan complet + eficiență calculată |
| S5.4      | 10          | Toate 3 comprimate corect |
| S5.5      | 10          | Toate 3 expandate corect |
| S5.6      | 15          | Plan coerent + justificare |

**Total:** 70 puncte

---

*Document de uz intern — Rețele de calculatoare, ASE-CSIE*
