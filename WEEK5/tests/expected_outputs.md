# Output-uri Așteptate — Referință pentru Verificare

Acest document conține output-urile de referință pentru principalele comenzi din starterkit.

---

## 1. CIDR Analyze

### Comandă
```bash
python ex_5_01_cidr_flsm.py analyze 192.168.1.100/24
```

### Output așteptat
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

---

## 2. FLSM Split

### Comandă
```bash
python ex_5_01_cidr_flsm.py flsm 10.0.0.0/8 4
```

### Output așteptat (sumar)
```
Partiționare FLSM: 10.0.0.0/8 → 4 subrețele
Prefix nou: /10 (biți împrumutați: 2)
Gazde per subrețea: 4,194,302

Subrețele:
  #0: 10.0.0.0/10
  #1: 10.64.0.0/10
  #2: 10.128.0.0/10
  #3: 10.192.0.0/10
```

---

## 3. VLSM Allocate

### Comandă
```bash
python ex_5_02_vlsm_ipv6.py vlsm 192.168.0.0/24 100 50 20 2
```

### Output așteptat (sumar)
```
Plan VLSM pentru 192.168.0.0/24
Cerințe: [100, 50, 20, 2]

Alocare:
  100 gazde → 192.168.0.0/25   (126 disponibile, 79.4% utilizare)
   50 gazde → 192.168.0.128/26 (62 disponibile, 80.6% utilizare)
   20 gazde → 192.168.0.192/27 (30 disponibile, 66.7% utilizare)
    2 gazde → 192.168.0.224/30 (2 disponibile, 100.0% utilizare)

Eficiență totală: 172/220 = 78.2%
```

---

## 4. IPv6 Compress

### Comandă
```bash
python ex_5_02_vlsm_ipv6.py ipv6 2001:0db8:0000:0000:0000:0000:0000:0001
```

### Output așteptat
```
Original:  2001:0db8:0000:0000:0000:0000:0000:0001
Comprimat: 2001:db8::1
Tip:       Global Unicast
```

---

## 5. IPv6 Expand

### Comandă
```bash
python ex_5_02_vlsm_ipv6.py ipv6-expand 2001:db8::1
```

### Output așteptat
```
Comprimat: 2001:db8::1
Expandat:  2001:0db8:0000:0000:0000:0000:0000:0001
```

---

## 6. Mininet Base Topology Test

### Comandă
```bash
sudo python topo_5_base.py --test
```

### Output așteptat
```
*** Construire topologie bază ***
*** Adăugare router și hosturi ***
*** Creare linkuri ***
*** Pornire rețea ***
*** Rulare test conectivitate (pingall) ***
h1 -> h2
h2 -> h1
*** Results: 0% dropped (2/2 received)
*** TEST REUȘIT: Toate nodurile comunică! ***
*** Oprire rețea ***
```

---

## 7. Quiz Generator (Batch Mode)

### Comandă
```bash
python ex_5_03_quiz_generator.py --batch --count 3
```

### Output așteptat (exemplu, variază aleator)
```
=== QUIZ: 3 Întrebări ===

Întrebarea 1 [CIDR]:
  Pentru rețeaua 172.16.50.0/21, care este adresa de broadcast?
  Răspuns: 172.16.55.255

Întrebarea 2 [FLSM]:
  Dacă împărțim 10.0.0.0/8 în 16 subrețele, care este noul prefix?
  Răspuns: /12

Întrebarea 3 [IPv6]:
  Comprimați: 2001:0db8:0000:0000:0000:0000:0000:0001
  Răspuns: 2001:db8::1
```

---

## Notă

Output-urile exacte pot varia ușor în funcție de:
- Versiunea Python
- Configurația terminalului (culori)
- Opțiunile specifice folosite

Elementele cheie care trebuie verificate sunt valorile numerice și adresele IP.

---

*Document de referință — Starterkit Săptămâna 5*
