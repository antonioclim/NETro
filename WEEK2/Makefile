# =============================================================================
# Makefile – Starterkit S2: Modele OSI/TCP-IP & Programare Socket
# =============================================================================
# Utilizare: make <target> | Ajutor: make help
# Autor: Revolvix&Hypotheticalandrei
# =============================================================================

SHELL := /bin/bash
.PHONY: help setup verify run-demo run-lab capture clean reset \
        demo-all demo-tcp demo-udp mininet-cli mininet-extended mininet-test \
        tcp-server tcp-client udp-server udp-client \
        capture-tcp capture-udp capture-stop analyze-tcp analyze-udp \
        docker-build docker-shell docker-demo diagrams test

# -----------------------------------------------------------------------------
# VARIABILE
# -----------------------------------------------------------------------------
PYTHON        := python3
MININET_SUDO  := sudo
TSHARK        := tshark
TCPDUMP       := tcpdump
NC            := nc

ROOT_DIR      := $(shell pwd)
EXERCISES_DIR := $(ROOT_DIR)/seminar/python/exercises
TEMPLATES_DIR := $(ROOT_DIR)/seminar/python/templates
CAPTURES_DIR  := $(ROOT_DIR)/seminar/captures
LOGS_DIR      := $(ROOT_DIR)/logs
MININET_DIR   := $(ROOT_DIR)/seminar/mininet
PCAP_DIR      := $(ROOT_DIR)/pcap

EX_TCP        := $(EXERCISES_DIR)/ex_2_01_tcp.py
EX_UDP        := $(EXERCISES_DIR)/ex_2_02_udp.py
TOPO_BASE     := $(MININET_DIR)/topologies/topo_2_base.py
TOPO_EXT      := $(MININET_DIR)/topologies/topo_2_extended.py

TCP_PORT      := 9999
UDP_PORT      := 9998
BIND_ADDR     := 0.0.0.0
MSG           ?= "Hello from Makefile"

DOCKER_IMAGE  := netlab-s2:latest

