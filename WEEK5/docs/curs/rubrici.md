# Rubrici de Evaluare — Săptămâna 5

## 1. Criterii pentru exercițiile de seminar

### Exerciții CIDR/FLSM (Ex. S5.1, S5.2)

| Criteriu | Punctaj | Descriere |
|----------|---------|-----------|
| Calculul adresei de rețea | 20% | Corectitudinea operației AND |
| Calculul broadcast | 20% | Corectitudinea inversării biților de host |
| Intervalul de gazde | 20% | Prima și ultima gazdă identificate corect |
| Numărul de gazde | 20% | Formula 2^(32-n)-2 aplicată corect |
| Documentarea pașilor | 20% | Explicarea metodei, nu doar rezultatul |

**Punctaj total:** 10 puncte per exercițiu

### Exerciții VLSM (Ex. S5.3)

| Criteriu | Punctaj | Descriere |
|----------|---------|-----------|
| Sortarea cerințelor | 15% | Ordine descrescătoare după număr de gazde |
| Selecția prefixurilor | 25% | Cel mai mic prefix care acoperă necesarul |
| Alocarea secvențială | 25% | Fără suprapuneri sau goluri neoptimizate |
| Calculul eficienței | 20% | Formula corectă: utilizate/alocate |
| Tabel complet | 15% | Toate câmpurile completate pentru fiecare subrețea |

**Punctaj total:** 15 puncte

### Exerciții IPv6 (Ex. S5.4, S5.5)

| Criteriu | Punctaj | Descriere |
|----------|---------|-----------|
| Comprimare corectă | 40% | Eliminarea zerourilor, utilizarea :: |
| Expandare corectă | 40% | Forma completă cu 8 grupuri de 4 cifre |
| Identificarea tipului | 20% | Global unicast, link-local, etc. |

**Punctaj total:** 10 puncte per exercițiu

---

## 2. Criterii pentru experimentele de laborator

### Topologia Mininet de bază

| Criteriu | Punctaj | Descriere |
|----------|---------|-----------|
| Pornire fără erori | 25% | Comanda `--cli` funcționează |
| Verificare configurație | 25% | `ip addr`, `ip route` afișate și interpretate |
| Test conectivitate | 30% | `ping` între subrețele reușit |
| Captură trafic | 20% | `tcpdump` rulat și output interpretat |

**Punctaj total:** 20 puncte

### Topologia VLSM extinsă

| Criteriu | Punctaj | Descriere |
|----------|---------|-----------|
| Pornire corectă | 20% | Toate cele 3 subrețele configurate |
| `pingall` reușit | 30% | 0% packet loss |
| Identificarea prefixurilor | 25% | Studenții recunosc /26, /28, /30 |
| IPv6 dual-stack (bonus) | 25% | `ping6` funcțional |

**Punctaj total:** 20 puncte (+5 bonus IPv6)

---

## 3. Criterii pentru raportul de laborator

| Secțiune | Punctaj | Cerințe |
|----------|---------|---------|
| Introducere | 10% | Obiective clare, context |
| Metodologie | 20% | Comenzile folosite, ordinea pașilor |
| Rezultate | 30% | Capturi de ecran/output-uri relevante |
| Analiză | 25% | Interpretarea rezultatelor, observații |
| Concluzii | 15% | Ce s-a învățat, dificultăți întâmpinate |

**Punctaj total:** 100 puncte (scalat la nota finală)

### Penalizări

| Motiv | Deducere |
|-------|----------|
| Lipsă capturi de ecran | -10% |
| Comenzi fără explicații | -10% |
| Copiere de la coleg | -50% până la -100% |
| Întârziere (per zi) | -5% |

---

## 4. Contribuția la proiectul de echipă

### Artefact livrabil Săptămâna 5
**Document de proiectare a schemei de adresare**

| Criteriu | Punctaj | Descriere |
|----------|---------|-----------|
| Minim 3 subrețele definite | 30% | Cu toate parametrii (rețea, prefix, interval) |
| Justificare alegere prefixuri | 25% | De ce aceste dimensiuni, FLSM vs VLSM |
| Topologie documentată | 25% | Diagramă sau descriere textuală |
| Funcționalitate Mininet | 20% | Topologie personalizată pornește fără erori |

**Punctaj total:** 15% din nota săptămânală a proiectului

### Criterii de calitate

| Nivel | Descriere |
|-------|-----------|
| Exemplar (90-100%) | Plan complet, eficiență >85%, documentație profesională |
| Competent (70-89%) | Plan funcțional, eficiență >70%, documentație adecvată |
| În dezvoltare (50-69%) | Plan parțial, unele erori de calcul, documentație minimă |
| Nesatisfăcător (<50%) | Plan incomplet sau cu erori majore |

---

## 5. Quiz-uri de verificare

### Quiz rapid (5 minute, 5 întrebări)

Generat automat cu:
```bash
python ex_5_03_quiz_generator.py --interactive --count 5
```

| Punctaj | Nivel |
|---------|-------|
| 5/5 | Excelent |
| 4/5 | Foarte bine |
| 3/5 | Bine |
| 2/5 | Suficient |
| 0-1/5 | Necesită remediere |

---

## 6. Legătura cu evaluarea finală

| Componentă | Pondere în nota finală | Contribuția S5 |
|------------|------------------------|----------------|
| Examen scris | 70% | ~5% (1/14 săptămâni) |
| Proiect echipă | 15% | 15% (artefact săptămânal) |
| Teste/quiz-uri | 15% | 7.5% (1/2 teste pe parcurs) |

---

## Anexă: Soluții exerciții (doar pentru cadrul didactic)

*Acest fișier se completează cu soluțiile din `solutions/exercitii_solutii.md` și nu se distribuie studenților înainte de termenul limită.*

---

*Rubrici elaborate conform fișei disciplinei — Rețele de calculatoare, ASE-CSIE*
