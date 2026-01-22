#!/bin/bash
# =============================================================================
# verify.sh - Verificare mediu Săptămâna 13
# =============================================================================
# Verificare rapidă a dependențelor necesare.
# Pentru verificare completă: ./tests/smoke_test.sh
# =============================================================================

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  Verificare Mediu - Starterkit S13                         ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Python
if python3 --version 2>/dev/null; then
    echo "[✓] Python3: $(python3 --version 2>&1)"
else
    echo "[✗] Python3: Nu este instalat"
fi

# Docker
if docker --version 2>/dev/null; then
    echo "[✓] Docker: disponibil"
else
    echo "[!] Docker: Nu este instalat (opțional)"
fi

# tcpdump/tshark
if command -v tcpdump &>/dev/null; then
    echo "[✓] tcpdump: disponibil"
elif command -v tshark &>/dev/null; then
    echo "[✓] tshark: disponibil"
else
    echo "[!] tcpdump/tshark: Nu sunt instalate"
fi

# Module Python
echo ""
echo "Module Python:"
for module in "paho.mqtt.client" "scapy.all" "requests" "socket" "json"; do
    if python3 -c "import ${module%%.*}" 2>/dev/null; then
        echo "  [✓] $module"
    else
        echo "  [!] $module: lipsă"
    fi
done

# Verificare artefacte
echo ""
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
if [ -d "$PROJECT_DIR/artifacts" ]; then
    echo "Artefacte demo:"
    [ -f "$PROJECT_DIR/artifacts/demo.log" ] && echo "  [✓] demo.log" || echo "  [!] demo.log (rulați run_all.sh)"
    [ -f "$PROJECT_DIR/artifacts/demo.pcap" ] && echo "  [✓] demo.pcap" || echo "  [!] demo.pcap"
    [ -f "$PROJECT_DIR/artifacts/validation.txt" ] && echo "  [✓] validation.txt" || echo "  [!] validation.txt"
else
    echo "[!] Director artifacts/ nu există (creat de run_all.sh)"
fi

echo ""
echo "Pentru verificare completă: ./tests/smoke_test.sh"
