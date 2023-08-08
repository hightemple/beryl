from lib.beryl import *



def test_flow_between_2pf():
    pf0 = PF('p1p1')
    all_vfs = []

    for i in range(4):
        vf = VF(f'p1p1_{i}', ip=f'1.1.1.{i}')
        pf0.add_vf(vf)
        all_vfs.append(vf)

    pf1 = PF('p2p1')
    for i in range(4):
        vf = VF(f'p2p1_{i}', ip=f'1.1.2.{i}')
        pf1.add_vf(vf)
        all_vfs.append(vf)

    server = BerylServer()
    server.connect()
    server.add_pf(pf0)
    server.add_pf(pf1)
    server.perform()
    pfs = server.get_pfs()
    print(pfs)
    for pf in pfs:
        print(pf)
        print(pf.get_vfs())

    for vf in all_vfs:
        print(vf)

    server.reset()

    for vf in all_vfs:
        print(vf)


    server.disconnect()


