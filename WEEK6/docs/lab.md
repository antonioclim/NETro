# Laborator 6 – Ghid Pas cu Pas
## NAT/PAT, SDN, Analiza Traficului în Mininet

**Format:** Laborator experimental autodirijat  
**Timp estimat:** 90-120 minute  
**Nivel:** Intermediar

---

## Step 0: Pregătirea mediului

### 0.1 Verificare sistem

```bash
# Verifică versiunea Python
python3 --version  # Trebuie >= 3.8

# Verifică Mininet
mn --version  # Trebuie >= 2.3.0

# Verifică Open vSwitch
ovs-vsctl --version

# Verifică iptables
iptables --version
```

### 0.2 Instalare dependențe (dacă lipsesc)

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y \
  python3 python3-pip python3-venv \
  mininet openvswitch-switch \
  tcpdump tshark iptables \
  iproute2 iputils-ping traceroute

# Python packages
pip3 install --break-system-packages os-ken scapy
```

### 0.3 Navigare la starterkit

```bash
cd starterkit_s6
make check
```

**Output așteptat:**
```
✓ python3
✓ mininet (mn)
✓ openvswitch
✓ tcpdump
✓ tshark
✓ iptables
✓ os-ken
```

---

## Step 1: NAT/PAT Demo (30 min)

### 1.1 Curățare și pornire topologie

```bash
# Curățare artefacte anterioare
sudo mn -c

# Pornire topologie NAT
sudo python3 seminar/mininet/topologies/topo_nat.py --cli
```

**Ce ar trebui să vezi:**
```
*** Creating network
*** Adding hosts:
h1 h2 h3 rnat 
*** Adding links:
(h1, s1) (h2, s1) (h3, s2) (rnat, s1) (rnat, s2) 
*** Configuring hosts
*** Configurare NAT completă
*** h1/h2 (192.168.1.x) → NAT → 203.0.113.1 → h3

============================================================
  TOPOLOGIE NAT/PAT PORNITĂ
  Comenzi utile:
    h1 ping 203.0.113.2
    rnat iptables -t nat -L -n -v
    h3 tcpdump -ni h3-eth0 icmp
============================================================

mininet>
```

### 1.2 Verificare adrese IP

```bash
mininet> h1 ip -br addr
# h1-eth0: 192.168.1.10/24

mininet> h2 ip -br addr
# h2-eth0: 192.168.1.20/24

mininet> h3 ip -br addr
# h3-eth0: 203.0.113.2/24

mininet> rnat ip -br addr
# rnat-eth0: 192.168.1.1/24
# rnat-eth1: 203.0.113.1/24
```

### 1.3 Test ping prin NAT

**🔮 PREDICȚIE înainte de execuție:**
> h1 are adresa 192.168.1.10 (privată, RFC 1918).
> h3 este pe "Internet" la 203.0.113.2.
> 
> Crezi că ping-ul va funcționa? □ Da □ Nu
> Dacă da, de ce? ________________________________

```bash
mininet> h1 ping -c 3 203.0.113.2
```

**Output așteptat:**
```
PING 203.0.113.2 (203.0.113.2) 56(84) bytes of data.
64 bytes from 203.0.113.2: icmp_seq=1 ttl=63 time=0.5 ms
64 bytes from 203.0.113.2: icmp_seq=2 ttl=63 time=0.3 ms
64 bytes from 203.0.113.2: icmp_seq=3 ttl=63 time=0.2 ms

--- 203.0.113.2 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss
```

**✅ Verificare predicție:** Funcționează pentru că router-ul NAT traduce 192.168.1.10 → 203.0.113.1

### 1.4 Inspectare reguli NAT

```bash
mininet> rnat iptables -t nat -L -n -v
```

**Output așteptat:**
```
Chain PREROUTING (policy ACCEPT)
...

Chain POSTROUTING (policy ACCEPT)
target     prot opt source        destination
MASQUERADE all  --  192.168.1.0/24  0.0.0.0/0

