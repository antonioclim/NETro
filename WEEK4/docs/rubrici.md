# Rubrici de Evaluare – Săptămâna 4

> **Disciplină:** Rețele de Calculatoare  
> **Săptămâna:** 4  
> **Temă:** Protocoale text și binare custom peste TCP și UDP

---

## 1. Evaluare activitate seminar/laborator

### 1.1 Participare activă (10 puncte)

| Nivel | Puncte | Descriere |
|-------|--------|-----------|
| **Excelent** | 9-10 | Participă activ, pune întrebări relevante, ajută colegii, finalizează toate exercițiile |
| **Bine** | 7-8 | Participă constant, finalizează majoritatea exercițiilor, întrebări ocazionale |
| **Satisfăcător** | 5-6 | Participare minimă, finalizează exercițiile de bază cu asistență |
| **Insuficient** | 1-4 | Participare sporadică, nu finalizează exercițiile, necesită ghidare continuă |
| **Absent** | 0 | Nu participă sau absentează nemotivat |

### 1.2 Implementare Protocol TEXT (20 puncte)

| Criteriu | Puncte max | Descriere |
|----------|------------|-----------|
| **Parsing corect** | 5 | Extragere corectă lungime și payload din format `<LEN> <PAYLOAD>\n` |
| **recv_until()** | 5 | Implementare corectă citire până la delimiter |
| **Validare** | 3 | Verificare lungime declarată vs. reală |
| **Handling erori** | 4 | Try/except adecvat, mesaje de eroare clare |
| **Cod curat** | 3 | Denumiri clare, comentarii, structură |

**Scala de notare:**

| Puncte | Nivel |
|--------|-------|
| 18-20 | Excelent - Implementare completă, robustă, elegantă |
| 14-17 | Bine - Funcționalitate completă, mici imperfecțiuni |
| 10-13 | Satisfăcător - Funcționează pentru cazuri simple |
| 5-9 | Parțial - Funcționalitate incompletă |
| 0-4 | Insuficient - Nu funcționează |

### 1.3 Implementare Protocol BINAR (30 puncte)

| Criteriu | Puncte max | Descriere |
|----------|------------|-----------|
| **Header struct** | 8 | Utilizare corectă struct.pack/unpack, format big-endian |
| **recv_exact()** | 5 | Citire exactă de N bytes, handling conexiune închisă |
| **CRC32** | 7 | Calcul corect CRC32, validare la recepție |
| **Tipuri mesaje** | 5 | Diferențiere request/response/error |
| **Handling erori** | 3 | Validare magic, versiune, tratare erori |
| **Cod curat** | 2 | Constante definite, structură modulară |

**Scala de notare:**

| Puncte | Nivel |
|--------|-------|
| 27-30 | Excelent - Implementare completă și robustă |
| 21-26 | Bine - Funcționalitate completă |
| 15-20 | Satisfăcător - Părți esențiale funcționează |
| 8-14 | Parțial - Funcționalitate limitată |
| 0-7 | Insuficient - Erori majore |

### 1.4 Implementare Protocol UDP Sensor (20 puncte)

| Criteriu | Puncte max | Descriere |
|----------|------------|-----------|
| **Datagram format** | 6 | Structură corectă 23 bytes, pack/unpack corect |
| **Padding location** | 3 | Câmp location padded la 10 caractere |
| **CRC32** | 4 | Calcul și validare CRC pentru datagrame |
| **sendto/recvfrom** | 4 | Utilizare corectă API UDP |
| **Fire-and-forget** | 3 | Înțelegere și implementare pattern UDP |

### 1.5 Analiză trafic (20 puncte)

| Criteriu | Puncte max | Descriere |
|----------|------------|-----------|
| **Captură corectă** | 5 | Filtre corecte pentru porturi, salvare pcap |
| **Identificare câmpuri** | 6 | Recunoaștere header, payload în hex dump |
| **Interpretare** | 5 | Explicație corectă a ce reprezintă fiecare byte |
| **Comparație** | 4 | Analiză overhead TEXT vs BINAR |

---

## 2. Evaluare exerciții individuale

### Exercițiu 1: Protocol TEXT cu comenzi multiple (15 puncte)

**Cerință:** Extindere protocol TEXT cu comenzi ECHO, UPPER, LOWER, REVERSE, COUNT

| Criteriu | Puncte | Descriere |
|----------|--------|-----------|
| Parser comenzi | 4 | Extragere corectă comandă din mesaj |
| Implementare comenzi | 6 | Toate 5 comenzile funcționează corect |
| Răspunsuri formatate | 3 | Format răspuns consistent |
| Tratare erori | 2 | Comandă necunoscută gestionată |

### Exercițiu 2: Agregator UDP (15 puncte)

**Cerință:** Server care primește de la multipli senzori și calculează statistici

| Criteriu | Puncte | Descriere |
|----------|--------|-----------|
| Parsare datagrame | 4 | Extragere corectă date senzor |
| Statistici per senzor | 5 | Count, sum, min, max, avg corecte |
| Raport periodic | 3 | Thread sau timer pentru raportare |
| Export JSON | 3 | Format JSON valid și complet |

