import _thread
from usocket import socket, AF_INET, SOCK_DGRAM
import ujson as json
import urequests as requests
import time
import gc

from settings import SettingsFile
from util import CommSnd
from util import HOST
from util import ADDR
from util import PORT_DST_HTTPC
from util import PORT_DST_DSP
from led import LedProc
from ifttt_evt import KEY_TO_EVENTID

RCV_BUF_SIZE = 64

class HttpcProc():
    
    def __init__(self, ssid, password):
        self._ssid = ssid
        self._password = password
        self._cs_dsp = CommSnd(ADDR, PORT_DST_DSP)
        self._settings_file = SettingsFile()
        # self._rtc = RTC()
        # self._rtc.datetime((2020, 2, 23, 11, 45, 0, 0, 0))
        self._led_proc = LedProc()
        self._led_proc.run()
        self._led_proc.on_all()
        self.do_connect()


    def do_connect(self):

        import network
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        if not wlan.isconnected():
            print('connecting to network...')
            # wlan.connect('essid', 'password')
            wlan.connect(self._ssid, self._password)
            while not wlan.isconnected():
                pass
                # time.sleep(1)
                time.sleep(3)
                print(".")
        self._led_proc.off_all()
        print('network config:', wlan.ifconfig())
        self._led_proc.blink_led("green")

        return


    def _act_cmd(self, d):
        print('_act_cmd - run')

        if False == ('cmd' in d):
            return False

        if 'httpc' in d['cmd']:
            self._act_cmd_sw(d['type'], d['how'])
            return True
        
        print('_act_cmd - over')
        return False


    def _act_cmd_sw(self, code, how):
        if code in KEY_TO_EVENTID:
            evt_id = KEY_TO_EVENTID[code][how]
            if evt_id is not None:
                self._cs_dsp.sendto_dict({'cmd': "dsp", 'type':(code + ":" + how + "..."), 'tmr':'3000'})
                self._do_webhook(evt_id)
                self._cs_dsp.sendto_dict({'cmd': "dsp", 'type':(code + ":" + how + "!!!"), 'tmr':'3000'})
        return


    def _do_webhook(self, eventid, value1="dummy1", value2="dummy2", value3="dummy3"):


        # care memory
        gc.collect()

        # valueに載せる情報
        payload = "value1="
        # payload += str(self._rtc.datetime())
        payload += value1
        payload += "&value2="
        payload += value2
        payload += "&value3="
        payload += value3

        url = "http://maker.ifttt.com/trigger/" + eventid + "/with/key/" + self._settings_file.get_param("token")

        response = requests.post(url, headers={"Content-Type": "application/x-www-form-urlencoded"}, data=payload)
        # value指定が不要な場合は↓でok
        # response = requests.post(url)
        self._led_proc.blink_led("blue")

        response.close()
        return




    def _proc_httpc(self):
        count = 0
        s = socket(AF_INET, SOCK_DGRAM)
        s.bind((HOST, PORT_DST_HTTPC))

        while True:

            # recive
            # count += 1
            msg, address = s.recvfrom(RCV_BUF_SIZE)

            d = json.loads(msg.decode())
            # print(d)
            # print("while - ", count)
            self._act_cmd(d)

        s.close()


    def run(self):
        _thread.start_new_thread(self._proc_httpc, ())
