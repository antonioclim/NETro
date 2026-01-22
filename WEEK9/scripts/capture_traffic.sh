#!/bin/bash
# Captură trafic pentru Starterkit S9

PORT=${1:-3333}
OUTPUT=${2:-"pcap/capture_$(date +%Y%m%d_%H%M%S).pcap"}

echo "Captură trafic pe port $PORT"
echo "Output: $OUTPUT"
echo "Ctrl+C pentru oprire"

sudo tcpdump -i any "tcp port $PORT" -w "$OUTPUT"
echo "✓ Captură salvată în $OUTPUT"
