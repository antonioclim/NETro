#!/bin/bash
# =============================================================================
# Smoke Test pentru Starterkit S9
# =============================================================================
# Verifică:
#   1. Exercițiu L6 (endianness)
#   2. Import pseudo-FTP
#   3. Utilitare comune (net_utils.py)
#   4. Artefacte generate (demo.log, demo.pcap, validation.txt)
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$ROOT_DIR"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

PASSED=0
FAILED=0

check() {
    local name="$1"
    local cmd="$2"
    
    if eval "$cmd" > /dev/null 2>&1; then
        echo -e "  ${GREEN}✓${NC} $name"
        ((PASSED++))
    else
        echo -e "  ${RED}✗${NC} $name"
        ((FAILED++))
    fi
}

echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║  Smoke Test – Starterkit S9                                      ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""

# Grup 1: Cod Python
echo "▶ Verificare cod Python:"
check "ex_9_01_endianness.py --selftest" \
    "python3 python/exercises/ex_9_01_endianness.py --selftest 2>&1 | grep -q 'Toate testele au trecut'"

check "Import ex_9_02_pseudo_ftp.py" \
    "python3 -c 'from python.exercises.ex_9_02_pseudo_ftp import pack_data, unpack_data'"

check "net_utils.py selftest" \
    "python3 python/utils/net_utils.py 2>&1 | grep -q 'Toate testele au trecut'"

echo ""

# Grup 2: Artefacte (după run_all.sh)
echo "▶ Verificare artefacte (după ./scripts/run_all.sh):"
if [ -d "artifacts" ]; then
    check "artifacts/demo.log există" "[ -f artifacts/demo.log ]"
    check "artifacts/demo.pcap există" "[ -f artifacts/demo.pcap ]"
    check "artifacts/validation.txt există" "[ -f artifacts/validation.txt ]"
    
    if [ -f "artifacts/demo.log" ]; then
        check "demo.log conține date" "[ -s artifacts/demo.log ]"
    fi
    
    if [ -f "artifacts/validation.txt" ]; then
        check "validation.txt conține PASS" "grep -q PASS artifacts/validation.txt"
    fi
else
    echo -e "  ${YELLOW}⚠${NC} Director artifacts/ nu există (rulați ./scripts/run_all.sh mai întâi)"
fi

echo ""

# Grup 3: Structură directoare
echo "▶ Verificare structură:"
check "scripts/ există" "[ -d scripts ]"
check "python/exercises/ există" "[ -d python/exercises ]"
check "python/utils/ există" "[ -d python/utils ]"
check "mininet/topologies/ există" "[ -d mininet/topologies ]"
check "tests/ există" "[ -d tests ]"
check "docs/ există" "[ -d docs ]"

echo ""

# Sumar
echo "══════════════════════════════════════════════════════════════════"
if [ $FAILED -eq 0 ]; then
    echo -e "  ${GREEN}Toate testele au trecut! ($PASSED/$((PASSED+FAILED)))${NC}"
else
    echo -e "  ${RED}$FAILED teste eșuate, $PASSED trecute${NC}"
fi
echo "══════════════════════════════════════════════════════════════════"

exit $FAILED
