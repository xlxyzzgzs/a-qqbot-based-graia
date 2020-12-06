from graia.application.entry import GraiaMiraiApplication, MemberPerm, GroupMessage
from graia.application.entry import (
    MemberJoinEvent,
    MessageChain,
    Plain,
    Member,
    At,
    Source,
)
from graia.broadcast import Broadcast
from utils.database import GetFromGroupInfoDB, UpdateGroupInfoDB
from utils.messageConvert import StrToMessageChain, MessageChainToStr
from utils.messageTrigger import startWith, strictPlainCommand
from utils.checkPermission import checkMemberPermission


async def GroupMemberJoin(app: GraiaMiraiApplication, event: MemberJoinEvent):
    message = GetFromGroupInfoDB(app, event.member.group, "MemberJoinMessage")
    if not message:
        message = MessageChain.create([At(event.member.id), Plain("欢迎入群")])
    else:
        message = StrToMessageChain(message)
        message.__root__.insert(0, At(event.member))
    await app.sendGroupMessage(event.member.group, message)


async def GroupUpdateMemberJoinMessage(app: GraiaMiraiApplication, event: GroupMessage):
    quoted = event.messageChain.get(Source)[0]
    if not await checkMemberPermission(
        app, event.sender, [MemberPerm.Administrator, MemberPerm.Owner], quoted
    ):
        return
    result = await MessageChainToStr(event.messageChain, "#更新入群词")
    if UpdateGroupInfoDB(app, event.sender.group, "MemberJoinMessage", result):
        await app.sendGroupMessage(
            event.sender.group, MessageChain.create([Plain("入群词更新成功.")]), quote=quoted
        )
    else:
        await app.sendGroupMessage(
            event.sender.group, MessageChain.create([Plain("入群词更新失败.")]), quote=quoted
        )


async def GroupNowMemberJoinMessage(app: GraiaMiraiApplication, event: GroupMessage):
    quoted = event.messageChain.get(Source)[0]
    message = GetFromGroupInfoDB(app, event.sender.group, "MemberJoinMessage")
    if message:
        message = StrToMessageChain(message)
    else:
        message = MessageChain.create([Plain("当前群没有入群词")])
    await app.sendGroupMessage(event.sender.group, message, quote=quoted)


def AddMemberJoinEventListener(bcc: Broadcast) -> None:
    bcc.receiver("MemberJoinEvent")(GroupMemberJoin)
    bcc.receiver("GroupMessage", headless_decoraters=[startWith("#更新入群词")])(
        GroupUpdateMemberJoinMessage
    )
    bcc.receiver("GroupMessage", headless_decoraters=[strictPlainCommand("#当前入群词")])(
        GroupNowMemberJoinMessage
    )
