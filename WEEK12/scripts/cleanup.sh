#!/usr/bin/env bash
# =============================================================================
# cleanup.sh — Curățare completă pentru Săptămâna 12
# =============================================================================
# Oprește toate procesele, șterge fișierele temporare și resetează mediul.
#
# Utilizare: ./scripts/cleanup.sh [--full]
#   --full: Șterge și artefactele (demo.log, demo.pcap, etc.)
# =============================================================================
# Licență: MIT | ASE-CSIE Rețele de Calculatoare
# Hypotheticalandrei & Rezolvix
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

# Culori
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info()    { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_done()    { echo -e "${GREEN}[DONE]${NC} $1"; }

FULL_CLEANUP=false

# Parse arguments
while [ $# -gt 0 ]; do
    case "$1" in
        --full) FULL_CLEANUP=true ;;
        --help|-h)
            echo "Usage: $0 [--full]"
            echo ""
            echo "Options:"
            echo "  --full    Remove artifacts as well"
            echo ""
            exit 0
            ;;
    esac
    shift
done

echo "============================================"
echo "CLEANUP - Săptămâna 12: Email & RPC"
echo "============================================"
echo ""

# --- Oprire procese Python ---
log_info "Oprire procese server..."

pkill -f "smtp_server.py" 2>/dev/null && log_info "  Oprit: smtp_server" || true
pkill -f "smtp_client.py" 2>/dev/null && log_info "  Oprit: smtp_client" || true
pkill -f "jsonrpc_server.py" 2>/dev/null && log_info "  Oprit: jsonrpc_server" || true
pkill -f "jsonrpc_client.py" 2>/dev/null && log_info "  Oprit: jsonrpc_client" || true
pkill -f "xmlrpc_server.py" 2>/dev/null && log_info "  Oprit: xmlrpc_server" || true
pkill -f "xmlrpc_client.py" 2>/dev/null && log_info "  Oprit: xmlrpc_client" || true
pkill -f "grpc_server.py" 2>/dev/null && log_info "  Oprit: grpc_server" || true
pkill -f "ex_01_smtp.py" 2>/dev/null && log_info "  Oprit: ex_01_smtp" || true
pkill -f "ex_02_rpc.py" 2>/dev/null && log_info "  Oprit: ex_02_rpc" || true

# Oprire tcpdump
pkill -f "tcpdump.*demo.pcap" 2>/dev/null && log_info "  Oprit: tcpdump" || true

# --- Oprire Mininet (dacă rulează) ---
if command -v mn &>/dev/null; then
    log_info "Cleanup Mininet..."
    sudo mn -c 2>/dev/null || true
fi

# --- Curățare fișiere temporare ---
log_info "Curățare fișiere temporare..."

# Directoare temporare
rm -rf tmp/ 2>/dev/null && log_info "  Șters: tmp/" || true
rm -rf logs/ 2>/dev/null && log_info "  Șters: logs/" || true
rm -rf spool/ 2>/dev/null && log_info "  Șters: spool/" || true
rm -rf __pycache__/ 2>/dev/null || true
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true

# Fișiere .eml din spool
rm -f artifacts/spool/*.eml 2>/dev/null && log_info "  Șters: artifacts/spool/*.eml" || true

# --- Curățare Docker (opțional) ---
if command -v docker &>/dev/null; then
    log_info "Cleanup containere Docker (s12_*)..."
    docker ps -aq --filter "name=s12_" | xargs -r docker stop 2>/dev/null || true
    docker ps -aq --filter "name=s12_" | xargs -r docker rm 2>/dev/null || true
fi

# --- Curățare artefacte (doar cu --full) ---
if [ "$FULL_CLEANUP" = true ]; then
    log_warning "Curățare completă (inclusiv artefacte)..."
    rm -rf artifacts/*.log 2>/dev/null && log_info "  Șters: artifacts/*.log" || true
    rm -rf artifacts/*.pcap 2>/dev/null && log_info "  Șters: artifacts/*.pcap" || true
    rm -rf artifacts/*.txt 2>/dev/null && log_info "  Șters: artifacts/*.txt" || true
    rm -rf artifacts/spool/ 2>/dev/null && log_info "  Șters: artifacts/spool/" || true
fi

# --- Eliberare porturi ---
log_info "Verificare porturi..."

PORTS_TO_CHECK="1025 6200 6201 8000 8001 8080 50051"
for port in $PORTS_TO_CHECK; do
    if lsof -i ":$port" &>/dev/null; then
        log_warning "Port $port încă ocupat"
        lsof -i ":$port" 2>/dev/null | head -3
    fi
done

echo ""
log_done "Cleanup complet!"
echo ""
echo "Pentru a rula din nou demonstrațiile:"
echo "  ./scripts/run_all.sh"
echo ""
