#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════
# entrypoint.sh — Script de pornire pentru containerul S3
# ═══════════════════════════════════════════════════════════════════════════

set -e

echo ""
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║     STARTERKIT S3 — Socket Programming                          ║"
echo "║     Rețele de Calculatoare, ASE-CSIE                            ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""

# Pornește Open vSwitch dacă e disponibil (pentru Mininet)
if command -v ovs-vsctl &> /dev/null; then
    service openvswitch-switch start 2>/dev/null || true
fi

# Afișează informații despre rețea
echo "Informații rețea:"
echo "  IP:       $(hostname -I 2>/dev/null | awk '{print $1}' || echo 'N/A')"
echo "  Hostname: $(hostname)"
echo ""

# Afișează comenzi utile
echo "Comenzi utile:"
echo "  python3 python/examples/ex01_udp_broadcast.py --help"
echo "  python3 python/examples/ex02_udp_multicast.py --help"
echo "  python3 python/examples/ex03_tcp_tunnel.py --help"
echo "  bash scripts/run_all_demos.sh"
echo ""

# Execută comanda transmisă sau bash interactiv
exec "$@"
