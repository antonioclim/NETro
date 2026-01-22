# ═══════════════════════════════════════════════════════════════════════════
# Dockerfile — Container pentru Starterkit S3 (Socket Programming)
# ═══════════════════════════════════════════════════════════════════════════
#
# BUILD:
#   docker build -t s3-starterkit .
#
# RUN (interactiv):
#   docker run -it --rm --privileged s3-starterkit
#
# RUN (ca server):
#   docker run -d --name s3-server -p 3333:3333 s3-starterkit \
#       python3 python/examples/ex05_tcp_multiclient.py
#
# NOTĂ:
#   --privileged e necesar pentru Mininet (creează namespace-uri de rețea)
#
# ═══════════════════════════════════════════════════════════════════════════

FROM ubuntu:22.04

LABEL maintainer="ASE-CSIE Retele de Calculatoare"
LABEL description="Starterkit S3: Socket Programming (UDP broadcast/multicast, TCP tunnel)"
LABEL version="1.0"

# ─── Variabile de mediu ───────────────────────────────────────────────────

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV TZ=Europe/Bucharest

# ─── Instalare pachete ────────────────────────────────────────────────────

RUN apt-get update && apt-get install -y --no-install-recommends \
    # Python
    python3 \
    python3-pip \
    # Mininet și Open vSwitch
    mininet \
    openvswitch-switch \
    openvswitch-common \
    # Unelte de rețea
    iproute2 \
    iputils-ping \
    tcpdump \
    tshark \
    netcat-openbsd \
    iperf3 \
    traceroute \
    dnsutils \
    net-tools \
    # Utilități
    vim \
    less \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# ─── Instalare pachete Python ─────────────────────────────────────────────

RUN pip3 install --no-cache-dir --break-system-packages \
    scapy \
    && rm -rf /root/.cache

# ─── Configurare Wireshark/tshark (non-root) ──────────────────────────────

RUN echo "wireshark-common wireshark-common/install-setuid boolean true" | \
    debconf-set-selections

# ─── Copiere fișiere starterkit ───────────────────────────────────────────

WORKDIR /app
COPY . /app/

# ─── Permisiuni scripturi ─────────────────────────────────────────────────

RUN chmod +x scripts/*.sh 2>/dev/null || true

# ─── Expunere porturi comune S3 ───────────────────────────────────────────

EXPOSE 3333/tcp
EXPOSE 5007/udp
EXPOSE 5001/udp
EXPOSE 8080/tcp
EXPOSE 9090/tcp

# ─── Script de pornire ────────────────────────────────────────────────────

COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh 2>/dev/null || true

# ─── Entry point ──────────────────────────────────────────────────────────

ENTRYPOINT ["/bin/bash"]
CMD ["-c", "echo 'Starterkit S3 ready. Use: python3 python/examples/ex0X_*.py'; exec bash"]
