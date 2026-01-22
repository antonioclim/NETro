"""Helper pentru reguli firewall — Săptămâna 7.

Acest utilitar aplică profile mici de reguli `iptables` din `configs/firewall_profiles.json`.
Este destinat unui namespace de router de laborator creat de Mininet.

Exemple:
- sudo python3 python/apps/firewallctl.py --profile baseline
- sudo python3 python/apps/firewallctl.py --profile block_tcp_9090
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from python.utils.net_utils import run_cmd, is_root


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Aplică profile iptables (Săptămâna 7).")
    p.add_argument("--profile", required=True, help="Numele profilului din configs/firewall_profiles.json")
    p.add_argument("--config", default="configs/firewall_profiles.json", help="Calea către fișierul JSON de profile")
    p.add_argument("--dry-run", action="store_true", help="Afișează comenzile fără să le execute")
    return p


def iptables(argv: list[str], dry_run: bool) -> None:
    if dry_run:
        print("[dry-run]", " ".join(argv))
        return
    run_cmd(argv, timeout=10, check=True)


def main() -> int:
    args = build_parser().parse_args()
    if not is_root() and not args.dry_run:
        print("Acest utilitar necesită privilegii root, folosește sudo")
        return 2

    cfg_path = Path(args.config)
    data: dict[str, Any] = json.loads(cfg_path.read_text(encoding="utf-8"))
    if args.profile not in data:
        print(f"Profil necunoscut: {args.profile}")
        print(f"Profile disponibile: {', '.join(sorted(data.keys()))}")
        return 3

    profile = data[args.profile]
    rules = profile.get("rules", [])
    forward_policy = profile.get("forward_policy", "ACCEPT")

    # Curăță chain-ul FORWARD și setează politica
    iptables(["iptables", "-F", "FORWARD"], args.dry_run)
    iptables(["iptables", "-P", "FORWARD", str(forward_policy)], args.dry_run)

    # Aplică regulile în ordine
    for rule in rules:
        chain = rule.get("chain", "FORWARD")
        proto = rule.get("proto")
        action = rule.get("action", "ACCEPT")
        dport = rule.get("dport")
        argv = ["iptables", "-A", str(chain)]
        if proto:
            argv += ["-p", str(proto)]
        if dport is not None:
            argv += ["--dport", str(dport)]
        argv += ["-j", str(action)]
        iptables(argv, args.dry_run)

    # Afișează regulile FORWARD rezultate, pentru transparență
    if not args.dry_run:
        out = run_cmd(["iptables", "-L", "FORWARD", "-n", "-v"], timeout=10, check=False)
        print(out.stdout)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
