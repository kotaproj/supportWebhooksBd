from machine import Pin

TACK_JUDGE = [False, False, True, True]
# TACK_JUDGE = [False, False, False, False]

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
        self.store.append(logic)
        if len(self.store) < 5:
            return False

        self.store.pop(0)
        if TACK_JUDGE == self.store:
            return True
        
        return False


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



