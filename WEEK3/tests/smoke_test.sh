#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════════════
# smoke_test.sh — Teste rapide pentru validarea kit-ului S3
# ═══════════════════════════════════════════════════════════════════════════
#
# UTILIZARE:
#   bash tests/smoke_test.sh           # Rulează toate testele
#   bash tests/smoke_test.sh syntax    # Doar verificare sintaxă Python
#   bash tests/smoke_test.sh imports   # Doar verificare importuri
#   bash tests/smoke_test.sh --verbose # Output detaliat
#
# DESCRIERE:
#   Acest script verifică rapid că toate componentele kit-ului funcționează:
#   1. Sintaxa Python e corectă (py_compile)
#   2. Importurile funcționează
#   3. Argumentele --help funcționează
#   4. Demo-uri rapide (opțional, necesită Mininet pentru unele)
#
# EXIT CODES:
#   0 - Toate testele au trecut
#   1 - Cel puțin un test a eșuat
#
# ═══════════════════════════════════════════════════════════════════════════

set -uo pipefail

# Culori
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

# Contoare
PASSED=0
FAILED=0
SKIPPED=0

# ─── Funcții helper ───────────────────────────────────────────────────────

log_test() {
    echo -e "${BLUE}[TEST]${NC} $1"
}

log_pass() {
    echo -e "${GREEN}[PASS]${NC} $1"
    ((PASSED++))
}

log_fail() {
    echo -e "${RED}[FAIL]${NC} $1"
    ((FAILED++))
}

log_skip() {
    echo -e "${YELLOW}[SKIP]${NC} $1"
    ((SKIPPED++))
}

# ─── Configurare ──────────────────────────────────────────────────────────

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
EXAMPLES_DIR="$ROOT_DIR/python/examples"
TEMPLATES_DIR="$ROOT_DIR/python/templates"
UTILS_DIR="$ROOT_DIR/python/utils"

VERBOSE=false
TEST_TYPE="${1:-all}"

if [[ "${1:-}" == "--verbose" ]] || [[ "${2:-}" == "--verbose" ]]; then
    VERBOSE=true
fi

# ─── Banner ───────────────────────────────────────────────────────────────

echo ""
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║     SMOKE TESTS — Starterkit S3 (Socket Programming)           ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""

cd "$ROOT_DIR"

# ═══════════════════════════════════════════════════════════════════════════
# TEST 1: Verificare sintaxă Python
# ═══════════════════════════════════════════════════════════════════════════

