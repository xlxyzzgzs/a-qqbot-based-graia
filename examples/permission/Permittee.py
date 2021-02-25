from .Permission import load_permission_from_dataBase, PermissionId
from pydantic import BaseModel
from typing import Sequence
from graia.application.entry import FriendMessage, GroupMessage, TempMessage
from .PermissionConfig import DATEBASE_PATH
import aiosqlite
'''
/**
 * 内建的 [PermitteeId].
 *
 * - 若指令 A 的权限被授予给 [AnyMember], 那么一个 [ExactMember] 可以执行这个指令.
 *
 * #### 字符串表示
 *
 * 当使用 [PermitteeId.asString] 时, 不同的类型的返回值如下表所示. 这些格式也适用于 [BuiltInCommands.PermissionCommand].
 *
 * (不区分大小写. 不区分 Bot).
 *
 * [查看字符串表示列表](https://github.com/mamoe/mirai-console/docs/Permissions.md#字符串表示)
 *
 * #### 关系图
 *
 * ```
 *          Console                               AnyContact
 *                                                     ↑
 *                                                     |
 *                         +---------------------------+------------------------+---------------------+
 *                         |                                                    |                     |
 *                      AnyUser                                             AnyGroup            AnyOtherClient
 *                         ↑                                                    ↑                     ↑
 *                         |                                                    |                     |
 *          +--------------+---------------------+                              |                     |
 *          |              |                     |                              |                     |
 *     AnyFriend           |            AnyMemberFromAnyGroup                   |                     |
 *          ↑              |                     ↑                              |                     |
 *          |              |                     |                              |                     |
 *          |              |            +--------+--------------+               |                     |
 *          |              |            |                       |               |                     |
 *          |              |            |              AnyTempFromAnyGroup      |                     |
 *          |              |            |                       ↑               |                     |
 *          |              |        AnyMember                   |               |                     |
 *          |              |            ↑                       |               |                     |
 *          |          ExactUser        |                       |           ExactGroup         ExactOtherClient
 *          |            ↑   ↑          |                       |
 *          |            |   |          |                       |
 *          +------------+   +----------+                       |
 *          |                           |                       |
 *     ExactFriend                 ExactMember                  |
 *                                      ↑                       |
 *                                      |                       |
 *                                      +-----------------------+
 *                                                              |
 *                                                              |
 *                                                          ExactTemp
 * ```
 */

|    被许可人类型    | 字符串表示示例 | 备注                                 |
|:----------------:|:-----------:|:------------------------------------|
|      控制台       |   console   |                                     |
|   任意其他客户端    |   client*   | 即 Bot 自己发消息给自己                |
|      精确群       |   g123456   | 表示群, 而不表示群成员                  |
|      精确好友      |   f123456   | 必须通过好友消息                       |
|   精确群临时会话    | t123456.789 | 群 123456 内的成员 789. 必须通过临时会话 |
|     精确群成员     | m123456.789 | 群 123456 内的成员 789. 同时包含临时会话 |
|      精确用户      |   u123456   | 同时包含群成员, 好友, 临时会话           |
|      任意群       |     g\*     | g 意为 group                         |
|  任意群的任意群员   |     m\*     | m 意为 member                        |
|  精确群的任意群员   | m123456.\*  | 群 123456 内的任意成员. 同时包含临时会话  |
|    任意临时会话    |     t\*      | t 意为 temp. 必须通过临时会话          |
| 精确群的任意临时会话 | t123456.\*  | 群 123456 内的任意成员. 必须通过临时会话  |
|      任意好友      |     f\*     | f 意为 friend                       |
|      任意用户      |     u\*     | u 意为 user. 任何人在任何环境           |
|     任意陌生人     |     s\*     | s 意为 stranger. 任何人在任何环境       |
|    任意联系对象    |      \*      | 即任何人, 任何群. 不包括控制台           |

'''


class PermitteeId(BaseModel):
    id: str
    directParents: Sequence["PermitteeId"]

    def __str__(self):
        return self.id

    def __repr__(self):
        return self.id

    def __hash__(self):
        return self.id

    def __eq__(self, other):
        return True if self.id == other.id else False

    def get_all_parents(self):
        for p in self.directParents:
            yield from p.all_parents_with_self()

    def get_all_parents_with_self(self):
        yield self
        yield from self.all_parents()