Chain OUTPUT (policy ACCEPT)
...
```

**Explicație:**
- `MASQUERADE` pe chain-ul `POSTROUTING`
- Se aplică pentru surse din 192.168.1.0/24
- Destinație: orice (0.0.0.0/0)

### 1.5 Observare traducere cu NAT Observer

**🔮 PREDICȚIE înainte de test:**
> Dacă h1 și h2 se conectează la serverul de pe h3, ce adresă IP sursă va vedea h3?
> 
> □ 192.168.1.10 pentru h1 și 192.168.1.20 pentru h2 (IP-urile reale)
> □ 203.0.113.1 pentru ambele (IP-ul NAT)
> □ Altceva: ________________________________

**Terminal 1 (server pe h3):**
```bash
mininet> xterm h3
# În xterm h3:
python3 seminar/python/apps/nat_observer.py server --bind 203.0.113.2 --port 5000
```

**Terminal principal (clienți):**
```bash
mininet> h1 python3 seminar/python/apps/nat_observer.py client \
    --host 203.0.113.2 --port 5000 --msg "Salut de la h1"

mininet> h2 python3 seminar/python/apps/nat_observer.py client \
    --host 203.0.113.2 --port 5000 --msg "Salut de la h2"
```

**Ce vezi pe server (h3):**
```
[2025-01-15 10:30:15] Connection from 203.0.113.1:40001 - Message: Salut de la h1
[2025-01-15 10:30:20] Connection from 203.0.113.1:40002 - Message: Salut de la h2
```

**✅ Verificare predicție - Observație crucială:**
- Ambele conexiuni apar ca venind de la **203.0.113.1** (IP-ul router-ului)
- Diferențierea se face prin **porturi diferite** (40001, 40002)
- Aceasta este esența PAT (Port Address Translation)!

### 1.6 Captură trafic cu tcpdump

**🔮 PREDICȚIE:** În captura de pe h3, se va vedea adresa 192.168.1.10?
> □ Da, tcpdump capturează pachetele originale
> □ Nu, NAT modifică pachetele înainte să ajungă la h3

```bash
mininet> h3 tcpdump -ni h3-eth0 -c 10 icmp or tcp port 5000
```

**În paralel, în alt terminal:**
```bash
mininet> h1 ping -c 3 203.0.113.2
```

**Output tcpdump:**
```
10:35:01.123456 IP 203.0.113.1 > 203.0.113.2: ICMP echo request
10:35:01.123789 IP 203.0.113.2 > 203.0.113.1: ICMP echo reply
```

**✅ Verificare predicție:** NU se vede 192.168.1.10! NAT a tradus adresa.

### 1.7 Cleanup

```bash
mininet> exit
sudo mn -c
```

---

## Step 2: Rutare Statică (15 min, opțional)

### 2.1 Pornire topologie triunghi

```bash
sudo mn -c
sudo python3 seminar/mininet/topologies/topo_triangle.py --cli
```

### 2.2 Verificare rute

```bash
mininet> r1 ip route
# 10.0.2.0/30 via 10.0.12.2 dev r1-eth0
# 10.0.3.0/30 via 10.0.13.2 dev r1-eth1
# 10.0.12.0/30 dev r1-eth0 proto kernel scope link src 10.0.12.1
# 10.0.13.0/30 dev r1-eth1 proto kernel scope link src 10.0.13.1

mininet> r1 traceroute -n 10.0.3.2
```

### 2.3 Modificare cale

**🔮 PREDICȚIE:** Dacă ștergem ruta directă r1→r3, ce cale va lua traficul?
> □ Traficul va eșua complet
> □ Traficul va merge prin r2 (cale alternativă)
> □ Routerul va genera eroare ICMP

Forțează traficul să treacă prin r2:

```bash
# Șterge ruta directă
mininet> r1 ip route del 10.0.3.0/30 via 10.0.13.2

# Adaugă rută via r2
mininet> r1 ip route add 10.0.3.0/30 via 10.0.12.2

# Verifică noua cale
mininet> r1 traceroute -n 10.0.3.2
```

**✅ Verificare predicție - Output după modificare:**
```
traceroute to 10.0.3.2
 1  10.0.12.2  0.5 ms  (r2)
 2  10.0.23.2  0.8 ms  (r3)
 3  10.0.3.2   1.0 ms  (destinația)
