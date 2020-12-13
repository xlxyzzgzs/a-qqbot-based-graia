from graia.application.entry import MessageChain, Friend, FriendMessage, Plain
from graia.broadcast import Broadcast
from graia.broadcast.interrupt import InterruptControl
from graia.broadcast.interrupt.waiter import Waiter
import asyncio
import random
event_loop = asyncio.get_event_loop()
bcc = Broadcast(loop=event_loop)
inc = InterruptControl(bcc)


class ReturnValue(Exception):
    def __init__(self, value):
        self.ReturnValue = value


async def RequestBoard(need_id: int):
    need_id = need_id
    try:
        @Waiter.create_using_function([FriendMessage])
        def wait(wait_event: FriendMessage):
            if wait_event.sender.id != need_id:
                return None
            return wait_event
        wait_task = asyncio.ensure_future(inc.wait(wait))
        print(f"wait for {need_id}")
        result = await asyncio.gather(wait_task)
        raise ReturnValue(result)
    except asyncio.CancelledError:
        print(f"cancel {need_id}")


@bcc.receiver("FriendMessage")
async def listener(event: FriendMessage):
    if event.sender.id != 0:
        return
    tasks = []
    print("start listener")
    for _ in range(10, 20):
        tasks.append(asyncio.ensure_future(RequestBoard(_)))
    try:
        await asyncio.gather(*tasks)
    except ReturnValue as result:
        for _ in tasks:
            _.cancel()
        print(result.ReturnValue)


async def main():
    print(len(inc.broadcast.listeners))
    friend = FriendMessage(messageChain=MessageChain.create(
        [Plain(f"this event{0}")]), sender=Friend(id=0, nickname="nickname", remark="remark"))
    bcc.postEvent(friend)
    while True:
        friendId = random.randint(1, 19)
        friend = FriendMessage(messageChain=MessageChain.create(
            [Plain(f"this event{friendId}")]), sender=Friend(id=friendId, nickname="nickname", remark="remark"))
        bcc.postEvent(friend)
        await asyncio.sleep(1)
        if friendId >= 10:
            break
    print(f"{friendId} send and leave postevent")
    await asyncio.sleep(10)
    print(len(inc.broadcast.listeners))

event_loop.run_until_complete(asyncio.wait([main()]))
