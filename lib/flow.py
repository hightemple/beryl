import random
import threading
import time
from lib.beryl import NetDev


# 设计思路：
# 1. flow可以绑定pf，也可以绑定到vf
# 2. flow可以绑定到多个pf，也可以绑定到多个vf
# 3. flow使用iperf3进行测试
# 4. flow可以根据pf或vf对象所包含的信息来给出iperf3的命令

# 创建一对一的流，流的数量默认为1


class FlowParams:
    def __init__(self, packet_size=64, duration=2, interval=1, port=None):
        self.packet_size = packet_size
        self.duration = duration
        self.port = port
        self.interval = interval


class PingFlowParams(FlowParams):
    def __init__(self, packet_size=64, duration=3, interval=1, port=None):
        super().__init__(packet_size=packet_size, duration=duration, interval=interval, port=port)

        # Add specific parameters for PingFlow here


class IperfFlowParams(FlowParams):
    def __init__(self, packet_size=64, duration=3, interval=1, port=None, type='udp'):
        super().__init__(packet_size=packet_size, duration=duration, interval=interval, port=port)
        self.type = type


class RDMAFlowParams(FlowParams):
    def __init__(self):
        super().__init__()
        # Add specific parameters for RDMAFlow here


class Flow:
    def __init__(self, c_device: NetDev, s_device: NetDev, port=None):
        self.c_device = c_device
        self.s_device = s_device
        self.log = None
        self.port = port

    def set_port(self, port):
        self.port = port

    def start(self):
        pass

    def parse_result(self):
        pass


class PingFlow(Flow):
    def __init__(self, c_device, s_device, flow_params: PingFlowParams):
        super().__init__(c_device, s_device)
        self.params = flow_params

    def start(self):
        # 生成一个随机的端口号
        if self.port is None:
            port = random.randint(1024, 65535)
        else:
            port = self.port

        # 生成在tmp下的文件，文件名为flow_时间戳, 时间戳转换为上海时间，且精确到毫秒
        self.log = f'/tmp/flow_{time.strftime(f"%Y%m%d_%H%M%S_{port}", time.localtime())}.log'

        c_iperf_cmd = f'nohup ping {self.s_device.ip} -i {self.params.interval} -s {self.params.packet_size} -c {int(self.params.duration / self.params.interval)}  > {self.log} 2>&1 &'
        # -1, --one-off             handle one client connection then exit
        s_iperf_cmd = f'nohup ping {self.c_device.ip} -i {self.params.interval} -s {self.params.packet_size} -c {int(self.params.duration / self.params.interval)}  > {self.log} 2>&1 &'

        c_server = self.c_device.get_server()
        s_server = self.s_device.get_server()

        s_server.run_cmd(s_iperf_cmd)
        c_server.run_cmd(c_iperf_cmd)

        time.sleep(self.params.duration + 1)

    def parse_result(self):
        pass


class IperfFlow(Flow):
    def __init__(self, c_device, s_device, flow_params: IperfFlowParams, port=None, type='udp'):
        super().__init__(c_device, s_device, port)
        self.params = flow_params
        self.type = type

    def start(self):

        # 生成一个随机的端口号
        if self.port is None:
            port = random.randint(1024, 65535)
        else:
            port = self.port

        # 生成在tmp下的文件，文件名为flow_时间戳, 时间戳转换为上海时间，且精确到毫秒
        self.log = f'/tmp/flow_{time.strftime(f"%Y%m%d_%H%M%S_{port}", time.localtime())}.log'



        c_iperf_cmd = f'nohup iperf3 -c {self.s_device.ip} -u -B {self.c_device.ip} -l {self.params.packet_size} -i {self.params.interval} -t {self.params.duration} -p {port}  > {self.log} 2>&1 &'
        # -1, --one-off             handle one client connection then exit
        s_iperf_cmd = f'nohup iperf3 -s -u -B {self.s_device.ip} -l {self.params.packet_size} -i {self.params.interval} -t {self.params.duration} -p {port}  -1 > {self.log} 2>&1 &'




        c_server = self.c_device.get_server()
        s_server = self.s_device.get_server()

        s_server.run_cmd(s_iperf_cmd)
        time.sleep(2)
        c_server.run_cmd(c_iperf_cmd)

        time.sleep(self.params.duration + 1)

    def parse_result(self):
        pass


class PerftestFlow(Flow):
    def start(self):
        pass  # Implement the logic for starting a PerftestFlow

    def parse_result(self):
        pass


class Flows:
    def __init__(self):
        self.flows = []

    def __iter__(self):
        return iter(self.flows)  # 返回迭代器，用于迭代flows列表

    def add_flow(self, flow):
        self.flows.append(flow)

    def start(self, parallel=True):
        if parallel:
            threads = []
            for flow in self.flows:
                thread = threading.Thread(target=flow.start)
                threads.append(thread)
                thread.start()

            for thread in threads:
                thread.join()
        else:
            for flow in self.flows:
                flow.start()

    def parse_result(self):
        for flow in self.flows:
            flow.parse_result()


def create_p2p_flows(c_device, s_device, flow_params: FlowParams, flow_num=1):
    """
    Create point-to-point flows between a client device and a server device.

    Args:
        c_device: Client device.
        s_device: Server device.
        flow_params (FlowParams): Parameters for flow creation.
        flow_num (int): Number of flows to create.

    Returns:
        Flows: Created flows.
    """
    flows = Flows()

    supported_flow_types = (PingFlowParams, IperfFlowParams)
    if not isinstance(flow_params, supported_flow_types):
        raise TypeError(f'{type(flow_params)} is not supported')

    flow_class = PingFlow if isinstance(flow_params, PingFlowParams) else IperfFlow

    for i in range(flow_num):
        flows.add_flow(flow_class(c_device, s_device, flow_params))

    for i, flow in enumerate(flows):
        flow.set_port(10000 + i)

    return flows



# 创建多对多的流，每个设备对之间的流的数量默认为1
def create_m2m_flows(c_devices, s_devices, flow_params: FlowParams, flow_num=1):
    """
    Create multiple flows between client devices and server devices.

    Args:
        c_devices (list): List of client devices.
        s_devices (list): List of server devices.
        flow_params (FlowParams): Parameters for flow creation.
        flow_num (int): Number of flows to create for each device pair.

    Returns:
        Flows: Created flows.
    """
    flows = Flows()

    supported_flow_types = (PingFlowParams, IperfFlowParams)
    if not isinstance(flow_params, supported_flow_types):
        raise TypeError(f'{type(flow_params)} is not supported')

    for c_device, s_device in zip(c_devices, s_devices):
        for i in range(flow_num):
            if isinstance(flow_params, PingFlowParams):
                flows.add_flow(PingFlow(c_device, s_device, flow_params))
            elif isinstance(flow_params, IperfFlowParams):
                flows.add_flow(IperfFlow(c_device, s_device, flow_params))

    # Set port numbers for each flow
    for i, flow in enumerate(flows):
        flow.set_port(10000 + i)

    return flows
