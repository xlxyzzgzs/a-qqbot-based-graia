from graia.application.entry import At, MessageChain, Plain, GroupMessage, Source
from graia.broadcast.builtin.decorators import Depend, DecoratorInterface, Decorator
from graia.broadcast.exceptions import ExecutionStop
from functools import reduce
from typing import Any, NoReturn
from graia.application.entry import GraiaMiraiApplication
from graia.broadcast import Broadcast
import asyncio
from config import connection_config, BotQQ
import datetime

loop = asyncio.get_event_loop()
bcc = Broadcast(loop=loop)
app = GraiaMiraiApplication(
    broadcast=bcc, connect_info=connection_config(), enable_chat_log=True, debug=False
)


def startWith(param: str) -> callable:
    """
    used in headless_decotator
    """

    @Depend
    def func(messageChain: MessageChain) -> NoReturn:
        p = messageChain.get(Plain)
        if not p or not reduce(
            lambda a, b: bool(a or b),
            map(lambda plain: plain.text.strip().startswith(param), p),
        ):
            raise ExecutionStop()

    return func


class CoolDown(Decorator):
    pre = True
    cool_down_time: datetime.timedelta
    cool_down_id: Any

    def __init__(self, cool_down_time: datetime.timedelta, cool_down_id: Any):
        self.cool_down_time = cool_down_time
        self.cool_down_id = cool_down_id

    def target(self, interface: DecoratorInterface):
        last_time = interface.local_storage.get(self.cool_down_id)
        time = datetime.datetime.today()
        if last_time and time - last_time <= self.cool_down_time:
            raise ExecutionStop()
        interface.local_storage[self.cool_down_id] = time
        return True


@bcc.receiver("GroupMessage", headless_decorators=[startWith("f1"), CoolDown(datetime.timedelta(seconds=60), "f1")])
async def func1(app: GraiaMiraiApplication, event: GroupMessage):
    await app.sendGroupMessage(event.sender.group, MessageChain.create([Plain("func1")]), quote=event.messageChain.get(Source)[0])


@bcc.receiver("GroupMessage", headless_decorators=[startWith("f2"), CoolDown(datetime.timedelta(seconds=60), "f1")])
async def func1(app: GraiaMiraiApplication, event: GroupMessage):
    await app.sendGroupMessage(event.sender.group, MessageChain.create([Plain("func2")]), quote=event.messageChain.get(Source)[0])

app.launch_blocking()
