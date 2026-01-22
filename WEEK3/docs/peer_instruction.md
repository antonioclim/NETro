# Întrebări pentru discuții — Peer Instruction

Pentru seminar. Fiecare întrebare are distractori bazați pe greșeli reale pe care le-am văzut.

---

## Cum se folosesc

1. Afișezi întrebarea
2. Studenții votează individual (30 sec)
3. Discuție în perechi — "convinge-l pe coleg" (2-3 min)
4. Vot din nou
5. Explicație

Funcționează cel mai bine când 30-70% răspund corect la primul vot. Prea ușor sau prea greu nu generează discuție.

---

## Întrebarea 1

```python
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.sendto(b"Test", ('255.255.255.255', 5301))
```

**Ce se întâmplă?**

A) Mesajul ajunge la toți din rețea  
B) PermissionError  
C) Mesajul ajunge doar la localhost  
D) ConnectionRefusedError

<details>
<summary>După discuție</summary>

**B** — PermissionError.

De ce studenții aleg greșit:
- **A**: Confundă UDP cu "merge oriunde". OS-ul blochează broadcast implicit.
- **C**: Nu există mecanism de redirecționare la localhost.
- **D**: ConnectionRefused e pentru TCP când nimeni nu ascultă. UDP nu are conexiuni.

Fix: adaugă `sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)`
</details>

---

## Întrebarea 2

h1 trimite multicast la 224.1.1.1:5302.  
h2 a făcut JOIN.  
h3 doar bind pe 5302, fără JOIN.

**Cine primește?**

A) Ambii — sunt pe același port  
B) Doar h2  
C) Niciunul — multicast necesită configurare specială pe switch  
D) h3 primește cu întârziere

<details>
<summary>După discuție</summary>

**B** — doar h2.

De ce studenții aleg greșit:
- **A**: Confuzie majoră. Portul nu e suficient, trebuie membership în grup.
- **C**: Switch-urile moderne suportă multicast fără configurare specială la nivel mic.
- **D**: Nu există mecanism de "întârziere" pentru non-membri.

Multicast ≠ "toți care ascultă pe port". E "toți care s-au înscris în grup".
</details>

---

## Întrebarea 3

Care e ordinea CORECTĂ pentru multicast receiver?

A) socket → JOIN → bind → recv  
B) socket → bind → JOIN → recv  
C) Nu contează ordinea  
D) JOIN se face automat la bind pe adresă multicast

<details>
<summary>După discuție</summary>

**B** — socket → bind → JOIN → recv.

De ce studenții aleg greșit:
- **A**: Pare logic să te "înscrii" primul, dar kernel-ul trebuie să știe PE CE PORT să livreze.
- **C**: Ordinea chiar contează. Cu A, poți pierde pachete.
- **D**: JOIN nu e niciodată automat. Trebuie făcut explicit.

Regula: bind() pregătește "cutia poștală", JOIN spune "vreau scrisori pentru grupul X".
</details>

---

## Întrebarea 4

```python
# Sender
sock.send(b"AAAA")
time.sleep(0.1)
sock.send(b"BBBB")
```

**Ce poate primi receiver-ul cu UN recv(1024)?**

A) Exact "AAAA" (primul mesaj)  
B) "AAAABBBB" (ambele concatenate)  
C) Orice combinație de bytes  
D) Eroare — nu poți primi mai mult decât un mesaj

<details>
<summary>După discuție</summary>

**C** — orice combinație.

Receiver-ul poate primi: "A", "AAAA", "AAAAB", "AAAABBBB", etc.

De ce studenții aleg greșit:
- **A**: Presupune că TCP păstrează "granițe de mesaj". Nu păstrează.
- **B**: E posibil, dar nu garantat.
- **D**: TCP e stream de bytes, nu de mesaje.

Asta se cheamă "TCP framing problem". Soluții: delimitatori, length prefix, format fix.
</details>

---

## Întrebarea 5

TCP tunnel cu un singur thread:

```python
while True:
    data = client.recv(1024)
    server.sendall(data)
    response = server.recv(1024)
    client.sendall(response)
```

**Ce e greșit?**

A) Nimic, funcționează corect  
B) Se blochează dacă server-ul răspunde înainte ca clientul să trimită  
C) sendall() nu există  
D) Trebuie să fie async, nu threading

<details>
<summary>După discuție</summary>

**B** — se blochează.

De ce:
- `client.recv()` blochează thread-ul
- Dacă server-ul trimite ceva între timp, datele se pierd sau se acumulează
- Nu poți "asculta" în două locuri simultan cu un thread

De ce studenții aleg greșit:
- **A**: "TCP e full-duplex deci ar trebui să meargă". Full-duplex se referă la mediu, nu la cod.
- **C**: sendall() există și garantează trimiterea completă.
- **D**: Async e O soluție, dar threading e la fel de valid.
</details>

---

## Întrebarea 6

Setezi IP_MULTICAST_TTL = 0 pe sender.

**Ce se întâmplă?**

A) Mesajele ajung normal  
B) Mesajele nu părăsesc host-ul sender  
C) Mesajele ajung în rețeaua locală dar nu mai departe  
D) Eroare la sendto()

<details>
<summary>După discuție</summary>

**B** — mesajele rămân locale.

TTL (Time To Live) = câte hop-uri poate face pachetul:
- TTL=0: nu pleacă de pe mașină (doar loopback)
- TTL=1: rețea locală
- TTL>1: poate traversa routere

De ce studenții aleg greșit:
- **A**: "0 = fără limită"? Nu. 0 = zero hop-uri.
- **C**: Asta e pentru TTL=1.
- **D**: sendto() reușește, dar pachetul nu pleacă.
</details>

---

## Întrebarea 7

Clientul se conectează la tunnel pe h2:9090. Tunnel-ul forward-ează la server pe h3:8080.

**Ce IP sursă vede serverul?**

A) IP-ul clientului original (h1)  
B) IP-ul tunnel-ului (h2)  
C) localhost (127.0.0.1)  
D) Depinde de NAT

<details>
<summary>După discuție</summary>

**B** — IP-ul tunnel-ului.

Tunnel-ul face O NOUĂ conexiune către server. Din perspectiva serverului, "clientul" este tunnel-ul.

Implicații:
- Logging pe server arată IP greșit
- Rate limiting per-IP nu funcționează corect
- Trebuie header-e speciale (X-Forwarded-For) pentru IP-ul real

De ce studenții aleg greșit:
- **A**: Ar fi frumos, dar TCP nu "transferă" sursa.
- **C**: Doar dacă tunnel și server ar fi pe aceeași mașină.
- **D**: NAT e altceva — asta e despre cum funcționează proxy-ul.
</details>

---

## Pentru discuție extinsă

Dacă ai timp, pune și întrebări deschise:

1. "Când ai folosi broadcast în loc de multicast într-o aplicație reală?"

2. "De ce crezi că OS-ul blochează broadcast implicit?"

3. "Cum ai implementa reliable multicast?" (hint: ACK-uri, dar cum?)

Acestea nu au răspuns "corect" — scopul e să genereze discuție.

---

## Scor de utilizat

După sesiune, notează:
- Câți au răspuns corect la primul vot
- Câți s-au corectat după discuție
- Care întrebare a generat cea mai bună discuție

Întrebările cu 30-70% corect inițial și >80% după discuție sunt cele mai eficiente.

---

Întrebări bazate pe greșeli observate în 3 ani de laboratoare.
