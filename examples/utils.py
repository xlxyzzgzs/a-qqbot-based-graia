from graia.application.entry import MessageChain, Member, MemberPerm, Group, FriendMessage, Friend, GroupMessage
from graia.broadcast import Broadcast
from typing import NoReturn


def postGroupMessage(message: MessageChain, bcc: Broadcast) -> NoReturn:
    bcc.postEvent(
        GroupMessage(
            messageChain=message,
            sender=Member(
                id=123456789,
                memberName="member name",
                permission=MemberPerm.Administrator,
                group=Group(
                    id=123456789,
                    name="group name",
                    permission=MemberPerm.Administrator
                )
            )
        )
    )


def postFriendMessage(message: MessageChain, bcc: Broadcast) -> NoReturn:
    bcc.postEvent(FriendMessage(
        messageChain=message,
        sender=Friend(
            id=123456789,
            nickname="friend name",
            remark="renamed name"
        )
    ))
