from lib.beryl import *



def test_add_some_vfs():
    pf0 = PF('p1p1')
    vf = VF('p1p1_1',ip='1.1.1.1')
    pf0.add_vf(vf)
    vf = VF('p1p1_2',ip='1.1.1.2')
    pf0.add_vf(vf)
    vf = VF('p1p1_3',ip='1.1.1.3')
    pf0.add_vf(vf)

    pf1 = PF('p2p1')
    vf = VF('p2p1_1',ip='1.1.2.1')
    pf1.add_vf(vf)
    vf = VF('p2p1_2',ip='1.1.2.2')
    pf1.add_vf(vf)
    vf = VF('p2p1_3',ip='1.1.2.3')
    pf1.add_vf(vf)

    server = BerylServer()
    server.add_pf(pf0)
    server.add_pf(pf1)

    server.perform()


def test_add_512vfs():
    pf0 = PF('p1p1')
    for i in range(512):
        vf = VF(f'p1p1_{i}',ip=f'1.1.1.{i}')
        pf0.add_vf(vf)

    pf1 = PF('p2p1')
    for i in range(512):
        vf = VF(f'p2p1_{i}',ip=f'1.1.2.{i}')
        pf1.add_vf(vf)

    server = BerylServer()
    server.add_pf(pf0)
    server.add_pf(pf1)

    server.perform()

def test_get_pfs():
    pf0 = PF('p1p1')
    for i in range(4):
        vf = VF(f'p1p1_{i}', ip=f'1.1.1.{i}')
        pf0.add_vf(vf)

    pf1 = PF('p2p1')
    for i in range(4):
        vf = VF(f'p2p1_{i}', ip=f'1.1.2.{i}')
        pf1.add_vf(vf)

    server = BerylServer()
    server.add_pf(pf0)
    server.add_pf(pf1)
    server.perform()
    pfs = server.get_pfs()
    print(pfs)
    for pf in pfs:
        print(pf)
        print(pf.get_vfs())

def test_change_vfs():
    pf0 = PF('p1p1')
    for i in range(4):
        vf = VF(f'p1p1_{i}', ip=f'1.1.1.{i}')
        pf0.add_vf(vf)

    pf1 = PF('p2p1')
    for i in range(4):
        vf = VF(f'p2p1_{i}', ip=f'1.1.2.{i}')
        pf1.add_vf(vf)

    server = BerylServer()
    server.connect()


    server.add_pf(pf0)
    server.add_pf(pf1)

    server.perform()

    server.disconnect()

