from graia.application.entry import GroupMessage, TempMessage, FriendMessage
from graia.broadcast.builtin.decorators import Depend
from graia.broadcast.exceptions import ExecutionStop
from graia.broadcast.interrupt import InterruptControl
from graia.broadcast import Broadcast
from typing import Type
from utils import MessageType


def SendFromSameTarget(event: MessageType, eventType: Type[MessageType]):
    @Depend
    def func(wait_event: eventType):
        if wait_event.sender.id != event.sender.id \
                or isinstance(wait_event, FriendMessage) \
                or wait_event.sender.group.id != event.sender.group.id:
            raise ExecutionStop()
    return func


def InitInterruptControl(bcc: Broadcast):
    global interruptcontrol
    interruptcontrol = InterruptControl(bcc)
