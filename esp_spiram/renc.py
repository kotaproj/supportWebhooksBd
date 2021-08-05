import _thread
import time
from machine import Pin

from rotary_enc import RotaryEnc
from util import *

PIN_RE_A_PH = 2
PIN_RE_B_PH = 4


class ReProc():
    
    def __init__(self, lock=None, snd_que=None, rcv_que=None):
        self._re = RotaryEnc(PIN_RE_A_PH, PIN_RE_B_PH)
        self._lock = lock
        self._snd_que = snd_que
        return


    def _proc_poll(self):
        print("_proc_poll - run")
        prev_position = 0
        while True:
            time.sleep_ms(50)
            position = self._re.get_positon()
            if position != prev_position :
                print("re", str(position - prev_position), str(position))
                send_que(self._lock, self._snd_que, ("dst:pre,src:renc,cmd:renc" + ",type:" + str(position) + ",chg_val:" + str(position - prev_position)))
                prev_position = position
        return

    def run(self):
        _thread.start_new_thread(self._proc_poll, ())


def main():
    lock = _thread.allocate_lock()
    que_re2pre = []
    re_proc = ReProc(lock, snd_que=que_re2pre)
    re_proc.run()
    time.sleep(1)
    print(que_re2pre)
    time.sleep(1)
    print(que_re2pre)
    time.sleep(5)
    print(que_re2pre)
    time.sleep(1)


if __name__ == "__main__":
    main()
