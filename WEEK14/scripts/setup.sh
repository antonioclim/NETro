#!/bin/bash
# setup.sh — Instalează dependențele pentru Starterkit S14
# Rulare: sudo bash scripts/setup.sh

set -e

echo "=============================================="
echo "  Setup Starterkit Săptămâna 14"
echo "=============================================="

# Verifică dacă rulează ca root
if [ "$EUID" -ne 0 ]; then
    echo "[!] Acest script trebuie rulat cu sudo"
    exit 1
fi

# Detectează distribuția
if [ -f /etc/os-release ]; then
    . /etc/os-release
    DISTRO=$ID
else
    DISTRO="unknown"
fi

echo "[*] Distribuție detectată: $DISTRO"

# Actualizează lista de pachete
echo "[*] Actualizare listă pachete..."
apt-get update -qq

# Instalează pachete de bază
echo "[*] Instalare pachete de bază..."
DEBIAN_FRONTEND=noninteractive apt-get install -y -qq \
    python3 \
    python3-pip \
    python3-venv \
    git \
    curl \
    wget \
    net-tools \
    iproute2 \
    iputils-ping \
    netcat-openbsd \
    tcpdump \
    > /dev/null

# Instalează tshark (Wireshark CLI)
echo "[*] Instalare tshark..."
DEBIAN_FRONTEND=noninteractive apt-get install -y -qq \
    tshark \
    > /dev/null 2>&1 || echo "[!] tshark installation may have issues (non-critical)"

# Instalează Mininet
echo "[*] Instalare Mininet..."
if ! command -v mn &> /dev/null; then
    DEBIAN_FRONTEND=noninteractive apt-get install -y -qq \
        mininet \
        openvswitch-switch \
        > /dev/null
    
    # Pornește OVS
    systemctl enable openvswitch-switch 2>/dev/null || true
    systemctl start openvswitch-switch 2>/dev/null || true
else
    echo "    Mininet deja instalat."
fi

# Instalează apache2-utils (pentru ab - Apache Benchmark)
echo "[*] Instalare apache2-utils (optional)..."
DEBIAN_FRONTEND=noninteractive apt-get install -y -qq \
    apache2-utils \
    > /dev/null 2>&1 || echo "    apache2-utils skipped (non-critical)"

# Verifică instalările
echo ""
echo "[*] Verificare instalări..."

check_cmd() {
    if command -v "$1" &> /dev/null; then
        echo "    ✓ $1"
    else
        echo "    ✗ $1 (lipsește)"
    fi
}

check_cmd python3
check_cmd pip3
check_cmd mn
check_cmd ovs-vsctl
check_cmd tcpdump
check_cmd tshark
check_cmd curl
check_cmd nc

# Verifică OVS
echo ""
echo "[*] Verificare Open vSwitch..."
if systemctl is-active --quiet openvswitch-switch; then
    echo "    ✓ openvswitch-switch activ"
else
    echo "    ! openvswitch-switch inactiv, încerc să pornesc..."
    systemctl start openvswitch-switch 2>/dev/null || true
fi

echo ""
echo "=============================================="
echo "  Setup completat!"
echo "=============================================="
echo ""
echo "Pași următori:"
echo "  1. bash tests/smoke_test.sh   # verificare mediu"
echo "  2. make run-demo              # rulează demo-ul"
echo ""
