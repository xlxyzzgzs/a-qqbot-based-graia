from graia.application.entry import GraiaMiraiApplication,BotInvitedJoinGroupRequestEvent,BotJoinGroupEvent
from graia.application.entry import MessageChain,Plain,FriendMessage,Quote,Friend
from graia.broadcast.interrupt.waiter import Waiter
from graia.broadcast import Broadcast
from utils.database import InsertNewGroupToGroupInfoDB
import utils.interrupt as Interrupt
from utils.messageTrigger import regexPlain
from config import BotMaster
import asyncio
from random import randint
from typing import Union

async def BotJoinGroup(app:GraiaMiraiApplication,event:BotJoinGroupEvent):
    await app.sendGroupMessage(event.group,MessageChain.create([
        Plain("引入了新的机器人时要小心命令冲突哦!")
    ]))
    InsertNewGroupToGroupInfoDB(app,event.group)

class ReturnValue(Exception):
    def __init__(self,value):
        self.ReturnValue=value

async def RequsetBotMaster(app:GraiaMiraiApplication,target:Union[Friend,int],event:BotInvitedJoinGroupRequestEvent):
    botMessage=None
    try:
        await asyncio.sleep(randint(1,10))
        botMessage=app.sendFriendMessage(target,MessageChain.create([
            Plain("有人邀请加群。\n"),
            Plain(f"请求事件ID: {event.requestId}"),
            Plain(f"邀请人为: {event.supplicant}\n"),
            Plain(f"邀请人称呼为: {event.nickname}\n"),
            Plain(f"群号为: {event.groupId}\n"),
            Plain(f"群名称为: {event.groupName}"),
            Plain(f"附加消息: {event.message}")
        ]))
        @Waiter.create_using_function([FriendMessage])
        async def wait(wait_event:FriendMessage,regexResult=regexPlain(r"^#(同意|拒绝)(?:\s*(?<=\s)(.*)|)$")):
            quote=wait_event.messageChain.get(Quote)
            if not quote or wait_event.sender.id != target or quote[0].id == botMessage.messageId:
                return None
            return regexResult
        raise ReturnValue([await Interrupt.interruptcontrol.wait(wait),target,botMessage.messageId])
    except asyncio.CancelledError:
        await asyncio.sleep(randint(1,10))
        await app.sendFriendMessage(target,MessageChain.create([Plain("已由其他人处理")]),quote=botMessage.messageId)
        
async def BotInviteJoinGroup(app:GraiaMiraiApplication,event:BotInvitedJoinGroupRequestEvent):
    if event.supplicant in BotMaster:
        event.accept("邀请通过")
        return
    taskList=[RequsetBotMaster(app,i,event) for i in BotMaster]
    try:
        await asyncio.gather(*taskList)
    except ReturnValue as value:
        for t in taskList:
            t.cancel()
        regexResult=value.ReturnValue[0]
        if regexResult.group(1)=="同意":
            event.accept(regexResult.group(2) if regexResult.group(2) else "")
            await app.sendFriendMessage(value.ReturnValue[1],MessageChain.create([Plain("完成同意加群申请")]),quote=value.ReturnValue[2])
        else:
            event.reject(regexResult.group(2) if regexResult.group(2) else "")
            await app.sendFriendMessage(value.ReturnValue,MessageChain.create([Plain("完成拒绝加群申请")]),quote=value.ReturnValue[2])
    finally :
        await asyncio.sleep(30)


def AddInviteBotListener(bcc:Broadcast):
    bcc.receiver("BotJoinGroupEvent")(BotJoinGroup)
    bcc.receiver("BotInvitedJoinGroupRequestEvent")(BotInviteJoinGroup)
    bcc.receiver("GroupMessage")