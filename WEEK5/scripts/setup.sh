#!/usr/bin/env bash
#===============================================================================
# setup.sh — Configurarea mediului pentru Săptămâna 5
#===============================================================================
# Utilizare: ./scripts/setup.sh [--full|--minimal|--check]
#
# Opțiuni:
#   --full     Instalează toate dependențele (necesită sudo)
#   --minimal  Doar verifică și configurează (fără instalări)
#   --check    Doar verifică starea mediului
#===============================================================================

set -euo pipefail

# Culori pentru output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Directorul scriptului
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

#-------------------------------------------------------------------------------
# Funcții utilitare
#-------------------------------------------------------------------------------

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[OK]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERR]${NC} $1"
}

check_command() {
    if command -v "$1" &> /dev/null; then
        log_success "$1 disponibil"
        return 0
    else
        log_error "$1 lipsește"
        return 1
    fi
}

#-------------------------------------------------------------------------------
# Verificări
#-------------------------------------------------------------------------------

check_environment() {
    log_info "Verificare mediu de lucru..."
    echo ""
    
    local errors=0
    
    # Python
    if check_command python3; then
        local py_version=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
        if [[ $(echo "$py_version >= 3.10" | bc -l 2>/dev/null || echo 0) -eq 1 ]] || \
           [[ "$py_version" > "3.9" ]]; then
            log_success "Python $py_version (>= 3.10)"
        else
            log_warning "Python $py_version (recomandat >= 3.10)"
        fi
    else
        ((errors++))
    fi
    
    # Mininet
    if check_command mn; then
        log_success "Mininet instalat"
    else
        log_warning "Mininet nu este instalat (necesită VM sau container)"
        ((errors++))
    fi
    
    # Open vSwitch
    if systemctl is-active --quiet openvswitch-switch 2>/dev/null; then
        log_success "Open vSwitch activ"
    elif pgrep -x ovs-vswitchd > /dev/null 2>&1; then
        log_success "Open vSwitch rulează"
    else
        log_warning "Open vSwitch nu este activ"
    fi
    
    # tcpdump
    check_command tcpdump || ((errors++))
    
    # ip command
    check_command ip || ((errors++))
    
    # Python module ipaddress
    if python3 -c "import ipaddress" 2>/dev/null; then
        log_success "Modulul Python ipaddress disponibil"
    else
        log_error "Modulul ipaddress lipsește"
        ((errors++))
    fi
    
    # Verificare permisiuni sudo
    if sudo -n true 2>/dev/null; then
        log_success "Permisiuni sudo disponibile"
    else
        log_warning "Sudo necesită parolă (normal pentru majoritatea sistemelor)"
    fi
    
    echo ""
    if [[ $errors -eq 0 ]]; then
        log_success "Toate verificările au trecut!"
        return 0
    else
        log_error "$errors verificări eșuate"
        return 1
    fi
}

#-------------------------------------------------------------------------------
# Instalare completă
#-------------------------------------------------------------------------------

install_full() {
    log_info "Instalare completă a dependențelor..."
    echo ""
    
    # Verificăm că avem sudo
    if ! sudo -v; then
        log_error "Necesită permisiuni sudo pentru instalare completă"
        exit 1
    fi
    
    # Actualizare liste pachete
    log_info "Actualizare liste pachete..."
    sudo apt-get update -qq
    
    # Instalare pachete sistem
    log_info "Instalare pachete sistem..."
    sudo apt-get install -y -qq \
        python3 \
        python3-pip \
        python3-venv \
        mininet \
        openvswitch-switch \
        tcpdump \
        wireshark-common \
        tshark \
        net-tools \
        iputils-ping \
        iproute2 \
        iperf3
    
    # Pornire Open vSwitch
    log_info "Pornire Open vSwitch..."
    sudo systemctl enable openvswitch-switch
    sudo systemctl start openvswitch-switch
    
    # Permisiuni pentru Wireshark/tcpdump (opțional)
    log_info "Configurare permisiuni captură pachete..."
    sudo usermod -aG wireshark "$USER" 2>/dev/null || true
    
    # Instalare dependențe Python (din requirements.txt dacă există)
    if [[ -f "$PROJECT_ROOT/requirements.txt" ]]; then
        log_info "Instalare dependențe Python..."
        pip3 install -r "$PROJECT_ROOT/requirements.txt" --break-system-packages --quiet
    fi
    
    log_success "Instalare completă finalizată!"
    echo ""
    log_info "NOTĂ: Reporniți terminalul pentru a activa noile grupuri (wireshark)"
}

#-------------------------------------------------------------------------------
# Configurare minimală
#-------------------------------------------------------------------------------

setup_minimal() {
    log_info "Configurare minimală..."
    echo ""
    
    # Setare permisiuni executabile pe scripturi
    chmod +x "$SCRIPT_DIR"/*.sh 2>/dev/null || true
    
    # Setare permisiuni pe topologii Mininet
    chmod +x "$PROJECT_ROOT/mininet/topologies/"*.py 2>/dev/null || true
    
    # Creare directoare lipsă
    mkdir -p "$PROJECT_ROOT/pcap"
    mkdir -p "$PROJECT_ROOT/solutions"
    
    log_success "Configurare minimală finalizată!"
}

#-------------------------------------------------------------------------------
# Main
#-------------------------------------------------------------------------------

main() {
    echo ""
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║       Setup Starterkit Săptămâna 5 — Adresare IP             ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo ""
    
    local mode="${1:---check}"
    
    case "$mode" in
        --full)
            install_full
            check_environment
            ;;
        --minimal)
            setup_minimal
            check_environment
            ;;
        --check)
            check_environment
            ;;
        --help|-h)
            echo "Utilizare: $0 [--full|--minimal|--check]"
            echo ""
            echo "Opțiuni:"
            echo "  --full     Instalează toate dependențele (necesită sudo)"
            echo "  --minimal  Doar verifică și configurează (fără instalări)"
            echo "  --check    Doar verifică starea mediului (implicit)"
            ;;
        *)
            log_error "Opțiune necunoscută: $mode"
            echo "Utilizare: $0 [--full|--minimal|--check]"
            exit 1
            ;;
    esac
}

main "$@"
