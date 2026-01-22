# Scenarii Mininet pentru Laborator 9

## Prezentare generală

Acest document descrie scenariile practice pentru utilizarea Mininet în cadrul Laboratorului 9. Fiecare scenariu include obiective, pași de execuție, rezultate așteptate și întrebări de reflecție.

---

## Scenariu 1: Testare de bază client-server

### Obiectiv
Validarea funcționalității protocolului pseudo-FTP într-o rețea simulată cu latență zero.

### Topologie
```
h1 (server) ──── s1 ──── h2 (client)
10.0.0.1              10.0.0.2
```

### Pași

1. **Pornirea topologiei**
   ```bash
   cd mininet/topologies
   sudo python topo_base.py
   ```

2. **Verificarea conectivității**
   ```
   mininet> pingall
   ```
   
   Rezultat așteptat:
   ```
   *** Ping: testing ping reachability
   h1 -> h2 
   h2 -> h1 
   *** Results: 0% dropped (2/2 received)
   ```

3. **Pornirea serverului pe h1**
   ```
   mininet> h1 python3 /path/to/ex_9_02_pseudo_ftp.py --mode server --port 9021 &
   ```

4. **Conectarea clientului de pe h2**
   ```
   mininet> h2 python3 /path/to/ex_9_02_pseudo_ftp.py --mode client --host 10.0.0.1 --port 9021
   ```

5. **Executarea comenzilor**
   - AUTH admin:secret123
   - PWD
   - LIST
   - GET small.txt
   - QUIT

6. **Verificarea transferului**
   ```
   mininet> h2 cat /tmp/client-files/small.txt
   ```

### Rezultate așteptate
- Toate comenzile returnează [OK]
- Fișierul transferat este identic cu originalul
- RTT foarte mic (<1ms)

### Întrebări de reflecție
1. Ce observați la timpul de răspuns pentru comenzi?
2. Ce s-ar întâmpla dacă serverul nu ar fi pornit?

---

## Scenariu 2: Impact latență asupra transferurilor

### Obiectiv
Observarea efectului latenței de rețea asupra performanței transferurilor de fișiere.

### Topologie
Aceeași ca Scenariu 1, cu latență adăugată.

### Pași

1. **Pornirea topologiei cu latență**
   ```bash
   sudo python topo_base.py --delay 100ms
   ```

2. **Testarea latenței**
   ```
   mininet> h1 ping -c 5 h2
   ```
   
   Rezultat așteptat:
   ```
   --- 10.0.0.2 ping statistics ---
   5 packets transmitted, 5 received, 0% packet loss
   rtt min/avg/max/mdev = 200.1/200.3/200.5/0.2 ms
   ```
   
   (Notă: RTT = 2 × delay = 200ms)

3. **Pornire server și client (ca în Scenariu 1)**

4. **Măsurarea timpului de transfer**
   ```
   mininet> h2 time python3 /path/to/client.py --host 10.0.0.1 --get large.bin
   ```

5. **Comparație cu latență diferită**
   Repetați cu `--delay 10ms` și `--delay 500ms`.

### Rezultate așteptate

| Latență | RTT | Timp transfer 1MB |
|---------|-----|-------------------|
| 0ms | <1ms | ~1s |
| 10ms | 20ms | ~3s |
| 100ms | 200ms | ~20s |
| 500ms | 1000ms | ~100s |

### Întrebări de reflecție
1. De ce crește timpul de transfer neliniar cu latența?
2. Ce rol joacă fereastra TCP în această situație?
3. Cum ar ajuta compresia în acest scenariu?

---

## Scenariu 3: Client local vs client remote

### Obiectiv
Compararea performanței între clienți cu caracteristici de rețea diferite.

### Topologie
```
                    ┌─── s2 ──── h2 (local, 1ms, 100Mbps)
h1 (server) ─── s1 ───┤
                      └─── s3 ──── h3 (remote, 50ms, 50Mbps)
```

### Pași

1. **Pornirea topologiei extinse**
   ```bash
   cd mininet/topologies
   sudo python topo_extended.py
   ```

2. **Verificarea diferenței de latență**
   ```
   mininet> h2 ping -c 5 10.0.0.1
   mininet> h3 ping -c 5 10.0.0.1
   ```

3. **Pornirea serverului**
   ```
   mininet> h1 python3 /path/to/server.py --port 9021 &
   ```

4. **Transfer simultan**
   ```
   mininet> h2 time python3 /path/to/client.py --host 10.0.0.1 --get medium.bin &
   mininet> h3 time python3 /path/to/client.py --host 10.0.0.1 --get medium.bin &
   ```

5. **Observarea rezultatelor**

### Rezultate așteptate
- Clientul local (h2) termină transferul mult mai repede
- Serverul gestionează ambii clienți simultan
- Latența remote introduce delay vizibil

### Întrebări de reflecție
1. Care client termină primul și de ce?
2. Ce se întâmplă când ambii clienți transferă același fișier simultan?
3. Cum ar beneficia un CDN (Content Delivery Network) utilizatorul remote?

---

## Scenariu 4: Packet loss și retransmisii

### Obiectiv
Observarea comportamentului TCP la packet loss și impactul asupra protocolului aplicație.

