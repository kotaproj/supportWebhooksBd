from ifttt_evt import KEY_TO_EVENTID

def conv_msg2dict(msg):
    # input : "a:b,c:d"
    # output: {"a":"b","c":"d"}
    d = {}
    for item in msg.split(','):
        key, val = item.split(':')
        d[key] = val
    return d

def conv_typ2eventid(typ, how):
    if typ in KEY_TO_EVENTID:
        return KEY_TO_EVENTID[typ][how]
    return None

def str2bool(s):
    return s.lower() in ["true", "t", "yes", "1"]
