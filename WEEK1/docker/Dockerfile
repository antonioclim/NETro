#===============================================================================
# Dockerfile - Mediu containerizat pentru Starterkit S1
#===============================================================================
# Rețele de Calculatoare - Săptămâna 1
# ASE București
#
# Build:   docker build -t s1-retele .
# Run:     docker run -it --rm --cap-add=NET_ADMIN --cap-add=NET_RAW s1-retele
#===============================================================================

FROM ubuntu:22.04

LABEL maintainer="Revolvix&Hypotheticalandrei"
LABEL description="Mediu de laborator pentru Rețele de Calculatoare - S1"
LABEL version="1.0"

# Evităm prompturi interactive
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Europe/Bucharest

# Actualizare și instalare pachete de bază
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Python
    python3 \
    python3-pip \
    python3-venv \
    # Instrumente rețea
    iproute2 \
    iputils-ping \
    netcat-openbsd \
    tcpdump \
    tshark \
    traceroute \
    dnsutils \
    net-tools \
    iptables \
    # Utilități
    curl \
    wget \
    vim \
    nano \
    less \
    tree \
    git \
    make \
    ca-certificates \
    # Cleanup
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Instalare pachete Python
RUN pip3 install --no-cache-dir --break-system-packages \
    scapy

# Configurare tshark pentru utilizare non-root
RUN groupadd -r wireshark || true && \
    chgrp wireshark /usr/bin/dumpcap && \
    chmod 750 /usr/bin/dumpcap && \
    setcap cap_net_raw,cap_net_admin=eip /usr/bin/dumpcap

# Creare utilizator non-root
RUN useradd -m -s /bin/bash -G wireshark student

# Copiere fișiere starterkit
WORKDIR /home/student/starterkit
COPY --chown=student:student . .

# Setare permisiuni
RUN chmod +x scripts/*.sh && \
    chmod +x python/exercises/*.py 2>/dev/null || true

# Comutare la utilizatorul student
USER student

# Director de lucru
WORKDIR /home/student/starterkit

# Verificare la pornire
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python3 --version && tshark --version | head -1 || exit 1

# Comandă implicită
CMD ["/bin/bash"]
