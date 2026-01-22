#!/bin/bash
# run_all.sh — Rulează demo-ul complet S14 (Mininet + trafic + captură)
# Rulare: sudo bash scripts/run_all.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
ARTIFACTS_DIR="$ROOT_DIR/artifacts"

echo "=============================================="
echo "  Demo S14 - Rulare completă"
echo "=============================================="

# Verifică permisiuni
if [ "$EUID" -ne 0 ]; then
    echo "[!] Acest script trebuie rulat cu sudo"
    echo "    Utilizare: sudo bash scripts/run_all.sh"
    exit 1
fi

# Curăță eventuale rămășițe Mininet
echo "[*] Curățare Mininet anterioară..."
mn -c 2>/dev/null || true
pkill -f "backend_server.py" 2>/dev/null || true
pkill -f "lb_proxy.py" 2>/dev/null || true
pkill -f "tcp_echo_server.py" 2>/dev/null || true
pkill -f "run_demo.py" 2>/dev/null || true
sleep 1

# Verifică OVS
echo "[*] Verificare Open vSwitch..."
if ! systemctl is-active --quiet openvswitch-switch; then
    echo "    Pornire openvswitch-switch..."
    systemctl start openvswitch-switch
    sleep 2
fi

# Creează directorul de artefacte
echo "[*] Pregătire director artefacte: $ARTIFACTS_DIR"
mkdir -p "$ARTIFACTS_DIR"

# Rulează orchestratorul Python
echo "[*] Pornire orchestrator demo..."
echo ""

cd "$ROOT_DIR"
python3 python/apps/run_demo.py --artifacts "$ARTIFACTS_DIR"

# Afișează artefactele
echo ""
echo "=============================================="
echo "  Demo completat!"
echo "=============================================="
echo ""
echo "Artefacte generate în: $ARTIFACTS_DIR"
echo ""
ls -la "$ARTIFACTS_DIR/"
echo ""
echo "Comenzi utile pentru analiză:"
echo "  tshark -r $ARTIFACTS_DIR/demo.pcap -q -z conv,ip"
echo "  tshark -r $ARTIFACTS_DIR/demo.pcap -Y 'http.request'"
echo "  cat $ARTIFACTS_DIR/validation.txt"
echo "  cat $ARTIFACTS_DIR/report.json | python3 -m json.tool"
echo ""
