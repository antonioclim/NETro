# Analiză Comparativă a Arhivelor S11

## Inventar Arhive Analizate

| Arhivă | Dimensiune | Focus Principal | Puncte Forte |
|--------|------------|-----------------|--------------|
| S11v1andrei | 156KB | Teorie FTP/DNS/SSH | Diagrame PlantUML, 4 scenarii Docker complete |
| S11v2starterkit | 29KB | Structură standard | Organizare curată, Mininet de bază |
| S11v3DEMOGPTstarterkit | 40KB | Demo-uri | python/apps, configs nginx multiple |
| S11v3starterkit_ideal | 100KB | Structură completă | Makefile elaborat, HTML prezentări |

## Decizii de Integrare

### 1. Structura Proiectului
- **Bază adoptată**: v3_ideal (cea mai completă și organizată)
- **Motivație**: Structură clară, Makefile complet, separare curs/seminar

### 2. Conținut Teoretic
- **Surse integrate**: v1_andrei/c11.md + v3_ideal/teoria/
- **Rezultat**: Documentație completă FTP, DNS, SSH cu diagrame
- **Modernizare**: Adăugare DNSSEC, DoH/DoT, SFTP vs FTPS

### 3. Scenarii Docker
- **FTP Demo**: v1_andrei/scenario-ftp-baseline (pyftpdlib complet)
- **DNS Demo**: v1_andrei/scenario-dns-ttl-caching (BIND + Unbound)
- **SSH Demo**: v1_andrei/scenario-ssh-provision (Paramiko)
- **Nginx/LB**: v2_starterkit + v3_ideal (combinat)

### 4. Python Exercises
- **Backend HTTP**: v2_starterkit (ex_11_01.py) + îmbunătățiri
- **Load Balancer**: v3_ideal (ex_11_02_loadbalancer.py) - 3 algoritmi
- **DNS Client**: v3_ideal (ex_11_03_dns_client.py) - RFC 1035

### 5. Mininet Topologii
- **Bază**: v2_starterkit/topo_11_base.py
- **Extended**: v3_ideal/topo_11_extended.py (failover)

### 6. HTML Prezentări
- **Stil**: Creat nou, inspirat de v3_ideal
- **Paleta**: Dark theme (#0f172a), accent albastru (#1e40af)
- **Funcționalități**: Navigare keyboard, progress bar, quiz-uri

## Log de Decizii

1. **Adoptat Python 3.10+** pentru compatibilitate cu type hints și match statements
2. **Eliminat `version:` din docker-compose.yml** (deprecated în Compose V2)
3. **Adăugat --break-system-packages** la pip pentru Ubuntu 24.04
4. **Unificat porturile**: LB=8080, backends=8001-8003, FTP=2121
5. **Standardizat README.md** cu structură consistentă
6. **Adăugat health checks** la toate exercițiile Python
7. **Creat Makefile unificat** cu 30+ targets
8. **Integrat verificare mediu** (make verify)
9. **Adăugat logging** în toate scripturile pentru debugging
10. **Creat slide outlines** pentru PowerPoint/reveal.js
11. **Documentat troubleshooting** pentru erori comune
12. **Adăugat benchmark** cu Apache Bench și fallback Python
13. **Standardizat naming** (ex_11_XX_nume.py)
14. **Creat DOCX comprehensiv** cu două perspective (instructor/student)
15. **Adăugat rubrici de evaluare** cu punctaje detaliate

## Presupuneri

1. Mediul de rulare este Ubuntu 22.04+ LTS (CLI-only VM recomandată)
2. Studenții au acces la Docker și drepturi sudo pentru Mininet
3. Conexiune Internet disponibilă pentru pull imagini Docker
4. Python 3.10+ instalat (standard în Ubuntu 22.04+)
5. Cunoștințe anterioare: TCP/IP, socket programming, HTTP basics
6. Timpul alocat: 90 min curs + 90 min seminar + 100 min laborator
7. Proiectul de echipă este în desfășurare și necesită artefact incremental
8. Evaluarea include atât componenta individuală cât și pe echipă

---
*Revolvix&Hypotheticalandrei*
