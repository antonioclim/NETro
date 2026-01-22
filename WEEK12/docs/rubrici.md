# Rubrici de Evaluare — Săptămâna 12

## Protocoale Email (SMTP, POP3, IMAP) și RPC (JSON-RPC, XML-RPC, gRPC)

---

## 1. Structura Evaluării Săptămânale

| Componentă | Pondere | Descriere |
|------------|---------|-----------|
| Participare activă | 10% | Prezență, întrebări, implicare în discuții |
| Exerciții laborator | 40% | Completarea pașilor din lab.html + capturi |
| Exerciții gradate | 30% | Rezolvarea ex_01_smtp.py și ex_02_rpc.py |
| Contribuție proiect echipă | 20% | Artefact incremental (modul email/RPC) |

---

## 2. Rubrică Detaliată — Exerciții Laborator (40 puncte)

### 2.1 Server SMTP Educațional (10 puncte)

| Criteriu | Excelent (10p) | Satisfăcător (6-9p) | Insuficient (<6p) |
|----------|----------------|---------------------|-------------------|
| Pornire server | Server pornit corect pe portul 1025, log activ | Pornit cu mici erori de configurare | Nu pornește sau erori majore |
| Trimitere email | Email trimis cu succes, headers corecte | Email trimis cu headers incomplete | Eșec la trimitere |
| Verificare mailbox | Listare corectă, conținut vizualizat | Listare parțială | Nu poate accesa mailbox |
| Captură tshark | Captură completă, dialog SMTP identificat | Captură parțială | Fără captură validă |

### 2.2 Servere RPC (15 puncte)

| Criteriu | Excelent (15p) | Satisfăcător (9-14p) | Insuficient (<9p) |
|----------|----------------|----------------------|-------------------|
| JSON-RPC server | Pornit, toate metodele funcționale | Pornit, unele metode problematice | Nu pornește |
| JSON-RPC client | Apeluri reușite, batch funcțional | Apeluri simple reușite | Eșecuri la apeluri |
| XML-RPC server | Pornit, introspecție funcțională | Pornit, fără introspecție | Nu pornește |
| Benchmark RPC | Rulat, rezultate interpretate corect | Rulat, interpretare superficială | Benchmark nerealizat |

### 2.3 Capturi și Analiză (15 puncte)

| Criteriu | Excelent (15p) | Satisfăcător (9-14p) | Insuficient (<9p) |
|----------|----------------|----------------------|-------------------|
| Captură SMTP | Sesiune completă: EHLO→DATA→QUIT | Captură parțială | Fără captură |
| Captură JSON-RPC | Request/Response HTTP identificate | Doar request sau response | Fără captură |
| Interpretare | Explicații corecte ale câmpurilor | Explicații superficiale | Fără interpretare |
| Filtre Wireshark | Filtre corecte aplicate și documentate | Filtre parțial corecte | Fără filtre |

---

## 3. Rubrică Detaliată — Exerciții Gradate (30 puncte)

### 3.1 Exercițiu 1: Client SMTP Extins (★☆☆) — 5 puncte

| Criteriu | Punctaj |
|----------|---------|
| Implementare comandă `MAIL FROM` manuală | 2p |
| Implementare comandă `RCPT TO` manuală | 1p |
| Validare coduri răspuns (250, 354, etc.) | 2p |

### 3.2 Exercițiu 2: Metodă RPC Nouă (★★☆) — 5 puncte

| Criteriu | Punctaj |
|----------|---------|
| Definire metodă nouă în server | 2p |
| Documentare parametri și return | 1p |
| Test client cu output corect | 2p |

### 3.3 Exercițiu 3: Gestionare Erori RPC (★★☆) — 5 puncte

| Criteriu | Punctaj |
|----------|---------|
| Implementare try-except în server | 2p |
| Returnare cod eroare JSON-RPC corect | 2p |
| Test cu input invalid | 1p |

### 3.4 Exercițiu 4: Comparație Protocol (★★★) — 7 puncte

| Criteriu | Punctaj |
|----------|---------|
| Benchmark JSON-RPC (100 apeluri) | 2p |
| Benchmark XML-RPC (100 apeluri) | 2p |
| Tabel comparativ cu metrici | 2p |
| Concluzie argumentată | 1p |

### 3.5 Exercițiu 5: Email cu Attachments (★★★) — 4 puncte

| Criteriu | Punctaj |
|----------|---------|
| Construire mesaj MIME multipart | 2p |
| Attachment base64 encoded corect | 1p |
| Trimitere și verificare | 1p |

### 3.6 Exercițiu Challenge: Email Relay (★★★★) — 4 puncte

| Criteriu | Punctaj |
|----------|---------|
| Implementare server relay funcțional | 2p |
| Forwarding către destinație | 1p |
| Logging și debugging | 1p |

