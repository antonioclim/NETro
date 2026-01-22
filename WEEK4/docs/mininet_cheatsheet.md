# Cheatsheet: Mininet CLI
## Ghid rapid pentru simularea rețelelor

**Săptămâna 4 - Nivelul Fizic și Legătura de Date**  
*Revolvix&Hypotheticalandrei*

---

## Ce este Mininet?

Mininet este un simulator de rețea care creează o rețea virtuală realistă:
- Hosturi (procese Linux cu namespaces separate)
- Switch-uri (Open vSwitch)
- Controllere SDN
- Linkuri virtuale cu caracteristici configurabile

---

## Pornire Mininet

### Topologii predefinite
```bash
# Topologie minimală (1 switch, 2 hosturi)
sudo mn

# Topologie simplă (1 switch, N hosturi)
sudo mn --topo single,4

# Topologie liniară (N switch-uri în serie)
sudo mn --topo linear,3

# Topologie arbore
sudo mn --topo tree,depth=2,fanout=2
```

### Opțiuni utile
```bash
# Cu MAC-uri predictibile
sudo mn --mac

# Cu controller remote
sudo mn --controller=remote,ip=127.0.0.1,port=6633

# Cu switch specific
sudo mn --switch ovsk          # Open vSwitch kernel
sudo mn --switch ovsbr         # Open vSwitch bridge

# Cu link-uri configurate
sudo mn --link tc,bw=10,delay=5ms,loss=1

# Fără controller (switch learning)
sudo mn --controller=none

# Cu log verbose
sudo mn -v debug
```

---

## Comenzi CLI Mininet

### Informații rețea
```bash
mininet> help              # Lista comenzi
mininet> nodes             # Lista noduri
mininet> net               # Topologie (conexiuni)
mininet> dump              # Info detaliate noduri
mininet> links             # Status linkuri
mininet> ports             # Porturi switch
```

### Executare comenzi pe hosturi
```bash
# Sintaxă: <node> <comandă>
mininet> h1 ifconfig
mininet> h1 ip addr
mininet> h1 ping -c 3 h2
mininet> h1 arp -n
mininet> h2 python3 --version
```

### Testare conectivitate
```bash
mininet> pingall           # Ping între toate perechile
mininet> pingpair          # Ping între primele 2 hosturi
mininet> h1 ping -c 1 h2   # Ping specific
```

### Bandwidth test
```bash
mininet> iperf             # Test bandwidth (default)
mininet> iperf h1 h2       # Test între h1 și h2
mininet> h1 iperf -s &     # Server iperf pe h1
mininet> h2 iperf -c h1    # Client iperf pe h2
```

### Managementul terminalelor
```bash
mininet> xterm h1          # Deschide terminal pentru h1
mininet> xterm h1 h2       # Terminale pentru h1 și h2
mininet> xterm s1          # Terminal pentru switch
```

### Control linkuri
```bash
mininet> link s1 h1 down   # Dezactivează link
mininet> link s1 h1 up     # Activează link
```

### Ieșire
```bash
mininet> exit
mininet> quit
```

---

## Exemple practice Săptămâna 4

### Demo ARP
```bash
# Pornire
sudo mn --mac

# În CLI Mininet:
mininet> h1 ip neigh flush all    # Curăță cache ARP
mininet> h2 ip neigh flush all

# Captură ARP pe h2
mininet> h2 tcpdump -i h2-eth0 arp &

# Ping pentru a declanșa ARP
mininet> h1 ping -c 1 h2

# Verificare cache ARP
mininet> h1 arp -n
mininet> h2 arp -n

# Oprire captură
mininet> h2 pkill tcpdump
```

### Demo TCP client-server
```bash
# Pornire cu MAC-uri fixe
sudo mn --mac

# Terminal pentru server
mininet> xterm h2

# În terminalul h2 (server):
# python3 /path/to/text_proto_server.py --port 5400

# În CLI Mininet (client):
mininet> h1 nc 10.0.0.2 5400

# Sau cu scriptul Python:
mininet> h1 python3 /path/to/text_proto_client.py --host 10.0.0.2 --port 5400 --message "Test"
```

### Captură trafic
```bash
# Pornire captură pe h2
mininet> h2 tshark -i h2-eth0 -w /tmp/capture.pcap &

# Generare trafic
mininet> h1 ping -c 5 h2

# Oprire captură
mininet> h2 pkill tshark

# Analiză (de pe host principal)
# tshark -r /tmp/capture.pcap
```

