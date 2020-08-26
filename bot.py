from graia.application.entry import *
from graia.broadcast import Broadcast
from graia.broadcast.builtin.decoraters import Depend
from graia.broadcast.exceptions import ExecutionStop
from graia.application.message.elements import InternalElement,ExternalElement
from graia.application.event.lifecycle import *
import asyncio
from typing import *
from datetime import *
import random
from functools import reduce
from sf_utils import *
import httpx
from config import connection_config
from graia.application.interrupt import InterruptControl
from graia.application.interrupt.interrupts import *
from NeteaseCloudMusic import SearchSongsInNeteaseCloudMusic


loop=asyncio.get_event_loop()
bcc=Broadcast(loop=loop)
app=GraiaMiraiApplication(
    broadcast=bcc,
    connect_info=connection_config()
)

@bcc.receiver(ApplicationLaunched)
async def t1(app:GraiaMiraiApplication):
    await InitGroupDataBase(app)

@bcc.receiver("GroupMessage",headless_decoraters=[Depend(strictPlainCommand('#睡眠套餐'))])
async def Group_Member_Sleep(app:GraiaMiraiApplication,event:GroupMessage):
    quoted=event.messageChain.get(Source)[0]
    group=event.sender.group

    startTime=datetime.now()
    endTime=datetime(startTime.year,startTime.month,startTime.day,7,0,0)
    if startTime.hour<7:
        delta=(endTime-startTime).total_seconds()
    else :
        delta=24*3600-(startTime-endTime).total_seconds()
    delta//=60
    random.gauss(delta,30.0)
    target=await getTargetFromAt(app,group,event.messageChain)
    if not target:
        target=[event.sender]
    elif not await checkMemberPermission(app,event.sender,[MemberPerm.Administrator,MemberPerm.Owner],quoted):
        target=[]
        
    for i in target:
        if not await muteMember(app,group,i,delta,quoted):
            break
        await app.sendGroupMessage(group,MessageChain.create([
            At(i.id),
            Plain(f"\n你的睡眠套餐已到账,请查收.\n总时长为{delta}分钟")
        ]),quote=(quoted if i==event.sender else {}))

@bcc.receiver("GroupMessage")
async def GroupAddAnswer(app:GraiaMiraiApplication,event:GroupMessage,regexResult=Depend(regexPlain(r'^#添加进群答案[\s]*([^\s]*)$'))):
    quoted=event.messageChain.get(Source)[0]
    if not await checkMemberPermission(app,event.sender,[MemberPerm.Administrator,MemberPerm.Owner],quoted):
        return 
    answer=regexResult.groups()[0]
    if not answer:
        return
    if InsertToGroupDB(event.sender.group,"GroupAnswer","Answer",answer):
        await app.sendGroupMessage(event.sender.group,MessageChain.create([
            Plain("答案添加成功")
        ]),quote=quoted)
    else :
        await app.sendGroupMessage(event.sender.group,MessageChain.create([
            Plain("答案添加失败,原因不明.")
        ]),quote=quoted)

@bcc.receiver("GroupMessage")
async def GroupDeleteAnswer(app:GraiaMiraiApplication,event:GroupMessage,regexResult=Depend(regexPlain(r'^#删除进群答案[\s]*([^\s]*)$'))):
    quoted=event.messageChain.get(Source)[0]
    if not await checkMemberPermission(app,event.sender,[MemberPerm.Administrator,MemberPerm.Owner],quoted):
        return 
    answer=regexResult.groups()[0]
    if not answer:
        return
    if DeleteFromGroupDB(event.sender.group,"GroupAnswer","Answer",answer):
        await app.sendGroupMessage(event.sender.group,MessageChain.create([
            Plain("答案删除成功")
        ]),quote=quoted)
    else :
        await app.sendGroupMessage(event.sender.group,MessageChain.create([
            Plain("答案删除失败")
        ]),quote=quoted)

@bcc.receiver("GroupMessage",headless_decoraters=[Depend(strictPlainCommand("#可用进群答案"))])
async def GroupAllowAnswer(app:GraiaMiraiApplication,event:GroupMessage):
    quoted=event.messageChain.get(Source)[0]
    answer=GetAllFromGroupDB(event.sender.group,"GroupAnswer","Answer")
    answer='\n'.join(map(lambda ans: ans[0],answer))
    await app.sendGroupMessage(event.sender.group,MessageChain.create([
        Plain("可用的进群答案为:\n"+answer)
    ]),quote=quoted)


