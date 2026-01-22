#!/usr/bin/env bash
#===============================================================================
# verify.sh - Verificare mediu de lucru pentru Starterkit S1
#===============================================================================
# Rețele de Calculatoare - Săptămâna 1
# ASE București
#
# Utilizare:
#   bash scripts/verify.sh
#   bash scripts/verify.sh --verbose
#===============================================================================

# Culori
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

VERBOSE="${1:-}"
ERRORS=0
WARNINGS=0

#===============================================================================
# Funcții helper
#===============================================================================

check_pass() {
    echo -e "${GREEN}[✓]${NC} $1"
}

check_fail() {
    echo -e "${RED}[✗]${NC} $1"
    ((ERRORS++))
}

check_warn() {
    echo -e "${YELLOW}[!]${NC} $1"
    ((WARNINGS++))
}

check_info() {
    echo -e "${CYAN}[i]${NC} $1"
}

header() {
    echo ""
    echo -e "${BLUE}━━━ $1 ━━━${NC}"
}

verbose() {
    if [[ "$VERBOSE" == "--verbose" ]]; then
        echo "    $1"
    fi
}

#===============================================================================
# Verificări
#===============================================================================

check_python() {
    header "Python"
    
    if command -v python3 &>/dev/null; then
        VERSION=$(python3 --version 2>&1)
        
        # Verificăm versiunea >= 3.10
        MAJOR=$(python3 -c "import sys; print(sys.version_info.major)")
        MINOR=$(python3 -c "import sys; print(sys.version_info.minor)")
        
        if [[ $MAJOR -ge 3 && $MINOR -ge 10 ]]; then
            check_pass "Python 3.10+ detectat: $VERSION"
        else
            check_warn "Python $VERSION detectat (recomandat: 3.10+)"
        fi
        
        verbose "Locație: $(which python3)"
    else
        check_fail "Python3 nu este instalat"
    fi
    
    # Verificăm module Python
    if [[ "$VERBOSE" == "--verbose" ]]; then
        echo "    Module Python:"
        for mod in socket subprocess csv re statistics; do
            if python3 -c "import $mod" 2>/dev/null; then
                echo "      ✓ $mod"
            else
                echo "      ✗ $mod"
            fi
        done
    fi
}

check_network_tools() {
    header "Instrumente de rețea"
    
    # tshark
    if command -v tshark &>/dev/null; then
        VERSION=$(tshark --version 2>&1 | head -1)
        check_pass "tshark disponibil: $VERSION"
        verbose "Locație: $(which tshark)"
    else
        check_fail "tshark nu este instalat (apt install tshark)"
    fi
    
    # tcpdump
    if command -v tcpdump &>/dev/null; then
        VERSION=$(tcpdump --version 2>&1 | head -1)
        check_pass "tcpdump disponibil: $VERSION"
    else
        check_warn "tcpdump nu este instalat (opțional)"
    fi
    
    # netcat
    if command -v nc &>/dev/null; then
        # Detectăm varianta
        NC_HELP=$(nc -h 2>&1 || true)
        if echo "$NC_HELP" | grep -q "OpenBSD"; then
            check_pass "netcat disponibil: netcat-openbsd"
        elif echo "$NC_HELP" | grep -q "GNU"; then
            check_pass "netcat disponibil: netcat-traditional"
        else
            check_pass "netcat disponibil"
        fi
    else
        check_fail "netcat nu este instalat (apt install netcat-openbsd)"
    fi
    
    # iproute2 (ip command)
    if command -v ip &>/dev/null; then
        VERSION=$(ip -V 2>&1 | head -1)
        check_pass "iproute2 disponibil: $VERSION"
    else
        check_fail "iproute2 nu este instalat"
    fi
    
    # ping
    if command -v ping &>/dev/null; then
        check_pass "ping disponibil"
    else
        check_fail "ping nu este instalat"
    fi
    
    # ss (socket statistics)
    if command -v ss &>/dev/null; then
        check_pass "ss disponibil"
    else
        check_warn "ss nu este disponibil"
    fi
    
    # curl/wget
    if command -v curl &>/dev/null; then
        check_pass "curl disponibil"
    elif command -v wget &>/dev/null; then
        check_pass "wget disponibil"
    else
        check_warn "curl/wget nu sunt instalate"
    fi
}

check_mininet() {
    header "Mininet"
    
    if command -v mn &>/dev/null; then
        VERSION=$(mn --version 2>&1 || echo "versiune necunoscută")
        check_pass "Mininet disponibil: $VERSION"
        verbose "Locație: $(which mn)"
        
        # Verificăm Open vSwitch
        if command -v ovs-vsctl &>/dev/null; then
            OVS_VERSION=$(ovs-vsctl --version 2>&1 | head -1)
            check_pass "Open vSwitch disponibil: $OVS_VERSION"
            
            # Verificăm dacă serviciul rulează
            if systemctl is-active --quiet openvswitch-switch 2>/dev/null; then
                check_pass "Serviciu OVS activ"
            elif pgrep -x ovs-vswitchd &>/dev/null; then
                check_pass "ovs-vswitchd rulează"
            else
                check_warn "Serviciul OVS nu pare activ"
            fi
        else
            check_warn "Open vSwitch nu este instalat"
        fi
    else
        check_warn "Mininet nu este instalat (opțional pentru acest lab)"
        check_info "Instalare: sudo apt install mininet openvswitch-switch"
    fi
}

