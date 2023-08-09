from lib.beryl import *
from lib.flow import create_m2m_flows


def test_add_some_vfs_2_pf():
    pf0 = PF('p1p1')
    pf0.add_vfs_by_num(10)

    vfs = pf0.get_vfs()

    for vf in vfs:
        print(vf)

    server1 = BerylServer(ip='10.211.3.223')
    server1.add_pf(pf0)


    server1.connect()

    server1.perform()
    server1.disconnect()


def test_m2m_flows_between_2_pf():
    s_pf0 = PF('p1p1')
    s_pf0.add_vfs_by_num(10)

    c_pf0 = PF('p1p1')
    c_pf0.add_vfs_by_num(10)

    server1 = BerylServer(ip='10.211.3.223')
    server1.add_pf(s_pf0)


    server2 = BerylServer(ip='10.211.3.224')
    server2.add_pf(c_pf0)


    for serv in [server1,server2]:
        serv.connect()
        serv.perform()


    flows = create_m2m_flows(c_pf0.get_vfs(), s_pf0.get_vfs())
    flows.start()

    for serv in [server1,server2]:
        serv.disconnect()