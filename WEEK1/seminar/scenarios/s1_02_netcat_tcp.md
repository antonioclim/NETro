# Scenariul S1.02: Server și Client cu Netcat

## Obiective

După parcurgerea acestui scenariu, studentul va putea:

1. Crea servere TCP și UDP simple cu netcat
2. Transfera date între procese folosind pipe-uri și redirectări
3. Observa diferențele practice între comunicarea TCP și UDP
4. Diagnostica probleme comune de conectivitate

## Context

Netcat (nc) este "cușitul elvețian" al diagnosticării de rețea. Permite crearea rapidă de servere și clienți pentru testare, fără a scrie cod.

**Analogie:** Netcat e ca un telefon simplu - poți suna (client) sau poți răspunde (server), fără funcții fancy. Perfect pentru teste rapide.

---

## Pași de Urmat

### Pasul 1: Server TCP Simplu (5 minute)

**👥 PAIR PROGRAMMING:** Driver execută în Terminal 1, Navigator verifică și ghidează.

**🎯 PREDICȚIE:** Ce va afișa `ss -tlnp | grep 9999` după ce pornești serverul?

**Terminal 1 (Driver - Server):**
```bash
# Pornire server pe port 9999
nc -l -p 9999
```

**Verificare (Navigator):**
```bash
# În alt terminal, verifică că serverul ascultă
ss -tlnp | grep 9999
# Output așteptat: LISTEN 0 1 0.0.0.0:9999 0.0.0.0:*
```

### Pasul 2: Client TCP (5 minute)

**Schimbați rolurile! Navigator devine Driver.**

**🎯 PREDICȚIE:** Câte pachete va trimite TCP pentru a stabili conexiunea ÎNAINTE de orice date?

**Terminal 2 (Navigator devenit Driver - Client):**
```bash
# Conectare la server
nc localhost 9999
```

**Experiment:**
1. Tastați un mesaj în Terminal 2 și apăsați Enter
2. Observați mesajul în Terminal 1
3. Tastați un răspuns în Terminal 1
4. Observați că comunicarea e bidirecțională!

**Întrebări de verificare:**
- Ce se întâmplă dacă închizi clientul cu Ctrl+C?
- Dar dacă închizi serverul?

### Pasul 3: Automatizare cu Pipe (5 minute)

```bash
# Trimitere mesaj automat
echo "Hello Server!" | nc localhost 9999

# Trimitere fișier
cat README.md | nc localhost 9999

# Trimitere cu timeout (așteaptă max 2 secunde răspuns)
echo "Test" | nc -w 2 localhost 9999
```

**🎯 PREDICȚIE:** Ce se întâmplă dacă trimiți `echo "Hello" | nc localhost 9999` când NICIUN server nu ascultă?

---

## 🗳️ PEER INSTRUCTION: Comportament Port Închis

**Scenariu:** Rulezi `nc localhost 9999` dar NICIUN proces nu ascultă pe portul 9999.

**Întrebare:** Ce mesaj vei primi?

| Opțiune | Răspuns |
|---------|---------|
| **A** | Comanda așteaptă la infinit fără output |
| **B** | "Connection refused" |
| **C** | "Connection timed out" |
| **D** | Conexiunea se stabilește dar nu poți trimite date |

<details>
<summary>🎯 Răspuns</summary>

**Corect: B** - "Connection refused"

Când portul e închis (niciun proces în LISTEN), kernel-ul răspunde cu TCP RST. Netcat interpretează asta ca "Connection refused".

**Opțiunea A** - ar fi cazul cu firewall DROP (pachetele sunt ignorate)
**Opțiunea C** - ar fi cazul cu host inaccesibil sau firewall DROP
**Opțiunea D** - imposibil fără handshake complet
</details>

---

### Pasul 4: UDP vs TCP (10 minute)

**Server UDP:**
```bash
# Terminal 1 - Server UDP
nc -u -l -p 8888
```

**Client UDP:**
```bash
# Terminal 2 - Client UDP
nc -u localhost 8888
```

**Observații importante:**
- NU există handshake (nu vezi SYN/SYN-ACK/ACK în tshark)
- Fiecare mesaj e independent
- Dacă serverul nu rulează, clientul NU primește eroare imediat!

**Experiment comparativ:**

| Aspect | TCP (`nc -l -p 9999`) | UDP (`nc -u -l -p 8888`) |
|--------|----------------------|-------------------------|
| Handshake | Da (3 pachete) | Nu |
| Conexiune persistentă | Da | Nu |
| Feedback la trimitere | Da | Nu |
| Pachete pentru "Hello" | ~8 | 1 |

---

## 📝 PARSONS PROBLEM: Script de Transfer Fișier

**Sarcină:** Aranjează comenzile pentru a transfera `data.txt` de pe "server" pe "client" folosind netcat.

**Comenzi amestecate:**
```
D) nc localhost 5000 > received.txt
C) nc -l -p 5000 < data.txt
B) diff data.txt received.txt
A) echo "Test content" > data.txt
E) echo "Transfer complet!"
```

