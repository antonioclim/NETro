#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XML-RPC Client - Săptămâna 12 | Rețele de Calculatoare
ASE-CSIE, 2025

Client XML-RPC pentru interacțiunea cu serverul calculator.
Demonstrează apeluri sincrone, gestionarea erorilor și benchmarking.

XML-RPC Wire Format (exemplu pentru add(5, 3)):
    Request:
        POST /RPC2 HTTP/1.1
        Content-Type: text/xml
        
        <?xml version="1.0"?>
        <methodCall>
          <methodName>add</methodName>
          <params>
            <param><value><int>5</int></value></param>
            <param><value><int>3</int></value></param>
          </params>
        </methodCall>
    
    Response:
        HTTP/1.1 200 OK
        Content-Type: text/xml
        
        <?xml version="1.0"?>
        <methodResponse>
          <params>
            <param><value><int>8</int></value></param>
          </params>
        </methodResponse>

Rulare:
    python xmlrpc_client.py [--host HOST] [--port PORT] [--demo|--benchmark|--interactive]
"""

from __future__ import annotations

import argparse
import sys
import time
import random
from datetime import datetime
from typing import Any, List, Optional
import xmlrpc.client

# =============================================================================
# Configurație
# =============================================================================

DEFAULT_HOST = "localhost"
DEFAULT_PORT = 8001


# =============================================================================
# Clasă Client
# =============================================================================

class XMLRPCCalculatorClient:
    """
    Client pentru serviciul Calculator XML-RPC.
    
    Încapsulează conexiunea și oferă metode de conveniență.
    """
    
    def __init__(self, host: str = DEFAULT_HOST, port: int = DEFAULT_PORT,
                 verbose: bool = False, timeout: float = 30.0):
        """
        Inițializează clientul XML-RPC.
        
        Args:
            host: Adresa serverului
            port: Portul serverului
            verbose: Afișează XML request/response
            timeout: Timeout pentru conexiune (secunde)
        """
        self.url = f"http://{host}:{port}/RPC2"
        self.verbose = verbose
        
        # Creează proxy-ul cu transport personalizat pentru timeout
        transport = xmlrpc.client.Transport()
        transport.timeout = timeout
        
        self.proxy = xmlrpc.client.ServerProxy(
            self.url,
            transport=transport,
            verbose=verbose,  # Afișează XML dacă True
            allow_none=True,
            encoding='utf-8'
        )
    
    def call(self, method: str, *args, **kwargs) -> Any:
        """
        Apelează o metodă RPC generic.
        
        Args:
            method: Numele metodei
            *args: Argumentele poziționale
            **kwargs: Argumentele numite (convertite la struct)
        
        Returns:
            Rezultatul apelului
        
        Raises:
            xmlrpc.client.Fault: Eroare de la server
            ConnectionError: Nu se poate conecta
        """
        try:
            func = getattr(self.proxy, method)
            if kwargs:
                # XML-RPC nu suportă kwargs nativ, le trimitem ca struct
                return func(*args, kwargs)
            return func(*args)
        except xmlrpc.client.Fault as e:
            raise RuntimeError(f"Eroare server: [{e.faultCode}] {e.faultString}")
        except ConnectionRefusedError:
            raise ConnectionError(f"Nu pot conecta la {self.url}")
    
    # Metode de conveniență
    def add(self, a, b): return self.proxy.add(a, b)
    def subtract(self, a, b): return self.proxy.subtract(a, b)
    def multiply(self, a, b): return self.proxy.multiply(a, b)
    def divide(self, a, b): return self.proxy.divide(a, b)
    def power(self, base, exp): return self.proxy.power(base, exp)
    def is_prime(self, n): return self.proxy.is_prime(n)
    def factorial(self, n): return self.proxy.factorial(n)
    def sort_list(self, lst): return self.proxy.sort_list(lst)
    def health(self): return self.proxy.health()
    def get_stats(self): return self.proxy.get_stats()
    def list_methods(self): return self.proxy.system.listMethods()


# =============================================================================
# Demonstrații
# =============================================================================

def demo_basic_calls(client: XMLRPCCalculatorClient) -> None:
    """Demonstrează apeluri de bază."""
    print("\n" + "=" * 60)
    print("DEMO 1: Operații Aritmetice de Bază")
    print("=" * 60)
    
    operations = [
        ("add(15, 27)", lambda: client.add(15, 27)),
        ("subtract(100, 42)", lambda: client.subtract(100, 42)),
        ("multiply(7, 8)", lambda: client.multiply(7, 8)),
        ("divide(144, 12)", lambda: client.divide(144, 12)),
        ("power(2, 10)", lambda: client.power(2, 10)),
    ]
    
    for name, func in operations:
        result = func()
        print(f"  {name:25} = {result}")


def demo_verification(client: XMLRPCCalculatorClient) -> None:
    """Demonstrează funcții de verificare."""
    print("\n" + "=" * 60)
    print("DEMO 2: Verificări și Calcule Avansate")
    print("=" * 60)
    
    # Verificări prime
    primes = [17, 23, 97, 100]
    print("\n  Numere prime:")
    for n in primes:
        is_p = client.is_prime(n)
        status = "✓ prim" if is_p else "✗ compus"
        print(f"    {n}: {status}")
    
    # Factorial
    print("\n  Factorial:")
    for n in [5, 7, 10]:
        result = client.factorial(n)
        print(f"    {n}! = {result:,}")


def demo_lists(client: XMLRPCCalculatorClient) -> None:
    """Demonstrează operații pe liste."""
    print("\n" + "=" * 60)
    print("DEMO 3: Operații pe Liste (array în XML-RPC)")
    print("=" * 60)
    
    test_list = [64, 25, 12, 22, 11, 90, 45]
    print(f"\n  Lista originală: {test_list}")
    
    sorted_list = client.proxy.sort_list(test_list)
    print(f"  sort_list:       {sorted_list}")
    
    sum_result = client.proxy.sum_list(test_list)
    print(f"  sum_list:        {sum_result}")
    
    avg_result = client.proxy.average(test_list)
    print(f"  average:         {avg_result:.2f}")
    
    minmax = client.proxy.min_max(test_list)
    print(f"  min_max:         min={minmax['min']}, max={minmax['max']}")


def demo_strings(client: XMLRPCCalculatorClient) -> None:
    """Demonstrează operații pe șiruri."""
    print("\n" + "=" * 60)
    print("DEMO 4: Operații pe Șiruri")
    print("=" * 60)
    
    test_str = "ASE-CSIE Rețele 2025"
    print(f"\n  Șir original:    '{test_str}'")
    
    reversed_str = client.proxy.reverse_string(test_str)
    print(f"  reverse_string:  '{reversed_str}'")
    
    upper = client.proxy.to_uppercase(test_str)
    print(f"  to_uppercase:    '{upper}'")
    
    sha = client.proxy.sha256_hash(test_str)
    print(f"  sha256_hash:     {sha[:32]}...")


def demo_introspection(client: XMLRPCCalculatorClient) -> None:
    """Demonstrează introspection (system.*)."""
    print("\n" + "=" * 60)
    print("DEMO 5: Introspection (system.*)")
    print("=" * 60)
    
    print("\n  system.listMethods():")
    methods = client.list_methods()
    # Afișează în coloane
    for i in range(0, len(methods), 4):
        row = methods[i:i+4]
        print("    " + ", ".join(f"{m:20}" for m in row))
    
    print("\n  system.methodHelp('add'):")
    help_text = client.proxy.system.methodHelp("add")
    # Afișează primele 5 linii
    lines = help_text.strip().split('\n')[:5]
    for line in lines:
        print(f"    {line}")
    if len(lines) < len(help_text.strip().split('\n')):
        print("    ...")


def demo_error_handling(client: XMLRPCCalculatorClient) -> None:
    """Demonstrează gestionarea erorilor."""
    print("\n" + "=" * 60)
    print("DEMO 6: Gestionarea Erorilor XML-RPC")
    print("=" * 60)
    
    error_cases = [
        ("divide(10, 0)", lambda: client.divide(10, 0)),
        ("factorial(-5)", lambda: client.factorial(-5)),
        ("metoda_inexistenta()", lambda: client.proxy.metoda_inexistenta()),
    ]
    
    for name, func in error_cases:
        try:
            result = func()
            print(f"  {name}: {result}")
        except xmlrpc.client.Fault as e:
            print(f"  {name}")
            print(f"    → Fault [{e.faultCode}]: {e.faultString[:50]}...")
        except Exception as e:
            print(f"  {name}")
            print(f"    → {type(e).__name__}: {str(e)[:50]}...")


def demo_server_info(client: XMLRPCCalculatorClient) -> None:
    """Demonstrează informații despre server."""
    print("\n" + "=" * 60)
    print("DEMO 7: Informații Server")
    print("=" * 60)
    
    health = client.health()
    print("\n  health():")
    for key, value in health.items():
        print(f"    {key}: {value}")
    
    stats = client.get_stats()
    print("\n  get_stats():")
    print(f"    Total apeluri: {stats['total_calls']}")
    print(f"    Uptime: {stats['uptime_seconds']}s")
    if stats['per_method']:
        print("    Top 5 metode:")
        sorted_methods = sorted(
            stats['per_method'].items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        for method, count in sorted_methods:
            print(f"      {method}: {count}")


def run_all_demos(client: XMLRPCCalculatorClient) -> None:
    """Rulează toate demonstrațiile."""
    print("\n" + "╔" + "═" * 68 + "╗")
    print("║" + " DEMO XML-RPC Client ".center(68) + "║")
    print("║" + f" Server: {client.url} ".center(68) + "║")
    print("╚" + "═" * 68 + "╝")
    
    demo_basic_calls(client)
    demo_verification(client)
    demo_lists(client)
    demo_strings(client)
    demo_introspection(client)
    demo_error_handling(client)
    demo_server_info(client)
    
    print("\n" + "=" * 60)
    print("Demo complet!")
    print("=" * 60 + "\n")


# =============================================================================
# Benchmark
# =============================================================================

def benchmark_xmlrpc(client: XMLRPCCalculatorClient, iterations: int = 100) -> dict:
    """
    Benchmark pentru a măsura overhead-ul XML-RPC.
    
    Compară:
    1. Apeluri simple (latență de bază)
    2. Transfer date mari (overhead serializare)
    3. Operații CPU-intensive
    4. Batch simulation (multiple apeluri secvențiale)
    
    Returns:
        Dict cu rezultatele benchmark-ului
    """
    results = {}
    
    print("\n" + "╔" + "═" * 68 + "╗")
    print("║" + " BENCHMARK XML-RPC ".center(68) + "║")
    print("╚" + "═" * 68 + "╝")
    
    # Test 1: Latență de bază
    print(f"\n[Test 1] Apeluri simple add(1, 2) × {iterations}")
    start = time.perf_counter()
    for _ in range(iterations):
        client.add(1, 2)
    elapsed = time.perf_counter() - start
    
    rps = iterations / elapsed
    avg_ms = (elapsed / iterations) * 1000
    print(f"  Timp total: {elapsed:.3f}s")
    print(f"  Timp mediu: {avg_ms:.2f}ms per apel")
    print(f"  Throughput: {rps:.1f} apeluri/secundă")
    results["simple_calls"] = {"total_s": elapsed, "avg_ms": avg_ms, "rps": rps}
    
    # Test 2: Transfer date mari
    large_list = list(range(5000))
    print(f"\n[Test 2] sort_list cu {len(large_list)} elemente × 10")
    
    start = time.perf_counter()
    for _ in range(10):
        client.sort_list(large_list)
    elapsed = time.perf_counter() - start
    
    avg_ms = (elapsed / 10) * 1000
    print(f"  Timp total: {elapsed:.3f}s")
    print(f"  Timp mediu: {avg_ms:.2f}ms per apel")
    
    # Comparație cu sortare locală
    start_local = time.perf_counter()
    for _ in range(10):
        sorted(large_list)
    elapsed_local = time.perf_counter() - start_local
    overhead = elapsed / elapsed_local
    print(f"  Overhead vs local: {overhead:.1f}x")
    results["large_data"] = {"total_s": elapsed, "avg_ms": avg_ms, "overhead": overhead}
    
    # Test 3: Operații CPU-intensive
    print(f"\n[Test 3] sha256_hash pe 1KB date × {iterations}")
    test_data = "x" * 1024
    
    start = time.perf_counter()
    for _ in range(iterations):
        client.proxy.sha256_hash(test_data)
    elapsed = time.perf_counter() - start
    
    avg_ms = (elapsed / iterations) * 1000
    print(f"  Timp total: {elapsed:.3f}s")
    print(f"  Timp mediu: {avg_ms:.2f}ms per apel")
    results["cpu_intensive"] = {"total_s": elapsed, "avg_ms": avg_ms}
    
    # Test 4: Multiple apeluri diferite (simulare workflow real)
    print(f"\n[Test 4] Workflow complet (5 operații) × {iterations // 5}")
    
    workflow_iters = iterations // 5
    start = time.perf_counter()
    for i in range(workflow_iters):
        # Simulează un flux tipic
        client.add(i, i + 1)
        client.multiply(i, 2)
        client.is_prime(i)
        client.proxy.echo(f"test_{i}")
        client.proxy.get_time()
    elapsed = time.perf_counter() - start
    
    ops_per_sec = (workflow_iters * 5) / elapsed
    print(f"  Timp total: {elapsed:.3f}s")
    print(f"  Operații/secundă: {ops_per_sec:.1f}")
    results["workflow"] = {"total_s": elapsed, "ops_per_sec": ops_per_sec}
    
    # Sumar
    print("\n" + "-" * 60)
    print("SUMAR BENCHMARK")
    print("-" * 60)
    print(f"  Latență medie (apel simplu): {results['simple_calls']['avg_ms']:.2f}ms")
    print(f"  Throughput maxim: {results['simple_calls']['rps']:.0f} req/s")
    print(f"  Overhead pentru date mari: {results['large_data']['overhead']:.1f}x")
    print("-" * 60)
    
    return results


# =============================================================================
# Mod Interactiv
# =============================================================================

def interactive_mode(client: XMLRPCCalculatorClient) -> None:
    """
    Mod interactiv pentru testare manuală.
    
    Permite utilizatorului să introducă apeluri XML-RPC direct.
    """
    print("\n" + "╔" + "═" * 68 + "╗")
    print("║" + " MOD INTERACTIV XML-RPC ".center(68) + "║")
    print("╚" + "═" * 68 + "╝")
    print("""
