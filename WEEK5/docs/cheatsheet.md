# Cheatsheet CLI — Săptămâna 5: Adresare IP

## Plan Rețea Week 5

| Componentă | Valoare |
|------------|---------|
| Rețea principală | `10.0.5.0/24` |
| Gateway/Router | `10.0.5.1` |
| Server aplicație | `10.0.5.100`, `10.0.5.101` |
| Hosturi standard | `h1=10.0.5.11`, `h2=10.0.5.12`, `h3=10.0.5.13` |
| Port Base | `5500-5599` |

## Comenzi Rapide

### Analiză CIDR

```bash
# Analiză completă
python3 python/exercises/ex_5_01_cidr_flsm.py analyze 192.168.10.14/26

# Cu detalii și binar
python3 python/exercises/ex_5_01_cidr_flsm.py analyze 192.168.10.14/26 --verbose

# Output JSON
python3 python/exercises/ex_5_01_cidr_flsm.py analyze 192.168.10.14/26 --json

# Conversie binară
python3 python/exercises/ex_5_01_cidr_flsm.py binary 10.0.5.1
```

### Subnetting FLSM

```bash
# Împărțire în 4 subrețele egale
python3 python/exercises/ex_5_01_cidr_flsm.py flsm 192.168.100.0/24 4

# Împărțire în 8 subrețele
python3 python/exercises/ex_5_01_cidr_flsm.py flsm 10.0.0.0/24 8

# Output JSON
python3 python/exercises/ex_5_01_cidr_flsm.py flsm 10.0.0.0/24 4 --json
```

### Alocare VLSM

```bash
# Alocare pentru 60, 20, 10, 2 hosturi
python3 python/exercises/ex_5_02_vlsm_ipv6.py vlsm 172.16.0.0/24 60 20 10 2

# Scenariul complex
python3 python/exercises/ex_5_02_vlsm_ipv6.py vlsm 10.10.0.0/22 200 100 50 25 10 2 2 2

# Output JSON
python3 python/exercises/ex_5_02_vlsm_ipv6.py vlsm 10.0.5.0/24 50 30 10 2 --json
```

### IPv6

```bash
# Comprimare adresă
python3 python/exercises/ex_5_02_vlsm_ipv6.py ipv6 2001:0db8:0000:0000:0000:0000:0000:0001

# Expandare adresă
python3 python/exercises/ex_5_02_vlsm_ipv6.py ipv6-expand 2001:db8::1

# Generare subrețele
python3 python/exercises/ex_5_02_vlsm_ipv6.py ipv6-subnets 2001:db8:10::/48 64 10

# Tipuri adrese IPv6
python3 python/exercises/ex_5_02_vlsm_ipv6.py ipv6-types
```

## Mininet

### Pornire Topologii

```bash
# Topologie bază (2 subrețele)
sudo python3 mininet/topologies/topo_5_base.py --cli

# Topologie extinsă (VLSM)
sudo python3 mininet/topologies/topo_5_extended.py --cli

# Cu IPv6 activat
sudo python3 mininet/topologies/topo_5_extended.py --cli --ipv6

# Test automat
sudo python3 mininet/topologies/topo_5_base.py --test
```

### Comenzi Mininet CLI

```bash
# Listare noduri și topologie
nodes
net
links

# Informații IP
h1 ip addr
h1 ip route
r1 ip route

# Ping și conectivitate
h1 ping -c 3 10.0.2.10
h1 ping6 -c 3 2001:db8:10:20::10

# Captură pachete
r1 tcpdump -ni r1-eth0 icmp &
h1 ping -c 5 10.0.2.10
r1 kill %tcpdump

# Terminal separat
xterm h1

# Ieșire
exit
```

### Cleanup Mininet

```bash
# Cleanup standard
sudo mn -c

# Restart OVS
sudo systemctl restart openvswitch-switch

# Script cleanup
./scripts/cleanup.sh --mininet
```

> **Truc:** Dacă Mininet rămâne blocat și `sudo mn -c` nu ajută, oprește complet OVS: `sudo systemctl stop openvswitch-switch`, așteaptă 5 secunde, apoi pornește-l din nou.

## Comenzi Linux IP

### Afișare Configurare

```bash
# Adrese IP
ip addr show
ip -4 addr show     # doar IPv4
ip -6 addr show     # doar IPv6

# Tabel rutare
ip route show
ip -6 route show

# Interfețe
ip link show
```

### Configurare Manuală

```bash
# Adăugare adresă
sudo ip addr add 10.0.5.100/24 dev eth0

# Ștergere adresă
sudo ip addr del 10.0.5.100/24 dev eth0

# Gateway implicit
sudo ip route add default via 10.0.5.1

# Rută specifică
sudo ip route add 192.168.0.0/16 via 10.0.5.1

# Activare IP forwarding
sudo sysctl -w net.ipv4.ip_forward=1
sudo sysctl -w net.ipv6.conf.all.forwarding=1
```

## Captură Trafic

### tcpdump

```bash
# Captură toate pachetele pe eth0
sudo tcpdump -i eth0

# Doar ICMP
sudo tcpdump -i eth0 icmp

# Doar o adresă
sudo tcpdump -i eth0 host 10.0.5.100

# Salvare în fișier
sudo tcpdump -i eth0 -w /tmp/capture.pcap

# Cu timestamps și verbose
sudo tcpdump -i eth0 -tttt -vv
```

### tshark

```bash
# Citire captură
tshark -r /tmp/capture.pcap

# Filtrare IP
tshark -r /tmp/capture.pcap -Y "ip.addr == 10.0.5.1"

# Câmpuri specifice
tshark -r /tmp/capture.pcap -T fields -e ip.src -e ip.dst -e ip.ttl

# Statistici
tshark -r /tmp/capture.pcap -q -z io,stat,1
```

## Formule Rapide

| Prefix | Mască | Hosturi | Increment |
|--------|-------|---------|-----------|
| /24 | 255.255.255.0 | 254 | 256 |
| /25 | 255.255.255.128 | 126 | 128 |
| /26 | 255.255.255.192 | 62 | 64 |
| /27 | 255.255.255.224 | 30 | 32 |
| /28 | 255.255.255.240 | 14 | 16 |
| /29 | 255.255.255.248 | 6 | 8 |
| /30 | 255.255.255.252 | 2 | 4 |

**Formula:** Hosturi = 2^(32-prefix) - 2

> **Pont rapid:** Pentru a ști câte adrese are un prefix, calculează 2 la puterea (32 minus prefix). Pentru hosturi, scazi 2.

## Make Targets

```bash
make help           # Toate comenzile
make setup          # Instalare
make test           # Smoke tests
make demo           # Demo complet
make demo-cidr      # Demo CIDR
make demo-vlsm      # Demo VLSM
make quiz           # Quiz interactiv
make clean          # Curățare
make reset          # Reset complet

# Mininet (cu sudo)
sudo make mininet-base
sudo make mininet-extended-ipv6
sudo make mininet-test
sudo make mininet-clean
```

## Referințe

- RFC 791: IPv4
- RFC 8200: IPv6
- RFC 1918: Adrese private
- RFC 4291: Arhitectura IPv6
- Mininet: http://mininet.org/walkthrough/

---

*ASE-CSIE | Rețele de calculatoare*
