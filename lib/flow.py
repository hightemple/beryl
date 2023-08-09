import random
import threading
import time


# 设计思路：
# 1. flow可以绑定pf，也可以绑定到vf
# 2. flow可以绑定到多个pf，也可以绑定到多个vf
# 3. flow使用iperf3进行测试
# 4. flow可以根据pf或vf对象所包含的信息来给出iperf3的命令

def create_p2p_flows(c_device, s_device, flow_num = 1):
    flows = Flows()
    for i in range(flow_num):
        flows.add_flow(Flow(c_device, s_device))
    return flows

# 创建多对多的流
def create_m2m_flows(c_devices, s_devices, flow_num = 1):
    flows = Flows()
    for c_device, s_device in zip(c_devices, s_devices):
        for i in range(flow_num):
            flows.add_flow(Flow(c_device, s_device))
    return flows

class Flow:
    def __init__(self, c_device, s_device,packet_size=64, interval=1, type='udp', duration=2):
        self.packet_size = packet_size

        self.interval = interval
        self.type = type
        self.duration = duration
        self.c_device = c_device
        self.s_device = s_device
        self.log = None

    def start(self):

        # 生成一个随机的端口号
        port = random.randint(1024, 65535)

        # 生成在tmp下的文件，文件名为flow_时间戳, 时间戳转换为上海时间，且精确到毫秒
        self.log = f'/tmp/flow_{time.strftime(f"%Y%m%d_%H%M%S_{port}", time.localtime())}.log'

        c_iperf_cmd = f'nohup iperf3 -c {self.s_device.ip} -u -B {self.c_device.ip} -l {self.packet_size} -i {self.interval} -t {self.duration} -p {port} > {self.log} 2>&1 &'
        s_iperf_cmd = f'nohup iperf3 -s -u -B {self.s_device.ip} -l {self.packet_size} -i {self.interval} -t {self.duration} -p {port} > {self.log} 2>&1 &'

        c_server = self.c_device.get_server()
        s_server = self.s_device.get_server()


        s_server.run_cmd(s_iperf_cmd)
        time.sleep(2)
        c_server.run_cmd(c_iperf_cmd)

        time.sleep(self.duration + 1)



    def parse_result(self):
        pass

class Flows:
    def __init__(self):
        self.flows = []

    def add_flow(self, flow):
        self.flows.append(flow)

    def start(self):
        threads = []
        for flow in self.flows:
            thread = threading.Thread(target=flow.start)
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()