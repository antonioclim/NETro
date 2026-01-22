"""Topologie pentru Săptămâna 7 (variantă cu host dedicat pentru securitate/monitorizare).

Include un host `sec` care poate fi folosit pentru captură, analiză sau scenarii controlate de tip IDS.
"""

from mininet.topo import Topo


class Week7SecurityTopo(Topo):
    def build(self) -> None:
        s1 = self.addSwitch("s1")
        h1 = self.addHost("h1", ip="10.0.7.11/24")
        h2 = self.addHost("h2", ip="10.0.7.12/24")
        sec = self.addHost("sec", ip="10.0.7.13/24")
        self.addLink(h1, s1)
        self.addLink(h2, s1)
        self.addLink(sec, s1)


topos = {"week7sec": Week7SecurityTopo}
