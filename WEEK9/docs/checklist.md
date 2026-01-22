# Checklist Cadru Didactic – Săptămâna 9

## Înainte de sesiune (24-48h)

### Verificare materiale

- [ ] Starterkit-ul S9 este actualizat și funcțional
- [ ] Toate fișierele din `server-files/` sunt prezente și netrunce
- [ ] `make verify` trece pe mașina de prezentare
- [ ] Versiunile software corespund (Python 3.8+, Docker 20.10+)
- [ ] Prezentările HTML se încarcă corect (theory.html, seminar.html, lab.html)

### Verificare infrastructură

- [ ] VM-ul de laborator pornește în mai puțin de 2 minute
- [ ] Docker daemon rulează și are imagini pre-construite
- [ ] Wireshark/tshark funcționează pe interfața loopback
- [ ] Conexiunea la internet este disponibilă (pentru pip/docker pull dacă e nevoie)
- [ ] Proiectorul/screen sharing funcționează

### Pregătire pedagogică

- [ ] Am parcurs materialul și am identificat punctele dificile
- [ ] Am pregătit întrebări de verificare pentru momentele cheie
- [ ] Am identificat exercițiile pe care le voi demonstra live
- [ ] Am soluțiile pentru toate exercițiile (inclusiv challenge)
- [ ] Am pregătit exemple de greșeli frecvente pentru debugging live

### Pregătire logistică

- [ ] Lista de prezență pregătită
- [ ] Știu distribuția pe grupe/echipe pentru proiectul de semestru
- [ ] Am verificat dacă sunt studenți cu întârzieri de recuperat

---

## În timpul sesiunii

### Deschidere (5 min)

- [ ] Salut și prezentare obiective
- [ ] Recapitulare scurtă săptămâna anterioară (L4 Transport → L5/L6)
- [ ] Anunț artefact săptămânal pentru proiectul de echipă

### Curs teoretic (dacă e cazul) (40-50 min)

- [ ] Slide-urile se afișează corect
- [ ] Demo-uri live funcționează (sau am backup video)
- [ ] Pauze pentru întrebări la fiecare secțiune majoră
- [ ] Mini-quiz interactiv la mijlocul prezentării

### Seminar/Laborator (60-90 min)

**Faza 1: Setup (10 min)**
- [ ] Toți studenții au acces la starterkit
- [ ] `make verify` trece pe cel puțin 80% din mașini
- [ ] Rezolvare rapidă probleme comune de setup

**Faza 2: Demonstrație ghidată (20 min)**
- [ ] Demo endianness executat și explicat
- [ ] Server pornit, client conectat
- [ ] Secvență AUTH → LIST → GET demonstrată

**Faza 3: Lucru individual/perechi (40-50 min)**
- [ ] Studenții lucrează la pașii 3-5 din lab.html
- [ ] Circul printre studenți pentru suport
- [ ] Notez problemele frecvente pentru discuție finală

**Faza 4: Debugging colectiv (10 min)**
- [ ] Adresez 2-3 probleme frecvente identificate
- [ ] Demonstrez tehnici de debugging (tshark, logs)

### Închidere (5-10 min)

- [ ] Recapitulez "Ce am învățat"
- [ ] Anunț termen predare artefact (dacă există)
- [ ] Întrebări finale
- [ ] Feedback rapid (ce a mers bine / ce poate fi îmbunătățit)

---

## După sesiune

### Imediat (same day)

- [ ] Notez problemele tehnice întâmpinate pentru remediere
- [ ] Actualizez FAQ dacă au apărut întrebări noi
- [ ] Salvez capturile de ecran interesante pentru viitoare sesiuni

### În 24-48h

- [ ] Verific predările (dacă există deadline)
- [ ] Răspund la întrebările primite pe email/forum
- [ ] Actualizez materialele cu corecții dacă e cazul

### Săptămânal

- [ ] Sincronizez cu ceilalți titulari despre progres
- [ ] Verific alinierea cu proiectul de semestru
- [ ] Pregătesc teaser pentru săptămâna următoare

---

## Întrebări de verificare pentru studenți

### Nivel înțelegere (poate fi adresată oricând)

1. Care este diferența între o conexiune TCP și o sesiune la nivel aplicație?
2. De ce folosim Big Endian pentru protocoale de rețea?
3. Ce rol are câmpul CRC-32 în protocolul nostru?

### Nivel aplicare (după demo)

4. Ce comandă tshark folosim pentru a filtra doar pachetele cu payload?
5. Cum verificăm că serverul ascultă pe portul corect?
6. Ce se întâmplă dacă trimitem o comandă fără a fi autentificați?

### Nivel analiză (în timpul laboratorului)

7. Analizând captura, puteți identifica momentul autentificării?
8. Câți bytes are header-ul protocolului nostru și de ce?
9. Ce observați în diferența de dimensiune între fișierul original și cel comprimat?

### Nivel sinteză (pentru avansați)

10. Cum ați modifica protocolul pentru a suporta criptare?
11. Ce dezavantaje are abordarea noastră cu un singur canal (față de FTP cu două)?

---

## Capcane și soluții rapide

| Capcană | Semn | Soluție rapidă |
|---------|------|----------------|
| Docker nu pornește | "Cannot connect to Docker daemon" | `sudo systemctl start docker` |
| Port ocupat | "Address already in use" | `sudo lsof -i :9021 && kill <PID>` |
| Permisiuni tshark | "Permission denied" | `sudo usermod -aG wireshark $USER` |
| Python greșit | ImportError pentru struct | `python3` în loc de `python` |
| Fișiere lipsă | FileNotFoundError | Verifică că ești în directorul corect |

---

## Note pentru îmbunătățire continuă

### Ce a funcționat bine

(Completați după fiecare sesiune)

### Ce necesită ajustări

(Completați după fiecare sesiune)

### Sugestii de la studenți

(Completați din feedback)
