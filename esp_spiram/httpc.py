import _thread
from usocket import socket, AF_INET, SOCK_DGRAM
import network
import ujson as json
import urequests as requests
import time
import gc

from settings import SettingsFile
from ifttt_evt import KEY_TO_EVENTID
from util import *

class HttpcProc():
    
    def __init__(self, lock=None, snd_que=None, rcv_que=None):
        # param
        settings_file = SettingsFile()
        self._token = settings_file.get_param("token")
        self._ssid = settings_file.get_param("ssid")
        self._password = settings_file.get_param("password")
        self._lock = lock
        self._snd_que = snd_que
        self._rcv_que = rcv_que

        # self._ssid = ssid
        # self._password = password
        # self._cs_ctl = CommSnd(ADDR, PORT_DST_CTL)
        # self._settings_file = SettingsFile()
        # # self._rtc = RTC()
        # # self._rtc.datetime((2020, 2, 23, 11, 45, 0, 0, 0))
        # self._led_proc = LedProc()
        # self._led_proc.run()
        # self._led_proc.on_all()
        # self.do_connect()
        return


    def do_connect(self):

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

        send_que(self._lock, self._snd_que, ("dst:pre,src:httpc,cmd:dsp,type:clear"))
        send_que(self._lock, self._snd_que, ("dst:pre,src:httpc,cmd:led,type:off_all"))
        print('network config:', wlan.ifconfig())
        send_que(self._lock, self._snd_que, ("dst:pre,src:httpc,cmd:led,type:blink,name:green"))
        return


    def _proc_httpc(self):

        def act_httpc(msg):

            def do_webhook(eventid, value1="dummy1", value2="dummy2", value3="dummy3"):
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

                url = "http://maker.ifttt.com/trigger/" + eventid + "/with/key/" + self._token

                ret = True
                try:
                    # response = requests.post(url, headers={"Content-Type": "application/x-www-form-urlencoded"}, data=payload)
                    # value指定が不要な場合は↓でok
                    response = requests.post(url)
                    send_que(self._lock, self._snd_que, ("dst:pre,src:httpc,cmd:led,type:blink,name:blue"))
                    response.close()
                except:
                    send_que(self._lock, self._snd_que, ("dst:pre,src:httpc,cmd:led,type:blink,name:red"))
                    ret = False
                return ret

            print("act_httpc:run")
            d = conv_msg2dict(msg)
            print(d)
            cmd, typ = d["cmd"], d["type"]

            if "sw" in cmd:
                how = d["how"]
                evt_id = conv_typ2eventid(typ, how)
                print(evt_id)
                if evt_id is not None:
                    send_que(self._lock, self._snd_que, ("dst:pre,src:httpc,cmd:dsp,type:ifttt,how:"+evt_id+",sts:sending...,tmr:3000"))
                    do_webhook(evt_id)
                    send_que(self._lock, self._snd_que, ("dst:pre,src:httpc,cmd:dsp,type:ifttt,how:"+evt_id+",sts:sended.,tmr:3000"))
            else:
                print("act_httpc:error, ", msg)
            return


        is_connect = False

        while True:

            if is_connect is False:
                self.do_connect()
                is_connect = True

            msg = recv_que(self._lock, self._rcv_que)
            if msg is None:
                time.sleep_ms(50)
                continue

            print("proc_httpc:msg - ", msg)
            ret = act_httpc(msg)
            if False == ret:
                # reconnect
                is_connect = False
        return


    def run(self):
        _thread.start_new_thread(self._proc_httpc, ())


def main():

    lock = _thread.allocate_lock()

    que_pre2httpc = []
    httpc_proc = HttpcProc(lock, snd_que=None, rcv_que=que_pre2httpc)
    httpc_proc.run()

    time.sleep_ms(5_000)
    send_que(lock, que_pre2httpc, ("dst:httpc,src:pre,cmd:sw,type:no3,how:released"))
    time.sleep_ms(5_000)
    send_que(lock, que_pre2httpc, ("dst:httpc,src:pre,cmd:sw,type:no3,how:released"))
    time.sleep_ms(10_000)
    return

if __name__ == "__main__":
    main()