@bcc.receiver("GroupMessage",headless_decoraters=[Depend(strictPlainCommand('#添加管理员'))])
async def GroupAddAdmin(app:GraiaMiraiApplication,event:GroupMessage):
    quoted=event.messageChain.get(Source)[0]
    if not await checkMemberPermission(app,event.sender,[MemberPerm.Administrator,MemberPerm.Owner],quoted):
        return
    target=set(map(lambda at: at.target,event.messageChain.get(At)))
    succ_result=[]
    fail_result=[]
    for i in target:
        if InsertToGroupDB(event.sender.group,'GroupPermission','AdminID',i):
            succ_result.append(At(i))
        else :
            fail_result.append(At(i))
    await app.sendGroupMessage(event.sender.group,MessageChain.create([
        Plain("操作完成\n以下成员获取权限成功:\n"),*succ_result,
        Plain("\n以下成员获取权限失败:\n"),*fail_result
    ]),quote=quoted)

@bcc.receiver("GroupMessage",headless_decoraters=[Depend(strictPlainCommand('#解除管理员'))])
async def GroupRemoveAdmin(app:GraiaMiraiApplication,event:GroupMessage):
    quoted=event.messageChain.get(Source)[0]
    if not await checkMemberPermission(app,event.sender,[MemberPerm.Administrator,MemberPerm.Owner],quoted):
        return
    target=set(map(lambda at: at.target,event.messageChain.get(At)))
    succ_result=[]
    fail_result=[]
    for i in target:
        if DeleteFromGroupDB(event.sender.group,'GroupPermission','AdminID',i):
            succ_result.append(At(i))
        else :
            fail_result.append(At(i))
    await app.sendGroupMessage(event.sender.group,MessageChain.create([
        Plain("操作完成\n以下成员取消权限成功:\n"),*succ_result,
        Plain("\n以下成员取消权限失败:\n"),*fail_result
    ]),quote=quoted)

@bcc.receiver("GroupMessage",headless_decoraters=[Depend(strictPlainCommand("#当前管理员"))])
async def GroupAvailableAdmin(app:GraiaMiraiApplication,event:GroupMessage):
    quoted=event.messageChain.get(Source)[0]
    admin=GetAllFromGroupDB(event.sender.group,"GroupPermission","AdminID")
    admin='\n'.join(map(lambda ad:str(ad[0]) ,admin))
    await app.sendGroupMessage(event.sender.group,MessageChain.create([
        Plain("可用的管理为:\n"+admin)
    ]),quote=quoted)

@bcc.receiver("GroupMessage")
async def Group_Mute_Member(app:GraiaMiraiApplication,event:GroupMessage,regexResult=Depend(regexPlain(r'^#禁言[\s]*([\d]*)$'))):
    sender=event.sender
    group=sender.group
    quoted=event.messageChain.get(Source)[0]
    time=int(regexResult.groups()[0])
    if not await checkMemberPermission(app,sender,[MemberPerm.Owner,MemberPerm.Administrator],quoted):
        return
    target =await getTargetFromAt(app,group,event.messageChain)
    for i in target:
        if not await muteMember(app,group,i,time,quoted):
            return 
    await app.sendGroupMessage(group,MessageChain.create([
        Plain("操作完成.")
    ]),quote=quoted)

@bcc.receiver("GroupMessage")
async def Group_UnMute_Member(app:GraiaMiraiApplication,event:GroupMessage,regexResult=Depend(strictPlainCommand("#解除禁言"))):
    quoted=event.messageChain.get(Source)[0]
    if not await checkMemberPermission(app,event.sender,[MemberPerm.Owner,MemberPerm.Administrator],quoted):
        return
    target =await getTargetFromAt(app,event.sender.group,event.messageChain)
    for i in target:
        if not await unMuteMember(app,event.sender.group,i,quoted):
            return 
    await app.sendGroupMessage(event.sender.group,MessageChain.create([
        Plain("操作完成.")
    ]),quote=quoted)

