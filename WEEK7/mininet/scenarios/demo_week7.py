"""Demo automat Săptămâna 7.

Rulează o topologie Mininet cu un router/firewall și demonstrează:
- conectivitate TCP și UDP în regim baseline
- blocarea portului TCP 9090 pe calea de forward
- blocarea portului UDP 9091 pe calea de forward

Se generează artefacte pentru reproducibilitate.
"""

from __future__ import annotations

import argparse
import signal
import time
from pathlib import Path
from typing import Optional

from mininet.log import setLogLevel
from mininet.net import Mininet
from mininet.node import OVSSwitch
from mininet.link import TCLink

# Importă clasa de topologie
from mininet.topologies.topo_week7_firewall import Week7FirewallTopo  # type: ignore


TCP_PORT = 9090
UDP_PORT = 9091
H2_IP = "10.0.7.200"


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Rulează demo-ul Mininet pentru Săptămâna 7.")
    p.add_argument("--artifacts", required=True, help="Directorul de artefacte")
    p.add_argument("--pcap", required=True, help="Unde se scrie demo.pcap")
    p.add_argument("--log", required=True, help="Unde se scrie demo.log")
    p.add_argument("--validation", required=True, help="Unde se scrie validation.txt")
    return p


def log_line(log_path: Path, line: str) -> None:
    stamp = time.strftime("%Y-%m-%d %H:%M:%S")
    msg = f"[{stamp}] {line}"
    print(msg, flush=True)
    with log_path.open("a", encoding="utf-8") as f:
        f.write(msg + "\n")


def run_cmd(node, argv: list[str], log_path: Path, expect_ok: Optional[bool] = None) -> int:
    """Rulează o comandă pe un nod Mininet și întoarce exit code-ul."""
    proc = node.popen(argv)
    out, _ = proc.communicate(timeout=20)
    rc = proc.returncode
    # Unele versiuni Mininet întorc bytes pe stdout, tratare robustă
    if isinstance(out, bytes):
        out_text = out.decode("utf-8", errors="replace")
    else:
        out_text = str(out)
    log_line(log_path, f"{node.name}$ {' '.join(argv)} -> rc={rc}")
    if out_text.strip():
        for ln in out_text.strip().splitlines()[:20]:
            log_line(log_path, f"  {ln}")
    if expect_ok is True and rc != 0:
        log_line(log_path, "  eșec neașteptat")
    if expect_ok is False and rc == 0:
        log_line(log_path, "  succes neașteptat")
    return rc


