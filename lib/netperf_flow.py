NETPERF_GLOBAL_TAG = {
    'local_send_recv': '-a',
    'remote_send_recv': '-A',
    'brandstr': '-B',
    'local_cpu_rate': '-c',
    'remote_cpu_rate': '-C',
    'increase_debug': '-d',
    'time': '-D',
    'output-units': '-f',
    'fill': '-F',
    'display': '-h',
    'host_ip': '-H',
    'max-min': '-i',
    'vl': '-I',
    'keep-add-timing-stats': '-j',
    'testlen': '-l',
    'loacl_name_ipaddr': '-L',
    'local_send_recv_offset': '-o',
    'local_send_recv_offset': '-O',
    'numcpu': '-n',
    'no_control_conn': '-N',
    'port': '-p',
    'display_headers': '-P',
    'allow_confidence_hit': '-r',
    'seconds': '-s',
    'keepalive': '-S',
    'test_name': '-t',
    'cpu': '-T',
    'verbosity': '-v',
    'send_recv_buffer': '-W',
    'level': '-v',
    'version': '-V',
    'socket priority': '-y',
    'ip_tos': '-Y',
    'passphrase': '-Z'
}
NETPERF_LOCAL_TAG = {
    'isolate': '--',
    'local_buff_length': '-s',
    'remote_buff_length': '-S',
    'local_group_length': '-m',
    'remote_group_length': '-M',
    'TCP_NODELAY': '-D'
}
NETPERF_TAG = NETPERF_GLOBAL_TAG.copy()
NETPERF_TAG.update(NETPERF_LOCAL_TAG)

NETSERVER_TAG = {
    'no_daemonize': '-D',
    'increase_debug': '-d',
    'run_serially': '-f',
    'name_family': '-L',
    'no_debugout': '-N',
    'port': '-p',
    'ipv4': '-4',
    'ipv6': '-6',
    'verbosity': '-v',
    'passphrase': '-Z'
}


def check_netperf_result(test_type, output, **args):
    num_list = {
        'TCP_STREAM': 7,
        'UDP_STREAM': 7,
        'TCP_CRR': 8
    }

    result_line_num = num_list.get(test_type, None)
    if result_line_num is None:
        print('-----ERROR:test_type is error-----')
    print("+++++++++++++++++check_netperf_result1++++++++++++++++++++++++++++")
    print(output)
    if len(output) < result_line_num:
        return False, "result is error, output:{}".format(output)
    print("+++++++++++++++++check_netperf_result++++++++++++++++++++++++++++")
    for line in output:
        print(line)

    if test_type == 'TCP_STREAM':
        str_list = output[result_line_num - 1].split()
        print(str_list)
        if float(str_list[4]) > 0.01:
            return True, "SUCCESS:{} Throughput(10^6bits/sec) is {}".format(test_type, float(str_list[4]))
        else:
            return False, "False:{} Throughput(10^6bits/sec) is {}".format(test_type, float(str_list[4]))
    elif test_type == 'TCP_CRR':
        str_list = output[result_line_num - 2].split()
        print(str_list)
        if float(str_list[5]) > 0.01:
            return True, "SUCCESS:{} Trans Rate(per sec) is {}".format(test_type, float(str_list[5]))
        else:
            return False, "False:{} Trans Rate(per sec) is {} < ".format(test_type, float(str_list[5]))
    elif test_type == 'UDP_STREAM':
        str_list_local = output[result_line_num - 2].split()
        str_list_remote = output[result_line_num - 1].split()
        print(str_list_local)
        print(str_list_remote)
        if (float(str_list_local[5]) > 0.01) and (
                float(str_list_remote[5]) > 0.01):
            return True, "SUCCESS:{} local and remote Throughput(10^6bits/sec) is {} and {}".format(test_type, float(
                str_list_local[5]), float(str_list_remote[5]))
        else:
            return False, "False:{} local and remote Throughput(10^6bits/sec) is {} and {}".format(test_type, float(
                str_list_local[5]), float(str_list_remote[5]))



class NetperfCmd:
    def __init__(self, client, **kwargs):
        self.client = client
        self.params = self.get_params(**kwargs)
        #  如果kwargs中有result_queue参数，将结果放入result_queue中
        self.result_queue = kwargs.get('result_queue', None)
        self.port = kwargs.get('port', None)
        self.testlen = kwargs.get('testlen', 60)
        self.test_name = kwargs.get('test_name', 'TCP_STREAM')

    def setup_common_command_line_options(self, cmd, **kwargs):
        print("set common command line")
        tags = []
        keys = []

        if 'netperf_server' in kwargs:
            cmd = "{}".format('netserver')
            tags = NETSERVER_TAG.copy()
        if 'netperf_client' in kwargs:
            cmd = "{}".format('netperf')
            tags = NETPERF_TAG.copy()

        # 从kwargs中获取key加入到keys中
        for key in kwargs.keys():
            if key == 'netperf_server' or key == 'netperf_client':
                continue
            if key in tags.keys():
                keys.append(key)
        # 保证keys中的key是唯一的
        cmd_keys = list(set(keys))
        cmd_keys.sort(key=keys.index)

        for key in cmd_keys:
            if key == 'isolate' or key == 'TCP_NODELAY':
                cmd = cmd + " {}".format(tags[key])
            else:
                cmd = cmd + " {} {}".format(tags[key], self.params[key])
        print("cmd: {}".format(cmd))

        return cmd

    def get_params(self, **kwargs) -> dict:
        params = {}
        params['test_name'] = kwargs.get('test_name', 'TCP_STREAM')
        params['host_ip'] = kwargs.get('host_ip', None)
        params['port'] = kwargs.get('port', 17701)
        params['testlen'] = kwargs.get('testlen', 30)
        params['length'] = kwargs.get('length', 64)
        params['local_group_length'] = kwargs.get('local_group_length', 64)
        return params

    def netperf_multi_start_and_run(self, server_list, client_list, result_queue):
        for index in range(len(server_list)):
            netperf_server = server_list[index]
            netperf_server.start()

        time.sleep(5)

        for index in range(len(client_list)):
            netperf_client = client_list[index]
            netperf_client.start()

        print("++++++++++++Wait for client to finish running ++++++++++++++")
        for index in range(len(client_list)):
            client_list[index].join()
        print("!!!!!!!!!!!!The current client have finished !!!!!!!!!!!!!!!")



class NetperfWrite(NetperfCmd):
    def __init__(self, client, **kwargs):
        super().__init__(client, **kwargs)
        self._cmd = ""
        self._cmd = self.setup_common_command_line_options(self._cmd, **kwargs)


class NetperfServer(threading.Thread, NetperfWrite, FlowOperate):
    def __init__(self, client, **kwargs):
        super().__init__()
        NetperfWrite.__init__(self, client, **kwargs)

    def run(self):
        print("\n")
        print("=" * 100)
        # print("server : {}".format(self._cmd))

        out = self.client.run_cmd(self._cmd, (self.testlen + 1200))
        # 检查返回结果
        if "xsc" in self.client.nic:
            self.result_queue.put((check_netperf_result(self.test_name, out)))


class NetperfClient(threading.Thread, NetperfWrite, FlowOperate):
    def __init__(self, client, **kwargs):
        super().__init__()
        NetperfWrite.__init__(self, client, **kwargs)

    def run(self):
        # print("client : {}".format(self._cmd))
        print("=" * 100 + "\n")

        out = self.client.run_cmd(self._cmd, (self.testlen + 1200))
        # 检查返回结果
        self.result_queue.put((check_netperf_result(self.test_name, out)))