```

---

## Step 3: SDN cu OpenFlow (40 min)

### 3.1 Pornire controller (Terminal 1)

```bash
cd starterkit_s6
osken-manager seminar/python/controllers/sdn_policy_controller.py
```

**Output așteptat:**
```
loading app seminar/python/controllers/sdn_policy_controller.py
instantiating app seminar/python/controllers/sdn_policy_controller.py of SDNPolicyController
```

**Lasă acest terminal deschis!**

### 3.2 Pornire topologie SDN (Terminal 2)

```bash
sudo mn -c
sudo python3 seminar/mininet/topologies/topo_sdn.py --cli
```

**În logurile controller-ului (Terminal 1), ar trebui să vezi:**
```
Table-miss installed on dpid=1 (packets→controller)
```

### 3.3 Test conectivitate

**🔮 PREDICȚIE înainte de teste:**
> Controller-ul implementează politica: h1↔h2 PERMIT, *→h3 DROP
> 
> Ping h1 → h2 (10.0.10.2): □ Va funcționa □ Va eșua
> Ping h1 → h3 (10.0.10.3): □ Va funcționa □ Va eșua

```bash
# Test h1 → h2 (PERMIT - trebuie să funcționeze)
mininet> h1 ping -c 3 10.0.10.2
```

**Output așteptat:**
```
64 bytes from 10.0.10.2: icmp_seq=1 ttl=64 time=1.5 ms
64 bytes from 10.0.10.2: icmp_seq=2 ttl=64 time=0.3 ms
...
```

```bash
# Test h1 → h3 (DROP - trebuie să eșueze)
mininet> h1 ping -c 3 10.0.10.3
```

**Output așteptat:**
```
PING 10.0.10.3 (10.0.10.3) 56(84) bytes of data.

--- 10.0.10.3 ping statistics ---
3 packets transmitted, 0 received, 100% packet loss
```

**✅ Verificare predicție:** Politica funcționează conform așteptărilor.

### 3.4 Inspectare flow table

**🔮 PREDICȚIE:** Cum arată o regulă de DROP în flow table?
> □ actions=DROP
> □ actions=drop
> □ actions= (listă goală)
> □ Nu există regulă, pachetele sunt ignorate

```bash
mininet> sh ovs-ofctl -O OpenFlow13 dump-flows s1
```

**Output exemplu:**
```
cookie=0x0, duration=45.123s, table=0, n_packets=6, n_bytes=588, 
  priority=10, ip, nw_src=10.0.10.1, nw_dst=10.0.10.2 
  actions=output:2

cookie=0x0, duration=45.123s, table=0, n_packets=6, n_bytes=588, 
  priority=10, ip, nw_src=10.0.10.2, nw_dst=10.0.10.1 
  actions=output:1

cookie=0x0, duration=30.456s, table=0, n_packets=3, n_bytes=252, 
  priority=30, ip, nw_dst=10.0.10.3, ip_proto=1 
  actions=drop

cookie=0x0, duration=120.789s, table=0, n_packets=15, n_bytes=1230, 
  priority=0 
  actions=CONTROLLER:65535
```

**✅ Verificare predicție:** `actions=drop` sau lista goală înseamnă DROP

**Interpretare:**
| Regulă | priority | match | actions | Efect |
|--------|----------|-------|---------|-------|
| h1↔h2 | 10 | nw_src/dst | output:X | PERMIT |
| →h3 ICMP | 30 | nw_dst=h3, proto=1 | drop | BLOCK |
| table-miss | 0 | (orice) | CONTROLLER | Trimite la controller |

### 3.5 Trafic aplicație

**Server TCP pe h2:**
```bash
mininet> h2 python3 seminar/python/apps/tcp_echo.py server \
    --bind 10.0.10.2 --port 5000 &
```

**Client TCP de pe h1:**
```bash
mininet> h1 python3 seminar/python/apps/tcp_echo.py client \
    --dst 10.0.10.2 --port 5000 --message "Hello TCP"
```

**Output așteptat:**
```
Sent: Hello TCP
Received: Hello TCP (echo from server)
```

### 3.6 Modificare politică

**Editează controller-ul:**
```bash
# În alt terminal (nu în Mininet CLI)
nano seminar/python/controllers/sdn_policy_controller.py
```

**Găsește și modifică:**
```python
# Schimbă din:
ALLOW_UDP_TO_H3 = False

