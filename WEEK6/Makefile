# ============================================================================
# Makefile – Săptămâna 6: Rețele de Calculatoare
# NAT/PAT · ARP · DHCP · NDP · ICMP · SDN/OpenFlow
# ASE-CSIE, Informatică Economică
# ============================================================================

.PHONY: all setup check clean help \
        nat-demo sdn-demo routing-demo run-all \
        controller-start controller-stop controller-status \
        smoke-test docker-build docker-run slides \
        install-deps verify-tools capture verify reset

# Colors for terminal output
GREEN  := \033[0;32m
YELLOW := \033[0;33m
RED    := \033[0;31m
CYAN   := \033[0;36m
BOLD   := \033[1m
RESET  := \033[0m

# Paths
SCRIPTS_DIR    := scripts
TOPO_DIR       := seminar/mininet/topologies
CONTROLLER_DIR := seminar/python/controllers
APPS_DIR       := seminar/python/apps
SLIDES_DIR     := slides
TESTS_DIR      := tests
PCAP_DIR       := pcap

# Controller settings
CONTROLLER_PY  := $(CONTROLLER_DIR)/sdn_policy_controller.py
CONTROLLER_PID := /tmp/osken_controller.pid
OFP_PORT       := 6633

# ============================================================================
# DEFAULT & HELP
# ============================================================================

all: help

help:
	@echo ""
	@echo "$(BOLD)═══════════════════════════════════════════════════════════════$(RESET)"
	@echo "$(CYAN)  Starterkit S6 – NAT/PAT, SDN, Analiza traficului$(RESET)"
	@echo "$(BOLD)═══════════════════════════════════════════════════════════════$(RESET)"
	@echo ""
	@echo "$(BOLD)Instalare & Verificare:$(RESET)"
	@echo "  $(GREEN)make setup$(RESET)        – Instalează toate dependențele"
	@echo "  $(GREEN)make check$(RESET)        – Verifică uneltele disponibile"
	@echo "  $(GREEN)make verify-tools$(RESET) – Verificare detaliată versiuni"
	@echo ""
	@echo "$(BOLD)Demo-uri Interactive:$(RESET)"
	@echo "  $(GREEN)make nat-demo$(RESET)     – Pornește topologia NAT cu PAT"
	@echo "  $(GREEN)make sdn-demo$(RESET)     – Pornește controller + topologie SDN"
	@echo "  $(GREEN)make routing-demo$(RESET) – Topologie triunghi pentru rutare"
	@echo "  $(GREEN)make run-all$(RESET)      – Demo automat (artifacts/)"
	@echo ""
	@echo "$(BOLD)Controller SDN:$(RESET)"
	@echo "  $(GREEN)make controller-start$(RESET)  – Pornește OS-Ken în background"
	@echo "  $(GREEN)make controller-stop$(RESET)   – Oprește controller-ul"
	@echo "  $(GREEN)make controller-status$(RESET) – Verifică starea controller-ului"
	@echo ""
	@echo "$(BOLD)Capturi & Verificare:$(RESET)"
	@echo "  $(GREEN)make capture$(RESET)      – Pornește captură pachete"
	@echo "  $(GREEN)make verify$(RESET)       – Verifică că demo-urile funcționează"
	@echo ""
	@echo "$(BOLD)Teste & Validare:$(RESET)"
	@echo "  $(GREEN)make smoke-test$(RESET)   – Rulează testele de validare"
	@echo ""
	@echo "$(BOLD)Docker (izolare completă):$(RESET)"
	@echo "  $(GREEN)make docker-build$(RESET) – Construiește imaginea Docker"
	@echo "  $(GREEN)make docker-run$(RESET)   – Rulează container interactiv"
	@echo ""
	@echo "$(BOLD)Prezentare & Curățare:$(RESET)"
	@echo "  $(GREEN)make slides$(RESET)       – Deschide prezentarea interactivă"
	@echo "  $(GREEN)make clean$(RESET)        – Curăță artefactele Mininet/OVS"
	@echo "  $(GREEN)make reset$(RESET)        – Reset complet (clean + kill processes)"
	@echo ""
	@echo "$(BOLD)═══════════════════════════════════════════════════════════════$(RESET)"
	@echo ""

# ============================================================================
# SETUP & DEPENDENCIES
# ============================================================================

setup:
	@echo "$(CYAN)>>> Instalare dependențe sistem...$(RESET)"
	@chmod +x $(SCRIPTS_DIR)/setup.sh 2>/dev/null || true
	@if [ -f $(SCRIPTS_DIR)/setup.sh ]; then \
		sudo $(SCRIPTS_DIR)/setup.sh; \
	else \
		echo "$(YELLOW)setup.sh nu există, instalare manuală:$(RESET)"; \
		sudo apt-get update; \
		sudo apt-get install -y python3 python3-pip mininet openvswitch-switch tcpdump tshark iptables; \
		pip3 install --break-system-packages os-ken scapy; \
	fi
	@echo "$(GREEN)✓ Setup complet!$(RESET)"

install-deps:
	@echo "$(CYAN)>>> Instalare pachete Python...$(RESET)"
	@pip3 install --break-system-packages os-ken scapy
	@echo "$(GREEN)✓ Pachete Python instalate.$(RESET)"

check:
	@echo ""
	@echo "$(BOLD)Verificare unelte necesare:$(RESET)"
	@echo ""
	@command -v python3 >/dev/null && echo "  $(GREEN)✓$(RESET) python3" || echo "  $(RED)✗$(RESET) python3"
	@command -v mn >/dev/null && echo "  $(GREEN)✓$(RESET) mininet (mn)" || echo "  $(RED)✗$(RESET) mininet"
	@command -v ovs-vsctl >/dev/null && echo "  $(GREEN)✓$(RESET) openvswitch" || echo "  $(RED)✗$(RESET) openvswitch"
	@command -v tcpdump >/dev/null && echo "  $(GREEN)✓$(RESET) tcpdump" || echo "  $(RED)✗$(RESET) tcpdump"
	@command -v tshark >/dev/null && echo "  $(GREEN)✓$(RESET) tshark" || echo "  $(RED)✗$(RESET) tshark"
	@command -v iptables >/dev/null && echo "  $(GREEN)✓$(RESET) iptables" || echo "  $(RED)✗$(RESET) iptables"
	@command -v osken-manager >/dev/null && echo "  $(GREEN)✓$(RESET) os-ken" || echo "  $(RED)✗$(RESET) os-ken (pip install os-ken)"
	@echo ""
	@python3 -c "import os_ken" 2>/dev/null && echo "  $(GREEN)✓$(RESET) os_ken (Python)" || echo "  $(RED)✗$(RESET) os_ken module"
	@python3 -c "import scapy" 2>/dev/null && echo "  $(GREEN)✓$(RESET) scapy (Python)" || echo "  $(RED)✗$(RESET) scapy module"
	@echo ""

verify-tools:
	@echo "$(BOLD)Versiuni unelte:$(RESET)"
	@echo ""
	@python3 --version 2>/dev/null || echo "python3: not found"
	@mn --version 2>/dev/null || echo "mininet: not found"
	@ovs-vsctl --version 2>/dev/null | head -1 || echo "ovs: not found"
	@tcpdump --version 2>/dev/null | head -1 || echo "tcpdump: not found"
	@tshark --version 2>/dev/null | head -1 || echo "tshark: not found"
	@pip3 show os-ken 2>/dev/null | grep -E "^(Name|Version)" || echo "os-ken: not installed"
	@echo ""

# ============================================================================
# NAT/PAT DEMO
# ============================================================================

nat-demo: clean
	@echo ""
	@echo "$(BOLD)═══════════════════════════════════════════════════════════════$(RESET)"
	@echo "$(CYAN)  Demo NAT/PAT – Observarea traducerii adreselor$(RESET)"
	@echo "$(BOLD)═══════════════════════════════════════════════════════════════$(RESET)"
	@echo ""
	@echo "$(YELLOW)Topologie:$(RESET)"
	@echo "  h1 (192.168.1.10) ──┐"
	@echo "                      ├── rnat ── h3 (203.0.113.2)"
	@echo "  h2 (192.168.1.20) ──┘    │"
	@echo "                       MASQUERADE"
	@echo ""
	@echo "$(YELLOW)Exerciții sugerate:$(RESET)"
	@echo "  1. $(BOLD)h1 ping h3$(RESET) sau $(BOLD)h1 ping 203.0.113.2$(RESET)"
	@echo "  2. $(BOLD)rnat iptables -t nat -L -n -v$(RESET) – vezi reguli NAT"
	@echo "  3. Pornește $(BOLD)nat_observer$(RESET) pe h3, apoi conectează de pe h1/h2"
	@echo ""
	@echo "$(GREEN)>>> Pornire topologie...$(RESET)"
	@echo ""
	@sudo python3 $(TOPO_DIR)/topo_nat.py --cli

# ============================================================================
# SDN / OPENFLOW DEMO
# ============================================================================

sdn-demo: clean controller-start
	@echo ""
	@echo "$(BOLD)═══════════════════════════════════════════════════════════════$(RESET)"
	@echo "$(CYAN)  Demo SDN/OpenFlow – Control centralizat$(RESET)"
	@echo "$(BOLD)═══════════════════════════════════════════════════════════════$(RESET)"
	@echo ""
	@echo "$(YELLOW)Topologie:$(RESET)"
	@echo "  h1 (10.0.6.11) ──┐"
	@echo "  h2 (10.0.6.12) ──┼── s1 (OVS) ←→ Controller (6633)"
	@echo "  h3 (10.0.6.13) ──┘"
	@echo ""
	@echo "$(YELLOW)Exerciții sugerate:$(RESET)"
	@echo "  1. $(BOLD)h1 ping 10.0.6.12$(RESET) – verifică conectivitate permisă"
	@echo "  2. $(BOLD)h1 ping 10.0.6.13$(RESET) – verifică trafic blocat"
	@echo "  3. $(BOLD)sh ovs-ofctl -O OpenFlow13 dump-flows s1$(RESET) – vezi flow-uri"
	@echo ""
	@echo "$(GREEN)>>> Pornire topologie cu controller activ...$(RESET)"
	@echo ""
	@sleep 2
	@sudo python3 $(TOPO_DIR)/topo_sdn.py --cli

# ============================================================================
# RUN-ALL (Demo automat non-interactiv)
# ============================================================================

run-all:
	@echo "$(CYAN)>>> Demo automat (produce artifacts/)...$(RESET)"
	@chmod +x $(SCRIPTS_DIR)/run_all.sh 2>/dev/null || true
	@sudo $(SCRIPTS_DIR)/run_all.sh

# ============================================================================
# CONTROLLER SDN
# ============================================================================

controller-start:
	@if [ -f $(CONTROLLER_PID) ] && kill -0 $$(cat $(CONTROLLER_PID)) 2>/dev/null; then \
		echo "$(YELLOW)Controller deja pornit (PID: $$(cat $(CONTROLLER_PID)))$(RESET)"; \
	else \
		echo "$(CYAN)>>> Pornire OS-Ken controller în background...$(RESET)"; \
		osken-manager $(CONTROLLER_PY) > /tmp/osken.log 2>&1 & \
		echo $$! > $(CONTROLLER_PID); \
		sleep 2; \
		if kill -0 $$(cat $(CONTROLLER_PID)) 2>/dev/null; then \
			echo "$(GREEN)✓ Controller pornit (PID: $$(cat $(CONTROLLER_PID)))$(RESET)"; \
		else \
			echo "$(RED)✗ Controller nu a pornit! Verifică /tmp/osken.log$(RESET)"; \
		fi \
	fi

controller-stop:
	@if [ -f $(CONTROLLER_PID) ]; then \
		echo "$(CYAN)>>> Oprire controller...$(RESET)"; \
		kill $$(cat $(CONTROLLER_PID)) 2>/dev/null || true; \
		rm -f $(CONTROLLER_PID); \
		echo "$(GREEN)✓ Controller oprit.$(RESET)"; \
	else \
		echo "$(YELLOW)Controller nu rulează.$(RESET)"; \
	fi

controller-status:
	@if [ -f $(CONTROLLER_PID) ] && kill -0 $$(cat $(CONTROLLER_PID)) 2>/dev/null; then \
		echo "$(GREEN)✓ Controller activ (PID: $$(cat $(CONTROLLER_PID)))$(RESET)"; \
		echo "  Log: /tmp/osken.log"; \
	else \
		echo "$(YELLOW)✗ Controller inactiv$(RESET)"; \
	fi

# ============================================================================
# ROUTING DEMO
# ============================================================================

routing-demo: clean
	@echo ""
	@echo "$(BOLD)═══════════════════════════════════════════════════════════════$(RESET)"
	@echo "$(CYAN)  Demo Rutare – Topologie triunghi$(RESET)"
	@echo "$(BOLD)═══════════════════════════════════════════════════════════════$(RESET)"
	@echo ""
	@echo "$(YELLOW)Topologie:$(RESET)"
	@echo "          r1 (10.0.1.1)"
	@echo "         /  \\"
	@echo "        /    \\"
	@echo "    r2 ────── r3"
	@echo "  (10.0.2.1)  (10.0.3.1)"
	@echo ""
	@echo "$(YELLOW)Exerciții sugerate:$(RESET)"
	@echo "  1. $(BOLD)r1 ip route$(RESET) – verifică rutele configurate"
	@echo "  2. $(BOLD)r1 traceroute -n 10.0.3.1$(RESET) – traseu spre r3"
	@echo "  3. Dezactivează r1-r3: $(BOLD)r1 ip link set r1-eth1 down$(RESET)"
	@echo "  4. Repetă traceroute – observă ruta alternativă"
	@echo ""
	@echo "$(GREEN)>>> Pornire topologie...$(RESET)"
	@echo ""
	@sudo python3 $(TOPO_DIR)/topo_triangle.py --cli 2>/dev/null || \
		echo "$(YELLOW)topo_triangle.py nu există în acest kit$(RESET)"

# ============================================================================
# CAPTURE & VERIFY
# ============================================================================

capture:
	@mkdir -p $(PCAP_DIR)
	@echo "$(CYAN)>>> Directorul pcap/ pregătit pentru capturi$(RESET)"
	@echo "Folosește: tcpdump -w $(PCAP_DIR)/capture.pcap -i <interface>"

verify:
	@echo "$(CYAN)>>> Verificare funcționalitate...$(RESET)"
	@echo "Rulează: make smoke-test"

# ============================================================================
# TESTING
# ============================================================================

smoke-test:
	@echo "$(CYAN)>>> Rulare teste de validare...$(RESET)"
	@if [ -f $(TESTS_DIR)/smoke_test.sh ]; then \
		chmod +x $(TESTS_DIR)/smoke_test.sh; \
		$(TESTS_DIR)/smoke_test.sh; \
	else \
		echo "$(YELLOW)smoke_test.sh nu există, rulare teste inline:$(RESET)"; \
		echo "Test NAT topology..."; \
		sudo python3 $(TOPO_DIR)/topo_nat.py --test || true; \
	fi

# ============================================================================
# DOCKER
# ============================================================================

docker-build:
	@echo "$(CYAN)>>> Construire imagine Docker...$(RESET)"
	@if [ -f docker/Dockerfile ]; then \
		docker build -t netlab-s6:latest -f docker/Dockerfile .; \
		echo "$(GREEN)✓ Imagine construită: netlab-s6:latest$(RESET)"; \
	else \
		echo "$(YELLOW)Dockerfile nu există$(RESET)"; \
	fi

docker-run:
	@echo "$(CYAN)>>> Pornire container Docker interactiv...$(RESET)"
	@docker run -it --rm --privileged \
		--name netlab-s6 \
		-v $(PWD):/workspace \
		-w /workspace \
		-p 6633:6633 \
		-p 6653:6653 \
		netlab-s6:latest \
		/bin/bash || echo "$(YELLOW)Imagine Docker nu există. Rulează: make docker-build$(RESET)"

docker-clean:
	@echo "$(CYAN)>>> Curățare containere și imagini...$(RESET)"
	@docker rm -f netlab-s6 2>/dev/null || true
	@docker rmi netlab-s6:latest 2>/dev/null || true
	@echo "$(GREEN)✓ Curățare Docker completă.$(RESET)"

# ============================================================================
# SLIDES
# ============================================================================

slides:
	@echo "$(CYAN)>>> Deschidere prezentare interactivă...$(RESET)"
	@if command -v xdg-open >/dev/null; then \
		xdg-open $(SLIDES_DIR)/theory.html 2>/dev/null || \
		echo "$(YELLOW)Deschide manual: $(SLIDES_DIR)/theory.html$(RESET)"; \
	elif command -v open >/dev/null; then \
		open $(SLIDES_DIR)/theory.html; \
	else \
		echo "$(YELLOW)Deschide manual: $(SLIDES_DIR)/theory.html$(RESET)"; \
	fi

# ============================================================================
# CLEANUP
# ============================================================================

clean: controller-stop
	@echo "$(CYAN)>>> Curățare artefacte Mininet/OVS...$(RESET)"
	@sudo mn -c 2>/dev/null || true
	@sudo pkill -9 -f "python.*topo_" 2>/dev/null || true
	@sudo pkill -9 -f "osken-manager" 2>/dev/null || true
	@rm -f $(CONTROLLER_PID)
	@sudo ip link | grep -oE "(s[0-9]+-|h[0-9]+-|r[a-z]*-)[a-z0-9]+" | xargs -I{} sudo ip link delete {} 2>/dev/null || true
	@sudo ovs-vsctl --if-exists del-br s1 2>/dev/null || true
	@sudo ovs-vsctl --if-exists del-br s2 2>/dev/null || true
	@echo "$(GREEN)✓ Curățare completă.$(RESET)"

reset: clean docker-clean
	@echo "$(CYAN)>>> Reset complet (inclusiv Docker)...$(RESET)"
	@rm -rf /tmp/osken.log /tmp/*.pcap
	@sudo systemctl restart openvswitch-switch 2>/dev/null || true
	@echo "$(GREEN)✓ Reset complet.$(RESET)"

deep-clean: reset
	@rm -rf $(PCAP_DIR)/*.pcap
	@echo "$(GREEN)✓ Curățare profundă completă.$(RESET)"
