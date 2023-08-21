import threading

PING_TAG = {
    'count': '-c',
    'interval': '-i',
    'interface': '-I',
    'mark': '-m',
    'pmtudisc_option': '-M',
    'preload': '-l',
    'pattern': '-p',
    'tos': '-Q',
    'packetsize': '-s',
    'sndbuf': '-S',
    'ttl': '-t',
    'timestamp_option': '-T',
    'deadline': '-w',
    'timeout': '-W',
    'flood_ping': '-f'
}
PING6_TAG = {
    'count': '-c',
    'interval': '-i',
    'interface': '-I',
    'preload': '-l',
    'pmtudisc_option': '-M',
    'nodeinfo_option': '-N',
    'pattern': '-p',
    'tclass': '-Q',
    'packetsize': '-s',
    'sndbuf': '-S',
    'ttl': '-t',
    'timestamp_option': '-T',
    'deadline': '-w',
    'timeout': '-W',
    'flood_ping': '-f'
}

class PingCmd:
    def __init__(self, client, **kwargs):
        self.client = client
        self.params = self.get_params(**kwargs)
        #   如果kwargs中有result_queue参数，将结果放入result_queue中
        self.result_queue = kwargs.get('result_queue', None)

    def setup_common_command_line_options(self, cmd, tags, **kwargs):
        print("set common command line")
        if 'ipv6' in kwargs:
            cmd += " {}".format("6")
        if 'host_ip' in kwargs:
            cmd += " {}".format(kwargs['host_ip'])
        if 'flood_ping' in kwargs:
            cmd += " {}".format("-f")

        keys = []
        #从kwargs中获取key加入到keys中
        keys.extend([key for key in kwargs.keys() if key in tags.key()])
        #保证keys中的key是唯一的
        keys = list(set(keys))
        for key in keys:
            cmd = cmd + " {} {}".format(tags[key], self.params[key])
        print("cmd:".format(cmd))

        return cmd

    #先做预留
    def get_params(self, **kwargs) -> dict:
        params = {}
        params['interval'] = kwargs.get('interval', '0.01')
        params['count'] = kwargs.get('time', 100)
        return params

'''
class PingWrite(Iperf3Cmd):
    def __init__(self, client, **kwargs):
        super().__init(client, **kwargs)
        self._cmd = "ping"
        self._cmd = self.setup_common_command_line_options(self._cmd, PING_TAG, **kwargs)


class PingClient(threading.Thread, PingWrite):
    def __init__(self, client, **kwargs):
        super().__init__()
        PingWrite.__init__(self, client, **kwargs)

    def run(self):
        print("\n")
        print("=" * 100)
        print("server : {}".format(self._cmd))

        out = self.clent.run_cmd(self._cmd, timeout=1200)
        check_iperf_result(out, self.result_queue)

'''



