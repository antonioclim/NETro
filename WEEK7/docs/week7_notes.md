# Note Săptămâna 7 — de ce contează capturile și filtrarea pentru ingineria software

## 1) Captura de pachete este „dovada"

Când un sistem distribuit se comportă anormal, logurile pot fi înșelătoare sau incomplete. Capturile (pcap) îți spun ce a traversat efectiv rețeaua. Acest lucru este util pentru:

- depanarea timeouts (există un SYN dar nu apare SYN-ACK?)
- verificarea a ceea ce trimite clientul în realitate (headere, framing, retry-uri)
- separarea problemelor de aplicație de problemele de rețea (retransmisii, RST, erori ICMP)

**În practică:** Când cineva spune "nu merge", prima întrebare e "ai captură?". Fără pcap, diagnosticul e ghicire.

## 2) Filtrarea face politica explicită

Filtrarea nu este doar un subiect de securitate. Este și un instrument operațional:

- limitarea „blast radius" când un serviciu se comportă greșit
- protejarea dependențelor fragile prin blocarea unor căi riscante
- separarea mediilor (dev, test și prod)

O cerință de inginerie este reproducibilitatea: o regulă trebuie să fie:

- lizibilă (ce face și de ce)
- testabilă (cum știm că funcționează)
- reversibilă (cum o anulăm în siguranță)

## 3) Capcane frecvente

- interpretarea unui drop ca bug de aplicație (poate fi o regulă de filtrare)
- uitarea rolului ICMP în diagnostic (blocarea totală a ICMP face diagnoza mult mai dificilă)
- amestecarea regulilor de host cu regulile de router (aplică regulile acolo unde trece efectiv traficul)

## 4) Concepte cheie — explicații intuitive

### TCP vs UDP: Scrisoarea recomandată vs Strigătul

**TCP** funcționează ca o scrisoare recomandată:
- Trimiți mesajul
- Aștepți confirmare că a ajuns
- Dacă nu vine confirmare, retrimiți
- Știi SIGUR când mesajul a ajuns (sau când a eșuat definitiv)

**UDP** funcționează ca un strigăt într-o sală aglomerată:
- Strigi mesajul
- Speri că te-a auzit cineva
- Nu primești confirmare
- Nu știi niciodată sigur dacă a ajuns

De aceea, când blochezi TCP, clientul primește un semnal clar (RST sau timeout cu retransmisii). Când blochezi UDP, clientul adesea nu știe dacă pachetul a fost blocat sau destinatarul pur și simplu n-a răspuns.

### DROP vs REJECT: Paznicul tăcut vs Paznicul vocal

Imaginează-ți că încerci să intri într-o clădire:

**DROP** = Paznicul te ignoră complet
- Stai la ușă și aștepți
- Nu se întâmplă nimic
- După mult timp, pleci frustrat
- Nu știi de ce n-ai putut intra

**REJECT** = Paznicul îți spune clar "Nu ai voie"
- Primești răspuns imediat
- Știi exact că accesul e interzis
- Poți decide rapid ce faci mai departe

În rețea:
- DROP: clientul așteaptă 30-60 secunde, retrimite pachete, apoi renunță
- REJECT: clientul primește RST sau ICMP instant, eșuează rapid

Când folosești ce:
- DROP e preferat pentru securitate (nu dezvălui că există firewall)
- REJECT e preferat pentru debugging și UX (aplicațiile eșuează rapid)

### INPUT vs FORWARD: Unde pui regula?

Diagrama mentală:

```
              FORWARD (trafic care TRECE prin)
    h1 ─────────────[router/fw]─────────────> h2
                        │
                 INPUT  │  OUTPUT
                (către) │  (de la)
                        │
                    router
```

- **INPUT:** pentru trafic destinat routerului/firewall-ului însuși (SSH către firewall, management)
- **OUTPUT:** pentru trafic generat de router (firewall-ul face el însuși request-uri)
- **FORWARD:** pentru trafic care doar trece prin (h1 vorbește cu h2)

Greșeala #1: pui regulă pe INPUT când vrei să blochezi trafic între h1 și h2. Acel trafic nu trece niciodată prin INPUT — merge direct pe FORWARD.

## 5) Metodologie de debugging

Când "nu merge", urmează pașii în ordine (nu sări):

1. **Layer 1-2:** Interfețele sunt UP? Au adrese? (`ip -br a`)
2. **Layer 3:** Ping merge? Ruta există? (`ping`, `ip route`)
3. **Layer 4:** Portul ascultă? (`ss -tlnp`)
4. **Firewall:** Ce reguli sunt active? (`iptables -L -n -v`)
5. **Captură:** Pachetele pleacă? Ajung? Se întoarce răspuns?

Detalii în `docs/troubleshooting.md`.

## 6) Legătura cu restul cursului

Această săptămână continuă programarea cu socket-uri și observarea traficului și te pregătește pentru subiecte la nivel de servicii, precum reverse proxy, networking în containere și diagnosticarea incidentelor reale din producție.

Conceptele de aici le vei folosi ori de câte ori:
- Debugging-ul unei aplicații distribuite pare să nu comunice
- Configurezi un serviciu să fie accesibil (sau inaccesibil) din anumite locuri
- Trebuie să demonstrezi că o problemă e de rețea, nu de aplicație
