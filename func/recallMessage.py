from graia.application.entry import GraiaMiraiApplication, GroupMessage, Source
from graia.application.entry import MemberPerm, MessageChain, Quote, Plain
from graia.broadcast import Broadcast
from utils.checkPermission import checkMemberPermission, checkBotPermission
from utils.messageTrigger import strictPlainCommand


async def GroupRecallOtherMessage(app: GraiaMiraiApplication, event: GroupMessage):
    quoted = event.messageChain.get(Source)[0]
    if not await checkMemberPermission(
        app, event.sender, [MemberPerm.Administrator, MemberPerm.Owner], quoted
    ):
        return
    target = event.messageChain.get(Quote)[0]
    member = await app.getMember(target.targetId, target.senderId)

    if not await checkBotPermission(
        app,
        event.sender.group,
        [
            MemberPerm.Owner,
            *(
                [MemberPerm.Administrator]
                if member.permission == MemberPerm.Member
                else []
            ),
        ],
    ):
        return
    await app.revokeMessage(target.origin.get(Source)[0])

    result = False
    member = event.sender
    if event.sender.group.accountPerm in [
        MemberPerm.Owner,
        *([MemberPerm.Administrator] if member.permission ==
          MemberPerm.Member else []),
    ]:
        await app.revokeMessage(event.messageChain.get(Source)[0])
        result = True
    await app.sendGroupMessage(
        event.sender.group,
        MessageChain.create(
            [Plain("撤回消息成功"), *([] if result else [Plain("\n记得撤回自己的消息")])]
        ),
        quote=quoted,
    )


def AddRecallMessageListener(bcc: Broadcast):
    bcc.receiver("GroupMessage", headless_decorators=[strictPlainCommand("#撤回")])(
        GroupRecallOtherMessage
    )