---

## 4. Rubrică — Contribuție Proiect Echipă (20 puncte)

### Opțiunea A: Modul Notificări Email

| Criteriu | Excelent (20p) | Bun (14-19p) | Satisfăcător (10-13p) | Insuficient (<10p) |
|----------|----------------|--------------|----------------------|-------------------|
| Arhitectură | Modul separat, API clar, documentat | Modul funcțional, API parțial documentat | Cod funcțional dar nemodularizat | Cod nefuncțional |
| Funcționalitate | Trimitere notificări, templates, retry | Trimitere de bază funcțională | Trimitere parțială | Eșec la trimitere |
| Configurabilitate | SMTP server configurabil, credențiale securizate | Configurare parțială | Hardcoded values | Fără configurare |
| Testare | Unit tests, integration tests | Teste manuale documentate | Teste ad-hoc | Fără testare |
| Integrare | PR aprobat, CI/CD funcțional | PR creat, review pending | Cod local netestat | Fără integrare |

### Opțiunea B: API Intern RPC

| Criteriu | Excelent (20p) | Bun (14-19p) | Satisfăcător (10-13p) | Insuficient (<10p) |
|----------|----------------|--------------|----------------------|-------------------|
| Design API | RESTful/RPC consistent, versionat | API funcțional, versionare parțială | Endpoint-uri funcționale | API nefuncțional |
| Documentație | OpenAPI/Swagger complet | Documentație manuală completă | README de bază | Fără documentație |
| Gestionare erori | Coduri eroare standard, mesaje clare | Erori gestionate parțial | Erori generice | Fără gestionare |
| Performanță | Response time <100ms, caching | Response time acceptabil | Performanță variabilă | Timeout frecvent |
| Securitate | Autentificare, rate limiting | Autentificare de bază | Fără autentificare | Vulnerabilități |

---

## 5. Criterii de Evaluare a Calității Codului

| Aspect | Punctaj Maxim | Descriere |
|--------|---------------|-----------|
| Funcționalitate | 40% | Codul face ce trebuie, fără erori |
| Claritate | 20% | Cod lizibil, variabile descriptive, structură logică |
| Documentare | 15% | Docstrings, comentarii utile, README |
| Gestionare erori | 15% | Try-except, validări input, mesaje clare |
| Stil | 10% | PEP8, formatare consistentă, imports organizate |

---

## 6. Penalizări

| Situație | Penalizare |
|----------|------------|
| Întârziere <24h | -10% |
| Întârziere 24-48h | -25% |
| Întârziere >48h | -50% |
| Plagiat | -100% + raportare |
| Cod care nu rulează | -30% minim |
| Lipsă documentație | -15% |
| Fără capturi Wireshark | -20% |

---

## 7. Bonusuri

| Realizare | Bonus |
|-----------|-------|
| Implementare gRPC complet funcțional | +10% |
| Implementare POP3 client funcțional | +5% |
| Securizare TLS pentru SMTP | +5% |
| Batch requests JSON-RPC optimizat | +5% |
| Documentație video demonstrativă | +5% |

---

## 8. Checklist Auto-Evaluare Student

Înainte de predare, verifică:

- [ ] Toate fișierele sunt în structura corectă
- [ ] `make verify` rulează fără erori
- [ ] Capturile .pcap sunt atașate
- [ ] README.md actualizat cu observații personale
- [ ] Codul este formatat consistent (black, flake8)
- [ ] Toate exercițiile au output documentat
- [ ] Proiectul de echipă are commit separat

---

## 9. Legătura cu Competențele din Fișa Disciplinei

| Competență Fișă | Activitate Săptămâna 12 | Verificare |
|-----------------|-------------------------|------------|
| Implementare servere concurente | Server SMTP multi-client | Captură tshark cu sesiuni paralele |
| Programare pe socket-uri | Client/Server SMTP manual | Cod funcțional fără biblioteci high-level |
| Analiza traficului | Capturi Wireshark pentru Email și RPC | Filtre aplicate, interpretare |
| Servicii distribuite | JSON-RPC, XML-RPC client-server | Benchmark și comparație |
| Docker și containerizare | Opțional: servicii în containere | docker-compose up funcțional |

---

## 10. Feedback și Îmbunătățire

După evaluare, cadrul didactic va furniza:

1. **Punctaj detaliat** — pe fiecare rubrică
2. **Comentarii specifice** — ce a fost bun, ce trebuie îmbunătățit
3. **Resurse suplimentare** — pentru studenții care doresc aprofundare
4. **Întâlnire individuală** — la cerere, pentru clarificări

---

*Material didactic — Săptămâna 12, Rețele de Calculatoare, ASE-CSIE*
