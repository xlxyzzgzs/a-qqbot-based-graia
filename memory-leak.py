from graia.application.entry import GroupMessage, MessageChain
from graia.application.entry import Plain, Member, Group, MemberPerm
from graia.broadcast import Broadcast
from graia.broadcast.builtin.decoraters import Depend
from graia.broadcast.exceptions import ExecutionStop
from graia.application.entry import GraiaMiraiApplication, Session
from config import connection_config
import random
import asyncio
from graia.application.context import enter_context

loop = asyncio.get_event_loop()
bcc = Broadcast(loop=loop)
app = GraiaMiraiApplication(
    broadcast=bcc,
    connect_info=Session(
        host="http://127.0.0.1:7777",
        authKey="mirai-api-http-token",
        account=123456789,
        websocket=True,
    ),
    enable_chat_log=True,
    debug=True,
)


def warpper(num):
    def func1(message: MessageChain):
        if num < 9000:
            raise ExecutionStop()
        print(f"In headless:{num}")
        return num

    return func1


def generator(num):
    async def func2(
        message: MessageChain,
        event: GroupMessage,
    ):
        print(f"In listener:{num} ")
        # if(num>90000):

    return func2


for _ in range(30):
    bcc.receiver(
        "GroupMessage", headless_decoraters=[Depend(warpper(random.randint(0, 10000)))]
    )(generator(random.randint(0, 100000)))
print("reciver added")


async def main():
    for _ in range(10000000):
        group = GroupMessage(
            messageChain=MessageChain.create(
                [
                    Plain(f"test{random.randint(0,1000000)}"),
                ]
            ),
            sender=Member(
                id=123456,
                memberName="tempNember",
                permission=MemberPerm.Member,
                group=Group(
                    id=123456789, name="tempGroup", permission=MemberPerm.Member
                ),
            ),
        )
        with enter_context(app=app, event_i=group):
            bcc.postEvent(group)
        await asyncio.sleep(0.1)
    await asyncio.sleep(100000)


loop.run_until_complete(asyncio.wait([main()]))
