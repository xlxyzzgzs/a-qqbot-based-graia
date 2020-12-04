from graia.application.entry import GraiaMiraiApplication,BotInvitedJoinGroupRequestEvent,BotJoinGroupEvent
from graia.application.entry import MessageChain,Plain
from graia.broadcast import Broadcast
from utils.database import InsertNewGroupToGroupInfoDB

async def BotJoinGroup(app:GraiaMiraiApplication,event:BotJoinGroupEvent):
    await app.sendGroupMessage(event.group,MessageChain.create([
        Plain("引入了新的机器人时要小心命令冲突哦!")
    ]))
    InsertNewGroupToGroupInfoDB(app,event.group)

def AddInviteBotListener(bcc:Broadcast):
    bcc.receiver("BotJoinGroupEvent")(BotJoinGroup)