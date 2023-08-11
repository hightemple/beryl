import random
class NetDev:
    def __init__(self, if_name, ip, netmask, mac):

        self.ip = ip
        self.netmask = netmask
        self.mac = mac
        self.if_name = if_name

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return f"NetDev({self.if_name}:{self.ip}/{self.netmask})"

class VF(NetDev):
    def __init__(self, name, ip=None, netmask=24, mac=None, vlan=None):
        super().__init__(name, ip, netmask, mac)
        self.pf = None

    def __str__(self):
        return f"VF({self.if_name}:{self.ip}/{self.netmask}:{self.mac}:{self.pf})"

    def __repr__(self):
        return self.__str__()

    def get_pf_name(self):
        return self.pf.if_name

    def get_server(self):
        return self.pf.server


# 创建一个PF类
class PF(NetDev):
    def __init__(self, name, ip=None, netmask=24, mac=None):
        super().__init__(name, ip, netmask, mac)
        self.server = None
        self.card = None
        self.vfs = []

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return f"PF({self.if_name}:{self.card}:{self.server}:{len(self.vfs)}VFs)"

    def add_vf(self, vf: VF):
        vf.pf = self
        self.vfs.append(vf)

    def add_vfs(self, vfs):
        for vf in vfs:
            self.add_vf(vf)

    def add_vfs_by_num(self, vf_num, ip_start='1.1.1.1', netmask=24, mac_start='00:00:00:00:00:01'):
        for i in range(vf_num):
            # 希望vf的ip地址是连续的，所以ip地址的最后一位要加1, mac地址也是一样,并且mac地址必须符合规范
            self.add_vf(VF(f'{self.if_name}_{i}', ip=f'{ip_start[:-1]}{int(ip_start[-1])+i}', netmask=netmask,
                           mac=f'{mac_start[:-2]}{i+int(mac_start[-2]):02x}'))


    def remove_all_vfs(self):
        for vf in self.vfs:
            vf.pf = None
        self.vfs = []


    def get_vfs(self):
        return self.vfs

    def get_random_vfs(self , vf_num):
        #从所有的vf中随机选择vf_num个vf
        if vf_num > len(self.vfs):
            raise ValueError("vf_num is bigger than the number of vfs")

        return random.sample(self.vfs , vf_num)

    def get_if_name(self):
        return self.if_name

    def get_vf_by_name(self, name):
        for vf in self.vfs:
            if vf.if_name == name:
                return vf
        return None

    def get_vf_by_index(self, index):
        if index < len(self.vfs):
            return self.vfs[index]
        return None

    def get_vf_index_by_name(self, name):
        for index, vf in enumerate(self.vfs):
            if vf.if_name == name:
                return index
        return None

    def get_vf_index_by_vf(self, vf):
        for index, v in enumerate(self.vfs):
            if vf == v:
                return index
        return None

    def get_server(self):
        return self.server


class Card:
    def __init__(self, name, pfs:[PF]):
        self.name = name
        self.server = None
        self.pfs = pfs

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return f"PF({self.name}:{self.server}:{len(self.pfs)}PFs)"

    def add_pf(self, pf:PF):
        self.pfs.append(pf)

    def add_pfs(self, pfs):
        for pf in pfs:
            self.add_pf(pf)

    def get_pfs(self):
        return self.pfs

    def get_pf_by_name(self, name):
        for pf in self.pfs:
            if pf.if_name == name:
                return pf
        return None

    def get_pf_by_index(self, index):
        if index < len(self.pfs):
            return self.pfs[index]
        return None



class Bond:
    def __init__(self, name, net_devs:NetDev, ip, netmask=24, mode='4'):
        self.name = name
        self.mode = mode
        self.net_devs = net_devs
        self.ip = ip
        self.netmask = netmask
        self.primary = None
        self.xmit_hash_policy = None

    def set_primary(self, primary:NetDev):
        self.primary = primary

    def set_xmit_hash_policy(self, hash_policy:str):
        self.xmit_hash_policy = hash_policy



class SSHable:
    def __init__(self, ip, username, password):
        self.ip = ip
        self.username = username
        self.password = password

    def connect(self):
        print("connect to server")

    def disconnect(self):
        print("disconnect to server")

    def run_cmd(self, cmd):
        print(f"[{self.ip}] SEND: {cmd} ")


