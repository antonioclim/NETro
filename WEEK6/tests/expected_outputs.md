# Expected Outputs - Săptămâna 6

Acest document conține output-urile așteptate pentru toate demonstrațiile și testele din laboratorul S6.

## NAT Demo

### Pornire topologie

```
$ make nat-demo
[INFO] Curățare configurație anterioară...
[INFO] Pornire topologie NAT...
*** Creating network
*** Adding hosts: h1 h2 h3 rnat
*** Adding switches: s1 s2
*** Adding links:
(h1, s1) (h2, s1) (s1, rnat) (rnat, s2) (s2, h3) 
*** Configuring hosts
*** Configuring NAT (MASQUERADE)...
✓ NAT configurat cu succes

=== TOPOLOGIE NAT ===
  h1 (10.0.1.101) ─┐
                   ├── s1 ── rnat ── s2 ── h3 (192.168.1.103)
  h2 (10.0.1.102) ─┘        │
                      MASQUERADE

*** Starting CLI:
mininet> 
```

### Test ping h1 → h3

```
mininet> h1 ping -c 3 192.168.1.103
PING 192.168.1.103 (192.168.1.103) 56(84) bytes of data.
64 bytes from 192.168.1.103: icmp_seq=1 ttl=63 time=0.521 ms
64 bytes from 192.168.1.103: icmp_seq=2 ttl=63 time=0.312 ms
64 bytes from 192.168.1.103: icmp_seq=3 ttl=63 time=0.287 ms

--- 192.168.1.103 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 2004ms
rtt min/avg/max/mdev = 0.287/0.373/0.521/0.104 ms
```

**Note**: TTL=63 indică un hop prin router (64-1=63)

### Verificare iptables NAT

```
mininet> rnat iptables -t nat -L -n -v
Chain PREROUTING (policy ACCEPT 0 packets, 0 bytes)
 pkts bytes target     prot opt in     out     source               destination         

Chain INPUT (policy ACCEPT 0 packets, 0 bytes)
 pkts bytes target     prot opt in     out     source               destination         

Chain OUTPUT (policy ACCEPT 0 packets, 0 bytes)
 pkts bytes target     prot opt in     out     source               destination         

Chain POSTROUTING (policy ACCEPT 0 packets, 0 bytes)
 pkts bytes target     prot opt in     out     source               destination         
   12   784 MASQUERADE  all  --  *      rnat-eth1  10.0.1.0/24          0.0.0.0/0
```

### NAT Observer - Server output

```
=== NAT Observer Server ===
Ascultă pe 0.0.0.0:8080
[CONN] Client de la 192.168.1.1:45231
[CONN] Client de la 192.168.1.1:45232
[CONN] Client de la 192.168.1.1:45233
---
Observație: IP identic (NAT), porturi diferite (PAT)!
```

### NAT Observer - Client output

```
=== NAT Observer Client ===
Hostname local: h1
Conectare la 192.168.1.103:8080...
Conectat!
Răspuns server: Server-ul te vede ca: 192.168.1.1:45231
---
Comparație:
  IP local (real): 10.0.1.101
  IP văzut de server: 192.168.1.1
  → NAT activ!
```

### Conntrack table

```
mininet> rnat conntrack -L
icmp     1 29 src=10.0.1.101 dst=192.168.1.103 type=8 code=0 id=1234 src=192.168.1.103 dst=192.168.1.1 type=0 code=0 id=1234 [ASSURED] mark=0
tcp      6 431999 ESTABLISHED src=10.0.1.101 dst=192.168.1.103 sport=54321 dport=8080 src=192.168.1.103 dst=192.168.1.1 sport=8080 dport=45231 [ASSURED] mark=0
```

---

## SDN Demo

### Pornire controller

```
$ make controller-start
[INFO] Pornire controller SDN...
loading app sdn_policy_controller.py
instantiating app sdn_policy_controller.py of PolicyController
(pid=12345) starting...
OFPHandler: DPSET/HANDSHAKE_DISPATCHER
```

### Pornire topologie SDN

```
$ make sdn-demo
[INFO] Curățare configurație anterioară...
[INFO] Pornire topologie SDN...
*** Creating network
*** Adding controller
*** Adding hosts: h1 h2 h3
*** Adding switches: s1
*** Adding links:
(h1, s1) (h2, s1) (h3, s1) 
*** Configuring hosts
*** Starting controller
*** Starting switch s1
...connected to controller

=== TOPOLOGIE SDN ===
Politici active:
  ✓ h1 ↔ h2: PERMIT
  ✗ * → h3: DROP

*** Starting CLI:
mininet>
```

### Test h1 → h2 (PERMIT)

```
mininet> h1 ping -c 2 10.0.10.2
PING 10.0.10.2 (10.0.10.2) 56(84) bytes of data.
64 bytes from 10.0.10.2: icmp_seq=1 ttl=64 time=12.3 ms
64 bytes from 10.0.10.2: icmp_seq=2 ttl=64 time=0.234 ms

--- 10.0.10.2 ping statistics ---
2 packets transmitted, 2 received, 0% packet loss, time 1001ms
rtt min/avg/max/mdev = 0.234/6.267/12.300/6.033 ms
```

**Note**: Primul ping e mai lent (table-miss → controller → flow install)

### Test h1 → h3 (DROP)

