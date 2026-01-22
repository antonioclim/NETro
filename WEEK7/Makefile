.PHONY: help setup demo test clean docker_up docker_down

help:
	@echo "Ținte:"
	@echo "  make setup      - Instalează sau validează prerechizitele"
	@echo "  make demo       - Rulează demo-ul automat (scripts/run_all.sh)"
	@echo "  make test       - Rulează smoke test-ul (tests/smoke_test.sh)"
	@echo "  make clean      - Cleanup (scripts/cleanup.sh)"
	@echo "  make docker_up  - Pornește demo-ul Docker (docker-compose up --build)"
	@echo "  make docker_down- Oprește demo-ul Docker (docker-compose down -v)"

setup:
	./scripts/setup.sh

demo:
	./scripts/run_all.sh

test:
	./tests/smoke_test.sh

clean:
	./scripts/cleanup.sh

docker_up:
	cd docker && docker-compose up --build

docker_down:
	cd docker && docker-compose down -v