### Topologie
Bază cu packet loss configurat.

### Pași

1. **Pornirea topologiei cu packet loss**
   ```bash
   sudo python topo_base.py --loss 5
   ```

2. **Observarea ping-ului**
   ```
   mininet> h1 ping -c 20 h2
   ```
   
   Așteptări: ~5% pierderi

3. **Capturarea traficului**
   ```
   mininet> h1 tcpdump -i h1-eth0 -w /tmp/loss_capture.pcap &
   ```

4. **Transfer cu server/client**

5. **Analiza capturii**
   ```
   mininet> h1 pkill tcpdump
   mininet> sh tshark -r /tmp/loss_capture.pcap -Y "tcp.analysis.retransmission"
   ```

### Rezultate așteptate
- Se observă retransmisii TCP
- Transferul durează mai mult
- CRC match la final (integritate păstrată)

### Întrebări de reflecție
1. Cum detectează TCP pierderea pachetelor?
2. De ce CRC-ul nostru de aplicație este încă valid deși au fost retransmisii?
3. Ce s-ar întâmpla dacă am folosi UDP în loc de TCP?

---

## Scenariu 5: Rate limiting și QoS

### Obiectiv
Experimentarea cu limitarea bandwidth-ului și observarea efectelor.

### Pași

1. **Pornire cu bandwidth limitat**
   ```bash
   sudo python topo_base.py --bw 1
   ```
   (1 Mbps)

2. **Test bandwidth cu iperf**
   ```
   mininet> h1 iperf -s &
   mininet> h2 iperf -c 10.0.0.1 -t 10
   ```

3. **Transfer fișier mare**
   ```
   mininet> h2 time python3 /path/to/client.py --host 10.0.0.1 --get large.bin
   ```

4. **Calcul throughput teoretic vs real**
   
   Teoretic: 1 Mbps = 125 KB/s → 1 MB în 8s
   
   Real: ___ s (completați)

### Întrebări de reflecție
1. De ce throughput-ul real este mai mic decât cel teoretic?
2. Ce overhead introduce protocolul nostru?
3. Cum ar ajuta compresia când bandwidth-ul este limitat?

---

## Scenariu 6: Modificare dinamică a condițiilor de rețea

### Obiectiv
Observarea comportamentului protocolului când condițiile de rețea se schimbă în timpul transferului.

### Pași

1. **Pornire topologie normală**
   ```bash
   sudo python topo_base.py
   ```

2. **Pornire transfer lung în background**
   ```
   mininet> h1 python3 server.py &
   mininet> h2 python3 client.py --get verylarge.bin &
   ```

3. **Adăugare latență în mijlocul transferului**
   ```
   mininet> sh tc qdisc add dev s1-eth1 root netem delay 200ms
   ```

4. **Observare efect**

5. **Revenire la normal**
   ```
   mininet> sh tc qdisc del dev s1-eth1 root
   ```

### Întrebări de reflecție
1. Ce se întâmplă cu rata de transfer când adăugăm latență?
2. Cât durează până TCP se adaptează la noile condiții?
3. Ce mecanisme TCP sunt responsabile pentru adaptare?

---

## Scenariu 7: Capturare și analiză completă

### Obiectiv
Realizarea unei capturi complete pentru analiză ulterioară cu Wireshark.

### Pași

1. **Pornire topologie**
   ```bash
   sudo python topo_base.py
   ```

2. **Pornire captură pe toate interfețele**
   ```
   mininet> h1 tcpdump -i h1-eth0 -w /tmp/h1_capture.pcap &
   mininet> h2 tcpdump -i h2-eth0 -w /tmp/h2_capture.pcap &
   ```

3. **Sesiune completă client-server**
   - AUTH
   - LIST
   - GET
   - PUT
   - QUIT

4. **Oprire capturi**
   ```
   mininet> h1 pkill tcpdump
   mininet> h2 pkill tcpdump
   ```

5. **Copiere fișiere pentru analiză externă**
   ```
   mininet> sh cp /tmp/*.pcap /host/shared/
   ```

### Analiza (în Wireshark GUI)
- Filtrare: `tcp.port == 9021`
- Follow TCP Stream pentru a vedea dialogul
- Identificare magic bytes, lungimi, CRC

---

## Checklist final scenarii Mininet

- [ ] Scenariu 1: Test de bază completat
- [ ] Scenariu 2: Impact latență observat
- [ ] Scenariu 3: Comparație local/remote efectuată
- [ ] Scenariu 4: Retransmisii identificate
- [ ] Scenariu 5: Rate limiting testat
- [ ] Scenariu 6: Modificare dinamică experimentată
- [ ] Scenariu 7: Captură completă realizată

## Note pentru instructor

### Timp estimat
- Scenarii 1-3: obligatorii, ~45 min
- Scenarii 4-7: opționale/avansate, ~30 min

### Probleme frecvente
- "No route to host" → verificați că hosts sunt în aceeași subrețea
- "Permission denied" → rulați cu sudo
- tcpdump nu capturează → verificați interfața corectă (h1-eth0, nu eth0)

### Extensii sugerate
- Adăugați un al treilea client și observați comportamentul
- Experimentați cu diferite dimensiuni de fișiere
- Încercați transferuri bidirecționale simultane
