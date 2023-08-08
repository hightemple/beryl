# 创建一个PF类
class PF:
    def __init__(self, name):
        self.if_name = name
        self.vfs = []

    def add_vf(self, vf):
        self.vfs.append(vf)

    def get_vfs(self):
        return self.vfs

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
        return None

    def get_vf_index_by_vf(self, vf):
        for index, v in enumerate(self.vfs):
            if vf == v:
                return index
        return None


class VF:
    def __init__(self, name):
        self.if_name = name
        self.pf_name = None


    def get_pf_name(self):
        return self.pf_name

class Bond:
    def __init__(self, mode, ports):
        self.mode = mode
        self.ports = ports

class BerylServer:
    def __init__(self):
        self.pfs = []
        self.bond = None

    def add_pf(self, pf: PF):
        self.pfs.append(pf)

    def set_bond(self, bond: Bond):
        self.bond = bond

    def get_pfs(self):
        return self.pfs

    def add_pfs(self, pfs):
        self.pfs.extend(pfs)

    def perform(self):
        # 如果self.pfs 不为空， 查询每个pf的vfs，如果vfs不为空，就创建vf
        # 根据vfs的长度来创建vf的数量， 命令如下：echo 2 >  /sys/class/pci_bus/0000\:65/device/0000\:65\:00.0/sriov_numvfs
        for pf in self.pfs:
            vfs = pf.get_vfs()

            # If there are VFs for this PF, create VFs based on the number of VFs
            if vfs:
                num_vfs = len(vfs)
                sriov_numvfs_path = r"/sys/class/pci_bus/0000\:65/device/0000\:65\:00.0/sriov_numvfs"

                print(f"echo {num_vfs} > {sriov_numvfs_path}")





if __name__ == '__main__':
    pf0 = PF('eth0')
    vf = VF('eth0.1')
    pf0.add_vf(vf)
    vf = VF('eth0.2')
    pf0.add_vf(vf)
    vf = VF('eth0.3')
    pf0.add_vf(vf)

    pf1 = PF('eth1')
    vf = VF('eth1.1')
    pf1.add_vf(vf)
    vf = VF('eth1.2')
    pf1.add_vf(vf)
    vf = VF('eth1.3')
    pf1.add_vf(vf)

    server = BerylServer()
    server.add_pf(pf0)
    server.add_pf(pf1)

    server.perform()

