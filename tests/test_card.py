from lib.beryl import *

def test_create_card():
    """
    Test case to add a card.
    """
    print("Test case to add a card.")
    pf0 = PF('p1p1')
    pf0.add_vfs_by_num(2)
    pf1 = PF('p2p1')
    pf1.add_vfs_by_num(2)

    card = Card('card1')
    card.add_pf(pf0)
    card.add_pf(pf1)

    print(card)

def test_add_pfs_by_num():
    """
    Test case to add a card.
    """
    print("Test case to add a card.")


    card = Card('card1')
    card.add_pfs_by_num(2)
    print(card)


    for pf in card.pfs:
        pf.add_vfs_by_num(2)
        print(pf)
        for vf in pf.vfs:
            print(vf)

