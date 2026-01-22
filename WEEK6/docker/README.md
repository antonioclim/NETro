# Docker pentru Săptămâna 6 - NAT/PAT & SDN

## ⚠️ Notă Importantă

**Docker NU este metoda recomandată pentru acest laborator.**

Mininet necesită acces privilegiat la kernel-ul Linux și namespace-uri de rețea, ceea ce face containerizarea problematică. Recomandăm utilizarea unei mașini virtuale (VirtualBox + Ubuntu 22.04/24.04).

## Când să folosești Docker?

- Ai deja experiență cu Docker și containere privilegiate
- Nu ai posibilitatea să rulezi VirtualBox
- Vrei să testezi rapid codul Python (fără topologii Mininet complexe)
- Ai Linux nativ ca sistem de operare host

## Limitări cunoscute

1. **Mininet în containere**: Poate avea comportament imprevizibil
2. **macOS/Windows**: Funcționalitate foarte limitată (Docker Desktop nu suportă complet namespace-uri de rețea)
3. **Network mode**: Necesită `--privileged` și de obicei `--net=host`

## Utilizare

### Build

```bash
cd docker/
docker build -t lab-s6-networking ..
```

### Run (modul interactiv)

```bash
docker run -it --privileged --net=host --name lab-s6 lab-s6-networking
```

### Cu docker-compose

```bash
# Build
docker-compose build

# Run interactiv
docker-compose run --rm lab-s6

# Oprire
docker-compose down -v
```

## Alternativa recomandată: VirtualBox

1. Descarcă [VirtualBox](https://www.virtualbox.org/)
2. Descarcă [Ubuntu 22.04 LTS](https://ubuntu.com/download/desktop) sau [Ubuntu Server](https://ubuntu.com/download/server)
3. Creează VM cu:
   - 2-4 GB RAM
   - 20 GB disk
   - Network: NAT sau Bridged
4. În VM, rulează: `make setup`

---

*Revolvix&Hypotheticalandrei*
