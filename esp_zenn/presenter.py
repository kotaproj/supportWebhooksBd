import _thread
import time

from util import *

class PreProc():
    
    def __init__(self, lock=None, snd_ques=None, rcv_ques=None):

        self._lock = lock
        self._snd_ques = snd_ques
        self._rcv_ques = rcv_ques
        return


    def _command_sw(self, msg):
        print("pre_command_sw:run")
        d = conv_msg2dict(msg)
        print(d)
        send_que(self._lock, self._snd_ques["httpc"], ("dst:httpc,src:pre,cmd:sw,type:"+d["type"]+",how:"+d["how"]))
        return

    def _command_dsp(self, msg):
        print("pre_command_dsp:run")
        msg = msg.replace("dst:pre,src:httpc,", "dst:dsp,src:pre,")
        send_que(self._lock, self._snd_ques["dsp"], msg)
        print("pre_command_dsp:over")
        return

    def _command_led(self, msg):
        print("pre_command_led:run")
        msg = msg.replace("dst:pre,src:httpc,", "dst:led,src:pre,")
        send_que(self._lock, self._snd_ques["led"], msg)
        print("pre_command_led:over")
        return


    def _proc_pre(self):
        while True:
            # recvive_que
            for key, rcv_q in self._rcv_ques.items():
                msg = recv_que(self._lock, rcv_q)
                if msg is None:
                    # print("IndexError")
                    continue
                print("proc_presenter:msg - ", msg)
                command = conv_msg2dict(msg)['cmd']
                if "sw" == command:
                    self._command_sw(msg)
                elif "dsp" == command:
                    self._command_dsp(msg)
                elif "led" == command:
                    self._command_led(msg)
                else:
                    print("proc_presenter:error - ", msg)
            time.sleep_ms(10)
        return


    def run(self):
        _thread.start_new_thread(self._proc_pre, ())


def main():

    lock = _thread.allocate_lock()

    from sw import SwProc
    que_sw2pre = []
    sw_proc = SwProc(lock, snd_que=que_sw2pre)
    sw_proc.run()

    from led import LedProc
    que_pre2led = []
    led_proc = LedProc(lock, rcv_que=que_pre2led)
    led_proc.run()

    from httpc import HttpcProc
    que_httpc2pre = []
    que_pre2httpc = []
    httpc_proc = HttpcProc(lock, snd_que=que_httpc2pre, rcv_que=que_pre2httpc)
    httpc_proc.run()

    from dsp import DspProc
    que_pre2dsp = []
    dsp_proc = DspProc(lock, rcv_que=que_pre2dsp)
    dsp_proc.run()

    que_snds = {
        "led" : que_pre2led,
        "httpc" : que_pre2httpc,
        "dsp" : que_pre2dsp,
    }
    que_rcvs = {
        "sw" : que_sw2pre,
        "httpc" : que_httpc2pre,
    }

    pre_proc = PreProc(lock, que_snds, que_rcvs)
    pre_proc.run()

    time.sleep(10_000)
    return

if __name__ == "__main__":
    main()
