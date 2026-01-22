# Checklist Cadru Didactic - Săptămâna 8

## Înainte de curs/seminar

### Pregătire tehnică (cu 1-2 zile înainte)
- [ ] Verificați că VM-ul funcționează: `make verify`
- [ ] Testați toate demo-urile manual
- [ ] Verificați conexiunea la internet (pentru eventuale descărcări)
- [ ] Pregătiți backup offline pentru tot materialul
- [ ] Testați tshark/tcpdump cu permisiuni sudo

### Materiale didactice
- [ ] Deschideți `docs/theory.html` în browser
- [ ] Deschideți `docs/seminar.html` în browser  
- [ ] Deschideți `docs/lab.html` într-un tab separat
- [ ] Pregătiți slide-urile de prezentare (opțional)
- [ ] Printați checklist-ul pentru laborator

### Setup sală
- [ ] Proiector funcțional
- [ ] Acces la consolă/terminal vizibil pentru toți
- [ ] Studenții au acces la VM sau mediul de lucru
- [ ] Whiteboard disponibil pentru diagrame ad-hoc

---

## În timpul cursului

### Introducere (10-15 min)
- [ ] Recapitulare scurtă Săptămâna 7 (rutare)
- [ ] Prezentare obiective Săptămâna 8
- [ ] Contextul nivelului transport în stiva OSI

### Teorie UDP/TCP (25-30 min)
- [ ] Slide-uri: UDP - caracteristici, header, use cases
- [ ] Slide-uri: TCP - caracteristici, header, flags
- [ ] Demonstrație: Three-way handshake cu tshark
- [ ] Întrebări de verificare: "De ce TCP are sequence numbers?"

### Teorie TLS (15 min)
- [ ] Slide-uri: Ce este TLS, de ce e important
- [ ] Slide-uri: Handshake simplificat
- [ ] Menționați HTTPS, certificate

### Teorie HTTP Server & Proxy (15-20 min)
- [ ] Slide-uri: Arhitectura server HTTP
- [ ] Slide-uri: Ce este un reverse proxy
- [ ] Slide-uri: Load balancing algorithms

### Recapitulare și întrebări (5-10 min)
- [ ] Rezumat puncte cheie
- [ ] Întrebări din audiență
- [ ] Preview pentru seminar

---

## În timpul seminarului

### Setup inițial (10 min)
- [ ] Studenții clonează/descarcă starterkit
- [ ] Verificare mediu: `make verify`
- [ ] Rezolvare probleme comune de setup

### Demo HTTP Server (25 min)
- [ ] Rulare `demo_http_server.py`
- [ ] Test cu curl (multiple cereri)
- [ ] Explicare cod: parsare request, generare response
- [ ] Demonstrație directory traversal (securitate)

### Demo Captură tshark (15 min)
- [ ] Captură handshake TCP
- [ ] Interpretare flags (SYN, SYN-ACK, ACK)
- [ ] Identificare HTTP request/response în captură

### Demo Reverse Proxy (20 min)
- [ ] Pornire 2 backend-uri
- [ ] Pornire proxy
- [ ] Demonstrație round robin
- [ ] Captură trafic prin proxy

### Exerciții ghidate (20-30 min)
- [ ] Exercițiul 1: Completare server HTTP
- [ ] Exercițiul 2: Completare proxy (pentru avansați)
- [ ] Suport individual pentru studenți blocați

### Wrap-up (5-10 min)
- [ ] Ce să pregătească pentru proiect
- [ ] Homework/exerciții suplimentare
- [ ] Întrebări finale

---

## După curs/seminar

### Imediat după
- [ ] Salvați capturi/demo-uri pentru referință
- [ ] Notați întrebări frecvente pentru FAQ
- [ ] Identificați studenți care au nevoie de suport extra

### Până la următoarea săptămână
- [ ] Verificați temele trimise
- [ ] Răspundeți la întrebări pe forum/email
- [ ] Pregătiți feedback pentru proiecte

---

## Troubleshooting frecvent

### "Port already in use"
```bash
lsof -i :8080
kill $(lsof -t -i :8080)
# sau schimbați portul
```

### "Permission denied" pentru tcpdump
```bash
sudo tcpdump ...
# sau adăugați utilizator la grupul wireshark
```

### "Module not found" Python
```bash
pip install --user <module>
# sau verificați virtual environment
```

### "Connection refused"
1. Verificați că serverul rulează: `ss -tuln | grep PORT`
2. Verificați IP-ul corect (localhost vs 0.0.0.0)
3. Verificați firewall-ul

### Mininet nu pornește
```bash
sudo mn -c  # cleanup
sudo python3 topo_....py
```

---

## Întrebări de verificare sugerate

### Nivel termeni
- Ce este un socket?
- Ce înseamnă TCP vs UDP?
- Ce este un port?

### Nivel înțelegere
- De ce TCP este "reliable"?
- Cum funcționează three-way handshake?
- Care e diferența dintre forward și reverse proxy?

### Nivel aplicare
- Scrieți codul pentru a trimite un mesaj UDP
- Cum vedeți toate conexiunile active pe un host?
- Cum capturați doar traficul HTTP?

### Nivel analiză
- De ce pierdem pachete în rețea și cum le detectăm?
- Cum identificați un atac de tip directory traversal?
- Ce se întâmplă dacă un backend cade?

### Nivel evaluare
- Care algoritm de load balancing e mai bun pentru ce scenarii?
- TCP sau UDP pentru streaming video - justificați

### Nivel creare
- Proiectați un sistem de caching pentru proxy
- Implementați health check pentru backend-uri

---

## Note pentru viitor

_Adăugați aici observații pentru următoarea iterație a cursului:_

- [ ] ...
- [ ] ...

---

© Revolvix&Hypotheticalandrei
