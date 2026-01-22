#!/usr/bin/env python3
"""
Seminarul 6 – Controller SDN (OS-Ken + OpenFlow 1.3)

Controller didactic pentru topologia SDN cu politici de securitate.

Arhitectura SDN:
┌─────────────────────────────────────────┐
│            Control Plane                │
│  ┌─────────────────────────────────┐    │
│  │      Controller (acest fișier)  │    │
│  │   - Primește packet_in          │    │
│  │   - Decide politica             │    │
│  │   - Instalează flow-uri         │    │
│  └──────────────┬──────────────────┘    │
└─────────────────┼───────────────────────┘
                  │ OpenFlow 1.3
┌─────────────────┼───────────────────────┐
│            Data Plane                   │
│  ┌──────────────▼──────────────────┐    │
│  │      Switch OVS (s1)            │    │
│  │   - Flow table (match→action)   │    │
│  │   - Forwarding hardware/soft    │    │
│  └─────────────────────────────────┘    │
└─────────────────────────────────────────┘

Politica implementată:
- h1 (10.0.6.11) ↔ h2 (10.0.6.12): PERMIT (tot traficul)
- * → h3 (10.0.6.13): DROP (implicit)
- UDP → h3: CONFIGURABIL (vezi ALLOW_UDP_TO_H3)

Utilizare:
    osken-manager sdn_policy_controller.py
    
    # Opțional, cu debugging verbose:
    osken-manager --verbose sdn_policy_controller.py
"""

from __future__ import annotations

from os_ken.base import app_manager
from os_ken.controller import ofp_event
from os_ken.controller.handler import (
    MAIN_DISPATCHER,
    CONFIG_DISPATCHER,
    set_ev_cls
)
from os_ken.ofproto import ofproto_v1_3
from os_ken.lib.packet import packet, ethernet, ipv4, arp


# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURAȚIE DIDACTICĂ - studenții pot modifica aceste constante
# ═══════════════════════════════════════════════════════════════════════════

# Schimbați în True pentru a permite UDP către h3 (dar TCP rămâne blocat)
ALLOW_UDP_TO_H3 = False

# Adresele IP ale hosturilor (corespund topologiei topo_sdn.py)
# Standard Week 6: 10.0.6.0/24
H1_IP = "10.0.6.11"
H2_IP = "10.0.6.12"
H3_IP = "10.0.6.13"

# Port fallback pentru h3 (în topologia noastră: port 3)
H3_PORT_FALLBACK = 3

# Timeout pentru flow-uri instalate (secunde)
FLOW_IDLE_TIMEOUT = 60
FLOW_HARD_TIMEOUT = 0  # 0 = fără hard timeout


