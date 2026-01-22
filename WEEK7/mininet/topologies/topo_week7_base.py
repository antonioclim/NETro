"""Topologie simplă pentru Săptămâna 7.

Două host-uri conectate printr-un switch. Utilă pentru verificări rapide de trafic fără firewall.
"""

from mininet.topo import Topo


class Week7BaseTopo(Topo):
    def build(self) -> None:
        s1 = self.addSwitch("s1")
        h1 = self.addHost("h1", ip="10.0.7.11/24")
        h2 = self.addHost("h2", ip="10.0.7.12/24")
        self.addLink(h1, s1)
        self.addLink(h2, s1)


topos = {"week7base": Week7BaseTopo}
