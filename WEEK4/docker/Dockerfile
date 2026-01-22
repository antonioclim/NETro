# =============================================================================
# Dockerfile pentru Starterkit Săptămâna 4
# Protocoale TEXT, BINARY și UDP peste TCP/UDP
# =============================================================================
# 
# Utilizare:
#   docker build -t s4-networking .
#   docker run -it --rm s4-networking
#
# Sau cu docker-compose:
#   docker-compose up -d
#   docker-compose exec server bash
#
# Autor: Revolvix&Hypotheticalandrei
# =============================================================================

FROM python:3.11-slim-bookworm

LABEL maintainer="Revolvix&Hypotheticalandrei"
LABEL description="Starterkit Săptămâna 4 - Protocoale de rețea"
LABEL version="1.0"

# Evităm interacțiuni în timpul instalării
ENV DEBIAN_FRONTEND=noninteractive

# Variabile de mediu pentru Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/python

# Instalare unelte de rețea și debugging
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Unelte de rețea esențiale
    iputils-ping \
    iproute2 \
    net-tools \
    netcat-openbsd \
    tcpdump \
    tshark \
    # Editor pentru debugging
    nano \
    vim-tiny \
    # Utilitare
    curl \
    wget \
    procps \
    # Cleanup
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Creare utilizator non-root pentru securitate
RUN groupadd -r netuser && useradd -r -g netuser netuser

# Creare structură directoare
WORKDIR /app

# Copiere fișiere aplicație
COPY python/ /app/python/
COPY scripts/ /app/scripts/
COPY docs/ /app/docs/

# Permisiuni pentru scripturi
RUN chmod +x /app/scripts/*.sh 2>/dev/null || true

# Creare directoare pentru capturi și loguri
RUN mkdir -p /app/pcap /app/logs \
    && chown -R netuser:netuser /app

# Port-uri expuse
# 3333 - Protocol TEXT TCP
# 4444 - Protocol BINARY TCP
# 5555 - Protocol UDP Sensor
EXPOSE 3333 4444 5555/tcp 5555/udp

# Healthcheck pentru server
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD nc -z localhost 3333 || nc -z localhost 4444 || exit 1

# Schimbăm la utilizator non-root
# Comentat pentru a permite tcpdump/tshark care necesită root
# USER netuser

# Director de lucru
WORKDIR /app

# Comandă implicită - shell interactiv
CMD ["/bin/bash"]

# =============================================================================
# Exemple de utilizare:
#
# 1. Pornire server TEXT:
#    docker run -it --rm -p 3333:3333 s4-networking \
#      python3 python/apps/text_proto_server.py --port 3333
#
# 2. Pornire server BINARY:
#    docker run -it --rm -p 4444:4444 s4-networking \
#      python3 python/apps/binary_proto_server.py --port 4444
#
# 3. Pornire server UDP:
#    docker run -it --rm -p 5555:5555/udp s4-networking \
#      python3 python/apps/udp_sensor_server.py --port 5555
#
# 4. Client TEXT:
#    docker run -it --rm --network host s4-networking \
#      python3 python/apps/text_proto_client.py --host localhost --port 3333 --message "Test"
#
# 5. Captură trafic:
#    docker run -it --rm --cap-add=NET_ADMIN --network host s4-networking \
#      tshark -i any -f "tcp port 3333"
#
# =============================================================================
