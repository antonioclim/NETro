# ============================================================================
# Dockerfile - Mediu containerizat pentru Săptămâna 6 (NAT/PAT & SDN)
# Autor: Revolvix&Hypotheticalandrei
# 
# NOTĂ: Docker NU este metoda primară pentru acest laborator deoarece
# Mininet necesită acces privilegiat la kernel și namespace-uri de rețea.
# Acest Dockerfile este oferit pentru scenarii specifice unde VM nu e disponibil.
# 
# Utilizare recomandată: VirtualBox cu Ubuntu 22.04/24.04 LTS
# ============================================================================

FROM ubuntu:22.04

LABEL maintainer="Revolvix&Hypotheticalandrei"
LABEL description="Mediu pentru Laboratorul S6 - NAT/PAT & SDN"
LABEL version="1.0"

# Evitare interacțiuni în timpul instalării
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Europe/Bucharest

# Instalare pachete de bază
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    net-tools \
    iproute2 \
    iptables \
    tcpdump \
    tshark \
    curl \
    wget \
    git \
    vim \
    nano \
    conntrack \
    iputils-ping \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Instalare Mininet și Open vSwitch
RUN apt-get update && apt-get install -y \
    mininet \
    openvswitch-switch \
    openvswitch-common \
    && rm -rf /var/lib/apt/lists/*

# Instalare pachete Python
RUN pip3 install --no-cache-dir --break-system-packages \
    os-ken \
    scapy \
    requests

# Creare utilizator non-root (pentru development)
RUN useradd -m -s /bin/bash student && \
    usermod -aG sudo student

# Creare directoare de lucru
RUN mkdir -p /home/student/lab_s6 && \
    chown -R student:student /home/student/lab_s6

# Copiere fișiere proiect
WORKDIR /home/student/lab_s6
COPY --chown=student:student . .

# Permisiuni execuție pentru scripturi
RUN chmod +x scripts/*.sh 2>/dev/null || true

# Configurare OVS (va fi pornit la runtime)
RUN mkdir -p /var/run/openvswitch

# Script de pornire
COPY --chown=root:root <<'EOF' /usr/local/bin/start-lab.sh
#!/bin/bash
# Pornire servicii necesare
service openvswitch-switch start 2>/dev/null || ovs-ctl start
sleep 2
echo "Mediu lab S6 pregătit."
echo "Comenzi utile:"
echo "  make check    - Verificare dependențe"
echo "  make nat-demo - Pornire demo NAT"
echo "  make sdn-demo - Pornire demo SDN"
exec "$@"
EOF

RUN chmod +x /usr/local/bin/start-lab.sh

# Port-uri expuse (pentru controller SDN)
EXPOSE 6633 6653

# Volum pentru persistență capturi
VOLUME ["/home/student/lab_s6/pcap", "/home/student/lab_s6/logs"]

# Punct de intrare
ENTRYPOINT ["/usr/local/bin/start-lab.sh"]
CMD ["/bin/bash"]

# ============================================================================
# INSTRUCȚIUNI DE UTILIZARE:
# 
# Build:
#   docker build -t lab-s6-networking .
#
# Run (IMPORTANT: necesită --privileged pentru Mininet):
#   docker run -it --privileged --name lab-s6 lab-s6-networking
#
# Run cu acces la rețeaua host:
#   docker run -it --privileged --net=host --name lab-s6 lab-s6-networking
#
# Reconectare la container existent:
#   docker exec -it lab-s6 /bin/bash
#
# LIMITĂRI CUNOSCUTE:
# - Mininet poate avea comportament imprevizibil în containere
# - Unele funcționalități de rețea necesită --net=host
# - Preferabil: utilizare VM cu VirtualBox
# ============================================================================