def main() -> int:
    args = build_parser().parse_args()
    art_dir = Path(args.artifacts)
    art_dir.mkdir(parents=True, exist_ok=True)

    log_path = Path(args.log)
    validation_path = Path(args.validation)
    pcap_path = Path(args.pcap)

    # Resetează fișierele de log
    log_path.write_text("", encoding="utf-8")
    validation_path.write_text("", encoding="utf-8")

    setLogLevel("warning")

    log_line(log_path, "pornește Mininet")
    topo = Week7FirewallTopo()
    net = Mininet(topo=topo, link=TCLink, switch=OVSSwitch, controller=None, autoSetMacs=True, autoStaticArp=True)
    net.start()

    h1 = net.get("h1")
    h2 = net.get("h2")
    fw = net.get("fw")

    # Pregătește reguli firewall baseline
    firewallctl = str((Path(__file__).resolve().parents[2] / "python" / "apps" / "firewallctl.py").resolve())
    log_line(log_path, "aplic profilul baseline de firewall pe fw")
    fw.cmd(f"python3 {firewallctl} --profile baseline")

    # Pornește tcpdump pe fw pentru dovezi (dacă există)
    tcpdump_proc = None
    if fw.cmd("command -v tcpdump >/dev/null 2>&1 && echo yes || echo no").strip() == "yes":
        log_line(log_path, f"pornește captură tcpdump pe fw: {pcap_path}")
        tcpdump_proc = fw.popen(["tcpdump", "-i", "any", "-nn", "-U", "-w", str(pcap_path), "tcp", "or", "udp"])
        time.sleep(0.4)
    else:
        log_line(log_path, "tcpdump nu este disponibil, pcap poate lipsi")

    # Pornește serverele pe h2
    tcp_server = str((Path(__file__).resolve().parents[2] / "python" / "apps" / "tcp_server.py").resolve())
    udp_receiver = str((Path(__file__).resolve().parents[2] / "python" / "apps" / "udp_receiver.py").resolve())

    log_line(log_path, "pornește serverul TCP pe h2")
    tcp_srv_proc = h2.popen(
        ["python3", tcp_server, "--host", "0.0.0.0", "--port", str(TCP_PORT), "--log", str(art_dir / "tcp_server.log")]
    )

    log_line(log_path, "baseline: client TCP din h1")
    tcp_client = str((Path(__file__).resolve().parents[2] / "python" / "apps" / "tcp_client.py").resolve())
    rc_tcp_baseline = run_cmd(
        h1, ["python3", tcp_client, "--host", H2_IP, "--port", str(TCP_PORT), "--message", "baseline"], log_path, expect_ok=True
    )

    log_line(log_path, "baseline: trimitere și recepție UDP")
    # Pornește receptorul, așteptând 1 mesaj
    udp_rcv_proc = h2.popen(
        ["python3", udp_receiver, "--host", "0.0.0.0", "--port", str(UDP_PORT), "--timeout", "5"]
    )
    time.sleep(0.2)
    udp_sender = str((Path(__file__).resolve().parents[2] / "python" / "apps" / "udp_sender.py").resolve())
    rc_udp_send = run_cmd(
        h1, ["python3", udp_sender, "--host", H2_IP, "--port", str(UDP_PORT), "--message", "baseline"], log_path, expect_ok=True
    )
    udp_rcv_proc.wait(timeout=10)
    rc_udp_baseline = udp_rcv_proc.returncode if udp_rcv_proc.returncode is not None else 9

    baseline_ok = (rc_tcp_baseline == 0) and (rc_udp_send == 0) and (rc_udp_baseline == 0)
    validation_lines: list[str] = []
    validation_lines.append(
        f"BASELINE_OK: tcp_echo={'ok' if rc_tcp_baseline == 0 else 'fail'} udp_echo={'ok' if rc_udp_baseline == 0 else 'fail'}"
    )

    # Blochează TCP 9090
    log_line(log_path, "aplic profilul block_tcp_9090 pe fw")
    fw.cmd(f"python3 {firewallctl} --profile block_tcp_9090")
    log_line(log_path, "test: TCP ar trebui să eșueze, UDP ar trebui să funcționeze")
    rc_tcp_block = run_cmd(
        h1,
        ["python3", tcp_client, "--host", H2_IP, "--port", str(TCP_PORT), "--message", "blocked", "--timeout", "1"],
        log_path,
        expect_ok=False,
    )

    udp_rcv_proc2 = h2.popen(["python3", udp_receiver, "--host", "0.0.0.0", "--port", str(UDP_PORT), "--timeout", "5"])
    time.sleep(0.2)
    run_cmd(h1, ["python3", udp_sender, "--host", H2_IP, "--port", str(UDP_PORT), "--message", "still_ok"], log_path, expect_ok=True)
    udp_rcv_proc2.wait(timeout=10)
    rc_udp_still = udp_rcv_proc2.returncode if udp_rcv_proc2.returncode is not None else 9

    block_tcp_ok = (rc_tcp_block != 0) and (rc_udp_still == 0)
    validation_lines.append(
        f"BLOCK_TCP_OK: tcp_echo={'blocked' if rc_tcp_block != 0 else 'unexpected_ok'} udp_echo={'ok' if rc_udp_still == 0 else 'fail'}"
    )

    # Blochează UDP 9091 (revino la baseline înainte, ca să eviți confuzii)
    log_line(log_path, "restaurez profilul baseline pe fw")
    fw.cmd(f"python3 {firewallctl} --profile baseline")
    log_line(log_path, "aplic profilul block_udp_9091 pe fw")
    fw.cmd(f"python3 {firewallctl} --profile block_udp_9091")

    log_line(log_path, "test: UDP ar trebui să eșueze, TCP ar trebui să funcționeze")
    rc_tcp_after = run_cmd(
        h1, ["python3", tcp_client, "--host", H2_IP, "--port", str(TCP_PORT), "--message", "tcp_ok_again"], log_path, expect_ok=True
    )

    udp_rcv_proc3 = h2.popen(["python3", udp_receiver, "--host", "0.0.0.0", "--port", str(UDP_PORT), "--timeout", "2"])
    time.sleep(0.2)
    run_cmd(h1, ["python3", udp_sender, "--host", H2_IP, "--port", str(UDP_PORT), "--message", "udp_blocked"], log_path, expect_ok=True)
    udp_rcv_proc3.wait(timeout=5)
    rc_udp_blocked = udp_rcv_proc3.returncode if udp_rcv_proc3.returncode is not None else 9

    block_udp_ok = (rc_tcp_after == 0) and (rc_udp_blocked != 0)
    validation_lines.append(
        f"BLOCK_UDP_OK: tcp_echo={'ok' if rc_tcp_after == 0 else 'fail'} udp_echo={'blocked' if rc_udp_blocked != 0 else 'unexpected_ok'}"
    )

    # Oprește serverele și captură
    log_line(log_path, "opresc serverele și captură")
    try:
        tcp_srv_proc.send_signal(signal.SIGTERM)
        tcp_srv_proc.wait(timeout=3)
    except Exception:
        try:
            tcp_srv_proc.kill()
        except Exception:
            pass

    if tcpdump_proc is not None:
        try:
            tcpdump_proc.send_signal(signal.SIGINT)
            tcpdump_proc.wait(timeout=3)
        except Exception:
            try:
                tcpdump_proc.kill()
            except Exception:
                pass

    # Oprește Mininet
    net.stop()

    validation_path.write_text("\n".join(validation_lines) + "\n", encoding="utf-8")

    # Codul de ieșire reflectă succesul general
    if baseline_ok and block_tcp_ok and block_udp_ok:
        log_line(log_path, "demo finalizat cu succes")
        return 0

    log_line(log_path, "demo finalizat cu erori")
    return 10


if __name__ == "__main__":
    raise SystemExit(main())
