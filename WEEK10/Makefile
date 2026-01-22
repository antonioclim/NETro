# Makefile – Săptămâna 10: HTTP/HTTPS, REST, SOAP + Servicii de Rețea
# Rețele de Calculatoare, ASE București 2025-2026
# Revolvix&Hypotheticalandrei

SHELL := /bin/bash
.PHONY: help check setup demo run-demo run-lab docker-up docker-down docker-build docker-debug docker-logs \
        mininet-cli mininet-test mininet-clean tcpdump capture clean reset verify slides selftest \
        dns-test ssh-test ftp-test https-test rest-test all run-all smoke-test artifacts

# Culori pentru output
GREEN  := \033[0;32m
YELLOW := \033[0;33m
RED    := \033[0;31m
BLUE   := \033[0;34m
CYAN   := \033[0;36m
NC     := \033[0m

# Directoare
ROOT_DIR    := $(shell pwd)
DOCKER_DIR  := $(ROOT_DIR)/docker
PYTHON_DIR  := $(ROOT_DIR)/python
MININET_DIR := $(ROOT_DIR)/mininet
SLIDES_DIR  := $(ROOT_DIR)/slides
DOCS_DIR    := $(ROOT_DIR)/docs
SCRIPTS_DIR := $(ROOT_DIR)/scripts
CERTS_DIR   := $(ROOT_DIR)/certs
PCAP_DIR    := $(ROOT_DIR)/pcap

# Porturi servicii
DNS_PORT    := 5353
SSH_PORT    := 2222
FTP_PORT    := 2121
HTTPS_PORT  := 8443
HTTP_PORT   := 8000

# Timestamp pentru log-uri
TS := $(shell date +%Y%m%d_%H%M%S)

#=============================================================================
# HELP
#=============================================================================

help:
	@echo ""
	@echo "$(GREEN)╔═══════════════════════════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(GREEN)║  SĂPTĂMÂNA 10 – HTTP/HTTPS, REST, SOAP + Servicii de Rețea (DNS, SSH, FTP)    ║$(NC)"
	@echo "$(GREEN)║  Rețele de Calculatoare | ASE București | 2025-2026                           ║$(NC)"
	@echo "$(GREEN)╚═══════════════════════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "$(YELLOW)═══ COMENZI PRINCIPALE ═══$(NC)"
	@echo "  $(CYAN)make check$(NC)         Verifică dependențele și mediul"
	@echo "  $(CYAN)make setup$(NC)         Instalare completă (venv + dependențe)"
	@echo "  $(CYAN)make demo$(NC)          Rulează demonstrația completă"
	@echo "  $(CYAN)make verify$(NC)        Verificare că totul funcționează"
	@echo "  $(CYAN)make all$(NC)           Setup + Demo complet"
	@echo ""
	@echo "$(YELLOW)═══ DOCKER COMPOSE (SEMINAR) ═══$(NC)"
	@echo "  $(CYAN)make docker-up$(NC)     Pornește serviciile (DNS, SSH, FTP, Web)"
	@echo "  $(CYAN)make docker-down$(NC)   Oprește serviciile"
	@echo "  $(CYAN)make docker-build$(NC)  Reconstruiește imaginile"
	@echo "  $(CYAN)make docker-debug$(NC)  Intră în containerul debug"
	@echo "  $(CYAN)make docker-logs$(NC)   Afișează log-urile serviciilor"
	@echo ""
	@echo "$(YELLOW)═══ TESTE INDIVIDUALE SERVICII ═══$(NC)"
	@echo "  $(CYAN)make dns-test$(NC)      Testează DNS (implicit Docker + custom)"
	@echo "  $(CYAN)make ssh-test$(NC)      Testează SSH + Paramiko"
	@echo "  $(CYAN)make ftp-test$(NC)      Testează FTP programatic"
	@echo "  $(CYAN)make https-test$(NC)    Testează server HTTPS local"
	@echo "  $(CYAN)make rest-test$(NC)     Testează nivelurile REST"
	@echo ""
	@echo "$(YELLOW)═══ MININET (LABORATOR AVANSAT) ═══$(NC)"
	@echo "  $(CYAN)make mininet-cli$(NC)   Pornește CLI Mininet"
	@echo "  $(CYAN)make mininet-test$(NC)  Rulează testul automat"
	@echo "  $(CYAN)make mininet-clean$(NC) Curățare Mininet"
	@echo ""
	@echo "$(YELLOW)═══ CAPTURI ȘI DIAGNOSTICARE ═══$(NC)"
	@echo "  $(CYAN)make capture$(NC)       Captură trafic cu tshark (porturi servicii)"
	@echo "  $(CYAN)make tcpdump$(NC)       Captură cu tcpdump (alternativă)"
	@echo "  $(CYAN)make slides$(NC)        Deschide prezentările HTML"
	@echo "  $(CYAN)make selftest$(NC)      Rulează self-test Python"
	@echo ""
	@echo "$(YELLOW)═══ CURĂȚARE ═══$(NC)"
	@echo "  $(CYAN)make clean$(NC)         Curățare fișiere temporare"
	@echo "  $(CYAN)make reset$(NC)         Reset complet (inclusiv volume Docker)"
	@echo ""
	@echo "$(YELLOW)═══ AUTOMATIZĂRI STANDARD ═══$(NC)"
	@echo "  $(CYAN)make run-all$(NC)       Demo automat complet (generează artifacts/)"
	@echo "  $(CYAN)make smoke-test$(NC)    Verificare artefacte generate"
	@echo ""

#=============================================================================
# CHECK DEPENDENCIES
#=============================================================================

check:
	@echo ""
	@echo "$(YELLOW)╔═══════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(YELLOW)║              VERIFICARE DEPENDENȚE                        ║$(NC)"
	@echo "$(YELLOW)╚═══════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@printf "%-20s" "Python 3.11+:" && (python3 -c "import sys; assert sys.version_info >= (3,11)" 2>/dev/null && python3 --version | cut -d' ' -f2 && echo -n "") || echo "$(RED)LIPSEȘTE sau < 3.11$(NC)"
	@printf "%-20s" "Docker:" && (docker --version 2>/dev/null | cut -d' ' -f3 | tr -d ',') || echo "$(RED)LIPSEȘTE$(NC)"
	@printf "%-20s" "Docker Compose:" && (docker compose version 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1) || echo "$(RED)LIPSEȘTE$(NC)"
	@printf "%-20s" "openssl:" && (openssl version 2>/dev/null | cut -d' ' -f2) || echo "$(RED)NECESAR$(NC)"
	@printf "%-20s" "curl:" && (curl --version 2>/dev/null | head -1 | cut -d' ' -f2) || echo "$(YELLOW)RECOMANDAT$(NC)"
	@printf "%-20s" "dig:" && (dig -v 2>&1 | head -1 | grep -oE '[0-9]+\.[0-9]+' | head -1 || echo "prezent") || echo "$(YELLOW)RECOMANDAT$(NC)"
	@printf "%-20s" "tshark:" && (tshark --version 2>/dev/null | head -1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1) || echo "$(YELLOW)OPȚIONAL$(NC)"
	@printf "%-20s" "Mininet:" && (mn --version 2>/dev/null) || echo "$(YELLOW)OPȚIONAL$(NC)"
	@echo ""
	@echo "$(GREEN)Verificare completă.$(NC)"
	@echo ""

#=============================================================================
# SETUP
#=============================================================================

setup:
	@echo "$(YELLOW)Instalare completă...$(NC)"
	@echo ""
	@# Create virtual environment if not exists
	@if [ ! -d ".venv" ]; then \
		echo "$(CYAN)Creare virtual environment...$(NC)"; \
		python3 -m venv .venv; \
	fi
	@echo "$(CYAN)Instalare dependențe Python...$(NC)"
	@. .venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt
	@echo ""
	@echo "$(CYAN)Generare certificate self-signed...$(NC)"
	@mkdir -p $(CERTS_DIR)
	@if [ ! -f $(CERTS_DIR)/server.crt ]; then \
		openssl req -x509 -newkey rsa:2048 -nodes \
			-keyout $(CERTS_DIR)/server.key -out $(CERTS_DIR)/server.crt \
			-days 7 -subj "/CN=lab.retele.local/O=ASE-CSIE/C=RO" 2>/dev/null; \
		echo "$(GREEN)Certificate generate: $(CERTS_DIR)/server.crt$(NC)"; \
	else \
		echo "Certificate deja existente."; \
	fi
	@echo ""
	@echo "$(GREEN)Setup complet!$(NC)"
	@echo "Activați virtual environment cu: $(CYAN)source .venv/bin/activate$(NC)"

#=============================================================================
# DOCKER COMPOSE
#=============================================================================

docker-up:
	@echo "$(YELLOW)Pornire servicii Docker...$(NC)"
	@cd $(DOCKER_DIR) && docker compose up -d --build
	@echo ""
	@echo "$(GREEN)╔═══════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(GREEN)║              SERVICII PORNITE                             ║$(NC)"
	@echo "$(GREEN)╚═══════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "  $(CYAN)Web demo:$(NC)     http://localhost:$(HTTP_PORT)"
	@echo "  $(CYAN)DNS custom:$(NC)   dig @localhost -p $(DNS_PORT) myservice.lab.local"
	@echo "  $(CYAN)SSH server:$(NC)   ssh labuser@localhost -p $(SSH_PORT) (parola: labpass)"
	@echo "  $(CYAN)FTP server:$(NC)   ftp localhost $(FTP_PORT) (user: labftp/labftp)"
	@echo ""
	@echo "Container debug: $(YELLOW)make docker-debug$(NC)"
	@echo ""

docker-down:
	@echo "$(YELLOW)Oprire servicii Docker...$(NC)"
	@cd $(DOCKER_DIR) && docker compose down
	@echo "$(GREEN)Servicii oprite.$(NC)"

docker-build:
	@echo "$(YELLOW)Reconstruire imagini Docker (fără cache)...$(NC)"
	@cd $(DOCKER_DIR) && docker compose build --no-cache

docker-debug:
	@echo "$(YELLOW)Intrare în containerul debug...$(NC)"
	@echo ""
	@echo "$(CYAN)Comenzi utile în container:$(NC)"
	@echo "  dig web                                    # DNS implicit Docker"
	@echo "  dig @dns-server -p 5353 myservice.lab.local  # DNS custom"
	@echo "  curl http://web:8000                      # Test web"
	@echo "  ssh labuser@ssh-server                    # SSH (parola: labpass)"
	@echo "  lftp -u labftp,labftp ftp-server:2121    # FTP"
	@echo ""
	@cd $(DOCKER_DIR) && docker compose exec debug sh

docker-logs:
	@cd $(DOCKER_DIR) && docker compose logs -f --tail=50

#=============================================================================
# INDIVIDUAL SERVICE TESTS
#=============================================================================

dns-test: docker-up
	@echo ""
	@echo "$(YELLOW)═══ TEST DNS ═══$(NC)"
	@echo ""
	@echo "$(CYAN)1. DNS implicit Docker (rezolvare 'web'):$(NC)"
	@cd $(DOCKER_DIR) && docker compose exec debug dig web +short 2>/dev/null || echo "  (containerul debug nu rulează)"
	@echo ""
	@echo "$(CYAN)2. DNS custom (myservice.lab.local):$(NC)"
	@cd $(DOCKER_DIR) && docker compose exec debug dig @dns-server -p 5353 myservice.lab.local +short 2>/dev/null || echo "  (serviciul DNS nu răspunde)"
	@echo ""
	@echo "$(CYAN)3. DNS custom (api.lab.local):$(NC)"
	@cd $(DOCKER_DIR) && docker compose exec debug dig @dns-server -p 5353 api.lab.local +short 2>/dev/null || echo "  (înregistrare inexistentă)"
	@echo ""
	@echo "$(GREEN)Test DNS complet.$(NC)"

ssh-test: docker-up
	@echo ""
	@echo "$(YELLOW)═══ TEST SSH + PARAMIKO ═══$(NC)"
	@echo ""
	@cd $(DOCKER_DIR) && docker compose exec ssh-client python3 /app/paramiko_client.py 2>/dev/null || echo "$(RED)Eroare la rulare Paramiko$(NC)"
	@echo ""
	@echo "$(GREEN)Test SSH complet.$(NC)"

ftp-test: docker-up
	@echo ""
	@echo "$(YELLOW)═══ TEST FTP ═══$(NC)"
	@echo ""
	@python3 -c "\
from ftplib import FTP; \
import sys; \
try: \
    f = FTP(); \
    f.connect('127.0.0.1', $(FTP_PORT), timeout=5); \
    f.login('labftp', 'labftp'); \
    print('  Conectat la FTP'); \
    print('  Director curent:', f.pwd()); \
    print('  Fișiere:', f.nlst()); \
    f.quit(); \
    print('  FTP OK'); \
except Exception as e: \
    print('  Eroare FTP:', e); \
    sys.exit(1)" || echo "$(RED)Test FTP eșuat$(NC)"
	@echo ""
	@echo "$(GREEN)Test FTP complet.$(NC)"

https-test:
	@echo ""
	@echo "$(YELLOW)═══ TEST HTTPS LOCAL ═══$(NC)"
	@echo ""
	@if [ -f $(PYTHON_DIR)/exercises/ex_10_01_https.py ]; then \
		cd $(ROOT_DIR) && python3 $(PYTHON_DIR)/exercises/ex_10_01_https.py selftest; \
	else \
		echo "$(RED)Fișierul ex_10_01_https.py nu există$(NC)"; \
	fi
	@echo ""
	@echo "$(GREEN)Test HTTPS complet.$(NC)"

rest-test:
	@echo ""
	@echo "$(YELLOW)═══ TEST REST MATURITY LEVELS ═══$(NC)"
	@echo ""
	@if [ -f $(PYTHON_DIR)/exercises/ex_10_02_rest_levels.py ]; then \
		cd $(ROOT_DIR) && python3 $(PYTHON_DIR)/exercises/ex_10_02_rest_levels.py selftest; \
	else \
		echo "$(RED)Fișierul ex_10_02_rest_levels.py nu există$(NC)"; \
	fi
	@echo ""
	@echo "$(GREEN)Test REST complet.$(NC)"

#=============================================================================
# MININET
#=============================================================================

mininet-cli:
	@echo "$(YELLOW)Pornire CLI Mininet...$(NC)"
	@echo ""
	@echo "$(CYAN)În CLI, rulați:$(NC)"
	@echo "  h1 python3 -m http.server 8000 &"
	@echo "  h2 curl http://10.0.0.1:8000/"
	@echo ""
	@if [ -f $(MININET_DIR)/topologies/topo_10_base.py ]; then \
		sudo python3 $(MININET_DIR)/topologies/topo_10_base.py --cli; \
	else \
		echo "$(RED)Fișierul topo_10_base.py nu există$(NC)"; \
		echo "Alternativă: sudo mn --topo single,3"; \
	fi

mininet-test:
	@echo "$(YELLOW)Rulare test automat Mininet...$(NC)"
	@if [ -f $(MININET_DIR)/topologies/topo_10_base.py ]; then \
		sudo python3 $(MININET_DIR)/topologies/topo_10_base.py --test; \
	else \
		echo "$(RED)Fișierul topo_10_base.py nu există$(NC)"; \
	fi

mininet-clean:
	@echo "$(YELLOW)Curățare Mininet...$(NC)"
	@sudo mn -c 2>/dev/null || true
	@echo "$(GREEN)Mininet curățat.$(NC)"

#=============================================================================
# CAPTURE & DIAGNOSTICS
#=============================================================================

capture:
	@echo "$(YELLOW)Captură trafic cu tshark...$(NC)"
	@echo "Apăsați Ctrl+C pentru oprire."
	@mkdir -p $(PCAP_DIR)
	@tshark -i any -f "tcp port $(HTTP_PORT) or tcp port $(HTTPS_PORT) or tcp port $(SSH_PORT) or tcp port $(FTP_PORT) or udp port $(DNS_PORT)" \
		-w $(PCAP_DIR)/capture_$(TS).pcap 2>/dev/null || \
		echo "$(RED)tshark nu este disponibil. Încercați: make tcpdump$(NC)"

tcpdump:
	@echo "$(YELLOW)Captură trafic cu tcpdump...$(NC)"
	@echo "Apăsați Ctrl+C pentru oprire."
	@mkdir -p $(PCAP_DIR)
	@sudo tcpdump -i any -nn "tcp port $(HTTP_PORT) or tcp port $(HTTPS_PORT) or tcp port $(SSH_PORT) or tcp port $(FTP_PORT) or udp port $(DNS_PORT)" \
		-w $(PCAP_DIR)/capture_$(TS).pcap -v

slides:
	@echo "$(YELLOW)Deschidere prezentări HTML...$(NC)"
	@if command -v xdg-open >/dev/null 2>&1; then \
		xdg-open $(SLIDES_DIR)/theory.html 2>/dev/null & \
		sleep 0.5; \
		xdg-open $(SLIDES_DIR)/seminar.html 2>/dev/null & \
		sleep 0.5; \
		xdg-open $(SLIDES_DIR)/lab.html 2>/dev/null & \
	elif command -v open >/dev/null 2>&1; then \
		open $(SLIDES_DIR)/theory.html; \
		open $(SLIDES_DIR)/seminar.html; \
		open $(SLIDES_DIR)/lab.html; \
	else \
		echo "Deschideți manual:"; \
		echo "  $(SLIDES_DIR)/theory.html"; \
		echo "  $(SLIDES_DIR)/seminar.html"; \
		echo "  $(SLIDES_DIR)/lab.html"; \
	fi

selftest:
	@echo "$(YELLOW)Rulare self-test Python...$(NC)"
	@cd $(ROOT_DIR) && python3 -m pytest tests/ -v 2>/dev/null || \
		(echo "pytest nu este instalat sau tests/ nu există"; \
		 echo "Încercați: make https-test")

#=============================================================================
# VERIFY
#=============================================================================

verify: check
	@echo ""
	@echo "$(YELLOW)╔═══════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(YELLOW)║              VERIFICARE COMPLETĂ                          ║$(NC)"
	@echo "$(YELLOW)╚═══════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "$(CYAN)1. Verificare structură fișiere...$(NC)"
	@test -f $(ROOT_DIR)/Makefile && echo "  ✓ Makefile" || echo "  ✗ Makefile lipsește"
	@test -f $(ROOT_DIR)/requirements.txt && echo "  ✓ requirements.txt" || echo "  ✗ requirements.txt lipsește"
	@test -d $(DOCKER_DIR) && echo "  ✓ docker/" || echo "  ✗ docker/ lipsește"
	@test -d $(PYTHON_DIR) && echo "  ✓ python/" || echo "  ✗ python/ lipsește"
	@test -d $(SLIDES_DIR) && echo "  ✓ slides/" || echo "  ✗ slides/ lipsește"
	@echo ""
	@echo "$(CYAN)2. Verificare Docker...$(NC)"
	@docker info >/dev/null 2>&1 && echo "  ✓ Docker daemon rulează" || echo "  ✗ Docker daemon nu rulează"
	@echo ""
	@echo "$(CYAN)3. Verificare porturi libere...$(NC)"
	@ss -tulpn 2>/dev/null | grep -q ":$(DNS_PORT) " && echo "  ⚠ Port $(DNS_PORT) ocupat" || echo "  ✓ Port $(DNS_PORT) liber"
	@ss -tulpn 2>/dev/null | grep -q ":$(SSH_PORT) " && echo "  ⚠ Port $(SSH_PORT) ocupat" || echo "  ✓ Port $(SSH_PORT) liber"
	@ss -tulpn 2>/dev/null | grep -q ":$(FTP_PORT) " && echo "  ⚠ Port $(FTP_PORT) ocupat" || echo "  ✓ Port $(FTP_PORT) liber"
	@echo ""
	@echo "$(GREEN)Verificare completă.$(NC)"

#=============================================================================
# DEMO COMPLET
#=============================================================================

run-demo: demo
demo: check docker-up
	@echo ""
	@echo "$(GREEN)╔═══════════════════════════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(GREEN)║                         DEMO SERVICII REȚEA                                   ║$(NC)"
	@echo "$(GREEN)╚═══════════════════════════════════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@sleep 2
	@$(MAKE) dns-test
	@echo ""
	@sleep 1
	@$(MAKE) ftp-test
	@echo ""
	@sleep 1
	@echo "$(YELLOW)Pentru SSH, rulați: make ssh-test$(NC)"
	@echo "$(YELLOW)Pentru HTTPS local, rulați: make https-test$(NC)"
	@echo ""
	@echo "$(GREEN)╔═══════════════════════════════════════════════════════════════════════════════╗$(NC)"
	@echo "$(GREEN)║  Demo complet. Serviciile rulează în background.                              ║$(NC)"
	@echo "$(GREEN)║  Oprire: make docker-down                                                     ║$(NC)"
	@echo "$(GREEN)║  Container debug: make docker-debug                                           ║$(NC)"
	@echo "$(GREEN)╚═══════════════════════════════════════════════════════════════════════════════╝$(NC)"

run-lab: demo
	@echo ""
	@echo "$(CYAN)Pașii laboratorului:$(NC)"
	@echo "  1. make docker-debug    → intrați în container"
	@echo "  2. dig web              → testați DNS implicit"
	@echo "  3. dig @dns-server -p 5353 myservice.lab.local"
	@echo "  4. curl http://web:8000 → testați HTTP"
	@echo "  5. ssh labuser@ssh-server → testați SSH"
	@echo ""

#=============================================================================
# CLEANUP
#=============================================================================

clean:
	@echo "$(YELLOW)Curățare fișiere temporare...$(NC)"
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.log" -delete 2>/dev/null || true
	@find . -type f -name ".DS_Store" -delete 2>/dev/null || true
	@rm -rf $(PCAP_DIR)/*.pcap 2>/dev/null || true
	@echo "$(GREEN)Curățare completă.$(NC)"

reset: clean docker-down mininet-clean
	@echo "$(YELLOW)Reset complet...$(NC)"
	@cd $(DOCKER_DIR) && docker compose down -v 2>/dev/null || true
	@rm -rf $(CERTS_DIR)/*.crt $(CERTS_DIR)/*.key 2>/dev/null || true
	@rm -rf .venv 2>/dev/null || true
	@echo "$(GREEN)Reset complet.$(NC)"

#=============================================================================
# DEMO AUTOMAT + SMOKE TEST (STANDARD TRANSVERSAL)
#=============================================================================

run-all: artifacts
	@echo "$(YELLOW)Rulare demo automat complet...$(NC)"
	@$(SCRIPTS_DIR)/run_all.sh
	@echo "$(GREEN)Demo automat finalizat.$(NC)"

smoke-test:
	@echo "$(YELLOW)Rulare smoke test...$(NC)"
	@$(ROOT_DIR)/tests/smoke_test.sh
	@echo ""

artifacts:
	@mkdir -p $(ROOT_DIR)/artifacts

#=============================================================================
# ALL
#=============================================================================

all: setup demo
	@echo ""
	@echo "$(GREEN)Instalare și demo complete!$(NC)"
