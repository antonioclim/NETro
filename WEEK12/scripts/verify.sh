#!/bin/bash
# =============================================================================
# verify.sh - Validare completă a mediului pentru Săptămâna 12
# Rețele de Calculatoare - ASE CSIE
# Autor: Revolvix&Hypotheticalandrei
# =============================================================================

set -e

# Culori
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

ERRORS=0
WARNINGS=0

check_pass() {
    echo -e "${GREEN}✓ PASS${NC}: $1"
}

check_fail() {
    echo -e "${RED}✗ FAIL${NC}: $1"
    ((ERRORS++))
}

check_warn() {
    echo -e "${YELLOW}⚠ WARN${NC}: $1"
    ((WARNINGS++))
}

print_section() {
    echo ""
    echo -e "${BLUE}━━━ $1 ━━━${NC}"
}

# =============================================================================
# Verificări Python
# =============================================================================
verify_python() {
    print_section "PYTHON"
    
    # Python 3.8+
    if command -v python3 &>/dev/null; then
        PY_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
        PY_MAJOR=$(echo $PY_VERSION | cut -d. -f1)
        PY_MINOR=$(echo $PY_VERSION | cut -d. -f2)
        
        if [[ $PY_MAJOR -ge 3 ]] && [[ $PY_MINOR -ge 8 ]]; then
            check_pass "Python $PY_VERSION (>= 3.8 necesar)"
        else
            check_fail "Python $PY_VERSION prea vechi (>= 3.8 necesar)"
        fi
    else
        check_fail "Python 3 nu este instalat"
    fi
    
    # Module standard
    for module in socket http.server json xmlrpc.client xmlrpc.server smtplib email threading; do
        if python3 -c "import $module" 2>/dev/null; then
            check_pass "Modul: $module"
        else
            check_fail "Modul lipsă: $module"
        fi
    done
    
    # Module opționale
    if python3 -c "import grpc" 2>/dev/null; then
        check_pass "Modul opțional: grpcio"
    else
        check_warn "Modul opțional lipsă: grpcio (necesar doar pentru gRPC)"
    fi
    
    if python3 -c "import colorama" 2>/dev/null; then
        check_pass "Modul opțional: colorama"
    else
        check_warn "Modul opțional lipsă: colorama (output mai frumos)"
    fi
}

# =============================================================================
# Verificări fișiere proiect
# =============================================================================
verify_project_files() {
    print_section "FIȘIERE PROIECT"
    
    # Fișiere esențiale
    essential_files=(
        "README.md"
        "Makefile"
        "requirements.txt"
        "src/email/smtp_server.py"
        "src/email/smtp_client.py"
        "src/rpc/jsonrpc/jsonrpc_server.py"
        "src/rpc/jsonrpc/jsonrpc_client.py"
        "exercises/ex_01_smtp.py"
        "exercises/ex_02_rpc.py"
    )
    
    for file in "${essential_files[@]}"; do
        if [[ -f "$file" ]]; then
            check_pass "Fișier: $file"
        else
            check_fail "Fișier lipsă: $file"
        fi
    done
    
    # Directoare
    directories=(
        "src/email"
        "src/rpc/jsonrpc"
        "src/rpc/xmlrpc"
        "exercises"
        "scripts"
        "docs"
        "mininet"
    )
    
    for dir in "${directories[@]}"; do
        if [[ -d "$dir" ]]; then
            check_pass "Director: $dir/"
        else
            check_fail "Director lipsă: $dir/"
        fi
    done
}

# =============================================================================
# Verificări sintaxă Python
# =============================================================================
verify_python_syntax() {
    print_section "SINTAXĂ PYTHON"
    
    python_files=(
        "src/email/smtp_server.py"
        "src/email/smtp_client.py"
        "src/rpc/jsonrpc/jsonrpc_server.py"
        "src/rpc/jsonrpc/jsonrpc_client.py"
        "exercises/ex_01_smtp.py"
        "exercises/ex_02_rpc.py"
    )
    
    for file in "${python_files[@]}"; do
        if [[ -f "$file" ]]; then
            if python3 -m py_compile "$file" 2>/dev/null; then
                check_pass "Sintaxă OK: $file"
            else
                check_fail "Eroare sintaxă: $file"
            fi
        fi
    done
}

