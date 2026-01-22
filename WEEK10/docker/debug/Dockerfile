FROM alpine:3.19

# Instalare unelte de diagnosticare
RUN apk add --no-cache \
    bash \
    curl \
    wget \
    bind-tools \
    openssh-client \
    lftp \
    tcpdump \
    nmap \
    netcat-openbsd \
    iputils \
    iproute2 \
    python3 \
    py3-pip

# Instalare unelte Python
RUN pip3 install --no-cache-dir --break-system-packages \
    requests \
    paramiko \
    dnspython

# Script de bun venit
RUN echo '#!/bin/sh' > /etc/profile.d/welcome.sh && \
    echo 'echo ""' >> /etc/profile.d/welcome.sh && \
    echo 'echo "╔═══════════════════════════════════════════════════════════════╗"' >> /etc/profile.d/welcome.sh && \
    echo 'echo "║        DEBUG CONTAINER - Săptămâna 10                         ║"' >> /etc/profile.d/welcome.sh && \
    echo 'echo "╠═══════════════════════════════════════════════════════════════╣"' >> /etc/profile.d/welcome.sh && \
    echo 'echo "║  Comenzi utile:                                               ║"' >> /etc/profile.d/welcome.sh && \
    echo 'echo "║    dig web                     - DNS implicit Docker          ║"' >> /etc/profile.d/welcome.sh && \
    echo 'echo "║    dig @dns-server -p 5353 myservice.lab.local                ║"' >> /etc/profile.d/welcome.sh && \
    echo 'echo "║    curl http://web:8000        - Test HTTP                    ║"' >> /etc/profile.d/welcome.sh && \
    echo 'echo "║    ssh labuser@ssh-server      - SSH (parola: labpass)        ║"' >> /etc/profile.d/welcome.sh && \
    echo 'echo "║    lftp -u labftp,labftp ftp-server:2121                      ║"' >> /etc/profile.d/welcome.sh && \
    echo 'echo "║    tcpdump -i any port 80      - Captură trafic               ║"' >> /etc/profile.d/welcome.sh && \
    echo 'echo "╚═══════════════════════════════════════════════════════════════╝"' >> /etc/profile.d/welcome.sh && \
    echo 'echo ""' >> /etc/profile.d/welcome.sh && \
    chmod +x /etc/profile.d/welcome.sh

WORKDIR /root

CMD ["/bin/sh", "-l"]
