import math
import re
import threading
import time


TAG = {
    'ib_device': '-d',
    'gid_index': '-x',
    'post_list_size': '-l',
    'mtu': '-m',
    'qp_num': '-q',
    'package_len': '-s',
    'package_num': '-n',
    'tx_depth': '-t',
    'port': '-p',
    'duration': '-D',

    'service_level': '-S',
    'tos': '-R -T',
    'connection': '-c',
    'qp_timeout': '-u',
    'retry_count': '--retry_count=',
    't_class': '--tclass=',
    'cq_mod': '-Q'
}

# WRITE_TAG 在 TAG上新增了rx_depth
WRITE_TAG = TAG.copy()
WRITE_TAG['rx_depth'] = '-r'
WRITE_TAG['inline_size'] = '-I'

READ_TAG = TAG.copy()

SEND_TAG = TAG.copy()
SEND_TAG['inline_size'] = '-I'
SEND_TAG['rx_depth'] = '-r'

class RDMAOperate:
    def retrieve_queue_info(self, result_queue):
        while not result_queue.empty():
            result, msg = result_queue.get()
            # print('----{} {}----'.format(result,msg))
            assert result, msg

    def start_server_client(self,ib_server, ib_client):
        ib_server.start()
        time.sleep(5)
        ib_client.start()
    def start_and_run(self, ib_server, ib_client):
        self.start_server_client(ib_server, ib_client)
        time.sleep(3)

        print("Waiting for client and server to finish...")
        ib_server.join()
        ib_client.join()


    def check_switch_counter(self, count, package_len, package_num, qp_num=1, direction='uni',mtu=4096, **kwargs):
        if direction == "uni":
            coefficient = 1
        else:
            coefficient = 2

        if package_len <= mtu:
            expect_pkg_num = package_num * coefficient * qp_num
        else:
            expect_pkg_num = package_num * math.ceil(package_len / mtu) * coefficient * qp_num

        # if kwargs have operate
        operate = kwargs.get('operate', None)
        if operate == 'send':

            expect_pkg_num_max = max(int(expect_pkg_num * 1.5), expect_pkg_num + 100)
            print("[CHK.Switch] Switch counter({}) should be between {} ~ {}.".format(count, expect_pkg_num,
                                                                                         expect_pkg_num_max, direction))
            assert expect_pkg_num <= count <= expect_pkg_num_max, \
                "The counter({}) is not between {} ~ {} on {}-direction for this test".format(count, expect_pkg_num,
                                                                                              expect_pkg_num_max, direction)
        else:
            expect_pkg_num_max = max(int(expect_pkg_num * 1.1), expect_pkg_num + 100)
            print("[CHK.Switch] Switch counter({}) should be between {} ~ {}.".format(count, expect_pkg_num,
                                                                                         expect_pkg_num_max, direction))
            assert expect_pkg_num <= count <= expect_pkg_num_max, \
                "The counter({}) is not between {} ~ {} on {}-direction for this test".format(count, expect_pkg_num,
                                                                                              expect_pkg_num_max,
                                                                                              direction)

            # print("[CHK.Switch] Switch counter is {}, expect package number is {}.".format(count, expect_pkg_num))
            # assert count == expect_pkg_num, \
            #     "The counter({}) is not equal to send package {} on {}-direction for this test".format(count, expect_pkg_num,
            #                                                                                   direction)

    def check_bw(self, bw_s, bw_c, server, client, is_bidirectional, log_file, coefficient=0.2):
        _, _, _, bw_cur_c, _ = self.get_perf_data(client, log_file)
        if is_bidirectional:
            _, _, _, bw_cur_s, _ = self.get_perf_data(server, log_file)
            print("[CHK]{}:BW is {} MB/s, expected bw is {} ~ {} MB/s".format(server.host, bw_cur_s,
                                                                                 round(bw_s * (1 - coefficient),2),
                                                                                 round(bw_s * (1 + coefficient),2)))
            assert abs(bw_cur_s - bw_s) < bw_s * coefficient, "BW is not as expected for {}".format(server.host)
        print("[CHK]{}:BW is {} MB/s, expected bw is {} ~ {} MB/s".format(client.host, bw_cur_c,
                                                                             round(bw_c * (1 - coefficient), 2),
                                                                             round(bw_c * (1 + coefficient), 2)))
        assert abs(bw_cur_c - bw_c) < bw_c * coefficient, "BW is not as expected for {}".format(client.host)

    def get_perf_data(self, client, log_file):
        str_out = client.run_cmd("tail -n 3 {}".format(log_file))
        # str_out 是一个list，将该list转换为str
        print("Current ib_write_bw performance: {}".format(str_out))
        str_out = ''.join(str_out)
        pattern = r"(\d+)\s+(\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)"
        matchs = re.findall(pattern, str_out, re.M)

        data = matchs[-1]
        bytes = data[0]
        iterations = data[1]
        bw_peak = data[2]
        bw_average = data[3]
        msgrate = data[4]
        print("bytes: {}, iterations: {}, bw_peak: {}, bw_average: {},"
                  " msgrate: {}".format(bytes, iterations, bw_peak, bw_average, msgrate))
        return int(bytes), int(iterations), float(bw_peak), float(bw_average), float(msgrate)

