#!/bin/bash
# ============================================================================
# setup.sh - Pregătirea mediului pentru Săptămâna 6 (NAT/PAT & SDN)
# Autor: Revolvix&Hypotheticalandrei
# ============================================================================

set -e  # Exit on error

# Culori pentru output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funcții utilitare
info() { echo -e "${BLUE}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[OK]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

# Banner
echo "=============================================="
echo "  Setup Mediu - Săptămâna 6: NAT/PAT & SDN"
echo "=============================================="
echo ""

# Verificare privilegii root (pentru Mininet)
check_privileges() {
    if [[ $EUID -eq 0 ]]; then
        warn "Rulezi ca root. Unele comenzi vor fi executate fără sudo."
        SUDO=""
    else
        SUDO="sudo"
        info "Se va folosi sudo pentru comenzile privilegiate."
    fi
}

# Verificare sistem de operare
check_os() {
    info "Verificare sistem de operare..."
    if [[ -f /etc/os-release ]]; then
        . /etc/os-release
        OS=$NAME
        VER=$VERSION_ID
        success "Sistem detectat: $OS $VER"
    else
        warn "Nu s-a putut detecta sistemul de operare"
    fi
}

# Verificare și instalare dependențe de bază
install_base_deps() {
    info "Verificare dependențe de bază..."
    
    DEPS_MISSING=()
    
    # Lista de pachete necesare
    PACKAGES=(
        "python3"
        "python3-pip"
        "python3-venv"
        "net-tools"
        "iproute2"
        "iptables"
        "tcpdump"
        "tshark"
        "curl"
        "wget"
        "git"
    )
    
    for pkg in "${PACKAGES[@]}"; do
        if ! dpkg -l | grep -q "^ii  $pkg "; then
            DEPS_MISSING+=("$pkg")
        fi
    done
    
    if [[ ${#DEPS_MISSING[@]} -gt 0 ]]; then
        warn "Pachete lipsă: ${DEPS_MISSING[*]}"
        info "Instalare pachete..."
        $SUDO apt-get update -qq
        $SUDO apt-get install -y "${DEPS_MISSING[@]}"
        success "Pachete instalate"
    else
        success "Toate pachetele de bază sunt instalate"
    fi
}

# Verificare și instalare Mininet
install_mininet() {
    info "Verificare Mininet..."
    
    if command -v mn &> /dev/null; then
        MN_VER=$(mn --version 2>/dev/null || echo "unknown")
        success "Mininet instalat: $MN_VER"
    else
        warn "Mininet nu este instalat"
        info "Instalare Mininet..."
        $SUDO apt-get install -y mininet openvswitch-switch openvswitch-testcontroller
        success "Mininet instalat"
    fi
    
    # Verificare OVS
    if ! systemctl is-active --quiet openvswitch-switch; then
        info "Pornire serviciu Open vSwitch..."
        $SUDO systemctl start openvswitch-switch
        $SUDO systemctl enable openvswitch-switch
    fi
    success "Open vSwitch activ"
}

# Configurare Python și dependențe
setup_python() {
    info "Configurare mediu Python..."
    
    # Verificare Python 3
    PYTHON_VER=$(python3 --version 2>&1 | cut -d' ' -f2)
    success "Python versiune: $PYTHON_VER"
    
    # Instalare pachete Python pentru SDN
    info "Instalare pachete Python pentru rețelistică..."
    
    # OS-Ken (fork Ryu pentru SDN)
    if ! python3 -c "import os_ken" 2>/dev/null; then
        pip3 install os-ken --break-system-packages 2>/dev/null || \
        pip3 install os-ken --user
    fi
    success "os-ken instalat"
    
    # Scapy pentru packet crafting
    if ! python3 -c "import scapy" 2>/dev/null; then
        pip3 install scapy --break-system-packages 2>/dev/null || \
        pip3 install scapy --user
    fi
    success "scapy instalat"
    
    # Mininet Python API
    if ! python3 -c "from mininet.net import Mininet" 2>/dev/null; then
        warn "Mininet Python API poate necesita instalare manuală"
    else
        success "Mininet Python API disponibil"
    fi
}

# Configurare conntrack pentru NAT
setup_conntrack() {
    info "Configurare conntrack pentru monitorizare NAT..."
    
    if ! command -v conntrack &> /dev/null; then
        $SUDO apt-get install -y conntrack
    fi
    success "conntrack disponibil"
    
    # Activare module kernel pentru NAT
    $SUDO modprobe nf_conntrack 2>/dev/null || true
    $SUDO modprobe nf_nat 2>/dev/null || true
}

# Configurare IP forwarding (necesar pentru NAT)
setup_ip_forwarding() {
    info "Verificare IP forwarding..."
    
    FORWARD=$(cat /proc/sys/net/ipv4/ip_forward)
    if [[ "$FORWARD" == "0" ]]; then
        warn "IP forwarding dezactivat (normal pentru host)"
        info "Va fi activat în namespace-urile Mininet"
    else
        success "IP forwarding activ"
    fi
}

# Creare directoare de lucru
setup_directories() {
    info "Creare directoare de lucru..."
    
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
    
    mkdir -p "$PROJECT_DIR/pcap"
    mkdir -p "$PROJECT_DIR/logs"
    mkdir -p "$PROJECT_DIR/output"
    
    success "Directoare create: pcap/, logs/, output/"
}

# Verificare finală
final_check() {
    echo ""
    echo "=============================================="
    echo "  Verificare Finală"
    echo "=============================================="
    
    CHECKS_PASSED=0
    CHECKS_TOTAL=0
    
    check_cmd() {
        ((CHECKS_TOTAL++))
        if command -v "$1" &> /dev/null; then
            success "$1 disponibil"
            ((CHECKS_PASSED++))
        else
            error "$1 LIPSĂ"
        fi
    }
    
    check_python_module() {
        ((CHECKS_TOTAL++))
        if python3 -c "import $1" 2>/dev/null; then
            success "Python: $1 disponibil"
            ((CHECKS_PASSED++))
        else
            warn "Python: $1 LIPSĂ"
        fi
    }
    
    check_cmd "python3"
    check_cmd "mn"
    check_cmd "ovs-vsctl"
    check_cmd "tcpdump"
    check_cmd "tshark"
    check_cmd "iptables"
    check_cmd "conntrack"
    
    check_python_module "os_ken"
    check_python_module "scapy"
    
    echo ""
    echo "=============================================="
    if [[ $CHECKS_PASSED -eq $CHECKS_TOTAL ]]; then
        success "Toate verificările au trecut ($CHECKS_PASSED/$CHECKS_TOTAL)"
        echo -e "${GREEN}Mediul este pregătit pentru laboratorul S6!${NC}"
    else
        warn "$CHECKS_PASSED din $CHECKS_TOTAL verificări au trecut"
        echo -e "${YELLOW}Unele componente pot necesita configurare manuală.${NC}"
    fi
    echo "=============================================="
}

# Funcție principală
main() {
    check_privileges
    check_os
    install_base_deps
    install_mininet
    setup_python
    setup_conntrack
    setup_ip_forwarding
    setup_directories
    final_check
}

# Rulare
main "$@"
