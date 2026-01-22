# Depanare — Săptămâna 7

Mai jos sunt cele mai frecvente probleme întâlnite într-o VM Linux minimală, plus soluții rapide.

---

## Strategii de debugging pentru rețelistică

Când ceva nu merge, urmează pașii în ordine. Nu sări etape — multe probleme "de aplicație" sunt de fapt probleme de rețea.

### Pas 1: Verifică stack-ul local (Layer 1-2)

```bash
ip link show           # Interfețele sunt UP?
ip -br a               # Au adrese IP configurate?
ping -c 1 127.0.0.1    # Stack-ul TCP/IP local funcționează?
```

Dacă `ping 127.0.0.1` nu merge, problema e în configurarea de bază a sistemului.

### Pas 2: Verifică conectivitatea (Layer 3)

```bash
ping -c 2 10.0.7.200        # Ajunge pachetul la destinație?
traceroute -n 10.0.7.200    # Pe unde trece? Unde se oprește?
```

Dacă ping nu merge:
- Verifică rute: `ip route`
- Verifică ARP: `ip neigh`
- Verifică dacă destinația există și e UP

### Pas 3: Verifică portul/serviciul (Layer 4)

```bash
ss -tlnp | grep 9090        # Ascultă cineva pe portul ăsta LOCAL?
nc -zv 10.0.7.200 9090      # Pot să mă conectez REMOTE?
```

Dacă serverul ascultă dar clientul nu se poate conecta, problema e între ei (firewall, routing).

### Pas 4: Verifică firewall-ul

```bash
sudo iptables -L -n -v                    # Ce reguli sunt active?
sudo iptables -L FORWARD -n --line-numbers # Specific pe FORWARD
sudo iptables -S                          # Format ușor de citit
```

Întrebări de pus:
- Ce politică implicită are chain-ul? (ACCEPT sau DROP)
- Sunt reguli care ar putea bloca traficul meu?
- Ordinea regulilor contează — prima care se potrivește câștigă.

### Pas 5: Verifică în pcap (dovada)

```bash
# Pe sursă — pachetul PLEACĂ?
tcpdump -i any -nn 'tcp port 9090'

# Pe destinație — pachetul AJUNGE?
tcpdump -i any -nn 'tcp port 9090'

# Pe firewall — ce se întâmplă?
tcpdump -i any -nn 'tcp port 9090'
```

Analiza capturii:
- Vezi SYN de la client? Dacă nu, problema e la client sau pe drumul până la punctul de captură.
- Vezi SYN-ACK de la server? Dacă nu, serverul nu ascultă sau e blocat.
- Vezi RST? De unde vine? (firewall REJECT sau aplicație care refuză)
- Nu vezi nimic după SYN? Probabil DROP pe drum.

---

## Analogii pentru concepte cheie

### DROP vs REJECT — Paznicul

Imaginează-ți că încerci să intri într-o clădire cu paznic:

**DROP** = Paznicul te ignoră complet. Stai la ușă, aștepți, nu se întâmplă nimic. După un timp pleci frustrat, fără să știi de ce n-ai putut intra.

**REJECT** = Paznicul îți spune clar "Nu ai voie să intri". Știi imediat răspunsul și poți decide ce faci mai departe.

**În rețea:**
- DROP: clientul așteaptă timeout (30-60 secunde), retrimite SYN-uri, consumă resurse
- REJECT: clientul primește RST sau ICMP imediat, știe că e blocat, poate afișa eroare clară

**Când folosești ce:**
- DROP e mai "sigur" din perspectivă de securitate — nu dezvălui că există firewall
- REJECT e mai prietenos — aplicațiile eșuează rapid, nu blochează utilizatorul

### TCP vs UDP — Scrisoarea vs Strigătul

**TCP** = Scrisoare recomandată
- Trimiți scrisoarea
- Primești confirmare de primire
- Știi SIGUR că a ajuns
- Dacă se pierde, poștașul încearcă din nou
- Durează mai mult, dar e garantat

**UDP** = Strigăt într-o piață aglomerată
- Strigi mesajul
- Speri că te-a auzit cineva
- Nu primești confirmare
- Dacă nu te-a auzit, nu afli niciodată
- Rapid, dar fără garanții

**De aceea:**
- TCP blocat → clientul ȘTIE (primește RST sau face timeout cu retransmisii vizibile)
- UDP blocat → clientul NU ȘTIE cu siguranță (poate n-a ajuns, poate destinatarul n-a răspuns, poate a fost filtrat)

