#!/usr/bin/env bash
#===============================================================================
# setup.sh - Instalare dependențe pentru Starterkit S1
#===============================================================================
# Rețele de Calculatoare - Săptămâna 1
# ASE București
#
# Utilizare:
#   sudo bash scripts/setup.sh
#   sudo bash scripts/setup.sh --minimal    # Doar esențiale
#   sudo bash scripts/setup.sh --docker     # Pregătește pentru Docker
#===============================================================================

set -e  # Oprire la prima eroare

# Culori pentru output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funcții helper
info()    { echo -e "${BLUE}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[✓]${NC} $1"; }
warn()    { echo -e "${YELLOW}[!]${NC} $1"; }
error()   { echo -e "${RED}[✗]${NC} $1"; }

header() {
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
}

#===============================================================================
# Verificări preliminare
#===============================================================================

check_root() {
    if [[ $EUID -ne 0 ]]; then
        error "Acest script trebuie rulat cu sudo!"
        echo "  Utilizare: sudo bash $0"
        exit 1
    fi
}

check_os() {
    if [[ -f /etc/os-release ]]; then
        . /etc/os-release
        OS=$ID
        VERSION=$VERSION_ID
        info "Sistem detectat: $PRETTY_NAME"
    else
        warn "Nu s-a putut detecta sistemul de operare"
        OS="unknown"
    fi
    
    case $OS in
        ubuntu|debian)
            PKG_MANAGER="apt"
            ;;
        fedora|centos|rhel)
            PKG_MANAGER="dnf"
            warn "Suport limitat pentru $OS - verificați manual pachetele"
            ;;
        *)
            error "Sistem de operare nesuportat: $OS"
            echo "  Sisteme suportate: Ubuntu 22.04+, Debian 12+"
            exit 1
            ;;
    esac
}

#===============================================================================
# Instalare pachete
#===============================================================================

install_essential() {
    header "Instalare pachete esențiale"
    
    info "Actualizare liste pachete..."
    apt-get update -qq
    
    ESSENTIAL_PKGS=(
        python3
        python3-pip
        python3-venv
        iproute2
        iputils-ping
        netcat-openbsd
        tcpdump
        tshark
        curl
        wget
        git
    )
    
    info "Instalare pachete esențiale..."
    for pkg in "${ESSENTIAL_PKGS[@]}"; do
        if dpkg -s "$pkg" &>/dev/null; then
            success "$pkg (deja instalat)"
        else
            echo -n "  Instalare $pkg... "
            if apt-get install -y -qq "$pkg" &>/dev/null; then
                echo -e "${GREEN}OK${NC}"
            else
                echo -e "${RED}FAIL${NC}"
            fi
        fi
    done
}

install_mininet() {
    header "Instalare Mininet"
    
    if command -v mn &>/dev/null; then
        success "Mininet deja instalat: $(mn --version 2>&1 | head -1)"
        return 0
    fi
    
    MININET_PKGS=(
        mininet
        openvswitch-switch
        openvswitch-common
    )
    
    info "Instalare Mininet și Open vSwitch..."
    for pkg in "${MININET_PKGS[@]}"; do
        echo -n "  Instalare $pkg... "
        if apt-get install -y -qq "$pkg" &>/dev/null; then
            echo -e "${GREEN}OK${NC}"
        else
            echo -e "${YELLOW}SKIP${NC} (poate nu e disponibil)"
        fi
    done
    
    # Pornim serviciul OVS
    info "Pornire serviciu Open vSwitch..."
    systemctl enable openvswitch-switch &>/dev/null || true
    systemctl start openvswitch-switch &>/dev/null || true
    
    if command -v mn &>/dev/null; then
        success "Mininet instalat cu succes"
    else
        warn "Mininet nu s-a instalat - verificați manual"
    fi
}

install_python_packages() {
    header "Instalare pachete Python"
    
    # Verificăm versiunea Python
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    info "Python versiune: $PYTHON_VERSION"
    
    # Pachete Python necesare
    PYTHON_PKGS=(
        scapy
    )
    
    info "Instalare pachete Python cu pip..."
    for pkg in "${PYTHON_PKGS[@]}"; do
        echo -n "  Instalare $pkg... "
        if pip3 install --quiet --break-system-packages "$pkg" 2>/dev/null; then
            echo -e "${GREEN}OK${NC}"
        elif pip3 install --quiet "$pkg" 2>/dev/null; then
            echo -e "${GREEN}OK${NC}"
        else
            echo -e "${YELLOW}SKIP${NC}"
        fi
    done
}

configure_permissions() {
    header "Configurare permisiuni"
    
    # Adăugăm utilizatorul curent la grupul wireshark
    SUDO_USER=${SUDO_USER:-$USER}
    
    if getent group wireshark &>/dev/null; then
        info "Adăugare $SUDO_USER la grupul wireshark..."
        usermod -aG wireshark "$SUDO_USER" 2>/dev/null || true
        success "Utilizator adăugat la grupul wireshark"
        warn "NOTĂ: Delogare/relogare necesară pentru activare!"
    fi
    
    # Permisiuni pentru tshark fără root (opțional)
    if [[ -f /usr/bin/dumpcap ]]; then
        info "Configurare capabilități pentru dumpcap..."
        setcap cap_net_raw,cap_net_admin=eip /usr/bin/dumpcap 2>/dev/null || true
    fi
}

install_docker() {
    header "Instalare Docker (opțional)"
    
    if command -v docker &>/dev/null; then
        success "Docker deja instalat: $(docker --version)"
        return 0
    fi
    
    info "Instalare Docker..."
    
    # Dependențe
    apt-get install -y -qq \
        ca-certificates \
        curl \
        gnupg \
        lsb-release &>/dev/null
    
    # Cheie GPG Docker
    mkdir -p /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/$OS/gpg | \
        gpg --dearmor -o /etc/apt/keyrings/docker.gpg 2>/dev/null
    
    # Repository Docker
    echo \
        "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
        https://download.docker.com/linux/$OS $(lsb_release -cs) stable" | \
        tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # Instalare
    apt-get update -qq
    apt-get install -y -qq docker-ce docker-ce-cli containerd.io docker-compose-plugin &>/dev/null
    
    # Adăugăm utilizatorul la grupul docker
    SUDO_USER=${SUDO_USER:-$USER}
    usermod -aG docker "$SUDO_USER" 2>/dev/null || true
    
    if command -v docker &>/dev/null; then
        success "Docker instalat cu succes"
        warn "NOTĂ: Delogare/relogare necesară pentru a folosi docker fără sudo!"
    else
        warn "Docker nu s-a instalat - verificați manual"
    fi
}

#===============================================================================
# Main
#===============================================================================

main() {
    header "Setup Starterkit S1 - Rețele de Calculatoare"
    
    check_root
    check_os
    
    case "${1:-full}" in
        --minimal)
            info "Mod minimal - doar pachete esențiale"
            install_essential
            ;;
        --docker)
            info "Mod Docker - pregătire pentru containere"
            install_essential
            install_docker
            ;;
        *)
            info "Instalare completă"
            install_essential
            install_mininet
            install_python_packages
            configure_permissions
            ;;
    esac
    
    header "Instalare completă!"
    
    echo "Pași următori:"
    echo "  1. Delogați-vă și relogați-vă (pentru permisiuni grup)"
    echo "  2. Rulați 'make verify' pentru a verifica instalarea"
    echo "  3. Consultați README.md pentru utilizare"
    echo ""
    success "Setup finalizat!"
}

main "$@"
