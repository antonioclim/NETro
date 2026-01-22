#!/bin/bash
# =============================================================================
# capture.sh - Captură de pachete pentru Săptămâna 12
# Rețele de Calculatoare - ASE CSIE
# Autor: Revolvix&Hypotheticalandrei
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
PCAP_DIR="$PROJECT_DIR/pcap"

# Culori
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Configurări implicite
INTERFACE="lo"
DURATION=30
SMTP_PORT=1025
RPC_PORT=8080
XMLRPC_PORT=8000

usage() {
    echo -e "${BLUE}Utilizare:${NC} $0 [OPȚIUNE] [COMANDĂ]"
    echo ""
    echo -e "${CYAN}Comenzi:${NC}"
    echo "  smtp       Captură trafic SMTP (port $SMTP_PORT)"
    echo "  jsonrpc    Captură trafic JSON-RPC (port $RPC_PORT)"
    echo "  xmlrpc     Captură trafic XML-RPC (port $XMLRPC_PORT)"
    echo "  all        Captură tot traficul relevant"
    echo "  custom     Captură cu parametri personalizați"
    echo ""
    echo -e "${CYAN}Opțiuni:${NC}"
    echo "  -i IFACE   Interfață (implicit: $INTERFACE)"
    echo "  -d SEC     Durată în secunde (implicit: $DURATION)"
    echo "  -o FILE    Fișier output (implicit: auto-generat)"
    echo "  -p PORT    Port pentru captură custom"
    echo "  -v         Mod verbose (afișează pachete live)"
    echo "  -h         Afișează acest ajutor"
    echo ""
    echo -e "${CYAN}Exemple:${NC}"
    echo "  $0 smtp                    # Captură SMTP 30 secunde"
    echo "  $0 -d 60 jsonrpc           # Captură JSON-RPC 60 secunde"
    echo "  $0 -i eth0 all             # Captură pe eth0"
    echo "  $0 -p 5000 custom          # Captură port personalizat"
    echo ""
}

check_tools() {
    if ! command -v tcpdump &>/dev/null && ! command -v tshark &>/dev/null; then
        echo -e "${RED}Eroare: tcpdump sau tshark necesar!${NC}"
        echo "Instalați cu: sudo apt install tcpdump"
        exit 1
    fi
}

check_permissions() {
    if [[ $EUID -ne 0 ]] && ! groups | grep -qE "(pcap|wireshark)"; then
        echo -e "${YELLOW}Atenție: Poate fi necesar sudo pentru captură.${NC}"
        echo "Alternativ, adăugați utilizatorul în grupul 'pcap':"
        echo "  sudo usermod -a -G pcap \$USER"
        echo ""
    fi
}

generate_filename() {
    local type=$1
    local timestamp=$(date +%Y%m%d_%H%M%S)
    echo "${PCAP_DIR}/${type}_${timestamp}.pcap"
}

capture_with_tcpdump() {
    local port=$1
    local output=$2
    local filter="port $port"
    
    echo -e "${GREEN}Începe captura cu tcpdump...${NC}"
    echo -e "  Interfață: ${CYAN}$INTERFACE${NC}"
    echo -e "  Port: ${CYAN}$port${NC}"
    echo -e "  Durată: ${CYAN}${DURATION}s${NC}"
    echo -e "  Output: ${CYAN}$output${NC}"
    echo ""
    echo -e "${YELLOW}Apăsați Ctrl+C pentru oprire prematură${NC}"
    echo ""
    
    if [[ "$VERBOSE" == "1" ]]; then
        sudo timeout $DURATION tcpdump -i $INTERFACE -w "$output" -v "$filter" 2>&1 || true
    else
        sudo timeout $DURATION tcpdump -i $INTERFACE -w "$output" "$filter" 2>&1 || true
    fi
    
    echo ""
    echo -e "${GREEN}Captură completă: $output${NC}"
}

capture_with_tshark() {
    local port=$1
    local output=$2
    local filter="tcp port $port"
    
    echo -e "${GREEN}Începe captura cu tshark...${NC}"
    echo -e "  Interfață: ${CYAN}$INTERFACE${NC}"
    echo -e "  Port: ${CYAN}$port${NC}"
    echo -e "  Durată: ${CYAN}${DURATION}s${NC}"
    echo -e "  Output: ${CYAN}$output${NC}"
    echo ""
    echo -e "${YELLOW}Apăsați Ctrl+C pentru oprire prematură${NC}"
    echo ""
    
    if [[ "$VERBOSE" == "1" ]]; then
        tshark -i $INTERFACE -a duration:$DURATION -w "$output" -f "$filter" 2>&1 || true
    else
        tshark -i $INTERFACE -a duration:$DURATION -w "$output" -f "$filter" -q 2>&1 || true
    fi
    
    echo ""
    echo -e "${GREEN}Captură completă: $output${NC}"
}

