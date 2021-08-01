import uasyncio as asyncio
import uheapq as heapq
import network
import urequests as requests
import gc
from machine import Pin

from settings import SettingsFile
from util import conv_msg2dict
from util import conv_typ2eventid
from util import str2bool

# variable
is_sub_proc_running = False

async def proc_httpc(snd_q=None, rcv_q=None):
    print("proc_httpc:run")
    while True:
        if False == is_sub_proc_running:
            print("proc_httpc:while")
            asyncio.create_task(subproc_httpc(snd_q, rcv_q))
        await asyncio.sleep_ms(5_000)
    return



async def subproc_httpc(snd_q=None, rcv_q=None):
    print("subproc_httpc:run")

    global is_sub_proc_running

    is_sub_proc_running = True

    # param
    settings_file = SettingsFile()
    token = settings_file.get_param("token")
    ssid = settings_file.get_param("ssid")
    password = settings_file.get_param("password")

    # do_connect
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect(ssid, password)
        while not wlan.isconnected():
            await asyncio.sleep_ms(3_000)
            print(".")
    
    heapq.heappush(snd_q, ("dst:pre,src:httpc,cmd:led,type:off_all"))
    print('network config:', wlan.ifconfig())
    heapq.heappush(snd_q, ("dst:pre,src:httpc,cmd:led,type:blink,name:green"))

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

            url = "http://maker.ifttt.com/trigger/" + eventid + "/with/key/" + token

            response = requests.post(url, headers={"Content-Type": "application/x-www-form-urlencoded"}, data=payload)
            # value指定が不要な場合は↓でok
            # response = requests.post(url)
            # self._led_proc.blink_led("blue")
            heapq.heappush(snd_q, ("dst:pre,src:httpc,cmd:led,type:blink,name:blue"))
            response.close()
            return

        print("act_httpc:run")
        d = conv_msg2dict(msg)
        print(d)
        cmd, typ = d["cmd"], d["type"]

        if "sw" in cmd:
            how = d["how"]
            evt_id = conv_typ2eventid(typ, how)
            print(evt_id)
            if evt_id is not None:
                heapq.heappush(snd_q, ("dst:pre,src:httpc,cmd:dsp,type:ifttt,how:"+evt_id+",sts:sending...,tmr:3000"))
                do_webhook(evt_id)
                heapq.heappush(snd_q, ("dst:pre,src:httpc,cmd:dsp,type:ifttt,how:"+evt_id+",sts:sended.,tmr:3000"))
        else:
            print("act_httpc:error, ", msg)
        return

    # polling
    while True:
        # recvive_que
        try:
            msg = heapq.heappop(rcv_q)
        except IndexError:
            if not wlan.isconnected():
                # reconnect
                break
            await asyncio.sleep_ms(100)
            continue

        print("proc_httpc:msg - ", msg)
        act_httpc(msg)

    is_sub_proc_running = False

    return

async def debug_main():
    que_pre2httpc = []
    asyncio.create_task(proc_httpc(snd_q=None, rcv_q=que_pre2httpc))
    await asyncio.sleep_ms(5_000)
    heapq.heappush(que_pre2httpc, ("dst:httpc,src:pre,cmd:sw,type:no3,how:released"))
    await asyncio.sleep_ms(5_000)
    heapq.heappush(que_pre2httpc, ("dst:httpc,src:pre,cmd:sw,type:no3,how:released"))
    await asyncio.sleep_ms(10_000)
    return

def main():
    asyncio.run(debug_main())

if __name__ == "__main__":
    main()
