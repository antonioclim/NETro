# Rubrici de Evaluare – Săptămâna 10

## Evaluare seminar/laborator

### Criterii generale

| Criteriu | Excelent (10-9) | Bun (8-7) | Satisfăcător (6-5) | Insuficient (<5) |
|----------|-----------------|-----------|---------------------|------------------|
| **Funcționalitate** | Toate task-urile complete, funcționale | Task-uri principale complete | Unele task-uri incomplete | Majoritate nefuncționale |
| **Înțelegere** | Explică clar mecanismele | Înțelege conceptele de bază | Înțelegere parțială | Nu poate explica |
| **Cod** | Curat, documentat, modular | Funcțional, documentat minimal | Funcțional dar haotic | Nu funcționează |
| **Debugging** | Rezolvă independent | Rezolvă cu indicații | Necesită asistență | Nu poate rezolva |

---

## Rubrica detaliată: Laborator S10

### Task 1: DNS (20 puncte)

| Componentă | Puncte | Criterii |
|------------|--------|----------|
| Query DNS implicit Docker | 5 | Output corect pentru `dig web`, `dig ssh-server` |
| Query DNS custom | 5 | Output corect pentru `dig @dns-server -p 5353 myservice.lab.local` |
| Captură trafic DNS | 5 | tcpdump funcțional, identifică query/response |
| Explicație diferențe | 5 | Răspuns corect și complet la întrebări |

**Indicatori:**
- 20/20: Toate componentele complete + explicații clare
- 15/20: Funcționalitate OK, explicații incomplete
- 10/20: Doar partea practică, fără înțelegere demonstrată
- 5/20: Partial funcțional, multe erori
- 0/20: Nefuncțional sau nelivrat

### Task 2: SSH + Paramiko (25 puncte)

| Componentă | Puncte | Criterii |
|------------|--------|----------|
| Conectare manuală SSH | 5 | Login reușit, comenzi executate |
| Script Paramiko funcțional | 10 | Conectare, exec_command, afișare output |
| Transfer SFTP | 5 | Upload și download fișier demonstrat |
| Tratare erori | 5 | try/except, mesaje informative |

**Indicatori:**
- 25/25: Script complet cu SFTP și error handling
- 20/25: Script funcțional fără error handling robust
- 15/25: Doar conectare și exec, fără SFTP
- 10/25: Conectare funcțională, script incomplet
- 0/25: Nefuncțional

### Task 3: Port Forwarding (20 puncte)

| Componentă | Puncte | Criterii |
|------------|--------|----------|
| Creare tunel SSH | 8 | Comanda corectă, tunel activ |
| Acces serviciu prin tunel | 7 | curl funcțional prin localhost:9000 |
| Explicație mecanism | 5 | Înțelege fluxul traficului |

**Indicatori:**
- 20/20: Tunel funcțional + explicație clară
- 15/20: Tunel funcțional, explicație vagă
- 10/20: Parțial funcțional
- 5/20: Comandă greșită, nu funcționează
- 0/20: Neîncercat

### Task 4: FTP Transfer (20 puncte)

| Componentă | Puncte | Criterii |
|------------|--------|----------|
| Conectare FTP | 5 | Login reușit |
| Listare fișiere | 5 | nlst() funcțional |
| Upload fișier | 5 | STOR reușit |
| Download fișier | 5 | RETR reușit |

**Indicatori:**
- 20/20: Toate operațiile funcționale
- 15/20: 3 din 4 operații OK
- 10/20: Doar conectare și listare
- 5/20: Doar conectare
- 0/20: Nefuncțional

### Task 5: Raport și documentare (15 puncte)

| Componentă | Puncte | Criterii |
|------------|--------|----------|
| Structură raport | 5 | Format corect, secțiuni clare |
| Capturi ecran | 5 | Output-uri relevante incluse |
| Reflexii personale | 5 | Observații proprii, nu copy-paste |

**Indicatori:**
- 15/15: Raport complet, profesional
- 10/15: Raport corect dar minimal
- 5/15: Structură OK dar conținut slab
- 0/15: Raport lipsă sau plagiat

---

## Contribuția la proiectul de echipă

### Script `lab10_automation.py`

| Criteriu | Puncte | Detalii |
|----------|--------|---------|
| Verificare servicii | 2 | Testează DNS, SSH, FTP disponibilitate |
| Query DNS | 1 | Interogare domeniu custom |
| Conexiune SSH | 2 | Execuție comandă, output |
| Transfer FTP | 2 | Upload/download fișier |
| Raport JSON | 1 | Output structurat corect |
| Error handling | 1 | Excepții tratate, mesaje clare |
| Documentare cod | 1 | Docstrings, comentarii |
| **Total** | **10** | |

### Criterii calitative cod

```
Excelent: Cod modular, funcții separate, docstrings complete,
          type hints, logging, configurare flexibilă

Bun:      Cod funcțional, structură OK, comentarii minimale,
          error handling de bază

Satisfăcător: Cod monolitic dar funcțional, fără documentare,
              error handling minimal

Insuficient: Cod nefuncțional sau hardcodat excesiv
```

---

## Grading scale

| Punctaj total | Notă |
|---------------|------|
| 95-100 | 10 |
| 85-94 | 9 |
| 75-84 | 8 |
| 65-74 | 7 |
| 55-64 | 6 |
| 45-54 | 5 |
| < 45 | 4 (respins) |

---

## Penalizări

| Situație | Penalizare |
|----------|------------|
| Întârziere 1-24h | -10% |
| Întârziere 24-48h | -25% |
| Întârziere >48h | Nu se acceptă |
| Plagiat parțial | -50% |
| Plagiat total | 0 + raportare |
| Cod AI-generat nedeclarat | -30% |

**Notă:** Folosirea AI (ChatGPT, Claude, Copilot) este permisă, dar trebuie declarată. Codul trebuie înțeles și explicat la cerere.

---

## Feedback structurat

### Template feedback individual

```
Student: [Nume]
Data: [Data]

PUNCTAJ:
- DNS: __/20
- SSH/Paramiko: __/25
- Port Forward: __/20
- FTP: __/20
- Raport: __/15
- TOTAL: __/100

OBSERVAȚII:
- Puncte forte: 
- De îmbunătățit:
- Recomandări:

NOTĂ FINALĂ: __
```

### Criterii feedback

1. **Specific**: Referință la cod/output concret
2. **Constructiv**: Sugestii de îmbunătățire
3. **Echilibrat**: Și puncte forte, și slăbiciuni
4. **Acționabil**: Ce poate face studentul diferit

---

## Exemplu evaluare

### Student: Exemplu Ionescu

**DNS (18/20):**
- ✓ Query implicit corect
- ✓ Query custom corect
- ✓ tcpdump funcțional
- △ Explicație parțială (nu menționează TTL)

**SSH (23/25):**
- ✓ Conectare manuală OK
- ✓ Script Paramiko excelent
- ✓ SFTP funcțional
- △ Error handling basic (doar try/except generic)

**Port Forward (20/20):**
- ✓ Tunel creat corect
- ✓ curl funcțional
- ✓ Explicație clară

**FTP (20/20):**
- ✓ Toate operațiile OK

**Raport (12/15):**
- ✓ Structură bună
- ✓ Capturi relevante
- △ Reflexii minimale

**TOTAL: 93/100 = Nota 9**

---

*Material pentru uz intern – Rețele de Calculatoare, ASE București*

*Revolvix&Hypotheticalandrei*
