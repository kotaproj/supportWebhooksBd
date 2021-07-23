import _thread
import time
from machine import Pin
import utime

# from util import TackSwitch

from rotary_enc import RotaryEnc
from util import CommSnd
from util import ADDR
from util import PORT_DST_CTL

PIN_RE_A_PH = 2
PIN_RE_B_PH = 4


class ReProc():
    
    def __init__(self):
        self._cs_ctl = CommSnd(ADDR, PORT_DST_CTL)
        self._re = RotaryEnc(PIN_RE_A_PH, PIN_RE_B_PH)
        self._prev_position = 0
        return


    def _proc_poll(self):
        print("_proc_poll - run")
        while True:
            time.sleep_ms(50)
            position = self._re.get_positon()
            if position != self._prev_position :
                print("re", str(position - self._prev_position), str(position))
                self._cs_ctl.sendto_dict({  'cmd': "re",
                                            'type':str(position - self._prev_position),
                                            'pos':str(position)})
                self._prev_position = position


    def run(self):
        _thread.start_new_thread(self._proc_poll, ())

