from machine import Pin

# 100msec
TACT_JUDGE_PRESS = [False, False, True, True]
# 1sec
TACT_JUDGE_LONG = [False, False, 
                   True, True, True, True, True, True, True, True,
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
            return True, "relesed"

        # 長押し
        self.long_store.append(logic)
        if len(self.long_store) <= len(TACT_JUDGE_LONG):
            return False, None
        self.long_store.pop(0)
        if TACT_JUDGE_LONG == self.long_store:
            return True, "long"

        return False, None


try:
    from usocket import socket, AF_INET, SOCK_DGRAM
except:
    from socket import socket, AF_INET, SOCK_DGRAM

try:
    import ujson as json
except:
    import json


HOST = ''
PORT = 5000
PORT_DST_CTL = 5001
PORT_DST_DSP = 5002
PORT_DST_HTTPC = 5003
ADDR = '127.0.0.1'

class CommSnd:

    def __init__(self, addr, port):
        self.addr = addr
        self.port = port
        self.s = socket(AF_INET, SOCK_DGRAM)


    def sendto_dict(self, d):
        # text = json.dumps(d)
        # self.s.sendto(text.encode(), (self.addr, self.port))
        self.s.sendto(json.dumps(d).encode(), (self.addr, self.port))


    def close(self):
        self.s.close()



