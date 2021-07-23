from systems import SystemsData
from settings import SettingsFile
from dsp import DspProc


def main():
    systems_data = SystemsData()

    mode = systems_data.get_system_mode()

    print(mode)

    dsp_proc = DspProc(mode)
    dsp_proc.run()

    if "server" == mode:
        proc_server()
    else:
        proc_client()

    dsp_proc.dsp_pwr_done()


def proc_server():
    from httpd import HttpdProc
    httpd_proc = HttpdProc()
    httpd_proc.run()


def proc_client():
    settings_file = SettingsFile()

    from httpc import HttpcProc
    httpc_proc = HttpcProc(
        settings_file.get_param("ssid"),
        settings_file.get_param("password")
    )
    httpc_proc.run()

    from ctl import CtlProc
    ctl_proc = CtlProc()
    ctl_proc.run()

    from sw import SwProc
    sw_proc = SwProc()
    sw_proc.run()

    # from renc import ReProc
    # re_proc = ReProc()
    # re_proc.run()

# main()