@bcc.receiver("GroupMessage",headless_decoraters=[Depend(startWith("#更新入群词"))])
async def GroupUpdateMemberJoinMessage(app:GraiaMiraiApplication,event:GroupMessage):
    quoted=event.messageChain.get(Source)[0]
    if not await checkMemberPermission(app,event.sender,[MemberPerm.Administrator,MemberPerm.Owner],quoted):
        return
    result= await MessageChainToStr(event.messageChain,"#更新入群词")
    if UpdateGroupInfoDB(event.sender.group,"MemberJoinMessage",result):
        await app.sendGroupMessage(event.sender.group,MessageChain.create([
            Plain("入群词更新成功.")
        ]),quote=quoted)
    else:
        await app.sendGroupMessage(event.sender.group,MessageChain.create([
            Plain("入群词更新失败.")
        ]),quote=quoted)

@bcc.receiver("GroupMessage",headless_decoraters=[Depend(strictPlainCommand("#当前入群词"))])
async def GroupNowMemberJoinMessage(app:GraiaMiraiApplication,event:GroupMessage):
    quoted=event.messageChain.get(Source)[0]
    message=GetFromGroupInfoDB(event.sender.group,"MemberJoinMessage")
    if message:
        message=StrToMessageChain(message)
    else :
        message=MessageChain.create([
            Plain("当前群没有入群词")
        ])
    await app.sendGroupMessage(event.sender.group,message,quote=quoted)

@bcc.receiver("GroupMessage",headless_decoraters=[Depend(startWith("#添加群语录"))])
async def GroupAddSentence(app:GraiaMiraiApplication,event:GroupMessage):
    quoted=event.messageChain.get(Source)[0]
    message= await MessageChainToStr(event.messageChain,"#添加群语录")
    SentenceID=GetFromGroupInfoDB(event.sender.group,"SentenceID")
    SentenceID+=1
    reply=[]
    if InsertGroupSentenceIntoDB(event.sender.group,message,SentenceID):
        if UpdateGroupInfoDB(event.sender.group,"SentenceID",SentenceID):
            reply=[Plain(f"语录插入成功,ID为{SentenceID}")]
        else :
            if not DeleteSentenceById(event.sender.group,SentenceID):
                reply=[Plain("发生了某些未知问题,建议去寻找管理")]
    else:
        reply=[Plain("语录插入失败")]
    await app.sendGroupMessage(event.sender.group,MessageChain.create(reply),quote=quoted)
    
@bcc.receiver("GroupMessage")
async def GroupShowSentence(app:GraiaMiraiApplication,event:GroupMessage,regexResult=Depend(regexPlain(r"^#群语录[\s]*([\d][\d]*)$"))):
    quoted=event.messageChain.get(Source)[0]
    SentenceID=int(regexResult.groups()[0])
    result=GetSentenceFromDBById(event.sender.group,SentenceID)
    if result:
        result=StrToMessageChain(result)
    else :
        result=MessageChain.create([
            Plain(f"ID为{SentenceID}的语录不存在")
        ])
    await app.sendGroupMessage(event.sender.group,result,quote=quoted)

@bcc.receiver("GroupMessage")
async def GroupDeleteMessage(app:GraiaMiraiApplication,event:GroupMessage,regexResult=Depend(regexPlain(r"^#删除语录[\s]*([\d]*)"))):
    quoted=event.messageChain.get(Source)[0]
    SentenceID=int(regexResult.groups()[0])
    message=GetSentenceFromDBById(event.sender.group,SentenceID)
    if message:
        message=StrToMessageChain(message)
    else:
        message=MessageChain.create([])
    if DeleteSentenceById(event.sender.group,SentenceID):
        message.__root__.insert(0,Plain("语录删除成功,原内容为:\n"))
    else :
        message.__root__.insert(0,Plain("语录删除失败"))
    await app.sendGroupMessage(event.sender.group,message,quote=quoted)

@bcc.receiver("GroupMessage")
async def Group_Ask_Daanshu(app:GraiaMiraiApplication,event:GroupMessage,regexResult=Depend(regexPlain(r"^#神启[\s]*([^\s]*)$"))):
    queted=event.messageChain.get(Source)[0]
    url="https://www.daanshu.com/"
    question=regexResult.groups()[0]
    if not question:
        return 
    question={"text":question}
    async with httpx.AsyncClient() as client:
        r=await client.post(url,data=question)
    parser=daanshuHtmlParser()
    parser.feed(r.text)
    parser.close()
    await app.sendGroupMessage(event.sender.group,MessageChain.create([
        Plain(parser.result.strip())
    ]),quote=queted)

