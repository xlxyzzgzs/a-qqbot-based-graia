from graia.application.entry import At, MessageChain, Plain, GroupMessage, Source
from graia.broadcast.builtin.decorators import Depend, DecoratorInterface, Decorator
from graia.broadcast.interfaces.dispatcher import DispatcherInterface, BaseDispatcher, IDispatcherInterface
from types import TracebackType
from graia.broadcast.exceptions import ExecutionStop
from functools import reduce
from typing import Any, NoReturn, Dict, Optional
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


class CoolDownDecorator(Decorator):
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


class CoolDownDispatcher(BaseDispatcher):
    always = True
    local_storage: Dict[Any, Any] = {}

    def __init__(self, cool_down_time: datetime.timedelta, cool_down_id: Any, target_name: str):
        self.cool_down_time = cool_down_time
        self.cool_down_id = cool_down_id
        self.cool_down_target = target_name
        self.result = False

    def beforeExecution(self, interface: IDispatcherInterface):
        last_time = self.local_storage.get(self.cool_down_id)
        time = datetime.datetime.today()
        if last_time and time - last_time <= self.cool_down_time:
            self.result = False
        else:
            self.result = True

    def afterExecution(self, interface: IDispatcherInterface, exception: Optional[Exception], tb: Optional[TracebackType]):
        if isinstance(exception, ExecutionStop):
            return
        self.result = False
        self.local_storage[self.cool_down_id] = datetime.datetime.today()

    async def catch(self, interface: DispatcherInterface):
        if self.cool_down_target and self.cool_down_target == interface.name:
            return self.result


@bcc.receiver("GroupMessage", headless_decorators=[startWith("f1"), CoolDownDecorator(datetime.timedelta(seconds=60), "f1")])
async def func1(app: GraiaMiraiApplication, event: GroupMessage):
    await app.sendGroupMessage(event.sender.group, MessageChain.create([Plain("do func1")]), quote=event.messageChain.get(Source)[0])


@bcc.receiver("GroupMessage", dispatchers=[CoolDownDispatcher(datetime.timedelta(seconds=60), "f2", "cool")], headless_decorators=[startWith("f2")])
async def func1(app: GraiaMiraiApplication, event: GroupMessage, cool):
    if cool:
        await app.sendGroupMessage(event.sender.group, MessageChain.create([Plain("do func2")]), quote=event.messageChain.get(Source)[0])
    else:
        await app.sendGroupMessage(event.sender.group, MessageChain.create([Plain("func2 in cooling")]), quote=event.messageChain.get(Source)[0])

app.launch_blocking()