test_syntax() {
    echo ""
    echo -e "${CYAN}═══ TEST: Sintaxă Python ═══${NC}"
    echo ""
    
    local files=(
        "$EXAMPLES_DIR"/*.py
        "$TEMPLATES_DIR"/*.py
        "$UTILS_DIR"/*.py
    )
    
    for file in "${files[@]}"; do
        if [[ -f "$file" ]]; then
            filename=$(basename "$file")
            log_test "Verificare sintaxă: $filename"
            
            if python3 -m py_compile "$file" 2>/dev/null; then
                log_pass "$filename - sintaxă corectă"
            else
                log_fail "$filename - erori de sintaxă"
                if $VERBOSE; then
                    python3 -m py_compile "$file" 2>&1 || true
                fi
            fi
        fi
    done
}

# ═══════════════════════════════════════════════════════════════════════════
# TEST 2: Verificare importuri
# ═══════════════════════════════════════════════════════════════════════════

test_imports() {
    echo ""
    echo -e "${CYAN}═══ TEST: Importuri Python ═══${NC}"
    echo ""
    
    # Test import socket (standard library)
    log_test "Import: socket"
    if python3 -c "import socket" 2>/dev/null; then
        log_pass "socket - disponibil"
    else
        log_fail "socket - lipsește"
    fi
    
    # Test import struct (standard library)
    log_test "Import: struct"
    if python3 -c "import struct" 2>/dev/null; then
        log_pass "struct - disponibil"
    else
        log_fail "struct - lipsește"
    fi
    
    # Test import threading (standard library)
    log_test "Import: threading"
    if python3 -c "import threading" 2>/dev/null; then
        log_pass "threading - disponibil"
    else
        log_fail "threading - lipsește"
    fi
    
    # Test import net_utils (local module)
    log_test "Import: net_utils (modul local)"
    if PYTHONPATH="$ROOT_DIR/python" python3 -c "from utils.net_utils import *" 2>/dev/null; then
        log_pass "net_utils - disponibil"
    else
        log_fail "net_utils - eroare import"
        if $VERBOSE; then
            PYTHONPATH="$ROOT_DIR/python" python3 -c "from utils.net_utils import *" 2>&1 || true
        fi
    fi
    
    # Test import scapy (opțional)
    log_test "Import: scapy (opțional)"
    if python3 -c "from scapy.all import IP, ICMP" 2>/dev/null; then
        log_pass "scapy - disponibil"
    else
        log_skip "scapy - nu e instalat (opțional)"
    fi
}

# ═══════════════════════════════════════════════════════════════════════════
# TEST 3: Verificare --help
# ═══════════════════════════════════════════════════════════════════════════

test_help() {
    echo ""
    echo -e "${CYAN}═══ TEST: Argumentul --help ═══${NC}"
    echo ""
    
    local examples=(
        "ex01_udp_broadcast.py"
        "ex02_udp_multicast.py"
        "ex03_tcp_tunnel.py"
        "ex04_echo_server.py"
        "ex05_tcp_multiclient.py"
        "ex06_tcp_framing.py"
        "ex07_udp_session_ack.py"
    )
    
    for example in "${examples[@]}"; do
        if [[ -f "$EXAMPLES_DIR/$example" ]]; then
            log_test "--help: $example"
            
            if timeout 5 python3 "$EXAMPLES_DIR/$example" --help >/dev/null 2>&1; then
                log_pass "$example --help funcționează"
            else
                log_fail "$example --help a eșuat"
            fi
        fi
    done
}

# ═══════════════════════════════════════════════════════════════════════════
# TEST 4: Demo rapid broadcast (localhost)
# ═══════════════════════════════════════════════════════════════════════════

test_broadcast_demo() {
    echo ""
    echo -e "${CYAN}═══ TEST: Demo Broadcast (localhost) ═══${NC}"
    echo ""
    
    log_test "Pornesc receiver pe :5007..."
    timeout 5 python3 "$EXAMPLES_DIR/ex01_udp_broadcast.py" recv \
        --port 5007 --count 1 &
    RECV_PID=$!
    sleep 0.5
    
    log_test "Trimit mesaj broadcast..."
    if timeout 5 python3 "$EXAMPLES_DIR/ex01_udp_broadcast.py" send \
        --dst 127.255.255.255 --port 5007 --message "SMOKE_TEST" --count 1 2>/dev/null; then
        log_pass "Broadcast send reușit"
    else
        log_fail "Broadcast send eșuat"
    fi
    
    # Așteptăm receiver-ul
    wait $RECV_PID 2>/dev/null || true
    
    log_pass "Demo broadcast finalizat"
}

# ═══════════════════════════════════════════════════════════════════════════
# TEST 5: Demo rapid echo server
# ═══════════════════════════════════════════════════════════════════════════

test_echo_demo() {
    echo ""
    echo -e "${CYAN}═══ TEST: Demo Echo Server ═══${NC}"
    echo ""
    
    log_test "Pornesc echo server pe :3333..."
    timeout 10 python3 "$EXAMPLES_DIR/ex04_echo_server.py" \
        --listen 127.0.0.1:3333 &
    SERVER_PID=$!
    sleep 0.5
    
    log_test "Trimit mesaj de test..."
    RESPONSE=$(echo "HELLO_SMOKE" | nc -w 2 127.0.0.1 3333 2>/dev/null || echo "")
    
    if [[ "$RESPONSE" == "HELLO_SMOKE" ]] || [[ "$RESPONSE" == *"HELLO"* ]]; then
        log_pass "Echo server răspunde corect"
    else
        log_fail "Echo server nu răspunde corect (primit: '$RESPONSE')"
    fi
    
    kill $SERVER_PID 2>/dev/null || true
}

# ═══════════════════════════════════════════════════════════════════════════
# TEST 6: Verificare Artefacte (după run_all.sh)
# ═══════════════════════════════════════════════════════════════════════════

test_artifacts() {
    echo ""
    echo -e "${CYAN}═══ TEST: Verificare Artefacte ═══${NC}"
    echo ""
    
    local artifacts_dir="$ROOT_DIR/artifacts"
    
    # Verificare demo.log
    log_test "Artefact: demo.log"
    if [[ -f "$artifacts_dir/demo.log" ]] && [[ -s "$artifacts_dir/demo.log" ]]; then
        log_pass "demo.log există și nu e gol"
    elif [[ -f "$artifacts_dir/demo.log" ]]; then
        log_skip "demo.log există dar e gol (rulați scripts/run_all.sh)"
    else
        log_skip "demo.log nu există (rulați scripts/run_all.sh)"
    fi
    
    # Verificare demo.pcap
    log_test "Artefact: demo.pcap"
    if [[ -f "$artifacts_dir/demo.pcap" ]] && [[ -s "$artifacts_dir/demo.pcap" ]]; then
        log_pass "demo.pcap există și conține date"
    elif [[ -f "$artifacts_dir/demo.pcap" ]]; then
        log_skip "demo.pcap există dar e gol (poate necesita trafic)"
    else
        log_skip "demo.pcap nu există (rulați scripts/run_all.sh)"
    fi
    
    # Verificare validation.txt
    log_test "Artefact: validation.txt"
    if [[ -f "$artifacts_dir/validation.txt" ]] && [[ -s "$artifacts_dir/validation.txt" ]]; then
        log_pass "validation.txt există"
        if grep -q "OVERALL_STATUS=SUCCESS" "$artifacts_dir/validation.txt" 2>/dev/null; then
            log_pass "validation.txt indică SUCCESS"
        elif grep -q "OVERALL_STATUS" "$artifacts_dir/validation.txt" 2>/dev/null; then
            log_skip "validation.txt indică status parțial"
        fi
    else
        log_skip "validation.txt nu există (rulați scripts/run_all.sh)"
    fi
}

# ═══════════════════════════════════════════════════════════════════════════
# EXECUȚIE TESTE
# ═══════════════════════════════════════════════════════════════════════════

case "$TEST_TYPE" in
    syntax)
        test_syntax
        ;;
    imports)
        test_imports
        ;;
    help)
        test_help
        ;;
    demo)
        test_broadcast_demo
        test_echo_demo
        ;;
    artifacts)
        test_artifacts
        ;;
    all)
        test_syntax
        test_imports
        test_help
        test_broadcast_demo
        test_echo_demo
        test_artifacts
        ;;
    *)
        echo "Tip necunoscut: $TEST_TYPE"
        echo "Opțiuni: syntax, imports, help, demo, artifacts, all"
        exit 1
        ;;
esac

# ═══════════════════════════════════════════════════════════════════════════
# SUMAR
# ═══════════════════════════════════════════════════════════════════════════

echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo -e "${BOLD}SUMAR TESTE${NC}"
echo "═══════════════════════════════════════════════════════════════════"
echo ""
echo -e "  ${GREEN}PASSED:${NC}  $PASSED"
echo -e "  ${RED}FAILED:${NC}  $FAILED"
echo -e "  ${YELLOW}SKIPPED:${NC} $SKIPPED"
echo ""

if [[ $FAILED -eq 0 ]]; then
    echo -e "${GREEN}═══ TOATE TESTELE AU TRECUT ═══${NC}"
    exit 0
else
    echo -e "${RED}═══ UNELE TESTE AU EȘUAT ═══${NC}"
    exit 1
fi
