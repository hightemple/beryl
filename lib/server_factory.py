import munch, yaml
from lib.beryl import BerylServer, Card, PF, VF

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




def create_server_by_config(conf: munch.Munch):
    '''
    server_conf1:
      ip: 10.211.3.223
      user: root
      password: 123456
      cards: ['card1']
      card1:
        name: mc50_1
        type: 25G
        pfs: ['pf1', 'pf2']
        pf1:
          if_name: p2p1
          ip: 1.1.1.1
          netmask: 24
          mac: 00:00:00:00:00:11
          vfs:
            vfs_per_pf: 2
            ip_start: 6.6.6.1
            netmask: 24
            mac_start: 01:11:00:00:00:01
        pf2:
          if_name: p2p1
          ip: 1.1.2.1
          netmask: 24
          mac: 00:00:00:00:00:21
          vfs:
            vfs_per_pf: 2
            ip_start: 6.6.6.11
            netmask: 24
            mac_start: 01:11:00:00:00:11

    '''
    server = BerylServer(conf.ip, conf.user, conf.password)
    for card_name in conf.cards:
        card_conf = conf[card_name]
        card = Card(card_name, card_conf.type)
        for pf_name in card_conf.pfs:
            pf_conf = card_conf[pf_name]
            pf = PF(pf_conf.if_name, pf_conf.ip, pf_conf.netmask, pf_conf.mac)
            pf.add_vfs_by_num(pf_conf.vfs.vfs_per_pf, pf_conf.vfs.ip_start, pf_conf.vfs.netmask, pf_conf.vfs.mac_start)
            card.add_pf(pf)
        server.add_card(card)
    return server