class BerylServer(SSHable):
    def __init__(self, ip='10.211.3.223', username='root', password='root123'):
        super().__init__(ip, username, password)
        self.cards = []
        self.pfs = []
        self.bonds = []

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return f"PF({self.ip}:{len(self.cards)}Cards{len(self.pfs)}PFs)"


    def add_card(self, card: Card):
        self.cards.append(card)
        card.server = self

        for pf in card.get_pfs():
            self.pfs.append(pf)

    def add_cards(self, cards:[Card]):
        for card in cards:
            self.cards.append(card)

    def get_cards(self):
        return self.cards

    def add_pf(self, pf: PF, card=None):
        if card is None:
            card = Card('card0', [pf])

        card.add_pf(pf)
        self.add_card(card)




    def add_pfs(self, pfs: [PF]):
        for pf in pfs:
            self.pfs.append(pf)

    def get_pfs(self):
        return self.pfs


    def perform(self):
        # 如果self.pfs 不为空， 查询每个pf的vfs，如果vfs不为空，就创建vf
        # 根据vfs的长度来创建vf的数量， 命令如下：echo 2 >  /sys/class/pci_bus/0000\:65/device/0000\:65\:00.0/sriov_numvfs
        self.__apply_pfs_vfs()

        self.__apply_bonds()

    def __apply_pfs_vfs(self):
        sriov_numvfs_path = r"/sys/class/pci_bus/0000\:65/device/0000\:65\:00.0/sriov_numvfs"
        for pf in self.pfs:
            vfs = pf.get_vfs()

            # If there are VFs for this PF, create VFs based on the number of VFs
            if vfs:
                num_vfs = len(vfs)

                self.run_cmd(f"echo {num_vfs} > {sriov_numvfs_path}")

                # ip link set dev p1p1_0 up
                # ip addr add dev p1p1_0 6.6.6.2/24

                for vf in vfs:
                    self.run_cmd(f"ip link set dev {vf.if_name} up")
                    self.run_cmd(f"ip addr add dev {vf.if_name} {vf.ip}/{vf.netmask}")

    def __apply_bonds(self):
        for bond in self.bonds:
            self.run_cmd(f"ip link set dev {bond.name} up")
            for dev in bond.net_devs:
                self.run_cmd(f"ip link set dev {dev.if_name} up")
            self.run_cmd(f"ip addr add dev {bond.name} {bond.ip}/{bond.netmask}")


            if bond.mode == '4':
                if bond.xmit_hash_policy :
                    self.run_cmd(f"ip link add {bond.name} mode {bond.mode}")
                    self.run_cmd(f"ip link set {bond.name} type bond xmit_hash_policy policy {bond.xmit_hash_policy}")

            elif bond.mode == 'active-backup':
                self.run_cmd(f"ip link add {bond.name} mode {bond.mode}")
                if bond.primary:
                    self.run_cmd(f"ip link set {bond.name} type bond primary {bond.primary.if_name}")

    def reset(self):
        for pf in self.pfs:
            pf.remove_all_vfs()
        self.perform()

    def add_bond(self, bond: Bond):
        self.bonds.append(bond)

    def add_bonds(self, bonds):
        for bond in bonds:
            self.bonds.append(bond)



if __name__ == '__main__':
    pf0 = PF('eth0')
    vf = VF('eth0.1',ip='1.1.1.1')
    pf0.add_vf(vf)
    vf = VF('eth0.2',ip='1.1.1.2')
    pf0.add_vf(vf)
    vf = VF('eth0.3',ip='1.1.1.3')
    pf0.add_vf(vf)

    pf1 = PF('eth1')
    vf = VF('eth1.1',ip='1.1.2.1')
    pf1.add_vf(vf)
    vf = VF('eth1.2',ip='1.1.2.1')
    pf1.add_vf(vf)
    vf = VF('eth1.3',ip='1.1.2.1')
    pf1.add_vf(vf)

    server = BerylServer()
    server.add_pf(pf0)
    server.add_pf(pf1)

    server.perform()

