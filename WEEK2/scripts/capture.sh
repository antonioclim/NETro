#!/usr/bin/env bash
# =============================================================================
# capture.sh - Captură și analiză pachete pentru Săptămâna 2
# Rețele de Calculatoare - ASE București, CSIE
# =============================================================================
# Revolvix&Hypotheticalandrei
# =============================================================================

set -euo pipefail
IFS=$'\n\t'

# Culori pentru output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Directorul script-ului și proiect
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
CAPTURES_DIR="$PROJECT_ROOT/seminar/captures"
PCAP_DIR="$PROJECT_ROOT/pcap"

# Configurări implicite
DEFAULT_INTERFACE="lo"
DEFAULT_PORT="8080"
DEFAULT_DURATION="30"
DEFAULT_COUNT="100"

# =============================================================================
# Funcții utilitare
# =============================================================================

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[✓]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[!]${NC} $1"; }
log_error() { echo -e "${RED}[✗]${NC} $1"; }

usage() {
    cat << EOF
${CYAN}═══════════════════════════════════════════════════════════════${NC}
${CYAN}         capture.sh - Captură Pachete pentru S2               ${NC}
${CYAN}═══════════════════════════════════════════════════════════════${NC}

Utilizare: $0 <comandă> [opțiuni]

${BLUE}Comenzi disponibile:${NC}
  tcp           Captură trafic TCP pe interfață/port
  udp           Captură trafic UDP pe interfață/port
  handshake     Captură handshake TCP (SYN, SYN-ACK, ACK)
  analyze       Analizează un fișier .pcap existent
  stats         Afișează statistici din captură
  live          Captură live cu afișare în terminal
  clean         Șterge capturile vechi

${BLUE}Opțiuni:${NC}
  -i, --interface   Interfață de rețea (implicit: $DEFAULT_INTERFACE)
  -p, --port        Port de capturat (implicit: $DEFAULT_PORT)
  -d, --duration    Durată captură în secunde (implicit: $DEFAULT_DURATION)
  -c, --count       Număr maxim de pachete (implicit: $DEFAULT_COUNT)
  -o, --output      Fișier output .pcap
  -f, --file        Fișier input pentru analiză
  -h, --help        Afișează acest mesaj

${BLUE}Exemple:${NC}
  $0 tcp -p 8080 -d 60          # Captură TCP 60s pe port 8080
  $0 udp -p 9999 -c 50          # Captură 50 pachete UDP pe 9999
  $0 handshake -p 8080          # Captură doar handshake TCP
  $0 analyze -f capture.pcap    # Analiză pcap existent
  $0 stats -f capture.pcap      # Statistici din captură
  $0 live -p 8080               # Vizualizare live

EOF
    exit 0
}

check_privileges() {
    if [[ $EUID -ne 0 ]]; then
        log_error "Capturile necesită privilegii root"
        log_info "Rulați: sudo $0 $*"
        exit 1
    fi
}

check_tool() {
    local tool=$1
    if ! command -v "$tool" &> /dev/null; then
        log_error "$tool nu este instalat"
        case "$tool" in
            tshark) log_info "Instalare: sudo apt-get install tshark" ;;
            tcpdump) log_info "Instalare: sudo apt-get install tcpdump" ;;
        esac
        exit 1
    fi
}

ensure_dirs() {
    mkdir -p "$CAPTURES_DIR" "$PCAP_DIR"
}

generate_filename() {
    local prefix=$1
    local timestamp
    timestamp=$(date +%Y%m%d_%H%M%S)
    echo "${CAPTURES_DIR}/${prefix}_${timestamp}.pcap"
}

# =============================================================================
# Funcții de captură
# =============================================================================

