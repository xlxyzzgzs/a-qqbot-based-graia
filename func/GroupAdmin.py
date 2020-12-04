from graia.application.entry import GraiaMiraiApplication,GroupMessage,Source,MemberPerm,At
from graia.application.entry import Plain,MessageChain
from graia.broadcast import Broadcast
from utils.messageTrigger import strictPlainCommand
from utils.checkPermission import checkMemberPermission
from utils.database import InsertToGroupDB,DeleteFromGroupDB,GetAllFromGroupDB

async def GroupAddAdmin(app:GraiaMiraiApplication,event:GroupMessage):
    quoted=event.messageChain.get(Source)[0]
    if not await checkMemberPermission(app,event.sender,[MemberPerm.Administrator,MemberPerm.Owner],quoted):
        return
    target=set(map(lambda at: at.target,event.messageChain.get(At)))
    succ_result=[]
    fail_result=[]
    for i in target:
        if InsertToGroupDB(app,event.sender.group,'GroupPermission','AdminID',i):
            succ_result.append(At(i))
        else :
            fail_result.append(At(i))
    await app.sendGroupMessage(event.sender.group,MessageChain.create([
        Plain("操作完成\n以下成员获取权限成功:\n"),*succ_result,
        Plain("\n以下成员获取权限失败:\n"),*fail_result
    ]),quote=quoted)

async def GroupRemoveAdmin(app:GraiaMiraiApplication,event:GroupMessage):
    quoted=event.messageChain.get(Source)[0]
    if not await checkMemberPermission(app,event.sender,[MemberPerm.Administrator,MemberPerm.Owner],quoted):
        return
    target=set(map(lambda at: at.target,event.messageChain.get(At)))
    succ_result=[]
    fail_result=[]
    for i in target:
        if DeleteFromGroupDB(app,event.sender.group,'GroupPermission','AdminID',i):
            succ_result.append(At(i))
        else :
            fail_result.append(At(i))
    await app.sendGroupMessage(event.sender.group,MessageChain.create([
        Plain("操作完成\n以下成员取消权限成功:\n"),*succ_result,
        Plain("\n以下成员取消权限失败:\n"),*fail_result
    ]),quote=quoted)

async def GroupAvailableAdmin(app:GraiaMiraiApplication,event:GroupMessage):
    quoted=event.messageChain.get(Source)[0]
    admin=GetAllFromGroupDB(app,event.sender.group,"GroupPermission","AdminID")
    admin='\n'.join(map(lambda ad:str(ad[0]) ,admin))
    await app.sendGroupMessage(event.sender.group,MessageChain.create([
        Plain("可用的管理为:\n"+admin)
    ]),quote=quoted)

def AddGroupAdminListener(bcc:Broadcast):
    bcc.receiver("GroupMessage",headless_decoraters=[strictPlainCommand('#添加管理员')])(GroupAddAdmin)
    bcc.receiver("GroupMessage",headless_decoraters=[strictPlainCommand('#解除管理员')])(GroupRemoveAdmin)
    bcc.receiver("GroupMessage",headless_decoraters=[strictPlainCommand("#当前管理员")])(GroupAvailableAdmin)

