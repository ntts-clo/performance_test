# -*- coding: utf-8 -*-

from ryu.base import app_manager
from ryu.controller.handler import set_ev_cls, MAIN_DISPATCHER
from ryu.controller import ofp_event
from ryu.topology import switches, event
from ryu.lib import ofctl_v1_3
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet, ipv6, icmpv6
from ryu.lib.ofp_pktinfilter import packet_in_filter, RequiredTypeFilter, PacketInFilterBase


class NDFilter(PacketInFilterBase):
    def filter(self, pkt):
        _type = pkt.get_protocol(icmpv6.icmpv6).type_
        if _type != icmpv6.ND_NEIGHBOR_SOLICIT:
            return False
        return True


class MLDFilter(PacketInFilterBase):
    MLD_TYPE_LIST = [
        icmpv6.MLD_LISTENER_QUERY,
        icmpv6.MLD_LISTENER_REPOR,
        icmpv6.MLD_LISTENER_DONE,
        icmpv6.MLDV2_LISTENER_REPORT
    ]

    def filter(self, pkt):
        _type = pkt.get_protocol(icmpv6.icmpv6).type_
        if not _type in self.MLD_TYPE_LIST:
            return False
        return True


class FilterSample(app_manager.RyuApp):
    OFP_VERSIONS = [
        ofproto_v1_3.OFP_VERSION,
    ]
    _CONTEXTS = {
        'switches': switches.Switches,
    }

    @set_ev_cls(event.EventSwitchEnter)
    def _switch_enter_handler(self, ev):
        datapath = ev.switch.dp
        print('New switch is joined: %s' % datapath.id)
        flow = {
            'match': {
                # Match any packets
            },
            'actions': [
                {
                    'type': 'OUTPUT',
                    'port': ofproto_v1_3.OFPP_CONTROLLER,
                    'max_len': ofproto_v1_3.OFPCML_MAX,
                },
            ]
        }
        ofctl_v1_3.mod_flow_entry(
            datapath,
            flow,
            ofproto_v1_3.OFPFC_ADD,
        )

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    @packet_in_filter(RequiredTypeFilter, args={
        'types': [
            ethernet.ethernet,
            ipv6.ipv6,
            icmpv6.icmpv6,
        ]
    })
    @packet_in_filter(NDFilter)
    def _packet_in_handler(self, ev):
        pkt = packet.Packet(ev.msg.data)
        print("\n@packet_in_filter: NDFilter(ping6)\n -- " + str(pkt))
        _type = pkt.get_protocol(icmpv6.icmpv6).type_
        print("\nicmpv6 type: \n -- " + str(_type))
