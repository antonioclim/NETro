#!/bin/bash
# =============================================================================
# setup.sh – Instalare mediu pentru Săptămâna 11
# =============================================================================
# Utilizare: ./setup.sh [--full]
# =============================================================================

set -e

GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m'

FULL_INSTALL=false
if [[ "$1" == "--full" ]]; then
    FULL_INSTALL=true
fi

echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  Setup Săptămâna 11 – Rețele de Calculatoare${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo ""

# Check if running as root for some operations
SUDO=""
if [[ $EUID -ne 0 ]]; then
    SUDO="sudo"
fi

# =============================================================================
# 1. Python Dependencies
# =============================================================================
echo -e "${YELLOW}[1/5]${NC} Instalare dependențe Python..."

if command -v pip3 &> /dev/null; then
    pip3 install --break-system-packages --quiet dnspython paramiko pyftpdlib 2>/dev/null || \
    pip3 install dnspython paramiko pyftpdlib 2>/dev/null || \
    echo -e "${YELLOW}[!]${NC} Unele pachete Python nu s-au instalat. Continuăm..."
else
    echo -e "${RED}[!]${NC} pip3 nu este instalat. Instalați-l manual."
fi

# =============================================================================
# 2. System Tools (apt-based)
# =============================================================================
echo -e "${YELLOW}[2/5]${NC} Verificare instrumente sistem..."

MISSING_TOOLS=""
command -v curl &> /dev/null || MISSING_TOOLS="$MISSING_TOOLS curl"
command -v netcat &> /dev/null || command -v nc &> /dev/null || MISSING_TOOLS="$MISSING_TOOLS netcat-openbsd"
command -v tshark &> /dev/null || MISSING_TOOLS="$MISSING_TOOLS tshark"

if [[ -n "$MISSING_TOOLS" ]]; then
    echo -e "${YELLOW}[INFO]${NC} Instalare:$MISSING_TOOLS"
    $SUDO apt-get update -qq
    $SUDO apt-get install -y -qq $MISSING_TOOLS 2>/dev/null || \
        echo -e "${YELLOW}[!]${NC} Unele instrumente nu s-au instalat. Verificați manual."
else
    echo -e "${GREEN}[OK]${NC} Toate instrumentele de bază sunt instalate."
fi

# =============================================================================
# 3. Docker (only if --full)
# =============================================================================
if $FULL_INSTALL; then
    echo -e "${YELLOW}[3/5]${NC} Verificare Docker..."
    
    if ! command -v docker &> /dev/null; then
        echo -e "${YELLOW}[INFO]${NC} Docker nu este instalat. Instalare..."
        curl -fsSL https://get.docker.com | $SUDO sh
        $SUDO usermod -aG docker $USER
        echo -e "${YELLOW}[!]${NC} Docker instalat. Faceți logout/login pentru a aplica permisiunile."
    else
        echo -e "${GREEN}[OK]${NC} Docker este instalat."
    fi
    
    # Docker Compose (v2 comes with Docker)
    if docker compose version &> /dev/null; then
        echo -e "${GREEN}[OK]${NC} Docker Compose v2 este disponibil."
    else
        echo -e "${YELLOW}[!]${NC} Docker Compose v2 nu este disponibil."
    fi
else
    echo -e "${YELLOW}[3/5]${NC} Docker: skip (rulați cu --full pentru instalare)"
fi

# =============================================================================
# 4. Mininet (only if --full)
# =============================================================================
if $FULL_INSTALL; then
    echo -e "${YELLOW}[4/5]${NC} Verificare Mininet..."
    
    if ! command -v mn &> /dev/null; then
        echo -e "${YELLOW}[INFO]${NC} Mininet nu este instalat. Instalare..."
        $SUDO apt-get update -qq
        $SUDO apt-get install -y -qq mininet openvswitch-switch 2>/dev/null || \
            echo -e "${YELLOW}[!]${NC} Mininet nu s-a instalat. Verificați manual."
    else
        echo -e "${GREEN}[OK]${NC} Mininet este instalat."
    fi
else
    echo -e "${YELLOW}[4/5]${NC} Mininet: skip (rulați cu --full pentru instalare)"
fi

# =============================================================================
# 5. Final Check
# =============================================================================
echo -e "${YELLOW}[5/5]${NC} Verificare finală..."

echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  Setup complet!${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "Rulați ${YELLOW}make verify${NC} pentru a verifica instalarea."
echo -e "Rulați ${YELLOW}make help${NC} pentru a vedea comenzile disponibile."
echo ""

# Revolvix&Hypotheticalandrei
