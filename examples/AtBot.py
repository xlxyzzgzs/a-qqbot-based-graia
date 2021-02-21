from graia.application.entry import At, MessageChain, Plain, GroupMessage, Source
from graia.broadcast.builtin.decorators import Depend
from graia.broadcast.exceptions import ExecutionStop
from functools import reduce
from typing import NoReturn
from graia.application.entry import GraiaMiraiApplication
from graia.broadcast import Broadcast
import asyncio
from config import connection_config, BotQQ


def AtBot(param: int) -> callable:
    """
    used in headless_decotator
    """

    @Depend
    def func(messageChain: MessageChain) -> NoReturn:
        p = messageChain.get(At)
        if not p or not reduce(
            lambda a, b: bool(a or b),
            map(lambda at: at.target == param, p),
            False
        ):
            raise ExecutionStop()

    return func


loop = asyncio.get_event_loop()
bcc = Broadcast(loop=loop)
app = GraiaMiraiApplication(
    broadcast=bcc, connect_info=connection_config(), enable_chat_log=True, debug=False
)


@bcc.receiver("GroupMessage", headless_decorators=[AtBot(BotQQ)])
async def temp(app: GraiaMiraiApplication, event: GroupMessage):
    await app.sendGroupMessage(event.sender.group, MessageChain.create([Plain("找我啥事？")]), quote=event.messageChain.get(Source)[0])

app.launch_blocking()