@bcc.receiver("GroupMessage")
async def GroupNeteaseMusic(app:GraiaMiraiApplication,event:GroupMessage,regexResult=Depend(regexPlain(r'^#网易云音乐[\s]*(.*)$'))):
    quoted=event.messageChain.get(Source)[0]
    key=regexResult.groups()[0].strip()
    if not key:
        return
    content,jumpUrl,songUrl=await SearchSongsInNeteaseCloudMusic(key)
    await app.sendGroupMessage(event.sender.group,MessageChain.create([
        Plain(f"歌曲链接: {jumpUrl}\n音乐链接: {songUrl}"),
        App(content=content)
        ]),quote=quoted)
        

@bcc.receiver("GroupMessage",headless_decoraters=[Depend(strictPlainCommand("#撤回"))])
async def GroupRecallOtherMessage(app:GraiaMiraiApplication,event:GroupMessage):
    quoted=event.messageChain.get(Source)[0]
    if not await checkMemberPermission(app,event.sender,[MemberPerm.Administrator,MemberPerm.Owner],quoted):
        return
    target=event.messageChain.get(Quote)[0]
    member=await app.getMember(target.targetId,target.senderId)

    if not await checkBotPermission(app,event.sender.group,[MemberPerm.Owner,*([MemberPerm.Administrator] if member.permission==MemberPerm.Member else [])]):
        return
    await app.revokeMessage(target.origin.get(Source)[0])

    result=False
    member=event.sender
    if event.sender.group.accountPerm in [MemberPerm.Owner,*([MemberPerm.Administrator] if member.permission==MemberPerm.Member else [])]:
        await app.revokeMessage(event.messageChain.get(Source)[0])
        result=True
    await app.sendGroupMessage(event.sender.group,MessageChain.create([
        Plain("撤回消息成功"),
        *([] if result else [Plain("\n记得撤回自己的消息")])
    ]),quote=quoted)
'''
    @bcc.receiver("GroupMessage",headless_decoraters=[Depend(strictPlainCommand("#警告"))])
    async def GroupWarnMember(app:GraiaMiraiApplication,event:GroupMessage):
        quoted=event.messageChain.get(Source)[0]
        if not await checkMemberPermission(app,event.sender,[MemberPerm.Administrator,MemberPerm.Owner],quoted):
            return
        target=getTargetFromAt(app,event.sender.group,event.messageChain)
        for i in target:
            GetMemberStatusFromGrouBlockDB(event.sender.group,)
'''
@bcc.receiver("GroupMessage",headless_decoraters=[Depend(strictPlainCommand("#帮助"))])
async def GroupMessageHelp(app:GraiaMiraiApplication,event:GroupMessage):
    quoted=event.messageChain.get(Source)[0]
    await app.sendGroupMessage(event.sender.group,MessageChain.create([
        Plain("因帮助过长，转为私发")
    ]),quote=quoted)
    await app.sendTempMessage(event.sender.group,event.sender,MessageChain.create([
        Plain("支持的命令为:\n"),
        Plain("#睡眠套餐\n如果要为他人提供,使用@或者回复的方式,需要具有管理权限\n"),
        Plain("#添加进群答案 [答案]\n需要管理权限\n"),
        Plain("#删除进群答案 [答案]\n需要管理权限\n"),
        Plain("#可用进群答案\n展示现在允许的答案\n"),
        Plain("#添加管理员 [@被添加的人]\n需要管理权限,可以同时添加多人\n"),
        Plain("#解除管理员 [@被解除的人]\n需要管理权限,可以同事解除多人\n"),
        Plain("#当前管理员\n以列出qq号的方式列出当前群在库中的管理员\n")
    ]))
    await app.sendTempMessage(event.sender.group,event.sender,MessageChain.create([
        Plain("#禁言 [禁言时间] [@被禁言的人]\n时间的单位是分钟,支持同时禁言多人,需要管理权限.\n"),
        Plain("#解除禁言 [@被解除的人]\n需要管理权限,支持同时解除多人\n"),
        Plain("#更新入群词 ...\n被添加的内容会在新成员加入的时候发出\n"),
        Plain("#当前入群词\n查看当前群有新成员加入时发出的内容\n"),
        Plain("#神启 [内容]\n仅支持文字内容.不宜过长.由 https://www.daanshu.com/ 提供答案.\n"),
        Plain("#撤回\n用 #撤回 回复需要被撤回的内容,bot会尝试撤回对应内容,需要管理权限\n")
    ]))

