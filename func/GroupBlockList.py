from graia.application.entry import GraiaMiraiApplication,GroupMessage,Source,MemberPerm,Plain
from graia.application.entry import MessageChain,At,Quote
from graia.broadcast import Broadcast
from utils.checkPermission import checkBotPermission,checkMemberPermission
from utils.database import GetMemberStatusFromGrouBlockDB,InsertMemberStatusToGroupBlockDB
from utils.sf_utils import getTargetFromAt,muteMember,kickMember
from utils.messageTrigger import strictPlainCommand,regexPlain
import re

async def GroupWarnMember(app:GraiaMiraiApplication,event:GroupMessage):
    quoted=event.messageChain.get(Source)[0]
    if not await checkMemberPermission(app,event.sender,[MemberPerm.Administrator,MemberPerm.Owner],quoted):
        return    
    target=getTargetFromAt(app,event.sender.group,event.messageChain)
    for i in target:
        reply=[At(target=i.id)]
        times=GetMemberStatusFromGrouBlockDB(app,event.sender.group,i,"Warn")
        if times==None:
            return
        times+=1
        if not InsertMemberStatusToGroupBlockDB(app,event.sender.group,i,"Warn",times):
            return
        if times==1:
            reply.append(Plain("第一次警告,注意群规."))
        elif times==2:
            reply.append(Plain("第二次警告,注意群规.关小黑屋1天."))
            await muteMember(app,event.sender.group,i,24*60,quoted)
        elif times==3:
            reply.append(Plain("第三次警告,注意群规.关小黑屋一个月.下次直接飞机票."))
            await muteMember(app,event.sender.group,i,30*24*60-1,quoted)
        elif times==4:
            reply.append(Plain("第四次警告,飞机票."))
            await kickMember(app,event.sender.group,i,quoted)
            block=GetMemberStatusFromGrouBlockDB(app,event.sender.group,i,"Blocked")
            if block==None:
                return
            block+=1
            if not InsertMemberStatusToGroupBlockDB(app,event.sender.group,i,"Blocked",block):
                return
        await app.sendGroupMessage(event.sender.group,MessageChain.create(reply))

    await app.sendGroupMessage(event.sender.group,MessageChain.create([
        Plain("操作完成")
    ]),quote=quoted)


async def GroupCancelWarnMember(app:GraiaMiraiApplication,event:GroupMessage):
    qutoed=event.messageChain.get(Source)[0]
    if not checkMemberPermission(app,event.sender,[MemberPerm.Administrator,MemberPerm.Owner],qutoed):
        return
    target=getTargetFromAt(app,event.sender.group,event.messageChain)
    succ=[]
    for i in target:
        if InsertMemberStatusToGroupBlockDB(app,event.sender.group,i,"Warn",0):
            succ.append(At(i))
    await app.sendGroupMessage(event.sender.group,MessageChain.create([
        Plain("操作完成.以下成员解除警告:\n"),
        *succ]))


async def GroupBlockMember(app:GraiaMiraiApplication,event:GroupMessage):
    quoted=event.messageChain.get(Quote)
    if not await checkMemberPermission(app,event.sender,[MemberPerm.Administrator,MemberPerm.Owner],quoted):
        return    
    if not checkBotPermission(app,event.sender.group,[MemberPerm.Owner,*([MemberPerm.Administrator] if event.sender.permission==MemberPerm.Member else [])],quoted):
        return
    target=getTargetFromAt(app,event.sender.group,event.messageChain.get(At))
    succ=[]
    for i in target:
        times=GetMemberStatusFromGrouBlockDB(app,event.sender.group,i,"Blocked")
        if times==None:
            return
        if not InsertMemberStatusToGroupBlockDB(app,event.sender.group,i,"Blocked",times+1):
            return
        if await kickMember(app,event.sender.group,i,quoted):
           succ.append(i.id)
    await app.sendGroupMessage(event.sender.group,MessageChain.create([
        Plain(f"操作完成.被拉黑的对象为:\n{' '.join(succ)}")]))


async def GroupUnBlockMember(app:GraiaMiraiApplication,event:GroupMessage,regexResult=regexPlain(r"^#解除拉黑([\s]*[\d]*)*$")):
    quoted=event.messageChain.get(Source)
    if not checkMemberPermission(app,event.sender,[MemberPerm.Administrator,MemberPerm.Owner],quoted):
        return 
    target=re.findall(r"[\d]*",regexResult.match)
    succ=[]
    for i in target:
        times=GetMemberStatusFromGrouBlockDB(app,event.sender.group,i,"Blocked")
        if times==None:
            return
        if not InsertMemberStatusToGroupBlockDB(app,event.sender.group,i,"Blocked",0):
            return
        succ.append(i.id)
    await app.sendGroupMessage(event.sender.group,MessageChain.create([
        Plain(f"操作完成.解除拉黑的对象为:\n{' '.join(succ)}")]))

    

def AddGroupBlockList(bcc:Broadcast):
    bcc.receiver("GroupMessage",headless_decoraters=[strictPlainCommand("#警告")])(GroupWarnMember)
    bcc.receiver("GroupMessage",headless_decoraters=[strictPlainCommand("#删除警告")])(GroupCancelWarnMember)
    bcc.receiver("GroupMessage",headless_decoraters=[strictPlainCommand("#拉黑")])(GroupBlockMember)
    bcc.receiver("GroupMessage",headless_decoraters=[strictPlainCommand("#解除拉黑")])(GroupUnBlockMember)
