from machine import Pin
import utime

LATCHSTATE = 3    # org
# LATCHSTATE = 2
# LATCHSTATE = 1

RE_DIR = [
    0,  -1, 1,  0,
    1,  0,  0,  -1,
    -1, 0,  0,  1,
    0,  1,  -1,  0
]


class RotaryEnc:
    def __init__(self, pin_a, pin_b):
        # self._pin_a = Pin(pin_a, Pin.IN)
        # self._pin_b = Pin(pin_b, Pin.IN)
        self._pin_a = Pin(pin_a, Pin.IN, Pin.PULL_UP)
        self._pin_b = Pin(pin_b, Pin.IN, Pin.PULL_UP)

        self._sig1_state = 0
        self._sig2_state = 0
        self._this_state = 0
        self._old_state = 3
        self._position = 0
        self._position_ext = 0
        self._position_ext_prev = 0

        self._pin_a.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=self._tick)
        self._pin_b.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=self._tick)

        self._count_tick = 0
        return


    def _tick(self, pin):
        self._count_tick += 1

        self._sig1_state = self._pin_a.value()
        self._sig2_state = self._pin_b.value()

        self._this_state = self._sig1_state + (self._sig2_state * 2)

        if self._old_state != self._this_state:
            self._position += RE_DIR[self._this_state + (self._old_state * 4)]
        
            if self._this_state == LATCHSTATE:
                self._position_ext = self._position // 4  # org
                # self._position_ext = self._position // 2
                self._position_ext_prev = self._position_ext
                self._position_ext = utime.ticks_ms()
        
            self._old_state = self._this_state


    def get_positon(self):
        # return self._position // 4
        return self._position // 2 # org


    def debug_print(self):
        print("_sig1_state : " , self._sig1_state)
        print("_sig2_state : " , self._sig2_state)
        print("_this_state : " , self._this_state)
        print("_old_state : " , self._old_state)
        print("_position : " , self._position)
        print("_position_ext : " , self._position_ext)
        print("_position_ext_prev : " , self._position_ext_prev)
        print("_count_tick : " , self._count_tick)


