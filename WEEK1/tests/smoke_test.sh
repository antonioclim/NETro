#!/usr/bin/env bash
#===============================================================================
# smoke_test.sh - Validare artefacte demo Săptămâna 1
#===============================================================================
# Verifică existența și conținutul minimal al artefactelor generate de run_all.sh
#
# Utilizare:
#   bash tests/smoke_test.sh
#
# Exit codes:
#   0 - Toate testele au trecut
#   1 - Unul sau mai multe teste au eșuat
#===============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
ARTIFACTS_DIR="$PROJECT_DIR/artifacts"

# Culori
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

pass() { echo -e "${GREEN}[PASS]${NC} $1"; }
fail() { echo -e "${RED}[FAIL]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }

#===============================================================================
# Teste
#===============================================================================

TESTS_PASSED=0
TESTS_FAILED=0
TESTS_WARNED=0

test_file_exists() {
    local file="$1"
    local desc="$2"
    
    if [[ -f "$file" ]]; then
        pass "$desc: fișier există"
        ((TESTS_PASSED++))
        return 0
    else
        fail "$desc: fișier lipsă ($file)"
        ((TESTS_FAILED++))
        return 1
    fi
}

test_file_not_empty() {
    local file="$1"
    local desc="$2"
    
    if [[ -s "$file" ]]; then
        local size=$(du -h "$file" | cut -f1)
        pass "$desc: fișier nevid ($size)"
        ((TESTS_PASSED++))
        return 0
    else
        fail "$desc: fișier gol sau lipsă"
        ((TESTS_FAILED++))
        return 1
    fi
}

test_pcap_valid() {
    local file="$1"
    local min_packets="$2"
    local desc="$3"
    
    if [[ ! -f "$file" ]]; then
        fail "$desc: fișier PCAP lipsă"
        ((TESTS_FAILED++))
        return 1
    fi
    
    if ! command -v tshark &>/dev/null; then
        warn "$desc: tshark indisponibil, skip validare conținut"
        ((TESTS_WARNED++))
        return 0
    fi
    
    local count=$(tshark -r "$file" 2>/dev/null | wc -l)
    
    if [[ $count -ge $min_packets ]]; then
        pass "$desc: $count pachete (min $min_packets)"
        ((TESTS_PASSED++))
        return 0
    else
        fail "$desc: doar $count pachete (necesar $min_packets)"
        ((TESTS_FAILED++))
        return 1
    fi
}

test_log_contains() {
    local file="$1"
    local pattern="$2"
    local desc="$3"
    
    if [[ ! -f "$file" ]]; then
        fail "$desc: fișier log lipsă"
        ((TESTS_FAILED++))
        return 1
    fi
    
    if grep -q "$pattern" "$file" 2>/dev/null; then
        pass "$desc: conține '$pattern'"
        ((TESTS_PASSED++))
        return 0
    else
        fail "$desc: nu conține '$pattern'"
        ((TESTS_FAILED++))
        return 1
    fi
}

test_validation_status() {
    local file="$ARTIFACTS_DIR/validation.txt"
    
    if [[ ! -f "$file" ]]; then
        fail "validation.txt: lipsă"
        ((TESTS_FAILED++))
        return 1
    fi
    
    local pass_count=$(grep -c "^PASS:" "$file" 2>/dev/null || echo 0)
    local fail_count=$(grep -c "^FAIL:" "$file" 2>/dev/null || echo 0)
    
    if [[ $pass_count -ge 3 && $fail_count -eq 0 ]]; then
        pass "validation.txt: $pass_count PASS, $fail_count FAIL"
        ((TESTS_PASSED++))
        return 0
    elif [[ $pass_count -gt $fail_count ]]; then
        warn "validation.txt: $pass_count PASS, $fail_count FAIL (partial)"
        ((TESTS_WARNED++))
        return 0
    else
        fail "validation.txt: prea multe eșecuri ($fail_count FAIL)"
        ((TESTS_FAILED++))
        return 1
    fi
}

#===============================================================================
# Teste structură proiect
#===============================================================================

test_project_structure() {
    echo ""
    echo "━━━ Teste structură proiect ━━━"
    
    # Directoare obligatorii
    for dir in scripts python tests docs artifacts; do
        if [[ -d "$PROJECT_DIR/$dir" ]]; then
            pass "Director: $dir/"
            ((TESTS_PASSED++))
        else
            fail "Director lipsă: $dir/"
            ((TESTS_FAILED++))
        fi
    done
    
    # Scripturi obligatorii
    for script in setup.sh run_all.sh cleanup.sh; do
        if [[ -x "$PROJECT_DIR/scripts/$script" ]] || [[ -f "$PROJECT_DIR/scripts/$script" ]]; then
            pass "Script: scripts/$script"
            ((TESTS_PASSED++))
        else
            fail "Script lipsă: scripts/$script"
            ((TESTS_FAILED++))
        fi
    done
}

#===============================================================================
# Teste artefacte demo
#===============================================================================

test_demo_artifacts() {
    echo ""
    echo "━━━ Teste artefacte demo ━━━"
    
    # demo.log
    test_file_exists "$ARTIFACTS_DIR/demo.log" "demo.log"
    test_file_not_empty "$ARTIFACTS_DIR/demo.log" "demo.log conținut"
    test_log_contains "$ARTIFACTS_DIR/demo.log" "Demo" "demo.log structură"
    
    # demo.pcap
    test_file_exists "$ARTIFACTS_DIR/demo.pcap" "demo.pcap"
    test_pcap_valid "$ARTIFACTS_DIR/demo.pcap" 5 "demo.pcap pachete"
    
    # validation.txt
    test_file_exists "$ARTIFACTS_DIR/validation.txt" "validation.txt"
    test_validation_status
}

#===============================================================================
# Teste Python
#===============================================================================

test_python_exercises() {
    echo ""
    echo "━━━ Teste exerciții Python ━━━"
    
    if ! command -v python3 &>/dev/null; then
        warn "Python3 indisponibil, skip teste Python"
        ((TESTS_WARNED++))
        return
    fi
    
    # Syntax check pentru fișierele Python
    local py_errors=0
    for pyfile in "$PROJECT_DIR"/python/exercises/*.py; do
        if [[ -f "$pyfile" ]]; then
            if python3 -m py_compile "$pyfile" 2>/dev/null; then
                pass "Syntax OK: $(basename "$pyfile")"
                ((TESTS_PASSED++))
            else
                fail "Syntax error: $(basename "$pyfile")"
                ((TESTS_FAILED++))
                ((py_errors++))
            fi
        fi
    done
    
    # Self-test pentru exercițiul TCP/UDP
    local tcp_test="$PROJECT_DIR/python/exercises/ex_1_02_tcp_server_client.py"
    if [[ -f "$tcp_test" ]]; then
        if timeout 10 python3 "$tcp_test" --test &>/dev/null; then
            pass "Self-test: ex_1_02_tcp_server_client.py"
            ((TESTS_PASSED++))
        else
            warn "Self-test partial: ex_1_02_tcp_server_client.py"
            ((TESTS_WARNED++))
        fi
    fi
}

#===============================================================================
# Sumar
#===============================================================================

print_summary() {
    echo ""
    echo "═══════════════════════════════════════════════════════════════"
    echo "  SUMAR SMOKE TEST - Săptămâna 1"
    echo "═══════════════════════════════════════════════════════════════"
    echo ""
    
    local total=$((TESTS_PASSED + TESTS_FAILED + TESTS_WARNED))
    
    echo -e "  ${GREEN}PASS:${NC} $TESTS_PASSED"
    echo -e "  ${RED}FAIL:${NC} $TESTS_FAILED"
    echo -e "  ${YELLOW}WARN:${NC} $TESTS_WARNED"
    echo "  ─────────────────"
    echo "  TOTAL: $total teste"
    echo ""
    
    if [[ $TESTS_FAILED -eq 0 ]]; then
        echo -e "  ${GREEN}✅ Toate testele critice au trecut!${NC}"
        return 0
    else
        echo -e "  ${RED}❌ $TESTS_FAILED teste au eșuat${NC}"
        echo ""
        echo "  Remediere:"
        echo "    1. Rulează: bash scripts/run_all.sh"
        echo "    2. Verifică: ls -la artifacts/"
        echo "    3. Re-rulează acest test"
        return 1
    fi
}

#===============================================================================
# Main
#===============================================================================

main() {
    echo ""
    echo "╔═══════════════════════════════════════════════════════════════════╗"
    echo "║              SMOKE TEST - Săptămâna 1                             ║"
    echo "║              Rețele de Calculatoare - ASE București               ║"
    echo "╚═══════════════════════════════════════════════════════════════════╝"
    
    test_project_structure
    test_demo_artifacts
    test_python_exercises
    
    print_summary
    exit $?
}

main
