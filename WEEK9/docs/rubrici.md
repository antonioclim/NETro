# Rubrici de Evaluare – Săptămâna 9

## Evaluare Laborator Individual

### Criteriu 1: Setup și Configurare (15 puncte)

| Nivel | Puncte | Descriere |
|-------|--------|-----------|
| Excelent | 15 | Mediul complet configurat, `make verify` trece, documentație setup completată |
| Bine | 12 | Setup funcțional cu mici ajutări, toate componentele instalate |
| Satisfăcător | 9 | Setup parțial, unele componente lipsesc dar nucleul funcționează |
| Insuficient | 5 | Setup incomplet, necesită asistență semnificativă |
| Nepredat | 0 | Nu a configurat mediul |

### Criteriu 2: Executarea Demo-urilor (25 puncte)

| Nivel | Puncte | Descriere |
|-------|--------|-----------|
| Excelent | 25 | Toate demo-urile executate și rezultatele interpretate corect |
| Bine | 20 | Demo-uri executate, interpretare parțială |
| Satisfăcător | 15 | 2 din 3 demo-uri reușite |
| Insuficient | 8 | 1 demo reușit |
| Nepredat | 0 | Nu a executat niciun demo |

### Criteriu 3: Captură și Analiză Trafic (25 puncte)

| Nivel | Puncte | Descriere |
|-------|--------|-----------|
| Excelent | 25 | Captură completă, analiză detaliată cu identificarea tuturor elementelor protocol, raport clar |
| Bine | 20 | Captură și analiză corectă, identificare parțială a elementelor |
| Satisfăcător | 15 | Captură generată, analiză superficială |
| Insuficient | 8 | Captură generată dar fără analiză |
| Nepredat | 0 | Nu a realizat captura |

### Criteriu 4: Docker Multi-Client (20 puncte)

| Nivel | Puncte | Descriere |
|-------|--------|-----------|
| Excelent | 20 | Orchestrație completă, toți clienții funcționali, logs interpretate |
| Bine | 16 | Docker compose funcțional, cel puțin 2 clienți conectați |
| Satisfăcător | 12 | Docker compose pornit, erori minore |
| Insuficient | 6 | Tentativă de pornire cu erori majore |
| Nepredat | 0 | Nu a încercat Docker |

### Criteriu 5: Notă Reflexivă (15 puncte)

| Nivel | Puncte | Descriere |
|-------|--------|-----------|
| Excelent | 15 | Reflecție profundă, conexiuni relevante, observații originale |
| Bine | 12 | Reflecție clară, conexiuni corecte |
| Satisfăcător | 9 | Reflecție de bază, răspunde la întrebări ghid |
| Insuficient | 5 | Reflecție minimală, sub 3 rânduri |
| Nepredat | 0 | Nu a completat nota reflexivă |

### Punctaj total: 100 puncte

**Conversia în notă:**
- 90-100: 10
- 80-89: 9
- 70-79: 8
- 60-69: 7
- 50-59: 6
- 40-49: 5
- < 40: 4 (necesită refacere)

---

## Evaluare Exerciții Seminar (Bonus)

### Exercițiu 1: Comanda INFO (⭐) - 5 puncte bonus

| Criteriu | Puncte |
|----------|--------|
| Funcționează corect | 2 |
| Cod curat și comentat | 1 |
| Gestionare erori | 1 |
| Format output conform specificației | 1 |

### Exercițiu 2: LIST cu Wildcard (⭐⭐) - 8 puncte bonus

| Criteriu | Puncte |
|----------|--------|
| Pattern matching funcțional | 3 |
| Integrare corectă în parser | 2 |
| Cazuri limită gestionate | 2 |
| Documentare utilizare | 1 |

### Exercițiu 3: MKDIR (⭐⭐) - 8 puncte bonus

| Criteriu | Puncte |
|----------|--------|
| Creare director funcțională | 3 |
| Validare nume corectă | 2 |
| Verificare permisiuni | 2 |
| Mesaje eroare clare | 1 |

### Exercițiu 4: Reluare Transfer (⭐⭐⭐) - 12 puncte bonus

