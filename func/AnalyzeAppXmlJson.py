from graia.application.entry import GraiaMiraiApplication, MessageChain, Plain, Source
from graia.application.entry import FriendMessage, GroupMessage, TempMessage
from graia.broadcast import Broadcast
from graia.broadcast.interrupt.waiter import Waiter
from graia.application.message.elements.internal import Xml, App, Json
from utils.customDispatcher import CustomDispatcher
from utils.messageTrigger import getElements, strictPlainCommand
from utils import SendToTarget, MessageType
import utils.interrupt as Interrupt

from typing import Union, Type


def AnalyzeGenerator(eventType: Type[MessageType]):
    async def func(
        app: GraiaMiraiApplication, event: eventType
    ):
        quoted = event.messageChain.get(Source)[0]

        @Waiter.create_using_function([eventType], using_dispatchers=[
            CustomDispatcher(getElements(App), target_name="target"),
            CustomDispatcher(getElements(Xml), target_name="target"),
            CustomDispatcher(getElements(Json), target_name="target")
        ],
            using_decorators=[Interrupt.SendFromSameTarget(event, eventType)], block_propagation=True)
        async def wait(
            wait_event: eventType,
            target
        ):
            return target[0]
        result = await Interrupt.interruptcontrol.wait(wait)
        if isinstance(result, Xml):
            result = result.xml
        elif isinstance(result, Json):
            result = result.Json
        elif isinstance(result, App):
            result = result.content
        else:
            result = "未知错误"
        await SendToTarget(app, event.sender, eventType, MessageChain.create([
            Plain(result)
        ]), quoted)
    return func


def AddAnalyzeEventListener(bcc: Broadcast):
    bcc.receiver(GroupMessage, headless_decoraters=[
                 strictPlainCommand("#解析复杂消息")])(AnalyzeGenerator(GroupMessage))
    bcc.receiver(FriendMessage, headless_decoraters=[
                 strictPlainCommand("#解析复杂消息")])(AnalyzeGenerator(FriendMessage))
    bcc.receiver(TempMessage, headless_decoraters=[
                 strictPlainCommand("#解析复杂消息")])(AnalyzeGenerator(TempMessage))
