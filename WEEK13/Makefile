# ==============================================================================
# Makefile - Starterkit S13: IoT și Securitate în Rețele de Calculatoare
# ==============================================================================
# Automatizări pentru demonstrații, exerciții și management infrastructură
# Folosire: make <target> [VARIABILE=valoare]
# ==============================================================================

.PHONY: help setup setup-mininet test lint clean clean-all \
        docker-up docker-down docker-logs docker-status \
        demo-offensive demo-defensive demo-mqtt-plain demo-mqtt-tls \
        scan mqtt-pub mqtt-sub exploit-ftp \
        mininet-base mininet-extended mininet-clean \
        capture-start capture-stop

# ==============================================================================
# CONFIGURARE
# ==============================================================================

SHELL := /bin/bash
PYTHON := python3
PIP := pip3
DOCKER_COMPOSE := docker compose

# Directoare
ROOT_DIR := $(shell pwd)
PYTHON_DIR := $(ROOT_DIR)/python
SCRIPTS_DIR := $(ROOT_DIR)/scripts
CONFIGS_DIR := $(ROOT_DIR)/configs
CERTS_DIR := $(CONFIGS_DIR)/certs
MININET_DIR := $(ROOT_DIR)/mininet

# Rețea Docker
DOCKER_NETWORK := pentestnet
DOCKER_SUBNET := 172.20.0.0/24

# IP-uri implicite
TARGET ?= 172.20.0.10
BROKER_IP ?= 10.0.0.100
MQTT_PORT_PLAIN ?= 1883
MQTT_PORT_TLS ?= 8883
TOPIC ?= home/kitchen/telemetry

