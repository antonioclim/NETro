# Scenariu laborator — Săptămâna 7 (Mininet)

Acest scenariu folosește o topologie în care traficul dintre două host-uri trebuie să treacă printr-un host `fw` configurat ca router. Pe `fw` aplici reguli `iptables` pentru a permite sau bloca trafic.

## Topologie

```
   h1 (10.0.7.11)                              h2 (10.0.7.200)
        │                                           │
        │                                           │
   ┌────┴────┐                               ┌─────┴────┐
   │   s1    │                               │    s2    │
   └────┬────┘                               └────┬─────┘
        │         fw (router/firewall)            │
        │         ┌─────────────────┐             │
        └─────────┤ fw-eth0  fw-eth1├─────────────┘
                  │ 10.0.7.1  10.0.7.129
                  └─────────────────┘
```

- h1: 10.0.7.11/25, gateway 10.0.7.1
- h2: 10.0.7.200/25, gateway 10.0.7.129
- fw: router cu două interfețe, face forwarding

## Reguli de lucru

- Lucrezi doar în laboratorul local creat de kit
- Păstrează dovezi: comenzi rulate, loguri, capturi pcap
- Notează predicțiile înainte de a rula comenzi
- Compară rezultatele cu predicțiile și explică diferențele

---

## Nivel 1 (bază): conectivitate și captură

**Timp estimat:** 15 min

### Pas 1: Rulează demo-ul

```bash
./scripts/run_all.sh
```

### Pas 2: Verifică artefactele

```bash
ls -lh artifacts/
cat artifacts/validation.txt
```

### Pas 3: Analizează captura

> **🎯 Predicție:** Câte pachete TCP cu destinația 9090 vei vedea?

```bash
tshark -r artifacts/demo.pcap -Y 'tcp.dstport==9090' | wc -l
```

> **🎯 Predicție:** Dar pachete UDP către 9091?

```bash
tshark -r artifacts/demo.pcap -Y 'udp.dstport==9091' | wc -l
```

### Întrebări de răspuns

1. Care sunt adresele IP sursă și destinație pentru traficul TCP?
2. Poți identifica three-way handshake-ul? Ce flag-uri vezi?
3. Dacă vezi și trafic UDP, câte pachete sunt în fiecare direcție?

---

## Nivel 2 (mediu): profile de firewall

**Timp estimat:** 25 min

### Experimentul 1: Baseline

```bash
sudo python3 python/apps/firewallctl.py --profile baseline
./scripts/run_all.sh
```

Notează conținutul lui `validation.txt`.

### Experimentul 2: Block TCP

> **🎯 Predicție:** După ce aplicăm block_tcp_9090:
> - Traficul TCP va mai ajunge la h2?
> - Ce vei vedea în pcap în loc de handshake normal?
> - UDP va fi afectat?

```bash
sudo python3 python/apps/firewallctl.py --profile block_tcp_9090
./scripts/run_all.sh
```

Verifică:
- Ce scrie în `validation.txt`?
- Caută RST în captură: `tshark -r artifacts/demo.pcap -Y 'tcp.flags.reset==1'`

### Experimentul 3: Block UDP

```bash
sudo python3 python/apps/firewallctl.py --profile baseline
sudo python3 python/apps/firewallctl.py --profile block_udp_9091
./scripts/run_all.sh
```

> **🎯 Predicție:** Cum se va manifesta blocarea UDP comparativ cu TCP?

Verifică:
- Cât a durat până clientul UDP a "terminat"?
- Ce diferență observi în comportament față de TCP blocat?

### Întrebări de răspuns

1. Care e diferența vizibilă în pcap între TCP blocat cu REJECT și UDP blocat cu DROP?
2. De ce clientul UDP nu primește eroare explicită?
3. Pe ce chain sunt aplicate regulile? De ce FORWARD și nu INPUT?

---

## Nivel 3 (provocare): profil personalizat

**Timp estimat:** 35 min

### Cerință

Creează un profil nou care îndeplinește TOATE condițiile:

1. ICMP funcționează (ping între h1 și h2)
2. TCP către portul 9090 funcționează DOAR din h1 către h2 (nu invers)
3. Tot restul traficului FORWARD este blocat

### Pași sugerați

1) Studiază structura profilelor în `configs/firewall_profiles.json`

2) Creează profilul. Vei avea nevoie de:
   - Politică implicită DROP pe FORWARD
   - Regulă ACCEPT pentru ICMP
   - Regulă ACCEPT pentru TCP 9090 cu restricție de sursă/destinație

3) Limitare: `firewallctl.py` actual nu suportă `-s` și `-d`. Opțiuni:
   - Extinde scriptul să suporte source/destination
   - Aplică regulile manual cu `iptables` după ce aplici profilul
   - Documentează ce comenzi ar fi necesare

4) Testează fiecare condiție:

```bash
# Test ICMP
ping -c 2 10.0.7.200

# Test TCP din h1 (ar trebui să meargă)
# [din Mininet CLI sau din script]

# Test TCP din h2 către h1 (ar trebui să nu meargă)
# [inițiază conexiune în direcția opusă]
```

5) Demonstrează cu captură:
   - Arată pachetele ICMP care trec
   - Arată conexiunea TCP reușită h1→h2
   - Arată ce se întâmplă când h2 încearcă să inițieze către h1

### Livrabil

- Fișierul JSON actualizat (sau lista de comenzi iptables)
- Log cu testele rulate
- Explicație: de ce ai ales aceste reguli și în această ordine

### Hint pentru debugging

Dacă nu funcționează cum te aștepți:

```bash
# Verifică regulile active
sudo iptables -L FORWARD -n -v --line-numbers

# Verifică pe ce interfață vine traficul
tcpdump -i fw-eth0 -nn

# Verifică dacă pachetele ajung deloc la fw
tcpdump -i any -nn 'host 10.0.7.11'
```

---

## Ce se evaluează

- **Reproducibilitatea:** poți rula setup → demo → test → cleanup fără erori
- **Claritatea explicațiilor:** înțelegi CE faci și DE CE
- **Corelarea:** poți demonstra cu pcap și loguri efectul regulilor
- **Predicții:** ai notat ce te așteptai și ai explicat diferențele

## Întrebări bonus (opțional)

1. Ce s-ar întâmpla dacă ai pune regulile pe INPUT în loc de FORWARD?
2. Cum ai configura logging pentru pachetele blocate? (hint: `-j LOG`)
3. Dacă ai avea mai multe clase de trafic de permis/blocat, cum ai organiza regulile pentru eficiență?
