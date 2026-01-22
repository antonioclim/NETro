#!/usr/bin/env bash
# =============================================================================
# cleanup.sh - Wrapper pentru curățare standard (WEEK 2)
# =============================================================================
# Acest script este un wrapper pentru compatibilitate cu standardul transversal.
# Logica principală este în clean.sh
# =============================================================================
# Rețele de Calculatoare - ASE București, CSIE
# Hypotheticalandrei & Rezolvix | MIT License
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Culori
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║       Cleanup - Săptămâna 2: Socket Programming             ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# =============================================================================
# CURĂȚARE PROCESE
# =============================================================================
echo "[INFO] Oprire procese demo..."

# Oprire servere TCP/UDP
pkill -f "ex_2_01_tcp.py" 2>/dev/null && echo "  ✓ Server TCP oprit" || true
pkill -f "ex_2_02_udp.py" 2>/dev/null && echo "  ✓ Server UDP oprit" || true

# Oprire capturi tcpdump
sudo pkill -f "tcpdump.*port.*909" 2>/dev/null && echo "  ✓ tcpdump oprit" || true

# =============================================================================
# CURĂȚARE MININET
# =============================================================================
echo "[INFO] Curățare Mininet..."
if command -v mn &>/dev/null; then
    sudo mn -c 2>/dev/null && echo "  ✓ Mininet curățat" || true
else
    echo "  - Mininet nu este instalat"
fi

# =============================================================================
# CURĂȚARE ARTIFACTS (OPȚIONAL)
# =============================================================================
if [[ "${1:-}" == "--full" ]]; then
    echo "[INFO] Curățare completă (inclusiv artefacte)..."
    rm -rf "$PROJECT_ROOT/artifacts/"*.log 2>/dev/null || true
    rm -rf "$PROJECT_ROOT/artifacts/"*.pcap 2>/dev/null || true
    rm -rf "$PROJECT_ROOT/artifacts/"*.txt 2>/dev/null || true
    rm -rf "$PROJECT_ROOT/logs/"*.log 2>/dev/null || true
    echo "  ✓ Artefacte șterse"
fi

# =============================================================================
# CURĂȚARE PYCACHE
# =============================================================================
echo "[INFO] Curățare __pycache__..."
find "$PROJECT_ROOT" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find "$PROJECT_ROOT" -name "*.pyc" -delete 2>/dev/null || true
echo "  ✓ Cache Python curățat"

# =============================================================================
# RAPORT
# =============================================================================
echo ""
echo "════════════════════════════════════════════════════════════════"
echo " Cleanup complet!"
echo ""
echo " Pentru curățare completă (inclusiv artefacte):"
echo "   ./scripts/cleanup.sh --full"
echo ""
echo " Pentru verificare status porturi:"
echo "   ss -tuln | grep -E '909[01]|8080|9999'"
echo "════════════════════════════════════════════════════════════════"
