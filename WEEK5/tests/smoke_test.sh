#!/usr/bin/env bash
#===============================================================================
# smoke_test.sh — Test rapid de funcționalitate
#===============================================================================
# Verifică că toate componentele principale funcționează.
# Validează artefactele generate de run_all.sh
# Exit code: 0 = succes, non-zero = eșec
#
# Utilizare: ./tests/smoke_test.sh [--with-artifacts]
#
# © 2025 ASE-CSIE | Rezolvix&Hypotheticalandrei | Licență MIT
#===============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
ARTIFACTS_DIR="$PROJECT_ROOT/artifacts"

# Configurare Week 5
WEEK=5
NETWORK_BASE="10.0.${WEEK}"
WEEK_PORT_BASE=$((5100 + 100 * (WEEK - 1)))

# Culori
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PASS=0
FAIL=0
SKIP=0

test_pass() {
    echo -e "${GREEN}[PASS]${NC} $1"
    ((PASS++))
}

test_fail() {
    echo -e "${RED}[FAIL]${NC} $1"
    ((FAIL++))
}

test_skip() {
    echo -e "${YELLOW}[SKIP]${NC} $1"
    ((SKIP++))
}

#-------------------------------------------------------------------------------
# Teste Python
#-------------------------------------------------------------------------------

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "              SMOKE TEST — Starterkit Săptămâna 5"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Test 1: Python disponibil
echo "Test 1: Python instalat"
if command -v python3 &> /dev/null; then
    test_pass "Python3 $(python3 --version 2>&1 | awk '{print $2}')"
else
    test_fail "Python3 nu este instalat"
fi

# Test 2: Modul ipaddress
echo "Test 2: Modul ipaddress"
if python3 -c "import ipaddress; ipaddress.ip_network('192.168.1.0/24')" 2>/dev/null; then
    test_pass "Modulul ipaddress funcțional"
else
    test_fail "Modulul ipaddress nu funcționează"
fi

# Test 3: ex_5_01 CIDR analyze
echo "Test 3: CIDR analyze (ex_5_01)"
cd "$PROJECT_ROOT/python/exercises"
if python3 ex_5_01_cidr_flsm.py analyze 192.168.1.100/24 --json 2>/dev/null | grep -q '"network"'; then
    test_pass "CIDR analyze produce output valid"
else
    test_fail "CIDR analyze nu funcționează"
fi

# Test 4: ex_5_01 FLSM
echo "Test 4: FLSM split (ex_5_01)"
if python3 ex_5_01_cidr_flsm.py flsm 10.0.0.0/8 4 2>/dev/null | grep -q "10.0.0.0/10"; then
    test_pass "FLSM produce subrețele corecte"
else
    test_fail "FLSM nu funcționează corect"
fi

# Test 5: ex_5_02 VLSM
echo "Test 5: VLSM allocate (ex_5_02)"
if python3 ex_5_02_vlsm_ipv6.py vlsm 192.168.0.0/24 100 50 2>/dev/null | grep -q "192.168.0"; then
    test_pass "VLSM produce alocare"
else
    test_fail "VLSM nu funcționează"
fi

# Test 6: ex_5_02 IPv6 compress
echo "Test 6: IPv6 compress (ex_5_02)"
result=$(python3 ex_5_02_vlsm_ipv6.py ipv6 2001:0db8:0000:0000:0000:0000:0000:0001 2>/dev/null | grep -o "2001:db8::1" || echo "")
if [[ "$result" == "2001:db8::1" ]]; then
    test_pass "IPv6 comprimare corectă"
else
    test_fail "IPv6 comprimare incorectă (așteptat: 2001:db8::1)"
fi

# Test 7: ex_5_03 Quiz generator (import)
echo "Test 7: Quiz generator import"
if python3 -c "import ex_5_03_quiz_generator" 2>/dev/null; then
    test_pass "Quiz generator importabil"
else
    test_fail "Quiz generator erori import"
fi

# Test 8: net_utils library
echo "Test 8: net_utils library"
cd "$PROJECT_ROOT/python/utils"
if python3 -c "from net_utils import analyze_ipv4_interface; print(analyze_ipv4_interface('10.0.0.1/24'))" 2>/dev/null | grep -q "network_address"; then
    test_pass "net_utils funcțional"
else
    test_fail "net_utils nu funcționează"
fi

cd "$PROJECT_ROOT"

# Test 9: Mininet topologii (syntax only)
echo "Test 9: Mininet topologii sintaxă"
if python3 -m py_compile mininet/topologies/topo_5_base.py 2>/dev/null && \
   python3 -m py_compile mininet/topologies/topo_5_extended.py 2>/dev/null; then
    test_pass "Topologii Mininet - sintaxă validă"
else
    test_fail "Topologii Mininet - erori sintaxă"
fi

# Test 10: Mininet disponibil (opțional)
echo "Test 10: Mininet disponibil"
if command -v mn &> /dev/null; then
    test_pass "Mininet instalat"
