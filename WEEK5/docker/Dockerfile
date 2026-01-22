# Dockerfile — Starterkit Săptămâna 5
# =====================================
# Container minimal pentru exercițiile Python (fără Mininet)
#
# Build:   docker build -t starterkit-s5 docker/
# Run:     docker run -it --rm starterkit-s5
# Volume:  docker run -it --rm -v $(pwd):/app starterkit-s5
#
# NOTĂ: Mininet necesită acces la kernel și nu funcționează în container standard.
#       Pentru Mininet, folosiți VM sau containerdlab.

FROM python:3.11-slim

LABEL maintainer="ASE-CSIE"
LABEL description="Starterkit Săptămâna 5 - Adresare IP"
LABEL version="1.0"

# Setări mediu
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV TERM=xterm-256color

# Instalare unelte de bază
RUN apt-get update && apt-get install -y --no-install-recommends \
    iputils-ping \
    iproute2 \
    net-tools \
    tcpdump \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Directorul de lucru
WORKDIR /app

# Copiere cod
COPY python/ ./python/
COPY docs/ ./docs/
COPY README.md ./

# Permisiuni executabile
RUN chmod +x python/exercises/*.py 2>/dev/null || true
RUN chmod +x python/apps/*.py 2>/dev/null || true

# Verificare la build
RUN python3 -c "import ipaddress; print('Python OK')"

# Punct de intrare implicit
ENTRYPOINT ["/bin/bash"]

# Comandă implicită
CMD ["-c", "echo 'Starterkit S5 - Utilizare: python python/exercises/ex_5_01_cidr_flsm.py --help'"]
