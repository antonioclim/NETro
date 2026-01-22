# Capturi de Trafic – Săptămâna 11

## Descriere

Acest director conține exemple de capturi de trafic pentru analiza protocoalelor FTP, DNS și a scenariilor de load balancing.

## Generare capturi

### Captură DNS
```bash
# Rulare client DNS + captură
tshark -i any -f "udp port 53" -w pcap/dns_query.pcap -c 10 &
python3 ../python/exercises/ex_11_03_dns_client.py --query google.com --type A
```

### Captură Load Balancer
```bash
# Pornire stack + captură
make demo-nginx
tshark -i any -f "tcp port 8080" -w pcap/lb_traffic.pcap -c 50 &
for i in {1..20}; do curl -s http://localhost:8080/; done
```

### Captură FTP
```bash
# Demo FTP + captură
cd ../docker/ftp_demo
docker compose up -d
tshark -i any -f "tcp port 2121 or tcp portrange 30000-30009" -w ../pcap/ftp_session.pcap -c 30 &
```

## Analiza capturilor

### Citire cu tshark
```bash
tshark -r dns_query.pcap -T fields -e dns.qry.name -e dns.a
tshark -r lb_traffic.pcap -q -z io,stat,0.5
```

### Citire cu Wireshark
```bash
wireshark ftp_session.pcap
```

## Note

- Capturile sunt regenerate la fiecare rulare `make capture`
- Fișierele `.pcap` mari sunt excluse din Git (vedeți `.gitignore`)
- Pentru analiza avansată, folosiți `tshark -r file.pcap -V`

---
*Revolvix&Hypotheticalandrei*
