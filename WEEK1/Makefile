# ==============================================================================
# Makefile – Starterkit Rețele de Calculatoare, Săptămâna 1
# ==============================================================================
# Automatizare completă pentru setup, demo, cleanup și development
# Versiune 3.0 Integrat | Revolvix&Hypotheticalandrei
# ==============================================================================

.PHONY: help setup verify demo clean test docker-build docker-run docker-shell docker-stop \
        demo-python demo-mininet demo-capture clean-mininet clean-outputs check-python slides \
        run-demo run-lab capture capture-examples reset all

# Variabile
SHELL := /bin/bash
PYTHON := python3
SUDO := sudo
OUTPUT_DIR := outputs
TIMESTAMP := $(shell date +%Y%m%d_%H%M%S)
RUN_DIR := $(OUTPUT_DIR)/run_$(TIMESTAMP)

# Culori pentru output
GREEN := \033[0;32m
YELLOW := \033[1;33m
BLUE := \033[0;34m
RED := \033[0;31m
CYAN := \033[0;36m
NC := \033[0m

# ==============================================================================
# HELP (TARGET IMPLICIT)
# ==============================================================================
help:
	@echo -e "$(BLUE)╔════════════════════════════════════════════════════════════════════════╗$(NC)"
	@echo -e "$(BLUE)║     Starterkit Rețele de Calculatoare - Săptămâna 1                    ║$(NC)"
	@echo -e "$(BLUE)║     Fundamente ale Rețelelor: Concepte, Componente, Clasificări        ║$(NC)"
	@echo -e "$(BLUE)╚════════════════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo -e "$(GREEN)INSTALARE ȘI VERIFICARE:$(NC)"
	@echo "  make setup              Instalează toate dependențele (necesită sudo)"
	@echo "  make verify             Verifică instalarea corectă a tuturor componentelor"
	@echo "  make check-python       Verifică doar Python și modulele necesare"
	@echo ""
	@echo -e "$(GREEN)RULARE DEMONSTRAȚII:$(NC)"
	@echo "  make demo               Demo complet (Python + info Mininet)"
	@echo "  make demo-python        Doar exercițiile Python"
	@echo "  make demo-mininet       Doar topologiile Mininet (necesită sudo)"
	@echo "  make demo-capture       Demo captură trafic cu tshark (necesită sudo)"
	@echo "  make run-demo           Alias pentru demo complet"
	@echo "  make run-lab            Rulează exercițiile de laborator"
	@echo ""
	@echo -e "$(GREEN)CURĂȚARE:$(NC)"
	@echo "  make clean              Curăță fișiere temporare și cache Python"
	@echo "  make clean-mininet      Curăță artefacte Mininet (namespace, OVS)"
	@echo "  make clean-outputs      Șterge conținutul directorului outputs/"
	@echo "  make reset              Reset complet (clean-mininet + clean-outputs)"
	@echo ""
	@echo -e "$(GREEN)CAPTURĂ TRAFIC:$(NC)"
	@echo "  make capture            Pornește o captură de trafic demonstrativă"
	@echo "  make capture-examples   Generează fișiere PCAP exemplu (TCP, UDP, HTTP)"
	@echo ""
	@echo -e "$(GREEN)DOCKER (ALTERNATIVĂ):$(NC)"
	@echo "  make docker-build       Construiește imaginea Docker"
	@echo "  make docker-run         Pornește containerul"
	@echo "  make docker-shell       Deschide shell în container"
	@echo "  make docker-stop        Oprește containerele"
	@echo ""
	@echo -e "$(GREEN)DEVELOPMENT:$(NC)"
	@echo "  make test               Rulează smoke tests"
	@echo "  make slides             Deschide prezentarea HTML"
	@echo ""
	@echo -e "$(CYAN)Exemplu flux complet:$(NC)"
	@echo "  make setup && make verify && make demo"
	@echo ""

# ==============================================================================
# SETUP ȘI VERIFICARE
# ==============================================================================
setup:
	@echo -e "$(BLUE)╔════════════════════════════════════════════════════════════════════════╗$(NC)"
	@echo -e "$(BLUE)║  SETUP - Instalare dependențe                                          ║$(NC)"
	@echo -e "$(BLUE)╚════════════════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@if [ -f scripts/setup.sh ]; then \
		bash scripts/setup.sh; \
	else \
		echo -e "$(YELLOW)[INFO]$(NC) Instalare manuală..."; \
		$(SUDO) apt-get update; \
		$(SUDO) apt-get install -y python3 python3-pip mininet openvswitch-switch tshark tcpdump netcat-openbsd iproute2 iputils-ping net-tools; \
		pip3 install --break-system-packages scapy || pip3 install scapy; \
	fi
	@echo ""
	@echo -e "$(GREEN)✓ Setup complet!$(NC)"

verify:
	@echo -e "$(BLUE)╔════════════════════════════════════════════════════════════════════════╗$(NC)"
	@echo -e "$(BLUE)║  VERIFICARE INSTALARE                                                  ║$(NC)"
	@echo -e "$(BLUE)╚════════════════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo -e "$(YELLOW)Verificare Python...$(NC)"
	@$(PYTHON) --version && echo -e "$(GREEN)  ✓ Python instalat$(NC)" || echo -e "$(RED)  ✗ Python lipsește$(NC)"
	@echo ""
	@echo -e "$(YELLOW)Verificare module Python...$(NC)"
	@$(PYTHON) -c "import socket" && echo -e "$(GREEN)  ✓ socket$(NC)" || echo -e "$(RED)  ✗ socket$(NC)"
	@$(PYTHON) -c "import struct" && echo -e "$(GREEN)  ✓ struct$(NC)" || echo -e "$(RED)  ✗ struct$(NC)"
	@$(PYTHON) -c "import argparse" && echo -e "$(GREEN)  ✓ argparse$(NC)" || echo -e "$(RED)  ✗ argparse$(NC)"
	@echo ""
	@echo -e "$(YELLOW)Verificare unelte rețea...$(NC)"
	@command -v ping >/dev/null && echo -e "$(GREEN)  ✓ ping$(NC)" || echo -e "$(RED)  ✗ ping$(NC)"
	@command -v netstat >/dev/null && echo -e "$(GREEN)  ✓ netstat$(NC)" || echo -e "$(YELLOW)  ⚠ netstat (opțional)$(NC)"
	@command -v nc >/dev/null && echo -e "$(GREEN)  ✓ netcat$(NC)" || echo -e "$(RED)  ✗ netcat$(NC)"
	@command -v tshark >/dev/null && echo -e "$(GREEN)  ✓ tshark$(NC)" || echo -e "$(YELLOW)  ⚠ tshark (recomandat)$(NC)"
	@command -v mn >/dev/null && echo -e "$(GREEN)  ✓ mininet$(NC)" || echo -e "$(YELLOW)  ⚠ mininet (recomandat)$(NC)"
	@echo ""
	@echo -e "$(GREEN)═══════════════════════════════════════════════════════════════$(NC)"
	@echo -e "$(GREEN)  Verificare completă!$(NC)"
	@echo -e "$(GREEN)═══════════════════════════════════════════════════════════════$(NC)"

check-python:
	@echo -e "$(BLUE)[CHECK]$(NC) Verificare Python..."
	@$(PYTHON) --version
	@$(PYTHON) -c "import socket; print('  ✓ socket module OK')"
	@$(PYTHON) -c "import struct; print('  ✓ struct module OK')"
	@$(PYTHON) -c "import argparse; print('  ✓ argparse module OK')"
	@echo -e "$(GREEN)[DONE]$(NC) Python verificat!"

# ==============================================================================
# DEMONSTRAȚII
# ==============================================================================
demo: demo-python
	@echo ""
	@echo -e "$(GREEN)═══════════════════════════════════════════════════════════════$(NC)"
	@echo -e "$(GREEN)  DEMO COMPLET FINALIZAT!$(NC)"
	@echo -e "$(GREEN)═══════════════════════════════════════════════════════════════$(NC)"
	@echo ""
	@echo -e "$(CYAN)Pentru funcționalități avansate:$(NC)"
	@echo "  • Demo Mininet (necesită sudo): make demo-mininet"
	@echo "  • Demo captură (necesită sudo): make demo-capture"
	@echo ""

run-demo: demo

demo-python:
	@echo -e "$(BLUE)╔════════════════════════════════════════════════════════════════════════╗$(NC)"
	@echo -e "$(BLUE)║  DEMO EXERCIȚII PYTHON                                                 ║$(NC)"
	@echo -e "$(BLUE)╚════════════════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@if [ -f python/exercises/ex_1_01_transmission_delay.py ]; then \
		echo -e "$(YELLOW)[1/4]$(NC) Exercițiu: Calcule de întârziere (L/R)"; \
		$(PYTHON) python/exercises/ex_1_01_transmission_delay.py; \
		echo ""; \
		$(PYTHON) python/exercises/ex_1_01_transmission_delay.py --self-test; \
	else \
		echo -e "$(YELLOW)[INFO]$(NC) Exercițiul ex_1_01 nu este disponibil"; \
	fi
	@echo ""
	@if [ -f python/exercises/ex_1_04_tcp_udp_demo.py ]; then \
		echo -e "$(YELLOW)[2/4]$(NC) Exercițiu: Demo TCP/UDP"; \
		$(PYTHON) python/exercises/ex_1_04_tcp_udp_demo.py --mode tcp --demo 2>/dev/null || \
		$(PYTHON) python/exercises/ex_1_04_tcp_udp_demo.py --demo 2>/dev/null || \
		echo "  Demo TCP/UDP necesită configurare suplimentară"; \
	fi
	@echo ""
	@echo -e "$(YELLOW)[3/4]$(NC) Verificare sniffer didactic..."
	@if [ -f python/exercises/ex_1_02_sniffer_didactic.py ]; then \
		$(PYTHON) python/exercises/ex_1_02_sniffer_didactic.py --help 2>/dev/null || true; \
	else \
		echo "  Fișierul nu este disponibil"; \
	fi
	@echo ""
	@echo -e "$(YELLOW)[4/4]$(NC) Verificare ARP analyzer..."
	@if [ -f python/exercises/ex_1_03_arp_analyzer.py ]; then \
		$(PYTHON) python/exercises/ex_1_03_arp_analyzer.py --help 2>/dev/null || true; \
	else \
		echo "  Fișierul nu este disponibil"; \
	fi
	@echo ""
	@echo -e "$(GREEN)[DONE]$(NC) Demo Python finalizat!"

demo-mininet:
	@echo -e "$(BLUE)[DEMO]$(NC) Demo Mininet..."
	@mkdir -p $(OUTPUT_DIR)
	@echo "--- Test pingall ---" | tee $(OUTPUT_DIR)/mininet_test.log
	$(SUDO) mn --test pingall 2>&1 | tee -a $(OUTPUT_DIR)/mininet_test.log
	@echo ""
	@echo -e "$(GREEN)[DONE]$(NC) Output salvat în $(OUTPUT_DIR)/mininet_test.log"

demo-capture:
	@echo -e "$(BLUE)[DEMO]$(NC) Demo captură trafic..."
	@mkdir -p $(OUTPUT_DIR)
	@echo "Captură 10 pachete ICMP pe loopback..."
	@(ping -c 5 localhost &) && $(SUDO) tshark -i lo -c 10 -w $(OUTPUT_DIR)/demo_capture.pcap 2>/dev/null || true
	@echo ""
	@if [ -f $(OUTPUT_DIR)/demo_capture.pcap ]; then \
		echo "Analiza capturii:"; \
		tshark -r $(OUTPUT_DIR)/demo_capture.pcap 2>/dev/null | head -10 || true; \
		echo -e "$(GREEN)[DONE]$(NC) Captură salvată în $(OUTPUT_DIR)/demo_capture.pcap"; \
	else \
		echo -e "$(YELLOW)[INFO]$(NC) Captura necesită privilegii root"; \
	fi

run-lab:
	@echo -e "$(BLUE)[LAB]$(NC) Rulare exerciții laborator..."
	@echo ""
	@echo "=== Exercițiu 1: Ping și latență ==="
	@ping -c 3 localhost
	@echo ""
	@echo "=== Exercițiu 2: Porturi active ==="
	@ss -tln 2>/dev/null || netstat -tln 2>/dev/null || echo "Comandă indisponibilă"
	@echo ""
	@echo "=== Exercițiu 3: DNS lookup ==="
	@nslookup google.com 2>/dev/null || host google.com 2>/dev/null || echo "DNS lookup indisponibil"
	@echo ""
	@echo -e "$(GREEN)[DONE]$(NC) Exerciții laborator complete!"

capture:
	@echo -e "$(BLUE)[CAPTURE]$(NC) Pornire captură demonstrativă..."
	@mkdir -p $(OUTPUT_DIR)
	$(SUDO) tshark -i any -c 20 -w $(OUTPUT_DIR)/capture_$(TIMESTAMP).pcap
	@echo -e "$(GREEN)[DONE]$(NC) Captură salvată în $(OUTPUT_DIR)/capture_$(TIMESTAMP).pcap"

capture-examples:
	@echo -e "$(BLUE)[CAPTURE]$(NC) Generare capturi exemplu pentru laborator..."
	@./scripts/capture_demo.sh --all

# ==============================================================================
# CURĂȚARE
# ==============================================================================
clean:
	@echo -e "$(BLUE)[CLEAN]$(NC) Curățare fișiere temporare..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@find . -type f -name ".DS_Store" -delete 2>/dev/null || true
	@rm -f /tmp/*.pcap /tmp/*.csv 2>/dev/null || true
	@echo -e "$(GREEN)[DONE]$(NC) Curățare completă!"

clean-mininet:
	@echo -e "$(BLUE)[CLEAN]$(NC) Curățare artefacte Mininet..."
	@$(SUDO) mn -c 2>/dev/null || true
	@$(SUDO) pkill -9 -f mininet 2>/dev/null || true
	@$(SUDO) pkill -9 -f ovs 2>/dev/null || true
	@$(SUDO) ip link show 2>/dev/null | grep -o 's[0-9]-eth[0-9]' | while read iface; do \
		$(SUDO) ip link delete $$iface 2>/dev/null || true; \
	done
	@echo -e "$(GREEN)[DONE]$(NC) Mininet curățat!"

clean-outputs:
	@echo -e "$(BLUE)[CLEAN]$(NC) Ștergere outputs/..."
	@rm -rf $(OUTPUT_DIR)/*
	@mkdir -p $(OUTPUT_DIR)
	@touch $(OUTPUT_DIR)/.gitkeep
	@echo -e "$(GREEN)[DONE]$(NC) Outputs șters!"

reset: clean-mininet clean-outputs clean
	@echo -e "$(GREEN)[DONE]$(NC) Reset complet!"

# ==============================================================================
# DOCKER
# ==============================================================================
docker-build:
	@echo -e "$(BLUE)[DOCKER]$(NC) Construire imagine..."
	@if [ -f docker/Dockerfile ]; then \
		cd docker && docker build -t netlab:latest .; \
		echo -e "$(GREEN)[DONE]$(NC) Imagine construită!"; \
	else \
		echo -e "$(RED)[ERROR]$(NC) Dockerfile nu există"; \
	fi

docker-run:
	@echo -e "$(BLUE)[DOCKER]$(NC) Pornire container..."
	@if [ -f docker/docker-compose.yml ]; then \
		cd docker && docker-compose up -d; \
		echo -e "$(GREEN)[DONE]$(NC) Container pornit! Folosiți 'make docker-shell' pentru acces."; \
	else \
		docker run -it --name netlab --network host --cap-add NET_ADMIN netlab:latest || true; \
	fi

docker-shell:
	@echo -e "$(BLUE)[DOCKER]$(NC) Conectare la container..."
	@docker exec -it netlab bash

docker-stop:
	@echo -e "$(BLUE)[DOCKER]$(NC) Oprire containere..."
	@if [ -f docker/docker-compose.yml ]; then \
		cd docker && docker-compose down; \
	else \
		docker stop netlab 2>/dev/null || true; \
		docker rm netlab 2>/dev/null || true; \
	fi
	@echo -e "$(GREEN)[DONE]$(NC) Containere oprite!"

# ==============================================================================
# DEVELOPMENT
# ==============================================================================
test:
	@echo -e "$(BLUE)[TEST]$(NC) Rulare smoke tests..."
	@if [ -f tests/smoke_test.sh ]; then \
		bash tests/smoke_test.sh; \
	else \
		echo "Smoke test simplu:"; \
		$(PYTHON) -c "print('Python OK')"; \
		ping -c 1 localhost >/dev/null && echo "Ping OK"; \
	fi
	@echo -e "$(GREEN)[DONE]$(NC) Teste finalizate!"

slides:
	@echo -e "$(BLUE)[SLIDES]$(NC) Deschidere prezentare..."
	@if [ -f theory.html ]; then \
		xdg-open theory.html 2>/dev/null || open theory.html 2>/dev/null || echo "Deschideți manual: theory.html"; \
	else \
		echo "Prezentarea HTML nu este disponibilă în directorul curent"; \
	fi

# ==============================================================================
# ALL
# ==============================================================================
all: setup verify demo
	@echo -e "$(GREEN)═══════════════════════════════════════════════════════════════$(NC)"
	@echo -e "$(GREEN)  TOTUL CONFIGURAT ȘI TESTAT CU SUCCES!$(NC)"
	@echo -e "$(GREEN)═══════════════════════════════════════════════════════════════$(NC)"

# Target implicit
.DEFAULT_GOAL := help
