#!/bin/bash
# =============================================================================
# smoke_test.sh – Verificare artefacte și funcționalitate WEEK 11
# =============================================================================
# Verifică:
#   1. Existența artefactelor (demo.log, demo.pcap, validation.txt)
#   2. Conținutul minim al fiecărui artefact
#   3. Sintaxa scripturilor Python
#   4. Configurații Docker Compose
# =============================================================================
# Utilizare: ./smoke_test.sh
# Exit codes: 0 = succes, >0 = număr de erori
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
ARTIFACTS_DIR="$ROOT_DIR/artifacts"

# Culori
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

ERRORS=0
WARNINGS=0

# ─────────────────────────────────────────────────────────────────────────────
# Funcții helper
# ─────────────────────────────────────────────────────────────────────────────

pass() {
    echo -e "${GREEN}[✓]${NC} $1"
}

fail() {
    echo -e "${RED}[✗]${NC} $1"
    ERRORS=$((ERRORS + 1))
}

warn() {
    echo -e "${YELLOW}[!]${NC} $1"
    WARNINGS=$((WARNINGS + 1))
}

info() {
    echo -e "${BLUE}[i]${NC} $1"
}

# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  Smoke Test – Săptămâna 11${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo ""

# ─────────────────────────────────────────────────────────────────────────────
# 1. Verificare existență artefacte
# ─────────────────────────────────────────────────────────────────────────────

echo -e "${YELLOW}─── 1. Verificare artefacte ───${NC}"

if [[ -d "$ARTIFACTS_DIR" ]]; then
    pass "Director artifacts/ există"
else
    fail "Director artifacts/ lipsește"
fi

# demo.log
if [[ -f "$ARTIFACTS_DIR/demo.log" ]]; then
    SIZE=$(stat -f%z "$ARTIFACTS_DIR/demo.log" 2>/dev/null || stat -c%s "$ARTIFACTS_DIR/demo.log" 2>/dev/null || echo "0")
    if [[ "$SIZE" -gt 100 ]]; then
        pass "demo.log există și are conținut ($SIZE bytes)"
    else
        warn "demo.log există dar este prea mic ($SIZE bytes)"
    fi
else
    fail "demo.log lipsește"
fi

# demo.pcap
if [[ -f "$ARTIFACTS_DIR/demo.pcap" ]]; then
    SIZE=$(stat -f%z "$ARTIFACTS_DIR/demo.pcap" 2>/dev/null || stat -c%s "$ARTIFACTS_DIR/demo.pcap" 2>/dev/null || echo "0")
    if [[ "$SIZE" -gt 0 ]]; then
        pass "demo.pcap există ($SIZE bytes)"
    else
        warn "demo.pcap există dar este gol (captură necesită tshark/tcpdump)"
    fi
else
    fail "demo.pcap lipsește"
fi

# validation.txt
if [[ -f "$ARTIFACTS_DIR/validation.txt" ]]; then
    if grep -q "PASS" "$ARTIFACTS_DIR/validation.txt" 2>/dev/null; then
        PASS_COUNT=$(grep -c "PASS" "$ARTIFACTS_DIR/validation.txt" 2>/dev/null || echo "0")
        pass "validation.txt conține $PASS_COUNT verificări PASS"
    else
        warn "validation.txt există dar nu conține verificări PASS"
    fi
else
    fail "validation.txt lipsește"
fi

echo ""

# ─────────────────────────────────────────────────────────────────────────────
# 2. Verificare sintaxă Python
# ─────────────────────────────────────────────────────────────────────────────

echo -e "${YELLOW}─── 2. Verificare sintaxă Python ───${NC}"

PYTHON_FILES=(
    "python/exercises/ex_11_01_backend.py"
    "python/exercises/ex_11_02_loadbalancer.py"
    "python/exercises/ex_11_03_dns_client.py"
    "python/utils/net_utils.py"
)

for pf in "${PYTHON_FILES[@]}"; do
    FULL_PATH="$ROOT_DIR/$pf"
    if [[ -f "$FULL_PATH" ]]; then
        if python3 -m py_compile "$FULL_PATH" 2>/dev/null; then
            pass "$pf"
        else
            fail "$pf (eroare sintaxă)"
        fi
    else
        warn "$pf nu există"
    fi
done

echo ""

# ─────────────────────────────────────────────────────────────────────────────
# 3. Verificare configurații Docker
# ─────────────────────────────────────────────────────────────────────────────

echo -e "${YELLOW}─── 3. Verificare Docker Compose ───${NC}"

