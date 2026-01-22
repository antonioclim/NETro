#!/usr/bin/env bash
# =============================================================================
# smoke_test.sh — Smoke Test pentru Săptămâna 12
# =============================================================================
# Verifică existența și conținutul artefactelor generate de run_all.sh
#
# Utilizare: ./tests/smoke_test.sh
# Exit codes: 0 = PASS, 1 = FAIL
# =============================================================================
# Licență: MIT | ASE-CSIE Rețele de Calculatoare
# Hypotheticalandrei & Rezolvix
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

# Artefacte așteptate
ARTIFACTS_DIR="${PROJECT_ROOT}/artifacts"
LOG_FILE="${ARTIFACTS_DIR}/demo.log"
PCAP_FILE="${ARTIFACTS_DIR}/demo.pcap"
VALIDATION_FILE="${ARTIFACTS_DIR}/validation.txt"

# Culori
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Contoare
PASSED=0
FAILED=0
WARNINGS=0

# =============================================================================
# FUNCȚII DE TEST
# =============================================================================

pass() {
    echo -e "${GREEN}[PASS]${NC} $1"
    PASSED=$((PASSED + 1))
}

fail() {
    echo -e "${RED}[FAIL]${NC} $1"
    FAILED=$((FAILED + 1))
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
    WARNINGS=$((WARNINGS + 1))
}

check_file_exists() {
    local file="$1"
    local desc="$2"
    if [ -f "$file" ]; then
        pass "$desc exists: $file"
        return 0
    else
        fail "$desc missing: $file"
        return 1
    fi
}

check_file_not_empty() {
    local file="$1"
    local desc="$2"
    if [ -s "$file" ]; then
        local size=$(stat -c%s "$file" 2>/dev/null || wc -c < "$file")
        pass "$desc not empty: $size bytes"
        return 0
    else
        fail "$desc is empty"
        return 1
    fi
}

check_file_contains() {
    local file="$1"
    local pattern="$2"
    local desc="$3"
    if grep -q "$pattern" "$file" 2>/dev/null; then
        pass "$desc contains '$pattern'"
        return 0
    else
        fail "$desc missing '$pattern'"
        return 1
    fi
}

check_command() {
    local cmd="$1"
    local desc="$2"
    if command -v "$cmd" &>/dev/null; then
        pass "$desc available: $cmd"
        return 0
    else
        warn "$desc not found: $cmd"
        return 1
    fi
}

check_python_import() {
    local module="$1"
    if python3 -c "import $module" 2>/dev/null; then
        pass "Python import: $module"
        return 0
    else
        fail "Python import failed: $module"
        return 1
    fi
}

# =============================================================================
# TESTE
# =============================================================================

echo "=============================================="
echo "SMOKE TEST - Săptămâna 12: Email & RPC"
echo "=============================================="
echo "Project: $PROJECT_ROOT"
echo "Date: $(date)"
echo ""

# --- Verificare structură directoare ---
echo ""
echo "--- Structură directoare ---"
[ -d "$ARTIFACTS_DIR" ] && pass "artifacts/ exists" || fail "artifacts/ missing"
[ -d "${PROJECT_ROOT}/scripts" ] && pass "scripts/ exists" || fail "scripts/ missing"
[ -d "${PROJECT_ROOT}/src" ] && pass "src/ exists" || fail "src/ missing"
[ -d "${PROJECT_ROOT}/tests" ] && pass "tests/ exists" || fail "tests/ missing"
[ -d "${PROJECT_ROOT}/docs" ] && pass "docs/ exists" || fail "docs/ missing"

# --- Verificare artefacte ---
echo ""
echo "--- Artefacte demo ---"

