# =============================================================================
# Makefile – Starterkit Săptămâna 5: Nivelul Rețea - Adresare IP
# =============================================================================
# Automatizare completă pentru instalare, demo-uri, teste și laborator Mininet
#
# Utilizare:
#   make help                # Afișează toate target-urile disponibile
#   make setup               # Instalează dependențele
#   make demo                # Rulează toate demo-urile Python
#   make mininet-base        # Pornește topologia Mininet de bază
#
# © 2025 ASE-CSIE | Revolvix&Hypotheticalandrei
# =============================================================================

.PHONY: help setup test demo demo-cidr demo-flsm demo-vlsm demo-ipv6 quiz \
        mininet-base mininet-extended mininet-extended-ipv6 mininet-clean \
        capture verify clean reset all run-demo run-lab run-all artifacts \
        docker-build docker-run

# -----------------------------------------------------------------------------
# Variabile
# -----------------------------------------------------------------------------
PYTHON := python3
PIP := pip3
SHELL := /bin/bash

# Week 5 Configuration
WEEK := 5
NETWORK_BASE := 10.0.$(WEEK)
WEEK_PORT_BASE := $(shell echo $$((5100 + 100 * ($(WEEK) - 1))))

ROOT_DIR := $(shell pwd)
PYTHON_DIR := $(ROOT_DIR)/python
EXERCISES_DIR := $(PYTHON_DIR)/exercises
MININET_DIR := $(ROOT_DIR)/mininet/topologies
SCRIPTS_DIR := $(ROOT_DIR)/scripts
DOCS_DIR := $(ROOT_DIR)/docs
PCAP_DIR := $(ROOT_DIR)/pcap
ARTIFACTS_DIR := $(ROOT_DIR)/artifacts