# În:
ALLOW_UDP_TO_H3 = True
```

**Repornește:**
```bash
# Oprește controller-ul (Ctrl+C în Terminal 1)
# Repornește:
osken-manager seminar/python/controllers/sdn_policy_controller.py

# În Terminal 2:
mininet> exit
sudo mn -c
sudo python3 seminar/mininet/topologies/topo_sdn.py --cli
```

**🔮 PREDICȚIE după modificare:**
> Cu ALLOW_UDP_TO_H3=True, ce va funcționa către h3?
> □ Doar UDP
> □ UDP și TCP
> □ UDP și ICMP
> □ Tot traficul

**Test UDP către h3:**
```bash
# Server UDP pe h3
mininet> h3 python3 seminar/python/apps/udp_echo.py server \
    --bind 10.0.10.3 --port 6000 &

# Client UDP de pe h1
mininet> h1 python3 seminar/python/apps/udp_echo.py client \
    --dst 10.0.10.3 --port 6000 --message "Hello UDP"
```

**✅ Verificare predicție:** Doar UDP funcționează! TCP și ICMP rămân blocate.

### 3.7 Verificare flow table după modificare

```bash
mininet> sh ovs-ofctl -O OpenFlow13 dump-flows s1
```

**Ar trebui să vezi o regulă nouă:**
```
priority=20, ip, nw_dst=10.0.10.3, ip_proto=17 actions=output:3
```

---

## Step 4: Verificare și cleanup final

### 4.1 Smoke test automat

```bash
make smoke-test
```

### 4.2 Cleanup complet

```bash
make clean
# sau manual:
sudo mn -c
sudo pkill -9 -f osken-manager
sudo ovs-vsctl --if-exists del-br s1
```

---

## Expected Outputs Reference

### NAT Ping Success
```
PING 203.0.113.2 (203.0.113.2) 56(84) bytes of data.
64 bytes from 203.0.113.2: icmp_seq=1 ttl=63 time=0.XXX ms
```

### SDN Ping h1→h2 Success
```
PING 10.0.10.2 (10.0.10.2) 56(84) bytes of data.
64 bytes from 10.0.10.2: icmp_seq=1 ttl=64 time=X.XXX ms
```

### SDN Ping h1→h3 Blocked
```
PING 10.0.10.3 (10.0.10.3) 56(84) bytes of data.
--- 10.0.10.3 ping statistics ---
3 packets transmitted, 0 received, 100% packet loss
```

### Controller Log (packet_in)
```
IPv4: 10.0.10.1 → 10.0.10.2 (proto=1) in_port=1
ALLOW: 10.0.10.1 → 10.0.10.2 (proto=1) out_port=2
```

---

## What-If Scenarios

### Ce se întâmplă dacă...

| Modificare | Efect |
|------------|-------|
| Dezactivezi IP forwarding pe rnat | NAT nu mai funcționează, ping eșuează |
| Ștergi regula MASQUERADE | Pachetele ies cu IP privat, răspunsurile nu ajung înapoi |
| Oprești controller-ul SDN | Switch-ul nu mai știe ce să facă cu pachete noi |
| Crești priority pe table-miss | Toate pachetele ajung la controller (overhead mare) |
| Adaugi regulă DROP pentru h2 | h2 devine izolat de restul rețelei |

---

## Fișiere cheie din starterkit

| Fișier | Rol |
|--------|-----|
| `seminar/mininet/topologies/topo_nat.py` | Topologie NAT cu router Linux |
| `seminar/mininet/topologies/topo_sdn.py` | Topologie SDN cu OVS |
| `seminar/python/controllers/sdn_policy_controller.py` | Controller cu politici |
| `seminar/python/apps/nat_observer.py` | Server/client pentru observare NAT |
| `seminar/python/apps/tcp_echo.py` | Echo server/client TCP |
| `seminar/python/apps/udp_echo.py` | Echo server/client UDP |
| `Makefile` | Automatizări (make nat-demo, make sdn-demo) |

---

*Revolvix&Hypotheticalandrei*
