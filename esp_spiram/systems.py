from util import TackSwitch
import time
import sys

PIN_SW_NO1 = 35
PIN_SW_NO3 = 19
AP_SSID = 'WebhooksBoard'
AP_PASSWORD = '12345678'
AP_IP = '192.168.200.1'

class SystemsData:
    _instance = None

    def __init__(self):
        print("SystemData - init")


    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)

        return cls._instance


    def _init_work(self):
        tsw_no1 = TackSwitch(PIN_SW_NO1, "in", 0)
        tsw_no3 = TackSwitch(PIN_SW_NO3, "in_pullup", 0)

        # If [tsw_no3] is pressed, exit the program
        for i in range(10):
            if False == tsw_no3.read():
                time.sleep_ms(10)
                continue
            print("!!!program shutdown!!!")
            time.sleep_ms(100)
            sys.exit()

        self._system_mode = "server"

        for i in range(10):
            if True == tsw_no1.read():
                time.sleep_ms(10)
                continue
            self._system_mode = "client"

        return self._system_mode

    def get_system_mode(self):
        try:
            return self._system_mode
        except:
            return self._init_work()


    def get_system_AP_SSID(self):
        return AP_SSID


    def get_system_AP_PASSWORD(self):
        return AP_PASSWORD


    def get_system_AP_IP(self):
        return AP_IP

