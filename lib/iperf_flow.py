import threading
import time



import random


IPERF3_COMMON_TAG = {
    'port': '-p',
    'format': '-f',
    'interval': '-i',
    'pidfile': '-I',
    'file': '-F',
    'affinity': '-A',
    'bind-ip': '-B',
    'bind-dev': '--bind-dev',
    'verbose': '-V',
    'json': '-J',
    'logfile': '--logfile',
    'forceflush': '--forceflush',
    'timestamps': '--timestamps',
    'rcv_timeout': '--rcv-timeout',
    'snd_timeout': '--snd--timeout',
    'debug': '-d',
    'version': '-v',
    'help': '-h'
}
IPERF3_SERVER_SPEC_TAG = {
    'server': '-s',
    'daemon': '-D',
    'one_off': '-1',
    'server_bitrate_limit': '--server-bitrate-limit',
    'idle_timeout': '--idle-timeout'
}
IPERF3_CLIENT_SPEC_TAG = {
    'client': '-c',
    'udp': '-u',
    'connect_timeout': '--connect-timeout',
    'bitrate': '-b',
    'pacing_timer': '--pacing-timer',
    'fq_rate': '--fq-rate',
    'time': '-t',
    'bytes': '-n',
    'blockcount': '-k',
    'length': '-l',
    'cport': '--cport',
    'parallel': '-P',
    'reverse': '-R',
    'bidir': '--bidir',
    'window': '-w',
    'congestion': '-C',
    'set-mss': '-M',
    'no_delay': '-N',
    'version4': '-4',
    'version6': '-6',
    'tos_N': '-S',
    'dscp_val': '--dscp',
    'flowlabel': '-L',
    'zerocopy': '-Z',
    'omit_N': '-O',
    'title str': '-T',
    'extra_data_str': '--extra-data str',
    'get_server_output': '--get-server-output',
    'udp_counters_64bit': '--udp-counters-64bit',
    'repeating_payload': '--repeating-payload',
    'dont_fragment': '--dont-fragment'
}

IPERF3_SERVER_TAG = IPERF3_COMMON_TAG.copy()
IPERF3_SERVER_TAG.update(IPERF3_SERVER_SPEC_TAG)
IPERF3_CLIENT_TAG = IPERF3_COMMON_TAG.copy()
IPERF3_CLIENT_TAG.update(IPERF3_CLIENT_SPEC_TAG)


def check_iperf_result(output, **args):
    flag = False
    msg = "Transfer is not meet expectations"
    # print("*" * 100)
    # print("-" * 40 + "check_iperf_result" + "-" * 40)
    # for line in output:
    #     print(line)
    # print("*" * 100)

    # 当前只做丢包检查，
    for line in output:
        line_list = line.split()
        if len(line_list) > 5:
            if ".00-" in line_list[2]:
                if int(float(line_list[6])) > 0:
                    flag = True
                    msg = line
                else:
                    return False, line
    return flag, msg


class FlowOperate:
    def retrieve_queue_info(self, result_queue):
        while not result_queue.empty():
            result, msg = result_queue.get()
            print(result)
            print(msg)
            assert result, msg

    def start_server_client(self, server, client):
        if server is not None:
            server.start()
        time.sleep(20)
        if client is not None:
            client.start()

    def start_and_run(self, server, client):
        self.start_server_client(server, client)
        time.sleep(3)

        print("Waiting for client and server to finish...")
        if client is not None:
            client.join()

    def valid_port_get(self, server, client):
        print("get a valid port")
        port = 0
        while port == 0:
            port = random.randint(35000, 40000)
            cmd = "netstat -ntulp | grep {}".format(port)
            server_output = server.run_cmd(cmd)
            client_output = client.run_cmd(cmd)
            if len(server_output) != 0 or len(client_output) != 0:
                port = 0
        print("valid port is {}".format(port))
        return port


class Iperf3Cmd:
    def __init__(self, client, **kwargs):
        self.client = client
        self.params = self.get_params(**kwargs)
        #   如果kwargs中有result_queue参数，将结果放入result_queue中
        self.result_queue = kwargs.get('result_queue', None)
        self.port = kwargs.get('port', None)
        self.interval = kwargs.get('interval', 1)
        self.time = kwargs.get('time', 30)

    def setup_common_command_line_options(self, cmd, **kwargs):
        print("set common command line")
        tags = []
        keys = []
        if 'udp' in kwargs:
            cmd += " {}".format("-u")
        if 'iperf3_server' in kwargs:
            cmd += " {}".format("-s")
            tags = IPERF3_SERVER_TAG.copy()
        if 'iperf3_client' in kwargs:
            cmd += " {}".format("-c")
            tags = IPERF3_CLIENT_TAG.copy()
        if 'host_ip' in kwargs:
            cmd += " {}".format(kwargs['host_ip'])

        #从kwargs中获取key加入到keys中
        for key in kwargs.keys():
            if key == 'server' or key == 'client' or key == 'udp':
                continue
            if key in tags.keys():
                keys.append(key)
        #保证keys中的key是唯一的
        cmd_keys = list(set(keys))
        cmd_keys.sort(key = keys.index)

        for key in cmd_keys:
            cmd = cmd + " {} {}".format(tags[key], self.params[key])
        print("cmd: {}".format(cmd))

        return cmd

    def get_params(self, **kwargs) -> dict:
        params = {}
        params['host_ip'] = kwargs.get('host_ip', None)
        params['port'] = kwargs.get('port', 17701)
        params['interval'] = kwargs.get('interval', 1)
        params['length'] = kwargs.get('length', 64)
        params['time'] = kwargs.get('time', 30)
        params['bitrate'] = kwargs.get('bitrate', '25g')
        return params

    def performance_test_iperf3_kill(self, client1, client2):
        print("kill iperf3 process")
        iperf3_kill = "pkill iperf"
        client1.run_cmd(iperf3_kill)
        client2.run_cmd(iperf3_kill)
        time.sleep(3)


class Iperf3Write(Iperf3Cmd):
    def __init__(self, client, **kwargs):
        super().__init__(client, **kwargs)
        self._cmd = "iperf3"
        self._cmd = self.setup_common_command_line_options(self._cmd, **kwargs)


class Iperf3Server(threading.Thread, Iperf3Write, FlowOperate):
    def __init__(self, client, **kwargs):
        super().__init__()
        Iperf3Write.__init__(self, client, **kwargs)

    def run(self):
        print("\n")
        print("=" * 100)
        # print("server {}: {}".format(self.client.ip, self._cmd))

        out = self.client.run_cmd(self._cmd, (self.time + 60))
        # 检查返回结果
        if "xsc" in self.client.nic:
            self.result_queue.put((check_iperf_result(out)))


class Iperf3Client(threading.Thread, Iperf3Write, FlowOperate):
    def __init__(self, client, **kwargs):
        super().__init__()
        Iperf3Write.__init__(self, client, **kwargs)

    def run(self):
        # print("client {}: {}".format(self.client.ip, self._cmd))
        # print("=" * 100 + "\n")

        out = self.client.run_cmd(self._cmd, (self.time + 60))
        # 检查返回结果
        self.result_queue.put((check_iperf_result(out)))











