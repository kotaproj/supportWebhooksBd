from machine import Pin

import _thread
import time

from util import send_que

TACT_SW_DEFs = {
    "no1": (35, "in", 0),
    "no2": (33, "in", 0),
    "no3": (19, "in_pullup", 0),
    "no4": (32, "in", 0),
    "no5": (34, "in", 0),
    # "no6": (255, "in", 0),
    "no7": (23, "in_pullup", 0),
    "no8": (18, "in_pullup", 0),
    "no9": (5, "in_pullup", 0),
}


# 100msec
TACT_JUDGE_PRESS = [False, False, True, True]
# 1sec
TACT_JUDGE_LONG = [False, False, 
                   True, True, True, True, True, True, True, True]
# released
TACT_JUDGE_RELEASE = [True, True, False, False]

class TackSwitch:
    def __init__(self, pin, mode, push_logic):
        if mode == "in":
            self.pin = Pin(pin, Pin.IN)
            pass
        elif mode == "in_pullup":
            self.pin = Pin(pin, Pin.IN, Pin.PULL_UP)
        else:
            raise Exception('')

        self.store = []
        self.long_store = []
        self.push_logic = push_logic
        self.long_evt = False


    def read(self):
        value = self.pin.value()
        # value = 1 # self.pin.value()
        if value == self.push_logic:
            return True
        else:
            return False


    def read_poll(self):
        logic = self.read()

        # 短押し
        self.store.append(logic)
        if len(self.store) <= len(TACT_JUDGE_PRESS):
            return False, None

        self.store.pop(0)
        if TACT_JUDGE_PRESS == self.store:
            return True, "pressed"

        if TACT_JUDGE_RELEASE == self.store:
            if self.long_evt:
                self.long_evt = False
                return False, None
            return True, "released"

        # 長押し
        self.long_store.append(logic)
        if len(self.long_store) <= len(TACT_JUDGE_LONG):
            return False, None
        self.long_store.pop(0)
        if TACT_JUDGE_LONG == self.long_store:
            self.long_evt = True
            return True, "long"

        return False, None



class SwProc():
    
    def __init__(self, lock=None, snd_que=None, rcv_que=None):
        self._lock = lock
        self._tsws = {k: TackSwitch(v[0], v[1], v[2]) for k, v in TACT_SW_DEFs.items()}
        self._snd_que = snd_que
        self._rcv_que = rcv_que
        return


    def _proc_poll(self):
        print("_proc_poll - run")
        while True:
            time.sleep_ms(25)
            for key, tact_sw in self._tsws.items():
                sw_evt, sw_how = tact_sw.read_poll()
                if sw_evt:
                    print("sw", key, ":", sw_how)
                    send_que(self._lock, self._snd_que, ("dst:pre,src:sw,cmd:sw" + ",type:" + str(key) + ",how:" + sw_how))


    def run(self):
        _thread.start_new_thread(self._proc_poll, ())

def main():
    lock = _thread.allocate_lock()
    que_sw2pre = []
    sw_proc = SwProc(lock, snd_que=que_sw2pre)
    sw_proc.run()
    time.sleep(1)
    print(que_sw2pre)
    time.sleep(1)
    print(que_sw2pre)
    time.sleep(5)
    print(que_sw2pre)
    time.sleep(1)


if __name__ == "__main__":
    main()
