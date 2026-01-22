# Rubrici de Evaluare – Săptămâna 11

## Prezentare Generală

Evaluarea săptămânii 11 contribuie la:
- **Nota de seminar** (30% din nota finală)
- **Proiectul de echipă** (30% din nota finală)

---

## 1. Criterii Laborator (max 10 puncte)

### 1.1 Pregătire și Verificare (1 punct)

| Nivel | Descriere | Puncte |
|-------|-----------|--------|
| Excelent | Mediul pregătit înainte de laborator, toate verificările trec | 1.0 |
| Satisfăcător | Pregătire în primele 10 minute | 0.5 |
| Insuficient | Probleme persistente cu mediul | 0 |

### 1.2 Load Balancer Python (2 puncte)

| Nivel | Descriere | Puncte |
|-------|-----------|--------|
| Excelent | Demonstrează toate algoritmii (RR, LC, IP Hash) + failover | 2.0 |
| Bine | Demonstrează 2 algoritmi corect | 1.5 |
| Satisfăcător | Demonstrează 1 algoritm corect | 1.0 |
| Insuficient | Nu reușește să pornească LB | 0 |

### 1.3 Nginx Docker (2 puncte)

| Nivel | Descriere | Puncte |
|-------|-----------|--------|
| Excelent | Stack pornit + testare + modificare algoritm | 2.0 |
| Bine | Stack pornit + testare | 1.5 |
| Satisfăcător | Stack pornit | 1.0 |
| Insuficient | Erori Docker netratate | 0 |

### 1.4 DNS/FTP Client (2 puncte)

| Nivel | Descriere | Puncte |
|-------|-----------|--------|
| Excelent | DNS client + FTP pasiv/activ + explicație diferențe | 2.0 |
| Bine | Ambele funcționează, explicație parțială | 1.5 |
| Satisfăcător | Unul din cele două funcționează | 1.0 |
| Insuficient | Nici unul nu funcționează | 0 |

### 1.5 Mininet (2 puncte)

| Nivel | Descriere | Puncte |
|-------|-----------|--------|
| Excelent | Demo complet + mod interactiv + modificări | 2.0 |
| Bine | Demo complet rulat | 1.5 |
| Satisfăcător | Topologie creată, teste parțiale | 1.0 |
| Insuficient | Erori netratate | 0 |

### 1.6 Captură Trafic (1 punct)

| Nivel | Descriere | Puncte |
|-------|-----------|--------|
| Excelent | Captură + analiză + interpretare | 1.0 |
| Satisfăcător | Captură realizată | 0.5 |
| Insuficient | Nu reușește captură | 0 |

---

## 2. Criterii Proiect de Echipă (max 10 puncte)

### 2.1 Docker Compose cu Load Balancing (4 puncte)

| Nivel | Descriere | Puncte |
|-------|-----------|--------|
| Excelent | 3+ backend-uri, nginx configurat, health checks, documentație | 4.0 |
| Bine | 2 backend-uri, nginx funcțional, documentație minimă | 3.0 |
| Satisfăcător | docker-compose.yml funcțional cu 1 backend | 2.0 |
| Insuficient | Fișiere lipsă sau erori | 0-1.0 |

### 2.2 Configurație Nginx (2 puncte)

| Nivel | Descriere | Puncte |
|-------|-----------|--------|
| Excelent | upstream configurat, headers corect setate, comentarii | 2.0 |
| Bine | upstream funcțional | 1.5 |
| Satisfăcător | nginx.conf prezent, configurare minimală | 1.0 |
| Insuficient | Configurare invalidă | 0 |

### 2.3 Script Health Check (2 puncte)

| Nivel | Descriere | Puncte |
|-------|-----------|--------|
| Excelent | Script funcțional + logging + alerting | 2.0 |
| Bine | Script funcțional | 1.5 |
| Satisfăcător | Script prezent, funcționare parțială | 1.0 |
| Insuficient | Lipsă sau nefuncțional | 0 |

### 2.4 Documentație (2 puncte)

| Nivel | Descriere | Puncte |
|-------|-----------|--------|
| Excelent | Diagramă arhitectură + README complet + instrucțiuni deployment | 2.0 |
| Bine | README cu instrucțiuni clare | 1.5 |
| Satisfăcător | README minimal | 1.0 |
| Insuficient | Documentație lipsă | 0 |

---

## 3. Bonusuri (+max 2 puncte)

| Criteriu | Bonus |
|----------|-------|
| Implementare algoritm custom în LB Python | +0.5 |
| Configurare TLS în Nginx (HTTPS) | +0.5 |
| Active health checks cu script personalizat | +0.5 |
| Benchmark documentat cu grafice | +0.5 |

---

## 4. Penalizări

| Criteriu | Penalizare |
|----------|------------|
| Întârziere predare (per zi) | -1 punct |
| Cod copiat între echipe | -50% din nota proiectului |
| Lipsă README sau documentație | -2 puncte |
| Erori grave de securitate (ex: credențiale în cod) | -1 punct |

---

## 5. Grila Finală Săptămânii

| Componentă | Pondere | Max Puncte |
|------------|---------|------------|
| Laborator practic | 50% | 10 |
| Artefact proiect echipă | 50% | 10 |
| **Total** | 100% | **20** |

**Notare**: Punctajul se transformă în notă pe scala 1-10.

---

*Document generat pentru Săptămâna 11 – Rețele de Calculatoare*  
*Revolvix&Hypotheticalandrei*
