import random
import time


# 设计思路：
# 1. flow可以绑定pf，也可以绑定到vf
# 2. flow可以绑定到多个pf，也可以绑定到多个vf
# 3. flow使用iperf3进行测试
# 4. flow可以根据pf或vf对象所包含的信息来给出iperf3的命令

def create_flow(c_device, s_device):
    flow = Flow(c_device, s_device)
    return flow

class Flow:
    def __init__(self, packet_size, interval=1, type='udp', duration=10, c_device=None, s_device=None):
        self.packet_size = packet_size

        self.interval = interval
        self.type = type
        self.duration = duration
        self.c_device = c_device
        self.s_device = s_device

    def start(self):
        # 生成一个随机的端口号
        port = random.randint(1024, 65535)
        # 如果 self.c_device 是 PF 对象，则使用 PF 对象的信息来构造iperf3命令

        c_iperf_cmd = f'iperf3 -c {self.s_device.ip} -u -B {self.c_device.ip} -l {self.packet_size} -i {self.interval} -t {self.duration} -p {port}'
        s_iperf_cmd = f'iperf3 -s -u -B {self.s_device.ip} -l {self.packet_size} -i {self.interval} -t {self.duration} -p {port}'

        c_server = self.c_device.get_server()
        s_server = self.s_device.get_server()


        s_server.run_cmd(s_iperf_cmd)
        time.sleep(1)
        c_server.run_cmd(c_iperf_cmd)



    def parse_result(self):
        pass