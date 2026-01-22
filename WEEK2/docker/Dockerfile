# ============================================================
# Dockerfile - Starterkit Săptămâna 2: Programare pe Socket-uri
# Rețele de calculatoare - ASE București, CSIE
# ============================================================
# Imagine lightweight pentru rularea scenariilor TCP/UDP
# Revolvix&Hypotheticalandrei
# ============================================================

FROM python:3.11-slim-bullseye

LABEL maintainer="ASE CSIE - Rețele de calculatoare"
LABEL description="Mediu pentru laboratorul de socket-uri TCP/UDP"
LABEL week="2"

# Variabile de mediu
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8

# Instalare dependențe sistem
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Unelte rețea
    netcat-openbsd \
    net-tools \
    iproute2 \
    iputils-ping \
    tcpdump \
    tshark \
    curl \
    # Utilitare
    procps \
    less \
    vim-tiny \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Creare utilizator non-root pentru securitate
RUN useradd -m -s /bin/bash student \
    && mkdir -p /app /app/pcap /app/logs \
    && chown -R student:student /app

WORKDIR /app

# Copiere requirements și instalare pachete Python
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copiere cod sursă
COPY --chown=student:student seminar/python/ /app/python/
COPY --chown=student:student scripts/ /app/scripts/

# Permisiuni pentru scripturi
RUN chmod +x /app/scripts/*.sh 2>/dev/null || true

# Schimbare la utilizatorul non-root
USER student

# Port-uri expuse pentru TCP/UDP
EXPOSE 8080/tcp 8081/tcp 9000/udp 9001/udp

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python -c "import socket; s=socket.socket(); s.close(); print('OK')" || exit 1

# Entrypoint implicit - shell interactiv
CMD ["/bin/bash"]
