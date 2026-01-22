#!/usr/bin/env python3
"""ex_14_01.py — Drill-uri de recapitulare pentru Săptămâna 14.

Funcționalități:
  - Self-test interactiv cu întrebări de tip grilă
  - Generare quiz cu N întrebări random
  - Export rezultate în JSON

Utilizare:
  python3 ex_14_01.py --selftest          # test interactiv
  python3 ex_14_01.py --quiz 10           # 10 întrebări random
  python3 ex_14_01.py --quiz 10 --out q.json  # export JSON
"""

from __future__ import annotations

import argparse
import json
import random
from typing import Dict, List, Tuple

# Banca de întrebări (format: (întrebare, [opțiuni], index_răspuns_corect, explicație))
QUESTIONS: List[Tuple[str, List[str], int, str]] = [
    # Straturi și încapsulare
    (
        "Care strat OSI este responsabil pentru adresarea logică (IP)?",
        ["Link (2)", "Network (3)", "Transport (4)", "Application (7)"],
        1,
        "Stratul Network (3) gestionează adresarea IP și rutarea."
    ),
    (
        "Ce PDU folosește stratul Transport pentru TCP?",
        ["Frame", "Packet", "Segment", "Message"],
        2,
        "TCP folosește segmente; UDP folosește datagrame."
    ),
    (
        "Încapsularea adaugă header-e când datele...",
        ["Urcă în stivă", "Coboară în stivă", "Sunt procesate de aplicație", "Ajung la destinație"],
        1,
        "La transmitere, datele coboară și primesc headere la fiecare strat."
    ),
    
    # Adresare
    (
        "O adresă MAC are...",
        ["32 biți", "48 biți", "64 biți", "128 biți"],
        1,
        "Adresele MAC (Ethernet) au 48 biți (6 octeți), ex: 00:1A:2B:3C:4D:5E."
    ),
    (
        "Ce protocol rezolvă IP → MAC în rețele locale?",
        ["DNS", "DHCP", "ARP", "ICMP"],
        2,
        "ARP (Address Resolution Protocol) mapează IP-uri la adrese MAC."
    ),
    (
        "Care dintre următoarele este o adresă IP privată?",
        ["8.8.8.8", "192.168.1.1", "172.32.0.1", "11.0.0.1"],
        1,
        "192.168.0.0/16 este un bloc privat (RFC 1918)."
    ),
    
    # TCP/UDP
    (
        "Care flag TCP inițiază o conexiune nouă?",
        ["ACK", "FIN", "SYN", "RST"],
        2,
        "SYN (Synchronize) începe handshake-ul TCP în 3 pași."
    ),
    (
        "UDP este un protocol...",
        ["Orientat conexiune, fiabil", "Orientat conexiune, nefiabil", 
         "Fără conexiune, fiabil", "Fără conexiune, nefiabil"],
        3,
        "UDP nu garantează livrarea și nu stabilește conexiune."
    ),
    (
        "Ce înseamnă un pachet TCP cu flag RST?",
        ["Cerere de retransmisie", "Resetarea conexiunii", "Confirmare primire", "Cerere de sincronizare"],
        1,
        "RST (Reset) închide brusc conexiunea, de obicei la eroare."
    ),
    (
        "Care mecanism TCP previne congestionarea rețelei?",
        ["Flow Control", "Congestion Control", "Error Control", "Sequence Control"],
        1,
        "Congestion Control (ex: AIMD, slow start) ajustează rata la congestionare."
    ),
    
    # Porturi
    (
        "Pe ce port standard ascultă HTTP?",
        ["22", "53", "80", "443"],
        2,
        "HTTP folosește portul 80; HTTPS folosește 443."
    ),
    (
        "Pe ce port standard ascultă DNS?",
        ["22", "53", "80", "443"],
        1,
        "DNS folosește portul 53 (UDP și TCP)."
    ),
    (
        "Un port efemer este de obicei în intervalul...",
        ["0-1023", "1024-49151", "49152-65535", "80-443"],
        2,
        "Porturile efemere (client) sunt în 49152-65535 (sau 32768+ pe Linux)."
    ),
    
    # Rutare
    (
        "Ce comandă Linux afișează tabela de rutare?",
        ["ip addr", "ip route", "ip link", "ip neigh"],
        1,
        "`ip route` sau `ip r` afișează rutele; `netstat -rn` e varianta veche."
    ),
    (
        "Default gateway este folosit când...",
        ["Destinația este în aceeași subrețea", "Destinația este în altă subrețea", 
         "Pachetul este broadcast", "Nu există rută specifică"],
        3,
        "Gateway-ul implicit e folosit când nu există rută mai specifică (0.0.0.0/0)."
    ),
    
    # HTTP
    (
        "Ce cod HTTP indică succes?",
        ["200", "301", "404", "500"],
        0,
        "200 OK = succes; 301 = redirect; 404 = not found; 500 = server error."
    ),
    (
        "Ce metodă HTTP este idempotentă și sigură?",
        ["GET", "POST", "PUT", "DELETE"],
        0,
        "GET nu modifică starea; POST nu e idempotent."
    ),
    
    # Diagnostic
    (
        "Ce înseamnă 'Connection refused' la o conexiune TCP?",
        ["Timeout pe rețea", "Portul nu ascultă", "Firewall blochează", "DNS eșuat"],
        1,
        "RST imediat = portul nu ascultă; timeout = filtrat/blocat."
    ),
    (
        "Ce comandă verifică ce porturi ascultă pe host?",
        ["ping localhost", "ss -lntp", "ip addr", "tcpdump -i lo"],
        1,
        "`ss -lntp` arată socket-uri TCP în LISTEN; `netstat -tlnp` e echivalent."
    ),
    (
        "Care instrument captează pachete pentru analiză?",
        ["ping", "traceroute", "tcpdump", "ss"],
        2,
        "tcpdump/tshark/Wireshark captează și analizează pachete."
    ),
    
    # CIDR
    (
        "Câte adrese IP utilizabile are o rețea /24?",
        ["254", "255", "256", "512"],
        0,
        "/24 = 256 adrese, dar 2 sunt rezervate (rețea și broadcast) → 254 utilizabile."
    ),
    (
        "Care este masca de subrețea pentru /16?",
        ["255.0.0.0", "255.255.0.0", "255.255.255.0", "255.255.255.128"],
        1,
        "/16 = 16 biți pentru rețea → 255.255.0.0."
    ),
]


