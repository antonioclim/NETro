"""Analiză ușoară a capturilor pcap folosind tshark.

Scopul este să obții un rezumat util pentru laborator, fără dependențe grele.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Optional

from python.utils.net_utils import run_cmd


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Generează un rezumat dintr-un pcap folosind tshark.")
    p.add_argument("--pcap", required=True, help="Calea către fișierul pcap")
    p.add_argument("--out", required=True, help="Calea către fișierul de ieșire (text)")
    return p


def main() -> int:
    args = build_parser().parse_args()
    pcap = Path(args.pcap)
    out = Path(args.out)

    if not pcap.exists():
        print(f"[analysis] pcap lipsește: {pcap}")
        return 2

    # Verifică disponibilitatea tshark
    res = run_cmd(["bash", "-lc", "command -v tshark"], timeout=5)
    if res.returncode != 0:
        print("[analysis] tshark nu este disponibil. Sar peste analiză.")
        return 0

    lines: list[str] = []
    lines.append(f"PCAP: {pcap}")
    lines.append("")

    # Statistici simple: conversații TCP
    conv_tcp = run_cmd(["tshark", "-r", str(pcap), "-q", "-z", "conv,tcp"], timeout=30)
    lines.append("Conversații TCP (tshark -z conv,tcp):")
    lines.append(conv_tcp.stdout.strip() or conv_tcp.stderr.strip())
    lines.append("")

    # Top endpoints (IP src/dst)
    endpoints = run_cmd(["tshark", "-r", str(pcap), "-q", "-z", "endpoints,ip"], timeout=30)
    lines.append("Endpoints IP (tshark -z endpoints,ip):")
    lines.append(endpoints.stdout.strip() or endpoints.stderr.strip())
    lines.append("")

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[analysis] Am scris: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