| Criteriu | Puncte |
|----------|--------|
| REST funcțional | 4 |
| RETR cu offset funcțional | 4 |
| Integritate după reluare | 2 |
| Test cu fișier mare | 2 |

### Exercițiu 5: Rate Limiting (⭐⭐⭐) - 12 puncte bonus

| Criteriu | Puncte |
|----------|--------|
| Limitare funcțională | 4 |
| Algoritm corect (token bucket sau similar) | 3 |
| Configurabilitate | 3 |
| Măsurare și raportare viteză | 2 |

### Exercițiu CHALLENGE: Transfer Multi-Fișier (🏆) - 20 puncte bonus

| Criteriu | Puncte |
|----------|--------|
| MGET funcțional | 5 |
| MPUT funcțional | 5 |
| Raport progres | 3 |
| Gestionare erori parțiale | 4 |
| Documentație completă | 3 |

---

## Contribuția la Proiectul de Echipă

### Artefact săptămânal: Modul de Transfer Fișiere

**Cerință**: Echipa integrează în proiect un mecanism de transfer fișiere între componente (fie protocol custom, fie wrapper peste biblioteci existente).

### Criterii de evaluare echipă (30 puncte din nota proiectului)

| Criteriu | Puncte | Descriere |
|----------|--------|-----------|
| Funcționalitate | 10 | Transferul funcționează între cel puțin 2 componente |
| Integrare | 8 | Codul se integrează curat în arhitectura existentă |
| Testare | 6 | Teste automate pentru scenariile principale |
| Documentare | 4 | README actualizat cu secțiunea de transfer |
| Code review | 2 | Pull request cu review de la coechipier |

### Timeline

| Data | Activitate |
|------|-----------|
| Săpt. 9 + 2 zile | Branch creat, design documentat |
| Săpt. 9 + 5 zile | Implementare completă, teste scrise |
| Săpt. 10 | Demo în seminar, merge în main |

---

## Criterii de Recuperare

### Pentru nota de trecere (5)

Studentul trebuie să demonstreze:
1. Înțelegerea conceptelor L5/L6 (test oral sau scris)
2. Capacitatea de a rula serverul și clientul (demonstrație)
3. O captură minimală analizată (fișier .pcap + 5 observații)

### Termen limită recuperare

- Până la sesiunea de examene
- Se programează individual cu cadrul didactic

---

## Feedback și Calibrare

### Rubrica de feedback pentru studenți

După evaluare, fiecare student primește:
- Punctaj detaliat pe fiecare criteriu
- 2-3 puncte forte identificate
- 2-3 sugestii de îmbunătățire
- Resurse recomandate pentru aprofundare (dacă e cazul)

### Calibrare între evaluatori

La începutul semestrului și la mijloc:
- Toți evaluatorii notează aceleași 3 lucrări anonimizate
- Discuție pentru aliniere
- Ajustare rubrici dacă apar discrepanțe > 10%

---

## Anexă: Formulare

### Formular evaluare laborator

```
Student: ___________________ Grupa: _____ Data: _______

CRITERII                                    PUNCTAJ
─────────────────────────────────────────────────────
1. Setup și configurare            [   ] / 15
2. Executarea demo-urilor          [   ] / 25
3. Captură și analiză              [   ] / 25
4. Docker multi-client             [   ] / 20
5. Notă reflexivă                  [   ] / 15
─────────────────────────────────────────────────────
TOTAL                              [   ] / 100

BONUS exerciții:                   [   ] puncte

Observații:


Evaluator: ___________________
```

### Formular feedback echipă

```
Echipa: ___________________  Săptămâna: 9

Artefact: Modul Transfer Fișiere

CRITERII                                    PUNCTAJ
─────────────────────────────────────────────────────
Funcționalitate                    [   ] / 10
Integrare                          [   ] / 8
Testare                            [   ] / 6
Documentare                        [   ] / 4
Code review                        [   ] / 2
─────────────────────────────────────────────────────
TOTAL                              [   ] / 30

Puncte forte:
1.
2.

De îmbunătățit:
1.
2.

Evaluator: ___________________
```