### INPUT vs FORWARD vs OUTPUT — Unde pui regula

```
                    FORWARD
        h1 ─────────[fw]─────────> h2
                     │
              INPUT  │  OUTPUT
                     │
                 spre/de la fw
```

- **INPUT:** trafic cu DESTINAȚIA fw (cineva vorbește CU firewall-ul)
- **OUTPUT:** trafic cu SURSA fw (firewall-ul vorbește cu altcineva)  
- **FORWARD:** trafic care TRECE PRIN fw (h1 vorbește cu h2, fw doar rutează)

**Greșeală frecventă:** pui regula pe INPUT când vrei să blochezi trafic între h1 și h2. INPUT nu vede acel trafic — trebuie FORWARD.

---

## Probleme frecvente și soluții

### 1) `tshark: You don't have permission to capture on that device`

Opțiuni:
- Rulează capturile cu `sudo`
- Configurează capabilități pentru `dumpcap`:
  ```bash
  sudo dpkg-reconfigure wireshark-common
  sudo usermod -aG wireshark $USER
  ```
  Apoi delogare/relogare.

Dacă nu poți captura fără root, kitul rămâne funcțional: păstrează `demo.log` și `validation.txt`.

### 2) `mininet` nu este instalat

Poți:
- Instala Mininet: `sudo apt-get install -y mininet`
- Sau folosi demo-ul alternativ din `docker/`

### 3) `iptables` lipsește sau nu ai permisiuni

Instalează iptables:
```bash
sudo apt-get update
sudo apt-get install -y iptables
```

În Mininet, rulează comenzi care cer root din interiorul nodului `fw` (prin `mn`), nu pe host.

### 4) `mn: command not found`

```bash
sudo apt-get install -y mininet openvswitch-switch
```

### 5) Nu există trafic în pcap

Verifică:
- Ai rulat demo-ul cu `tshark`/`tcpdump` disponibil?
- Capturi pe interfața potrivită? (`any` e cea mai simplă în VM)
- Firewall-ul nu blochează chiar traficul pe care încerci să îl observi?
- Timing: ai pornit captura ÎNAINTE de a genera trafic?

Debug rapid:
```bash
# Terminal 1: pornește captură
sudo tcpdump -i any -nn -w /tmp/test.pcap

# Terminal 2: generează trafic
ping -c 3 10.0.7.200

# Terminal 1: Ctrl+C, verifică
tcpdump -r /tmp/test.pcap | head
```

### 6) Porturile sunt deja ocupate

Verifică ce rulează:
```bash
ss -tulpn | grep -E '9090|9091|8080|8081|8082'
```

Oprește procesele sau rulează cleanup:
```bash
./scripts/cleanup.sh
```

### 7) Docker nu pornește în VM

```bash
sudo systemctl status docker
sudo systemctl enable --now docker
```

Dacă nu poți folosi Docker, folosește Mininet.

### 8) Demo-ul se oprește cu eroare

- Citește `artifacts/demo.log` de la început
- Identifică prima comandă care a eșuat
- Rulează manual acea comandă pentru a vedea eroarea completă
- Verifică dependențele din `./scripts/setup.sh`

### 9) Clientul TCP dă timeout dar serverul ascultă

Cauze posibile (în ordinea probabilității):
1. Firewall blochează pe FORWARD (dacă trece prin router)
2. Adresă IP greșită (typo)
3. Serverul ascultă pe altă interfață (127.0.0.1 vs 0.0.0.0)
4. Routing incorect (pachetul nu știe cum să ajungă)

Debug:
```bash
# Pe server: ascultă pe toate interfețele?
ss -tlnp | grep 9090
# Trebuie să vezi 0.0.0.0:9090, nu 127.0.0.1:9090

# Pe client: ruta există?
ip route get 10.0.7.200
```

### 10) "Connection refused" vs timeout — ce înseamnă?

**Connection refused** (RST primit):
- Pachetul a AJUNS la destinație
- Dar nimeni nu ascultă pe portul respectiv
- SAU firewall-ul a făcut REJECT

**Timeout** (nimic primit):
- Pachetul probabil NU a ajuns
- SAU firewall-ul a făcut DROP
- SAU serverul e foarte lent (rar)

Diferența contează pentru diagnostic: refused = problema e la destinație, timeout = problema e pe drum sau la destinație cu DROP.
