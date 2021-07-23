import _thread
import time

from util import TackSwitch
from util import CommSnd
from util import ADDR
from util import PORT_DST_CTL

PIN_SW_NO1 = 35
PIN_SW_NO2 = 33
PIN_SW_NO3 = 19
PIN_SW_NO4 = 32
PIN_SW_NO5 = 34
#PIN_SW_NO6 = 255    dummy
PIN_SW_NO7 = 23
PIN_SW_NO8 = 18
PIN_SW_NO9 = 5

class SwProc():
    
    def __init__(self):
        self._cs_ctl = CommSnd(ADDR, PORT_DST_CTL)
        self._tsw_no1 = TackSwitch(PIN_SW_NO1, "in", 0)
        self._tsw_no2 = TackSwitch(PIN_SW_NO2, "in", 0)
        self._tsw_no3 = TackSwitch(PIN_SW_NO3, "in_pullup", 0)
        self._tsw_no4 = TackSwitch(PIN_SW_NO4, "in", 0)
        self._tsw_no5 = TackSwitch(PIN_SW_NO5, "in", 0)
        # self._tsw_no6 = TackSwitch(PIN_SW_NO6, "in_pullup", 0)
        self._tsw_no7 = TackSwitch(PIN_SW_NO7, "in_pullup", 0)
        self._tsw_no8 = TackSwitch(PIN_SW_NO8, "in_pullup", 0)
        self._tsw_no9 = TackSwitch(PIN_SW_NO9, "in_pullup", 0)

        self.debug_SW_NO1_count = 0
        self.debug_SW_NO2_count = 0
        self.debug_SW_NO3_count = 0
        self.debug_SW_NO4_count = 0
        self.debug_SW_NO5_count = 0
        # self.debug_SW_NO6_count = 0
        self.debug_SW_NO7_count = 0
        self.debug_SW_NO8_count = 0
        self.debug_SW_NO9_count = 0
        # self.debug_SW_NO10_count = 0
        return


    def _proc_poll(self):
        print("_proc_poll - run")
        while True:
            time.sleep_ms(50)
            sw_evt, sw_how = self._tsw_no1.read_poll()
            if sw_evt :
                self.debug_SW_NO1_count += 1
                print("sw_no1 : ", sw_how)
                self._cs_ctl.sendto_dict({'cmd': "sw", 'type':'no1', 'how':sw_how})

            sw_evt, sw_how = self._tsw_no2.read_poll()
            if sw_evt :
                self.debug_SW_NO2_count += 1
                print("sw_no2 : ", sw_how)
                self._cs_ctl.sendto_dict({'cmd': "sw", 'type':'no2', 'how':sw_how})

            sw_evt, sw_how = self._tsw_no3.read_poll()
            if sw_evt :
                self.debug_SW_NO3_count += 1
                print("sw_no3 : ", sw_how)
                self._cs_ctl.sendto_dict({'cmd': "sw", 'type':'no3', 'how':sw_how})

            sw_evt, sw_how = self._tsw_no4.read_poll()
            if sw_evt :
                self.debug_SW_NO4_count += 1
                print("sw_no4 : ", sw_how)
                self._cs_ctl.sendto_dict({'cmd': "sw", 'type':'no4', 'how':sw_how})

            sw_evt, sw_how = self._tsw_no5.read_poll()
            if sw_evt :
                self.debug_SW_NO5_count += 1
                print("sw_no5 : ", sw_how)
                self._cs_ctl.sendto_dict({'cmd': "sw", 'type':'no5', 'how':sw_how})

            # sw_evt, sw_how = self._tsw_no6.read_poll()
            # if sw_evt :
            #     self.debug_SW_NO6_count += 1
            #     print("sw_no6 : ", sw_how)
            #     self._cs_ctl.sendto_dict({'cmd': "sw", 'type':'no6', 'how':sw_how})

            sw_evt, sw_how = self._tsw_no7.read_poll()
            if sw_evt :
                self.debug_SW_NO7_count += 1
                print("sw_no7 : ", sw_how)
                self._cs_ctl.sendto_dict({'cmd': "sw", 'type':'no7', 'how':sw_how})

            sw_evt, sw_how = self._tsw_no8.read_poll()
            if sw_evt :
                self.debug_SW_NO8_count += 1
                print("sw_no8 : ", sw_how)
                self._cs_ctl.sendto_dict({'cmd': "sw", 'type':'no8', 'how':sw_how})

            sw_evt, sw_how = self._tsw_no9.read_poll()
            if sw_evt :
                self.debug_SW_NO9_count += 1
                print("sw_no9 : ", sw_how)
                self._cs_ctl.sendto_dict({'cmd': "sw", 'type':'no9', 'how':sw_how})

            # sw_evt, sw_how = self._tsw_no10.read_poll()
            # if sw_evt :
            #     self.debug_SW_NO10_count += 1
            #     print("sw_no10 : ", sw_how)
            #     self._cs_ctl.sendto_dict({'cmd': "sw", 'type':'no10', 'how':sw_how})


    def run(self):
        _thread.start_new_thread(self._proc_poll, ())