# Culori pentru output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[0;33m
BLUE := \033[0;34m
NC := \033[0m

# ==============================================================================
# HELP
# ==============================================================================

help:
	@echo -e "$(BLUE)╔══════════════════════════════════════════════════════════════════════╗$(NC)"
	@echo -e "$(BLUE)║     Starterkit S13 - IoT și Securitate în Rețele de Calculatoare     ║$(NC)"
	@echo -e "$(BLUE)╚══════════════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo -e "$(GREEN)SETUP:$(NC)"
	@echo "  make setup              - Instalare dependențe + certificate"
	@echo "  make setup-mininet      - Setup complet pentru Mininet (sudo)"
	@echo ""
	@echo -e "$(GREEN)DOCKER:$(NC)"
	@echo "  make docker-up          - Pornire containere vulnerabile"
	@echo "  make docker-down        - Oprire și curățare containere"
	@echo "  make docker-logs        - Vizualizare loguri containere"
	@echo "  make docker-status      - Starea containerelor"
	@echo ""
	@echo -e "$(GREEN)DEMONSTRAȚII (secvențe automate):$(NC)"
	@echo "  make demo-offensive     - Scan → Enum → Exploit (complet)"
	@echo "  make demo-defensive     - TLS → ACL → Segmentare"
	@echo "  make demo-mqtt-plain    - MQTT fără criptare"
	@echo "  make demo-mqtt-tls      - MQTT cu TLS"
	@echo ""
	@echo -e "$(GREEN)EXERCIȚII INDIVIDUALE:$(NC)"
	@echo "  make scan TARGET=IP     - Scanare porturi (default: $(TARGET))"
	@echo "  make mqtt-pub TOPIC=X   - Publicare mesaj MQTT"
	@echo "  make mqtt-sub TOPIC=X   - Abonare la topic MQTT"
	@echo "  make exploit-ftp        - Exploit vsftpd backdoor"
	@echo ""
	@echo -e "$(GREEN)MININET (necesită sudo):$(NC)"
	@echo "  make mininet-base       - Topologie bază"
	@echo "  make mininet-extended   - Topologie segmentată"
	@echo "  make mininet-clean      - Curățare Mininet"
	@echo ""
	@echo -e "$(GREEN)CAPTURĂ TRAFIC:$(NC)"
	@echo "  make capture-start IF=X - Pornire captură (default: any)"
	@echo "  make capture-stop       - Oprire captură"
	@echo ""
	@echo -e "$(GREEN)UTILITARE:$(NC)"
	@echo "  make test               - Smoke test complet"
	@echo "  make lint               - Verificare sintaxă Python"
	@echo "  make clean              - Curățare fișiere temporare"
	@echo "  make clean-all          - Reset complet"
	@echo ""

# ==============================================================================
# SETUP
# ==============================================================================

setup: _check-python _install-python-deps _generate-certs
	@echo -e "$(GREEN)[✓] Setup complet!$(NC)"
	@echo "    Rulează 'make test' pentru verificare."

_check-python:
	@echo -e "$(BLUE)[*] Verificare Python...$(NC)"
	@$(PYTHON) --version || (echo -e "$(RED)[✗] Python3 nu este instalat$(NC)" && exit 1)

_install-python-deps:
	@echo -e "$(BLUE)[*] Instalare dependențe Python...$(NC)"
	@$(PIP) install -q --upgrade pip
	@$(PIP) install -q -r requirements.txt
	@echo -e "$(GREEN)[✓] Dependențe Python instalate$(NC)"

_generate-certs:
	@echo -e "$(BLUE)[*] Generare certificate TLS...$(NC)"
	@mkdir -p $(CERTS_DIR)
	@if [ ! -f $(CERTS_DIR)/ca.crt ]; then \
		openssl req -x509 -nodes -newkey rsa:2048 \
			-keyout $(CERTS_DIR)/ca.key \
			-out $(CERTS_DIR)/ca.crt \
			-subj "/CN=IoT-Lab-CA" \
			-days 365 2>/dev/null; \
		echo -e "$(GREEN)[✓] CA generat$(NC)"; \
	fi
	@if [ ! -f $(CERTS_DIR)/server.crt ]; then \
		openssl req -nodes -newkey rsa:2048 \
			-keyout $(CERTS_DIR)/server.key \
			-out $(CERTS_DIR)/server.csr \
			-subj "/CN=broker" 2>/dev/null; \
		openssl x509 -req \
			-in $(CERTS_DIR)/server.csr \
			-CA $(CERTS_DIR)/ca.crt \
			-CAkey $(CERTS_DIR)/ca.key \
			-CAcreateserial \
			-out $(CERTS_DIR)/server.crt \
			-days 365 2>/dev/null; \
		rm -f $(CERTS_DIR)/server.csr; \
		echo -e "$(GREEN)[✓] Certificate server generate$(NC)"; \
	fi

setup-mininet: setup
	@echo -e "$(BLUE)[*] Instalare Mininet și dependențe...$(NC)"
	@sudo apt-get update -qq
	@sudo apt-get install -y -qq mininet openvswitch-switch mosquitto mosquitto-clients tcpdump tshark
	@sudo service openvswitch-switch start || true
	@echo -e "$(GREEN)[✓] Setup Mininet complet$(NC)"

# ==============================================================================
# DOCKER
# ==============================================================================

docker-up:
	@echo -e "$(BLUE)[*] Pornire containere vulnerabile...$(NC)"
	@$(DOCKER_COMPOSE) -f docker-compose.yml up -d
	@sleep 3
	@echo -e "$(GREEN)[✓] Containere pornite:$(NC)"
	@$(DOCKER_COMPOSE) -f docker-compose.yml ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"

docker-down:
	@echo -e "$(BLUE)[*] Oprire containere...$(NC)"
	@$(DOCKER_COMPOSE) -f docker-compose.yml down -v --remove-orphans
	@echo -e "$(GREEN)[✓] Containere oprite$(NC)"

docker-logs:
	@$(DOCKER_COMPOSE) -f docker-compose.yml logs -f

docker-status:
	@$(DOCKER_COMPOSE) -f docker-compose.yml ps

# ==============================================================================
# DEMONSTRAȚII AUTOMATE
# ==============================================================================

demo-offensive: docker-up
	@echo ""
	@echo -e "$(YELLOW)╔════════════════════════════════════════════════════════════════╗$(NC)"
	@echo -e "$(YELLOW)║            DEMO OFENSIV - Fluxul complet de pentest            ║$(NC)"
	@echo -e "$(YELLOW)╚════════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@sleep 2
	@echo -e "$(BLUE)═══════════════════════════════════════════════════════════════════$(NC)"
	@echo -e "$(BLUE)  ETAPA 1: Descoperire rețea (Host Discovery)$(NC)"
	@echo -e "$(BLUE)═══════════════════════════════════════════════════════════════════$(NC)"
	@echo -e "$(YELLOW)  Scanăm rețeaua $(DOCKER_SUBNET) pentru hosturi active...$(NC)"
	@$(PYTHON) $(PYTHON_DIR)/exercises/ex_01_port_scanner.py --target 172.20.0.1-15 --mode discovery --timeout 0.5
	@echo ""
	@sleep 2
	@echo -e "$(BLUE)═══════════════════════════════════════════════════════════════════$(NC)"
	@echo -e "$(BLUE)  ETAPA 2: Scanare porturi (Port Scanning)$(NC)"
	@echo -e "$(BLUE)═══════════════════════════════════════════════════════════════════$(NC)"
	@echo -e "$(YELLOW)  Identificăm serviciile pe hosturile descoperite...$(NC)"
	@$(PYTHON) $(PYTHON_DIR)/exercises/ex_01_port_scanner.py --target 172.20.0.10 --ports 1-1024 --timeout 0.3
	@$(PYTHON) $(PYTHON_DIR)/exercises/ex_01_port_scanner.py --target 172.20.0.12 --ports 20-25,2121,6200 --timeout 0.3
	@echo ""
	@sleep 2
	@echo -e "$(BLUE)═══════════════════════════════════════════════════════════════════$(NC)"
	@echo -e "$(BLUE)  ETAPA 3: Enumerare servicii (Service Enumeration)$(NC)"
	@echo -e "$(BLUE)═══════════════════════════════════════════════════════════════════$(NC)"
	@echo -e "$(YELLOW)  Extragem informații despre versiuni și configurări...$(NC)"
	@$(PYTHON) $(PYTHON_DIR)/exploits/banner_grabber.py --target 172.20.0.12 --port 2121
	@$(PYTHON) $(PYTHON_DIR)/exploits/banner_grabber.py --target 172.20.0.10 --port 80 --http
	@echo ""
	@sleep 2
	@echo -e "$(BLUE)═══════════════════════════════════════════════════════════════════$(NC)"
	@echo -e "$(BLUE)  ETAPA 4: Verificare vulnerabilități (Vulnerability Check)$(NC)"
	@echo -e "$(BLUE)═══════════════════════════════════════════════════════════════════$(NC)"
	@echo -e "$(YELLOW)  Căutăm vulnerabilități cunoscute...$(NC)"
	@$(PYTHON) $(PYTHON_DIR)/exercises/ex_04_vuln_checker.py --target 172.20.0.12 --port 2121 --service ftp
	@echo ""
	@sleep 2
	@echo -e "$(BLUE)═══════════════════════════════════════════════════════════════════$(NC)"
	@echo -e "$(BLUE)  ETAPA 5: Exploatare controlată (Controlled Exploitation)$(NC)"
	@echo -e "$(BLUE)═══════════════════════════════════════════════════════════════════$(NC)"
	@echo -e "$(YELLOW)  Demonstrăm exploatarea vulnerabilității vsftpd 2.3.4...$(NC)"
	@$(PYTHON) $(PYTHON_DIR)/exploits/ftp_backdoor_vsftpd.py --target 172.20.0.12 --ftp-port 2121 --backdoor-port 6200 --command "id; whoami; uname -a"
	@echo ""
	@echo -e "$(GREEN)╔════════════════════════════════════════════════════════════════╗$(NC)"
	@echo -e "$(GREEN)║                    DEMO OFENSIV COMPLET!                       ║$(NC)"
	@echo -e "$(GREEN)╚════════════════════════════════════════════════════════════════╝$(NC)"

demo-defensive:
	@echo ""
	@echo -e "$(YELLOW)╔════════════════════════════════════════════════════════════════╗$(NC)"
	@echo -e "$(YELLOW)║           DEMO DEFENSIV - Măsuri de protecție IoT             ║$(NC)"
	@echo -e "$(YELLOW)╚════════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo -e "$(RED)  ⚠  Acest demo necesită Mininet (sudo make setup-mininet)$(NC)"
	@echo ""
	@bash $(SCRIPTS_DIR)/run_demo_defensive.sh

demo-mqtt-plain:
	@echo -e "$(BLUE)[*] Demo MQTT în clar (NESECURIZAT)...$(NC)"
	@echo -e "$(RED)  ⚠  Traficul este vizibil în captură!$(NC)"
	@$(PYTHON) $(PYTHON_DIR)/exercises/ex_02_mqtt_client.py --role sensor --host $(BROKER_IP) --port $(MQTT_PORT_PLAIN) --topic $(TOPIC) --count 3

demo-mqtt-tls:
	@echo -e "$(BLUE)[*] Demo MQTT cu TLS (SECURIZAT)...$(NC)"
	@$(PYTHON) $(PYTHON_DIR)/exercises/ex_02_mqtt_client.py --role sensor --host $(BROKER_IP) --port $(MQTT_PORT_TLS) --topic $(TOPIC) --count 3 --tls on --cafile $(CERTS_DIR)/ca.crt --username sensor1 --password sensor1pass

# ==============================================================================
# EXERCIȚII INDIVIDUALE
# ==============================================================================

scan:
	@echo -e "$(BLUE)[*] Scanare porturi pe $(TARGET)...$(NC)"
	@$(PYTHON) $(PYTHON_DIR)/exercises/ex_01_port_scanner.py --target $(TARGET) --ports 1-1024 --timeout 0.3 --json-out /tmp/scan_$(shell date +%Y%m%d_%H%M%S).json

mqtt-pub:
	@echo -e "$(BLUE)[*] Publicare MQTT pe topic '$(TOPIC)'...$(NC)"
	@$(PYTHON) $(PYTHON_DIR)/exercises/ex_02_mqtt_client.py --role sensor --host $(BROKER_IP) --port $(MQTT_PORT_PLAIN) --topic $(TOPIC) --count 1

mqtt-sub:
	@echo -e "$(BLUE)[*] Abonare la topic '$(TOPIC)'...$(NC)"
	@$(PYTHON) $(PYTHON_DIR)/exercises/ex_02_mqtt_client.py --role controller --host $(BROKER_IP) --port $(MQTT_PORT_PLAIN) --topic $(TOPIC)

exploit-ftp:
	@echo -e "$(BLUE)[*] Exploit vsftpd 2.3.4 backdoor...$(NC)"
	@$(PYTHON) $(PYTHON_DIR)/exploits/ftp_backdoor_vsftpd.py --target 172.20.0.12 --ftp-port 2121 --backdoor-port 6200 --command "id"

# ==============================================================================
# MININET
# ==============================================================================

mininet-base:
	@echo -e "$(BLUE)[*] Pornire topologie Mininet bază...$(NC)"
	@sudo $(PYTHON) $(MININET_DIR)/topologies/topo_base.py --mode plain --cli

mininet-extended:
	@echo -e "$(BLUE)[*] Pornire topologie Mininet segmentată...$(NC)"
	@sudo $(PYTHON) $(MININET_DIR)/topologies/topo_segmented.py --mode tls --policy restricted --cli

mininet-clean:
	@echo -e "$(BLUE)[*] Curățare Mininet...$(NC)"
	@sudo pkill -f mosquitto || true
	@sudo pkill -f mgmt_http || true
	@sudo mn -c 2>/dev/null || true
	@echo -e "$(GREEN)[✓] Mininet curățat$(NC)"

# ==============================================================================
# CAPTURĂ TRAFIC
# ==============================================================================

IF ?= any
PCAP_FILE ?= /tmp/capture_$(shell date +%Y%m%d_%H%M%S).pcap

capture-start:
	@echo -e "$(BLUE)[*] Pornire captură pe interfața '$(IF)'...$(NC)"
	@sudo tcpdump -i $(IF) -w $(PCAP_FILE) -n 'tcp port 1883 or tcp port 8883 or tcp port 2121' &
	@echo -e "$(GREEN)[✓] Captură pornită: $(PCAP_FILE)$(NC)"
	@echo "    Oprește cu: make capture-stop"

capture-stop:
	@echo -e "$(BLUE)[*] Oprire captură...$(NC)"
	@sudo pkill -f tcpdump || true
	@echo -e "$(GREEN)[✓] Captură oprită$(NC)"

# ==============================================================================
# TESTE
# ==============================================================================

test: _test-syntax _test-imports
	@echo -e "$(GREEN)[✓] Toate testele au trecut!$(NC)"

_test-syntax:
	@echo -e "$(BLUE)[*] Verificare sintaxă Python...$(NC)"
	@$(PYTHON) -m py_compile $(PYTHON_DIR)/exercises/*.py $(PYTHON_DIR)/utils/*.py $(PYTHON_DIR)/exploits/*.py
	@echo -e "$(GREEN)[✓] Sintaxă corectă$(NC)"

_test-imports:
	@echo -e "$(BLUE)[*] Verificare importuri...$(NC)"
	@$(PYTHON) -c "import socket, json, argparse, time; print('  Standard libs: OK')"
	@$(PYTHON) -c "import paho.mqtt.client; print('  paho-mqtt: OK')" || echo -e "$(YELLOW)  [!] paho-mqtt nu este instalat$(NC)"
	@echo -e "$(GREEN)[✓] Importuri verificate$(NC)"

lint:
	@echo -e "$(BLUE)[*] Linting Python...$(NC)"
	@$(PYTHON) -m py_compile $(PYTHON_DIR)/**/*.py

# ==============================================================================
# CURĂȚARE
# ==============================================================================

clean:
	@echo -e "$(BLUE)[*] Curățare fișiere temporare...$(NC)"
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@rm -f /tmp/scan_*.json /tmp/capture_*.pcap /tmp/mqtt_*.pcap
	@echo -e "$(GREEN)[✓] Curățare completă$(NC)"

clean-all: clean docker-down mininet-clean
	@echo -e "$(BLUE)[*] Reset complet...$(NC)"
	@rm -rf $(CERTS_DIR)/*
	@echo -e "$(GREEN)[✓] Reset complet$(NC)"

# ==============================================================================
# FIN
# ==============================================================================
