# Rubrici de Evaluare — Săptămâna 14: Proiect Final

## Cuprins

1. [Rubrică de Evaluare a Proiectului de Echipă](#1-rubrică-de-evaluare-a-proiectului-de-echipă)
2. [Criterii Detaliate](#2-criterii-detaliate)
3. [Grila de Notare](#3-grila-de-notare)
4. [Întrebări de Apărare](#4-întrebări-de-apărare)
5. [Indicatori de Originalitate](#5-indicatori-de-originalitate)

---

## 1. Rubrică de Evaluare a Proiectului de Echipă

### Criteriu A: Complexitate Tehnică (40 puncte)

| Punctaj | Descriptor | Indicatori |
|---------|------------|------------|
| 36-40   | Excepțional | Arhitectură multi-tier, protocol personalizat sau extensie semnificativă, load balancing funcțional, persistență date, logging avansat |
| 30-35   | Foarte bun | Client-server TCP/UDP cu multiple funcționalități, validare date, tratare erori, cel puțin 3 tipuri de mesaje |
| 24-29   | Bun | Client-server funcțional cu 2 tipuri de mesaje, tratare erori de bază, cod structurat |
| 16-23   | Satisfăcător | Echo client-server cu mici modificări, cod funcțional dar minimal |
| 0-15    | Insuficient | Cod nefuncțional sau copiat fără înțelegere |

### Criteriu B: Funcționalitate și Demonstrație (30 puncte)

| Punctaj | Descriptor | Indicatori |
|---------|------------|------------|
| 27-30   | Excepțional | Demonstrație live impecabilă, scenarii multiple, recuperare din erori demonstrată |
| 22-26   | Foarte bun | Demonstrație fluentă, cel puțin 2 scenarii, captură Wireshark interpretată corect |
| 16-21   | Bun | Demonstrație funcțională cu mici probleme, captură prezentată |
| 10-15   | Satisfăcător | Demonstrație parțială, necesită ajutor pentru rulare |
| 0-9     | Insuficient | Proiectul nu pornește sau demonstrație eșuată |

### Criteriu C: Prezentare și Comunicare (20 puncte)

| Punctaj | Descriptor | Indicatori |
|---------|------------|------------|
| 18-20   | Excepțional | Structură clară, timing respectat, răspunsuri la întrebări precise și complete |
| 14-17   | Foarte bun | Prezentare organizată, răspunsuri corecte la majoritatea întrebărilor |
| 10-13   | Bun | Prezentare acceptabilă, unele ezitări la întrebări |
| 6-9     | Satisfăcător | Prezentare dezorganizată sau răspunsuri incomplete |
| 0-5     | Insuficient | Comunicare deficitară sau incapacitate de a explica codul propriu |

### Criteriu D: Documentație și Reproducibilitate (10 puncte)

| Punctaj | Descriptor | Indicatori |
|---------|------------|------------|
| 9-10    | Excepțional | README complet, pași clari, diagrame, capturi exemplu, Makefile/scripturi |
| 7-8     | Foarte bun | README cu instrucțiuni funcționale, dependențe listate |
| 5-6     | Bun | README minimal dar suficient pentru rulare |
| 3-4     | Satisfăcător | Instrucțiuni incomplete sau eronate |
| 0-2     | Insuficient | Fără documentație sau nefolosibilă |

---

## 2. Criterii Detaliate

### 2.1 Ce înseamnă „Complexitate Tehnică"

Nivelurile de complexitate sunt evaluate astfel:

**Nivel 1 (Basic)**: Echo simplu TCP sau UDP
- Un singur tip de mesaj (text → ecou)
- Fără validare sau tratare erori

**Nivel 2 (Intermediar)**: Protocol cu comenzi
- Cel puțin 3 comenzi diferite (ex: GET, PUT, LIST)
- Validare input, coduri de eroare
- Separare client/server clară

**Nivel 3 (Avansat)**: Aplicație completă
- Persistență (fișiere sau bază de date simplă)
- Autentificare sau sesiuni
- Logging structurat

**Nivel 4 (Expert)**: Arhitectură distribuită
- Load balancing sau failover
- Protocol binar sau compresie
- Metrici și monitorizare

### 2.2 Cerințe pentru Demonstrație Live

Demonstrația trebuie să includă:

1. **Pornirea componentelor** (în ordine corectă)
2. **Scenariul principal** (funcționalitatea de bază)
3. **Scenariul de eroare** (ce se întâmplă când ceva eșuează)
4. **Captură Wireshark/tshark** (cu explicația pachetelor)

Timp alocat: 7-10 minute prezentare + 3-5 minute întrebări.

---

## 3. Grila de Notare

| Total puncte | Notă | Calificativ |
|--------------|------|-------------|
| 95-100       | 10   | Excepțional |
| 85-94        | 9    | Foarte bun  |
| 75-84        | 8    | Bun         |
| 65-74        | 7    | Satisfăcător |
| 55-64        | 6    | Acceptabil  |
| 45-54        | 5    | Minim       |
| 0-44         | 4    | Insuficient |

### Bonusuri (maxim +10 puncte)

- **+3**: Containerizare Docker funcțională
- **+2**: Teste automate (pytest sau similar)
- **+2**: CI/CD configurație (GitHub Actions)
- **+2**: Documentație în format profesional (PDF generat)
- **+1**: Diagrame de arhitectură (draw.io, Mermaid)

### Penalizări

- **-5**: Întârziere la prezentare fără motiv
- **-10**: Cod plagiat (detectat prin similaritate)
- **-15**: Membru echipă absent fără justificare
- **-20**: Proiect identic cu altă echipă

---

## 4. Întrebări de Apărare

Întrebările sunt structurate pe niveluri cognitive:

### Nivel 1: Cunoaștere

- Ce protocol de transport folosiți?
- Ce port ascultă serverul?
- Ce bibliotecă Python folosiți pentru socket-uri?

### Nivel 2: Înțelegere

- De ce ați ales TCP în loc de UDP (sau invers)?
- Ce reprezintă cei trei timpi din handshake-ul TCP?
- Care este diferența dintre `bind()` și `connect()`?

### Nivel 3: Aplicare

- Cum ați modifica serverul să accepte conexiuni multiple?
- Ce se întâmplă dacă clientul trimite date mai mari decât bufferul?
- Cum ați adăuga timeout la operațiile de rețea?

### Nivel 4: Analiză

- Unde este bottleneck-ul în arhitectura voastră?
- Ce s-ar întâmpla dacă serverul cade în mijlocul transferului?
- Cum afectează latența rețelei performanța aplicației?

### Nivel 5: Evaluare

- Ce ați face diferit dacă ați reîncepe proiectul?
- Care sunt limitările arhitecturii alese?
- Cum se compară soluția voastră cu alternative comerciale?

---

## 5. Indicatori de Originalitate

### Semne pozitive

- Cod organizat în funcții/clase cu nume descriptive
- Comentarii care explică „de ce", nu „ce"
- Tratare erori specifică proiectului
- Integrare naturală între componente
- Răspunsuri prompte la întrebări despre orice parte a codului

### Semne negative (posibil plagiat)

- Cod copiat dintr-un tutorial fără adaptare
- Variabile generice (x, y, data1, data2)
- Comentarii în limba engleză când proiectul e în română (sau invers)
- Incapacitate de a explica secțiuni de cod
- Stil inconsistent (mixare tabs/spaces, convenții diferite)

---

## Anexă: Formular de Notare

```
Echipa: __________________ Data: __________

Membri prezenți:
□ __________________ □ __________________
□ __________________ □ __________________

EVALUARE:
                           Punctaj acordat
A. Complexitate tehnică    _____ / 40
B. Funcționalitate         _____ / 30
C. Prezentare              _____ / 20
D. Documentație            _____ / 10
                           -----------
   SUBTOTAL                _____ / 100

Bonusuri:                  + _____
Penalizări:                - _____
                           -----------
   TOTAL FINAL             _____

Observații:
_________________________________________________
_________________________________________________

Semnătura evaluator: _________________
```

---

*Document generat pentru disciplina „Rețele de calculatoare", Săptămâna 14.*
