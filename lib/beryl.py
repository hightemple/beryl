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





if __name__ == '__main__':
    pf = PF('eth0')
    vf = VF('eth0.1')
    vf.set_pf_name(pf.if_name)
    print( vf.get_pf_name())