capture_tcp() {
    local interface="${INTERFACE:-$DEFAULT_INTERFACE}"
    local port="${PORT:-$DEFAULT_PORT}"
    local duration="${DURATION:-$DEFAULT_DURATION}"
    local count="${COUNT:-$DEFAULT_COUNT}"
    local output="${OUTPUT:-$(generate_filename tcp_port${port})}"
    
    check_privileges
    check_tool tshark
    ensure_dirs
    
    log_info "Captură TCP pe $interface:$port"
    log_info "Durată: ${duration}s, Max pachete: $count"
    log_info "Output: $output"
    echo ""
    
    # Folosim tshark pentru captură
    timeout "$duration" tshark \
        -i "$interface" \
        -f "tcp port $port" \
        -c "$count" \
        -w "$output" \
        2>/dev/null || true
    
    if [[ -f "$output" ]]; then
        local pkt_count
        pkt_count=$(tshark -r "$output" 2>/dev/null | wc -l)
        log_success "Captură completă: $pkt_count pachete"
        log_info "Fișier salvat: $output"
        
        # Rezumat rapid
        echo ""
        log_info "Rezumat rapid:"
        tshark -r "$output" -q -z io,phs 2>/dev/null | head -20 || true
    else
        log_warning "Nu s-au capturat pachete (trafic inexistent pe $interface:$port)"
    fi
}

capture_udp() {
    local interface="${INTERFACE:-$DEFAULT_INTERFACE}"
    local port="${PORT:-$DEFAULT_PORT}"
    local duration="${DURATION:-$DEFAULT_DURATION}"
    local count="${COUNT:-$DEFAULT_COUNT}"
    local output="${OUTPUT:-$(generate_filename udp_port${port})}"
    
    check_privileges
    check_tool tshark
    ensure_dirs
    
    log_info "Captură UDP pe $interface:$port"
    log_info "Durată: ${duration}s, Max pachete: $count"
    log_info "Output: $output"
    echo ""
    
    timeout "$duration" tshark \
        -i "$interface" \
        -f "udp port $port" \
        -c "$count" \
        -w "$output" \
        2>/dev/null || true
    
    if [[ -f "$output" ]]; then
        local pkt_count
        pkt_count=$(tshark -r "$output" 2>/dev/null | wc -l)
        log_success "Captură completă: $pkt_count pachete"
        log_info "Fișier salvat: $output"
    else
        log_warning "Nu s-au capturat pachete UDP"
    fi
}

capture_handshake() {
    local interface="${INTERFACE:-$DEFAULT_INTERFACE}"
    local port="${PORT:-$DEFAULT_PORT}"
    local output="${OUTPUT:-$(generate_filename handshake_port${port})}"
    
    check_privileges
    check_tool tshark
    ensure_dirs
    
    log_info "Captură TCP Handshake pe $interface:$port"
    log_info "Aștept SYN, SYN-ACK, ACK..."
    log_info "Output: $output"
    echo ""
    
    # Filtrăm doar pachetele de handshake (SYN, SYN-ACK, ACK fără date)
    timeout 30 tshark \
        -i "$interface" \
        -f "tcp port $port" \
        -Y "tcp.flags.syn==1 || (tcp.flags.ack==1 && tcp.len==0)" \
        -c 10 \
        -w "$output" \
        2>/dev/null || true
    
    if [[ -f "$output" ]]; then
        log_success "Handshake capturat"
        echo ""
        log_info "Pachete capturate:"
        tshark -r "$output" -T fields \
            -e frame.number \
            -e ip.src \
            -e ip.dst \
            -e tcp.srcport \
            -e tcp.dstport \
            -e tcp.flags.syn \
            -e tcp.flags.ack \
            -E header=y \
            -E separator='|' \
            2>/dev/null || true
    else
        log_warning "Nu s-a capturat handshake"
    fi
}

analyze_pcap() {
    local input="${FILE:-}"
    
    if [[ -z "$input" ]]; then
        log_error "Specificați fișierul cu -f"
        exit 1
    fi
    
    if [[ ! -f "$input" ]]; then
        log_error "Fișierul nu există: $input"
        exit 1
    fi
    
    check_tool tshark
    
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}         Analiză: $(basename "$input")                         ${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
    
    log_info "Informații generale:"
    capinfos "$input" 2>/dev/null || tshark -r "$input" -q -z io,stat,0 2>/dev/null
    echo ""
    
    log_info "Primele 20 de pachete:"
    tshark -r "$input" -c 20 2>/dev/null
    echo ""
    
    log_info "Protocoale detectate:"
    tshark -r "$input" -q -z io,phs 2>/dev/null
}

