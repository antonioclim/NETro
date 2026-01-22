#!/usr/bin/env bash
# =============================================================================
# setup.sh - Pregătirea mediului pentru Săptămâna 2: Socket Programming
# Rețele de Calculatoare - ASE București, CSIE
# =============================================================================
# Revolvix&Hypotheticalandrei
# =============================================================================

set -euo pipefail
IFS=$'\n\t'

# Culori pentru output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Directorul script-ului
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║       Setup Environment - Săptămâna 2: Socket Programming   ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# =============================================================================
# Funcții utilitare
# =============================================================================

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

log_error() {
    echo -e "${RED}[✗]${NC} $1"
}

check_command() {
    if command -v "$1" &> /dev/null; then
        log_success "$1 găsit: $(command -v "$1")"
        return 0
    else
        log_error "$1 NU este instalat"
        return 1
    fi
}

# =============================================================================
# Verificare cerințe sistem
# =============================================================================

log_info "Verificare cerințe sistem..."
echo ""

MISSING_DEPS=0

# Python 3
if check_command python3; then
    PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
    log_info "  Versiune Python: $PYTHON_VERSION"
else
    MISSING_DEPS=$((MISSING_DEPS + 1))
fi

# pip3
if check_command pip3; then
    :
else
    MISSING_DEPS=$((MISSING_DEPS + 1))
fi

# Mininet (opțional dar recomandat)
if check_command mn; then
    log_success "Mininet găsit"
else
    log_warning "Mininet NU este instalat (opțional pentru simulări de rețea)"
    log_info "  Instalare: sudo apt-get install mininet"
fi

# tshark/Wireshark
if check_command tshark; then
    log_success "tshark găsit"
else
    log_warning "tshark NU este instalat (necesar pentru capturi)"
    log_info "  Instalare: sudo apt-get install tshark"
fi

# tcpdump
if check_command tcpdump; then
    log_success "tcpdump găsit"
else
    log_warning "tcpdump NU este instalat"
    log_info "  Instalare: sudo apt-get install tcpdump"
fi

# netcat
if check_command nc; then
    log_success "netcat (nc) găsit"
else
    log_warning "netcat NU este instalat"
    log_info "  Instalare: sudo apt-get install netcat-openbsd"
fi

# lsof
if check_command lsof; then
    log_success "lsof găsit"
else
    log_warning "lsof NU este instalat"
fi

echo ""

# =============================================================================
# Instalare dependențe Python
# =============================================================================

log_info "Instalare dependențe Python..."

REQUIREMENTS_FILE="$PROJECT_ROOT/requirements.txt"

if [[ -f "$REQUIREMENTS_FILE" ]]; then
    log_info "Folosesc requirements.txt din proiect"
    pip3 install --user -q -r "$REQUIREMENTS_FILE" 2>/dev/null || {
        log_warning "Unele pachete pot necesita sudo: pip3 install -r requirements.txt"
    }
    log_success "Dependențe Python instalate"
else
    log_warning "requirements.txt nu a fost găsit, instalez pachete esențiale"
    pip3 install --user -q scapy pyshark 2>/dev/null || true
fi

echo ""

# =============================================================================
# Creare structură directoare
# =============================================================================

log_info "Verificare/creare structură directoare..."

DIRS=(
    "$PROJECT_ROOT/seminar/captures"
    "$PROJECT_ROOT/logs"
    "$PROJECT_ROOT/pcap"
)

for dir in "${DIRS[@]}"; do
    if [[ ! -d "$dir" ]]; then
        mkdir -p "$dir"
        log_success "Creat: $dir"
    else
        log_info "Există: $dir"
    fi
done

echo ""

# =============================================================================
# Configurare sysctl (dacă este root)
# =============================================================================

if [[ $EUID -eq 0 ]]; then
    log_info "Aplicare configurări sysctl pentru rețea..."
    
    SYSCTL_CONF="$PROJECT_ROOT/configs/sysctl.conf"
    if [[ -f "$SYSCTL_CONF" ]]; then
        sysctl -p "$SYSCTL_CONF" 2>/dev/null || log_warning "Unele setări sysctl nu au putut fi aplicate"
        log_success "Configurări sysctl aplicate"
    fi
else
    log_warning "Nu rulează ca root - configurările sysctl vor fi omise"
    log_info "  Pentru configurări de rețea avansate, rulați: sudo $0"
fi

echo ""

# =============================================================================
# Verificare porturi disponibile
# =============================================================================

log_info "Verificare porturi folosite în demo-uri..."

PORTS_TO_CHECK=(8080 8081 9999 5000)
PORTS_IN_USE=0

for port in "${PORTS_TO_CHECK[@]}"; do
    if ss -tuln 2>/dev/null | grep -q ":$port "; then
        log_warning "Port $port este OCUPAT"
        log_info "  Proces: $(lsof -i :$port 2>/dev/null | tail -1 || echo 'necunoscut')"
        PORTS_IN_USE=$((PORTS_IN_USE + 1))
    else
        log_success "Port $port disponibil"
    fi
done

echo ""

# =============================================================================
# Raport final
# =============================================================================

echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}                        RAPORT SETUP                           ${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

if [[ $MISSING_DEPS -eq 0 ]]; then
    log_success "Toate dependențele critice sunt instalate"
else
    log_error "$MISSING_DEPS dependențe critice lipsesc"
fi

if [[ $PORTS_IN_USE -gt 0 ]]; then
    log_warning "$PORTS_IN_USE porturi necesare sunt ocupate"
else
    log_success "Toate porturile necesare sunt disponibile"
fi

echo ""
echo -e "${GREEN}Setup completat!${NC}"
echo ""
echo "Pași următori:"
echo "  1. make verify        - Verifică configurația"
echo "  2. make demo-tcp      - Rulează demo TCP"
echo "  3. make demo-udp      - Rulează demo UDP"
echo "  4. make mininet-cli   - Deschide CLI Mininet"
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