Comenzi disponibile:
  list              - Afișează toate metodele
  help <metodă>     - Documentația unei metode  
  <metodă> args...  - Apelează metoda cu argumente
  quit / exit       - Ieșire

Exemple:
  add 5 3           → 8
  is_prime 17       → True
  sort_list [5,2,8] → [2, 5, 8]
  echo "Hello"      → Hello
""")
    
    while True:
        try:
            cmd = input("\nxml-rpc> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nLa revedere!")
            break
        
        if not cmd:
            continue
        
        if cmd.lower() in ("quit", "exit", "q"):
            print("La revedere!")
            break
        
        if cmd.lower() == "list":
            methods = client.list_methods()
            print("Metode disponibile:")
            for i, m in enumerate(methods, 1):
                print(f"  {i:2}. {m}")
            continue
        
        if cmd.lower().startswith("help "):
            method_name = cmd[5:].strip()
            try:
                help_text = client.proxy.system.methodHelp(method_name)
                print(f"Documentație pentru {method_name}:")
                print(help_text)
            except Exception as e:
                print(f"Eroare: {e}")
            continue
        
        # Parse method call
        parts = cmd.split(maxsplit=1)
        method_name = parts[0]
        args_str = parts[1] if len(parts) > 1 else ""
        
        try:
            # Evaluează argumentele (atenție la securitate în producție!)
            if args_str:
                # Înlocuiește lista cu sintaxă Python
                args_str = args_str.replace('[', '(').replace(']', ',)')
                args = eval(f"({args_str},)")
            else:
                args = ()
            
            # Apelează metoda
            method = getattr(client.proxy, method_name)
            result = method(*args)
            print(f"Rezultat: {result}")
            
        except xmlrpc.client.Fault as e:
            print(f"Eroare XML-RPC [{e.faultCode}]: {e.faultString}")
        except Exception as e:
            print(f"Eroare: {type(e).__name__}: {e}")


# =============================================================================
# Main
# =============================================================================

def main():
    """Punct de intrare principal."""
    parser = argparse.ArgumentParser(
        description="XML-RPC Calculator Client",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemple:
  # Rulează demo-uri
  python xmlrpc_client.py --demo
  
  # Benchmark
  python xmlrpc_client.py --benchmark
  
  # Mod interactiv
  python xmlrpc_client.py --interactive
  
  # Verbose (afișează XML)
  python xmlrpc_client.py --demo --verbose
"""
    )
    
    parser.add_argument(
        "--host",
        default=DEFAULT_HOST,
        help=f"Adresa serverului (default: {DEFAULT_HOST})"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=DEFAULT_PORT,
        help=f"Portul serverului (default: {DEFAULT_PORT})"
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Rulează toate demonstrațiile"
    )
    parser.add_argument(
        "--benchmark",
        action="store_true",
        help="Rulează benchmark"
    )
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Pornește mod interactiv"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Afișează XML request/response"
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=100,
        help="Număr de iterații pentru benchmark (default: 100)"
    )
    
    args = parser.parse_args()
    
    # Implicit: demo dacă nu e specificat altceva
    if not (args.demo or args.benchmark or args.interactive):
        args.demo = True
    
    try:
        client = XMLRPCCalculatorClient(
            host=args.host,
            port=args.port,
            verbose=args.verbose
        )
        
        # Verifică conectivitatea
        try:
            client.health()
        except Exception as e:
            print(f"[EROARE] Nu pot conecta la {client.url}")
            print(f"  {type(e).__name__}: {e}")
            print(f"\n  Asigurați-vă că serverul rulează:")
            print(f"    python xmlrpc_server.py --port {args.port}")
            sys.exit(1)
        
        if args.demo:
            run_all_demos(client)
        
        if args.benchmark:
            benchmark_xmlrpc(client, iterations=args.iterations)
        
        if args.interactive:
            interactive_mode(client)
    
    except KeyboardInterrupt:
        print("\n[Întrerupt de utilizator]")
        sys.exit(0)


if __name__ == "__main__":
    main()