show_stats() {
    local input="${FILE:-}"
    
    if [[ -z "$input" ]]; then
        log_error "Specificați fișierul cu -f"
        exit 1
    fi
    
    if [[ ! -f "$input" ]]; then
        log_error "Fișierul nu există: $input"
        exit 1
    fi
    
    check_tool tshark
    
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}         Statistici: $(basename "$input")                      ${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
    
    log_info "Conversații TCP:"
    tshark -r "$input" -q -z conv,tcp 2>/dev/null || echo "  Nu există conversații TCP"
    echo ""
    
    log_info "Conversații UDP:"
    tshark -r "$input" -q -z conv,udp 2>/dev/null || echo "  Nu există conversații UDP"
    echo ""
    
    log_info "Distribuție pe protocoale:"
    tshark -r "$input" -q -z io,phs 2>/dev/null
    echo ""
    
    log_info "Statistici I/O (intervale 1s):"
    tshark -r "$input" -q -z io,stat,1 2>/dev/null | head -30
}

capture_live() {
    local interface="${INTERFACE:-$DEFAULT_INTERFACE}"
    local port="${PORT:-$DEFAULT_PORT}"
    
    check_privileges
    check_tool tshark
    
    log_info "Captură LIVE pe $interface:$port"
    log_info "Apăsați Ctrl+C pentru oprire"
    echo ""
    
    tshark -i "$interface" \
        -f "port $port" \
        -T fields \
        -e frame.time_relative \
        -e ip.src \
        -e ip.dst \
        -e tcp.srcport \
        -e tcp.dstport \
        -e udp.srcport \
        -e udp.dstport \
        -e frame.len \
        -e _ws.col.Protocol \
        -e _ws.col.Info \
        -E header=y \
        2>/dev/null
}

clean_captures() {
    log_info "Curățare capturi vechi..."
    
    local count=0
    
    if [[ -d "$CAPTURES_DIR" ]]; then
        count=$(find "$CAPTURES_DIR" -name "*.pcap" -mtime +7 | wc -l)
        find "$CAPTURES_DIR" -name "*.pcap" -mtime +7 -delete 2>/dev/null || true
    fi
    
    log_success "Șterse $count fișiere .pcap mai vechi de 7 zile"
}

# =============================================================================
# Parser argumente
# =============================================================================

COMMAND=""
INTERFACE=""
PORT=""
DURATION=""
COUNT=""
OUTPUT=""
FILE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        tcp|udp|handshake|analyze|stats|live|clean)
            COMMAND=$1
            shift
            ;;
        -i|--interface)
            INTERFACE=$2
            shift 2
            ;;
        -p|--port)
            PORT=$2
            shift 2
            ;;
        -d|--duration)
            DURATION=$2
            shift 2
            ;;
        -c|--count)
            COUNT=$2
            shift 2
            ;;
        -o|--output)
            OUTPUT=$2
            shift 2
            ;;
        -f|--file)
            FILE=$2
            shift 2
            ;;
        -h|--help)
            usage
            ;;
        *)
            log_error "Argument necunoscut: $1"
            echo "Rulați: $0 --help"
            exit 1
            ;;
    esac
done

# =============================================================================
# Execuție comandă
# =============================================================================

case "$COMMAND" in
    tcp)        capture_tcp ;;
    udp)        capture_udp ;;
    handshake)  capture_handshake ;;
    analyze)    analyze_pcap ;;
    stats)      show_stats ;;
    live)       capture_live ;;
    clean)      clean_captures ;;
    "")
        log_error "Nicio comandă specificată"
        echo "Rulați: $0 --help"
        exit 1
        ;;
    *)
        log_error "Comandă necunoscută: $COMMAND"
        exit 1
        ;;
esac
