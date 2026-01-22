"""Topologie firewall Săptămâna 7 (două subrețele cu un router Linux).

Traficul trece prin host-ul router `fw`, unde sunt aplicate regulile de filtrare.

Plan de adresare (tot în 10.0.7.0/24, împărțit în două subrețele /25):
- subrețeaua stângă:  10.0.7.0/25
  - h1: 10.0.7.11/25, rută implicită via 10.0.7.1
  - fw-eth0: 10.0.7.1/25
- subrețeaua dreaptă: 10.0.7.128/25
  - fw-eth1: 10.0.7.129/25
  - h2: 10.0.7.200/25, rută implicită via 10.0.7.129
"""

from mininet.node import Node
from mininet.topo import Topo


class LinuxRouter(Node):
    """Un Node cu IPv4 forwarding activat."""

    def config(self, **params):
        super().config(**params)
        self.cmd("sysctl -w net.ipv4.ip_forward=1")

    def terminate(self):
        self.cmd("sysctl -w net.ipv4.ip_forward=0")
        super().terminate()


class Week7FirewallTopo(Topo):
    def build(self) -> None:
        s1 = self.addSwitch("s1")
        s2 = self.addSwitch("s2")

        h1 = self.addHost("h1", ip="10.0.7.11/25", defaultRoute="via 10.0.7.1")
        h2 = self.addHost("h2", ip="10.0.7.200/25", defaultRoute="via 10.0.7.129")

        fw = self.addHost("fw", cls=LinuxRouter)

        # Legături
        self.addLink(h1, s1)
        self.addLink(h2, s2)

        # Legături router cu IP-uri explicite pe interfețele fw
        self.addLink(fw, s1, intfName1="fw-eth0", params1={"ip": "10.0.7.1/25"})
        self.addLink(fw, s2, intfName1="fw-eth1", params1={"ip": "10.0.7.129/25"})


topos = {"week7fw": Week7FirewallTopo}
