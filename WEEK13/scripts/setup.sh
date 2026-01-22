#!/usr/bin/env bash
# =============================================================================
# Setup Script - Săptămâna 13 IoT & Security
# =============================================================================
# Pregătește mediul de lucru pentru exercițiile de laborator.
#
# Acțiuni:
#   1. Instalare pachete sistem (apt-get)
#   2. Instalare biblioteci Python (pip)
#   3. Generare certificate TLS pentru MQTT
#   4. Creare fișier parole Mosquitto
#   5. Verificare configurare
#
# Utilizare:
#   ./setup.sh              # Setup complet
#   ./setup.sh --certs      # Doar generare certificate
#   ./setup.sh --pip        # Doar dependențe Python
#   ./setup.sh --check      # Doar verificare
#
# Autor: Colectiv Didactic ASE-CSIE
# =============================================================================

set -e  # Exit on error

# -----------------------------------------------------------------------------
# CONSTANTE ȘI CULORI
# -----------------------------------------------------------------------------

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
CERTS_DIR="$PROJECT_DIR/configs/certs"
MOSQUITTO_DIR="$PROJECT_DIR/configs/mosquitto"

# Culori
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# -----------------------------------------------------------------------------
# FUNCȚII HELPER
# -----------------------------------------------------------------------------

log_info() {
    echo -e "${CYAN}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

log_error() {
    echo -e "${RED}[✗]${NC} $1"
}

log_section() {
    echo ""
    echo -e "${BOLD}${BLUE}=== $1 ===${NC}"
    echo ""
}

check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_warning "Unele operații necesită privilegii root."
        log_info "Rulați cu: sudo ./setup.sh"
        return 1
    fi
    return 0
}

# -----------------------------------------------------------------------------
# INSTALARE PACHETE SISTEM
# -----------------------------------------------------------------------------

install_system_packages() {
    log_section "Instalare Pachete Sistem"
    
    if ! check_root; then
        log_warning "Skip instalare pachete sistem (necesită sudo)"
        return
    fi
    
    log_info "Actualizare liste pachete..."
    apt-get update -qq
    
    log_info "Instalare pachete..."
    apt-get install -y -qq \
        mosquitto \
        mosquitto-clients \
        tcpdump \
        nmap \
        netcat-openbsd \
        python3-pip \
        python3-venv \
        docker.io \
        docker-compose \
        wireshark-common \
        tshark \
        2>/dev/null
    
    # Mininet (opțional, poate fi instalat separat)
    if ! command -v mn &> /dev/null; then
        log_info "Instalare Mininet..."
        apt-get install -y -qq mininet 2>/dev/null || \
            log_warning "Mininet nu s-a putut instala. Instalați manual."
    fi
    
    log_success "Pachete sistem instalate"
}

# -----------------------------------------------------------------------------
# INSTALARE DEPENDENȚE PYTHON
# -----------------------------------------------------------------------------

install_python_deps() {
    log_section "Instalare Dependențe Python"
    
    local req_file="$PROJECT_DIR/requirements.txt"
    
    if [[ ! -f "$req_file" ]]; then
        log_warning "requirements.txt nu există, creez unul implicit..."
        cat > "$req_file" << 'EOF'
# Dependențe Python - Săptămâna 13 IoT & Security

# MQTT Client
paho-mqtt>=1.6.0

# Packet sniffing
scapy>=2.5.0

# Utilities
requests>=2.28.0
colorama>=0.4.6
EOF
    fi
    
    log_info "Instalare din requirements.txt..."
    
    # Încercăm fără --break-system-packages prima dată
    if pip3 install -r "$req_file" -q 2>/dev/null; then
        log_success "Dependențe Python instalate"
    elif pip3 install -r "$req_file" --break-system-packages -q 2>/dev/null; then
        log_success "Dependențe Python instalate (--break-system-packages)"
    else
        log_warning "Instalare pip eșuată. Încercați manual:"
        log_info "  pip3 install -r requirements.txt --break-system-packages"
    fi
}

# -----------------------------------------------------------------------------
# GENERARE CERTIFICATE TLS
# -----------------------------------------------------------------------------

