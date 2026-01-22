# Demo Docker — Săptămâna 7

Acest demo oferă o variantă alternativă (fără Mininet) pentru a rula aplicațiile TCP și UDP din săptămâna 7 în containere Docker. Este util când Mininet nu este disponibil, dar vrei să poți reproduce rapid:

- un server TCP (echo)
- un server UDP (echo)
- clienți simpli care generează trafic

## Pornire rapidă

Din folderul `WEEK7/docker`:

```bash
docker-compose up --build
```

În alt terminal, poți urmări logurile:

```bash
docker-compose logs -f
```

Oprire și cleanup:

```bash
docker-compose down -v
```

## Observații

- Demo-ul rulează pe rețeaua virtuală Docker, local.
- Dacă vrei captură de trafic, poți rula `tcpdump` pe interfața `docker0` (sau pe interfața bridge specifică) pe host-ul Linux.
