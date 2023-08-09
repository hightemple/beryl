from lib.beryl import *
from lib.flow import create_m2m_flows
import time


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


def test_m2m_flows_between_vfs():
    vf_num = 4
    # 创建一个pf，名字为p1p1
    s_pf0 = PF('p1p1')
    # 为pf创建vf，数量为vf_num
    s_pf0.add_vfs_by_num(vf_num)

    c_pf0 = PF('p1p1')
    c_pf0.add_vfs_by_num(vf_num)

    # 创建一个server，ip为 10.211.3.223
    server1 = BerylServer(ip='10.211.3.223')
    # 将创建的pf添加到server中
    server1.add_pf(s_pf0)


    server2 = BerylServer(ip='10.211.3.224')
    server2.add_pf(c_pf0)


    for serv in [server1,server2]:
        # 连接到server
        serv.connect()
        # 执行server的配置并生效
        serv.perform()

    # 创建m2m流，从c_pf0的vf到s_pf0的vf
    flows = create_m2m_flows(c_pf0.get_vfs(), s_pf0.get_vfs())
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    print('start test parallel')

    # 默认是所有的流一起发，如果parallel=False，就是一个一个发
    flows.start()
    print('end test parallel')
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

    print('start test one by one')
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    flows.start(parallel=False)
    print('end test one by one')
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

    for serv in [server1,server2]:
        serv.disconnect()


def test_m2m_random_flows_between_vfs():
    vf_num = 10
    s_pf0 = PF('p1p1')
    s_pf0.add_vfs_by_num(vf_num, ip_start='1.1.1.1')

    c_pf0 = PF('p1p1')
    c_pf0.add_vfs_by_num(vf_num, ip_start='1.1.1.101')

    server1 = BerylServer(ip='10.211.3.223')
    server1.add_pf(s_pf0)

    server2 = BerylServer(ip='10.211.3.224')
    server2.add_pf(c_pf0)

    for serv in [server1, server2]:
        serv.connect()
        serv.perform()

    flows = create_m2m_flows(c_pf0.get_random_vfs(int(vf_num/2)), s_pf0.get_random_vfs(int(vf_num/2)))
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    print('-------start test parallel--------')
    # 打印当前的时间

    flows.start()
    print('-------end test parallel-------')
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

    print('\n\n-------start test one by one-------')
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    flows.start(parallel=False)
    print('-------end test one by one-------')
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

    for serv in [server1, server2]:
        serv.disconnect()
