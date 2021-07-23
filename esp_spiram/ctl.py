import _thread
from usocket import socket, AF_INET, SOCK_DGRAM
import ujson as json

from util import CommSnd
from util import HOST
from util import ADDR
from util import PORT_DST_CTL
from util import PORT_DST_DSP
from util import PORT_DST_HTTPC


RCV_BUF_SIZE = 128


class CtlProc():
    
    def __init__(self):
        self._cs_dsp = CommSnd(ADDR, PORT_DST_DSP)
        self._cs_httpc = CommSnd(ADDR, PORT_DST_HTTPC)
        return


    def _act_cmd(self, d):
        # print('_act_cmd - run')

        if False == ('cmd' in d):
            return False

        if 'sw' in d['cmd']:
            self._act_cmd_sw(d['type'], d['how'])
            return True
        
        if 're' in d['cmd']:
            self._act_cmd_re(d['type'], d['pos'])
            return True
        
        # print('_act_cmd - over')
        return False


    def _act_cmd_sw(self, code, how):
        # print('_act_cmd_sw - run')
        # create - ['no1', 'no2', ..., 'no10']
        parse_no = ["no" + str(x) for x in range(1, 11, 1)] 
        for no in parse_no:
            if no in code:
                self._cs_httpc.sendto_dict({'cmd': "httpc", 'type':no, 'how':how})
                break
        # print('_act_cmd_sw - over')
        return


    def _act_cmd_re(self, code, pos):
        # print('_act_cmd_re - run')
        self._cs_dsp.sendto_dict({'cmd': "dsp", 'type':'re', 'pos':pos, 'tmr':'3000'})
        # print('_act_cmd_re - over')
        return


    def _proc_ctl(self):
        s = socket(AF_INET, SOCK_DGRAM)
        s.bind((HOST, PORT_DST_CTL))

        while True:
            msg, address = s.recvfrom(RCV_BUF_SIZE)
            d = json.loads(msg.decode())
            # print(d)
            self._act_cmd(d)

        s.close()


    def run(self):
        _thread.start_new_thread(self._proc_ctl, ())