else
    test_skip "Mininet nu este instalat (necesită VM Linux)"
fi

#-------------------------------------------------------------------------------
# Teste Artefacte (dacă există)
#-------------------------------------------------------------------------------

validate_artifacts() {
    echo ""
    echo "═══════════════════════════════════════════════════════════════"
    echo "              VALIDARE ARTEFACTE"
    echo "═══════════════════════════════════════════════════════════════"
    echo ""
    
    # Test 11: demo.log
    echo "Test 11: Artefact demo.log"
    if [[ -f "$ARTIFACTS_DIR/demo.log" ]]; then
        local log_size
        log_size=$(stat -f%z "$ARTIFACTS_DIR/demo.log" 2>/dev/null || stat -c%s "$ARTIFACTS_DIR/demo.log" 2>/dev/null || echo "0")
        if [[ "$log_size" -gt 100 ]]; then
            test_pass "demo.log există ($log_size bytes)"
        else
            test_fail "demo.log prea mic ($log_size bytes)"
        fi
    else
        test_skip "demo.log nu există (rulați scripts/run_all.sh)"
    fi
    
    # Test 12: demo.pcap
    echo "Test 12: Artefact demo.pcap"
    if [[ -f "$ARTIFACTS_DIR/demo.pcap" ]]; then
        local pcap_size
        pcap_size=$(stat -f%z "$ARTIFACTS_DIR/demo.pcap" 2>/dev/null || stat -c%s "$ARTIFACTS_DIR/demo.pcap" 2>/dev/null || echo "0")
        if [[ "$pcap_size" -gt 24 ]]; then
            # Verificăm magic number PCAP
            local magic
            magic=$(xxd -l 4 -p "$ARTIFACTS_DIR/demo.pcap" 2>/dev/null || echo "")
            if [[ "$magic" == "d4c3b2a1" ]] || [[ "$magic" == "a1b2c3d4" ]]; then
                test_pass "demo.pcap valid ($pcap_size bytes, PCAP format)"
            else
                test_pass "demo.pcap există ($pcap_size bytes)"
            fi
        else
            test_fail "demo.pcap prea mic ($pcap_size bytes)"
        fi
    else
        test_skip "demo.pcap nu există (rulați scripts/run_all.sh)"
    fi
    
    # Test 13: validation.txt
    echo "Test 13: Artefact validation.txt"
    if [[ -f "$ARTIFACTS_DIR/validation.txt" ]]; then
        if grep -q "CONCLUZIE" "$ARTIFACTS_DIR/validation.txt" 2>/dev/null; then
            test_pass "validation.txt complet"
        else
            test_fail "validation.txt incomplet"
        fi
    else
        test_skip "validation.txt nu există (rulați scripts/run_all.sh)"
    fi
    
    # Test 14: Conținut validation.txt
    echo "Test 14: Verificări OK în validation.txt"
    if [[ -f "$ARTIFACTS_DIR/validation.txt" ]]; then
        local ok_count fail_count
        ok_count=$(grep -c "^\[OK\]" "$ARTIFACTS_DIR/validation.txt" 2>/dev/null || echo "0")
        fail_count=$(grep -c "^\[FAIL\]" "$ARTIFACTS_DIR/validation.txt" 2>/dev/null || echo "0")
        
        if [[ "$ok_count" -ge 5 ]] && [[ "$fail_count" -eq 0 ]]; then
            test_pass "Toate verificările OK ($ok_count verificări, 0 eșecuri)"
        elif [[ "$fail_count" -gt 0 ]]; then
            test_fail "Există $fail_count verificări eșuate"
        else
            test_skip "Insuficiente verificări ($ok_count)"
        fi
    else
        test_skip "validation.txt nu există"
    fi
}

#-------------------------------------------------------------------------------
# Sumar
#-------------------------------------------------------------------------------

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "                      REZULTATE TESTE"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo -e "  ${GREEN}Trecute:${NC}  $PASS"
echo -e "  ${RED}Eșuate:${NC}   $FAIL"
echo -e "  ${YELLOW}Omise:${NC}    $SKIP"
echo ""

# Validare artefacte dacă cerut sau dacă există
if [[ "${1:-}" == "--with-artifacts" ]] || [[ -d "$ARTIFACTS_DIR" ]]; then
    validate_artifacts
    
    echo ""
    echo "═══════════════════════════════════════════════════════════════"
    echo "                      REZULTATE FINALE"
    echo "═══════════════════════════════════════════════════════════════"
    echo ""
    echo -e "  ${GREEN}Trecute:${NC}  $PASS"
    echo -e "  ${RED}Eșuate:${NC}   $FAIL"
    echo -e "  ${YELLOW}Omise:${NC}    $SKIP"
    echo ""
fi

if [[ $FAIL -eq 0 ]]; then
    echo -e "${GREEN}✓ Toate testele au trecut!${NC}"
    exit 0
else
    echo -e "${RED}✗ $FAIL teste eșuate${NC}"
    exit 1
fi