do_capture() {
    local port=$1
    local output=$2
    
    mkdir -p "$PCAP_DIR"
    
    if command -v tshark &>/dev/null; then
        capture_with_tshark $port "$output"
    else
        capture_with_tcpdump $port "$output"
    fi
    
    # Afișare statistici
    if [[ -f "$output" ]]; then
        local size=$(du -h "$output" | cut -f1)
        echo ""
        echo -e "${BLUE}━━━ Statistici captură ━━━${NC}"
        echo -e "  Dimensiune: ${CYAN}$size${NC}"
        
        if command -v tshark &>/dev/null; then
            local packets=$(tshark -r "$output" 2>/dev/null | wc -l)
            echo -e "  Pachete: ${CYAN}$packets${NC}"
        fi
        
        echo ""
        echo -e "${CYAN}Pentru analiză:${NC}"
        echo "  tshark -r $output"
        echo "  wireshark $output"
    fi
}

analyze_capture() {
    local file=$1
    
    if [[ ! -f "$file" ]]; then
        echo -e "${RED}Fișier inexistent: $file${NC}"
        exit 1
    fi
    
    echo -e "${BLUE}━━━ Analiză captură: $file ━━━${NC}"
    echo ""
    
    if command -v tshark &>/dev/null; then
        echo -e "${CYAN}Sumar protocol:${NC}"
        tshark -r "$file" -q -z io,phs 2>/dev/null || true
        
        echo ""
        echo -e "${CYAN}Conversații TCP:${NC}"
        tshark -r "$file" -q -z conv,tcp 2>/dev/null | head -20 || true
        
        echo ""
        echo -e "${CYAN}Primele 10 pachete:${NC}"
        tshark -r "$file" 2>/dev/null | head -10 || true
    else
        echo "tshark necesar pentru analiză detaliată"
        tcpdump -r "$file" -n | head -20
    fi
}

# Parse opțiuni
VERBOSE=0
OUTPUT_FILE=""
CUSTOM_PORT=""

while getopts "i:d:o:p:vh" opt; do
    case $opt in
        i) INTERFACE="$OPTARG" ;;
        d) DURATION="$OPTARG" ;;
        o) OUTPUT_FILE="$OPTARG" ;;
        p) CUSTOM_PORT="$OPTARG" ;;
        v) VERBOSE=1 ;;
        h) usage; exit 0 ;;
        *) usage; exit 1 ;;
    esac
done

shift $((OPTIND-1))
COMMAND="${1:-help}"

# Main
check_tools
check_permissions

case "$COMMAND" in
    smtp)
        OUTPUT_FILE="${OUTPUT_FILE:-$(generate_filename smtp)}"
        do_capture $SMTP_PORT "$OUTPUT_FILE"
        ;;
    jsonrpc)
        OUTPUT_FILE="${OUTPUT_FILE:-$(generate_filename jsonrpc)}"
        do_capture $RPC_PORT "$OUTPUT_FILE"
        ;;
    xmlrpc)
        OUTPUT_FILE="${OUTPUT_FILE:-$(generate_filename xmlrpc)}"
        do_capture $XMLRPC_PORT "$OUTPUT_FILE"
        ;;
    all)
        echo -e "${BLUE}Captură multiplă (SMTP + JSON-RPC + XML-RPC)${NC}"
        echo -e "${YELLOW}Notă: Pentru captură simultană, folosiți un filtru combinat${NC}"
        
        OUTPUT_FILE="${OUTPUT_FILE:-$(generate_filename all)}"
        FILTER="port $SMTP_PORT or port $RPC_PORT or port $XMLRPC_PORT"
        
        mkdir -p "$PCAP_DIR"
        
        echo -e "${GREEN}Captură: $FILTER${NC}"
        if command -v tshark &>/dev/null; then
            tshark -i $INTERFACE -a duration:$DURATION -w "$OUTPUT_FILE" -f "($FILTER)" 2>&1 || true
        else
            sudo timeout $DURATION tcpdump -i $INTERFACE -w "$OUTPUT_FILE" "($FILTER)" 2>&1 || true
        fi
        
        echo -e "${GREEN}Captură completă: $OUTPUT_FILE${NC}"
        ;;
    custom)
        if [[ -z "$CUSTOM_PORT" ]]; then
            echo -e "${RED}Specificați portul cu -p PORT${NC}"
            exit 1
        fi
        OUTPUT_FILE="${OUTPUT_FILE:-$(generate_filename custom_${CUSTOM_PORT})}"
        do_capture $CUSTOM_PORT "$OUTPUT_FILE"
        ;;
    analyze)
        if [[ -z "$2" ]]; then
            echo -e "${RED}Specificați fișierul pentru analiză${NC}"
            echo "Utilizare: $0 analyze <fisier.pcap>"
            exit 1
        fi
        analyze_capture "$2"
        ;;
    list)
        echo -e "${BLUE}Capturi disponibile în $PCAP_DIR:${NC}"
        ls -lh "$PCAP_DIR"/*.pcap 2>/dev/null || echo "  (nicio captură)"
        ;;
    help|*)
        usage
        ;;
esac