### Exercițiu Challenge: Protocol hibrid (25 puncte bonus)

| Criteriu | Puncte | Descriere |
|----------|--------|-----------|
| Specificație documentată | 5 | Document clar cu toate detaliile |
| Negociere TEXT | 5 | Handshake text pentru capabilități |
| Transfer BINAR | 7 | Mod binar funcțional după negociere |
| Compresie opțională | 5 | zlib funcțional, negociat în handshake |
| Demonstrație tshark | 3 | Captură care arată ambele moduri |

---

## 3. Contribuția la proiectul de echipă

### 3.1 Artefact S4 – Protocol custom pentru aplicație (50 puncte)

**Deadline:** Conform planificării proiectului

| Criteriu | Puncte max | Descriere |
|----------|------------|-----------|
| **Specificație protocol** | 15 | |
| - Format header documentat | 5 | Structură bytes, semnificație câmpuri |
| - Tipuri mesaje definite | 5 | Minim 3 tipuri cu coduri distincte |
| - Diagrame/tabele | 5 | Vizualizare clară a formatului |
| **Implementare** | 25 | |
| - Server funcțional | 10 | Pornește, acceptă conexiuni, procesează |
| - Client funcțional | 8 | Trimite cereri, primește răspunsuri |
| - Validare integritate | 7 | CRC sau alt mecanism implementat |
| **Demonstrație** | 10 | |
| - Captură tshark | 5 | Pcap cu trafic real al protocolului |
| - Interpretare | 5 | Explicație câmpuri în captură |

### 3.2 Integrare în proiect (evaluare ulterioară)

| Aspect | Descriere |
|--------|-----------|
| Compatibilitate | Protocolul se integrează în arhitectura echipei |
| Documentație | README actualizat cu detalii protocol |
| Teste | Teste automate pentru protocol |
| Code review | Feedback de la colegi integrat |

---

## 4. Criterii transversale

### 4.1 Calitatea codului

| Nivel | Descriere |
|-------|-----------|
| **Excelent** | Denumiri clare, comentarii docstring, structură modulară, fără duplicare |
| **Bine** | Cod lizibil, comentarii relevante, structură acceptabilă |
| **Satisfăcător** | Cod funcțional dar dezordonat, comentarii minime |
| **Insuficient** | Cod greu de citit, fără comentarii, copy-paste evident |

### 4.2 Documentare

| Nivel | Descriere |
|-------|-----------|
| **Excelent** | README complet, diagrame, exemple rulare, troubleshooting |
| **Bine** | README cu instrucțiuni de bază, câteva exemple |
| **Satisfăcător** | README minimal, comenzi de rulare |
| **Insuficient** | Fără documentație sau documentație greșită |

### 4.3 Testare

| Nivel | Descriere |
|-------|-----------|
| **Excelent** | Teste automate, cazuri limită, teste integrare |
| **Bine** | Teste manuale documentate, câteva cazuri |
| **Satisfăcător** | Testare ad-hoc, fără documentare |
| **Insuficient** | Fără testare evidentă |

---

## 5. Penalizări

| Situație | Penalizare |
|----------|------------|
| Întârziere livrare (per zi) | -10% din punctaj |
| Plagiat parțial | -50% și raportare |
| Plagiat total | 0 puncte și raportare |
| Cod care nu compilează/rulează | -30% din punctaj |
| Fără instrucțiuni de rulare | -10% din punctaj |
| Dependențe nespecificate | -5% din punctaj |

---

## 6. Feedback formativ

### Întrebări de auto-evaluare (studenți)

1. **Înțelegere conceptuală:**
   - Pot explica diferența între recv() și recv_exact()?
   - Înțeleg de ce TCP necesită framing explicit?
   - Pot descrie când aleg TEXT vs BINAR?

2. **Competențe practice:**
   - Pot implementa un protocol simplu de la zero?
   - Știu să folosesc struct.pack/unpack?
   - Pot analiza traficul custom în Wireshark?

3. **Integrare:**
   - Văd cum se aplică în proiectul de echipă?
   - Pot estima overhead-ul protocolului meu?

### Feedback instructor → student

Template feedback individual:

```
Student: [Nume]
Data: [Data]

✅ Puncte forte:
- 
- 

⚠️ Arii de îmbunătățire:
- 
- 

📚 Recomandări:
- 
- 

Punctaj S4: ___/100
```

---

## 7. Mapare la competențe disciplină

| Competență (din fișă) | Acoperire S4 |
|-----------------------|--------------|
| Programare pe sockets | ✓✓✓ Protocol text și binar |
| Implementare protocoale custom | ✓✓✓ Trei protocoale implementate |
| Analiza traficului | ✓✓ Captură și interpretare |
| Debugging rețea | ✓✓ Troubleshooting comune |
| Lucru în echipă | ✓ Integrare în proiect |

**Legendă:** ✓ = parțial, ✓✓ = substanțial, ✓✓✓ = complet

---

*Versiune rubrici: S4 v1.0 | Ultima actualizare: 2025*

<!-- Revolvix&Hypotheticalandrei -->