# =============================================================================
# Verificări porturi disponibile
# =============================================================================
verify_ports() {
    print_section "PORTURI"
    
    ports=(1025 8080 8000 50051)
    
    for port in "${ports[@]}"; do
        if ! ss -tuln 2>/dev/null | grep -q ":$port "; then
            check_pass "Port $port disponibil"
        else
            check_warn "Port $port ocupat (poate afecta demo-urile)"
        fi
    done
}

# =============================================================================
# Verificări unelte rețea
# =============================================================================
verify_network_tools() {
    print_section "UNELTE REȚEA"
    
    # Esențiale
    if command -v nc &>/dev/null || command -v netcat &>/dev/null; then
        check_pass "netcat disponibil"
    else
        check_warn "netcat nu este instalat"
    fi
    
    if command -v curl &>/dev/null; then
        check_pass "curl disponibil"
    else
        check_warn "curl nu este instalat"
    fi
    
    # Pentru captură
    if command -v tcpdump &>/dev/null; then
        check_pass "tcpdump disponibil"
    else
        check_warn "tcpdump nu este instalat (necesar pentru capturi)"
    fi
    
    if command -v tshark &>/dev/null; then
        check_pass "tshark disponibil"
    else
        check_warn "tshark nu este instalat (recomandat pentru analiză)"
    fi
}

# =============================================================================
# Test funcțional rapid
# =============================================================================
verify_functional() {
    print_section "TESTE FUNCȚIONALE"
    
    # Test exercițiu SMTP
    echo -n "Test ex_01_smtp.py... "
    if timeout 5 python3 exercises/ex_01_smtp.py --help &>/dev/null; then
        check_pass "ex_01_smtp.py rulează"
    else
        check_fail "ex_01_smtp.py nu rulează corect"
    fi
    
    # Test exercițiu RPC
    echo -n "Test ex_02_rpc.py... "
    if timeout 5 python3 exercises/ex_02_rpc.py --help &>/dev/null; then
        check_pass "ex_02_rpc.py rulează"
    else
        check_fail "ex_02_rpc.py nu rulează corect"
    fi
    
    # Test import module principale
    echo -n "Test import SMTP server... "
    if python3 -c "
import sys
sys.path.insert(0, '.')
from src.email.smtp_server import SimpleSMTPServer
print('OK')
" 2>/dev/null | grep -q "OK"; then
        check_pass "Import SMTP server OK"
    else
        check_warn "Import SMTP server necesită ajustări path"
    fi
}

# =============================================================================
# Sumar
# =============================================================================
show_summary() {
    print_section "SUMAR"
    
    echo ""
    if [[ $ERRORS -eq 0 ]] && [[ $WARNINGS -eq 0 ]]; then
        echo -e "${GREEN}════════════════════════════════════════════${NC}"
        echo -e "${GREEN}  ✓ TOATE VERIFICĂRILE AU TRECUT!           ${NC}"
        echo -e "${GREEN}════════════════════════════════════════════${NC}"
        echo ""
        echo "Mediul este pregătit pentru Săptămâna 12."
        echo "Rulați 'make run-demo' pentru a începe."
        exit 0
    elif [[ $ERRORS -eq 0 ]]; then
        echo -e "${YELLOW}════════════════════════════════════════════${NC}"
        echo -e "${YELLOW}  ⚠ VERIFICĂRI TRECUTE CU $WARNINGS AVERTISMENTE${NC}"
        echo -e "${YELLOW}════════════════════════════════════════════${NC}"
        echo ""
        echo "Mediul funcționează, dar unele componente opționale lipsesc."
        exit 0
    else
        echo -e "${RED}════════════════════════════════════════════${NC}"
        echo -e "${RED}  ✗ $ERRORS ERORI, $WARNINGS AVERTISMENTE     ${NC}"
        echo -e "${RED}════════════════════════════════════════════${NC}"
        echo ""
        echo "Rezolvați erorile înainte de a continua."
        echo "Rulați 'scripts/setup.sh' pentru configurare automată."
        exit 1
    fi
}

# =============================================================================
# Main
# =============================================================================
main() {
    echo ""
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║  VERIFICARE MEDIU - Săptămâna 12: Email & RPC              ║${NC}"
    echo -e "${BLUE}║  Rețele de Calculatoare - ASE CSIE                         ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
    
    verify_python
    verify_project_files
    verify_python_syntax
    verify_ports
    verify_network_tools
    verify_functional
    show_summary
}

main "$@"
