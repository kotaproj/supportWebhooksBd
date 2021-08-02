import uasyncio as asyncio

from util import *

from machine import Pin

LED_DEFs = {
    "red": (27, ),
    "green": (26, ),
    "blue": (25, ),
}

ledctl_inited = False

class LedCtl:
    _instance = None

    def __init__(self):
        print("LedCtl - init")
        global ledctl_inited
        if False == ledctl_inited:
            self._leds = {}
            for key, val in LED_DEFs.items():
                self._leds[key] = {"pin":Pin(val[0], Pin.OUT), "blink":False, "cont":False, "count":0}
            ledctl_inited = True
        return

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)

        return cls._instance

    def off_all(self):
        for key in self._leds:
            self._leds[key]["blink"] = False
            self._leds[key]["pin"].value(False)
        return

    def on_all(self):
        for key in self._leds:
            self._leds[key]["blink"] = False
            self._leds[key]["pin"].value(True)
        return

    def blink_led(self, led_name, blink=True, cont=False, count=10):
        if led_name in self._leds:
            self._leds[led_name]["blink"] = blink
            self._leds[led_name]["pin"].value(False)
            self._leds[led_name]["cont"] = cont
            self._leds[led_name]["count"] = count
        elif "all" == led_name:
            for key in self._leds:
                self._leds[key]["blink"] = blink
                self._leds[key]["pin"].value(False)
                self._leds[key]["cont"] = cont
                self._leds[key]["count"] = count
        return

    def countdown_blink(self, blk_sts):
        for key in self._leds:
            if self._leds[key]["blink"] and (self._leds[key]["cont"] or self._leds[key]["count"] > 0):
                self._leds[key]["pin"].value(blk_sts)
                self._leds[key]["count"] -= 1
                if self._leds[key]["count"] == 0:
                    self._leds[key]["pin"].value(False)
        return


async def proc_led(snd_q=None, rcv_q=None):
    print("proc_led:run")

    # init
    led_ctl = LedCtl()

    def act_led(msg):

        print("act_led_led:run")
        d = conv_msg2dict(msg)
        print(d)
        if "off_all" in d['type']:
            led_ctl.off_all()
        elif "on_all" in d['type']:
            led_ctl.on_all()
        elif "blink" in d['type']:
            # name, blink, cont, count
            name = 'all'
            blink = True
            cont = False
            count = 10
            if 'name' in d:
                name = d['name']
            if 'blink' in d:
                blink = str2bool(d['blink'])
            if 'cont' in d:
                cont = str2bool(d['cont'])
            if 'count' in d:
                count = int(d['count'])
            led_ctl.blink_led(name, blink, cont, count)
        print('led:_act_cmd - over')
        return


    # polling
    blink_status = False

    while True:
        # recvive_que
        msg = recv_que(rcv_q)
        if msg is None:
            # print("IndexError")
            # LED Blink
            blink_status = False if blink_status else True
            led_ctl.countdown_blink(blink_status)
            await asyncio.sleep_ms(200)
            continue

        print("proc_led:msg - ", msg)
        act_led(msg)

    return


async def debug_main():
    que_pre2led = []
    asyncio.create_task(proc_led(snd_q=None, rcv_q=que_pre2led))
    await asyncio.sleep_ms(1_000)
    # send_que(que_pre2led, )
    send_que(que_pre2led, ("dst:led,src:pre,cmd:led,type:off_all"))
    await asyncio.sleep_ms(1_000)
    send_que(que_pre2led, ("dst:led,src:pre,cmd:led,type:on_all"))
    await asyncio.sleep_ms(1_000)
    send_que(que_pre2led, ("dst:led,src:pre,cmd:led,type:blink"))
    await asyncio.sleep_ms(10_000)
    return

def main():
    asyncio.run(debug_main())

if __name__ == "__main__":
    main()
