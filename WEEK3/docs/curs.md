# Curs 3: Programare de rețea — Socket-uri, Broadcast, Multicast

Rețele de Calculatoare, ASE-CSIE, Anul 3

---

## La ce ne uităm azi

Socket-uri. Broadcast. Multicast. TCP tunnel.

Pare mult, dar toate se leagă. Până la finalul săptămânii, vei putea trimite mesaje la toate calculatoarele din rețea (broadcast), doar la un grup specific (multicast), sau să faci un intermediar care retransmite trafic (tunnel).

De ce contează? Pentru că orice aplicație distribuită — de la un chat până la Netflix — folosește socket-uri undeva în spate. Chiar dacă n-o să scrii socket-uri raw în producție (vei folosi framework-uri), trebuie să înțelegi ce se întâmplă dedesubt când ceva nu merge.

---

## Socket-uri: ideea de bază

Un socket e un capăt de comunicare. Gândește-te la el ca la un telefon.

| Tu ai | Socket-ul are |
|-------|---------------|
| Număr de telefon | Adresă IP |
| Extensie internă | Port |
| Limba în care vorbești | Protocol (TCP/UDP) |

Nu vezi firele și centralele telefonice — asta-i treaba rețelei. Tu doar ridici telefonul, formezi un număr, vorbești.

```
[Procesul tău] ←→ [Socket] ←——rețea——→ [Socket] ←→ [Alt proces]
```

### Funcțiile de bază

Vin din BSD Unix, 1983. S-au păstrat aproape neschimbate de atunci.

| Funcție | Ce face | Analogie |
|---------|---------|----------|
| socket() | Creează socket-ul | Cumperi telefonul |
| bind() | Îi dai o adresă | Îți alegi numărul |
| listen() | Aștepți apeluri (TCP) | Pui telefonul pe masă |
| accept() | Răspunzi (TCP) | Ridici receptorul |
| connect() | Suni pe cineva | Formezi numărul |
| send/recv | Vorbești/asculți | ... |
| close() | Închizi | Pui receptorul în furcă |

Pentru UDP mai ai sendto() și recvfrom() — trimiți/primești fără să stabilești conexiune.

---

## TCP vs UDP

Aici studenții se încurcă des. Hai să lămurim.

**TCP** = scrisoare recomandată cu confirmare de primire
- Știi că a ajuns
- Ajunge în ordine
- Dacă se pierde, se retrimite
- Mai lent (aștepți confirmarea)

**UDP** = carte poștală
- Arunci în cutie și pleci
- Poate ajunge, poate nu
- Poate ajunge în altă ordine
- Rapid (nu aștepți nimic)

Când folosești care? TCP pentru când contează să ajungă tot (web, email, fișiere). UDP pentru când viteza contează mai mult decât să ajungă fiecare pachet (video live, jocuri, DNS).

---

## UDP Broadcast

Acum devine interesant.

Broadcast = trimiți la TOȚI din rețeaua locală. Nu selectezi destinatari, primesc toți.

### Analogia cu megafonul

Imaginează-ți că ești într-o sală de conferințe. Ai un megafon. Strigi.

- Toți aud (vrei, nu vrei)
- Nu poți alege cine aude
- Vocea nu iese din sală (routerele blochează broadcast)
- E ineficient dacă vrei să vorbești cu o singură persoană

Asta-i broadcast. Adresa: 255.255.255.255 (sau .255 din subnet-ul tău).

### De ce ai nevoie de SO_BROADCAST?

Am văzut în laborator — studenți blocați 20 de minute pentru că nu înțelegeau de ce primesc PermissionError.

Sistemul de operare te protejează să nu faci broadcast din greșeală. Trebuie să "semnezi un formular" care zice: da, chiar vreau să deranjez pe toată lumea din rețea.

```python
# Fără asta → PermissionError
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
```

E ca și cum trebuie să ceri voie să folosești megafonul. Altfel, cineva ar putea să-l folosească accidental și să inunde rețeaua.

---

## UDP Multicast

Multicast rezolvă o problemă: ce faci când vrei să trimiți la un GRUP, nu la toți?

### Analogia cu grupul de WhatsApp

- Creezi un grup (adresă multicast, ex: 224.1.1.1)
- Cine vrea să primească mesaje face JOIN (IP_ADD_MEMBERSHIP)
- Cine nu-i în grup, nu primește nimic
- Poți ieși oricând (LEAVE)

