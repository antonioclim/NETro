#!/bin/bash
# =============================================================================
# capture.sh – Captură trafic pentru Săptămâna 11
# =============================================================================

GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'

PORT=${1:-8080}
COUNT=${2:-20}
OUTPUT="pcap/capture_$(date +%Y%m%d_%H%M%S).pcap"

echo -e "${GREEN}[CAPTURE]${NC} Captură trafic pe portul $PORT"
echo -e "${YELLOW}[INFO]${NC} Output: $OUTPUT"
echo -e "${YELLOW}[INFO]${NC} Pachete: $COUNT"
echo -e "${YELLOW}[INFO]${NC} Ctrl+C pentru a opri manual"
echo ""

mkdir -p pcap

if command -v tshark &> /dev/null; then
    sudo tshark -i any -f "tcp port $PORT" -c $COUNT -w "$OUTPUT" 2>/dev/null
    echo ""
    echo -e "${GREEN}[OK]${NC} Captură salvată în $OUTPUT"
    echo -e "${YELLOW}[INFO]${NC} Vizualizare: tshark -r $OUTPUT"
elif command -v tcpdump &> /dev/null; then
    sudo tcpdump -i any -n tcp port $PORT -c $COUNT -w "$OUTPUT" 2>/dev/null
    echo ""
    echo -e "${GREEN}[OK]${NC} Captură salvată în $OUTPUT"
else
    echo -e "${YELLOW}[!]${NC} Nici tshark, nici tcpdump nu sunt instalate."
    echo -e "${YELLOW}[INFO]${NC} Instalare: sudo apt-get install tshark"
fi

# Revolvix&Hypotheticalandrei
