# WiFiAccessPoint, WebServer on ESP32 MicroPython
import network
import machine
import time
# import _thread
import socket
import re

from settings import SettingsFile

# WiFiAccessPoint
AP_SSID = 'WebhooksBoard'
AP_PASSWORD = '12345678'

# webserver
IP = '192.168.200.1'

# html
HTML_FORMAT_BASE = """<!DOCTYPE html> <html>
<head><meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
<title>Webhooks Board </title>
<style>html { font-family: Helvetica; display: inline-block; margin: 0px auto; text-align: center;}
body{margin-top: 50px;} h1 {color: #444444;margin: 50px auto 30px;} h3 {color: #444444;margin-bottom: 50px;}
.button {display: block;width: 80px;background-color: #3498db;border: none;color: white;padding: 13px 30px;text-decoration: none;font-size: 25px;margin: 0px auto 35px;cursor: pointer;border-radius: 4px;}
.button-on {background-color: #3498db;}
.button-on:active {background-color: #2980b9;}
.button-off {background-color: #34495e;}
.button-off:active {background-color: #2c3e50;}
p {font-size: 14px;color: #888;margin-bottom: 10px;}
</style>
</head>
replace_body
</html>"""

HTML_FORMAT_BODY_SAVED = """<body>
<h1>ESP32 Web Server [using MicroPython]</h1>
<h3>Saved...</h3>
</body>"""

HTML_FORMAT_BODY_FORM = """<body>
<h1>ESP32 Web Server [using MicroPython]</h1>
<h3>Setting : Webhook Board</h3>

<form action="/form" method="post">
<p>
ssid:<input type="text" name="ssid" value="replace_ssid" size="40">
</p>
<p>
pass:<input type="text" name="pass" value="replace_password" size="40">
</p>

<br>
<br>

<p>
access key:<input type="text" name="acskey" value="replace_token" size="40">
</p>

<input type="hidden" name="dummy" value="1">

<input type="submit" value="send"><input type="reset" value="reset">
</p>
</form>
</body>"""

# form pattern
PTN_DICT = {
    "ssid": 'ssid=',
    "password": 'pass=',
    "token": 'acskey=',
}

class HttpdProc():
    
    def __init__(self):
        # self._ssid = ssid
        # self._password = password
        self._settings_file = SettingsFile()
        return


    def _wiFiAccessPoint(self, essid, pwd, ip, mask, gw, dns):
        ap = network.WLAN(network.AP_IF)
        ap.config(essid=essid, authmode=3, password=pwd)
        ap.ifconfig((ip,mask,gw,dns))
        print("(ip,netmask,gw,dns)=" + str(ap.ifconfig()))
        ap.active(True)
        return ap


    def _get_html_form(self):

        html = HTML_FORMAT_BASE
        html = html.replace("replace_body", HTML_FORMAT_BODY_FORM)

        ssid = self._settings_file.get_param("ssid")
        # print("ssid - ", ssid)
        password = self._settings_file.get_param("password")
        # print("password - ", password)
        token = self._settings_file.get_param("token")
        # print("token - ", token)

        html = html.replace("replace_ssid", ssid)
        html = html.replace("replace_password", password)
        html = html.replace("replace_token", token)

        return html


    def _get_html_saved(self):
        html = HTML_FORMAT_BASE
        html = html.replace("replace_body", HTML_FORMAT_BODY_SAVED)
        return html


    def run(self):
        self._wiFiAccessPoint(AP_SSID,AP_PASSWORD,IP,'255.255.255.0',IP,'8.8.8.8')

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('', 80))
        s.listen(5)

        while True:
            saved_flag = False
            conn, addr = s.accept()
            print("Got a connection from %s" % str(addr))
            request = conn.recv(1024* 2)
            request = str(request)
            # print(request)
            # print("Content = %s" % request)

            # analize - form
            #  "..key=value&.." -> "value"
            for key in PTN_DICT.keys():
                srt_point = request.find(PTN_DICT[key])
                if srt_point > 0:
                    sep_point = request[srt_point:].find('&')
                    if sep_point > 0:
                        print("find!", request[srt_point+len(PTN_DICT[key]):srt_point+sep_point])
                        self._settings_file.set_param(key=key, value=request[srt_point+len(PTN_DICT[key]):srt_point+sep_point])
                        saved_flag = True

            if saved_flag:
                self._settings_file.write()
                response = self._get_html_saved()
            else:
                response = self._get_html_form()

            conn.send("HTTP/1.1 200 OK")
            conn.send("Content-Type: text/html; encoding=utf8\nContent-Length: ")
            conn.send(str(len(response)))
            conn.send("\nConnection: close\n")
            conn.send("\n")
            conn.send(response)
            conn.close()
