#!/bin/bash
# ============================================================================
# verify.sh - Verificare mediu și validare demo-uri
# Autor: Revolvix&Hypotheticalandrei
# ============================================================================

set -e

# Culori
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Contoare
PASS=0
FAIL=0
WARN=0

check_pass() { 
    echo -e "  ${GREEN}✓${NC} $1"
    ((PASS++))
}

check_fail() { 
    echo -e "  ${RED}✗${NC} $1"
    ((FAIL++))
}

check_warn() { 
    echo -e "  ${YELLOW}⚠${NC} $1"
    ((WARN++))
}

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Banner
echo ""
echo -e "${CYAN}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║      Verificare Mediu - Săptămâna 6                     ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""

# ============================================================================
# SECȚIUNEA 1: Comenzi sistem
# ============================================================================
echo -e "${BLUE}[1/5] Verificare comenzi sistem...${NC}"

check_command() {
    local cmd=$1
    local min_ver=$2
    
    if command -v "$cmd" &> /dev/null; then
        VER=$($cmd --version 2>&1 | head -1 | grep -oP '\d+\.\d+(\.\d+)?' | head -1 || echo "unknown")
        check_pass "$cmd ($VER)"
    else
        check_fail "$cmd LIPSĂ"
    fi
}

check_command "python3"
check_command "mn"
check_command "ovs-vsctl"
check_command "tcpdump"
check_command "tshark"
check_command "iptables"
check_command "conntrack"
check_command "ip"

echo ""

# ============================================================================
# SECȚIUNEA 2: Module Python
# ============================================================================
echo -e "${BLUE}[2/5] Verificare module Python...${NC}"

check_python_module() {
    local module=$1
    if python3 -c "import $module" 2>/dev/null; then
        VER=$(python3 -c "import $module; print(getattr($module, '__version__', 'ok'))" 2>/dev/null || echo "ok")
        check_pass "$module ($VER)"
    else
        check_fail "$module LIPSĂ"
    fi
}

check_python_module "socket"
check_python_module "argparse"
check_python_module "json"
check_python_module "subprocess"
check_python_module "os_ken"
check_python_module "scapy"

# Mininet Python API (special check)
if python3 -c "from mininet.net import Mininet" 2>/dev/null; then
    check_pass "mininet Python API"
else
    check_warn "mininet Python API (poate necesita PYTHONPATH)"
fi

echo ""

# ============================================================================
# SECȚIUNEA 3: Servicii sistem
# ============================================================================
echo -e "${BLUE}[3/5] Verificare servicii...${NC}"

# Open vSwitch
if systemctl is-active --quiet openvswitch-switch 2>/dev/null; then
    check_pass "openvswitch-switch (activ)"
else
    if pgrep -x ovs-vswitchd > /dev/null 2>&1; then
        check_pass "ovs-vswitchd (rulează)"
    else
        check_fail "Open vSwitch nu rulează"
    fi
fi

# Verificare port 6633 (SDN controller)
if netstat -tlnp 2>/dev/null | grep -q ":6633"; then
    check_warn "Port 6633 ocupat (controller deja activ?)"
else
    check_pass "Port 6633 liber"
fi

echo ""

# ============================================================================
# SECȚIUNEA 4: Fișiere proiect
# ============================================================================
echo -e "${BLUE}[4/5] Verificare fișiere proiect...${NC}"

check_file() {
    local file=$1
    local desc=$2
    
    if [[ -f "$PROJECT_DIR/$file" ]]; then
        check_pass "$desc"
    else
        check_fail "$desc ($file)"
    fi
}

check_file "seminar/mininet/topologies/topo_nat.py" "Topologie NAT"
check_file "seminar/mininet/topologies/topo_sdn.py" "Topologie SDN"
check_file "seminar/python/controllers/sdn_policy_controller.py" "Controller SDN"
check_file "seminar/python/apps/nat_observer.py" "NAT Observer"
check_file "seminar/python/apps/tcp_echo.py" "TCP Echo"
check_file "seminar/python/apps/udp_echo.py" "UDP Echo"
check_file "Makefile" "Makefile"
check_file "README.md" "README"

echo ""

# ============================================================================
# SECȚIUNEA 5: Test rapid funcționalitate
# ============================================================================
echo -e "${BLUE}[5/5] Test rapid funcționalitate...${NC}"

# Test Python syntax
test_python_syntax() {
    local file=$1
    local name=$2
    
    if [[ -f "$PROJECT_DIR/$file" ]]; then
        if python3 -m py_compile "$PROJECT_DIR/$file" 2>/dev/null; then
            check_pass "$name (syntax OK)"
        else
            check_fail "$name (syntax error)"
        fi
    fi
}

test_python_syntax "seminar/mininet/topologies/topo_nat.py" "topo_nat.py"
test_python_syntax "seminar/mininet/topologies/topo_sdn.py" "topo_sdn.py"
test_python_syntax "seminar/python/controllers/sdn_policy_controller.py" "sdn_policy_controller.py"
test_python_syntax "seminar/python/apps/nat_observer.py" "nat_observer.py"

# Test Mininet rapid (doar dacă root)
if [[ $EUID -eq 0 ]]; then
    echo ""
    echo -e "${BLUE}  Test rapid Mininet (necesită root)...${NC}"
    
    if timeout 10 mn --test pingall 2>/dev/null | grep -q "0% dropped"; then
        check_pass "Mininet ping test"
    else
        check_warn "Mininet test (poate necesita cleanup: mn -c)"
    fi
else
    echo ""
    check_warn "Test Mininet sărit (necesită root)"
fi

echo ""

# ============================================================================
# RAPORT FINAL
# ============================================================================
echo -e "${CYAN}══════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}                    RAPORT FINAL                          ${NC}"
echo -e "${CYAN}══════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "  ${GREEN}Verificări reușite:${NC}  $PASS"
echo -e "  ${YELLOW}Avertismente:${NC}        $WARN"
echo -e "  ${RED}Verificări eșuate:${NC}   $FAIL"
echo ""

TOTAL=$((PASS + FAIL))
if [[ $TOTAL -gt 0 ]]; then
    PERCENT=$((PASS * 100 / TOTAL))
else
    PERCENT=0
fi

if [[ $FAIL -eq 0 ]]; then
    echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}  ✓ MEDIU PREGĂTIT! Toate verificările au trecut.          ${NC}"
    echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
    exit 0
elif [[ $PERCENT -ge 70 ]]; then
    echo -e "${YELLOW}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${YELLOW}  ⚠ MEDIU PARȚIAL PREGĂTIT ($PERCENT% verificări reușite)   ${NC}"
    echo -e "${YELLOW}  Unele funcționalități pot fi indisponibile.               ${NC}"
    echo -e "${YELLOW}═══════════════════════════════════════════════════════════${NC}"
    exit 1
else
    echo -e "${RED}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${RED}  ✗ MEDIU NECORESPUNZĂTOR ($PERCENT% verificări reușite)     ${NC}"
    echo -e "${RED}  Rulează: make setup pentru instalare dependențe.          ${NC}"
    echo -e "${RED}═══════════════════════════════════════════════════════════${NC}"
    exit 2
fi
