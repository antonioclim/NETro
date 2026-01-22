# Scenarii Practice Mininet — Săptămâna 5

## Scenariul 1: Verificare Conectivitate Bază

### Obiectiv
Verificarea funcționării rutării între două subrețele.

### Pași

1. Pornire topologie bază:
```bash
sudo python3 mininet/topologies/topo_5_base.py --cli
```

2. Verificare adrese IP:
```bash
mininet> h1 ip addr show dev h1-eth0
mininet> h2 ip addr show dev h2-eth0
mininet> r1 ip addr
```

3. Verificare tabele rutare:
```bash
mininet> h1 ip route
mininet> h2 ip route
mininet> r1 ip route
```

4. Test ping:
```bash
mininet> h1 ping -c 5 10.0.5.140
```

### Rezultat Așteptat
- 0% packet loss între h1 și h2
- TTL = 63 (a trecut prin router)

---

## Scenariul 2: Captură și Analiză Trafic ICMP

### Obiectiv
Captura și analiza pachetelor ICMP între subrețele.

### Pași

1. Pornire captură pe router:
```bash
mininet> r1 tcpdump -ni r1-eth0 icmp -w /tmp/icmp_capture.pcap &
```

2. Generare trafic:
```bash
mininet> h1 ping -c 10 10.0.5.140
```

3. Oprire captură:
```bash
mininet> r1 kill %tcpdump
```

4. Analiză captură (în alt terminal):
```bash
sudo tshark -r /tmp/icmp_capture.pcap -T fields -e ip.src -e ip.dst -e ip.ttl -e icmp.type
```

### Rezultat Așteptat
- Echo Request: src=10.0.5.11, dst=10.0.5.140, TTL=64
- Echo Reply: src=10.0.5.140, dst=10.0.5.11, TTL=63

---

## Scenariul 3: Simulare Eroare Rutare

### Obiectiv
Înțelegerea importanței gateway-ului corect.

### Pași

1. Pornire topologie și ștergere rută implicită h1:
```bash
mininet> h1 ip route del default
```

2. Încercare ping:
```bash
mininet> h1 ping -c 3 10.0.5.140
```

3. Observare eroare:
```
Network is unreachable
```

4. Restaurare rută:
```bash
mininet> h1 ip route add default via 10.0.5.1
```

5. Verificare funcționalitate:
```bash
mininet> h1 ping -c 3 10.0.5.140
```

---

## Scenariul 4: Topologie VLSM

### Obiectiv
Verificarea funcționării VLSM cu prefixe diferite.

### Pași

1. Pornire topologie extinsă:
```bash
sudo python3 mininet/topologies/topo_5_extended.py --cli
```

2. Verificare configurare subrețele:
```bash
mininet> h1 ip addr   # /26 - 62 hosturi
mininet> h2 ip addr   # /27 - 30 hosturi
mininet> h3 ip addr   # /30 - 2 hosturi (P2P)
```

3. Test conectivitate completă:
```bash
mininet> pingall
```

4. Verificare că h1 ajunge la h3:
```bash
mininet> h1 traceroute 10.0.5.98
```

### Rezultat Așteptat
- pingall: 0% packet loss
- traceroute: 1 hop (prin r1)

---

## Scenariul 5: IPv6 Dual-Stack

### Obiectiv
Verificarea funcționării IPv6 simultan cu IPv4.

### Pași

1. Pornire topologie cu IPv6:
```bash
sudo python3 mininet/topologies/topo_5_extended.py --cli --ipv6
```

2. Verificare adrese IPv6:
```bash
mininet> h1 ip -6 addr
mininet> h2 ip -6 addr
mininet> r1 ip -6 addr
```

3. Test ping IPv6:
```bash
mininet> h1 ping6 -c 5 2001:db8:5:20::10
```

4. Verificare rutare IPv6:
```bash
mininet> h1 ip -6 route
mininet> r1 ip -6 route
```

### Rezultat Așteptat
- Adrese IPv6 configurate pe toate nodurile
- Ping IPv6 funcțional între subrețele

---

## Scenariul 6: Analiză TTL și Hop Count

### Obiectiv
Înțelegerea decrementării TTL la traversarea routerului.

### Pași

1. Pornire topologie bază:
```bash
sudo python3 mininet/topologies/topo_5_base.py --cli
```

2. Captură pe r1-eth1 (spre h2):
```bash
mininet> r1 tcpdump -ni r1-eth1 icmp &
```

3. Ping cu TTL specific:
```bash
mininet> h1 ping -c 1 -t 64 10.0.5.140
mininet> h1 ping -c 1 -t 1 10.0.5.140
```

4. Observare diferențe:
- TTL=64 ajunge la destinație cu TTL=63
- TTL=1 generează "Time exceeded" de la router

---

## Scenariul 7: Calcul Manual vs Automat

### Obiectiv
Compararea calculelor manuale cu rezultatele scripturilor.

### Pași

1. Calcul manual pentru 10.0.5.100/26:
   - Mască: 255.255.255.192
   - Rețea: 10.0.5.64
   - Broadcast: 10.0.5.127
   - Hosturi: 62

2. Verificare cu script:
```bash
python3 python/exercises/ex_5_01_cidr_flsm.py analyze 10.0.5.100/26 --verbose
```

3. Verificare în Mininet:
```bash
mininet> h2 ip addr   # h2 e în 10.0.5.64/27, subset al /26
```

---

## Livrabile Student

Pentru fiecare scenariul, studentul trebuie să producă:

1. **Captură de ecran** a comenzilor executate
2. **Fișier PCAP** (unde e cazul)
3. **Răspunsuri** la întrebările:
   - Ce se întâmplă când TTL ajunge la 0?
   - De ce este necesar IP forwarding pe router?
   - Care e diferența între /25 și /26 în practică?
   - Cum verifici dacă o adresă e validă pentru host?

---

*Rezolvix&Hypotheticalandrei | ASE-CSIE | Licență MIT*
