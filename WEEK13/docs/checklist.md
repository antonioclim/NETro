# Checklist Cadru Didactic — Săptămâna 13

## Înainte de Laborator

- [ ] Verificare VM-uri disponibile în sală
- [ ] Test Docker funcțional pe stația demo
- [ ] Pregătire slides (theory.html)
- [ ] Test conexiune MQTT broker
- [ ] Pregătire fișiere pentru upload Moodle

## În Timpul Laboratorului

### Introducere (10 min)
- [ ] Prezentare obiective
- [ ] Recapitulare concepte TCP/IP
- [ ] Avertisment etic: doar medii autorizate

### Demo Curs (30 min)
- [ ] Arhitectura IoT (slide 5-10)
- [ ] Protocol MQTT (slide 11-15)
- [ ] OWASP Top 10 (slide 16-20)

### Practică (70 min)
- [ ] Setup mediu (15 min)
- [ ] Port scanning (20 min)
- [ ] MQTT pub/sub (20 min)
- [ ] Traffic capture (15 min)

### Wrap-up (10 min)
- [ ] Recapitulare concepte
- [ ] Indicații temă
- [ ] Q&A

## După Laborator

- [ ] Verificare upload livrabile studenți
- [ ] Notare participare
- [ ] Actualizare feedback pentru săptămâna viitoare

## Probleme Frecvente

| Problemă | Soluție Rapidă |
|----------|---------------|
| Docker nu pornește | `sudo systemctl start docker` |
| Permission denied tshark | `sudo setcap cap_net_raw+ep $(which tshark)` |
| MQTT connection refused | Verificare container: `docker ps` |
