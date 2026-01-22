#!/usr/bin/env bash
# =============================================================================
# smoke_test.sh - Test Rapid pentru Săptămâna 2
# =============================================================================
# Verifică existența și conținutul minimal al artefactelor generate de run_all.sh
#
# Artefacte verificate:
#   - artifacts/demo.log
#   - artifacts/demo.pcap
#   - artifacts/validation.txt
#
# Cod returnare:
#   0 = toate verificările au trecut
#   1 = una sau mai multe verificări au eșuat
# =============================================================================
# Rețele de Calculatoare - ASE București, CSIE
# Hypotheticalandrei & Rezolvix | MIT License
# =============================================================================

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
ARTIFACTS_DIR="$PROJECT_ROOT/artifacts"

# Culori
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Contoare
PASSED=0
FAILED=0
WARNED=0

# =============================================================================
# FUNCȚII DE TEST
# =============================================================================

check_file_exists() {
    local file="$1"
    local name="$2"
    if [[ -f "$file" ]]; then
        echo -e "${GREEN}[PASS]${NC} $name există"
        PASSED=$((PASSED + 1))
        return 0
    else
        echo -e "${RED}[FAIL]${NC} $name lipsă: $file"
        FAILED=$((FAILED + 1))
        return 1
    fi
}

check_file_not_empty() {
    local file="$1"
    local name="$2"
    if [[ -s "$file" ]]; then
        local size
        size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null || echo "?")
        echo -e "${GREEN}[PASS]${NC} $name nu este gol ($size bytes)"
        PASSED=$((PASSED + 1))
        return 0
    else
        echo -e "${YELLOW}[WARN]${NC} $name este gol"
        WARNED=$((WARNED + 1))
        return 1
    fi
}

check_file_contains() {
    local file="$1"
    local pattern="$2"
    local name="$3"
    if grep -q "$pattern" "$file" 2>/dev/null; then
        echo -e "${GREEN}[PASS]${NC} $name conține '$pattern'"
        PASSED=$((PASSED + 1))
        return 0
    else
        echo -e "${RED}[FAIL]${NC} $name nu conține '$pattern'"
        FAILED=$((FAILED + 1))
        return 1
    fi
}

check_min_lines() {
    local file="$1"
    local min_lines="$2"
    local name="$3"
    if [[ -f "$file" ]]; then
        local lines
        lines=$(wc -l < "$file" 2>/dev/null || echo "0")
        if [[ "$lines" -ge "$min_lines" ]]; then
            echo -e "${GREEN}[PASS]${NC} $name are $lines linii (min: $min_lines)"
            PASSED=$((PASSED + 1))
            return 0
        else
            echo -e "${RED}[FAIL]${NC} $name are doar $lines linii (necesar: $min_lines)"
            FAILED=$((FAILED + 1))
            return 1
        fi
    else
        echo -e "${RED}[FAIL]${NC} $name nu există pentru verificare linii"
        FAILED=$((FAILED + 1))
        return 1
    fi
}

# =============================================================================
# TESTE PRINCIPALE
# =============================================================================

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║       Smoke Test - Săptămâna 2: Socket Programming          ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "Verificare directoare..."
echo "  Artifacts: $ARTIFACTS_DIR"
echo ""

# Test 1: Verificare existență directorul artifacts
echo "─── Test 1: Directoare ───"
if [[ -d "$ARTIFACTS_DIR" ]]; then
    echo -e "${GREEN}[PASS]${NC} Directorul artifacts/ există"
    PASSED=$((PASSED + 1))
else
    echo -e "${RED}[FAIL]${NC} Directorul artifacts/ lipsă"
    FAILED=$((FAILED + 1))
    echo ""
    echo "Rulați mai întâi: ./scripts/run_all.sh"
    exit 1
fi

# Test 2: demo.log
echo ""
echo "─── Test 2: demo.log ───"
DEMO_LOG="$ARTIFACTS_DIR/demo.log"
check_file_exists "$DEMO_LOG" "demo.log"
check_file_not_empty "$DEMO_LOG" "demo.log"
check_min_lines "$DEMO_LOG" 10 "demo.log"
check_file_contains "$DEMO_LOG" "INFO" "demo.log"

