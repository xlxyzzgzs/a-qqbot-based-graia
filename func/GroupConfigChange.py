from graia.application.entry import GraiaMiraiApplication,BotGroupPermissionChangeEvent,MessageChain,Plain
from graia.application.entry import GroupNameChangeEvent,GroupEntranceAnnouncementChangeEvent,GroupMuteAllEvent
from graia.application.entry import GroupAllowAnonymousChatEvent,GroupAllowConfessTalkEvent,MemberPerm
from graia.broadcast import Broadcast
from utils import GroupSettingChanged

async def GroupPermissionChange(app:GraiaMiraiApplication,event:BotGroupPermissionChangeEvent):
    if event.origin==event.current:
        await app.sendGroupMessage(event.group,MessageChain.create([
            Plain("为啥会发出这句?这是发生了啥?我不知道,不要问我.")
        ]))
    elif event.current==MemberPerm.Member:
        await app.sendGroupMessage(event.group,MessageChain.create([
            Plain("哦豁,管理权限没了.")
        ]))
    elif event.current==MemberPerm.Administrator:
        await app.sendGroupMessage(event.group,MessageChain.create([
            Plain("权限升级,功能升级(雾)")
        ]))
    elif event.current==MemberPerm.Owner:
        await app.sendGroupMessage(event.group,MessageChain.create([
            Plain("我咋成群主了?发生了啥?")
        ]))
    else :
        await app.sendGroupMessage(event.group,MessageChain.create([
            Plain("为啥会发出这句?这是发生了啥?我不知道,不要问我.")
        ]))

async def GroupNameChange(app:GraiaMiraiApplication,event:GroupNameChangeEvent):
    if event.isByBot:
        return 
    await app.sendGroupMessage(event.group,MessageChain.create([
        Plain("这是发生了啥?为啥要改群名?")
    ]))

async def GroupEntranceAnnouncementChange(app:GraiaMiraiApplication,event:GroupEntranceAnnouncementChangeEvent):
    await app.sendGroupMessage(event.group,MessageChain.create([
        Plain("本群的入群公告改了哦,记得去看看."),
        (Plain("\n此处应有@全体") if event.group.accountPerm in [MemberPerm.Owner,MemberPerm.Administrator] else Plain("\n既然不具备权限就不@全体了"))
    ]))


async def GroupMuteAll(app:GraiaMiraiApplication,event:GroupMuteAllEvent):
    if not event.group.accountPerm in [MemberPerm.Administrator,MemberPerm.Owner]:
        return
    else:
        await GroupSettingChanged(app,event,
            enable=MessageChain.create([
                Plain("看誰还再跳,这不,被开全体禁言了吧.")
            ]),
            disable=MessageChain.create([
                Plain("这里我们赢感谢管理大大(大雾)")
            ]),
            invalid=MessageChain.create([
                Plain("为啥会发出这句?这是发生了啥?我不知道,不要问我.")
            ]))
    

async def GroupAnonymousChat(app:GraiaMiraiApplication,event:GroupAllowAnonymousChatEvent):
    await GroupSettingChanged(app,event,
        enable=MessageChain.create([
            Plain("突然开始允许匿名聊天?")
        ]),
        disable=MessageChain.create([
            Plain("匿名聊天被关了..")
        ]),
        invalid=MessageChain.create([
            Plain("为啥会发出这句?这是发生了啥?我不知道,不要问我.")
        ]))

async def GroupConfessTalk(app:GraiaMiraiApplication,event:GroupAllowConfessTalkEvent):
    await GroupSettingChanged(app,event,
        enable=MessageChain.create([
            Plain("坦白说开启了?有人要用吗?")
        ]),
        disable=MessageChain.create([
            Plain("坦白说被关了.需要的等下次开启吧.")
        ]),
        invalid=MessageChain.create([
            Plain("为啥会发出这句?这是发生了啥?我不知道,不要问我.")
        ]))

def AddGroupConfigChangeListener(bcc:Broadcast):
    bcc.receiver("BotGroupPermissionChangeEvent")(GroupPermissionChange)
    bcc.receiver("GroupNameChangeEvent")(GroupNameChange)
    bcc.receiver("GroupEntranceAnnouncementChangeEvent")(GroupEntranceAnnouncementChange)
    bcc.receiver("GroupMuteAllEvent")(GroupMuteAll)
    bcc.receiver("GroupAllowAnonymousChatEvent")(GroupAnonymousChat)
    bcc.receiver("GroupAllowConfessTalkEvent")(GroupConfessTalk)
