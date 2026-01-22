#!/bin/bash
# =============================================================================
# setup.sh - Script de configurare a mediului pentru Săptămâna 12
# Rețele de Calculatoare - ASE CSIE
# Autor: Revolvix&Hypotheticalandrei
# =============================================================================

set -e

# Culori pentru output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}============================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}============================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Verifică dacă rulează ca root (necesar pentru unele instalări)
check_root() {
    if [[ $EUID -eq 0 ]]; then
        print_warning "Rulați ca root - unele pachete pot necesita acest lucru"
    fi
}

# Verifică și instalează dependențele Python
setup_python() {
    print_header "Configurare Python"
    
    # Verifică Python 3
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
        print_success "Python 3 găsit: $PYTHON_VERSION"
    else
        print_error "Python 3 nu este instalat!"
        echo "Instalați cu: sudo apt install python3 python3-pip"
        exit 1
    fi
    
    # Verifică pip
    if command -v pip3 &> /dev/null; then
        print_success "pip3 disponibil"
    else
        print_warning "pip3 nu este disponibil, se încearcă instalarea..."
        sudo apt install -y python3-pip || {
            print_error "Nu s-a putut instala pip3"
            exit 1
        }
    fi
    
    # Instalează dependențele din requirements.txt
    if [[ -f "../requirements.txt" ]]; then
        echo "Se instalează dependențele Python..."
        pip3 install -r ../requirements.txt --break-system-packages 2>/dev/null || \
        pip3 install -r ../requirements.txt --user 2>/dev/null || \
        pip3 install -r ../requirements.txt
        print_success "Dependențe Python instalate"
    fi
}

# Configurare pentru gRPC (opțional)
setup_grpc() {
    print_header "Configurare gRPC (opțional)"
    
    read -p "Doriți să instalați suportul pentru gRPC? [y/N] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        pip3 install grpcio grpcio-tools protobuf --break-system-packages 2>/dev/null || \
        pip3 install grpcio grpcio-tools protobuf --user
        print_success "gRPC instalat"
        
        # Generează codul din .proto
        if [[ -f "../src/rpc/grpc/calculator.proto" ]]; then
            cd ../src/rpc/grpc
            python3 -m grpc_tools.protoc \
                --proto_path=. \
                --python_out=. \
                --grpc_python_out=. \
                calculator.proto
            cd - > /dev/null
            print_success "Cod gRPC generat din calculator.proto"
        fi
    else
        print_warning "gRPC omis - JSON-RPC și XML-RPC rămân disponibile"
    fi
}

# Verifică uneltele de rețea
check_network_tools() {
    print_header "Verificare unelte de rețea"
    
    # netcat
    if command -v nc &> /dev/null || command -v netcat &> /dev/null; then
        print_success "netcat disponibil"
    else
        print_warning "netcat nu este instalat (opțional)"
        echo "  Instalați cu: sudo apt install netcat-openbsd"
    fi
    
    # tcpdump
    if command -v tcpdump &> /dev/null; then
        print_success "tcpdump disponibil"
    else
        print_warning "tcpdump nu este instalat"
        echo "  Instalați cu: sudo apt install tcpdump"
    fi
    
    # tshark
    if command -v tshark &> /dev/null; then
        print_success "tshark disponibil"
    else
        print_warning "tshark nu este instalat (recomandat)"
        echo "  Instalați cu: sudo apt install tshark"
    fi
    
    # Wireshark (GUI)
    if command -v wireshark &> /dev/null; then
        print_success "Wireshark GUI disponibil"
    else
        print_warning "Wireshark GUI nu este instalat (opțional)"
    fi
}

# Verifică Docker (opțional)
check_docker() {
    print_header "Verificare Docker (opțional)"
    
    if command -v docker &> /dev/null; then
        DOCKER_VERSION=$(docker --version 2>&1 | cut -d' ' -f3 | tr -d ',')
        print_success "Docker disponibil: $DOCKER_VERSION"
        
        if command -v docker-compose &> /dev/null || docker compose version &> /dev/null; then
            print_success "Docker Compose disponibil"
        else
            print_warning "Docker Compose nu este disponibil"
        fi
    else
        print_warning "Docker nu este instalat (opțional pentru acest laborator)"
        echo "  Pentru instalare: https://docs.docker.com/engine/install/"
    fi
}

# Verifică Mininet (opțional)
check_mininet() {
    print_header "Verificare Mininet (opțional)"
    
    if command -v mn &> /dev/null; then
        print_success "Mininet disponibil"
    else
        print_warning "Mininet nu este instalat"
        echo "  Instalați cu: sudo apt install mininet"
        echo "  Sau consultați: http://mininet.org/download/"
    fi
}

# Creează directoarele necesare
create_directories() {
    print_header "Creare structură directoare"
    
    cd "$(dirname "$0")/.."
    
    mkdir -p logs
    mkdir -p pcap
    mkdir -p spool
    mkdir -p tmp
    
    print_success "Directoare create: logs/, pcap/, spool/, tmp/"
}

# Test rapid al funcționalității
quick_test() {
    print_header "Test rapid de funcționalitate"
    
    cd "$(dirname "$0")/.."
    
    # Test SMTP server (verifică doar importul)
    echo -n "Test import SMTP server... "
    if python3 -c "import src.email.smtp_server" 2>/dev/null; then
        print_success "OK"
    else
        print_warning "Eșuat (verificați dependențele)"
    fi
    
    # Test JSON-RPC server
    echo -n "Test import JSON-RPC... "
    if python3 -c "import src.rpc.jsonrpc.jsonrpc_server" 2>/dev/null; then
        print_success "OK"
    else
        print_warning "Eșuat (verificați dependențele)"
    fi
    
    # Test exercițiu autonom
    echo -n "Test exercițiu SMTP autonom... "
    if python3 exercises/ex_01_smtp.py --help &>/dev/null; then
        print_success "OK"
    else
        print_warning "Verificați exercises/ex_01_smtp.py"
    fi
}

# Afișare sumar final
show_summary() {
    print_header "Configurare completă!"
    
    echo ""
    echo "Comenzi utile:"
    echo "  make help          - Afișează toate țintele disponibile"
    echo "  make run-demo      - Rulează demonstrațiile"
    echo "  make verify        - Verifică mediul"
    echo ""
    echo "Pentru laborator:"
    echo "  make smtp-server   - Pornește serverul SMTP educațional"
    echo "  make jsonrpc-demo  - Demonstrație JSON-RPC"
    echo ""
    echo "Documentație:"
    echo "  cat README.md      - Ghid complet"
    echo "  docs/              - Materiale detaliate"
    echo ""
}

# Main
main() {
    print_header "Setup Săptămâna 12 - Email & RPC"
    echo "Rețele de Calculatoare - ASE CSIE"
    echo ""
    
    check_root
    setup_python
    check_network_tools
    check_docker
    check_mininet
    create_directories
    
    # gRPC este opțional și interactiv
    if [[ "$1" != "--quick" ]]; then
        setup_grpc
    fi
    
    quick_test
    show_summary
}

# Rulează dacă este executat direct
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
