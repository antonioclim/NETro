# Rubrici de Evaluare – Săptămâna 6

## NAT/PAT, SDN, Analiza Traficului

---

## Structura evaluării săptămânale

| Componentă | Pondere | Fișier |
|------------|---------|--------|
| NAT/PAT Lab | 30% | `nat_output.txt` |
| Rutare (bonus) | 10% | `routing_output.txt` |
| SDN Lab | 40% | `sdn_output.txt` |
| Reflecție | 20% | `reflectie.txt` |

**Total:** 100% (+ 10% bonus)

---

## Livrabil A: NAT/PAT (30%)

### Criterii detaliate

| Criteriu | Puncte | Excelent (100%) | Satisfăcător (70%) | Insuficient (<50%) |
|----------|--------|-----------------|--------------------|--------------------|
| Comenzi corecte | 10p | Toate comenzile prezente cu output complet | Majoritatea comenzilor, output parțial | Comenzi lipsă sau output incomplet |
| Output ping | 5p | Ping-uri h1→h3 și h2→h3 cu succes | Un singur ping documentat | Fără output ping |
| Output iptables | 5p | Tabel NAT complet cu counters | Tabel prezent fără counters | Lipsă sau erori |
| Log NAT Observer | 5p | Minim 2 conexiuni cu IP:port vizibil | 1 conexiune documentată | Lipsă sau incomplet |
| Interpretare | 5p | Explicație clară traducere PAT, mapare, end-to-end | Explicație parțială | Fără interpretare sau greșeli conceptuale |

### Ce trebuie să conțină `nat_output.txt`

```
=== COMENZI NAT ===
[output ping h1 → h3]
[output ping h2 → h3]
[output iptables -t nat -L -n -v]
[log server NAT Observer]

=== INTERPRETARE ===
[minim 8 rânduri explicând:]
- Ce IP vede h3 pentru pachetele de la h1/h2?
- Ce se traduce și ce NU se traduce?
- De ce e nevoie de mapare bidirecțională?
- Ce se pierde din perspectiva end-to-end?
```

---

## Livrabil B: Rutare statică (10% BONUS)

### Criterii

| Criteriu | Puncte | Descriere |
|----------|--------|-----------|
| Traceroute înainte | 3p | Output cu calea inițială |
| Comenzi modificare | 4p | Comenzile folosite, corecte |
| Traceroute după | 3p | Output cu noua cale (diferită) |

---

## Livrabil C: SDN (40%)

### Criterii detaliate

| Criteriu | Puncte | Excelent (100%) | Satisfăcător (70%) | Insuficient (<50%) |
|----------|--------|-----------------|--------------------|--------------------|
| Test ping h1↔h2 | 5p | Output complet cu succes | Output prezent | Lipsă |
| Test ping h1→h3 | 5p | Output cu 100% loss (policy funcționează) | Output prezent | Lipsă sau policy nefuncțională |
| Flow table înainte | 10p | dump-flows complet, formatat | Prezent dar incomplet | Lipsă sau erori |
| Flow table după | 10p | dump-flows după modificare, diferențe vizibile | Prezent | Lipsă |
| Log controller | 5p | Minim 10 linii relevante (packet_in, flow install) | 5-9 linii | <5 linii |
| Interpretare | 5p | Explicație control/data plane, flow rules, table-miss | Explicație parțială | Fără interpretare |

### Ce trebuie să conțină `sdn_output.txt`

```
=== TESTE PING ===
[h1 ping 10.0.10.2 - succes]
[h1 ping 10.0.10.3 - timeout]

=== FLOW TABLE ÎNAINTE ===
[ovs-ofctl dump-flows s1]

=== FLOW TABLE DUPĂ MODIFICARE ===
[ovs-ofctl dump-flows s1 după ALLOW_UDP_TO_H3=True]

=== LOG CONTROLLER ===
[minim 10 linii relevante]

=== INTERPRETARE ===
[minim 10 rânduri explicând:]
- Cum se vede politica h1↔h2 în flow table?
- Ce diferențiază allow de drop? (actions)
- Rolul table-miss
- Separarea control/data plane
- De ce primul pachet e mai lent?
```

---

## Livrabil D: Reflecție (20%)

### Criterii

| Întrebare | Puncte | Ce se evaluează |
|-----------|--------|-----------------|
| NAT și end-to-end | 7p | Înțelegerea compromisurilor NAT |
| Automatizare | 7p | Comparație iptables vs OpenFlow |
| Troubleshooting | 6p | Metodologie debugging |

### Răspunsuri de referință (pentru evaluator)

**1. NAT și end-to-end:**
- NAT "încalcă" end-to-end prin modificarea adreselor în tranzit
- Aplicații P2P, VoIP, gaming sunt afectate
- Port forwarding necesar pentru conexiuni inbound
- Răspuns bun: menționează cel puțin 2 aplicații afectate și explică de ce

**2. Automatizare:**
- iptables: scripturi shell, persistent, dar greu de orchestrat
- OpenFlow: API programatice, vizibilitate centralizată, mai ușor de integrat în CI/CD
- Răspuns bun: argumentează cu exemple concrete

**3. Troubleshooting:**
- NAT: `iptables -L`, `conntrack`, `tcpdump`, verificare routing
- SDN: `ovs-ofctl dump-flows`, loguri controller, `tcpdump`
- Răspuns bun: menționează cel puțin 3 instrumente per caz

---

## Legătura cu proiectul de echipă

### Contribuția săptămânii 6

**Artefact:** Modul de monitoring rețea

**Cerințe:**
1. Script Python care detectează gateway-ul prin ARP
2. Funcție de verificare conectivitate (ICMP ping)
3. Logging traduceri NAT observate (opțional)

**Integrare:**
- Se adaugă la repo-ul de proiect în `/monitoring/`
- Se documentează în README
- Se demonstrează funcționalitatea la prezentare

### Punctaj proiect

| Componentă S6 | Puncte din proiect |
|---------------|-------------------|
| Modul funcțional | 5p |
| Documentație | 2p |
| Integrare corectă | 3p |

---

## Penalizări

| Situație | Penalizare |
|----------|------------|
| Predare cu întârziere (1-24h) | -10% |
| Predare cu întârziere (24-48h) | -25% |
| Predare după 48h | Nu se acceptă |
| Plagiat/copiere | 0 puncte + raportare |
| Fișiere corupte/nelizibile | Se solicită retrimite în 24h |

---

## Feedback standard

### Pentru livrabile excelente
"Foarte bine! Comenzile sunt complete, interpretările demonstrează înțelegere profundă a conceptelor. Observațiile despre [specific] sunt deosebit de pertinente."

### Pentru livrabile satisfăcătoare
"Bine. Comenzile sunt prezente, dar interpretarea ar putea fi mai detaliată. Sugestie: explicați mai clar [specific concept]."

### Pentru livrabile insuficiente
"Necesită îmbunătățiri. Lipsesc [specific elements]. Recomand revizuirea materialelor despre [topic] și retrimite până la [deadline]."

---

*Revolvix&Hypotheticalandrei*
