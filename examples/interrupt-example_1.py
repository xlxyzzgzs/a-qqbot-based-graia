from graia.application.entry import MessageChain, Group, GroupMessage, MemberPerm, Member, Plain
from graia.broadcast import Broadcast
from graia.broadcast.interrupt import InterruptControl
from graia.broadcast.interrupt.waiter import Waiter
import asyncio
import random
event_loop = asyncio.get_event_loop()
bcc = Broadcast(loop=event_loop)
inc = InterruptControl(bcc)


@bcc.receiver("GroupMessage")
async def interrupt_example(event: GroupMessage):
    if event.messageChain.get(Plain)[0].text.startswith("/begin"):
        @Waiter.create_using_function([FriendMessage])
        def wait(wait_event: GroupMessage):
