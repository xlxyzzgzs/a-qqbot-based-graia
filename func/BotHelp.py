from graia.application.entry import GraiaMiraiApplication,GroupMessage,Source,MessageChain
from graia.application.entry import Plain
from graia.broadcast import Broadcast
from utils.messageTrigger import strictPlainCommand

async def GroupHelpMessage(app:GraiaMiraiApplication,event:GroupMessage):
    quoted=event.messageChain.get(Source)[0]
    await app.sendGroupMessage(event.sender.group,MessageChain.create([
        Plain("因帮助过长，转为私发")
    ]),quote=quoted)
    await app.sendTempMessage(event.sender.group,event.sender,MessageChain.create([
        Plain("支持的命令为:\n"),
        Plain("#睡眠套餐\n如果要为他人提供,使用@或者回复的方式,需要具有管理权限\n"),
        Plain("#添加进群答案 [答案]\n需要管理权限\n"),
        Plain("#删除进群答案 [答案]\n需要管理权限\n"),
        Plain("#可用进群答案\n展示现在允许的答案\n"),
        Plain("#添加管理员 [@被添加的人]\n需要管理权限,可以同时添加多人\n"),
        Plain("#解除管理员 [@被解除的人]\n需要管理权限,可以同事解除多人\n"),
        Plain("#当前管理员\n以列出qq号的方式列出当前群在库中的管理员\n")
    ]))
    await app.sendTempMessage(event.sender.group,event.sender,MessageChain.create([
        Plain("#禁言 [禁言时间] [@被禁言的人]\n时间的单位是分钟,支持同时禁言多人,需要管理权限.\n"),
        Plain("#解除禁言 [@被解除的人]\n需要管理权限,支持同时解除多人\n"),
        Plain("#更新入群词 ...\n被添加的内容会在新成员加入的时候发出\n"),
        Plain("#当前入群词\n查看当前群有新成员加入时发出的内容\n"),
        Plain("#神启 [内容]\n仅支持文字内容.不宜过长.由 https://www.daanshu.com/ 提供答案.\n"),
        Plain("#网易云音乐 [歌曲名]\n返回第一个搜索结果\n"),
        Plain("#撤回\n用 #撤回 回复需要被撤回的内容,bot会尝试撤回对应内容,需要管理权限\n")
    ]))
    await app.sendTempMessage(event.sender.group,event.sender,MessageChain.create([
        Plain("#警告 [@被警告的人]\n警告次数+1,警告3次后飞机票,需要管理权限\n"),
        Plain("#解除警告 [@被解除的人]\n警告次数置0,需要管理权限\n"),
        Plain("#拉黑 [@被拉黑的人]\n飞机票处理.并自动拒绝加入申请\n"),
        Plain("#关于\n项目链接\n"),
        Plain("#帮助\n显示此条帮助")
    ]))


async def GroupAboutMessage(app:GraiaMiraiApplication,event:GroupMessage):
    quoted=event.messageChain.get(Source)[0]
    await app.sendGroupMessage(event.sender.group,MessageChain.create([
        Plain("本项目基于AGPL 3.0协议\n项目地址：\nhttps://github.com/xlxyzzgzs/a-qqbot-based-graia")
    ]),quote=quoted)

def AddBotHelpListener(bcc:Broadcast):
    bcc.receiver("GroupMessage",headless_decoraters=[strictPlainCommand("#帮助")])(GroupHelpMessage)
    bcc.receiver("GroupMessage",headless_decoraters=[strictPlainCommand("#关于")])(GroupAboutMessage)
