import uasyncio as asyncio
from machine import Pin
from util import *
from rotary_enc import RotaryEnc


PIN_RE_A_PH = 2
PIN_RE_B_PH = 4


async def proc_renc(snd_q=None, rcv_q=None):
    print("proc_renc:run")
    # init
    re = RotaryEnc(PIN_RE_A_PH, PIN_RE_B_PH)
    prev_position = 0


    # polling
    while True:
        await asyncio.sleep_ms(50)

        position = re.get_positon()
        if position != prev_position :
            print("re", str(position - prev_position), str(position))
            send_que(snd_q, ("dst:pre,src:renc,cmd:renc" + ",type:" + str(position) + ",chg_val:" + str(position - prev_position)))
            prev_position = position
    print("proc_renc:over")
    return


async def debug_main():
    que_pre_renc = []
    asyncio.create_task(proc_renc(snd_q=que_pre_renc, rcv_q=None))
    await asyncio.sleep_ms(10_000)
    return

def main():
    asyncio.run(debug_main())

if __name__ == "__main__":
    main()
