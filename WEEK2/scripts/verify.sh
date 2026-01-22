#!/usr/bin/env bash
# =============================================================================
# verify.sh - Verificare mediu și funcționalitate pentru Săptămâna 2
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
CYAN='\033[0;36m'
NC='\033[0m'

# Directorul script-ului
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Contoare
TESTS_PASSED=0
TESTS_FAILED=0
TESTS_SKIPPED=0

echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║         Verificare Mediu - Săptămâna 2: Sockets             ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# =============================================================================
# Funcții utilitare
# =============================================================================

test_pass() {
    echo -e "${GREEN}[PASS]${NC} $1"
    TESTS_PASSED=$((TESTS_PASSED + 1))
}

test_fail() {
    echo -e "${RED}[FAIL]${NC} $1"
    TESTS_FAILED=$((TESTS_FAILED + 1))
}

test_skip() {
    echo -e "${YELLOW}[SKIP]${NC} $1"
    TESTS_SKIPPED=$((TESTS_SKIPPED + 1))
}

test_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

section_header() {
    echo ""
    echo -e "${BLUE}── $1 ──${NC}"
}

# =============================================================================
# 1. VERIFICARE STRUCTURĂ DIRECTOARE
# =============================================================================

section_header "1. Structură Directoare"

REQUIRED_DIRS=(
    "seminar/python/exercises"
    "seminar/python/templates"
    "seminar/python/utils"
    "seminar/mininet/topologies"
    "seminar/captures"
    "docs"
    "scripts"
    "logs"
)

for dir in "${REQUIRED_DIRS[@]}"; do
    if [[ -d "$PROJECT_ROOT/$dir" ]]; then
        test_pass "Director: $dir"
    else
        test_fail "Director lipsă: $dir"
    fi
done

# =============================================================================
# 2. VERIFICARE FIȘIERE CRITICE
# =============================================================================

section_header "2. Fișiere Critice"

