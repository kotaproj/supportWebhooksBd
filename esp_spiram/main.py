import _thread
import time

# system data
from systems import SystemsData
from settings import SettingsFile

# control task
from presenter import PreProc

# input task
from sw import SwProc
from renc import ReProc

# output task
from dsp import DspProc
from led import LedProc
# from httpc import HttpcProc
# from httpd import HttpdProc

# initial
from dsp import OledCtl
from led import LedCtl


def main():
    # initial
    led_ctl = LedCtl()
    led_ctl.on_all()
    systems_data = SystemsData()

    mode = systems_data.get_system_mode()

    print(mode)

    oled_ctl = OledCtl()
    oled_ctl.dsp_power(mode)

    time.sleep(0.5)

    if "server" == mode:
        proc_server()
    else:
        proc_client()

    while True:
        time.sleep(10)
    return

def proc_server():
    from httpd import HttpdProc
    httpd_proc = HttpdProc()
    httpd_proc.run()


def proc_client():

    # thread lock
    lock = _thread.allocate_lock()

    # input task
    que_sw2pre = []
    sw_proc = SwProc(lock, snd_que=que_sw2pre)
    sw_proc.run()

    que_re2pre = []
    re_proc = ReProc(lock, snd_que=que_re2pre)
    re_proc.run()

    # output task
    que_pre2led = []
    led_proc = LedProc(lock, rcv_que=que_pre2led)
    led_proc.run()

    que_pre2dsp = []
    dsp_proc = DspProc(lock, rcv_que=que_pre2dsp)
    dsp_proc.run()

    from httpc import HttpcProc
    que_httpc2pre = []
    que_pre2httpc = []
    httpc_proc = HttpcProc(lock, snd_que=que_httpc2pre, rcv_que=que_pre2httpc)
    httpc_proc.run()

    # presenter
    que_snds = {
        "led" : que_pre2led,
        "httpc" : que_pre2httpc,
        "dsp" : que_pre2dsp,
    }
    que_rcvs = {
        "sw" : que_sw2pre,
        "re" : que_re2pre,
        "httpc" : que_httpc2pre,
    }
    pre_proc = PreProc(lock, que_snds, que_rcvs)
    pre_proc.run()
    return

if __name__ == "__main__":
    main()
