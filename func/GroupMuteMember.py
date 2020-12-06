from graia.application.entry import (
    GraiaMiraiApplication,
    GroupMessage,
    Source,
    MemberPerm,
    MessageChain,
)
from graia.application.entry import Plain
from graia.broadcast import Broadcast
from utils.messageTrigger import regexPlain, strictPlainCommand
from utils.checkPermission import checkMemberPermission
from utils import muteMember, getTargetFromAt, unmuteMember, muteAll, unmuteAll


async def GroupMuteMember(
    app: GraiaMiraiApplication,
    event: GroupMessage,
    regexResult=regexPlain(r"^#禁言[\s]*([\d]*)$"),
):
    sender = event.sender
    group = sender.group
    quoted = event.messageChain.get(Source)[0]
    time = int(regexResult.groups()[0])
    if not await checkMemberPermission(
        app, sender, [MemberPerm.Owner, MemberPerm.Administrator], quoted
    ):
        return
    target = await getTargetFromAt(app, group, event.messageChain)
    for i in target:
        if not await muteMember(app, group, i, time, quoted):
            return
    await app.sendGroupMessage(
        group, MessageChain.create([Plain("操作完成.")]), quote=quoted
    )


async def GroupunmuteMember(app: GraiaMiraiApplication, event: GroupMessage):
    quoted = event.messageChain.get(Source)[0]
    if not await checkMemberPermission(
        app, event.sender, [MemberPerm.Owner, MemberPerm.Administrator], quoted
    ):
        return
    target = await getTargetFromAt(app, event.sender.group, event.messageChain)
    for i in target:
        if not await unmuteMember(app, event.sender.group, i, quoted):
            return
    await app.sendGroupMessage(
        event.sender.group, MessageChain.create([Plain("操作完成.")]), quote=quoted
    )


async def GroupMuteAll(app: GraiaMiraiApplication, event: GroupMessage):
    quoted = event.messageChain.get(Source)[0]
    if not await checkMemberPermission(
        app, event.sender, [MemberPerm.Owner, MemberPerm.Administrator], quoted
    ):
        return
    if await muteAll(app, event.sender.group, quoted):
        await app.sendGroupMessage(
            event.sender.group, MessageChain.create([Plain("操作完成.")]), quote=quoted
        )


async def GroupUnMuteAll(app: GraiaMiraiApplication, event: GroupMessage):
    quoted = event.messageChain.get(Source)[0]
    if not await checkMemberPermission(
        app, event.sender, [MemberPerm.Owner, MemberPerm.Administrator], quoted
    ):
        return
    if await unmuteAll(app, event.sender.group, quoted):
        await app.sendGroupMessage(
            event.sender.group, MessageChain.create([Plain("操作完成.")]), quote=quoted
        )


def AddGroupMuteMemberListener(bcc: Broadcast):
    bcc.receiver("GroupMessage")(GroupMuteMember)
    bcc.receiver("GroupMessage", headless_decoraters=[strictPlainCommand("#解除禁言")])(
        GroupunmuteMember
    )
    bcc.receiver("GroupMessage", headless_decoraters=[strictPlainCommand("#全体禁言")])(
        GroupMuteAll
    )
    bcc.receiver("GroupMessage", headless_decoraters=[strictPlainCommand("#解除全体禁言")])(
        GroupUnMuteAll
    )