def run_selftest() -> Tuple[int, int]:
    """Rulează self-test interactiv."""
    print("\n" + "=" * 60)
    print("  Self-Test Recapitulare S14")
    print("=" * 60 + "\n")
    
    questions = QUESTIONS.copy()
    random.shuffle(questions)
    
    correct = 0
    total = len(questions)
    
    for i, (question, options, answer_idx, explanation) in enumerate(questions, 1):
        print(f"\nÎntrebarea {i}/{total}:")
        print(f"  {question}\n")
        
        for j, opt in enumerate(options):
            print(f"    {j + 1}. {opt}")
        
        while True:
            try:
                user_input = input("\nRăspuns (1-4, sau 'q' pentru ieșire): ").strip()
                if user_input.lower() == 'q':
                    print(f"\nTest întrerupt. Scor parțial: {correct}/{i-1}")
                    return correct, i - 1
                
                user_answer = int(user_input) - 1
                if 0 <= user_answer < len(options):
                    break
                print("Introdu un număr între 1 și 4.")
            except ValueError:
                print("Introdu un număr valid.")
        
        if user_answer == answer_idx:
            print("✓ Corect!")
            correct += 1
        else:
            print(f"✗ Greșit. Răspunsul corect: {answer_idx + 1}. {options[answer_idx]}")
        
        print(f"  Explicație: {explanation}")
    
    return correct, total


def generate_quiz(n: int) -> List[Dict]:
    """Generează un quiz cu N întrebări random."""
    questions = random.sample(QUESTIONS, min(n, len(QUESTIONS)))
    
    quiz = []
    for q, opts, ans_idx, expl in questions:
        quiz.append({
            "question": q,
            "options": opts,
            "correct_index": ans_idx,
            "correct_answer": opts[ans_idx],
            "explanation": expl,
        })
    
    return quiz


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Drill-uri recapitulare S14")
    parser.add_argument("--selftest", action="store_true", help="Rulează self-test interactiv")
    parser.add_argument("--quiz", type=int, help="Generează quiz cu N întrebări")
    parser.add_argument("--out", help="Fișier output pentru quiz (JSON)")
    parser.add_argument("--list", action="store_true", help="Listează toate întrebările")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    
    if args.selftest:
        correct, total = run_selftest()
        print("\n" + "=" * 60)
        print(f"  Scor final: {correct}/{total} ({100 * correct // total}%)")
        print("=" * 60 + "\n")
        return 0 if correct == total else 1
    
    elif args.quiz:
        quiz = generate_quiz(args.quiz)
        
        if args.out:
            with open(args.out, "w", encoding="utf-8") as f:
                json.dump(quiz, f, indent=2, ensure_ascii=False)
            print(f"Quiz salvat în: {args.out}")
        else:
            print(json.dumps(quiz, indent=2, ensure_ascii=False))
        return 0
    
    elif args.list:
        print(f"\nTotal întrebări: {len(QUESTIONS)}\n")
        for i, (q, opts, ans_idx, _) in enumerate(QUESTIONS, 1):
            print(f"{i}. {q}")
            print(f"   Răspuns: {opts[ans_idx]}\n")
        return 0
    
    else:
        print("Utilizare:")
        print("  python3 ex_14_01.py --selftest       # test interactiv")
        print("  python3 ex_14_01.py --quiz 10        # 10 întrebări random")
        print("  python3 ex_14_01.py --quiz 10 --out q.json")
        print("  python3 ex_14_01.py --list           # listează întrebările")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
