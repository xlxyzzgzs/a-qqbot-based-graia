from graia.application.entry import MessageChain
from typing import Optional
import json


async def MessageChainToStr(
    messageChain: MessageChain, skipStrInPlain: Optional[str] = None
) -> str:
    """
    将 MessageChain 转成 str 方便存储的类型.
    """
    result = await messageChain.asSendable().build()
    result = result.dict()["__root__"]
    for i in range(len(result)):
        if result[i]["type"] == "Plain" and skipStrInPlain:
            result[i]["text"] = result[i]["text"].replace(skipStrInPlain, "")
    return json.dumps(result)


def StrToMessageChain(origin: str) -> MessageChain:
    """
    将 str 转成 MessageChain
    """
    return MessageChain.parse_obj(json.loads(origin)).asMutable()
