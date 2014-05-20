# -*- coding: utf-8 -*-

from ryu.base import app_manager
from ryu.controller.handler import set_ev_cls, MAIN_DISPATCHER
from ryu.controller import ofp_event
from ryu.topology import switches, event
from ryu.lib import ofctl_v1_3
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet, ipv6, icmpv6
from ryu.lib.ofp_pktinfilter import packet_in_filter, RequiredTypeFilter


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
    def _packet_in_handler(self, ev):
        pkt = packet.Packet(ev.msg.data)
        print("\n@packet_in_filter: \n -- " + str(pkt))
