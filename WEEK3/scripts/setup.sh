#!/bin/bash
# ============================================================================
# setup.sh — Instalare dependențe pentru Starter Kit S3
# ============================================================================
set -e

CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'

echo -e "${CYAN}[SETUP] Verificare sistem...${NC}"

# Detectare distribuție
if [ -f /etc/os-release ]; then
    . /etc/os-release
    DISTRO=$ID
else
    DISTRO="unknown"
fi

echo -e "${CYAN}[INFO] Distribuție detectată: $DISTRO${NC}"

# Instalare pachete sistem
echo -e "${CYAN}[SETUP] Instalare pachete sistem...${NC}"
case $DISTRO in
    ubuntu|debian)
        sudo apt-get update -qq
        sudo apt-get install -y -qq python3 python3-pip python3-venv \
            mininet openvswitch-switch \
            tcpdump tshark net-tools netcat-openbsd
        ;;
    *)
        echo -e "${YELLOW}[WARN] Instalați manual: python3, mininet, tcpdump${NC}"
        ;;
esac

echo -e "${GREEN}[OK] Setup complet!${NC}"
