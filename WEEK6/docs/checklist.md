# Checklist Cadru Didactic – Săptămâna 6

## NAT/PAT, ARP, DHCP, NDP, ICMP + SDN

---

## ☐ ÎNAINTE DE CURS/SEMINAR

### Pregătire tehnică (cu 1 zi înainte)
- [ ] VM-ul de demonstrație pornește corect
- [ ] Mininet funcționează: `sudo mn --test pingall`
- [ ] Open vSwitch pornit: `sudo systemctl status openvswitch-switch`
- [ ] OS-Ken instalat: `osken-manager --version`
- [ ] Starterkit-ul dezarhivat în folder accesibil
- [ ] `make check` returnează toate ✓

### Pregătire materiale
- [ ] Slide-urile/HTML-urile deschise și testate
- [ ] Fișierul `theory.html` navighează corect (săgeți)
- [ ] Diagramele PlantUML renderizate (PNG-uri prezente în `curs/assets/images/`)
- [ ] Codul Python verificat (fără erori de sintaxă)

### Logistică
- [ ] Proiector/ecran funcțional
- [ ] Conexiune la Internet (pentru demonstrații live)
- [ ] Studenții au acces la VM sau instrucțiuni de instalare
- [ ] Link-uri de download pentru starterkit trimise

---

## ☐ ÎN TIMPUL CURSULUI (100 min)

### Deschidere (5 min)
- [ ] Prezentare obiective
- [ ] Conexiune cu săptămâna anterioară (adresare IP, subnetting)
- [ ] Întrebare de activare: "Câți dintre voi folosesc routere acasă?"

### Secțiunea 1: Context IPv4 (15 min)
- [ ] Explicație criză adrese
- [ ] RFC 1918 - adrese private
- [ ] Mini-întrebare: "De ce nu putem folosi 192.168.1.1 pe Internet?"

### Secțiunea 2: NAT/PAT (30 min)
- [ ] NAT static vs dinamic vs PAT
- [ ] Demo tabelă NAT (slide interactiv)
- [ ] Flux pachet OUTBOUND/INBOUND
- [ ] Dezavantaje - discuție end-to-end
- [ ] Mini-quiz (2 întrebări)

### Secțiunea 3: ARP (15 min)
- [ ] Request/Reply
- [ ] Proxy ARP (concept)
- [ ] Legătura cu nivelul 2

### Secțiunea 4: DHCP (15 min)
- [ ] DORA pas cu pas
- [ ] DHCP Relay
- [ ] BOOTP vs DHCP (istoric)

### Secțiunea 5: NDP + ICMP (15 min)
- [ ] NDP vs ARP
- [ ] SLAAC
- [ ] Tipuri ICMP
- [ ] Ping și Traceroute

### Închidere (5 min)
- [ ] Recapitulare "Ce am învățat"
- [ ] Preview săptămâna viitoare (Protocoale de rutare)
- [ ] Întrebări finale

---

## ☐ ÎN TIMPUL SEMINARULUI (100 min)

### Verificare mediu (15 min)
- [ ] Toți studenții au `make check` cu succes
- [ ] Probleme comune rezolvate la tablă/proiector
- [ ] Curățare artefacte: `make clean`

### NAT/PAT Demo (40 min)
- [ ] Pornire topologie: `make nat-demo`
- [ ] Test ping h1→h3
- [ ] Inspectare iptables
- [ ] NAT Observer - demonstrație traducere
- [ ] Captură tcpdump
- [ ] Întrebări verificare: "Ce IP vede h3?"

### SDN Demo (35 min)
- [ ] Pornire controller (Terminal 1)
- [ ] Pornire topologie (Terminal 2)
- [ ] Test politici (h1↔h2 vs h1→h3)
- [ ] Inspectare flow table
- [ ] Modificare politică (ALLOW_UDP_TO_H3)
- [ ] Re-test și observații

### Exerciții și livrabile (10 min)
- [ ] Explicare structură livrabile
- [ ] Criteriile de evaluare
- [ ] Termen predare

---

## ☐ DUPĂ CURS/SEMINAR

### Imediat
- [ ] Salvare capturi demo (pentru referință)
- [ ] Notare probleme tehnice întâlnite
- [ ] Feedback rapid de la studenți (mâini ridicate / poll)

### În 24-48 ore
- [ ] Upload materiale pe platforma e-learning
- [ ] Trimitere link starterkit (dacă nu s-a făcut)
- [ ] Răspuns la întrebări pe forum/email

### Până la următoarea sesiune
- [ ] Evaluare livrabile primite
- [ ] Pregătire feedback individual
- [ ] Notare probleme frecvente pentru îmbunătățire

---

## ÎNTREBĂRI DE CONTROL (pentru dialog)

### NAT/PAT
1. Ce tip de NAT folosește majoritatea routerelor casnice?
2. De ce PAT folosește porturi pentru diferențiere?
3. Ce protocol/aplicație nu funcționează bine cu NAT și de ce?

### ARP
1. Ce tip de mesaj este ARP Request - unicast sau broadcast?
2. Ce se întâmplă dacă ARP Reply nu vine?
3. De ce Proxy ARP poate fi și un risc de securitate?

### DHCP
1. De ce DHCP Request e trimis broadcast, nu unicast?
2. Ce rol are DHCP Relay?
3. Ce se întâmplă când lease-ul expiră?

### SDN
1. Ce înseamnă separarea control plane / data plane?
2. Ce face regula table-miss?
3. De ce primul pachet e mai lent în SDN reactiv?

---

## CAPCANE FRECVENTE

| Situație | Cauză | Rezolvare |
|----------|-------|-----------|
| Topologia nu pornește | Artefacte anterioare | `sudo mn -c` |
| Controller nu se conectează | Port ocupat | `sudo pkill osken-manager` |
| NAT nu funcționează | IP forwarding off | `sysctl -w net.ipv4.ip_forward=1` |
| Ping-uri foarte lente | Flow-uri nu se instalează | Verifică logurile controller |
| tcpdump fără output | Interfață greșită | Verifică cu `ip link` |

---

## RUBRICĂ EVALUARE SĂPTĂMÂNALĂ

| Criteriu | Punctaj | Descriere |
|----------|---------|-----------|
| Comenzi corecte | 20% | Output-uri NAT și SDN prezente |
| Interpretare NAT | 20% | Înțelegere traducere, mapare |
| Interpretare SDN | 30% | Analiză flow table, control/data |
| Reflecție | 20% | Răspunsuri argumentate |
| Organizare | 10% | Structură clară, formatare |

---

*Revolvix&Hypotheticalandrei*
