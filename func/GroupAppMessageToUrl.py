from graia.application.entry import GraiaMiraiApplication,GroupMessage,MessageChain,Plain,App,Source
from graia.application.entry import FriendMessage,TempMessage
from graia.application.event import BaseEvent
from graia.broadcast import Broadcast
from graia.broadcast.interrupt.waiter import Waiter
import json
import re
from utils.messageTrigger import getElements,strictPlainCommand
import utils.interrupt as Interrupt
from utils import SendToTarget

def BilibiliMessageToUrl(message:App):
    try :
        url=json.loads(message.content)['meta']['detail_1']['qqdocurl']
        url=re.search(r"^[^\?]*",url).group(0)
        if url:
            return url
        else :
            return None
    except Exception:
        return None
AppToUrlFuntion=[BilibiliMessageToUrl]

def AppMessageToUrl(message:App):
    url=None
    for func in AppToUrlFuntion:
        url=func(message)
        if url:
            break
    return url

async def GroupBilibiliMessageToUrl(app:GraiaMiraiApplication,event:GroupMessage,target=getElements(App)):
    url=AppMessageToUrl(target[0])
    if url:
        await app.sendGroupMessage(event.sender.group,MessageChain.create([
            Plain(url)
        ]))
def AppToUrlAutoConvertGenerator(eventType:BaseEvent):
    async def func(app:GraiaMiraiApplication,event:eventType,target=getElements(App)):
        url=AppMessageToUrl(target[0])
        if url:
            SendToTarget(app,event.sender,eventType,MessageChain.create([Plain(url)]))
    return func

def MessageAppToUrlGenerator(eventType:BaseEvent):
    async def func(app:GraiaMiraiApplication,event:eventType):
        quoted=event.messageChain.get(Source)[0]
        SendToTarget(app,event.sender,eventType,MessageChain.create([Plain("发送APP消息")]),quote=quoted)
        @Waiter.create_using_function([eventType])
        async def waiter(wait_event:eventType):
            if wait_event.sender.id==event.sender.id and \
                ( not isinstance(wait_event,(GroupMessage,TempMessage)) or \
                wait_event.sender.group.id==event.sender.group.id ):
                message=wait_event.messageChain.get(App)
                if message:
                    print(message[0])
                    return message[0]
        message=await Interrupt.interruptcontrol.wait(waiter)
        url=AppMessageToUrl(message)
        if not url:
            url="没找到合适的链接"
        SendToTarget(app,event.sender,eventType,MessageChain.create([Plain(url)]),quote=quoted)
    return func

def AddAppToUrlListener(bcc:Broadcast):
    bcc.receiver("GroupMessage")(AppToUrlAutoConvertGenerator(GroupMessage))
    bcc.receiver("FriendMessage")(AppToUrlAutoConvertGenerator(FriendMessage))
    bcc.receiver("TempMessage")(AppToUrlAutoConvertGenerator(TempMessage))
    bcc.receiver("GroupMessage",headless_decoraters=[strictPlainCommand("#提取App链接")])(MessageAppToUrlGenerator(GroupMessage))
    bcc.receiver("FriendMessage",headless_decoraters=[strictPlainCommand("#提取App链接")])(MessageAppToUrlGenerator(FriendMessage))
    bcc.receiver("TempMessage",headless_decoraters=[strictPlainCommand("#提取App链接")])(MessageAppToUrlGenerator(TempMessage))