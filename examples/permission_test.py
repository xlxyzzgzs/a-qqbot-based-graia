from graia.application.entry import GraiaMiraiApplication, GroupMessage, MessageChain, Plain, At, Quote, Source
from graia.application.event.lifecycle import ApplicationLaunched
from graia.broadcast import Broadcast
from graia.broadcast.builtin.decorators import Depend
from graia.broadcast.exceptions import ExecutionStop
import aiosqlite
import asyncio
import permission as permission_custom
from typing import NoReturn
from config import connection_config
import re
from functools import reduce
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


def regexPlain(param: str) -> callable:
    """
    used in headless_decotator
    """

    @Depend
    def func(messageChain: MessageChain):
        p = messageChain.get(Plain)
        for i in p:
            if not i.text.strip():
                continue
            t = re.fullmatch(param, i.text.strip())
            if t:
                return t
        else:
            raise ExecutionStop()

    return func


@bcc.receiver(ApplicationLaunched)
async def __init_database():
    await permission_custom.init_database()


# 使用 "#cs1" 命令
@bcc.receiver("GroupMessage", headless_decorators=[permission_custom.MessagePermissionCheckDecorator("perm1", "perm1", "perms"), startWith("#cs1")])
async def func1(app: GraiaMiraiApplication, event: GroupMessage):
    await app.sendGroupMessage(event.sender.group, MessageChain.create([Plain("have perm 1")]), quote=event.messageChain.getFirst(Source))


# 使用 "#cs2" 命令
@bcc.receiver("GroupMessage", dispatchers=[permission_custom.MessagePermissionCheckDispatcher(
    "allow", "perm2", "perm2", "perms")], headless_decorators=[startWith("#cs2")])
async def func2(app: GraiaMiraiApplication, event: GroupMessage, allow):
    if allow:
        await app.sendGroupMessage(event.sender.group, MessageChain.create([Plain("have perm 2")]), quote=event.messageChain.getFirst(Source))
    else:
        await app.sendGroupMessage(event.sender.group, MessageChain.create([Plain("not have perm 2")]), quote=event.messageChain.getFirst(Source))


# 使用 "#perm 被许可人ID  权限" 命令
@bcc.receiver("GroupMessage", headless_decorators=[permission_custom.MessagePermissionCheckDecorator(permission_custom.PermissionConfig.ROOT_PERMISSION_ID)])
async def func3(app: GraiaMiraiApplication, event: GroupMessage, regexResult=regexPlain(r"^#perm[\s]*(client[^\s\S]*|[futmg]\*|[fug][1-9][0-9]{4,}|[mt][1-9][0-9]{4,}\.(?:\*|[1-9][0-9]{4,}))[\s]*([\S]+)[\s]*$")):
    permittee = permission_custom.str_to_permittee(regexResult.group(1))
    permission = await permission_custom.get_permission(regexResult.group(2))
    await permission_custom.set_permission_with_permittee(regexResult.group(2), regexResult.group(1))
    await app.sendGroupMessage(event.sender.group, MessageChain.create([Plain("complete perm")]), quote=event.messageChain.getFirst(Source))

app.launch_blocking()