if [ -d "$ARTIFACTS_DIR" ]; then
    check_file_exists "$LOG_FILE" "demo.log"
    check_file_exists "$PCAP_FILE" "demo.pcap"
    check_file_exists "$VALIDATION_FILE" "validation.txt"
    
    # Verificare conținut demo.log
    if [ -f "$LOG_FILE" ]; then
        echo ""
        echo "--- Conținut demo.log ---"
        local lines=$(wc -l < "$LOG_FILE")
        [ "$lines" -gt 10 ] && pass "demo.log has $lines lines (>10)" || warn "demo.log has only $lines lines"
        
        check_file_contains "$LOG_FILE" "SMTP" "demo.log"
        check_file_contains "$LOG_FILE" "JSON-RPC" "demo.log"
        check_file_contains "$LOG_FILE" "OK" "demo.log"
    fi
    
    # Verificare conținut validation.txt
    if [ -f "$VALIDATION_FILE" ]; then
        echo ""
        echo "--- Conținut validation.txt ---"
        check_file_contains "$VALIDATION_FILE" "VALIDATION" "validation.txt"
        check_file_contains "$VALIDATION_FILE" "WEEK: 12" "validation.txt"
    fi
else
    fail "artifacts/ directory missing - run './scripts/run_all.sh' first"
fi

# --- Verificare module Python ---
echo ""
echo "--- Module Python ---"
check_python_import "src.email.smtp_server"
check_python_import "src.email.smtp_client"
check_python_import "src.rpc.jsonrpc.jsonrpc_server"
check_python_import "src.rpc.jsonrpc.jsonrpc_client"
check_python_import "src.rpc.xmlrpc.xmlrpc_server"
check_python_import "src.rpc.xmlrpc.xmlrpc_client"
check_python_import "src.common.net_utils"

# --- Verificare exerciții ---
echo ""
echo "--- Exerciții ---"
if [ -f "${PROJECT_ROOT}/exercises/ex_01_smtp.py" ]; then
    python3 "${PROJECT_ROOT}/exercises/ex_01_smtp.py" --help &>/dev/null && \
        pass "ex_01_smtp.py --help works" || fail "ex_01_smtp.py --help failed"
fi

if [ -f "${PROJECT_ROOT}/exercises/ex_02_rpc.py" ]; then
    python3 "${PROJECT_ROOT}/exercises/ex_02_rpc.py" --help &>/dev/null && \
        pass "ex_02_rpc.py --help works" || fail "ex_02_rpc.py --help failed"
fi

# --- Verificare scripturi ---
echo ""
echo "--- Scripturi ---"
[ -x "${PROJECT_ROOT}/scripts/setup.sh" ] && pass "setup.sh is executable" || warn "setup.sh not executable"
[ -x "${PROJECT_ROOT}/scripts/run_all.sh" ] && pass "run_all.sh is executable" || warn "run_all.sh not executable"
[ -x "${PROJECT_ROOT}/scripts/cleanup.sh" ] && pass "cleanup.sh is executable" || warn "cleanup.sh not executable"

# --- Verificare unelte ---
echo ""
echo "--- Unelte sistem ---"
check_command "python3" "Python 3"
check_command "curl" "curl"
check_command "nc" "netcat" || check_command "netcat" "netcat"
check_command "tcpdump" "tcpdump"

# =============================================================================
# SUMAR
# =============================================================================

echo ""
echo "=============================================="
echo "REZULTAT SMOKE TEST"
echo "=============================================="
echo -e "Passed:   ${GREEN}${PASSED}${NC}"
echo -e "Failed:   ${RED}${FAILED}${NC}"
echo -e "Warnings: ${YELLOW}${WARNINGS}${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}SMOKE TEST: PASSED${NC}"
    exit 0
else
    echo -e "${RED}SMOKE TEST: FAILED${NC}"
    echo ""
    echo "Verificați:"
    echo "  1. Rulați './scripts/setup.sh' pentru instalare"
    echo "  2. Rulați './scripts/run_all.sh' pentru demo"
    echo "  3. Verificați logurile în artifacts/"
    exit 1
fi
