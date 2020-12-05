from graia.application.entry import GraiaMiraiApplication,GroupMessage,MessageChain,Plain,App,Source
from graia.broadcast import Broadcast
from graia.broadcast.interrupt.waiter import Waiter
from utils.messageTrigger import getElements,strictPlainCommand
import json
import re
import utils.interrupt as Interrupt

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

async def GroupBilibiliMessageToUrl(app:GraiaMiraiApplication,event:GroupMessage,target=getElements(App)):
    try :
        url=json.loads(target[0].content)['meta']['detail_1']['qqdocurl']
        url=re.search(r"^[^\?]*",url).group(0)
        if url:
            await app.sendGroupMessage(event.sender.group,MessageChain.create([
                Plain(url)
            ]))
    except Exception as e:
        app.logger.exception(e)

AppToUrlFuntion=[BilibiliMessageToUrl]
async def GroupMessageAppToUrl(app:GraiaMiraiApplication,event:GroupMessage):
    quoted=event.messageChain.get(Source)[0]
    await app.sendGroupMessage(event.sender.group,MessageChain.create([Plain("发送APP消息")]),quote=quoted)
    @Waiter.create_using_function([GroupMessage])
    async def waiter(wait_event:GroupMessage):
        if wait_event.sender.id==event.sender.id and \
            wait_event.sender.group.id==event.sender.group.id :
            message=wait_event.messageChain.get(App)
            if message:
                print(message[0])
                return message[0]
    message=await Interrupt.interruptcontrol.wait(waiter)
    url=None
    for func in AppToUrlFuntion:
        url=func(message)
        if url:
            break
    if not url:
        url="没找到合适的链接"
    await app.sendGroupMessage(event.sender.group,MessageChain.create([Plain(url)]))


def AddAppToUrlListener(bcc:Broadcast):
    bcc.receiver("GroupMessage")(GroupBilibiliMessageToUrl)
    #bcc.receiver("GroupMessage",headless_decoraters=[strictPlainCommand("#解析App")])(GroupMessageAppToUrl)