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


def send_que(que, value, lock=None):
    if que is None:
        return
    que.append(value)
    return

def recv_que(que, lock=None):
    val = None
    if len(que) > 0:
        val = que[0]
        del que[0]
    return val