class IBCmd:
    def __init__(self, client, **kwargs):
        self.client = client
        self.params = self.get_params(**kwargs)
    #   如果kwargs中有result_queue参数，将结果放入result_queue中
        self.result_queue = kwargs.get('result_queue', None)



    def pprint(self, msg):
        for line in msg:
            print(line)
    def setup_common_command_line_options(self, cmd, tags, **kwargs):
        # 判断kwargs中有host参数
        if 'host' in kwargs:
            cmd += " {}".format(kwargs['host'])
        # 判断kwargs中是否有run_infinitely参数
        if self.params['run_infinitely']:
            cmd += " --run_infinitely"
        if self.params['bidirectional']:
            cmd += " -b"
        if self.params['rdma_cm']:
            cmd += " -R"
        if self.params['ipv6']:
            cmd += " --ipv6"
        if self.params['event']:
            cmd += " -e"
        if self.params['all']:
            cmd += " -a"
        if self.params['t_class'] == 12:
            cmd += " --tclass=12"

        log_file = kwargs.get('log_file', '/tmp/ib.log')

        CARD_TYPE = self.client.nic.lower()
        if 'mlx' in CARD_TYPE:
            keys = ['gid_index']
        else:
            keys = ['ib_device', 'gid_index']
        # 从 kwargs中获取key加入到keys中
        keys.extend([key for key in kwargs.keys() if key in tags.keys()])
        # 保证keys中的key是唯一的
        keys = list(set(keys))
        for key in keys:
            if '=' in tags[key]:
                cmd = cmd + " {}{}".format(tags[key], self.params[key])
            else:
                cmd = cmd + " {} {}".format(tags[key], self.params[key])
        if self.params['run_infinitely']:
            cmd = '{}  | tee  {} '.format(cmd, log_file)
        cmd = f"{cmd} -N"
        return cmd


    def get_params(self, **kwargs) -> dict:
        params = {}
        # params['host'] = kwargs.get('host', None)
        params['package_num'] = kwargs.get('package_num', 50000)
        params['ib_device'] = kwargs.get('ib_device', 'xscale_0')
        params['gid_index'] = kwargs.get('gid_index', 5)
        params['post_list_size'] = kwargs.get('post_list_size', 10)
        params['mtu'] = kwargs.get('mtu', 4096)
        params['qp_num'] = kwargs.get('qp_num', 1)
        params['rx_depth'] = kwargs.get('rx_depth', 128)
        params['tx_depth'] = kwargs.get('tx_depth', 128)
        params['package_len'] = kwargs.get('package_len', 65536)
        params['run_infinitely'] = kwargs.get('run_infinitely', False)
        params['bidirectional'] = kwargs.get('bidirectional', False)
        params['inline_size'] = kwargs.get('inline_size', 0)
        params['port'] = kwargs.get('port', 9999)
        params['duration'] = kwargs.get('duration', 10)

        params['rdma_cm'] = kwargs.get('rdma_cm', False)
        params['service_level'] = kwargs.get('service_level', 0)
        params['ipv6'] = kwargs.get('ipv6', False)
        params['tos'] = kwargs.get('tos', None)
        params['event'] = kwargs.get('event', False)
        params['all'] = kwargs.get('all', False)
        params['t_class'] = kwargs.get('t_class', 12)
        params['cq_mod'] = kwargs.get('cq_mod', 2)

        return params

    def check_result(self, msg, package_len, package_num):
        # 如果msg是一个列表，将该列表合并位为一个字符串
        errMsg = ""
        if isinstance(msg, list):
            msg = ''.join(msg)

        if str(package_len) not in msg:
            errMsg += "\nERR: Not found package len {} from cmd returned message!\n".format(package_len)
        if str(package_num) not in msg:
            errMsg += "ERR: Not found package number {} from cmd returned message!\n".format(package_num)
        if len(errMsg) > 0:
            if self.result_queue:
                self.result_queue.put((False, errMsg))
            return False, errMsg
        else:
            return True, "Success"

    def check_cmd_msg(self, out):

        if not self.params['run_infinitely']:
            self.pprint(out)
            success, errMsg = self.check_result(out, self.params['package_len'],
                                                self.params['package_num'] * self.params['qp_num'])

            if success:
                print("[CHK] Success! Get correct msg from {}!\n".format(self.client.host))
            else:
                print("\n[CHK] Failed! Not get correct msg from {}! {}".format(self.client.host,errMsg))



