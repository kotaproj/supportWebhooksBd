# 通知とIFTTT-Webhookイベントの紐づけ
#  - cmd:sw,type:no1,how:released" => sw1をイベントIDとしてIFTTTにリクエスト
KEY_TO_EVENTID = {
    "no1" : {
        "pressed" : None,
        "released" : "sw1",
        "long" : "long_sw1",
    },
    "no2" : {
        "pressed" : None,
        "released" : "sw2",
        "long" : "long_sw2",
    },
    "no3" : {
        "pressed" : None,
        "released" : "sw3",
        "long" : "long_sw3",
    },
}

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

def send_que(lock, que, value):
    if que is None:
        print("Error:que is None.")
        return
    # lock
    lock_p = lock.acquire(1, -1) #wait forever
    if not lock_p:
        print("Error:task can not get the lock.")
    else:
        que.append(value)
        lock.release()
    # unlock
    return

def recv_que(lock, que):
    if que is None:
        print("Error:que is None.")
        return

    val = None

    # lock
    lock_p = lock.acquire(1, -1) #wait forever
    if not lock_p:
        print("Error:task can not get the lock.")
    else:
        if len(que) > 0:
            val = que[0]
            del que[0]
        lock.release()
    # unlock
    return val