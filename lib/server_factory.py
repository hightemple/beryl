import munch, yaml


def load_yaml_topo(yaml_file):
    """This function is to load YAML file as an object

        Args:
          yaml_file (str): the YAML file name

        Return:
          YAML object

    """

    with open(yaml_file, 'r') as f:
        yaml_dict = yaml.safe_load(f)
    yaml_obj = munch.munchify(yaml_dict)

    return yaml_obj


def create_standard_server(card_num=1, pfs_per_card=2, vfs_per_pf=4):
    server = BerylServer()
    for card_index in range(card_num):
        card = Card(f'card{card_index}')
        for pf_index in range(pfs_per_card):
            pf = PF(f'p2p_{pf_index + 1}')
            for vf_index in range(vfs_per_pf):
                vf = VF(f'p2p_{pf_index + 1}_{vf_index}')
                pf.add_vf(vf)
            card.add_pf(pf)
        server.add_card(card)
    return server


def create_server_by_config(conf: munch.Munch):
    '''
    server_conf1:
      ip: 10.211.3.223
      user: root
      password: 123456
      cards:
        num: 1
        type: 25G
      pfs:
        pfs_per_card: 2
        intf_start: p2p1
        ip_start: 1.1.1.1
        netmask: 24
        mac_start: 00:00:00:00:00:01
      vfs:
        vfs_per_pf: 2
        ip_start: 6.6.6.1
        netmask: 24
        mac_start: 01:11:00:00:00:01

    '''
    server = BerylServer(conf.ip, conf.user, conf.password)
    for card_index in range(conf.cards.num):
        card = Card(f'card{card_index}')
        card.add_pfs_by_num(conf.pfs.pfs_per_card, conf.pfs.intf_start, conf.pfs.ip_start, conf.pfs.netmask,
                            conf.pfs.mac_start)

        for pf in card.get_pfs():
            pf.add_vfs_by_num(conf.vfs.vfs_per_pf, conf.vfs.ip_start, conf.vfs.netmask, conf.vfs.mac_start)
        server.add_card(card)

    return server