REQUIRED_FILES=(
    "README.md"
    "Makefile"
    "seminar/python/exercises/ex_2_01_tcp.py"
    "seminar/python/exercises/ex_2_02_udp.py"
    "seminar/python/templates/tcp_server_template.py"
    "seminar/python/templates/udp_server_template.py"
    "seminar/mininet/topologies/topo_2_base.py"
    "docs/curs.md"
    "docs/seminar.md"
    "docs/lab.md"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [[ -f "$PROJECT_ROOT/$file" ]]; then
        test_pass "Fișier: $file"
    else
        test_fail "Fișier lipsă: $file"
    fi
done

# =============================================================================
# 3. VERIFICARE DEPENDENȚE SISTEM
# =============================================================================

section_header "3. Dependențe Sistem"

# Python 3
if command -v python3 &> /dev/null; then
    PY_VER=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" 2>/dev/null; then
        test_pass "Python $PY_VER (>= 3.8)"
    else
        test_fail "Python $PY_VER (necesită >= 3.8)"
    fi
else
    test_fail "Python 3 nu este instalat"
fi

# pip3
if command -v pip3 &> /dev/null; then
    test_pass "pip3 disponibil"
else
    test_fail "pip3 nu este instalat"
fi

# tshark
if command -v tshark &> /dev/null; then
    test_pass "tshark disponibil"
else
    test_skip "tshark nu este instalat (opțional)"
fi

# tcpdump
if command -v tcpdump &> /dev/null; then
    test_pass "tcpdump disponibil"
else
    test_skip "tcpdump nu este instalat (opțional)"
fi

# netcat
if command -v nc &> /dev/null; then
    test_pass "netcat (nc) disponibil"
else
    test_skip "netcat nu este instalat (opțional)"
fi

# Mininet
if command -v mn &> /dev/null; then
    test_pass "Mininet disponibil"
else
    test_skip "Mininet nu este instalat (opțional pentru simulări)"
fi

# =============================================================================
# 4. VERIFICARE MODULE PYTHON
# =============================================================================

section_header "4. Module Python"

PYTHON_MODULES=(
    "socket:Sockets (builtin)"
    "threading:Threading (builtin)"
    "argparse:Argparse (builtin)"
    "json:JSON (builtin)"
    "struct:Struct (builtin)"
    "datetime:Datetime (builtin)"
)

for module_entry in "${PYTHON_MODULES[@]}"; do
    module="${module_entry%%:*}"
    name="${module_entry##*:}"
    if python3 -c "import $module" 2>/dev/null; then
        test_pass "$name"
    else
        test_fail "$name (import $module)"
    fi
done

# Module opționale
OPTIONAL_MODULES=(
    "scapy:Scapy (packet crafting)"
    "pyshark:PyShark (pcap analysis)"
)

for module_entry in "${OPTIONAL_MODULES[@]}"; do
    module="${module_entry%%:*}"
    name="${module_entry##*:}"
    if python3 -c "import $module" 2>/dev/null; then
        test_pass "$name"
    else
        test_skip "$name (opțional)"
    fi
done

# =============================================================================
# 5. VERIFICARE SINTAXĂ PYTHON
# =============================================================================

section_header "5. Sintaxă Python"

PYTHON_FILES=(
    "seminar/python/exercises/ex_2_01_tcp.py"
    "seminar/python/exercises/ex_2_02_udp.py"
    "seminar/python/templates/tcp_server_template.py"
    "seminar/python/templates/udp_server_template.py"
    "seminar/mininet/topologies/topo_2_base.py"
)

for pyfile in "${PYTHON_FILES[@]}"; do
    filepath="$PROJECT_ROOT/$pyfile"
    if [[ -f "$filepath" ]]; then
        if python3 -m py_compile "$filepath" 2>/dev/null; then
            test_pass "Sintaxă OK: $(basename "$pyfile")"
        else
            test_fail "Eroare sintaxă: $pyfile"
        fi
    fi
done

# =============================================================================
# 6. VERIFICARE PORTURI DISPONIBILE
# =============================================================================

section_header "6. Porturi Disponibile"

DEFAULT_PORTS=(8080 8081 9999 5000)

for port in "${DEFAULT_PORTS[@]}"; do
    if ! ss -tuln 2>/dev/null | grep -q ":$port "; then
        test_pass "Port $port disponibil"
    else
        test_fail "Port $port OCUPAT"
        # Afișează ce proces folosește portul
        if command -v lsof &> /dev/null; then
            PROC=$(lsof -i :$port 2>/dev/null | tail -1 | awk '{print $1}' || echo "necunoscut")
            test_info "  └─ Proces: $PROC"
        fi
    fi
done

# =============================================================================
# 7. TEST FUNCȚIONAL RAPID (SOCKET BASIC)
# =============================================================================

section_header "7. Test Funcțional Socket"

# Test rapid: creăm un socket TCP și verificăm că funcționează
SOCKET_TEST=$(python3 -c "
import socket
import sys
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('127.0.0.1', 0))  # Port aleator
    port = s.getsockname()[1]
    s.listen(1)
    s.close()
    print(f'OK:{port}')
except Exception as e:
    print(f'ERR:{e}')
    sys.exit(1)
" 2>&1)

if [[ "$SOCKET_TEST" == OK:* ]]; then
    test_pass "Socket TCP poate fi creat și bound"
else
    test_fail "Eroare creare socket: ${SOCKET_TEST#ERR:}"
fi

# Test UDP
UDP_TEST=$(python3 -c "
import socket
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('127.0.0.1', 0))
    s.close()
    print('OK')
except Exception as e:
    print(f'ERR:{e}')
" 2>&1)

if [[ "$UDP_TEST" == "OK" ]]; then
    test_pass "Socket UDP poate fi creat și bound"
else
    test_fail "Eroare creare socket UDP: ${UDP_TEST#ERR:}"
fi

# =============================================================================
# 8. VERIFICARE PERMISIUNI
# =============================================================================

section_header "8. Permisiuni"

# Verificăm dacă putem scrie în directoarele necesare
WRITE_DIRS=("logs" "seminar/captures" "pcap")

for dir in "${WRITE_DIRS[@]}"; do
    dirpath="$PROJECT_ROOT/$dir"
    if [[ -d "$dirpath" ]]; then
        if [[ -w "$dirpath" ]]; then
            test_pass "Scriere permisă: $dir/"
        else
            test_fail "Nu pot scrie în: $dir/"
        fi
    fi
done

# Verificare pentru capturi de pachete (necesită privilegii)
if [[ $EUID -eq 0 ]]; then
    test_pass "Rulează ca root (poate captura pachete)"
else
    test_info "Nu rulează ca root"
    test_info "  └─ Pentru capturi de pachete: sudo make capture"
    
    # Verificăm dacă user-ul e în grupul wireshark
    if groups 2>/dev/null | grep -qw wireshark; then
        test_pass "User în grupul 'wireshark' (poate captura fără sudo)"
    else
        test_skip "User NU e în grupul 'wireshark'"
        test_info "  └─ Adăugare: sudo usermod -aG wireshark \$USER"
    fi
fi

# =============================================================================
# RAPORT FINAL
# =============================================================================

echo ""
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}                      RAPORT VERIFICARE                        ${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo ""

TOTAL_TESTS=$((TESTS_PASSED + TESTS_FAILED + TESTS_SKIPPED))

echo -e "  ${GREEN}Trecute:${NC}  $TESTS_PASSED / $TOTAL_TESTS"
echo -e "  ${RED}Eșuate:${NC}   $TESTS_FAILED / $TOTAL_TESTS"
echo -e "  ${YELLOW}Omise:${NC}    $TESTS_SKIPPED / $TOTAL_TESTS"
echo ""

if [[ $TESTS_FAILED -eq 0 ]]; then
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║          ✓ MEDIUL ESTE PREGĂTIT PENTRU LABORATOR            ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
    exit 0
else
    echo -e "${RED}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║    ✗ ATENȚIE: $TESTS_FAILED teste eșuate - verificați erorile          ║${NC}"
    echo -e "${RED}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "Sugestii:"
    echo "  1. Rulați: make setup"
    echo "  2. Verificați instalarea: pip3 install -r requirements.txt"
    echo "  3. Pentru Mininet: sudo apt-get install mininet"
    exit 1
fi
