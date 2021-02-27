from graia.application.entry import GraiaMiraiApplication, Session, MessageChain, GroupMessage, Group, Member, MemberPerm, Plain, At, Face
from graia.broadcast import Broadcast
import asyncio
from graia.application.message.parser.kanata import Kanata
from graia.application.message.parser.signature import FullMatch, RegexMatch, OptionalParam, RequireParam
from .utils import postGroupMessage


loop = asyncio.get_event_loop()
bcc = Broadcast(loop=loop)

'''
kanata 是匹配对话框中的第一个元素。当且仅当发送的消息中第一个元素为文本时可用。
FullMatch是从第一个文本开始进行匹配的
RegexMatch使用正则进行匹配，返回匹配的部分的后面剩余的部分。
RequireParm 是指定前一个匹配结果的名称,没有就不满足条件
OptionalParam 是指定前一个匹配结果的名称，是一个可选条件。不满足时为None
'''


@bcc.receiver("GroupMessage", dispatchers=[Kanata(
    [FullMatch("test full match:"), RequireParam("full_match_result")], stop_exec_if_fail=True)])
def test_full_match(full_match_result, event: GroupMessage):
    print(full_match_result)


@bcc.receiver("GroupMessage", dispatchers=[Kanata(
    [RegexMatch(r"test regex match:(.*)"), RequireParam("regex_match_result")], stop_exec_if_fail=True)])
def test_regex_match(regex_match_result, event: GroupMessage):
    print("regex match")
    print(regex_match_result)


postGroupMessage(MessageChain.create(
    [Plain("test regex match:2134e"), Face(faceId=123)]), bcc)

postGroupMessage(MessageChain.create(
    [Plain("test full match: "), Face(faceId=12), At(target=987654321), Plain("test full match:dqwoefr")]), bcc)

loop.run_until_complete(asyncio.sleep(10))