# Test 3: demo.pcap
echo ""
echo "─── Test 3: demo.pcap ───"
DEMO_PCAP="$ARTIFACTS_DIR/demo.pcap"
check_file_exists "$DEMO_PCAP" "demo.pcap"

if [[ -f "$DEMO_PCAP" ]]; then
    # Verificare conținut pcap (dacă tshark disponibil)
    if command -v tshark &>/dev/null; then
        local_pkts=$(tshark -r "$DEMO_PCAP" 2>/dev/null | wc -l || echo "0")
        if [[ "$local_pkts" -gt 0 ]]; then
            echo -e "${GREEN}[PASS]${NC} demo.pcap conține $local_pkts pachete"
            PASSED=$((PASSED + 1))
        else
            echo -e "${YELLOW}[WARN]${NC} demo.pcap are 0 pachete (tcpdump nu a capturat?)"
            WARNED=$((WARNED + 1))
        fi
    else
        check_file_not_empty "$DEMO_PCAP" "demo.pcap (fără tshark)"
    fi
fi

# Test 4: validation.txt
echo ""
echo "─── Test 4: validation.txt ───"
VALIDATION_FILE="$ARTIFACTS_DIR/validation.txt"
check_file_exists "$VALIDATION_FILE" "validation.txt"
check_file_not_empty "$VALIDATION_FILE" "validation.txt"
check_file_contains "$VALIDATION_FILE" "REZULTAT" "validation.txt"

# Test 5: Verificări suplimentare (opționale)
echo ""
echo "─── Test 5: Verificări suplimentare ───"

# Verificare cod Python funcțional
if python3 -c "import socket; import threading" 2>/dev/null; then
    echo -e "${GREEN}[PASS]${NC} Module Python (socket, threading) disponibile"
    PASSED=$((PASSED + 1))
else
    echo -e "${RED}[FAIL]${NC} Module Python indisponibile"
    FAILED=$((FAILED + 1))
fi

# Verificare exerciții există
TCP_EX="$PROJECT_ROOT/seminar/python/exercises/ex_2_01_tcp.py"
UDP_EX="$PROJECT_ROOT/seminar/python/exercises/ex_2_02_udp.py"

if [[ -f "$TCP_EX" ]]; then
    echo -e "${GREEN}[PASS]${NC} Exercițiu TCP (ex_2_01_tcp.py) există"
    PASSED=$((PASSED + 1))
else
    echo -e "${RED}[FAIL]${NC} Exercițiu TCP lipsă"
    FAILED=$((FAILED + 1))
fi

if [[ -f "$UDP_EX" ]]; then
    echo -e "${GREEN}[PASS]${NC} Exercițiu UDP (ex_2_02_udp.py) există"
    PASSED=$((PASSED + 1))
else
    echo -e "${RED}[FAIL]${NC} Exercițiu UDP lipsă"
    FAILED=$((FAILED + 1))
fi

# =============================================================================
# RAPORT FINAL
# =============================================================================
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo " RAPORT SMOKE TEST"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo -e "  ${GREEN}Trecut:${NC}  $PASSED"
echo -e "  ${RED}Eșuat:${NC}   $FAILED"
echo -e "  ${YELLOW}Atenție:${NC} $WARNED"
echo ""

if [[ $FAILED -eq 0 ]]; then
    echo -e "${GREEN}══════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN} ✓ SMOKE TEST TRECUT                                         ${NC}"
    echo -e "${GREEN}══════════════════════════════════════════════════════════════${NC}"
    exit 0
else
    echo -e "${RED}══════════════════════════════════════════════════════════════${NC}"
    echo -e "${RED} ✗ SMOKE TEST EȘUAT ($FAILED verificări)                      ${NC}"
    echo -e "${RED}══════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo "Sugestii:"
    echo "  1. Rulați: ./scripts/run_all.sh"
    echo "  2. Verificați: ./scripts/setup.sh"
    echo "  3. Consultați: logs/*.log"
    exit 1
fi
