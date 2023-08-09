from lib.beryl import *
from lib.flow import create_flows


def test_flow_between_2pf():
    s_pf0 = PF('p1p1',ip='6.6.6.1')


    c_pf0 = PF('p1p1',ip='6.6.6.2')


    server1 = BerylServer(ip='10.211.3.223')
    server1.add_pf(s_pf0)
    server2 = BerylServer(ip='10.211.3.224')
    server2.add_pf(c_pf0)

    for serv in [server1,server2]:
        serv.connect()
        serv.perform()

    print(s_pf0)
    print(c_pf0)

    flows = create_flows(c_pf0, s_pf0)
    flows.start()



def test_flow_between_2vf():
    s_pf0 = PF('p1p1')
    s_vf0 = VF('p1p1_1',ip='6.6.6.1')
    s_vf1 = VF('p1p1_2',ip='6.6.6.2')
    s_pf0.add_vfs([s_vf0,s_vf1])

    c_pf0 = PF('p1p1')
    c_vf0 = VF('p1p1_1',ip='6.6.6.11')
    c_vf1 = VF('p1p1_2',ip='6.6.6.12')
    c_pf0.add_vfs([c_vf0,c_vf1])


    server1 = BerylServer(ip='10.211.3.223')
    server1.add_pf(s_pf0)
    server2 = BerylServer(ip='10.211.3.224')
    server2.add_pf(c_pf0)

    for serv in [server1,server2]:
        serv.connect()
        serv.perform()

    print(s_vf0)
    print(c_vf0)

    flows = create_flows(c_vf0, s_vf0)
    flows.start()


def test_flow_between_2_pf_4_flows():
    s_pf0 = PF('p1p1',ip='6.6.6.1')


    c_pf0 = PF('p1p1',ip='6.6.6.2')


    server1 = BerylServer(ip='10.211.3.223')
    server1.add_pf(s_pf0)
    server2 = BerylServer(ip='10.211.3.224')
    server2.add_pf(c_pf0)

    for serv in [server1,server2]:
        serv.connect()
        serv.perform()

    print(s_pf0)
    print(c_pf0)

    flows = create_flows(c_pf0, s_pf0, flow_num=4)
    flows.start()




def test_flow_between_2vf_4_flows():
    s_pf0 = PF('p1p1')
    s_vf0 = VF('p1p1_1',ip='6.6.6.1')
    s_vf1 = VF('p1p1_2',ip='6.6.6.2')
    s_pf0.add_vfs([s_vf0,s_vf1])

    c_pf0 = PF('p1p1')
    c_vf0 = VF('p1p1_1',ip='6.6.6.11')
    c_vf1 = VF('p1p1_2',ip='6.6.6.12')
    c_pf0.add_vfs([c_vf0,c_vf1])


    server1 = BerylServer(ip='10.211.3.223')
    server1.add_pf(s_pf0)
    server2 = BerylServer(ip='10.211.3.224')
    server2.add_pf(c_pf0)

    for serv in [server1,server2]:
        serv.connect()
        serv.perform()

    print(s_vf0)
    print(c_vf0)

    flows = create_flows(c_vf0, s_vf0, flow_num=4)
    flows.start()