PermitteeId.update_forward_refs()
'''
AnyContact = PermitteeId(id="*", directParents=tuple())

AnyUser = PermitteeId(id="u*", directParents=(AnyContact,))
AnyGroup = PermitteeId(id="g*", directParents=(AnyContact,))
AnyOtherClient = PermitteeId(id="client*", directParents=(AnyContact,))

AnyFriend = PermitteeId(id="f*", directParents=(AnyUser,))
AnyMemberFromAnyGroup = PermitteeId(id="m*", directParents=(AnyUser,))
AnyTempFromAnyGroup = PermitteeId(
    id="t*", directParents=(AnyMemberFromAnyGroup,))
'''


class AnyContact(PermitteeId):
    id = "*"
    directParents: Sequence["PermitteeId"] = tuple()


class AnyUser(PermitteeId):
    id = "u*"
    directParents: Sequence["PermitteeId"] = (AnyContact(),)


class AnyGroup(PermitteeId):
    id = "g*"
    directParents: Sequence["PermitteeId"] = (AnyContact(),)


class AnyOtherClient(PermitteeId):
    id = "client*"
    directParents: Sequence["PermitteeId"] = (AnyContact(),)


class AnyFriend(PermitteeId):
    id = "f*"
    directParents: Sequence["PermitteeId"] = (AnyUser(),)


class AnyMemberFromAnyGroup(PermitteeId):
    id = "m*"
    directParents: Sequence["PermitteeId"] = (AnyUser(),)


class AnyTempFromAnyGroup(PermitteeId):
    id = "t*"
    directParents: Sequence["PermitteeId"] = (AnyMemberFromAnyGroup(),)


class AnyMember(PermitteeId):
    directParents: Sequence["PermitteeId"] = (AnyMemberFromAnyGroup(),)


class ExactFriend(PermitteeId):
    ...


class ExactGroup(PermitteeId):
    directParents: Sequence["PermitteeId"] = (AnyGroup(),)


class ExactMember(PermitteeId):
    ...


class ExactOtherClient(PermitteeId):
    directParents: Sequence["PermitteeId"] = (AnyOtherClient(),)


class ExactTemp(PermitteeId):
    ...


class ExactUser(PermitteeId):
    directParents: Sequence["PermitteeId"] = (AnyUser(),)


def __make_exact_friend(id: int):
    # return ExactFriend(id=f"f{id}", directParents=(ExactUser(id=f"u{id}"), AnyFriend))
    return ExactFriend(id=f"f{id}", directParents=(ExactUser(id=f"u{id}"), AnyFriend()))


def __make_exact_member(id: int, group: int):
    # return ExactMember(id=f"m{group}.{id}", directParents=(ExactUser(id=f"u{id}"), AnyMember(id=f"m{group}.*")))
    return ExactMember(id=f"m{group}.{id}", directParents=(ExactUser(id=f"u{id}"), AnyMember(id=f"m{group}.*")))


def __make_exact_temp(id: int, group: int):
    # return ExactTemp(id=f"t{group}.{id}", directParents=(__make_exact_member(id, group), AnyTempFromAnyGroup))
    return ExactTemp(id=f"t{group}.{id}", directParents=(__make_exact_member(id, group), AnyTempFromAnyGroup()))


def friend_message_permittee(event: FriendMessage) -> ExactFriend:
    return __make_exact_friend(event.sender.id)


def group_message_permittee(event: GroupMessage) -> ExactMember:
    return __make_exact_member(event.sender.id, event.sender.group.id)


def temp_message_permittee(event: TempMessage) -> ExactTemp:
    return __make_exact_temp(event.sender.id, event.sender.group.id)


def str_to_permittee(permittee_str: str) -> PermitteeId:
    if permittee_str[0] == "*":
        return AnyContact()
    elif permittee_str[0] == "u":
        if permittee_str[1] == "*":
            return AnyUser()
        return ExactUser(id=permittee_str)
    elif permittee_str[0] == "g":
        if permittee_str[1] == "*":
            return AnyGroup()
        return ExactGroup(id=permittee_str)
    elif permittee_str[0] == "c":
        if permittee_str == "client*":
            return AnyOtherClient()
        return ExactOtherClient()
    elif permittee_str[0] == "f":
        if permittee_str[1] == "*":
            return AnyFriend()
        return __make_exact_friend(permittee_str[1:])
    elif permittee_str[0] == "m":
        if permittee_str[1] == "*":
            return AnyMemberFromAnyGroup()
        p_split = permittee_str.split(".")
        if p_split[1] == "*":
            return AnyMember(id=permittee_str)
        return __make_exact_member(p_split[1], p_split[0][1:])
    elif permittee_str[0] == "t":
        if permittee_str[1] == "*":
            return AnyTempFromAnyGroup()
        p_split = permittee_str.split(".")
        return __make_exact_temp(p_split[1], p_split[0][1:])
    else:
        raise SyntaxError("invalid permittee string")