@bcc.receiver("GroupMessage",headless_decoraters=[Depend(strictPlainCommand("#关于"))])
async def GroupAboutMessage(app:GraiaMiraiApplication,event:GroupMessage):
    quoted=event.messageChain.get(Source)[0]
    await app.sendGroupMessage(event.sender.group,MessageChain.create([
        Plain("本项目基于AGPL 3.0协议\n项目地址：\nhttps://github.com/xlxyzzgzs/a-qqbot-based-graia")
    ]),quote=quoted)

@bcc.receiver("BotGroupPermissionChangeEvent")
async def Group_Permission_Change(app:GraiaMiraiApplication,event:BotGroupPermissionChangeEvent):
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

@bcc.receiver("BotJoinGroupEvent")
async def Bot_Join_Group(app:GraiaMiraiApplication,event:BotJoinGroupEvent):
    await app.sendGroupMessage(event.group,MessageChain.create([
        Plain("引入了新的机器人时要小心命令冲突哦!")
    ]))
    InsertNewGroupToGroupInfoDB(event.group)

@bcc.receiver("GroupNameChangeEvent")
async def Group_Name_Change(app:GraiaMiraiApplication,event:GroupNameChangeEvent):
    if event.isByBot:
        return 
    await app.sendGroupMessage(event.group,MessageChain.create([
        Plain("这是发生了啥?为啥要改群名?")
    ]))

@bcc.receiver("GroupEntranceAnnouncementChangeEvent")
async def Group_Entrance_Announcement_Change(app:GraiaMiraiApplication,event:GroupEntranceAnnouncementChangeEvent):
    await app.sendGroupMessage(event.group,MessageChain.create([
        Plain("本群的入群公告改了哦,记得去看看."),
        (Plain("\n此处应有@全体") if event.group.accountPerm in [MemberPerm.Owner,MemberPerm.Administrator] else Plain("\n既然不具备权限就不@全体了"))
    ]))

@bcc.receiver("GroupMuteAllEvent")
async def Group_Mute_All_Event(app:GraiaMiraiApplication,event:GroupMuteAllEvent):
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
    
@bcc.receiver("GroupAllowAnonymousChatEvent")
async def Group_AnonymousChat_Event(app:GraiaMiraiApplication,event:GroupAllowAnonymousChatEvent):
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
@bcc.receiver("GroupAllowConfessTalkEvent")
async def Group_ConfessTalk_Event(app:GraiaMiraiApplication,event:GroupAllowConfessTalkEvent):
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

@bcc.receiver("MemberJoinEvent")
async def Group_Member_Join(app:GraiaMiraiApplication,event:MemberJoinEvent):
    message=GetFromGroupInfoDB(event.member.group,"MemberJoinMessage")
    if not message:
        return 
    message=StrToMessageChain(message)
    message.__root__.insert(0,At(event.member))
    await app.sendGroupMessage(event.member.group,message)


@bcc.receiver("MemberJoinRequestEvent")
async def Member_Join_Request(app:GraiaMiraiApplication,event:MemberJoinRequestEvent):
    group=await app.getGroup(event.groupId)
    #if not BlockedInGroup(group,)
    answer=event.message.strip().splitlines()[1][3:]
    if not CheckIfInGroupDB(group,"GroupAnswer","Answer",answer):
        return
    await event.accept("答案看上去没啥大问题.")
    await app.sendGroupMessage(group,MessageChain.create([
        Plain(event.nickname+"申请加群,答案为:"+answer+"\n已通过")
    ]))
'''
def func1():yitonggup
    return []
@bcc.receiver("GroupMessage")
async def test(param=Depend(func1,cache=False)):
    pass
'''

app.launch_blocking()

