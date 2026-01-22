#!/bin/bash
# smoke_test.sh — Teste rapide de mediu pentru Starterkit S14
# Rulare: bash tests/smoke_test.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

echo "=============================================="
echo "  Smoke Tests S14"
echo "=============================================="
echo ""

PASS=0
FAIL=0

# Funcție pentru test
test_check() {
    local name=$1
    local cmd=$2
    
    if eval "$cmd" > /dev/null 2>&1; then
        echo "  ✓ $name"
        PASS=$((PASS + 1))
    else
        echo "  ✗ $name"
        FAIL=$((FAIL + 1))
    fi
}

# Teste de existență fișiere
echo "[*] Verificare structură fișiere..."
test_check "README.md exists" "[ -f '$ROOT_DIR/README.md' ]"
test_check "Makefile exists" "[ -f '$ROOT_DIR/Makefile' ]"
test_check "requirements.txt exists" "[ -f '$ROOT_DIR/requirements.txt' ]"
test_check "setup.sh exists" "[ -f '$ROOT_DIR/scripts/setup.sh' ]"
test_check "run_all.sh exists" "[ -f '$ROOT_DIR/scripts/run_all.sh' ]"
test_check "cleanup.sh exists" "[ -f '$ROOT_DIR/scripts/cleanup.sh' ]"
test_check "topo_14_recap.py exists" "[ -f '$ROOT_DIR/mininet/topologies/topo_14_recap.py' ]"
test_check "backend_server.py exists" "[ -f '$ROOT_DIR/python/apps/backend_server.py' ]"
test_check "lb_proxy.py exists" "[ -f '$ROOT_DIR/python/apps/lb_proxy.py' ]"
test_check "run_demo.py exists" "[ -f '$ROOT_DIR/python/apps/run_demo.py' ]"
test_check "ex_14_03.py exists" "[ -f '$ROOT_DIR/python/exercises/ex_14_03.py' ]"
test_check "scenario_14_tasks.md exists" "[ -f '$ROOT_DIR/mininet/scenarios/scenario_14_tasks.md' ]"
test_check "sysctl.conf exists" "[ -f '$ROOT_DIR/configs/sysctl.conf' ]"

# Teste Python
echo ""
echo "[*] Verificare Python..."
test_check "Python 3 available" "command -v python3"
test_check "Python >= 3.8" "python3 -c 'import sys; exit(0 if sys.version_info >= (3,8) else 1)'"

# Teste dependențe sistem
echo ""
echo "[*] Verificare dependențe sistem..."
test_check "mininet (mn) available" "command -v mn"
test_check "ovs-vsctl available" "command -v ovs-vsctl"
test_check "tcpdump available" "command -v tcpdump"
test_check "ip available" "command -v ip"
test_check "ss available" "command -v ss"

# Teste opționale
echo ""
echo "[*] Verificare dependențe opționale..."
if command -v tshark > /dev/null 2>&1; then
    echo "  ✓ tshark available"
    PASS=$((PASS + 1))
else
    echo "  ○ tshark not available (optional)"
fi

if command -v curl > /dev/null 2>&1; then
    echo "  ✓ curl available"
    PASS=$((PASS + 1))
else
    echo "  ○ curl not available (optional)"
fi

# Test sintaxă Python
echo ""
echo "[*] Verificare sintaxă Python..."
for pyfile in "$ROOT_DIR"/python/apps/*.py; do
    if [ -f "$pyfile" ]; then
        name=$(basename "$pyfile")
        test_check "Syntax: $name" "python3 -m py_compile '$pyfile'"
    fi
done

# Test import Mininet (necesită root pentru unele funcții)
echo ""
echo "[*] Verificare import Mininet..."
if python3 -c "from mininet.topo import Topo; print('OK')" 2>/dev/null; then
    echo "  ✓ Mininet import OK"
    PASS=$((PASS + 1))
else
    echo "  ✗ Mininet import FAIL"
    FAIL=$((FAIL + 1))
fi

# Sumar
echo ""
echo "=============================================="
echo "  Rezultat: $PASS passed, $FAIL failed"
echo "=============================================="

if [ $FAIL -eq 0 ]; then
    echo ""
    echo "Toate testele au trecut! ✓"
    echo ""
    echo "Pași următori:"
    echo "  make run-demo    # rulează demo-ul complet"
    echo ""
    exit 0
else
    echo ""
    echo "Unele teste au eșuat. Rulează 'sudo bash scripts/setup.sh'"
    echo ""
    exit 1
fi