```
mininet> h1 ping -c 2 -W 2 10.0.10.3
PING 10.0.10.3 (10.0.10.3) 56(84) bytes of data.

--- 10.0.10.3 ping statistics ---
2 packets transmitted, 0 received, 100% packet loss, time 1001ms
```

### Flow table (înainte de modificare)

```
$ sudo ovs-ofctl dump-flows s1
 cookie=0x0, duration=45.123s, table=0, n_packets=0, n_bytes=0, priority=0 actions=CONTROLLER:65535
 cookie=0x0, duration=45.001s, table=0, n_packets=4, n_bytes=392, priority=10,ip,nw_src=10.0.10.1,nw_dst=10.0.10.2 actions=output:2
 cookie=0x0, duration=45.001s, table=0, n_packets=4, n_bytes=392, priority=10,ip,nw_src=10.0.10.2,nw_dst=10.0.10.1 actions=output:1
 cookie=0x0, duration=45.001s, table=0, n_packets=2, n_bytes=196, priority=30,ip,nw_dst=10.0.10.3 actions=drop
```

### Flow table (după ALLOW_UDP_TO_H3=True)

```
$ sudo ovs-ofctl dump-flows s1
 cookie=0x0, duration=12.456s, table=0, n_packets=0, n_bytes=0, priority=0 actions=CONTROLLER:65535
 cookie=0x0, duration=12.234s, table=0, n_packets=4, n_bytes=392, priority=10,ip,nw_src=10.0.10.1,nw_dst=10.0.10.2 actions=output:2
 cookie=0x0, duration=12.234s, table=0, n_packets=4, n_bytes=392, priority=10,ip,nw_src=10.0.10.2,nw_dst=10.0.10.1 actions=output:1
 cookie=0x0, duration=12.234s, table=0, n_packets=0, n_bytes=0, priority=20,udp,nw_dst=10.0.10.3 actions=output:3
 cookie=0x0, duration=12.234s, table=0, n_packets=2, n_bytes=196, priority=30,ip,nw_dst=10.0.10.3 actions=drop
```

### Controller log (fragment)

```
[PolicyController] Switch connected: dpid=0000000000000001
[PolicyController] Installing default table-miss rule
[PolicyController] Installing policy: h1 <-> h2 PERMIT
[PolicyController] Installing policy: * -> h3 DROP
[PolicyController] ALLOW_UDP_TO_H3 = True, installing UDP permit rule
[PolicyController] PacketIn from dpid=1: eth_src=00:00:00:00:00:01, eth_dst=00:00:00:00:00:02
[PolicyController] Installing flow: 10.0.10.1 -> 10.0.10.2, out_port=2
```

---

## UDP Echo (după modificare politici)

### Server (h3)

```
mininet> h3 python3 udp_echo.py server --port 9000
=== UDP Echo Server ===
Ascultă pe 0.0.0.0:9000
[RECV] De la 10.0.10.1:54321: "Hello from h1"
[SEND] Echo trimis către 10.0.10.1:54321
```

### Client (h1)

```
mininet> h1 python3 udp_echo.py client --host 10.0.10.3 --port 9000
=== UDP Echo Client ===
Trimitere către 10.0.10.3:9000
Mesaj: Hello from h1
Răspuns: Hello from h1 [ECHO]
RTT: 2.34 ms
```

---

## Verificări de mediu

### make check

```
$ make check
[CHECK] Verificare dependențe...
  ✓ python3          3.10.12
  ✓ mn (mininet)     2.3.1
  ✓ ovs-vsctl        2.17.0
  ✓ tcpdump          4.99.1
  ✓ tshark           3.6.2
  ✓ iptables         1.8.7
  ✓ conntrack        1.4.6
  ✓ osken-manager    prezent
  ✓ os_ken module    importabil
  ✓ scapy module     importabil
[OK] Toate dependențele sunt instalate!
```

### make clean

```
$ make clean
[INFO] Curățare artefacte...
[INFO] Oprire controller SDN...
[INFO] Curățare Mininet...
*** Removing excess controllers/ofprotocols/ofdatapaths/paborers
*** Removing junk from /tmp
*** Removing junk from /etc/lxc/auto
*** Removing excess kernel datapaths
*** Removing OVS datapaths
*** Removing all links of the pattern foo-eth0
*** Cleanup complete.
[OK] Mediu curățat!
```

---

## Error Outputs (pentru debugging)

### NAT nu funcționează - IP forwarding off

```
mininet> h1 ping -c 1 192.168.1.103
PING 192.168.1.103 (192.168.1.103) 56(84) bytes of data.

--- 192.168.1.103 ping statistics ---
1 packets transmitted, 0 received, 100% packet loss, time 0ms

# Verificare:
mininet> rnat sysctl net.ipv4.ip_forward
net.ipv4.ip_forward = 0

# Soluție:
mininet> rnat sysctl -w net.ipv4.ip_forward=1
```

### Controller nu se conectează - Port ocupat

```
$ make controller-start
[ERROR] Port 6633 already in use
Address already in use

# Soluție:
$ sudo pkill -9 osken-manager
$ sudo fuser -k 6633/tcp
$ make controller-start
```

### Mininet artefacte vechi

```
$ make nat-demo
*** Error: could not create interface

# Soluție:
$ sudo mn -c
$ make nat-demo
```

---

*Revolvix&Hypotheticalandrei*
