from graia.application.entry import GraiaMiraiApplication
from graia.broadcast import Broadcast
import asyncio
from config import connection_config
from func import AddListener
import utils.interrupt as Interrupt

loop=asyncio.get_event_loop()
bcc=Broadcast(loop=loop)
app=GraiaMiraiApplication(
    broadcast=bcc,
    connect_info=connection_config(),
    enable_chat_log=True,
    debug=True
)

Interrupt.InitInterruptControl(bcc)
AddListener(bcc)
'''
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
'''

app.launch_blocking()
