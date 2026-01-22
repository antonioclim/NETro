# Întrebări Peer Instruction – Săptămâna 11

## Instrucțiuni pentru Instructor

1. Afișează întrebarea (1 min)
2. Vot individual – fără discuții (1 min)
3. Discuție în perechi (3 min)
4. Revot (30 sec)
5. Explicație cu accent pe misconceptii (2 min)

**Țintă**: ~50% răspunsuri corecte la primul vot

---

## PI-1: FTP Mode Selection 🗳️

### Scenariu
Un dezvoltator încearcă să se conecteze cu un client FTP de pe laptopul său (aflat în spatele unui router NAT casnic) la un server FTP public. Conexiunea de control se stabilește, dar `LIST` și `RETR` eșuează cu timeout.

### Întrebare
Ce mod FTP ar trebui să folosească și de ce?

**A)** Modul activ — serverul are IP public, deci poate iniția conexiunea de date  
**B)** Modul pasiv — clientul inițiază ambele conexiuni, ocolind problema NAT  
**C)** Nu contează modul — problema e la firewall-ul serverului  
**D)** Trebuie să deschidă portul 20 pe routerul său  

### Răspuns corect: B

### Analiza distractorilor (pentru instructor)
- **A**: Misconceptie — serverul poate iniția, dar routerul NAT al clientului blochează conexiunea incoming pe portul efemer
- **C**: Misconceptie — firewall-ul serverului nu e relevant dacă conexiunea de control funcționează
- **D**: Misconceptie — portul 20 e pentru modul activ, și oricum portul clientului e dinamic

### Explicație post-vot
Modul pasiv rezolvă NAT pentru că CLIENTUL inițiază AMBELE conexiuni (control + date). În modul activ, serverul încearcă să se conecteze la un port al clientului, dar routerul NAT nu știe să ruteze acel pachet înapoi.

### Timing: 8 minute total

---

## PI-2: DNS TTL Trade-off 🗳️

### Scenariu
Administrezi DNS pentru `api.exemplu.ro`. Serverul API se mută pe un IP nou mâine la ora 10:00. Acum e ora 18:00 și TTL-ul curent e 86400 secunde (24 ore).

### Întrebare
Ce strategie minimizează downtime-ul pentru utilizatori?

**A)** Schimbi IP-ul mâine la 10:00 și aștepți propagarea  
**B)** Reduci TTL la 300s acum, schimbi IP-ul mâine, apoi revii la TTL mare  
**C)** Schimbi IP-ul acum — până mâine se propagă  
**D)** TTL-ul nu afectează propagarea, doar performanța cache  

### Răspuns corect: B

### Analiza distractorilor
- **A**: Misconceptie — clienții cu cache vechi vor avea downtime până la 24h după schimbare
- **C**: Misconceptie — serverul vechi trebuie să funcționeze până la migrare; schimbarea prematură creează downtime imediat
- **D**: Misconceptie — nu înțelege că TTL determină cât timp rămâne IP-ul vechi în cache

### Explicație post-vot
TTL mic = propagare rapidă dar mai multe query-uri. Strategia e:
1. Scade TTL cu cel puțin TTL_curent înainte de schimbare (aici, cu 24h înainte = acum)
2. Așteaptă ca noul TTL să se propage
3. Faci schimbarea de IP
4. După ce totul e stabil, crești TTL înapoi pentru performanță

### Timing: 8 minute total

---

## PI-3: SSH Known Hosts Warning 🗳️

### Scenariu
Te conectezi la serverul de producție și primești:

```
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@    WARNING: REMOTE HOST IDENTIFICATION HAS CHANGED!     @
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
Host key verification failed.
```

### Întrebare
Care e cea mai probabilă cauză și ce ar trebui să faci PRIMA DATĂ?

**A)** Serverul a fost reinstalat — ștergi linia din known_hosts și reconectezi  
**B)** Cineva încearcă un atac MITM — nu te conecta, contactează echipa de securitate  
**C)** Certificatul SSH a expirat — cere adminului să-l reînnoiască  
**D)** E o eroare normală — rulezi `ssh-keygen -R hostname` și ignori  

### Răspuns corect: Depinde! (întrebare de discuție)

### Note pentru instructor
Aceasta e o întrebare cu răspuns contextual — folosește-o pentru a genera discuție:
- **A**: Corect DACĂ știi sigur că serverul a fost reinstalat recent
- **B**: Corect DACĂ nu te așteptai la nicio schimbare și nu ai fost notificat
- **C**: Misconceptie — SSH nu folosește certificate X.509 implicit, ci chei de host
- **D**: Periculos — "ignori" warning-uri de securitate e o practică proastă

### Explicație post-vot
Punctul principal: Warning-ul NU trebuie ignorat automat! `known_hosts` te protejează de MITM.

