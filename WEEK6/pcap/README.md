# PCAP Directory

Acest director va conține fișiere de captură Wireshark/tshark generate în timpul demonstrațiilor.

## Fișiere generate automat

După rularea demo-urilor, veți găsi aici:
- `pre_nat.pcap` - Captură pe interfața internă a routerului NAT
- `post_nat.pcap` - Captură pe interfața externă (după traducere)
- `sdn_flows.pcap` - Captură trafic controlat de SDN

## Generare capturi

```bash
# Din Mininet CLI
rnat tcpdump -i rnat-eth0 -w /tmp/pre_nat.pcap &
rnat tcpdump -i rnat-eth1 -w /tmp/post_nat.pcap &
```

## Analiză

```bash
tshark -r pre_nat.pcap -Y "icmp" -T fields -e ip.src -e ip.dst
```

---
*Revolvix&Hypotheticalandrei*
