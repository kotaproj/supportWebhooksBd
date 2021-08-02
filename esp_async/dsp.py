import uasyncio as asyncio
import machine
import ssd1306

from util import *
from settings import SettingsFile

# Defines
PIN_SCL = 22
PIN_SDA = 21

TIMER_ID_DSP = 0
oledctl_inited = False

class OledCtl:
    _instance = None

    def __init__(self):
        print("OledCtl - init")
        global oledctl_inited
        if False == oledctl_inited:
            i2c = machine.I2C(scl=machine.Pin(PIN_SCL), sda=machine.Pin(PIN_SDA))
            self._oled = ssd1306.SSD1306_I2C(128, 64, i2c)
            oledctl_inited = True
        return

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)

        return cls._instance


    def dsp_clear(self):
        self._oled.fill(0)
        self._oled.show()
        return

    def dsp_power(self, mode):
        print("dsp:_dsp_power - run")
        if mode == "server":
            from systems import SystemsData
            systems_data = SystemsData()
            self._oled.fill(0)
            self._oled.text('Web Server Mode', 0, 0)
            self._oled.text('SSID:' + systems_data.get_system_AP_SSID(), 0, 10)
            self._oled.text('PASS:' + systems_data.get_system_AP_PASSWORD(), 0, 20)
            self._oled.text('Please Access', 0, 30)
            self._oled.text('http://', 0, 40)
            self._oled.text(systems_data.get_system_AP_IP(), 0, 50)
            self._oled.show()
        elif mode == "client":
            self._oled.fill(0)
            self._oled.text('Booting...', 0, 0)
            self._oled.text('Client Mode', 0, 10)
            self._oled.show()
        elif mode == "done":
            print("dsp:dsp_pwr_done - run")
            self._oled.fill(0)
            self._oled.show()
        else:
            print("dsp:dsp_pwr - error:", mode)
        return


    def dsp_ifttt(self, evt_id, sts):
        print("dsp:dsp_ifttt - run")
        self._oled.fill(0)
        self._oled.text('<IFTTT Request>', 0, 0)
        self._oled.text(('->' +  evt_id), 0, 10)
        self._oled.text(sts, 0, 20)
        self._oled.text('[MicroPython]', 0, 30)
        self._oled.show()
        return



async def proc_dsp(snd_q=None, rcv_q=None):
    print("proc_dsp:run")

    # init
    oled_ctl = OledCtl()
    tmr = machine.Timer(TIMER_ID_DSP)

    def start_timer(type, peri):
        print("dsp:start_timer - run", peri)
        if type == "clear":
            tmr.init(period=int(peri), mode=machine.Timer.ONE_SHOT, callback=set_event_clear)
        return

    def stop_timer():
        print("dsp:stop_timer - run")
        tmr.deinit()
        return

    def set_event_clear(t):
        print("dsp:_set_event_clear - run")
        oled_ctl.dsp_clear()
        return

    def act_dsp(msg):
        print('dsp:act_dsp - run')
        d = conv_msg2dict(msg)
        if False == ('cmd' in d) or False == ('type' in d):
            return False

        # {cmd:dsp,type:ifttt,how:"evt_id",tmr:3000}
        # {cmd:dsp,type:power,how:server,tmr:3000}
        # {cmd:dsp,type:power,how:client,tmr:3000}
        # {cmd:dsp,type:power,how:done,tmr:3000}
        # {cmd:dsp,type:clear,how: ,tmr:0}
        typ = d['type'] if ('type' in d) else "dummy"
        how = d['how'] if ('how' in d) else "dummy"
        tm_count = int(d['tmr']) if ('tmr' in d) else -1

        if "power" == typ:
            oled_ctl.dsp_power(how)
        elif "clear" == typ:
            oled_ctl.dsp_clear()
        elif "ifttt" == typ:
            sts = d['sts'] if ('sts' in d) else "dummy"
            oled_ctl.dsp_ifttt(how, sts)
        else:
            return False

        # timer
        if tm_count > 0:
            start_timer(type="clear", peri=tm_count)

        print('dsp:act_dsp - over')
        return True

    while True:
        # recvive_que
        msg = recv_que(rcv_q)
        if msg is None:
            # print("IndexError")
            await asyncio.sleep_ms(50)
            continue

        # stop : timer
        stop_timer()

        print("proc_dsp:msg - ", msg)
        act_dsp(msg)

    return


async def debug_main():
    que_pre2dsp = []
    asyncio.create_task(proc_dsp(snd_q=None, rcv_q=que_pre2dsp))
    await asyncio.sleep_ms(1_000)
    send_que(que_pre2dsp, ("dst:dsp,src:pre,cmd:dsp,type:ifttt,how:evt_id,sts:sending...,tmr:3000"))
    await asyncio.sleep_ms(1_000)
    send_que(que_pre2dsp, ("dst:dsp,src:pre,cmd:dsp,type:ifttt,how:evt_id,sts:sended.,tmr:3000"))
    await asyncio.sleep_ms(3_000)
    send_que(que_pre2dsp, ("dst:dsp,src:pre,cmd:dsp,type:power,how:server,tmr:3000"))
    await asyncio.sleep_ms(3_000)
    send_que(que_pre2dsp, ("dst:dsp,src:pre,cmd:dsp,type:power,how:client,tmr:3000"))
    await asyncio.sleep_ms(3_000)
    send_que(que_pre2dsp, ("dst:dsp,src:pre,cmd:dsp,type:power,how:done,tmr:3000"))
    await asyncio.sleep_ms(10_000)
    print("debug - done!")
    await asyncio.sleep_ms(1_000)
    return

def main():
    asyncio.run(debug_main())

if __name__ == "__main__":
    main()