**Procedura corectă:**
1. STOP — nu te conecta imediat
2. Verifică cu echipa/adminul dacă a fost vreo schimbare planificată
3. DOAR DACĂ confirmă schimbarea legitimă, ștergi vechea intrare
4. La reconectare, verifică noul fingerprint

### Timing: 10 minute total (include discuție extinsă)

---

## PI-4: Load Balancer Algorithm Selection 🗳️

### Scenariu
Ai 3 backend-uri identice ca hardware. Un load balancer distribuie cereri. Backend-ul 1 procesează cereri în medie în 50ms, iar backend-urile 2 și 3 în 200ms fiecare (sunt mai încărcate cu alte task-uri). Primești 100 cereri noi.

### Întrebare
Cu ce algoritm vei obține cel mai mic timp mediu de răspuns pentru cele 100 cereri?

**A)** Round Robin — distribuție egală, deci timp egal  
**B)** Least Connections — trimite mai multe cereri la backend-ul rapid  
**C)** IP Hash — consistent, fără overhead de decizie  
**D)** Random — distribuție statistică uniformă  

### Răspuns corect: B

### Analiza distractorilor
- **A**: Misconceptie — RR distribuie egal numeric, dar nu ține cont de viteza de procesare; va trimite 33-33-34 cereri indiferent de load
- **C**: Misconceptie — IP hash e pentru sticky sessions, nu optimizare performanță
- **D**: Misconceptie — random distribuie uniform, similar cu RR, nu optimizează pentru latență

### Explicație post-vot
**Least Connections** observă că:
- Backend 1 termină cereri în 50ms → eliberează conexiunea rapid → are mai puține conexiuni active
- Backend-urile 2-3 termină în 200ms → conexiunile "stau" mai mult → par mai ocupate

Rezultat: Backend-ul rapid primește automat mai multe cereri, optimizând timpul total.

### Timing: 8 minute total

---

## PI-5: DNS Record Type Selection 🗳️

### Scenariu
Vrei ca `mail.exemplu.ro` să rezolve la același IP ca `exemplu.ro`, fără să hardcodezi IP-ul în două locuri. Dacă schimbi IP-ul lui `exemplu.ro`, vrei ca `mail.exemplu.ro` să se actualizeze automat.

### Întrebare
Ce tip de înregistrare DNS folosești pentru `mail.exemplu.ro`?

**A)** A record cu IP-ul serverului  
**B)** CNAME record care pointează la `exemplu.ro`  
**C)** MX record care pointează la `exemplu.ro`  
**D)** NS record care delegă la `exemplu.ro`  

### Răspuns corect: B

### Analiza distractorilor
- **A**: Funcționează tehnic, dar nu e DRY — dacă schimbi IP-ul, trebuie să actualizezi în 2 locuri
- **C**: Misconceptie — MX e pentru email routing (specifică serverul de mail pentru un domeniu), nu pentru alias
- **D**: Misconceptie — NS e pentru delegare de zone DNS, nu pentru alias de nume

### Explicație post-vot
**CNAME = Canonical Name = alias**

Când cineva interogează `mail.exemplu.ro`:
1. DNS răspunde: "mail.exemplu.ro e alias pentru exemplu.ro"
2. Clientul interogează apoi `exemplu.ro`
3. Primește IP-ul real

Avantaj: Schimbi IP-ul doar într-un loc (la A record-ul pentru `exemplu.ro`).

**Atenție**: Nu poți pune CNAME pe apex domain (ex: `exemplu.ro` direct) — doar pe subdomenii.

### Timing: 8 minute total

---

## Statistici Așteptate (pentru calibrare)

| Întrebare | First Vote Target | Dificultate | Timp |
|-----------|-------------------|-------------|------|
| PI-1 (FTP modes) | 40-50% | Medie | 8 min |
| PI-2 (DNS TTL) | 30-40% | Grea | 8 min |
| PI-3 (SSH known_hosts) | 50-60% | Medie (discuție) | 10 min |
| PI-4 (LB algorithms) | 45-55% | Medie | 8 min |
| PI-5 (DNS records) | 55-65% | Ușoară | 8 min |

**Total timp Peer Instruction: ~42 minute** (selectează 2-3 pentru o sesiune de laborator)

---

## Recomandări de Utilizare

### Pentru laborator de 2 ore:
- PI-1 (FTP) — la începutul secțiunii FTP
- PI-4 (LB algorithms) — după demo-ul round robin

### Pentru laborator de 3 ore:
- PI-1 (FTP)
- PI-2 (DNS TTL) — înainte de demo DNS
- PI-4 (LB algorithms)

### Pentru curs teoretic:
- PI-2 (DNS TTL)
- PI-3 (SSH) — excelent pentru discuții despre securitate
- PI-5 (DNS records)

---

*Material pentru Peer Instruction – Săptămâna 11*  
*Rețele de Calculatoare, ASE-CSIE*
