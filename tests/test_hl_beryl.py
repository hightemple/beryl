from lib.beryl import *
from lib.server_factory import *
from lib.flow import *
import time


def test_load_yaml():
    conf_obj = load_yaml_topo('./topo.yaml')
    print(conf_obj)


def test_create_server_from_yaml():
    topo = load_yaml_topo('./topo.yaml')
    server = create_server_by_config(topo.server_conf1)
    print(server)

    for card in server.cards:
        print(card)
        for pf in card.pfs:
            print(pf)
            for vf in pf.vfs:
                print(vf)



def test_hl_flow_inner_node_1_flow_ping():
    topo = load_yaml_topo('./topo.yaml')
    server = create_server_by_config(topo.server_conf1)
    flow_params = PingFlowParams()

    server.connect()
    server.perform()
    flows = create_p2p_flows(server.cards[0].pfs[0].vfs[0], server.cards[0].pfs[1].vfs[0], flow_params)
    flows.start()

    server.disconnect()

def test_hl_flow_inner_node_1_flow_iperf():
    topo = load_yaml_topo('./topo.yaml')
    server = create_server_by_config(topo.server_conf1)
    flow_params =IperfFlowParams()

    server.connect()
    server.perform()
    flows = create_p2p_flows(server.cards[0].pfs[0].vfs[0], server.cards[0].pfs[1].vfs[0], flow_params)
    flows.start()

    server.disconnect()

def test_hl_flow_cross_node():
    topo = load_yaml_topo('./topo.yaml')
    server1 = create_server_by_config(topo.server_conf1)
    server2 = create_server_by_config(topo.server_conf2)
    for server in [server1, server2]:
        server.connect()
        server.perform()

    flows = create_m2m_flows(server1.cards[0].pfs[0].vfs, server2.cards[0].pfs[1].vfs, flow_params=PingFlowParams())
    flows.start(parallel=False)

    flows = create_m2m_flows(server1.cards[0].pfs[0].vfs, server2.cards[0].pfs[1].vfs, flow_params =IperfFlowParams())
    flows.start(parallel=False)



    server.disconnect()

