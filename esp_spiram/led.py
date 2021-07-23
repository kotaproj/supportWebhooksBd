import _thread
import time
from machine import Pin

# from util import TackSwitch
# from util import CommSnd
# from util import ADDR
# from util import PORT_DST_CTL

PIN_LED_RED = 27
PIN_LED_GRENN = 26
PIN_LED_BLUE = 25


class LedProc():
    
    def __init__(self):
        self._leds = {}
        self._leds["red"] = {"pin":Pin(PIN_LED_RED, Pin.OUT), "blink":False, "cont":False, "count":0}
        self._leds["green"] = {"pin":Pin(PIN_LED_GRENN, Pin.OUT), "blink":False, "cont":False, "count":0}
        self._leds["blue"] = {"pin":Pin(PIN_LED_BLUE, Pin.OUT), "blink":False, "cont":False, "count":0}
        self._blink_status = False
        return


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


    def _proc_poll(self):
        print("_proc_poll - run")
        while True:
            time.sleep_ms(200)
            if self._blink_status:
                self._blink_status = False
            else:
                self._blink_status = True

            for key in self._leds:
                if self._leds[key]["blink"] and (self._leds[key]["cont"] or self._leds[key]["count"] > 0):
                    self._leds[key]["pin"].value(self._blink_status)
                    self._leds[key]["count"] -= 1
                    if self._leds[key]["count"] == 0:
                        self._leds[key]["pin"].value(False)
        return


    def run(self):
        _thread.start_new_thread(self._proc_poll, ())
