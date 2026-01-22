# =============================================================================
# Dockerfile pentru Săptămâna 12 - Protocoale Email și RPC
# =============================================================================
# Imagine minimalistă pentru rularea demo-urilor și exercițiilor
# 
# Build:   docker build -t s12-email-rpc .
# Run:     docker run -it --rm -p 1025:1025 -p 8000:8000 -p 8001:8001 s12-email-rpc
# =============================================================================

FROM python:3.11-slim-bookworm

LABEL maintainer="Revolvix&Hypotheticalandrei"
LABEL description="Week 12 - Email Protocols (SMTP/POP3/IMAP) and RPC (JSON-RPC/XML-RPC)"
LABEL version="1.0"

# Evităm interactive prompts
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instalare pachete sistem necesare
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Utilități rețea
    tshark \
    tcpdump \
    netcat-openbsd \
    curl \
    wget \
    dnsutils \
    iproute2 \
    iputils-ping \
    net-tools \
    # Editor și utilități
    vim-tiny \
    less \
    tree \
    # Compilare (pentru unele pachete Python)
    gcc \
    python3-dev \
    # Cleanup
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Creare utilizator non-root pentru securitate
RUN useradd -m -s /bin/bash student \
    && usermod -aG wireshark student 2>/dev/null || true

# Setare director de lucru
WORKDIR /app

# Copiere requirements și instalare dependențe Python
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copiere cod sursă
COPY src/ ./src/
COPY scripts/ ./scripts/
COPY exercises/ ./exercises/
COPY Makefile .
COPY README.md .

# Permisiuni pentru scripturi
RUN chmod +x scripts/*.sh 2>/dev/null || true

# Creare directoare pentru output
RUN mkdir -p /app/pcap /app/mailbox /app/logs \
    && chown -R student:student /app

# Expunere porturi
# 1025 - SMTP server educațional
# 8000 - JSON-RPC server
# 8001 - XML-RPC server
# 50051 - gRPC server (opțional)
EXPOSE 1025 8000 8001 50051

# Schimbare la utilizator non-root
USER student

# Verificare mediu la pornire
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import socket; s=socket.socket(); s.settimeout(1); s.connect(('localhost',1025)); s.close()" || exit 1

# Comandă default - shell interactiv
CMD ["/bin/bash"]

# =============================================================================
# Utilizare:
#
# 1. Build imagine:
#    docker build -t s12-email-rpc .
#
# 2. Rulare interactivă:
#    docker run -it --rm --name s12 \
#      -p 1025:1025 -p 8000:8000 -p 8001:8001 \
#      s12-email-rpc
#
# 3. Rulare server SMTP în background:
#    docker run -d --name smtp-server \
#      -p 1025:1025 \
#      s12-email-rpc python src/email/smtp_server.py
#
# 4. Rulare server JSON-RPC:
#    docker run -d --name jsonrpc-server \
#      -p 8000:8000 \
#      s12-email-rpc python src/rpc/jsonrpc/jsonrpc_server.py
#
# 5. Accesare shell în container rulat:
#    docker exec -it s12 /bin/bash
#
# 6. Captură trafic:
#    docker exec s12 tshark -i any -w /app/pcap/capture.pcap
# =============================================================================