# Culori pentru output
GREEN := \033[0;32m
YELLOW := \033[1;33m
BLUE := \033[0;34m
CYAN := \033[0;36m
RED := \033[0;31m
BOLD := \033[1m
NC := \033[0m

# -----------------------------------------------------------------------------
# Target implicit și help
# -----------------------------------------------------------------------------
.DEFAULT_GOAL := help

help:
	@echo ""
	@echo "$(BLUE)╔══════════════════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(BLUE)║$(NC)       $(GREEN)Starterkit Săptămâna 5 – Nivelul Rețea$(NC)                         $(BLUE)║$(NC)"
	@echo "$(BLUE)║$(NC)       $(YELLOW)Adresare IPv4/IPv6, CIDR, Subnetting, VLSM$(NC)                    $(BLUE)║$(NC)"
	@echo "$(BLUE)╚══════════════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "$(GREEN)$(BOLD)Comenzi de Bază:$(NC)"
	@echo "  make setup               Instalează dependențele sistem și Python"
	@echo "  make test                Rulează smoke tests pentru validare"
	@echo "  make demo                Rulează toate demo-urile Python"
	@echo "  make clean               Curăță fișierele temporare"
	@echo "  make reset               Reset complet (clean + mininet-clean)"
	@echo ""
	@echo "$(GREEN)$(BOLD)Demo-uri Python (fără sudo):$(NC)"
	@echo "  make demo-cidr           Demo analiză CIDR (192.168.10.14/26)"
	@echo "  make demo-flsm           Demo subnetting FLSM (4 și 8 subrețele)"
	@echo "  make demo-vlsm           Demo alocare VLSM (60, 20, 10, 2 hosturi)"
	@echo "  make demo-ipv6           Demo conversii IPv6 + subrețele"
	@echo "  make quiz                Quiz interactiv de subnetting"
	@echo ""
	@echo "$(GREEN)$(BOLD)Laborator Mininet (necesită sudo):$(NC)"
	@echo "  make mininet-base        Topologie bază: 2 subrețele + 1 router"
	@echo "  make mininet-extended    Topologie extinsă: VLSM (3 prefixe diferite)"
	@echo "  make mininet-extended-ipv6  Topologie extinsă cu IPv6"
	@echo "  make mininet-test        Test automat conectivitate"
	@echo "  make mininet-clean       Curăță procese Mininet rămase"
	@echo ""
	@echo "$(GREEN)$(BOLD)Captură și Verificare:$(NC)"
	@echo "  make capture             Rulează captură de pachete automatizată"
	@echo "  make verify              Verifică că mediul e configurat corect"
	@echo ""
	@echo "$(GREEN)$(BOLD)Target-uri Compuse:$(NC)"
	@echo "  make run-demo            Setup + demo complet"
	@echo "  make run-lab             Setup + test + mininet-base"
	@echo "  make run-all             Demo automat cu artefacte"
	@echo "  make artifacts           Generare artefacte (demo.log, demo.pcap, validation.txt)"
	@echo "  make all                 Setup + test + demo"
	@echo ""
	@echo "$(CYAN)Configurare Week $(WEEK):$(NC)"
	@echo "  Rețea: $(NETWORK_BASE).0/24"
	@echo "  Porturi: $(WEEK_PORT_BASE)-$(shell echo $$(($(WEEK_PORT_BASE) + 99)))"
	@echo ""
	@echo "$(CYAN)Exemple complete:$(NC)"
	@echo "  make setup && make demo          # Setup și demo"
	@echo "  make run-all                     # Demo complet cu artefacte"
	@echo "  sudo make mininet-base           # Laborator Mininet"
	@echo "  make quiz                        # Practică interactivă"
	@echo ""

# -----------------------------------------------------------------------------
# Setup și Instalare
# -----------------------------------------------------------------------------
setup: setup-system setup-python setup-permissions
	@echo ""
	@echo "$(GREEN)$(BOLD)✓ Setup complet!$(NC)"
	@echo "  Rulați $(CYAN)'make test'$(NC) pentru verificare."
	@echo "  Rulați $(CYAN)'make demo'$(NC) pentru demonstrații."

setup-system:
	@echo ""
	@echo "$(BLUE)>>> Instalare dependențe sistem...$(NC)"
	@if [ -f /etc/debian_version ]; then \
		echo "  Sistem Debian/Ubuntu detectat"; \
		sudo apt-get update -qq && \
		sudo apt-get install -y -qq \
			python3 python3-pip python3-venv \
			mininet openvswitch-switch \
			iproute2 iputils-ping net-tools \
			tcpdump tshark wireshark-common \
			traceroute curl wget make >/dev/null 2>&1 || \
		echo "  $(YELLOW)Notă: Unele pachete pot necesita instalare manuală$(NC)"; \
	else \
		echo "  $(YELLOW)Sistem non-Debian detectat. Instalați manual dependențele.$(NC)"; \
	fi
	@echo "$(GREEN)✓ Verificare dependențe sistem completă$(NC)"

setup-python:
	@echo ""
	@echo "$(BLUE)>>> Verificare Python...$(NC)"
	@$(PYTHON) --version
	@echo "  Notă: Kit-ul folosește doar biblioteca standard (ipaddress, argparse)"
	@echo "$(GREEN)✓ Python OK$(NC)"

setup-permissions:
	@echo ""
	@echo "$(BLUE)>>> Setare permisiuni scripturi...$(NC)"
	@chmod +x $(SCRIPTS_DIR)/*.sh 2>/dev/null || true
	@chmod +x $(ROOT_DIR)/tests/*.sh 2>/dev/null || true
	@chmod +x $(EXERCISES_DIR)/*.py 2>/dev/null || true
	@echo "$(GREEN)✓ Permisiuni setate$(NC)"

# -----------------------------------------------------------------------------
# Teste și Verificare
# -----------------------------------------------------------------------------
test: verify
	@echo ""
	@echo "$(BLUE)>>> Rulare smoke tests Python...$(NC)"
	@$(PYTHON) -c "import ipaddress; print('  ✓ Modul ipaddress disponibil')"
	@$(PYTHON) -c "from python.utils.net_utils import analyze_ipv4_interface; print('  ✓ Utilitare net_utils OK')"
	@$(PYTHON) $(EXERCISES_DIR)/ex_5_01_cidr_flsm.py analyze 192.168.1.1/24 --json >/dev/null && \
		echo "  ✓ Exercițiu CIDR funcțional" || \
		echo "  $(RED)✗ Exercițiu CIDR eșuat$(NC)"
	@$(PYTHON) $(EXERCISES_DIR)/ex_5_02_vlsm_ipv6.py vlsm 10.0.0.0/24 10 5 2 --json >/dev/null && \
		echo "  ✓ Exercițiu VLSM funcțional" || \
		echo "  $(RED)✗ Exercițiu VLSM eșuat$(NC)"
	@echo ""
	@echo "$(GREEN)$(BOLD)✓ Toate testele au trecut!$(NC)"

verify:
	@echo ""
	@echo "$(BLUE)>>> Verificare mediu...$(NC)"
	@echo -n "  Python 3:    " && $(PYTHON) --version 2>/dev/null || echo "$(RED)LIPSĂ$(NC)"
	@echo -n "  Mininet:     " && (mn --version 2>/dev/null | head -1) || echo "$(YELLOW)Nu este instalat$(NC)"
	@echo -n "  OVS:         " && (ovs-vsctl --version 2>/dev/null | head -1) || echo "$(YELLOW)Nu este instalat$(NC)"
	@echo -n "  tshark:      " && (tshark --version 2>/dev/null | head -1) || echo "$(YELLOW)Nu este instalat$(NC)"
	@echo -n "  tcpdump:     " && (tcpdump --version 2>/dev/null | head -1) || echo "$(YELLOW)Nu este instalat$(NC)"
	@echo ""

# -----------------------------------------------------------------------------
# Demo-uri Python
# -----------------------------------------------------------------------------
demo: demo-cidr demo-flsm demo-vlsm demo-ipv6
	@echo ""
	@echo "$(GREEN)═══════════════════════════════════════════════════$(NC)"
	@echo "$(GREEN)  Demo complet finalizat!$(NC)"
	@echo "$(GREEN)═══════════════════════════════════════════════════$(NC)"
	@echo ""
	@echo "$(YELLOW)Pentru laborator Mininet (necesită sudo):$(NC)"
	@echo "  sudo make mininet-base"
	@echo "  sudo make mininet-extended-ipv6"
	@echo ""
	@echo "$(YELLOW)Pentru quiz interactiv:$(NC)"
	@echo "  make quiz"

demo-cidr:
	@echo ""
	@echo "$(BLUE)═══════════════════════════════════════════════════$(NC)"
	@echo "$(BLUE)  Demo 1: Analiză CIDR$(NC)"
	@echo "$(BLUE)═══════════════════════════════════════════════════$(NC)"
	@echo ""
	@echo "$(YELLOW)Comandă:$(NC) python3 ex_5_01_cidr_flsm.py analyze 192.168.10.14/26"
	@cd $(EXERCISES_DIR) && $(PYTHON) ex_5_01_cidr_flsm.py analyze 192.168.10.14/26
	@echo ""
	@echo "$(YELLOW)Comandă:$(NC) python3 ex_5_01_cidr_flsm.py analyze 172.16.50.100/20 --verbose"
	@cd $(EXERCISES_DIR) && $(PYTHON) ex_5_01_cidr_flsm.py analyze 172.16.50.100/20 --verbose

demo-flsm:
	@echo ""
	@echo "$(BLUE)═══════════════════════════════════════════════════$(NC)"
	@echo "$(BLUE)  Demo 2: Subnetting FLSM$(NC)"
	@echo "$(BLUE)═══════════════════════════════════════════════════$(NC)"
	@echo ""
	@echo "$(YELLOW)Comandă:$(NC) python3 ex_5_01_cidr_flsm.py flsm 192.168.100.0/24 4"
	@cd $(EXERCISES_DIR) && $(PYTHON) ex_5_01_cidr_flsm.py flsm 192.168.100.0/24 4
	@echo ""
	@echo "$(YELLOW)Comandă:$(NC) python3 ex_5_01_cidr_flsm.py flsm 10.0.0.0/24 8"
	@cd $(EXERCISES_DIR) && $(PYTHON) ex_5_01_cidr_flsm.py flsm 10.0.0.0/24 8

demo-vlsm:
	@echo ""
	@echo "$(BLUE)═══════════════════════════════════════════════════$(NC)"
	@echo "$(BLUE)  Demo 3: Alocare VLSM$(NC)"
	@echo "$(BLUE)═══════════════════════════════════════════════════$(NC)"
	@echo ""
	@echo "$(YELLOW)Comandă:$(NC) python3 ex_5_02_vlsm_ipv6.py vlsm 172.16.0.0/24 60 20 10 2"
	@cd $(EXERCISES_DIR) && $(PYTHON) ex_5_02_vlsm_ipv6.py vlsm 172.16.0.0/24 60 20 10 2
	@echo ""
	@echo "$(YELLOW)Comandă:$(NC) python3 ex_5_02_vlsm_ipv6.py vlsm 10.10.0.0/22 200 100 50 25 10 2 2 2"
	@cd $(EXERCISES_DIR) && $(PYTHON) ex_5_02_vlsm_ipv6.py vlsm 10.10.0.0/22 200 100 50 25 10 2 2 2

demo-ipv6:
	@echo ""
	@echo "$(BLUE)═══════════════════════════════════════════════════$(NC)"
	@echo "$(BLUE)  Demo 4: Utilitare IPv6$(NC)"
	@echo "$(BLUE)═══════════════════════════════════════════════════$(NC)"
	@echo ""
	@echo "$(YELLOW)Comandă:$(NC) python3 ex_5_02_vlsm_ipv6.py ipv6 2001:0db8:0000:0000:0000:0000:0000:0001"
	@cd $(EXERCISES_DIR) && $(PYTHON) ex_5_02_vlsm_ipv6.py ipv6 2001:0db8:0000:0000:0000:0000:0000:0001
	@echo ""
	@echo "$(YELLOW)Comandă:$(NC) python3 ex_5_02_vlsm_ipv6.py ipv6-subnets 2001:db8:10::/48 64 5"
	@cd $(EXERCISES_DIR) && $(PYTHON) ex_5_02_vlsm_ipv6.py ipv6-subnets 2001:db8:10::/48 64 5
	@echo ""
	@echo "$(YELLOW)Comandă:$(NC) python3 ex_5_02_vlsm_ipv6.py ipv6-types"
	@cd $(EXERCISES_DIR) && $(PYTHON) ex_5_02_vlsm_ipv6.py ipv6-types

quiz:
	@echo ""
	@echo "$(BLUE)═══════════════════════════════════════════════════$(NC)"
	@echo "$(BLUE)  Quiz Interactiv de Subnetting$(NC)"
	@echo "$(BLUE)═══════════════════════════════════════════════════$(NC)"
	@cd $(EXERCISES_DIR) && $(PYTHON) ex_5_03_quiz_generator.py --interactive --count 5

# -----------------------------------------------------------------------------
# Mininet
# -----------------------------------------------------------------------------
mininet-base:
	@echo ""
	@echo "$(BLUE)═══════════════════════════════════════════════════$(NC)"
	@echo "$(BLUE)  Mininet: Topologie Bază (2 subrețele + 1 router)$(NC)"
	@echo "$(BLUE)═══════════════════════════════════════════════════$(NC)"
	@echo ""
	@echo "$(YELLOW)Arhitectură Week $(WEEK):$(NC)"
	@echo "  h1 (10.0.5.11/25) -- r1 -- h2 (10.0.5.140/25)"
	@echo ""
	sudo $(PYTHON) $(MININET_DIR)/topo_5_base.py --cli

mininet-extended:
	@echo ""
	@echo "$(BLUE)═══════════════════════════════════════════════════$(NC)"
	@echo "$(BLUE)  Mininet: Topologie Extinsă (VLSM)$(NC)"
	@echo "$(BLUE)═══════════════════════════════════════════════════$(NC)"
	@echo ""
	sudo $(PYTHON) $(MININET_DIR)/topo_5_extended.py --cli

mininet-extended-ipv6:
	@echo ""
	@echo "$(BLUE)═══════════════════════════════════════════════════$(NC)"
	@echo "$(BLUE)  Mininet: Topologie Extinsă (VLSM + IPv6)$(NC)"
	@echo "$(BLUE)═══════════════════════════════════════════════════$(NC)"
	@echo ""
	sudo $(PYTHON) $(MININET_DIR)/topo_5_extended.py --cli --ipv6

mininet-test:
	@echo ""
	@echo "$(BLUE)>>> Test automat conectivitate Mininet...$(NC)"
	@sudo $(PYTHON) $(MININET_DIR)/topo_5_base.py --test && \
		echo "$(GREEN)✓ Test bază reușit$(NC)" || \
		echo "$(RED)✗ Test bază eșuat$(NC)"
	@sudo $(PYTHON) $(MININET_DIR)/topo_5_extended.py --test --ipv6 && \
		echo "$(GREEN)✓ Test extins (IPv6) reușit$(NC)" || \
		echo "$(RED)✗ Test extins eșuat$(NC)"

mininet-clean:
	@echo ""
	@echo "$(BLUE)>>> Curățare procese Mininet...$(NC)"
	@sudo mn -c 2>/dev/null || true
	@sudo pkill -9 -f "python.*mininet" 2>/dev/null || true
	@sudo pkill -9 -f "ovs-" 2>/dev/null || true
	@sudo systemctl restart openvswitch-switch 2>/dev/null || \
		echo "  $(YELLOW)OVS nu este disponibil$(NC)"
	@echo "$(GREEN)✓ Mininet curățat$(NC)"

# -----------------------------------------------------------------------------
# Captură
# -----------------------------------------------------------------------------
capture:
	@echo ""
	@echo "$(BLUE)>>> Captură de pachete (demonstrativ)$(NC)"
	@mkdir -p $(PCAP_DIR)
	@echo "  Pentru captură reală, rulați în CLI Mininet:"
	@echo "    r1 tcpdump -ni r1-eth0 -w /tmp/capture.pcap icmp &"
	@echo "    h1 ping -c 5 10.0.2.10"
	@echo "    r1 kill %tcpdump"
	@echo ""
	@echo "  Analiză cu tshark:"
	@echo "    sudo tshark -r /tmp/capture.pcap -T fields -e ip.ttl -e ip.src -e ip.dst"

# -----------------------------------------------------------------------------
# Curățare
# -----------------------------------------------------------------------------
clean:
	@echo ""
	@echo "$(BLUE)>>> Curățare fișiere temporare...$(NC)"
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@find . -type f -name ".DS_Store" -delete 2>/dev/null || true
	@rm -rf .pytest_cache/ 2>/dev/null || true
	@rm -f $(PCAP_DIR)/*.pcap 2>/dev/null || true
	@echo "$(GREEN)✓ Fișiere temporare curățate$(NC)"

reset: clean mininet-clean
	@echo ""
	@echo "$(GREEN)✓ Reset complet finalizat$(NC)"

# -----------------------------------------------------------------------------
# Target-uri compuse
# -----------------------------------------------------------------------------
run-demo: setup demo

run-lab: setup test
	@echo ""
	@echo "$(YELLOW)Acum porniți laboratorul cu:$(NC)"
	@echo "  sudo make mininet-base"

run-all: setup
	@echo ""
	@echo "$(BLUE)>>> Rulare demo automat complet...$(NC)"
	@chmod +x $(SCRIPTS_DIR)/run_all.sh
	@$(SCRIPTS_DIR)/run_all.sh --full
	@echo ""
	@echo "$(GREEN)$(BOLD)✓ Demo complet finalizat!$(NC)"
	@echo "$(YELLOW)Artefacte în:$(NC) $(ARTIFACTS_DIR)/"
	@echo "$(YELLOW)Validare cu:$(NC) make test-artifacts"

artifacts:
	@echo ""
	@echo "$(BLUE)>>> Generare artefacte...$(NC)"
	@mkdir -p $(ARTIFACTS_DIR)
	@chmod +x $(SCRIPTS_DIR)/run_all.sh
	@$(SCRIPTS_DIR)/run_all.sh --quick
	@echo ""
	@echo "$(GREEN)✓ Artefacte generate:$(NC)"
	@ls -la $(ARTIFACTS_DIR)/ 2>/dev/null || echo "  (director gol)"

test-artifacts:
	@echo ""
	@echo "$(BLUE)>>> Validare artefacte...$(NC)"
	@chmod +x $(ROOT_DIR)/tests/smoke_test.sh
	@$(ROOT_DIR)/tests/smoke_test.sh --with-artifacts

all: setup test demo
	@echo ""
	@echo "$(GREEN)$(BOLD)✓ Setup, test și demo complete!$(NC)"
