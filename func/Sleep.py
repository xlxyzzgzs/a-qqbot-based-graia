from graia.application.entry import GraiaMiraiApplication, MemberPerm, GroupMessage
from graia.application.entry import MessageChain, Plain, Member, At, Source, Group
from graia.broadcast import Broadcast
from datetime import datetime
from typing import Union
import random
from utils import muteMember, getTargetFromAt
from utils.messageTrigger import strictPlainCommand
from utils.checkPermission import checkMemberPermission


def GenerateSleepTime():
    startTime = datetime.now()
    endTime = datetime(startTime.year, startTime.month, startTime.day, 7, 0, 0)
    if startTime.hour < 7:
        delta = (endTime - startTime).total_seconds()
    else:
        delta = 24 * 3600 - (startTime - endTime).total_seconds()
    delta //= 60
    random.gauss(delta, 30.0)
    return delta


async def Group_Member_Sleep(app: GraiaMiraiApplication, event: GroupMessage):
    quoted = event.messageChain.get(Source)[0]
    group = event.sender.group
    target = await getTargetFromAt(app, group, event.messageChain)
    if not target:
        target = [event.sender]
    elif not await checkMemberPermission(
        app, event.sender, [MemberPerm.Administrator, MemberPerm.Owner], quoted
    ):
        target = []
    for i in target:
        delta = GenerateSleepTime()
        if not await muteMember(app, group, i, delta, quoted):
            break
        await app.sendGroupMessage(
            group,
            MessageChain.create(
                [At(i.id), Plain(f"\n你的睡眠套餐已到账,请查收.\n总时长为{delta}分钟")]),
            quote=(quoted if i == event.sender else {}),
        )


def AddGroupSleepListener(bcc: Broadcast) -> None:
    bcc.receiver("GroupMessage", headless_decorators=[strictPlainCommand("#睡眠套餐")])(
        Group_Member_Sleep
    )