**Notă:** Comenzile C și D trebuie rulate în terminale SEPARATE, simultan!

<details>
<summary>✅ Soluție</summary>

**Ordinea:** A → (C și D simultan) → B → E

1. **A** - Creează fișierul sursă
2. **C** - Pornește "serverul" care trimite fișierul (Terminal 1)
3. **D** - Pornește "clientul" care primește fișierul (Terminal 2)
4. **B** - Verifică că fișierele sunt identice
5. **E** - Confirmă succesul

**Script complet:**
```bash
# Pregătire
echo "Test content" > data.txt

# Terminal 1 (server - trimite)
nc -l -p 5000 < data.txt &

# Terminal 2 (client - primește)
sleep 1  # Așteaptă serverul să pornească
nc localhost 5000 > received.txt

# Verificare
diff data.txt received.txt && echo "Transfer complet!"
```
</details>

---

## 🔍 TRACING EXERCISE: Ce se întâmplă în rețea?

**Scenariul:** Rulezi următoarele comenzi:

```bash
# Terminal 1
nc -l -p 5000

# Terminal 2
echo "Hi" | nc localhost 5000
```

**Întrebări (fără a rula comenzile):**

1. Câte pachete TCP vei vedea în total în tshark?
   - a) 1-2 pachete
   - b) 5-7 pachete
   - c) 8-10 pachete
   - d) > 10 pachete

2. Care va fi PRIMUL pachet capturat?
   - a) Pachet cu datele "Hi"
   - b) Pachet SYN de la client
   - c) Pachet SYN-ACK de la server
   - d) Pachet ACK

3. Ce flag-uri TCP vor fi pe pachetul care conține "Hi"?
   - a) SYN
   - b) ACK
   - c) PSH, ACK
   - d) FIN

<details>
<summary>✅ Răspunsuri</summary>

1. **c) 8-10 pachete** - Detaliere:
   - 3 pachete handshake (SYN, SYN-ACK, ACK)
   - 1-2 pachete date (PSH-ACK) + ACK
   - 4 pachete terminare (FIN-ACK în ambele direcții)

2. **b) Pachet SYN de la client** - Clientul inițiază conexiunea

3. **c) PSH, ACK** - PSH = "push" (datele trebuie livrate imediat aplicației), ACK = confirmă secvența anterioară
</details>

---

## 🐛 DEBUG CHALLENGE: De ce nu merge?

**Scenariul:** Un coleg încearcă să facă un server TCP dar primește erori.

```bash
# Încercare 1
$ nc -l -p 80
nc: Permission denied

# Încercare 2 (după ce a schimbat portul)
$ nc -l -p 9999
nc: Address already in use
```

**Întrebări:**

1. De ce "Permission denied" pe portul 80?
2. De ce "Address already in use" pe 9999?
3. Cum rezolvi fiecare problemă?

<details>
<summary>✅ Soluții</summary>

**Problema 1: Permission denied**
- Porturile sub 1024 sunt "privilegiate" și necesită root
- Soluție: `sudo nc -l -p 80` SAU folosește port > 1024

**Problema 2: Address already in use**
- Alt proces folosește deja portul 9999
- Diagnostic: `ss -tlnp | grep 9999`
- Soluție: 
  - Oprește procesul existent: `kill <PID>`
  - SAU folosește alt port: `nc -l -p 9998`
  - SAU așteaptă (TIME_WAIT durează ~2 minute)
</details>

---

## Mini HTTP Server (Challenge)

Creează un server HTTP minimal doar cu bash și netcat:

```bash
#!/bin/bash
# mini_http.sh

while true; do
    echo -e "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n<h1>Hello from netcat!</h1>" | nc -l -p 8080 -q 1
done
```

**Test:**
```bash
# Terminal 1
bash mini_http.sh

# Terminal 2 sau browser
curl http://localhost:8080
```

---

## Recapitulare Comenzi

| Comandă | Scop |
|---------|------|
| `nc -l -p PORT` | Server TCP pe PORT |
| `nc HOST PORT` | Client TCP către HOST:PORT |
| `nc -u -l -p PORT` | Server UDP |
| `nc -u HOST PORT` | Client UDP |
| `nc -zv HOST PORT` | Scanare port (verificare deschis) |
| `nc -w TIMEOUT` | Timeout pentru operații |
| `echo "msg" \| nc ...` | Trimitere automată mesaj |

---

## Debugging Frecvent

| Simptom | Cauză | Soluție |
|---------|-------|---------|
| Connection refused | Server nu rulează | Verifică cu `ss -tlnp` |
| Permission denied | Port < 1024 | Folosește sudo sau port mai mare |
| Address already in use | Port ocupat | Verifică cu `ss -tlnp \| grep PORT` |
| Nu apare nimic | Firewall/alt terminal | Verifică interfața și portul |

---

## Ce Urmează

În scenariul următor vom captura și analiza traficul cu tshark pentru a vedea exact ce pachete se trimit.

---

*Timp estimat: 25 minute*
*Nivel: Începător-Mediu*
