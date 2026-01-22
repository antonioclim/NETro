# Checklist Cadru Didactic – Săptămâna 10

## Înainte de sesiune

### Cu 1-2 zile înainte

- [ ] Verificare actualizări Docker images: `docker compose pull`
- [ ] Test complet infrastructură pe mașina de demonstrație
- [ ] Pregătire backup plan (VM snapshot sau docker images salvate)
- [ ] Verificare slide-uri și materiale actualizate
- [ ] Pregătire fișiere exemplu pentru demonstrații

### Cu 30 minute înainte

- [ ] Pornire infrastructură Docker: `make docker-up`
- [ ] Verificare toate serviciile active: `docker compose ps`
- [ ] Test rapid DNS, SSH, FTP
- [ ] Deschidere terminale necesare (3-4)
- [ ] Pregătire editor cu script-uri demo
- [ ] Verificare proiector/screen sharing funcțional

### Verificare rapidă funcționalitate

```bash
# Toate trebuie să returneze OK
make check
make verify
curl -s http://localhost:8000/ | head -1
dig @localhost -p 5353 myservice.lab.local +short
ssh -p 2222 labuser@localhost "echo OK" 
ftp localhost 2121 <<< "user labftp
labftp
quit"
```

---

## În timpul sesiunii

### Curs (50 minute)

| Timp | Subiect | Verificare |
|------|---------|------------|
| 0-5 | Introducere, obiective | Studenții atenți |
| 5-15 | HTTP semantics review | Întrebare: „Ce înseamnă idempotent?" |
| 15-25 | REST maturity levels | Întrebare: „Ce nivel e API-ul nostru curent?" |
| 25-35 | CORS și debugging | Demo curl vs browser |
| 35-45 | HTTP/2, WebSocket | Întrebare: „Când WebSocket vs polling?" |
| 45-50 | Recapitulare, întrebări | Participare activă |

### Seminar/Laborator (100 minute)

| Timp | Activitate | Checkpoint |
|------|------------|------------|
| 0-10 | Setup mediu, verificări | Toți au Docker funcțional |
| 10-25 | DNS: implicit vs custom | Output dig corect |
| 25-40 | SSH manual + Paramiko | Conectare reușită |
| 40-55 | Port forwarding demo | curl prin tunel |
| 55-70 | FTP transfer | Upload/download OK |
| 70-85 | Exerciții individuale | Asistență la nevoie |
| 85-100 | Recapitulare, Q&A | Clarificări finale |

---

## Întrebări de control

### Verificare înțelegere

1. „Care este diferența între DNS-ul implicit Docker și serverul nostru custom?"
   - **Răspuns așteptat:** DNS implicit știe doar serviciile din compose; custom poate defini orice zone.

2. „De ce folosim mod pasiv FTP în Docker?"
   - **Răspuns așteptat:** Modul activ presupune că serverul inițiază conexiunea de date către client, ceea ce nu funcționează prin NAT/firewall.

3. „Ce avantaj aduce tunelarea SSH față de expunerea directă a porturilor?"
   - **Răspuns așteptat:** Securitate (criptare), acces selectiv, nu necesită modificări firewall.

### Nivel aplicare

4. „Cum ai accesa o bază de date care rulează pe port 5432 într-un container neexpus?"
   - **Răspuns așteptat:** `ssh -L 5432:db-container:5432 user@ssh-server`

5. „Cum verifici programatic dacă un serviciu SSH este activ?"
   - **Răspuns așteptat:** Paramiko connect + timeout handling sau tcp connect pe port 22.

### Nivel analiză

6. „De ce FTP arată credențialele în captură dar SSH nu?"
   - **Răspuns așteptat:** FTP transmite în plaintext; SSH criptează tot traficul după handshake.

---

## Capcane frecvente

### La studenți

| Problemă | Cauză | Soluție rapidă |
|----------|-------|----------------|
| „Docker command not found" | Docker Desktop nepornit | Start Docker Desktop |
| „Port already in use" | Alt serviciu pe port | `lsof -i :2222`, kill sau schimbă port |
| „Connection refused" | Serviciu nepornit | `docker compose up -d` |
| „Permission denied" | User greșit sau parolă | Verifică credențiale în compose |
| „Name not resolved" | Container în altă rețea | Verifică network în compose |

### La demonstrații

- **Plan B pentru DNS:** Folosește IP direct dacă DNS-ul nu funcționează
- **Plan B pentru SSH:** Demonstrează cu container debug intern
- **Plan B pentru FTP:** Folosește curl pentru upload/download simplu

---

## După sesiune

### Imediat după

- [ ] Salvare întrebări neadresate pentru follow-up
- [ ] Notare puncte de confuzie observate
- [ ] Cleanup infrastructură: `make docker-down`

### Până la sesiunea următoare

- [ ] Răspuns la întrebări rămase (forum, email)
- [ ] Verificare livrabile trimise
- [ ] Pregătire feedback pentru probleme comune

---

## Resurse backup

### Dacă Docker nu funcționează deloc

1. Folosește VM pregătită cu totul instalat
2. Demo pe mașina ta cu screen share
3. Cod walk-through fără execuție live

### Dacă rețeaua e problematică

1. Verifică firewall institutional
2. Folosește hotspot mobil ca backup
3. Demo offline cu captures pre-făcute

### Link-uri utile în sesiune

- Docker docs: https://docs.docker.com/compose/
- Paramiko: https://docs.paramiko.org/
- pyftpdlib: https://pyftpdlib.readthedocs.io/
- dig manual: `man dig`

---

## Timing sugestiv curs

```
[00:00-05:00] Introducere, context săptămână
[05:00-12:00] HTTP review: metode, coduri, headere
[12:00-20:00] REST levels + anti-patterns
[20:00-28:00] CORS: de ce și cum
[28:00-35:00] HTTP/2 vs HTTP/1.1
[35:00-42:00] WebSocket basics
[42:00-48:00] Recapitulare + întrebări
[48:00-50:00] Preview seminar
```

## Timing sugestiv seminar

```
[00:00-10:00] Setup, verificare mediu
[10:00-25:00] DNS exercises
[25:00-45:00] SSH + Paramiko
[45:00-60:00] Port forwarding
[60:00-75:00] FTP transfer
[75:00-90:00] Integration + Q&A
[90:00-100:00] Cleanup, wrap-up
```

---

*Material pentru uz intern – Rețele de Calculatoare, ASE București*

*Revolvix&Hypotheticalandrei*
