from graia.application.entry import (
    GraiaMiraiApplication,
    GroupMessage,
    Source,
    MessageChain,
    Member,
    MemberPerm,
)
from graia.application.entry import Plain, MemberJoinRequestEvent
from graia.broadcast import Broadcast
from utils.checkPermission import checkMemberPermission
from utils.database import (
    InsertToGroupDB,
    DeleteFromGroupDB,
    GetAllFromGroupDB,
    GetMemberStatusFromGrouBlockDB,
    CheckIfInGroupDB,
)
from utils.messageTrigger import regexPlain, strictPlainCommand


async def GroupAddAnswer(
    app: GraiaMiraiApplication,
    event: GroupMessage,
    regexResult=regexPlain(r"^#添加进群答案[\s]*([^\s]*)$"),
):
    quoted = event.messageChain.get(Source)[0]
    if not await checkMemberPermission(
        app, event.sender, [MemberPerm.Administrator, MemberPerm.Owner], quoted
    ):
        return
    answer = regexResult.groups()[0]
    if not answer:
        return
    if InsertToGroupDB(app, event.sender.group, "GroupAnswer", "Answer", answer):
        await app.sendGroupMessage(
            event.sender.group, MessageChain.create([Plain("答案添加成功")]), quote=quoted
        )
    else:
        await app.sendGroupMessage(
            event.sender.group,
            MessageChain.create([Plain("答案添加失败,原因不明.")]),
            quote=quoted,
        )


async def GroupDeleteAnswer(
    app: GraiaMiraiApplication,
    event: GroupMessage,
    regexResult=regexPlain(r"^#删除进群答案[\s]*([^\s]*)$"),
):
    quoted = event.messageChain.get(Source)[0]
    if not await checkMemberPermission(
        app, event.sender, [MemberPerm.Administrator, MemberPerm.Owner], quoted
    ):
        return
    answer = regexResult.groups()[0]
    if not answer:
        return
    if DeleteFromGroupDB(app, event.sender.group, "GroupAnswer", "Answer", answer):
        await app.sendGroupMessage(
            event.sender.group, MessageChain.create([Plain("答案删除成功")]), quote=quoted
        )
    else:
        await app.sendGroupMessage(
            event.sender.group, MessageChain.create([Plain("答案删除失败")]), quote=quoted
        )


async def GroupAllowAnswer(app: GraiaMiraiApplication, event: GroupMessage):
    quoted = event.messageChain.get(Source)[0]
    answer = GetAllFromGroupDB(app, event.sender.group, "GroupAnswer", "Answer")
    answer = "\n".join(map(lambda ans: ans[0], answer))
    await app.sendGroupMessage(
        event.sender.group,
        MessageChain.create([Plain("可用的进群答案为:\n" + answer)]),
        quote=quoted,
    )


async def MemberJoinRequest(app: GraiaMiraiApplication, event: MemberJoinRequestEvent):
    group = await app.getGroup(event.groupId)
    target = Member(
        id=event.supplicant,
        group=group,
        permission=MemberPerm.Member,
        memberName=event.nickname,
    )
    if GetMemberStatusFromGrouBlockDB(app, group, target, "Blocked"):
        await event.reject("你在群组的黑名单之中")
    answer = event.message.strip().splitlines()[1][3:]
    if not CheckIfInGroupDB(app, group, "GroupAnswer", "Answer", answer):
        return
    await event.accept("答案看上去没啥大问题.")
    await app.sendGroupMessage(
        group,
        MessageChain.create([Plain(event.nickname + "申请加群,答案为:" + answer + "\n已通过")]),
    )


def AddGroupAnswerListener(bcc: Broadcast):
    bcc.receiver("GroupMessage")(GroupAddAnswer)
    bcc.receiver("GroupMessage")(GroupDeleteAnswer)
    bcc.receiver("GroupMessage", headless_decoraters=[strictPlainCommand("#可用进群答案")])(
        GroupAllowAnswer
    )
    bcc.receiver("MemberJoinRequestEvent")(MemberJoinRequest)
