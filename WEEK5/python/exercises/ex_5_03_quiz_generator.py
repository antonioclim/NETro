#!/usr/bin/env python3
"""
Exercițiul 5.03 – Generator Quiz Interactiv
===========================================
Generează întrebări pentru practică CIDR, VLSM și IPv6.

Utilizare:
    python ex_5_03_quiz_generator.py --count 5
    python ex_5_03_quiz_generator.py --interactive
    python ex_5_03_quiz_generator.py --type cidr --count 3

Autor: Material didactic ASE-CSIE
"""

from __future__ import annotations

import argparse
import ipaddress
import random
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

# Import utilitar local
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from python.utils.net_utils import analyze_ipv4_interface, ipv4_host_range


# Coduri de culoare ANSI
class Colors:
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'


def colorize(text: str, color: str) -> str:
    if sys.stdout.isatty():
        return f"{color}{text}{Colors.END}"
    return text


@dataclass
class QuizQuestion:
    """Structură pentru o întrebare quiz."""
    question: str
    correct_answer: str
    hint: Optional[str] = None
    explanation: Optional[str] = None
    category: str = "general"


def generate_cidr_question() -> QuizQuestion:
    """Generează o întrebare despre analiza CIDR."""
    # Generăm adresă aleatoare
    octets = [random.randint(1, 254) for _ in range(4)]
    prefix = random.choice([24, 25, 26, 27, 28, 29, 30])
    
    ip = '.'.join(map(str, octets))
    cidr = f"{ip}/{prefix}"
    
    # Calculăm răspunsul
    info = analyze_ipv4_interface(cidr)
    
    # Alegem tipul întrebării
    q_type = random.choice([
        "network", "broadcast", "hosts", "first_host", "last_host", "netmask"
    ])
    
    if q_type == "network":
        question = f"Care este adresa de rețea pentru {cidr}?"
        answer = str(info.network.network_address)
        explanation = f"Adresa de rețea se obține punând toți biții host pe 0. Pentru /{prefix}, avem {32-prefix} biți host."
    elif q_type == "broadcast":
        question = f"Care este adresa de broadcast pentru {cidr}?"
        answer = str(info.broadcast)
        explanation = f"Adresa de broadcast se obține punând toți biții host pe 1."
    elif q_type == "hosts":
        question = f"Câte hosturi utilizabile are rețeaua {cidr}?"
        answer = str(info.usable_hosts)
        explanation = f"Hosturi = 2^{32-prefix} - 2 = {info.usable_hosts} (scădem adresa de rețea și broadcast)"
    elif q_type == "first_host":
        question = f"Care este prima adresă de host utilizabilă în {cidr}?"
        answer = str(info.first_host)
        explanation = f"Primul host = adresa de rețea + 1"
    elif q_type == "last_host":
        question = f"Care este ultima adresă de host utilizabilă în {cidr}?"
        answer = str(info.last_host)
        explanation = f"Ultimul host = adresa de broadcast - 1"
    else:  # netmask
        question = f"Care este masca de rețea pentru prefixul /{prefix}?"
        answer = str(info.netmask)
        explanation = f"Masca se obține punând primii {prefix} biți pe 1 și restul pe 0"
    
    return QuizQuestion(
        question=question,
        correct_answer=answer,
        explanation=explanation,
        category="cidr"
    )


def generate_flsm_question() -> QuizQuestion:
    """Generează o întrebare despre subnetting FLSM."""
    # Rețea de bază
    base_prefixes = [16, 20, 22, 24]
    base_prefix = random.choice(base_prefixes)
    
    first_octet = random.choice([10, 172, 192])
    if first_octet == 10:
        ip = f"10.{random.randint(0,255)}.0.0"
    elif first_octet == 172:
        ip = f"172.{random.randint(16,31)}.0.0"
    else:
        ip = f"192.168.{random.randint(0,255)}.0"
    
    base_cidr = f"{ip}/{base_prefix}"
    
    # Număr de subrețele
    num_subnets = random.choice([2, 4, 8, 16])
    bits_needed = num_subnets.bit_length() - 1
    new_prefix = base_prefix + bits_needed
    
    q_type = random.choice(["new_prefix", "num_hosts", "increment"])
    
    if q_type == "new_prefix":
        question = f"Dacă împărțim {base_cidr} în {num_subnets} subrețele egale, care va fi noul prefix?"
        answer = f"/{new_prefix}"
        explanation = f"Împrumutăm log₂({num_subnets}) = {bits_needed} biți. Prefix nou = {base_prefix} + {bits_needed} = {new_prefix}"
    elif q_type == "num_hosts":
        hosts_per_subnet = 2**(32-new_prefix) - 2
        question = f"Câte hosturi utilizabile va avea fiecare subrețea dacă împărțim {base_cidr} în {num_subnets} părți?"
        answer = str(hosts_per_subnet)
        explanation = f"Fiecare subrețea are prefix /{new_prefix}, deci {32-new_prefix} biți host: 2^{32-new_prefix} - 2 = {hosts_per_subnet}"
    else:  # increment
        increment = 2**(32-new_prefix)
        question = f"Care este incrementul între subrețelele rezultate din împărțirea {base_cidr} în {num_subnets}?"
        answer = str(increment)
        explanation = f"Increment = 2^(32 - {new_prefix}) = {increment}"
    
    return QuizQuestion(
        question=question,
        correct_answer=answer,
        explanation=explanation,
        category="flsm"
    )


