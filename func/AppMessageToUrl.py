from graia.application.entry import (
    GraiaMiraiApplication,
    GroupMessage,
    MessageChain,
    Plain,
    App,
    Source,
    FriendMessage,
    TempMessage,
)
from graia.broadcast import Broadcast
from graia.broadcast.interrupt.waiter import Waiter
import json
import re
from typing import Type
from utils.messageTrigger import getElements, strictPlainCommand
import utils.interrupt as Interrupt
from utils import SendToTarget, MessageType


def BilibiliMessageToUrl(message: App):
    try:
        url = json.loads(message.content)["meta"]["detail_1"]["qqdocurl"]
        url = re.search(r"^[^\?]*", url).group(0)
        if url:
            return url
        else:
            return None
    except Exception:
        return None


AppToUrlFuntion = [BilibiliMessageToUrl]


def AppMessageToUrl(message: App):
    url = None
    for func in AppToUrlFuntion:
        url = func(message)
        if url:
            break
    return url


async def GroupBilibiliMessageToUrl(
    app: GraiaMiraiApplication, event: GroupMessage, target=getElements(App)
):
    url = AppMessageToUrl(target[0])
    if url:
        await app.sendGroupMessage(
            event.sender.group, MessageChain.create([Plain(url)])
        )


def AppToUrlAutoConvertGenerator(eventType: Type[MessageType]):
    async def func(
        app: GraiaMiraiApplication, event: eventType, target=getElements(App)
    ):
        url = AppMessageToUrl(target[0])
        if url:
            print(url)
            # await SendToTarget(
            #    app, event.sender, eventType, MessageChain.create([Plain(url)])
            # )

    return func


def MessageAppToUrlGenerator(eventType: Type[MessageType]):
    async def func(app: GraiaMiraiApplication, event: eventType):
        quoted = event.messageChain.get(Source)[0]
        await SendToTarget(
            app,
            event.sender,
            eventType,
            MessageChain.create([Plain("发送APP消息")]),
            quote=quoted,
        )

        @Waiter.create_using_function([eventType], using_decorators=[Interrupt.SendFromSameTarget(event, eventType)], block_propagation=True)
        async def waiter(wait_event: eventType):
            message = wait_event.messageChain.get(App)
            if message:
                print(message[0])
                return message[0]

        message = await Interrupt.interruptcontrol.wait(waiter)
        url = AppMessageToUrl(message)
        if not url:
            url = "没找到合适的链接"
        await SendToTarget(
            app,
            event.sender,
            eventType,
            MessageChain.create([Plain(url)]),
            quote=quoted,
        )

    return func


def AddAppToUrlListener(bcc: Broadcast):
    bcc.receiver("GroupMessage")(AppToUrlAutoConvertGenerator(GroupMessage))
    bcc.receiver("FriendMessage")(AppToUrlAutoConvertGenerator(FriendMessage))
    bcc.receiver("TempMessage")(AppToUrlAutoConvertGenerator(TempMessage))
    bcc.receiver("GroupMessage", headless_decoraters=[strictPlainCommand("#提取App链接")])(
        MessageAppToUrlGenerator(GroupMessage)
    )
    bcc.receiver("FriendMessage", headless_decoraters=[strictPlainCommand("#提取App链接")])(
        MessageAppToUrlGenerator(FriendMessage)
    )
    bcc.receiver("TempMessage", headless_decoraters=[strictPlainCommand("#提取App链接")])(
        MessageAppToUrlGenerator(TempMessage)
    )
