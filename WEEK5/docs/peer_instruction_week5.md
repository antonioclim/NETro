# Întrebări Peer Instruction — Săptămâna 5

Aceste întrebări sunt proiectate pentru discuții în grupuri mici. Folosește-le în seminar sau laborator pentru a identifica și corecta misconceptii.

**Mod de utilizare:**
1. Prezintă întrebarea (1 min)
2. Vot individual — studenții aleg răspunsul fără să discute (1 min)
3. Discuție în perechi — studenții își explică reciproc alegerea (3 min)
4. Revot — studenții pot schimba răspunsul (30 sec)
5. Explicație finală — discutați răspunsul corect și de ce distractorii sunt greșiți (2 min)

---

## PI-5.1: Număr de hosturi

### Scenariu
Ai primit rețeaua `192.168.10.0/26` pentru departamentul IT.

### Întrebare
Câte dispozitive poți conecta efectiv în această subrețea?

### Opțiuni
- **A)** 64
- **B)** 62 ✓
- **C)** 256
- **D)** 30

---

### Note instructor (nu pentru studenți)

**Target:** ~50-60% corect la primul vot

**Analiza distractorilor:**
- **A (64):** Confundă total adrese (2^6) cu hosturi utilizabili. Nu a scăzut adresa de rețea și broadcast.
- **C (256):** Confundă /26 cu /24 (2^8 = 256). Nu înțelege cum funcționează prefixul.
- **D (30):** Confundă /26 cu /27 (30 hosturi pentru /27). Eroare de calcul la puterea lui 2.

**După discuție:** Subliniază formula: `hosturi = 2^(32-prefix) - 2`. Cele 2 scăzute sunt ÎNTOTDEAUNA adresa de rețea (primul) și broadcast (ultimul).

**Timing total:** ~8 minute

---

## PI-5.2: Adresa de broadcast

### Scenariu
Ai adresa `172.16.50.12/21` și trebuie să trimiți un mesaj tuturor din subrețea.

### Întrebare
Care este adresa de broadcast pentru această subrețea?

### Opțiuni
- **A)** 172.16.50.255
- **B)** 172.16.55.255 ✓
- **C)** 172.16.63.255
- **D)** 172.16.48.255

---

### Note instructor

**Target:** ~40-50% corect la primul vot (mai dificilă)

**Analiza distractorilor:**
- **A (172.16.50.255):** Presupune greșit că broadcast e .255 în ultimul octet al IP-ului dat. Nu a calculat efectiv.
- **C (172.16.63.255):** Calculează greșit wildcard-ul — confuzie cu /19 (ar fi 0.0.31.255 în loc de 0.0.7.255).
- **D (172.16.48.255):** Confundă adresa de rețea (172.16.48.0) cu broadcast. Pune .255 la rețea în loc să calculeze corect.

**Explicație pas cu pas:**
1. /21 → Mască: 255.255.248.0 → Wildcard: 0.0.7.255
2. Adresa de rețea (AND): 172.16.48.0
3. Broadcast (OR cu wildcard): 172.16.48.0 | 0.0.7.255 = 172.16.55.255

**Timing total:** ~8 minute

---

## PI-5.3: FLSM vs VLSM

### Scenariu
Ai rețeaua `10.0.0.0/24` și trebuie să creezi subrețele pentru:
- Departament A: 100 hosturi
- Departament B: 50 hosturi  
- Departament C: 20 hosturi
- Link router-router: 2 hosturi

### Întrebare
Ce tehnică de subnetting ar trebui să folosești și de ce?

### Opțiuni
- **A)** FLSM cu /26 (4 subrețele egale de 62 hosturi)
- **B)** VLSM cu /25, /26, /27, /30 ✓
- **C)** Nu se poate — nevoile depășesc capacitatea rețelei
- **D)** FLSM cu /27 (8 subrețele egale de 30 hosturi)

---

### Note instructor

**Target:** ~50-60% corect la primul vot

**Analiza distractorilor:**
- **A (/26 = 62 hosturi):** Nu acoperă nevoile Departamentului A (100 hosturi). Studenții care aleg asta nu au verificat că fiecare subrețea îndeplinește cerința.
- **C (nu se poate):** Total necesar = 172 hosturi. /24 oferă 254. Încape lejer! Studenții care aleg asta au adunat greșit sau nu înțeleg capacitatea /24.
- **D (/27 = 30 hosturi):** Nu acoperă nici Dept A (100) nici Dept B (50). Eroare similară cu A.