### Simulare pierderi pachete
```bash
# Adăugare loss pe interfața h1
mininet> h1 tc qdisc add dev h1-eth0 root netem loss 10%

# Verificare
mininet> h1 tc qdisc show dev h1-eth0

# Test cu ping (vom vedea pierderi)
mininet> h1 ping -c 20 h2

# Resetare
mininet> h1 tc qdisc del dev h1-eth0 root
```

### Simulare delay
```bash
# Adăugare delay 100ms
mininet> h1 tc qdisc add dev h1-eth0 root netem delay 100ms

# Test RTT (vom vedea ~200ms dus-întors)
mininet> h1 ping -c 5 h2

# Resetare
mininet> h1 tc qdisc del dev h1-eth0 root
```

---

## Topologii custom (Python API)

### Structura de bază
```python
#!/usr/bin/env python3
from mininet.net import Mininet
from mininet.node import Controller, OVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.link import TCLink

def create_topology():
    net = Mininet(
        controller=Controller,
        switch=OVSSwitch,
        link=TCLink
    )
    
    # Adăugare controller
    net.addController('c0')
    
    # Adăugare switch
    s1 = net.addSwitch('s1')
    
    # Adăugare hosturi
    h1 = net.addHost('h1', ip='10.0.0.1/24')
    h2 = net.addHost('h2', ip='10.0.0.2/24')
    
    # Creare linkuri
    net.addLink(h1, s1, bw=100, delay='5ms')
    net.addLink(h2, s1, bw=100, delay='5ms')
    
    return net

if __name__ == '__main__':
    setLogLevel('info')
    net = create_topology()
    net.start()
    CLI(net)
    net.stop()
```

### Rulare topologie custom
```bash
sudo python3 my_topology.py
```

### Opțiuni Link (TCLink)
```python
net.addLink(h1, s1,
    bw=10,           # Bandwidth Mbps
    delay='5ms',     # Delay
    loss=1,          # Packet loss %
    max_queue_size=100,  # Queue size
    use_htb=True     # Hierarchical Token Bucket
)
```

---

## Open vSwitch (OVS) Commands

### În CLI Mininet sau terminal switch
```bash
# Informații switch
mininet> s1 ovs-vsctl show

# Tabela MAC (CAM)
mininet> s1 ovs-appctl fdb/show s1

# Flow-uri OpenFlow
mininet> s1 ovs-ofctl dump-flows s1

# Porturi switch
mininet> s1 ovs-ofctl dump-ports s1

# Statistici porturi
mininet> s1 ovs-ofctl dump-ports-desc s1
```

### Adăugare flow-uri manual
```bash
# Permite tot traficul
mininet> s1 ovs-ofctl add-flow s1 action=normal

# Drop pachete pe portul 80
mininet> s1 ovs-ofctl add-flow s1 "tcp,tp_dst=80,actions=drop"

# Forward specific
mininet> s1 ovs-ofctl add-flow s1 "in_port=1,actions=output:2"
```

---

## Debugging și Troubleshooting

### Verificări comune
```bash
# Verificare procese Mininet
ps aux | grep mininet

# Cleanup după crash
sudo mn -c

# Log-uri OVS
sudo ovs-vsctl show
sudo ovs-ofctl show s1

# Verificare namespace-uri
ip netns list
```

### Probleme frecvente

| Problemă | Cauză | Soluție |
|----------|-------|---------|
| "RTNETLINK answers: File exists" | Instanță anterioară | `sudo mn -c` |
| Hosturi nu comunică | ARP/routing | Verificați `ip route`, `arp -n` |
| Bandwidth incorect | tc neaplicat | Verificați `tc qdisc show` |
| "Exception: could not connect" | Controller lipsă | Adăugați controller |
| xterm nu funcționează | X11 | Verificați DISPLAY |

### Cleanup complet
```bash
sudo mn -c
sudo ovs-vsctl --if-exists del-br s1
sudo pkill -9 controller
sudo pkill -9 ovs
```

---

## Integrare cu Python aplicații

### Executare script pe host
```python
# În script Python de topologie
h1.cmd('python3 /path/to/server.py &')
time.sleep(2)  # Așteptăm pornirea
result = h2.cmd('python3 /path/to/client.py')
print(result)
```

### Captură programatică
```python
# Pornire captură
h2.cmd('tshark -i h2-eth0 -w /tmp/cap.pcap &')
time.sleep(1)

# Generare trafic
h1.cmd('ping -c 5 10.0.0.2')

# Oprire captură
h2.cmd('pkill tshark')
```

---

## Resurse

- Documentație: http://mininet.org/walkthrough/
- GitHub: https://github.com/mininet/mininet
- Wiki: https://github.com/mininet/mininet/wiki
- Open vSwitch: http://www.openvswitch.org/
