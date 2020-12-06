from typing import List
from pydantic import BaseModel
import json


class QQButtonAutoReply(BaseModel):
    """
    slot :作用暂时不明确
    action_data :用户点击后 自动发送（回复）的内容
    name :显示在消息中的蓝色的内容
    action :作用暂时不明确
    """

    slot: int
    action_data: str
    name: str
    action: str = "notify"

    def __str__(self):
        s = f"""{{"slot":{self.slot},"action_data":"{self.action_data}","name":"{self.name}","action":"{self.action}"}}"""
        return s

    """
    def __repr__(self):
        return {
            'slot':self.slot,
            'action_data':self.action_data,
            'name':self.name,
            'action':self.action
        }
    """

    def to_dict(self) -> dict:
        return {
            "slot": self.slot,
            "action_data": self.action_data,
            "name": self.name,
            "action": self.action,
        }


def GenerateAutoReplyButton(
    prompt: str,
    title: str,
    button: List[QQButtonAutoReply],
    forward: bool = True,
    showSender: bool = True,
) -> str:
    """
    prompt :显示在预览（即在消息列表）中显示的内容
    title :消息中的黑色字体的部分（不可点击）
    button :消息中包含的可点击的按钮，类型为 List[QQButtonAutoReply]
    forward :是否可转发（个人猜测）
    showSender :是否显示发送者（个人猜测）
    """
    button_str = []
    for b in button:
        button_str.append(b.to_dict())
    content = f"""{{"app":"com.tencent.autoreply","desc":"","view":"autoreply","ver":"0.0.0.1","prompt":"{prompt}","meta":{{"metadata":{{"title":"{title}","buttons":{json.dumps(button_str)},"type":"guest"}}}},"config":{{"forward":{1 if forward else 0},"showSender":{1 if showSender else 0}}}}}"""
    return content