class SDNPolicyController(app_manager.OSKenApp):
    """
    Controller SDN cu politici de securitate per-host și per-protocol.
    
    Funcționare:
    1. La conectarea switch-ului: instalează regula table-miss
    2. La packet_in: învață MAC-uri, apoi decide:
       - ARP: flood/forward pentru funcționare L2
       - IPv4 h1↔h2: instalează flow-uri allow
       - IPv4 *→h3: instalează flow drop (sau allow UDP dacă configurat)
       - Restul: L2 learning switch basic
    """
    
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Tabel de învățare: dpid → {mac → port}
        self.mac_to_port: dict[int, dict[str, int]] = {}
    
    # ───────────────────────────────────────────────────────────────────────
    # Event handler: Switch conectat
    # ───────────────────────────────────────────────────────────────────────
    
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def on_switch_features(self, ev):
        """
        Apelat când switch-ul se conectează la controller.
        
        Instalăm regula table-miss cu prioritate 0:
        - Match: orice pachet (match gol)
        - Action: trimite la controller (OFPP_CONTROLLER)
        
        Această regulă asigură că pachetele necunoscute ajung la controller
        pentru a fi procesate și a genera flow-uri specifice.
        """
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        
        # Match gol = potrivește orice
        match = parser.OFPMatch()
        
        # Acțiune: trimite la controller
        actions = [
            parser.OFPActionOutput(
                ofproto.OFPP_CONTROLLER,
                ofproto.OFPCML_NO_BUFFER
            )
        ]
        
        # Instalează cu prioritate minimă (0)
        self._add_flow(datapath, priority=0, match=match, actions=actions)
        
        self.logger.info(
            "Table-miss installed on dpid=%s (packets→controller)", 
            datapath.id
        )
    
    # ───────────────────────────────────────────────────────────────────────
    # Helper: Instalare flow
    # ───────────────────────────────────────────────────────────────────────
    
    def _add_flow(
        self,
        datapath,
        priority: int,
        match,
        actions: list,
        buffer_id=None,
        idle_timeout: int = FLOW_IDLE_TIMEOUT,
        hard_timeout: int = FLOW_HARD_TIMEOUT
    ):
        """
        Instalează un flow în switch.
        
        Args:
            datapath: Switch-ul țintă
            priority: Prioritatea regulii (mai mare = verificat mai întâi)
            match: Criteriile de potrivire
            actions: Lista de acțiuni (gol = drop)
            buffer_id: ID buffer dacă pachetul e în switch
            idle_timeout: Ștergere după X secunde de inactivitate
            hard_timeout: Ștergere după X secunde (0 = niciodată)
        """
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        
        # Construiește instrucțiunile (wrapper peste acțiuni)
        instructions = [
            parser.OFPInstructionActions(
                ofproto.OFPIT_APPLY_ACTIONS,
                actions
            )
        ]
        
        # Parametri flow_mod
        kwargs = dict(
            datapath=datapath,
            priority=priority,
            match=match,
            instructions=instructions,
            idle_timeout=idle_timeout,
            hard_timeout=hard_timeout,
        )
        
        # Dacă pachetul e în buffer, îl legăm de flow
        if buffer_id is not None and buffer_id != ofproto.OFP_NO_BUFFER:
            kwargs["buffer_id"] = buffer_id
        
        # Trimite mesajul flow_mod
        flow_mod = parser.OFPFlowMod(**kwargs)
        datapath.send_msg(flow_mod)
    
    # ───────────────────────────────────────────────────────────────────────
    # Helper: MAC learning
    # ───────────────────────────────────────────────────────────────────────
    
    def _learn_mac(self, dpid: int, mac: str, port: int) -> None:
        """Învață asocierea MAC → port pentru un switch."""
        self.mac_to_port.setdefault(dpid, {})
        self.mac_to_port[dpid][mac] = port
    
    def _get_port(self, dpid: int, mac: str, fallback=None) -> int:
        """Obține portul pentru un MAC, sau fallback dacă necunoscut."""
        return self.mac_to_port.get(dpid, {}).get(mac, fallback)
    
    # ───────────────────────────────────────────────────────────────────────
    # Event handler: Packet-in (pachet necunoscut)
    # ───────────────────────────────────────────────────────────────────────
    
    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def on_packet_in(self, ev):
        """
        Apelat când switch-ul trimite un pachet necunoscut.
        
        Flux de procesare:
        1. Extrage informații din pachet (MAC-uri, IP-uri)
        2. Învață MAC-ul sursă
        3. Tratează ARP (flood/forward pentru funcționare L2)
        4. Tratează IPv4 conform politicii:
           - h1↔h2: permit
           - *→h3: drop (sau permit UDP)
           - restul: L2 learning switch
        """
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        dpid = datapath.id
        in_port = msg.match["in_port"]
        
        # Parsează pachetul
        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]
        
        src_mac = eth.src
        dst_mac = eth.dst
        
        # Învață MAC sursă
        self._learn_mac(dpid, src_mac, in_port)
        
        # ─────────────────────────────────────────────────────────────────
        # Tratare ARP: learning + flood/forward
        # ─────────────────────────────────────────────────────────────────
        
        arp_pkt = pkt.get_protocol(arp.arp)
        if arp_pkt:
            # Log pentru debugging
            self.logger.debug(
                "ARP: %s → %s (op=%s)",
                arp_pkt.src_ip, arp_pkt.dst_ip, arp_pkt.opcode
            )
            
            # Determină portul de ieșire
            out_port = self._get_port(dpid, dst_mac, fallback=ofproto.OFPP_FLOOD)
            
            # Trimite pachetul (nu instalăm flow pentru ARP)
            actions = [parser.OFPActionOutput(out_port)]
            out = parser.OFPPacketOut(
                datapath=datapath,
                buffer_id=ofproto.OFP_NO_BUFFER,
                in_port=in_port,
                actions=actions,
                data=msg.data
            )
            datapath.send_msg(out)
            return
        
        # ─────────────────────────────────────────────────────────────────
        # Tratare IPv4: aplicare politică
        # ─────────────────────────────────────────────────────────────────
        
        ip_pkt = pkt.get_protocol(ipv4.ipv4)
        if not ip_pkt:
            # Nu e IPv4, ignorăm
            return
        
        src_ip = ip_pkt.src
        dst_ip = ip_pkt.dst
        proto = ip_pkt.proto  # 1=ICMP, 6=TCP, 17=UDP
        
        self.logger.info(
            "IPv4: %s → %s (proto=%s) in_port=%s",
            src_ip, dst_ip, proto, in_port
        )
        
        # ─────────────────────────────────────────────────────────────────
        # Politica 1: Permit h1 ↔ h2
        # ─────────────────────────────────────────────────────────────────
        
        if self._is_h1_h2_traffic(src_ip, dst_ip):
            out_port = self._get_port(dpid, dst_mac, fallback=ofproto.OFPP_FLOOD)
            actions = [parser.OFPActionOutput(out_port)]
            
            # Instalează flow pentru acest trafic
            match = parser.OFPMatch(
                eth_type=0x0800,
                ipv4_src=src_ip,
                ipv4_dst=dst_ip
            )
            self._add_flow(
                datapath,
                priority=10,
                match=match,
                actions=actions,
                buffer_id=msg.buffer_id if msg.buffer_id != ofproto.OFP_NO_BUFFER else None
            )
            
            # Trimite pachetul curent
            if msg.buffer_id == ofproto.OFP_NO_BUFFER:
                self._send_packet_out(datapath, in_port, actions, msg.data)
            
            self.logger.info(
                "ALLOW: %s → %s (proto=%s) out_port=%s",
                src_ip, dst_ip, proto, out_port
            )
            return
        
        # ─────────────────────────────────────────────────────────────────
        # Politica 2: Tratare trafic către h3
        # ─────────────────────────────────────────────────────────────────
        
        if dst_ip == H3_IP:
            # Cazul special: UDP permis (dacă configurat)
            if proto == 17 and ALLOW_UDP_TO_H3:
                out_port = self._get_port(dpid, dst_mac, fallback=H3_PORT_FALLBACK)
                actions = [parser.OFPActionOutput(out_port)]
                
                # Flow pentru UDP către h3
                match = parser.OFPMatch(
                    eth_type=0x0800,
                    ip_proto=17,
                    ipv4_dst=H3_IP
                )
                self._add_flow(
                    datapath,
                    priority=20,
                    match=match,
                    actions=actions,
                    buffer_id=msg.buffer_id if msg.buffer_id != ofproto.OFP_NO_BUFFER else None
                )
                
                if msg.buffer_id == ofproto.OFP_NO_BUFFER:
                    self._send_packet_out(datapath, in_port, actions, msg.data)
                
                self.logger.info("ALLOW UDP → %s out_port=%s", H3_IP, out_port)
                return
            
            # Implicit: DROP (flow fără acțiuni)
            match_kwargs = dict(eth_type=0x0800, ipv4_dst=H3_IP)
            
            # Opțional: match și pe protocol pentru a vedea reguli separate
            if proto in (1, 6, 17):  # ICMP, TCP, UDP
                match_kwargs["ip_proto"] = proto
            
            match = parser.OFPMatch(**match_kwargs)
            actions = []  # Lista goală = DROP
            
            self._add_flow(
                datapath,
                priority=30,
                match=match,
                actions=actions,
                buffer_id=msg.buffer_id if msg.buffer_id != ofproto.OFP_NO_BUFFER else None
            )
            
            self.logger.info(
                "DROP: → %s (proto=%s)",
                H3_IP, proto
            )
            return
        
        # ─────────────────────────────────────────────────────────────────
        # Implicit: L2 learning switch
        # ─────────────────────────────────────────────────────────────────
        
        out_port = self._get_port(dpid, dst_mac, fallback=ofproto.OFPP_FLOOD)
        actions = [parser.OFPActionOutput(out_port)]
        
        # Instalează flow doar dacă știm portul
        if out_port != ofproto.OFPP_FLOOD:
            match = parser.OFPMatch(in_port=in_port, eth_dst=dst_mac)
            self._add_flow(
                datapath,
                priority=1,
                match=match,
                actions=actions,
                buffer_id=msg.buffer_id if msg.buffer_id != ofproto.OFP_NO_BUFFER else None
            )
        
        # Trimite pachetul
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            self._send_packet_out(datapath, in_port, actions, msg.data)
    
    # ───────────────────────────────────────────────────────────────────────
    # Helpers privați
    # ───────────────────────────────────────────────────────────────────────
    
    def _is_h1_h2_traffic(self, src_ip: str, dst_ip: str) -> bool:
        """Verifică dacă traficul este între h1 și h2."""
        return (
            (src_ip == H1_IP and dst_ip == H2_IP) or
            (src_ip == H2_IP and dst_ip == H1_IP)
        )
    
    def _send_packet_out(self, datapath, in_port: int, actions: list, data: bytes):
        """Trimite un pachet individual prin switch."""
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        
        out = parser.OFPPacketOut(
            datapath=datapath,
            buffer_id=ofproto.OFP_NO_BUFFER,
            in_port=in_port,
            actions=actions,
            data=data
        )
        datapath.send_msg(out)