check_docker() {
    header "Docker (opțional)"
    
    if command -v docker &>/dev/null; then
        VERSION=$(docker --version 2>&1)
        check_pass "Docker disponibil: $VERSION"
        
        # Verificăm dacă putem rula fără sudo
        if docker ps &>/dev/null 2>&1; then
            check_pass "Docker accesibil fără sudo"
        else
            check_warn "Docker necesită sudo (adăugați user la grupul docker)"
        fi
        
        # Docker Compose
        if docker compose version &>/dev/null 2>&1; then
            COMPOSE_VERSION=$(docker compose version 2>&1)
            check_pass "Docker Compose disponibil: $COMPOSE_VERSION"
        elif command -v docker-compose &>/dev/null; then
            check_pass "docker-compose (legacy) disponibil"
        else
            check_warn "Docker Compose nu este instalat"
        fi
    else
        check_info "Docker nu este instalat (alternativă pentru VM)"
    fi
}

check_permissions() {
    header "Permisiuni"
    
    # Verificăm grupul wireshark
    if groups 2>/dev/null | grep -q wireshark; then
        check_pass "Utilizator în grupul wireshark"
    else
        check_warn "Utilizator NU în grupul wireshark (tshark poate necesita sudo)"
        check_info "Remediere: sudo usermod -aG wireshark \$USER && logout/login"
    fi
    
    # Verificăm dacă putem captura fără sudo
    if timeout 1 tshark -i lo -c 1 &>/dev/null 2>&1; then
        check_pass "Captură posibilă fără sudo"
    else
        check_warn "Captura poate necesita sudo"
    fi
}

check_connectivity() {
    header "Conectivitate"
    
    # Loopback
    if ping -c 1 -W 1 127.0.0.1 &>/dev/null; then
        check_pass "Loopback funcțional"
    else
        check_fail "Loopback nu răspunde!"
    fi
    
    # Gateway
    GATEWAY=$(ip route | grep default | awk '{print $3}' | head -1)
    if [[ -n "$GATEWAY" ]]; then
        if ping -c 1 -W 2 "$GATEWAY" &>/dev/null; then
            check_pass "Gateway ($GATEWAY) accesibil"
        else
            check_warn "Gateway ($GATEWAY) nu răspunde"
        fi
    else
        check_warn "Nu s-a detectat gateway"
    fi
    
    # Internet
    if ping -c 1 -W 2 8.8.8.8 &>/dev/null; then
        check_pass "Internet accesibil (8.8.8.8)"
    else
        check_warn "Internet inaccesibil"
    fi
}

check_starterkit_files() {
    header "Fișiere Starterkit"
    
    # Determinăm directorul starterkit
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    KIT_DIR="$(dirname "$SCRIPT_DIR")"
    
    # Fișiere esențiale
    FILES=(
        "README.md"
        "Makefile"
        "python/exercises/ex_1_01_ping_latency.py"
        "python/exercises/ex_1_02_tcp_server_client.py"
    )
    
    for file in "${FILES[@]}"; do
        if [[ -f "$KIT_DIR/$file" ]]; then
            check_pass "Fișier prezent: $file"
        else
            check_warn "Fișier lipsă: $file"
        fi
    done
}

#===============================================================================
# Sumar
#===============================================================================

print_summary() {
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    
    if [[ $ERRORS -eq 0 && $WARNINGS -eq 0 ]]; then
        echo -e "${GREEN}  ✅ MEDIU OK - toate verificările au trecut!${NC}"
    elif [[ $ERRORS -eq 0 ]]; then
        echo -e "${YELLOW}  ⚠️  MEDIU PARȚIAL - $WARNINGS avertismente${NC}"
        echo -e "${YELLOW}     Laboratorul poate funcționa, dar unele funcții lipsesc.${NC}"
    else
        echo -e "${RED}  ❌ MEDIU INCOMPLET - $ERRORS erori, $WARNINGS avertismente${NC}"
        echo -e "${RED}     Rulați 'make setup' sau 'sudo bash scripts/setup.sh'${NC}"
    fi
    
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
}

#===============================================================================
# Main
#===============================================================================

main() {
    echo ""
    echo -e "${BLUE}╔═══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║     VERIFICARE MEDIU - Starterkit S1 Rețele                   ║${NC}"
    echo -e "${BLUE}╚═══════════════════════════════════════════════════════════════╝${NC}"
    
    check_python
    check_network_tools
    check_mininet
    check_docker
    check_permissions
    check_connectivity
    check_starterkit_files
    
    print_summary
    
    # Exit code
    if [[ $ERRORS -gt 0 ]]; then
        exit 1
    else
        exit 0
    fi
}

main "$@"
