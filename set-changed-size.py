from graia.application.entry import (
    GraiaMiraiApplication,
    GroupMessage,
    Source,
    Plain,
    MessageChain,
    FriendMessage,
    Quote,
)
from graia.broadcast import Broadcast
from graia.broadcast.interrupt import InterruptControl
from graia.broadcast.interrupt.waiter import Waiter
import asyncio
from config import connection_config, BotMaster

# from func import AddListener
import utils.interrupt as Interrupt
from utils.messageTrigger import strictPlainCommand, regexPlain
from random import randint

loop = asyncio.get_event_loop()
bcc = Broadcast(loop=loop)
app = GraiaMiraiApplication(
    broadcast=bcc, connect_info=connection_config(), enable_chat_log=True, debug=True
)

Interrupt.InitInterruptControl(bcc)
# AddListener(bcc)


@bcc.receiver(FriendMessage, headless_decoraters=[strictPlainCommand("#test")])
async def BotInviteJoinGroup(app: GraiaMiraiApplication, event: FriendMessage):
    message = MessageChain.create([Plain("有人邀请加群。\n")])
    BotMessageList = []
    for i in BotMaster:
        try:
            await asyncio.sleep(randint(1, 10))
            BotMessageList.append(await app.sendFriendMessage(i, message))
        except KeyError:
            app.logger.error(f"为啥Master {i}连个好友都不是。!")
            pass

    @Waiter.create_using_function([FriendMessage])
    async def wait(
        wait_event: FriendMessage,
        regexResult=regexPlain(r"^#(同意|拒绝)(?:\s*(?<=\s)(.*)|())$"),
    ):
        quote = wait_event.messageChain.get(Quote)
        if not quote or wait_event.sender.id not in BotMaster:
            return None
        for bot in BotMessageList:
            if quote[0].id == bot.messageId:
                return regexResult, bot.messageId

    regexResult, quoted = await Interrupt.interruptcontrol.wait(wait)
    if regexResult.group(1) == "同意":
        # event.accept(regexResult.group(2))
        message = MessageChain.create([Plain("完成同意加群申请")])
        for i in BotMaster:
            # await asyncio.sleep(randint(1,10))
            await app.sendFriendMessage(i, message, quote=quoted)
    else:
        # event.reject(regexResult.group(2))
        message = MessageChain.create([Plain("完成同意加群申请")])
        for i in BotMaster:
            # await asyncio.sleep(randint(1,10))
            await app.sendFriendMessage(i, message, quote=quoted)


"""
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
"""

app.launch_blocking()