**De ce VLSM?**
- 100 hosturi → nevoie /25 (126 disponibili)
- 50 hosturi → nevoie /26 (62 disponibili)
- 20 hosturi → nevoie /27 (30 disponibili)
- 2 hosturi → nevoie /30 (2 disponibili)
- Total alocat: 128+64+32+4 = 228 < 256 ✓

**Timing total:** ~8 minute

---

## PI-5.4: TTL și routing

### Scenariu
Host h1 trimite un ping către h2 care se află la 3 routere distanță. TTL inițial setat de sistemul de operare este 64.

### Întrebare
Ce valoare TTL va avea pachetul ICMP Echo Request când ajunge la h2?

### Opțiuni
- **A)** 64
- **B)** 61 ✓
- **C)** 63
- **D)** 60

---

### Note instructor

**Target:** ~60-70% corect la primul vot

**Analiza distractorilor:**
- **A (64):** Nu înțelege că TTL scade la fiecare hop. Crede că TTL rămâne constant.
- **C (63):** Crede că doar primul router decrementează, sau numără greșit.
- **D (60):** Numără greșit — include și sursă/destinație ca hop-uri, sau adună în loc să scadă.

**Explicație:**
- TTL inițial: 64
- După router 1: 63
- După router 2: 62
- După router 3: 61 (ajunge la h2)

**Analogie:** TTL e ca un bilet de metro cu limită de stații. La fiecare router (stație), se ștampilează — scade cu 1.

**Întrebare bonus:** Ce TTL va avea reply-ul când se întoarce la h1? (Tot 61, pentru că h2 setează un nou TTL pentru reply)

**Timing total:** ~8 minute

---

## PI-5.5: Comprimarea IPv6

### Scenariu
Trebuie să documentezi adresa unui server: `2001:0db8:0000:0000:0000:0000:0000:0001`

### Întrebare
Care este forma comprimată **corectă** și **minimă**?

### Opțiuni
- **A)** 2001:db8:0:0:0:0:0:1
- **B)** 2001:db8::1 ✓
- **C)** 2001:db8:::1
- **D)** 2001:db8::0001

---

### Note instructor

**Target:** ~50-60% corect la primul vot

**Analiza distractorilor:**
- **A (fără ::):** Comprimare parțială — a eliminat zerourile de început din fiecare grup, dar nu a folosit `::` pentru grupurile consecutive de zerouri. E validă, dar nu minimă.
- **C (:::):** Sintaxă invalidă! Nu poți avea `:::`. `::` apare o singură dată și înlocuiește una sau mai multe grupuri de 0000.
- **D (::0001):** Greșit — după `::` nu păstrezi zerourile de început. Ar trebui să fie `::1`, nu `::0001`.

**Reguli de reținut:**
1. Elimină zerourile de început din fiecare grup: 0db8 → db8, 0001 → 1
2. Înlocuiește cea mai lungă secvență de grupuri 0000 cu `::` (o singură dată!)
3. Dacă sunt două secvențe egale de zerouri, o comprimi pe prima

**Timing total:** ~8 minute

---

## Sumar pentru instructor

| Întrebare | Concept testat | Misconceptie principală |
|-----------|----------------|-------------------------|
| PI-5.1 | Calcul hosturi | Uitarea de -2 (rețea + broadcast) |
| PI-5.2 | Broadcast address | Calcul incorect wildcard/AND/OR |
| PI-5.3 | FLSM vs VLSM | Nu verifică dacă subrețelele acoperă nevoile |
| PI-5.4 | TTL | Nu înțelege decrementarea per hop |
| PI-5.5 | IPv6 comprimare | Sintaxă :: și zerouri de început |

**Recomandare:** Folosește 2-3 întrebări per sesiune de seminar (15-25 minute). Nu le folosi pe toate în aceeași zi — lasă timp pentru discuții de calitate.

---

*Material pentru Peer Instruction — Săptămâna 5*  
*Rețele de calculatoare, ASE-CSIE*