Mult mai eficient decât să trimiți individual la fiecare. Și spre deosebire de broadcast, poate trece de routere (dacă TTL-ul e destul de mare).

### Adresele multicast

Sunt speciale: 224.0.0.0 – 239.255.255.255 (Class D).

Pentru teste locale folosim 224.1.1.1. Nu îți face griji de range-uri acum, important e să înțelegi mecanismul.

### Ordinea contează!

Asta-i capcana principală. Anul trecut, aproape jumătate din studenți au pierdut timp aici.

```python
# GREȘIT — poate să nu primești mesaje
sock.setsockopt(IPPROTO_IP, IP_ADD_MEMBERSHIP, mreq)  # JOIN
sock.bind(('', port))  # bind după

# CORECT
sock.bind(('', port))  # bind ÎNTÂI
sock.setsockopt(IPPROTO_IP, IP_ADD_MEMBERSHIP, mreq)  # apoi JOIN
```

De ce? Când faci JOIN, kernel-ul trebuie să știe unde să livreze pachetele. Dacă n-ai făcut bind, nu știe.

---

## Broadcast vs Multicast — când folosești care

| Situație | Alegere | De ce |
|----------|---------|-------|
| Alertă de incendiu — toți trebuie să știe | Broadcast | Simplu, sigur că ajunge la toți |
| Notificări pentru echipa de dev (15 oameni) | Multicast | Eficient, nu deranjezi pe alții |
| Service discovery la pornire | Broadcast | Nu știi cine există încă |
| Streaming video intern | Multicast | Scalează mai bine |

Nu există răspuns universal. Depinde de context.

---

## TCP Tunnel

Ultimul concept pentru azi.

Un tunnel e un intermediar. Primește conexiuni pe un port și le retransmite la altă destinație.

### Analogia cu recepționerul

Suni la firma X. Răspunde recepționerul.
- Îi spui cu cine vrei să vorbești
- Te pune în legătură
- Tu nu știi numărul direct al persoanei

```
[Tu] → [Recepționer :9090] → [Persoana :8080]
```

### De ce 2 thread-uri?

Aici se blochează mulți. "TCP e full-duplex, de ce nu merge cu un thread?"

Problema: recv() e blocant. Când aștepți date de la client, nu poți în același timp să aștepți date de la server.

```python
# Cu un thread — SE BLOCHEAZĂ
data = client.recv()  # Stai aici până clientul trimite
# Dacă serverul trimite între timp, nu primești!
response = server.recv()
```

Soluția: două thread-uri paralele.
- Thread 1: citește de la client, trimite la server
- Thread 2: citește de la server, trimite la client

Ambele rulează simultan. Problema rezolvată.

---

## TCP Framing Problem

Încă o capcană pe care trebuie s-o știi.

TCP garantează că datele ajung în ordine. NU garantează că ajung în aceleași "bucăți" în care le-ai trimis.

```python
# Sender
sock.send(b"AAA")
sock.send(b"BBB")

# Receiver poate primi:
recv() → b"AAABBB"  # concatenate
# sau
recv() → b"AA"      # fragmentat
recv() → b"ABBB"
```

De ce? TCP e un flux de octeți, nu de mesaje. Ca apa într-un tub — nu știi unde era separarea.

Soluții:
1. Delimitator (mesaje terminate cu \n)
2. Lungime la început (primii 4 bytes = lungimea mesajului)
3. Lungime fixă (toate mesajele de 100 bytes)

---

## Recapitulare vizuală

```
              SOCKET
                 │
         ┌───────┴───────┐
        TCP             UDP
    (scrisoare)    (carte poștală)
         │               │
    conexiune      ┌─────┼─────┐
    garantată   unicast bcast mcast
                 1:1   1:ALL  1:GRUP
```

---

## Verificare rapidă

Înainte de seminar, asigură-te că poți răspunde:

1. Ce opțiune socket trebuie pentru broadcast sender?
2. Care-i ordinea corectă: bind sau JOIN primul?
3. De ce tunnel-ul are nevoie de 2 thread-uri?
4. TCP păstrează granițele mesajelor?

Dacă nu știi vreuna, recitește secțiunea relevantă.

---

## Bibliografie

Stevens, Fenner, Rudoff — UNIX Network Programming (biblia socket-urilor)
Kurose & Ross — Computer Networking (pentru context teoretic)
docs.python.org/3/library/socket.html (referință Python)

---

Material pentru cursul Rețele de Calculatoare, ASE-CSIE.
Actualizat pe baza feedback-ului din semestrele anterioare.
