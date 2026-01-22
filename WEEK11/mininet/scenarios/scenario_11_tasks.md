# Sarcini Mininet – Săptămâna 11

## Scenariu: Topologie Load Balancer

### Obiectiv
Construirea și testarea unei topologii de rețea cu load balancer și multiple backend-uri.

### Topologie
```
       [h1: client]
            |
          [s1: switch]
            |
    +-------+-------+-------+
    |       |       |       |
  [h2]    [h3]    [h4]    [h5: LB]
 (backend)(backend)(backend)
```

### Sarcini

#### Sarcina 1: Pornirea topologiei
```bash
sudo python3 mininet/topologies/topo_11_base.py --cli
```

#### Sarcina 2: Testare conectivitate
```bash
mininet> pingall
```

**Rezultat așteptat:** Toate nodurile comunică între ele (0% pierderi).

#### Sarcina 3: Pornire servere HTTP pe backends
```bash
mininet> h2 python3 -m http.server 8000 &
mininet> h3 python3 -m http.server 8000 &
mininet> h4 python3 -m http.server 8000 &
```

#### Sarcina 4: Testare acces direct la backends
```bash
mininet> h1 curl http://10.0.0.2:8000/
mininet> h1 curl http://10.0.0.3:8000/
mininet> h1 curl http://10.0.0.4:8000/
```

#### Sarcina 5: Captură trafic pe switch
```bash
mininet> s1 tcpdump -i s1-eth1 -c 10 &
mininet> h1 curl http://10.0.0.2:8000/
```

#### Sarcina 6: Analiza latențelor
```bash
mininet> h1 ping -c 5 10.0.0.2
mininet> h1 ping -c 5 10.0.0.3
mininet> h1 ping -c 5 10.0.0.4
```

### Întrebări de verificare

1. Ce observați la RTT-ul între h1 și backends?
2. Cum influențează numărul de hop-uri latența?
3. Ce se întâmplă dacă opriți un backend?

### Extensii (opțional)

1. Adăugați rate limiting pe s1
2. Implementați QoS cu tc
3. Adăugați un al doilea switch pentru redundanță

---
*Revolvix&Hypotheticalandrei*