generate_certificates() {
    log_section "Generare Certificate TLS"
    
    # Creare director
    mkdir -p "$CERTS_DIR"
    cd "$CERTS_DIR"
    
    # Verificare dacă există deja
    if [[ -f "server.crt" && -f "server.key" && -f "ca.crt" ]]; then
        log_warning "Certificate existente găsite. Regenerare? [y/N]"
        read -r response
        if [[ ! "$response" =~ ^[Yy]$ ]]; then
            log_info "Păstrez certificatele existente"
            return
        fi
    fi
    
    log_info "Generare Certificate Authority (CA)..."
    
    # 1. Generare CA private key
    openssl genrsa -out ca.key 2048 2>/dev/null
    
    # 2. Generare CA certificate (self-signed)
    openssl req -new -x509 -days 365 -key ca.key -out ca.crt \
        -subj "/C=RO/ST=Bucuresti/L=Bucuresti/O=ASE-CSIE/OU=Laborator/CN=MQTT-CA" \
        2>/dev/null
    
    log_success "CA generat: ca.crt, ca.key"
    
    log_info "Generare certificat server MQTT..."
    
    # 3. Generare server private key
    openssl genrsa -out server.key 2048 2>/dev/null
    
    # 4. Generare Certificate Signing Request (CSR)
    openssl req -new -key server.key -out server.csr \
        -subj "/C=RO/ST=Bucuresti/L=Bucuresti/O=ASE-CSIE/OU=MQTT/CN=mqtt-broker" \
        2>/dev/null
    
    # 5. Semnare CSR cu CA -> server certificate
    openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key \
        -CAcreateserial -out server.crt -days 365 \
        2>/dev/null
    
    # 6. Cleanup CSR
    rm -f server.csr
    
    log_success "Certificat server generat: server.crt, server.key"
    
    # Opțional: generare certificat client
    log_info "Generare certificat client (opțional)..."
    
    openssl genrsa -out client.key 2048 2>/dev/null
    openssl req -new -key client.key -out client.csr \
        -subj "/C=RO/ST=Bucuresti/L=Bucuresti/O=ASE-CSIE/OU=Client/CN=mqtt-client" \
        2>/dev/null
    openssl x509 -req -in client.csr -CA ca.crt -CAkey ca.key \
        -CAcreateserial -out client.crt -days 365 \
        2>/dev/null
    rm -f client.csr
    
    log_success "Certificat client generat: client.crt, client.key"
    
    # Setare permisiuni
    chmod 600 *.key
    chmod 644 *.crt
    
    # Afișare rezumat
    log_info "Certificate generate în: $CERTS_DIR"
    ls -la "$CERTS_DIR"
    
    cd - > /dev/null
}

# -----------------------------------------------------------------------------
# CREARE FIȘIER PAROLE MOSQUITTO
# -----------------------------------------------------------------------------

create_mosquitto_passwords() {
    log_section "Configurare Parole Mosquitto"
    
    local passwd_file="$MOSQUITTO_DIR/passwd"
    
    mkdir -p "$MOSQUITTO_DIR"
    
    if [[ -f "$passwd_file" ]]; then
        log_warning "Fișier parole existent. Regenerare? [y/N]"
        read -r response
        if [[ ! "$response" =~ ^[Yy]$ ]]; then
            log_info "Păstrez fișierul existent"
            return
        fi
    fi
    
    # Creare fișier parole
    log_info "Creare utilizatori MQTT..."
    
    # Verificare dacă mosquitto_passwd e disponibil
    if ! command -v mosquitto_passwd &> /dev/null; then
        log_warning "mosquitto_passwd nu este instalat. Creez fișier manual..."
        
        # Format: user:password_hash (plain text pentru demo - NU în producție!)
        cat > "$passwd_file" << 'EOF'
# ATENȚIE: În producție, folosiți mosquitto_passwd pentru hash-uri!
# Acest fișier e doar pentru demonstrație
admin:admin123
sensor1:sensor123
sensor2:sensor123
controller:ctrl123
dashboard:dash123
student:student123
guest:guest123
EOF
        log_warning "Parole în plain text! Pentru producție: mosquitto_passwd -c passwd user"
    else
        # Folosire mosquitto_passwd
        rm -f "$passwd_file"
        
        # Adăugare utilizatori
        echo "admin123" | mosquitto_passwd -b -c "$passwd_file" admin admin123 2>/dev/null || true
        echo "sensor123" | mosquitto_passwd -b "$passwd_file" sensor1 sensor123 2>/dev/null || true
        echo "sensor123" | mosquitto_passwd -b "$passwd_file" sensor2 sensor123 2>/dev/null || true
        echo "ctrl123" | mosquitto_passwd -b "$passwd_file" controller ctrl123 2>/dev/null || true
        echo "dash123" | mosquitto_passwd -b "$passwd_file" dashboard dash123 2>/dev/null || true
        echo "student123" | mosquitto_passwd -b "$passwd_file" student student123 2>/dev/null || true
        echo "guest123" | mosquitto_passwd -b "$passwd_file" guest guest123 2>/dev/null || true
        
        log_success "Parole hash-uite create"
    fi
    
    # Afișare utilizatori
    log_info "Utilizatori creați:"
    echo "  admin      : admin123     (acces complet)"
    echo "  sensor1    : sensor123    (publish telemetrie)"
    echo "  sensor2    : sensor123    (publish telemetrie)"
    echo "  controller : ctrl123      (read all, write commands)"
    echo "  dashboard  : dash123      (read only)"
    echo "  student    : student123   (test/sandbox)"
    echo "  guest      : guest123     (read public only)"
}

