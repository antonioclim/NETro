#!/bin/bash
# Verificare mediu pentru Starterkit S9

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo "═══ Verificare Mediu S9 ═══"
PASS=0
FAIL=0

check() {
    if $1 &>/dev/null; then
        echo -e "${GREEN}✓${NC} $2"
        ((PASS++))
    else
        echo -e "${RED}✗${NC} $2"
        ((FAIL++))
    fi
}

check "python3 --version" "Python3 instalat"
check "python3 -c 'import socket'" "Modul socket disponibil"
check "python3 -c 'import struct'" "Modul struct disponibil"
check "python3 -c 'import gzip'" "Modul gzip disponibil"
check "test -d server-files" "Director server-files există"
check "test -f server-files/hello.txt" "Fișier hello.txt există"
check "test -f python/exercises/ex_9_01_endianness.py" "Exercițiu 1 există"
check "test -f python/exercises/ex_9_02_pseudo_ftp.py" "Exercițiu 2 există"

echo ""
echo "═══ Rezultat ═══"
echo "Trecute: $PASS, Eșuate: $FAIL"

if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}✓ Mediul este configurat corect!${NC}"
    exit 0
else
    echo -e "${RED}✗ Unele verificări au eșuat. Rulați 'make setup'.${NC}"
    exit 1
fi
