#!/usr/bin/env python3
"""run_demo.py — Orchestrator pentru demo automat complet (Mininet + trafic + captură).

Produce artefacte în directorul specificat:
  - capture_lb.pcap (captură tcpdump pe interfața lb)
  - tshark_summary.txt (analiză offline)
  - http_client.log (log cereri HTTP)
  - report.json (sinteză)
  - *.log (loguri individuale per componentă)

Utilizare (din scripts/run_all.sh):
  sudo python3 python/apps/run_demo.py --artifacts ./artifacts
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import shutil
import signal
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional

# IMPORTANT: Evită ca directorul curent să umbrească pachetul 'mininet' instalat.
# Kit-ul are un director numit 'mininet/' pentru topologii, nu biblioteca Mininet.
for p in ["", os.getcwd()]:
    if p in sys.path:
        sys.path.remove(p)

from mininet.net import Mininet
from mininet.node import Controller
from mininet.link import TCLink
from mininet.log import setLogLevel


def log(msg: str) -> None:
    """Logging cu timestamp."""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] [demo] {msg}")


def load_topo_class(topo_file: Path, class_name: str):
    """Încarcă dinamic o clasă de topologie din fișier."""
    spec = importlib.util.spec_from_file_location("topo_mod", topo_file)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load topology from {topo_file}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return getattr(mod, class_name)


def sh(cmd: List[str], timeout: int = 30) -> subprocess.CompletedProcess:
    """Execută o comandă shell și returnează rezultatul."""
    return subprocess.run(cmd, text=True, capture_output=True, timeout=timeout)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Demo orchestrator pentru S14")
    p.add_argument("--artifacts", required=True, help="Director pentru artefacte")
    p.add_argument("--http-count", type=int, default=20, help="Număr cereri HTTP")
    p.add_argument("--http-interval", type=float, default=0.05, help="Interval între cereri")
    return p.parse_args()


def main() -> int:
    setLogLevel("info")
    args = parse_args()

    # Determină căile
    root = Path(__file__).resolve().parents[2]  # starterkit_saptamana_14/
    apps_dir = root / "python" / "apps"
    topo_file = root / "mininet" / "topologies" / "topo_14_recap.py"

    art = Path(args.artifacts).resolve()
    art.mkdir(parents=True, exist_ok=True)

    # Definire căi artefacte (nume standard conform specificației)
    pcap_path = art / "demo.pcap"
    tshark_summary = art / "tshark_summary.txt"
    http_log = art / "http_client.log"
    http_stdout = art / "http_client.stdout"
    tcp_echo_log = art / "tcp_echo.log"
    demo_log = art / "demo.log"
    validation_txt = art / "validation.txt"
    report_json = art / "report.json"

    # Curăță artefactele anterioare
    for f in [pcap_path, tshark_summary, http_log, http_stdout, tcp_echo_log, 
              demo_log, validation_txt, report_json]:
        try:
            f.unlink()
        except FileNotFoundError:
            pass

    # Încarcă topologia
    log("Se încarcă topologia...")
    TopoCls = load_topo_class(topo_file, "Recap14Topo")
    topo = TopoCls()

    net = Mininet(
        topo=topo,
        link=TCLink,
        controller=Controller,
        autoSetMacs=True,
        autoStaticArp=True
    )
    net.addController("c0")

    proc_handles: List[Tuple[Any, Any]] = []

    try:
        log("Pornire rețea Mininet...")
        net.start()

        cli = net.get("cli")
        lb = net.get("lb")
        app1 = net.get("app1")
        app2 = net.get("app2")

        # Test conectivitate de bază
        log("Testare conectivitate de bază (ping)...")
        ping_out = {
            "cli->lb": cli.cmd("ping -c 1 -W 1 10.0.14.1 || true").strip(),
            "cli->app1": cli.cmd("ping -c 1 -W 1 10.0.14.100 || true").strip(),
            "cli->app2": cli.cmd("ping -c 1 -W 1 10.0.14.101 || true").strip(),
        }

        # Pornește backend servers
        log("Pornire servere backend...")
        app1_log_f = open(art / "app1.log", "w", encoding="utf-8")
        app2_log_f = open(art / "app2.log", "w", encoding="utf-8")
        
        p_app1 = app1.popen(
            ["python3", str(apps_dir / "backend_server.py"), "--id", "app1", "--port", "8080"],
            stdout=app1_log_f,
            stderr=subprocess.STDOUT,
        )
        p_app2 = app2.popen(
            ["python3", str(apps_dir / "backend_server.py"), "--id", "app2", "--port", "8080"],
            stdout=app2_log_f,
            stderr=subprocess.STDOUT,
        )
        proc_handles.extend([(p_app1, app1_log_f), (p_app2, app2_log_f)])
        time.sleep(0.5)

        # Pornește TCP echo server pe app1 (port standard 9090)
        log("Pornire server TCP echo pe app1:9090...")
        echo_log_f = open(tcp_echo_log, "w", encoding="utf-8")
        p_echo = app1.popen(
            ["python3", str(apps_dir / "tcp_echo_server.py"), "--port", "9090"],
            stdout=echo_log_f,
            stderr=subprocess.STDOUT,
        )
        proc_handles.append((p_echo, echo_log_f))
        time.sleep(0.3)

        # Pornește load balancer pe lb
        log("Pornire load balancer pe lb:8080...")
        lb_log_f = open(art / "lb.log", "w", encoding="utf-8")
        p_lb = lb.popen(
            [
                "python3",
                str(apps_dir / "lb_proxy.py"),
                "--listen-host", "0.0.0.0",
                "--listen-port", "8080",
                "--backends", "10.0.14.100:8080,10.0.14.101:8080",
            ],
            stdout=lb_log_f,
            stderr=subprocess.STDOUT,
        )
        proc_handles.append((p_lb, lb_log_f))
        time.sleep(0.5)

        # Pornește captură tcpdump pe lb
        log("Pornire captură tcpdump pe lb-eth0...")
        tcpdump_log_f = open(art / "tcpdump.log", "w", encoding="utf-8")
        p_tcpdump = lb.popen(
            ["tcpdump", "-i", "lb-eth0", "-w", str(pcap_path)],
            stdout=subprocess.DEVNULL,
            stderr=tcpdump_log_f,
        )
        proc_handles.append((p_tcpdump, tcpdump_log_f))
        time.sleep(0.5)

        # Generează trafic TCP echo
        log("Generare trafic TCP: cli -> app1:9090...")
        echo_client_out = cli.cmd(
            f"python3 {apps_dir / 'tcp_echo_client.py'} "
            f"--host 10.0.14.100 --port 9090 --message hello_s14 || true"
        ).strip()
        with open(art / "tcp_echo_client.stdout", "w", encoding="utf-8") as f:
            f.write(echo_client_out + "\n")

        # Generează trafic HTTP
        log(f"Generare trafic HTTP: {args.http_count} cereri către lb:8080...")
        http_cmd = (
            f"python3 {apps_dir / 'http_client.py'} "
            f"--url http://10.0.14.1:8080/ "
            f"--count {args.http_count} --interval {args.http_interval} "
            f"--out {http_log} "
            f"> {http_stdout} 2>&1 || true"
        )
        _ = cli.cmd(http_cmd)
        time.sleep(0.3)

        # Oprește tcpdump pentru a salva pcap-ul
        log("Oprire tcpdump...")
        try:
            p_tcpdump.send_signal(signal.SIGINT)
        except Exception:
            p_tcpdump.terminate()
        time.sleep(0.7)

        # Procesare tshark offline
        log("Rulare post-procesare tshark...")
        if shutil.which("tshark") is None:
            tshark_summary.write_text(
                "tshark nu a fost găsit. Instalează tshark și rerulează.\n",
                encoding="utf-8"
            )
        else:
            chunks: List[str] = []
            
            chunks.append("=" * 60 + "\n")
            chunks.append("TSHARK SUMMARY - Săptămâna 14 Demo\n")
            chunks.append("=" * 60 + "\n\n")
            
            chunks.append("## IP Conversations\n")
            chunks.append("-" * 40 + "\n")
            result = sh(["tshark", "-r", str(pcap_path), "-q", "-z", "conv,ip"])
            chunks.append(result.stdout)
            
            chunks.append("\n## TCP Conversations\n")
            chunks.append("-" * 40 + "\n")
            result = sh(["tshark", "-r", str(pcap_path), "-q", "-z", "conv,tcp"])
            chunks.append(result.stdout)
            
            chunks.append("\n## HTTP Requests\n")
            chunks.append("-" * 40 + "\n")
            result = sh([
                "tshark", "-r", str(pcap_path),
                "-Y", "http.request",
                "-T", "fields",
                "-e", "frame.number",
                "-e", "ip.src",
                "-e", "ip.dst",
                "-e", "tcp.dstport",
                "-e", "http.request.method",
                "-e", "http.request.uri",
            ])
            chunks.append("frame.no\tip.src\t\tip.dst\t\tport\tmethod\turi\n")
            chunks.append(result.stdout)
            
            chunks.append("\n## TCP SYN Packets (New Connections)\n")
            chunks.append("-" * 40 + "\n")
            result = sh([
                "tshark", "-r", str(pcap_path),
                "-Y", "tcp.flags.syn==1 && tcp.flags.ack==0",
                "-T", "fields",
                "-e", "frame.number",
                "-e", "ip.src",
                "-e", "ip.dst",
                "-e", "tcp.dstport",
            ])
            chunks.append("frame.no\tip.src\t\tip.dst\t\tdport\n")
            chunks.append(result.stdout)
            
            tshark_summary.write_text("".join(chunks), encoding="utf-8")

        # Construiește report.json
        log("Construire report.json...")
        http_lines = []
        if http_log.exists():
            http_lines = http_log.read_text(encoding="utf-8", errors="replace").splitlines()
        
        dist: Dict[str, int] = {}
        ok_count = 0
        for line in http_lines:
            parts = line.split()
            status = next((p.split("=", 1)[1] for p in parts if p.startswith("status=")), "ERR")
            backend = next((p.split("=", 1)[1] for p in parts if p.startswith("backend=")), "-")
            if status.startswith("2"):
                ok_count += 1
            dist[backend] = dist.get(backend, 0) + 1

        report = {
            "timestamp": datetime.now().isoformat(),
            "ping": ping_out,
            "tcp_echo": {
                "output": echo_client_out[:500] if echo_client_out else "",
                "success": "Echo valid" in echo_client_out if echo_client_out else False,
            },
            "http": {
                "count": len(http_lines),
                "ok": ok_count,
                "errors": len(http_lines) - ok_count,
                "backend_distribution": dist,
            },
            "artifacts": {
                "pcap": str(pcap_path),
                "tshark_summary": str(tshark_summary),
                "http_log": str(http_log),
            },
        }
        report_json.write_text(
            json.dumps(report, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8"
        )

        # Generează demo.log (consolidare loguri)
        log("Construire demo.log...")
        demo_lines = [
            "=" * 60,
            "DEMO LOG — Săptămâna 14 Recapitulare",
            f"Timestamp: {datetime.now().isoformat()}",
            "=" * 60,
            "",
            "## Ping Results",
            "-" * 40,
        ]
        for k, v in ping_out.items():
            demo_lines.append(f"{k}:")
            demo_lines.append(v[:200] if v else "  (no output)")
            demo_lines.append("")
        
        demo_lines.extend([
            "## TCP Echo",
            "-" * 40,
            echo_client_out[:500] if echo_client_out else "(no output)",
            "",
            "## HTTP Summary",
            "-" * 40,
            f"Total requests: {len(http_lines)}",
            f"Successful (2xx): {ok_count}",
            f"Errors: {len(http_lines) - ok_count}",
            f"Backend distribution: {dist}",
            "",
            "## Artifacts Generated",
            "-" * 40,
            f"- demo.pcap: {pcap_path.stat().st_size if pcap_path.exists() else 0} bytes",
            f"- report.json: generated",
            f"- tshark_summary.txt: generated",
            "",
            "=" * 60,
            "END OF DEMO LOG",
            "=" * 60,
        ])
        demo_log.write_text("\n".join(demo_lines) + "\n", encoding="utf-8")

        # Generează validation.txt (checklist de verificare)
        log("Construire validation.txt...")
        validations = []
        
        # Check 1: Ping conectivitate
        ping_ok = all("1 received" in v or "1 packets received" in v 
                      for v in ping_out.values() if v)
        validations.append(f"[{'TRECUT' if ping_ok else 'EȘUAT'}] Conectivitate ping către toate hosturile")
        
        # Check 2: TCP echo
        echo_ok = "Echo valid" in echo_client_out if echo_client_out else False
        validations.append(f"[{'TRECUT' if echo_ok else 'EȘUAT'}] Serverul TCP echo răspunde corect")
        
        # Check 3: HTTP requests
        http_ok = ok_count > 0 and ok_count >= len(http_lines) * 0.8
        validations.append(f"[{'TRECUT' if http_ok else 'EȘUAT'}] Cereri HTTP reușite (>=80%)")
        
        # Check 4: Load balancing
        lb_ok = len(dist) >= 2 if dist else False
        validations.append(f"[{'TRECUT' if lb_ok else 'EȘUAT'}] Load balancing distribuit către mai multe backends")
        
        # Check 5: PCAP exists
        pcap_ok = pcap_path.exists() and pcap_path.stat().st_size > 100
        validations.append(f"[{'TRECUT' if pcap_ok else 'EȘUAT'}] Fișier captură PCAP generat")
        
        # Summary
        passed = sum(1 for v in validations if "[TRECUT]" in v)
        total = len(validations)
        
        validation_content = [
            "=" * 60,
            "REZULTATE VALIDARE — Săptămâna 14",
            f"Timestamp: {datetime.now().isoformat()}",
            "=" * 60,
            "",
            *validations,
            "",
            "-" * 60,
            f"TOTAL: {passed}/{total} verificări trecute",
            "STATUS: " + ("TOATE TRECUTE ✓" if passed == total else "UNELE EȘUATE ✗"),
            "=" * 60,
        ]
        validation_txt.write_text("\n".join(validation_content) + "\n", encoding="utf-8")

        log("Demo completat cu succes!")
        log(f"Artefacte salvate în: {art}")

    finally:
        log("Oprire procese și Mininet...")
        for proc, log_f in reversed(proc_handles):
            try:
                proc.terminate()
            except Exception:
                pass
            try:
                proc.wait(timeout=1)
            except Exception:
                try:
                    proc.kill()
                except Exception:
                    pass
            try:
                log_f.close()
            except Exception:
                pass
        try:
            net.stop()
        except Exception:
            pass

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