# -----------------------------------------------------------------------------
# VERIFICARE CONFIGURARE
# -----------------------------------------------------------------------------

verify_setup() {
    log_section "Verificare Configurare"
    
    local errors=0
    
    # Verificare Python
    log_info "Verificare Python..."
    if command -v python3 &> /dev/null; then
        log_success "Python3: $(python3 --version)"
    else
        log_error "Python3 nu este instalat"
        ((errors++))
    fi
    
    # Verificare module Python
    log_info "Verificare module Python..."
    
    for module in "paho.mqtt.client" "scapy.all" "requests"; do
        if python3 -c "import $module" 2>/dev/null; then
            log_success "  $module: OK"
        else
            log_warning "  $module: Nu este instalat"
        fi
    done
    
    # Verificare Docker
    log_info "Verificare Docker..."
    if command -v docker &> /dev/null; then
        if docker ps &> /dev/null; then
            log_success "Docker: OK (serviciul rulează)"
        else
            log_warning "Docker instalat dar serviciul nu rulează"
        fi
    else
        log_warning "Docker nu este instalat"
    fi
    
    # Verificare certificate
    log_info "Verificare certificate TLS..."
    if [[ -f "$CERTS_DIR/ca.crt" && -f "$CERTS_DIR/server.crt" ]]; then
        log_success "Certificate TLS: OK"
        openssl x509 -in "$CERTS_DIR/server.crt" -noout -subject -dates 2>/dev/null | \
            sed 's/^/  /'
    else
        log_warning "Certificate TLS: Nu există (rulați --certs)"
    fi
    
    # Verificare Mosquitto
    log_info "Verificare Mosquitto..."
    if command -v mosquitto &> /dev/null; then
        log_success "Mosquitto: OK"
    else
        log_warning "Mosquitto nu este instalat"
    fi
    
    # Verificare tcpdump
    log_info "Verificare tcpdump..."
    if command -v tcpdump &> /dev/null; then
        log_success "tcpdump: OK"
    else
        log_warning "tcpdump nu este instalat"
    fi
    
    # Verificare Mininet
    log_info "Verificare Mininet..."
    if command -v mn &> /dev/null; then
        log_success "Mininet: OK"
    else
        log_warning "Mininet nu este instalat (opțional pentru Docker workflow)"
    fi
    
    echo ""
    if [[ $errors -eq 0 ]]; then
        log_success "Verificare completă - mediul este pregătit!"
    else
        log_error "Verificare completă cu $errors erori"
    fi
}

# -----------------------------------------------------------------------------
# MAIN
# -----------------------------------------------------------------------------

main() {
    echo ""
    echo -e "${BOLD}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BOLD}║   Setup Script - Săptămâna 13 IoT & Security                 ║${NC}"
    echo -e "${BOLD}║   Academia de Studii Economice - CSIE                        ║${NC}"
    echo -e "${BOLD}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    case "${1:-}" in
        --apt|--system)
            install_system_packages
            ;;
        --pip|--python)
            install_python_deps
            ;;
        --certs|--certificates)
            generate_certificates
            ;;
        --passwd|--passwords)
            create_mosquitto_passwords
            ;;
        --check|--verify)
            verify_setup
            ;;
        --help|-h)
            echo "Utilizare: $0 [opțiune]"
            echo ""
            echo "Opțiuni:"
            echo "  (fără)      Setup complet"
            echo "  --apt       Doar pachete sistem (necesită sudo)"
            echo "  --pip       Doar dependențe Python"
            echo "  --certs     Doar generare certificate TLS"
            echo "  --passwd    Doar creare parole Mosquitto"
            echo "  --check     Verificare configurare"
            echo "  --help      Afișare acest mesaj"
            ;;
        *)
            # Setup complet
            install_system_packages
            install_python_deps
            generate_certificates
            create_mosquitto_passwords
            verify_setup
            ;;
    esac
    
    echo ""
    log_success "Setup complet!"
    echo ""
}

main "$@"