class IBWrite(IBCmd):
    def __init__(self, client, **kwargs):
        super().__init__(client, **kwargs)
        self._cmd = "ib_write_bw"
        self._cmd = self.setup_common_command_line_options(self._cmd, WRITE_TAG, **kwargs)




class IBWriteServer(threading.Thread, IBWrite):
    def __init__(self, client, **kwargs):
        super().__init__()
        IBWrite.__init__(self, client, **kwargs)


    def run(self):
        print("\n" * 3)
        print("="*100)
        print("server : {}".format(self._cmd))

        out = self.client.run_cmd(self._cmd, timeout=600)
        self.check_cmd_msg(out)



class IBWriteClient(threading.Thread, IBWrite):
    def __init__(self, client, **kwargs):
        super().__init__()
        IBWrite.__init__(self, client, **kwargs)


    def run(self):
        print("client : {}".format(self._cmd))
        print("=" * 100 + "\n"*3)

        out = self.client.run_cmd(self._cmd, timeout=600)
        self.check_cmd_msg(out)


class IBRead(IBCmd):
    def __init__(self, client, **kwargs):
        super().__init__(client, **kwargs)
        self._cmd = "ib_read_bw"
        self._cmd = self.setup_common_command_line_options(self._cmd,READ_TAG,**kwargs)
        if 'mlx' in client.nic:
            self._cmd += ' -o 1'



class IBReadServer(threading.Thread, IBRead):
    def __init__(self, client, **kwargs):
        super().__init__()
        IBRead.__init__(self, client, **kwargs)


    def run(self):
        print("\n" * 3)
        print("=" * 100)
        print("server : {}".format(self._cmd))

        out = self.client.run_cmd(self._cmd, timeout=600)
        self.check_cmd_msg(out)




class IBReadClient(threading.Thread, IBRead):
    def __init__(self, client ,**kwargs):
        super().__init__()
        IBRead.__init__(self, client, **kwargs)

    def run(self):
        print("client : {}".format(self._cmd))
        print("=" * 100 + "\n"*3)

        out = self.client.run_cmd(self._cmd, timeout=600)
        self.check_cmd_msg(out)


class IBSend(IBCmd):
    def __init__(self, client, **kwargs):
        super().__init__(client, **kwargs)
        self._cmd = "ib_send_bw"

        self._cmd = self.setup_common_command_line_options(self._cmd,SEND_TAG, **kwargs)


class IBSendServer(threading.Thread, IBSend):
    def __init__(self, client, **kwargs):
        super().__init__()
        IBSend.__init__(self, client, **kwargs)


    def run(self):
        print("\n" * 3)
        print("=" * 100)
        print("server : {}".format(self._cmd))

        out = self.client.run_cmd(self._cmd, timeout=600)
        self.check_cmd_msg(out)



class IBSendClient(threading.Thread, IBSend):
    def __init__(self, client, **kwargs):
        super().__init__()
        IBSend.__init__(self, client, **kwargs)


    def run(self):
        print("client : {}".format(self._cmd))
        print("=" * 100 + "\n"*3)

        out = self.client.run_cmd(self._cmd, timeout=600)
        self.check_cmd_msg(out)