import uasyncio as asyncio
import uheapq as heapq

from util import conv_msg2dict

async def proc_presenter(snd_ques=None, rcv_ques=None):

    print("proc_presenter:run")

    def command_sw(msg):
        print("pre_command_sw:run")
        d = conv_msg2dict(msg)
        print(d)
        heapq.heappush(snd_ques["httpc"], ("dst:httpc,src:pre,cmd:sw,type:"+d["type"]+",how:"+d["how"]))
        return

    def command_dsp(msg):
        print("pre_command_dsp:run")
        msg = msg.replace("dst:pre,src:httpc,", "dst:dsp,src:pre,")
        heapq.heappush(snd_ques["dsp"], msg)
        print("pre_command_dsp:over")
        return

    def command_led(msg):
        print("pre_command_led:run")
        msg = msg.replace("dst:pre,src:httpc,", "dst:led,src:pre,")
        heapq.heappush(snd_ques["led"], msg)
        print("pre_command_led:over")
        return

    while True:
        # recvive_que
        for key, rcv_q in rcv_ques.items():
            try:
                msg = heapq.heappop(rcv_q)
            except IndexError:
                # print("IndexError")
                continue
            print("proc_presenter:msg - ", msg)
            command = conv_msg2dict(msg)['cmd']
            if "sw" == command:
                command_sw(msg)
            elif "dsp" == command:
                command_dsp(msg)
            elif "led" == command:
                command_led(msg)
            elif "dummy" == command:
                pass
            else:
                print("proc_presenter:error - ", msg)

            # moji = "pre_" + msg
            # heapq.heappush(snd_ques["output"], moji)
        await asyncio.sleep_ms(10)


async def debug_main():
    from sw import proc_sw
    que_sw2pre = []
    asyncio.create_task(proc_sw(snd_q=que_sw2pre, rcv_q=None))

    from led import proc_led
    que_pre2led = []
    asyncio.create_task(proc_led(snd_q=None, rcv_q=que_pre2led))

    que_snds = {
        "led" : que_pre2led,
    }
    que_rcvs = {
        "sw" : que_sw2pre,
    }

    que_pre_sw = []
    asyncio.create_task(proc_presenter(que_snds, que_rcvs))

    await asyncio.sleep_ms(10_000)
    return

def main():
    asyncio.run(debug_main())

if __name__ == "__main__":
    main()
