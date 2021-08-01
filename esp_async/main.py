import uasyncio as asyncio
import time

from systems import SystemsData
from settings import SettingsFile


# control task
from presenter import proc_presenter

# input task
from sw import proc_sw
from renc import proc_renc

# output task
from dsp import proc_dsp
from led import proc_led
# from httpc import proc_httpc
# from httpd import proc_httpd

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
        asyncio.run(proc_client())

    time.sleep(3)
    oled_ctl.dsp_clear()

    while True:
        time.sleep(10)
    return

def proc_server():
    from httpd import HttpdProc
    httpd_proc = HttpdProc()
    httpd_proc.run()
    return

async def proc_client():

    from httpc import proc_httpc

    # que : presenter -> task
    que_pre2led = []
    que_pre2httpc = []
    que_pre2dsp = []

    # que : task -> presenter
    que_sw2pre = []
    que_renc2pre = []
    que_httpc2pre = []

    # output tasks
    asyncio.create_task(proc_led(snd_q=None, rcv_q=que_pre2led))
    asyncio.create_task(proc_httpc(snd_q=que_httpc2pre, rcv_q=que_pre2httpc))
    asyncio.create_task(proc_dsp(snd_q=None, rcv_q=que_pre2dsp))

    # input tasks
    asyncio.create_task(proc_sw(snd_q=que_sw2pre, rcv_q=None))
    asyncio.create_task(proc_renc(snd_q=que_renc2pre, rcv_q=None))

    # control tasks
    que_snds = {
        "led" : que_pre2led,
        "httpc" : que_pre2httpc,
        "dsp" : que_pre2dsp,
    }
    que_rcvs = {
        "sw" : que_sw2pre,
        "renc" : que_renc2pre,
        "httpc" : que_httpc2pre,
    }

    que_pre_sw = []
    asyncio.create_task(proc_presenter(que_snds, que_rcvs))

    while True:
        await asyncio.sleep_ms(10_000)
    return



if __name__ == "__main__":
    main()