# Culori pentru output
GREEN  := \033[0;32m
YELLOW := \033[0;33m
RED    := \033[0;31m
NC_CLR := \033[0m

# =============================================================================
# HELP
# =============================================================================
help:
	@echo ""
	@echo "╔══════════════════════════════════════════════════════════════════════════╗"
	@echo "║  $(GREEN)Starterkit S2$(NC_CLR) – Makefile                                              ║"
	@echo "║  Modele Arhitecturale OSI/TCP-IP & Programare Socket                     ║"
	@echo "╠══════════════════════════════════════════════════════════════════════════╣"
	@echo "║ $(YELLOW)SETUP & VERIFICARE$(NC_CLR)                                                     ║"
	@echo "║   make setup              Instalare pachete și dependințe                ║"
	@echo "║   make verify             Verificare mediu de lucru                      ║"
	@echo "║   make test               Smoke test rapid                               ║"
	@echo "╠══════════════════════════════════════════════════════════════════════════╣"
	@echo "║ $(YELLOW)DEMONSTRAȚII (OBLIGATORIU)$(NC_CLR)                                              ║"
	@echo "║   make run-demo           Demo complet (TCP + UDP + captură)             ║"
	@echo "║   make run-lab            Rulare laborator interactiv                    ║"
	@echo "║   make demo-tcp           Demo doar TCP                                  ║"
	@echo "║   make demo-udp           Demo doar UDP                                  ║"
	@echo "╠══════════════════════════════════════════════════════════════════════════╣"
	@echo "║ $(YELLOW)MININET$(NC_CLR)                                                                 ║"
	@echo "║   make mininet-cli        Mininet interactiv (topologie bază)            ║"
	@echo "║   make mininet-extended   Topologie cu router (2 subrețele)              ║"
	@echo "║   make mininet-test       Test automat în Mininet                        ║"
	@echo "║   make mininet-clean      Curățare sesiuni Mininet                       ║"
	@echo "╠══════════════════════════════════════════════════════════════════════════╣"
	@echo "║ $(YELLOW)SERVER / CLIENT$(NC_CLR)                                                         ║"
	@echo "║   make tcp-server         Server TCP pe localhost:$(TCP_PORT)                   ║"
	@echo "║   make tcp-client MSG=x   Client TCP cu mesaj custom                     ║"
	@echo "║   make udp-server         Server UDP pe localhost:$(UDP_PORT)                   ║"
	@echo "║   make udp-client         Client UDP interactiv                          ║"
	@echo "║   make load-test N=10     Test încărcare N clienți                       ║"
	@echo "╠══════════════════════════════════════════════════════════════════════════╣"
	@echo "║ $(YELLOW)CAPTURI & ANALIZĂ$(NC_CLR)                                                       ║"
	@echo "║   make capture            Pornire captură TCP+UDP                        ║"
	@echo "║   make capture-tcp        Pornire tcpdump doar TCP                       ║"
	@echo "║   make capture-udp        Pornire tcpdump doar UDP                       ║"
	@echo "║   make capture-stop       Oprire toate capturile                         ║"
	@echo "║   make analyze-tcp        Analiză TCP cu tshark                          ║"
	@echo "║   make analyze-udp        Analiză UDP cu tshark                          ║"
	@echo "╠══════════════════════════════════════════════════════════════════════════╣"
	@echo "║ $(YELLOW)DOCKER (OPȚIONAL)$(NC_CLR)                                                       ║"
	@echo "║   make docker-build       Construire imagine Docker                      ║"
	@echo "║   make docker-shell       Shell interactiv în container                  ║"
	@echo "║   make docker-demo        Rulare demo în container                       ║"
	@echo "╠══════════════════════════════════════════════════════════════════════════╣"
	@echo "║ $(YELLOW)CURĂȚARE$(NC_CLR)                                                                ║"
	@echo "║   make clean              Curățare procese active                        ║"
	@echo "║   make reset              Reset complet (clean + fișiere generate)       ║"
	@echo "╚══════════════════════════════════════════════════════════════════════════╝"
	@echo ""

# =============================================================================
# SETUP & VERIFY (OBLIGATORIU)
# =============================================================================
setup:
	@echo "$(GREEN)[SETUP]$(NC_CLR) Instalare dependințe..."
	@mkdir -p $(CAPTURES_DIR) $(LOGS_DIR) $(PCAP_DIR)
	@if command -v apt-get >/dev/null 2>&1; then \
		sudo apt-get update -qq && \
		sudo DEBIAN_FRONTEND=noninteractive apt-get install -y -qq \
			python3 python3-pip python3-venv \
			mininet openvswitch-switch \
			tcpdump tshark wireshark-common \
			netcat-openbsd iproute2 net-tools curl; \
	fi
	@$(PYTHON) -m pip install --upgrade pip -q 2>/dev/null || true
	@test -f requirements.txt && $(PYTHON) -m pip install -r requirements.txt -q 2>/dev/null || true
	@echo "$(GREEN)[SETUP]$(NC_CLR) ✓ Instalare completă"

verify:
	@echo "$(GREEN)[VERIFY]$(NC_CLR) Verificare mediu de lucru..."
	@echo ""
	@echo "  Componente sistem:"
	@printf "    Python3:    " && $(PYTHON) --version 2>&1 || echo "$(RED)LIPSĂ$(NC_CLR)"
	@printf "    Mininet:    " && ($(MININET_SUDO) mn --version 2>/dev/null || echo "$(RED)LIPSĂ$(NC_CLR)")
	@printf "    tshark:     " && ($(TSHARK) -v 2>&1 | head -n1 || echo "$(RED)LIPSĂ$(NC_CLR)")
	@printf "    tcpdump:    " && ($(TCPDUMP) --version 2>&1 | head -n1 || echo "$(RED)LIPSĂ$(NC_CLR)")
	@printf "    netcat:     " && ($(NC) -h 2>&1 | head -n1 || echo "$(RED)LIPSĂ$(NC_CLR)")
	@echo ""
	@echo "  Fișiere exerciții:"
	@test -f $(EX_TCP) && echo "    $(GREEN)✓$(NC_CLR) ex_2_01_tcp.py" || echo "    $(RED)✗$(NC_CLR) ex_2_01_tcp.py LIPSĂ"
	@test -f $(EX_UDP) && echo "    $(GREEN)✓$(NC_CLR) ex_2_02_udp.py" || echo "    $(RED)✗$(NC_CLR) ex_2_02_udp.py LIPSĂ"
	@echo ""
	@echo "  Topologii Mininet:"
	@test -f $(TOPO_BASE) && echo "    $(GREEN)✓$(NC_CLR) topo_2_base.py" || echo "    $(RED)✗$(NC_CLR) topo_2_base.py LIPSĂ"
	@test -f $(TOPO_EXT) && echo "    $(GREEN)✓$(NC_CLR) topo_2_extended.py" || echo "    $(RED)✗$(NC_CLR) topo_2_extended.py LIPSĂ"
	@echo ""
	@echo "$(GREEN)[VERIFY]$(NC_CLR) ✓ Verificare completă"

test:
	@echo "$(GREEN)[TEST]$(NC_CLR) Smoke test..."
	@chmod +x scripts/verify.sh 2>/dev/null || true
	@./scripts/verify.sh 2>/dev/null || echo "$(YELLOW)[INFO]$(NC_CLR) verify.sh indisponibil, rulare verificare minimă"
	@$(PYTHON) -c "import socket; print('  Socket module: OK')" 2>/dev/null || echo "$(RED)EROARE$(NC_CLR) Socket module"
	@$(PYTHON) -c "import threading; print('  Threading module: OK')" 2>/dev/null || echo "$(RED)EROARE$(NC_CLR) Threading module"
	@echo "$(GREEN)[TEST]$(NC_CLR) ✓ Smoke test complet"

# =============================================================================
# DEMONSTRAȚII (OBLIGATORIU)
# =============================================================================
run-demo: demo-all

demo-all: clean
	@echo "$(GREEN)[DEMO]$(NC_CLR) Rulare demonstrație completă TCP + UDP..."
	@mkdir -p $(CAPTURES_DIR) $(LOGS_DIR)
	@echo ""
	@echo "  $(YELLOW)Pas 1:$(NC_CLR) Pornire server TCP..."
	@$(PYTHON) -u $(EX_TCP) server --bind $(BIND_ADDR) --port $(TCP_PORT) > $(LOGS_DIR)/tcp_server.log 2>&1 &
	@sleep 1
	@echo "  $(YELLOW)Pas 2:$(NC_CLR) Pornire captură TCP..."
	@sudo $(TCPDUMP) -i lo -w $(CAPTURES_DIR)/demo_tcp.pcap tcp port $(TCP_PORT) > /dev/null 2>&1 &
	@sleep 0.5
	@echo "  $(YELLOW)Pas 3:$(NC_CLR) Trimitere mesaje TCP..."
	@$(PYTHON) $(EX_TCP) client --host 127.0.0.1 --port $(TCP_PORT) --message "Hello TCP #1"
	@$(PYTHON) $(EX_TCP) client --host 127.0.0.1 --port $(TCP_PORT) --message "Hello TCP #2"
	@sleep 0.5
	@sudo pkill -f "tcpdump.*tcp port" 2>/dev/null || true
	@pkill -f "ex_2_01_tcp.py server" 2>/dev/null || true
	@echo ""
	@echo "  $(YELLOW)Pas 4:$(NC_CLR) Pornire server UDP..."
	@$(PYTHON) -u $(EX_UDP) server --bind $(BIND_ADDR) --port $(UDP_PORT) > $(LOGS_DIR)/udp_server.log 2>&1 &
	@sleep 1
	@echo "  $(YELLOW)Pas 5:$(NC_CLR) Pornire captură UDP..."
	@sudo $(TCPDUMP) -i lo -w $(CAPTURES_DIR)/demo_udp.pcap udp port $(UDP_PORT) > /dev/null 2>&1 &
	@sleep 0.5
	@echo "  $(YELLOW)Pas 6:$(NC_CLR) Trimitere mesaje UDP..."
	@$(PYTHON) $(EX_UDP) client --host 127.0.0.1 --port $(UDP_PORT) --once "ping"
	@$(PYTHON) $(EX_UDP) client --host 127.0.0.1 --port $(UDP_PORT) --once "upper:hello"
	@sleep 0.5
	@sudo pkill -f "tcpdump.*udp port" 2>/dev/null || true
	@pkill -f "ex_2_02_udp.py server" 2>/dev/null || true
	@echo ""
	@echo "$(GREEN)[DEMO]$(NC_CLR) ✓ Demonstrație completă"
	@echo "  Capturi disponibile în: $(CAPTURES_DIR)/"
	@echo "  Loguri disponibile în: $(LOGS_DIR)/"
	@echo ""
	@echo "  $(YELLOW)Următorii pași:$(NC_CLR)"
	@echo "    make analyze-tcp    # Vizualizare handshake TCP"
	@echo "    make analyze-udp    # Vizualizare trafic UDP"

run-lab:
	@echo "$(GREEN)[LAB]$(NC_CLR) Pornire laborator interactiv..."
	@echo "  1. Deschide terminal nou pentru server"
	@echo "  2. Rulează: make tcp-server"
	@echo "  3. În acest terminal, rulează: make tcp-client MSG=\"mesajul tău\""
	@echo ""
	@read -p "Apasă ENTER pentru a porni serverul TCP în acest terminal..."
	@make tcp-server

demo-tcp:
	@echo "$(GREEN)[DEMO-TCP]$(NC_CLR) Demonstrație TCP..."
	@$(PYTHON) -u $(EX_TCP) server --bind $(BIND_ADDR) --port $(TCP_PORT) &
	@sleep 1 && $(PYTHON) $(EX_TCP) client --host 127.0.0.1 --port $(TCP_PORT) --message $(MSG)
	@pkill -f "ex_2_01_tcp.py server" 2>/dev/null || true

demo-udp:
	@echo "$(GREEN)[DEMO-UDP]$(NC_CLR) Demonstrație UDP..."
	@$(PYTHON) -u $(EX_UDP) server --bind $(BIND_ADDR) --port $(UDP_PORT) &
	@sleep 1 && $(PYTHON) $(EX_UDP) client --host 127.0.0.1 --port $(UDP_PORT) --once "ping"
	@pkill -f "ex_2_02_udp.py server" 2>/dev/null || true

# =============================================================================
# MININET
# =============================================================================
mininet-cli:
	@echo "$(GREEN)[MININET]$(NC_CLR) Pornire CLI topologie bază (3 hosturi, 1 switch)..."
	@echo "  Comenzi utile în Mininet:"
	@echo "    nodes          - lista noduri"
	@echo "    net            - topologia"
	@echo "    pingall        - test conectivitate"
	@echo "    h1 ping h2     - ping între hosturi"
	@echo ""
	@$(MININET_SUDO) $(PYTHON) $(TOPO_BASE) --cli

mininet-extended:
	@echo "$(GREEN)[MININET]$(NC_CLR) Pornire CLI topologie extinsă (2 subrețele + router)..."
	@$(MININET_SUDO) $(PYTHON) $(TOPO_EXT) --cli

mininet-test:
	@echo "$(GREEN)[MININET]$(NC_CLR) Test automat conectivitate..."
	@$(MININET_SUDO) $(PYTHON) $(TOPO_BASE) --test

mininet-clean:
	@echo "$(GREEN)[MININET]$(NC_CLR) Curățare sesiuni anterioare..."
	@$(MININET_SUDO) mn -c 2>/dev/null || true
	@echo "$(GREEN)[MININET]$(NC_CLR) ✓ Curățat"

# =============================================================================
# SERVER / CLIENT
# =============================================================================
tcp-server:
	@echo "$(GREEN)[TCP-SERVER]$(NC_CLR) Pornire pe $(BIND_ADDR):$(TCP_PORT)..."
	@$(PYTHON) -u $(EX_TCP) server --bind $(BIND_ADDR) --port $(TCP_PORT)

tcp-client:
	@echo "$(GREEN)[TCP-CLIENT]$(NC_CLR) Trimitere către 127.0.0.1:$(TCP_PORT)..."
	@$(PYTHON) $(EX_TCP) client --host 127.0.0.1 --port $(TCP_PORT) --message $(MSG)

udp-server:
	@echo "$(GREEN)[UDP-SERVER]$(NC_CLR) Pornire pe $(BIND_ADDR):$(UDP_PORT)..."
	@$(PYTHON) -u $(EX_UDP) server --bind $(BIND_ADDR) --port $(UDP_PORT)

udp-client:
	@echo "$(GREEN)[UDP-CLIENT]$(NC_CLR) Client interactiv către 127.0.0.1:$(UDP_PORT)..."
	@$(PYTHON) $(EX_UDP) client --host 127.0.0.1 --port $(UDP_PORT) --interactive

N ?= 10
load-test:
	@echo "$(GREEN)[LOAD-TEST]$(NC_CLR) Test cu $(N) clienți concurenți..."
	@$(PYTHON) $(EX_TCP) load --host 127.0.0.1 --port $(TCP_PORT) --clients $(N)

# =============================================================================
# CAPTURI (OBLIGATORIU)
# =============================================================================
capture: capture-tcp capture-udp
	@echo "$(GREEN)[CAPTURE]$(NC_CLR) Capturi active pentru TCP și UDP"

capture-tcp:
	@mkdir -p $(CAPTURES_DIR)
	@echo "$(GREEN)[CAPTURE]$(NC_CLR) TCP pe lo:$(TCP_PORT)..."
	@sudo $(TCPDUMP) -i lo -w $(CAPTURES_DIR)/capture_tcp.pcap tcp port $(TCP_PORT) &
	@echo "  PID: $$(pgrep -f 'tcpdump.*tcp port')"

capture-udp:
	@mkdir -p $(CAPTURES_DIR)
	@echo "$(GREEN)[CAPTURE]$(NC_CLR) UDP pe lo:$(UDP_PORT)..."
	@sudo $(TCPDUMP) -i lo -w $(CAPTURES_DIR)/capture_udp.pcap udp port $(UDP_PORT) &
	@echo "  PID: $$(pgrep -f 'tcpdump.*udp port')"

capture-stop:
	@echo "$(GREEN)[CAPTURE]$(NC_CLR) Oprire capturi..."
	@sudo pkill tcpdump 2>/dev/null || echo "$(YELLOW)[INFO]$(NC_CLR) Niciun tcpdump activ"

analyze-tcp:
	@echo "$(GREEN)[ANALYZE]$(NC_CLR) Analiză captură TCP..."
	@if [ -f $(CAPTURES_DIR)/demo_tcp.pcap ]; then \
		echo ""; \
		echo "  Frame | IP Sursă     | Port | IP Dest      | Port | Flags"; \
		echo "  ------|--------------|------|--------------|------|------"; \
		$(TSHARK) -r $(CAPTURES_DIR)/demo_tcp.pcap -Y "tcp" -T fields \
			-e frame.number -e ip.src -e tcp.srcport -e ip.dst -e tcp.dstport -e tcp.flags.str \
			2>/dev/null | while read line; do echo "  $$line"; done; \
		echo ""; \
		echo "$(GREEN)[ANALYZE]$(NC_CLR) Handshake-ul TCP (SYN, SYN-ACK, ACK) identificabil în primele 3 pachete"; \
	else \
		echo "$(RED)[ERROR]$(NC_CLR) Captură TCP lipsă. Rulează mai întâi: make demo-all"; \
	fi

analyze-udp:
	@echo "$(GREEN)[ANALYZE]$(NC_CLR) Analiză captură UDP..."
	@if [ -f $(CAPTURES_DIR)/demo_udp.pcap ]; then \
		echo ""; \
		echo "  Frame | IP Sursă     | Port | IP Dest      | Port | Lungime"; \
		echo "  ------|--------------|------|--------------|------|--------"; \
		$(TSHARK) -r $(CAPTURES_DIR)/demo_udp.pcap -Y "udp" -T fields \
			-e frame.number -e ip.src -e udp.srcport -e ip.dst -e udp.dstport -e frame.len \
			2>/dev/null | while read line; do echo "  $$line"; done; \
		echo ""; \
		echo "$(GREEN)[ANALYZE]$(NC_CLR) UDP: observă lipsa handshake-ului și overhead-ul redus"; \
	else \
		echo "$(RED)[ERROR]$(NC_CLR) Captură UDP lipsă. Rulează mai întâi: make demo-all"; \
	fi

# =============================================================================
# DOCKER (OPȚIONAL)
# =============================================================================
docker-build:
	@echo "$(GREEN)[DOCKER]$(NC_CLR) Construire imagine..."
	@docker build -t $(DOCKER_IMAGE) -f docker/Dockerfile .

docker-shell:
	@echo "$(GREEN)[DOCKER]$(NC_CLR) Shell interactiv..."
	@docker run -it --rm --privileged \
		-v $(ROOT_DIR):/workspace -w /workspace \
		$(DOCKER_IMAGE) /bin/bash

docker-demo:
	@echo "$(GREEN)[DOCKER]$(NC_CLR) Rulare demo în container..."
	@docker run --rm --privileged \
		-v $(ROOT_DIR):/workspace -w /workspace \
		$(DOCKER_IMAGE) make demo-all

# =============================================================================
# CURĂȚARE (OBLIGATORIU)
# =============================================================================
clean:
	@echo "$(GREEN)[CLEAN]$(NC_CLR) Curățare procese..."
	@pkill -f "ex_2_01_tcp.py" 2>/dev/null || true
	@pkill -f "ex_2_02_udp.py" 2>/dev/null || true
	@sudo pkill tcpdump 2>/dev/null || true
	@$(MININET_SUDO) mn -c 2>/dev/null || true
	@echo "$(GREEN)[CLEAN]$(NC_CLR) ✓"

reset: clean
	@echo "$(GREEN)[RESET]$(NC_CLR) Reset complet..."
	@rm -rf $(CAPTURES_DIR)/*.pcap $(LOGS_DIR)/*.log $(PCAP_DIR)/*.pcap
	@rm -rf __pycache__ */__pycache__ */*/__pycache__
	@rm -rf *.pyc */*.pyc */*/*.pyc
	@echo "$(GREEN)[RESET]$(NC_CLR) ✓"

# =============================================================================
# DEFAULT
# =============================================================================
.DEFAULT_GOAL := help