def generate_vlsm_question() -> QuizQuestion:
    """Generează o întrebare despre VLSM."""
    # Cerință de hosturi
    hosts_needed = random.choice([5, 10, 20, 30, 50, 60, 100, 120])
    
    # Calculăm prefixul
    import math
    host_bits = math.ceil(math.log2(hosts_needed + 2))
    prefix = 32 - host_bits
    usable = 2**host_bits - 2
    
    question = f"Ce prefix CIDR minim este necesar pentru a găzdui {hosts_needed} hosturi?"
    answer = f"/{prefix}"
    explanation = f"Avem nevoie de {hosts_needed}+2 = {hosts_needed+2} adrese. Cea mai mică putere a lui 2 >= {hosts_needed+2} este {2**host_bits}, deci {host_bits} biți host → prefix /{prefix} (oferă {usable} hosturi utilizabile)"
    
    return QuizQuestion(
        question=question,
        correct_answer=answer,
        explanation=explanation,
        category="vlsm"
    )


def generate_ipv6_question() -> QuizQuestion:
    """Generează o întrebare despre IPv6."""
    q_type = random.choice(["compress", "expand", "type"])
    
    if q_type == "compress":
        # Generăm o adresă lungă
        groups = []
        zero_start = random.randint(1, 5)
        zero_count = random.randint(2, 4)
        
        for i in range(8):
            if zero_start <= i < zero_start + zero_count:
                groups.append("0000")
            else:
                # Generăm grup cu zerouri la început
                val = random.randint(0, 255)
                groups.append(f"00{val:02x}" if random.random() < 0.5 else f"{val:04x}")
        
        full_addr = ':'.join(groups)
        compressed = str(ipaddress.IPv6Address(full_addr))
        
        question = f"Comprimă adresa IPv6: {full_addr}"
        answer = compressed
        explanation = "Eliminăm zerourile din stânga și folosim :: pentru cea mai lungă secvență de zerouri"
        
    elif q_type == "expand":
        # Adrese scurte cunoscute
        short_addrs = [
            ("2001:db8::1", "2001:0db8:0000:0000:0000:0000:0000:0001"),
            ("fe80::1", "fe80:0000:0000:0000:0000:0000:0000:0001"),
            ("::1", "0000:0000:0000:0000:0000:0000:0000:0001"),
            ("2001:db8:10::cafe", "2001:0db8:0010:0000:0000:0000:0000:cafe"),
        ]
        short, full = random.choice(short_addrs)
        
        question = f"Expandează adresa IPv6: {short}"
        answer = full
        explanation = "Înlocuim :: cu secvența de zerouri corespunzătoare și completăm fiecare grup la 4 cifre"
        
    else:  # type
        type_questions = [
            ("fe80::1", "link-local"),
            ("2001:db8::1", "global unicast"),
            ("::1", "loopback"),
            ("ff02::1", "multicast"),
            ("fc00::1", "unique local"),
        ]
        addr, addr_type = random.choice(type_questions)
        
        question = f"Ce tip de adresă IPv6 este {addr}?"
        answer = addr_type
        explanation = f"Prefixul {addr.split('::')[0] if '::' in addr else addr.split(':')[0]} indică tipul {addr_type}"
    
    return QuizQuestion(
        question=question,
        correct_answer=answer,
        explanation=explanation,
        category="ipv6"
    )


def generate_questions(count: int, q_type: Optional[str] = None) -> List[QuizQuestion]:
    """Generează o listă de întrebări."""
    generators = {
        "cidr": generate_cidr_question,
        "flsm": generate_flsm_question,
        "vlsm": generate_vlsm_question,
        "ipv6": generate_ipv6_question,
    }
    
    questions = []
    for _ in range(count):
        if q_type and q_type in generators:
            gen = generators[q_type]
        else:
            gen = random.choice(list(generators.values()))
        
        questions.append(gen())
    
    return questions


