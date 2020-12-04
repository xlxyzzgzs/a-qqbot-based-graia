from graia.application.entry import GraiaMiraiApplication,GroupMessage,MessageChain,Plain,App
from graia.broadcast import Broadcast
from utils.messageTrigger import getElements
import json
import re

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

def AddAppToUrlListener(bcc:Broadcast):
    bcc.receiver("GroupMessage")(GroupBilibiliMessageToUrl)