#!/bin/bash
# capture.sh — Pornește captură tcpdump standalone
# Rulare: sudo bash scripts/capture.sh [output.pcap] [interface]

OUTPUT="${1:-capture.pcap}"
INTERFACE="${2:-any}"

echo "=============================================="
echo "  Captură tcpdump"
echo "=============================================="
echo ""
echo "Output: $OUTPUT"
echo "Interface: $INTERFACE"
echo ""
echo "Oprire: Ctrl+C"
echo ""

sudo tcpdump -i "$INTERFACE" -w "$OUTPUT" -v

echo ""
echo "Captură salvată în: $OUTPUT"
echo ""
echo "Analiză:"
echo "  tshark -r $OUTPUT -q -z conv,ip"
echo "  tshark -r $OUTPUT -Y 'http.request'"
echo ""
