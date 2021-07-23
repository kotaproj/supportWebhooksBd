try:
    import uio as io
except:
    import io
try:
    import ujson as json
except:
    import json



SETTINGS_TXT = "settings.txt"

INIT_SET_DATA = {
    "ssid" : "ssid",
    "password" : "password",
    "token" : "token",
}


class SettingsFile:
    _instance = None

    def __init__(self):
        print('init')
        self._set_data = {}
        self.read()


    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)

        return cls._instance


    def reset(self):
        print('reset - run')
        f = io.open(SETTINGS_TXT, "w")
        f.write(json.dumps(INIT_SET_DATA))
        f.close()
        self._set_data = INIT_SET_DATA.copy()
        print('reset - over')
        return


    def read(self):
        print('read - run')

        try:
            print('read - r1')
            f = io.open(SETTINGS_TXT, "r")
            print('read - r2')
            print(json.loads( f.read() ))
            print('read - r3')
            # set_data = json.loads( f.read().replace("\'", "\"") )
            f.seek(0)
            self._set_data = json.loads( f.read() ).copy()
            print('read - r4')
        except:
            print('read - reset')
            self.reset()

        f.close()
        print('read - over')
        return


    def write(self):
        print('write - run')
        f = io.open(SETTINGS_TXT, "w")
        f.write(json.dumps(self._set_data))
        f.close()
        print('write - over')
        return


    def get_param(self, key):
        return self._set_data[key]


    def set_param(self, key, value):
        self._set_data[key] = value


    def get_re_pos(self):
        return self.re_pos


    def set_re_pos(self, pos):
        self.re_pos = pos


    def debug_all(self):
        return self._set_data