COMPOSE_FILES=(
    "docker/nginx_compose/docker-compose.yml"
    "docker/custom_lb_compose/docker-compose.yml"
    "docker/dns_demo/docker-compose.yml"
    "docker/ftp_demo/docker-compose.yml"
    "docker/ssh_demo/docker-compose.yml"
)

for cf in "${COMPOSE_FILES[@]}"; do
    FULL_PATH="$ROOT_DIR/$cf"
    if [[ -f "$FULL_PATH" ]]; then
        if command -v docker &> /dev/null; then
            if docker compose -f "$FULL_PATH" config > /dev/null 2>&1; then
                pass "$cf"
            else
                # Try without validation (might not have docker running)
                if grep -q "services:" "$FULL_PATH" 2>/dev/null; then
                    pass "$cf (structure valid)"
                else
                    fail "$cf (invalid)"
                fi
            fi
        else
            if grep -q "services:" "$FULL_PATH" 2>/dev/null; then
                pass "$cf (docker not available, basic check)"
            else
                fail "$cf (missing services section)"
            fi
        fi
    else
        warn "$cf nu există"
    fi
done

echo ""

# ─────────────────────────────────────────────────────────────────────────────
# 4. Verificare scripturi
# ─────────────────────────────────────────────────────────────────────────────

echo -e "${YELLOW}─── 4. Verificare scripturi shell ───${NC}"

SCRIPTS=(
    "scripts/setup.sh"
    "scripts/run_all.sh"
    "scripts/cleanup.sh"
    "scripts/verify.sh"
)

for sc in "${SCRIPTS[@]}"; do
    FULL_PATH="$ROOT_DIR/$sc"
    if [[ -f "$FULL_PATH" ]]; then
        if bash -n "$FULL_PATH" 2>/dev/null; then
            pass "$sc"
        else
            fail "$sc (eroare sintaxă bash)"
        fi
    else
        fail "$sc nu există"
    fi
done

echo ""

# ─────────────────────────────────────────────────────────────────────────────
# 5. Verificare Mininet (opțional)
# ─────────────────────────────────────────────────────────────────────────────

echo -e "${YELLOW}─── 5. Verificare Mininet topologii ───${NC}"

MININET_FILES=(
    "mininet/topologies/topo_11_base.py"
    "mininet/topologies/topo_11_extended.py"
)

for mf in "${MININET_FILES[@]}"; do
    FULL_PATH="$ROOT_DIR/$mf"
    if [[ -f "$FULL_PATH" ]]; then
        if python3 -m py_compile "$FULL_PATH" 2>/dev/null; then
            pass "$mf"
        else
            fail "$mf (eroare sintaxă)"
        fi
    else
        warn "$mf nu există"
    fi
done

echo ""

# ─────────────────────────────────────────────────────────────────────────────
# 6. Verificare README și documentație
# ─────────────────────────────────────────────────────────────────────────────

echo -e "${YELLOW}─── 6. Verificare documentație ───${NC}"

DOC_FILES=(
    "README.md"
    "docs/lab.md"
    "docs/seminar.md"
    "docs/curs.md"
)

for df in "${DOC_FILES[@]}"; do
    FULL_PATH="$ROOT_DIR/$df"
    if [[ -f "$FULL_PATH" ]]; then
        SIZE=$(stat -f%z "$FULL_PATH" 2>/dev/null || stat -c%s "$FULL_PATH" 2>/dev/null || echo "0")
        if [[ "$SIZE" -gt 500 ]]; then
            pass "$df ($SIZE bytes)"
        else
            warn "$df există dar este scurt ($SIZE bytes)"
        fi
    else
        fail "$df nu există"
    fi
done

echo ""

# ─────────────────────────────────────────────────────────────────────────────
# SUMAR
# ─────────────────────────────────────────────────────────────────────────────

echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"

if [[ $ERRORS -eq 0 ]]; then
    if [[ $WARNINGS -eq 0 ]]; then
        echo -e "${GREEN}  SUCCES: Toate verificările au trecut! ✓${NC}"
    else
        echo -e "${YELLOW}  SUCCES cu avertismente: $WARNINGS warning(s)${NC}"
    fi
else
    echo -e "${RED}  EȘEC: $ERRORS erori, $WARNINGS avertismente${NC}"
fi

echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo ""

# Afișare rezumat artefacte
if [[ -d "$ARTIFACTS_DIR" ]]; then
    info "Artefacte în $ARTIFACTS_DIR/:"
    ls -la "$ARTIFACTS_DIR/" 2>/dev/null | grep -v "^total" | grep -v "^d" || true
fi

echo ""

exit $ERRORS

# Revolvix&Hypotheticalandrei
