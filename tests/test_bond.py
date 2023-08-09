from lib.beryl import *



def test_bond_2pf_mode_4():
    pf0 = PF('p1p1')
    pf1 = PF('p1p2')

    server1 = BerylServer(ip='10.211.3.223')
    server1.add_pf(pf0)

    bond0 = Bond('bond0', [pf0, pf1], ip='1.1.1.1', netmask=24, mode=4)
    server1.add_bond(bond0)

    server1.connect()

    server1.perform()
    server1.disconnect()

def test_bond_2pf_mode_active_backup():
    pf0 = PF('p1p1')
    pf1 = PF('p1p2')

    server1 = BerylServer(ip='10.211.3.223')
    server1.add_pf(pf0)

    bond0 = Bond('bond0', [pf0, pf1], mode='active-backup',ip='1.1.1.1', netmask=24)
    bond0.set_primary(pf0)
    server1.add_bond(bond0)

    server1.connect()

    server1.perform()
    server1.disconnect()