def run_quiz_batch(count: int, q_type: Optional[str] = None) -> int:
    """Rulează un quiz în modul batch (afișează toate întrebările)."""
    questions = generate_questions(count, q_type)
    
    print()
    print(colorize("═" * 60, Colors.BLUE))
    print(colorize("  Quiz Subnetting - Setul de Întrebări", Colors.BOLD))
    print(colorize("═" * 60, Colors.BLUE))
    print()
    
    for i, q in enumerate(questions, 1):
        category_color = {
            "cidr": Colors.CYAN,
            "flsm": Colors.GREEN,
            "vlsm": Colors.YELLOW,
            "ipv6": Colors.RED,
        }.get(q.category, Colors.BLUE)
        
        print(f"  {colorize(f'Întrebarea {i}', Colors.BOLD)} [{colorize(q.category.upper(), category_color)}]")
        print(f"  {q.question}")
        print()
        print(f"  {colorize('Răspuns:', Colors.GREEN)} {q.correct_answer}")
        if q.explanation:
            print(f"  {colorize('Explicație:', Colors.CYAN)} {q.explanation}")
        print(colorize("─" * 60, Colors.BLUE))
        print()
    
    return 0


def run_quiz_interactive(count: int = 5, q_type: Optional[str] = None) -> int:
    """Rulează un quiz interactiv."""
    questions = generate_questions(count, q_type)
    
    print()
    print(colorize("═" * 60, Colors.BLUE))
    print(colorize("  Quiz Interactiv de Subnetting", Colors.BOLD))
    print(colorize("═" * 60, Colors.BLUE))
    print()
    print(f"  Vei primi {count} întrebări. Introdu răspunsul sau apasă Enter pentru a sări.")
    print(f"  Scrie 'quit' pentru a ieși.")
    print()
    
    correct = 0
    skipped = 0
    
    for i, q in enumerate(questions, 1):
        category_color = {
            "cidr": Colors.CYAN,
            "flsm": Colors.GREEN,
            "vlsm": Colors.YELLOW,
            "ipv6": Colors.RED,
        }.get(q.category, Colors.BLUE)
        
        print(colorize("─" * 60, Colors.BLUE))
        print(f"  {colorize(f'Întrebarea {i}/{count}', Colors.BOLD)} [{colorize(q.category.upper(), category_color)}]")
        print(f"  {q.question}")
        print()
        
        try:
            answer = input(f"  {colorize('Răspunsul tău:', Colors.CYAN)} ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        
        if answer.lower() == 'quit':
            break
        
        if not answer:
            skipped += 1
            print(f"  {colorize('Sărit.', Colors.YELLOW)} Răspuns corect: {colorize(q.correct_answer, Colors.GREEN)}")
        elif answer.lower().replace('/', '').replace(' ', '') == q.correct_answer.lower().replace('/', '').replace(' ', ''):
            correct += 1
            print(f"  {colorize('✓ Corect!', Colors.GREEN)}")
        else:
            print(f"  {colorize('✗ Greșit.', Colors.RED)} Răspuns corect: {colorize(q.correct_answer, Colors.GREEN)}")
        
        if q.explanation:
            print(f"  {colorize('Explicație:', Colors.CYAN)} {q.explanation}")
        print()
    
    # Rezultat final
    answered = count - skipped
    percentage = (correct / answered * 100) if answered > 0 else 0
    
    print(colorize("═" * 60, Colors.BLUE))
    print(colorize("  Rezultat Final", Colors.BOLD))
    print(colorize("═" * 60, Colors.BLUE))
    print()
    print(f"  Răspunsuri corecte: {colorize(str(correct), Colors.GREEN)}/{answered}")
    print(f"  Întrebări sărite:   {skipped}")
    print(f"  Scor:               {colorize(f'{percentage:.0f}%', Colors.YELLOW)}")
    print()
    
    if percentage >= 80:
        print(f"  {colorize('Excelent! Stăpânești subnetting-ul!', Colors.GREEN)}")
    elif percentage >= 60:
        print(f"  {colorize('Bine! Mai exersează pentru perfecțiune.', Colors.YELLOW)}")
    else:
        print(f"  {colorize('Mai e de lucru. Revizuiește teoria și încearcă din nou.', Colors.RED)}")
    print()
    
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Construiește parser-ul de argumente."""
    parser = argparse.ArgumentParser(
        description="Generator Quiz Interactiv pentru Subnetting",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemple:
  %(prog)s --count 5                    5 întrebări aleatorii
  %(prog)s --interactive                Quiz interactiv
  %(prog)s --type cidr --count 3        3 întrebări doar CIDR
  %(prog)s --type vlsm --interactive    Quiz interactiv VLSM
"""
    )
    
    parser.add_argument(
        "--count", "-n",
        type=int,
        default=5,
        help="Numărul de întrebări (implicit: 5)"
    )
    
    parser.add_argument(
        "--type", "-t",
        choices=["cidr", "flsm", "vlsm", "ipv6"],
        help="Tipul întrebărilor (implicit: toate)"
    )
    
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Mod interactiv (răspunzi la întrebări)"
    )
    
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """Funcția principală."""
    parser = build_parser()
    args = parser.parse_args(argv)
    
    if args.interactive:
        return run_quiz_interactive(args.count, args.type)
    else:
        return run_quiz_batch(args.count, args.type)


if __name__ == "__main__":
    sys.exit(main())
