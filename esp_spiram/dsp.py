import _thread
import machine
import time

import ssd1306

from systems import SystemsData
from settings import SettingsFile
from util import *

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


class DspProc():
    
    def __init__(self, lock=None, snd_que=None, rcv_que=None):

        # init
        print("dsp:__init__ - run")
        self._oled_ctl = OledCtl()
        self._tmr = machine.Timer(TIMER_ID_DSP)
        self._lock = lock
        self._snd_que = snd_que
        self._rcv_que = rcv_que
        self._clear_flg = False
        return

    def _proc_dsp(self):
        print("dsp:_proc_dsp - run")

        def start_timer(type, peri):
            print("dsp:start_timer - run", peri)
            if type == "clear":
                self._tmr.init(period=int(peri), mode=machine.Timer.ONE_SHOT, callback=set_event_clear)
            return

        def stop_timer():
            print("dsp:stop_timer - run")
            self._tmr.deinit()
            self._clear_flg = False
            return

        def set_event_clear(t):
            print("dsp:_set_event_clear - run")
            self._clear_flg = True
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
                self._oled_ctl.dsp_power(how)
            elif "clear" == typ:
                self._oled_ctl.dsp_clear()
            elif "ifttt" == typ:
                sts = d['sts'] if ('sts' in d) else "dummy"
                self._oled_ctl.dsp_ifttt(how, sts)
            else:
                return False

            # timer
            if tm_count > 0:
                start_timer(type="clear", peri=tm_count)


            print('dsp:act_dsp - over')
            return True

        while True:
            # recvive_que
            msg = recv_que(self._lock, self._rcv_que)
            if msg is None:
                # print("IndexError")
                time.sleep_ms(50)
                # clear
                if self._clear_flg:
                    self._oled_ctl.dsp_clear()
                    self._clear_flg = False
                continue

            # stop : timer
            stop_timer()
            print("proc_dsp:msg - ", msg)
            act_dsp(msg)

        return


    def run(self):
        _thread.start_new_thread(self._proc_dsp, ())


    def debug_clear(self):
        self._oled.fill(0)
        self._oled.show()




def main():

    lock = _thread.allocate_lock()

    que_dsp2pre = []
    que_pre2dsp = []
    dsp_proc = DspProc(lock, snd_q=que_dsp2pre, rcv_q=que_pre2dsp)
    dsp_proc.run()
    
    send_que(lock, que_pre2dsp, ("dst:dsp,src:pre,cmd:dsp,type:power,how:server,tmr:3000"))

    
    send_que(lock, que_pre2dsp, ("dst:dsp,src:pre,cmd:dsp,type:ifttt,how:evt_id,sts:sending...,tmr:3000"))
    send_que(lock, que_pre2dsp, ("dst:dsp,src:pre,cmd:dsp,type:ifttt,how:evt_id0,sts:sended.,tmr:3000"))
    send_que(lock, que_pre2dsp, ("dst:dsp,src:pre,cmd:dsp,type:ifttt,how:evt_id1,sts:sended.,tmr:3000"))
    send_que(lock, que_pre2dsp, ("dst:dsp,src:pre,cmd:dsp,type:ifttt,how:evt_id2,sts:sended.,tmr:3000"))
    send_que(lock, que_pre2dsp, ("dst:dsp,src:pre,cmd:dsp,type:ifttt,how:evt_id3,sts:sended.,tmr:3000"))
    send_que(lock, que_pre2dsp, ("dst:dsp,src:pre,cmd:dsp,type:ifttt,how:evt_id4,sts:sended.,tmr:3000"))
    send_que(lock, que_pre2dsp, ("dst:dsp,src:pre,cmd:dsp,type:ifttt,how:evt_id5,sts:sended.,tmr:3000"))
    time.sleep_ms(20_000)
    time.sleep_ms(1_000)
    time.sleep_ms(1_000)
    send_que(lock, que_pre2dsp, ("dst:dsp,src:pre,cmd:dsp,type:ifttt,how:evt_id,sts:sended.,tmr:3000"))
    time.sleep_ms(3_000)
    send_que(lock, que_pre2dsp, ("dst:dsp,src:pre,cmd:dsp,type:power,how:server,tmr:3000"))
    # time.sleep_ms(3_000)
    # send_que(lock, que_pre2dsp, ("dst:dsp,src:pre,cmd:dsp,type:power,how:client,tmr:3000"))
    # time.sleep_ms(3_000)
    # send_que(lock, que_pre2dsp, ("dst:dsp,src:pre,cmd:dsp,type:power,how:done,tmr:3000"))
    time.sleep_ms(20_000)
    # print("debug - done!")
    send_que(lock, que_pre2dsp, ("dst:dsp,src:pre,cmd:dsp,type:ifttt,how:evt_id10,sts:sended.,tmr:3000"))
    send_que(lock, que_pre2dsp, ("dst:dsp,src:pre,cmd:dsp,type:ifttt,how:evt_id11,sts:sended.,tmr:3000"))
    send_que(lock, que_pre2dsp, ("dst:dsp,src:pre,cmd:dsp,type:ifttt,how:evt_id12,sts:sended.,tmr:3000"))
    send_que(lock, que_pre2dsp, ("dst:dsp,src:pre,cmd:dsp,type:ifttt,how:evt_id13,sts:sended.,tmr:3000"))
    send_que(lock, que_pre2dsp, ("dst:dsp,src:pre,cmd:dsp,type:ifttt,how:evt_id14,sts:sended.,tmr:3000"))
    send_que(lock, que_pre2dsp, ("dst:dsp,src:pre,cmd:dsp,type:ifttt,how:evt_id15,sts:sended.,tmr:3000"))
    time.sleep_ms(1_000)
    return

if __name__ == "__main__":
    main()
