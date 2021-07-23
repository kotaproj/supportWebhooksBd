import _thread
from usocket import socket, AF_INET, SOCK_DGRAM
import ujson as json
import machine

import ssd1306

from settings import SettingsFile
from util import CommSnd
from util import HOST
from util import ADDR
from util import PORT_DST_DSP

RCV_BUF_SIZE = 128
PIN_SCL = 22
PIN_SDA = 21

TIMER_ID_DSP = 0

class DspProc():
    
    def __init__(self, mode):
        i2c = machine.I2C(scl=machine.Pin(PIN_SCL), sda=machine.Pin(PIN_SDA))
        self._oled = ssd1306.SSD1306_I2C(128, 64, i2c)
        self._tmr = machine.Timer(TIMER_ID_DSP)
        self._cs_dsp = CommSnd(ADDR, PORT_DST_DSP)
        self._settings_file = SettingsFile()
        self.dsp_pwr_on(mode)
        return


    def dsp_clear(self):
        self._oled.fill(0)
        self._oled.show()
        return


    def dsp_pwr_on(self, mode):
        print("dsp:_dsp_pwr_on - run")
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
            # self._oled.text('OLED display', 0, 30)
            self._oled.show()         
        else:
            self._oled.fill(0)
            self._oled.text('Booting...', 0, 0)
            self._oled.text('Client Mode', 0, 10)
            self._oled.show()         

        return


    def dsp_pwr_done(self):
        print("dsp:dsp_pwr_done - run")
        self.dsp_clear()
        return


    def _start_timer(self, type, peri):
        print("dsp:_start_timer - run", peri)
        if type == "clear":
            self._tmr.init(period=int(peri), mode=machine.Timer.ONE_SHOT, callback=self._set_event_clear)
        return


    def _stop_timer(self):
        print("dsp:_stop_timer - run")
        self._tmr.deinit()
        return


    def _set_event_clear(self, t):
        print("dsp:_set_event_clear - run")
        self._cs_dsp.sendto_dict({'cmd': "dsp", 'type':'clear'})
        return


    def _act_cmd(self, d):
        print('dsp:_act_cmd - run')

        if False == ('cmd' in d) or False == ('type' in d):
            return False

        if 'dsp' in d['cmd']:
            self._act_cmd_dsp(d['type'])

        if 're' in d['type']:
            self._act_cmd_dsp_re(d['type'], d['pos'])

        if True == ('tmr' in d):
            self._start_timer(type="clear", peri=d['tmr'])
            # self._start_timer("clear", d['tmr'])
            # self._start_timer("clear", "3000")

        print('dsp:_act_cmd - over')
        return True


    def _act_cmd_dsp(self, code):

        parse_code = {
            'no1' : "btn1_evt",
            'no2' : "btn2_evt",
            'no3' : "btn3_evt",
            'no4' : "btn4_evt",
            'no5' : "btn5_evt",
            'no6' : "btn6_evt",
            'no7' : "btn7_evt",
            'no8' : "btn8_evt",
            'no9' : "btn9_evt",
            'no10': "btn10_evt",
        }

        for key in parse_code.keys():
            if key in code:
                self._oled.fill(0)
                self._oled.text('<IFTTT Request>', 0, 0)
                # message = '->' +  self._settings_file.get_param(parse_code[key])
                self._oled.text(('->' +  self._settings_file.get_param(parse_code[key])), 0, 10)
                if "sending" in code:
                    self._oled.text('Sending...', 0, 20)
                if "sended" in code:
                    self._oled.text('Sended', 0, 20)
                self._oled.text('[MicroPython]', 0, 30)
                self._oled.show()
                break

        if 'clear' in code:
            print("dsp:_act_cmd_dsp - clear")
            self._oled.fill(0)
            self._oled.show()

        return


    def _act_cmd_dsp_re(self, code, pos):
        self._oled.fill(0)
        self._oled.text('<Rotary Enc>', 0, 0)
        self._oled.text(' position', 0, 10)
        self._oled.text(('->' +  pos), 0, 20)
        self._oled.show()
        return


    def _proc_dsp(self):
        count = 0
        s = socket(AF_INET, SOCK_DGRAM)
        s.bind((HOST, PORT_DST_DSP))

        while True:
            # 受信
            count += 1
            msg, address = s.recvfrom(RCV_BUF_SIZE)

            # タイマーの強制停止
            self._stop_timer()

            d = json.loads(msg.decode())
            print(d)
            print("while - ", count)
            
            self._act_cmd(d)

        s.close()


    def run(self):
        _thread.start_new_thread(self._proc_dsp, ())


    def debug_clear(self):
        self._oled.fill(0)
        self._oled.show()
