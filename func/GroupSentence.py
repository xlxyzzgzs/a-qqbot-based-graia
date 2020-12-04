from graia.application.entry import GraiaMiraiApplication,GroupMessage,Plain,Source,MessageChain
from graia.broadcast import Broadcast
from utils.database import InsertGroupSentenceIntoDB,UpdateGroupInfoDB,DeleteSentenceById,GetSentenceFromDBById
from utils.database import GetFromGroupInfoDB
from utils.messageConvert import MessageChainToStr,StrToMessageChain
from utils.messageTrigger import startWith,regexPlain,strictPlainCommand
from random import randint

async def GroupAddSentence(app:GraiaMiraiApplication,event:GroupMessage):
    quoted=event.messageChain.get(Source)[0]
    message= await MessageChainToStr(event.messageChain,"#添加群语录")
    SentenceID=GetFromGroupInfoDB(app,event.sender.group,"SentenceID")
    SentenceID+=1
    reply=[]
    if InsertGroupSentenceIntoDB(app,event.sender.group,message,SentenceID):
        if UpdateGroupInfoDB(app,event.sender.group,"SentenceID",SentenceID):
            reply=[Plain(f"语录插入成功,ID为{SentenceID}")]
        else :
            if not DeleteSentenceById(app,event.sender.group,SentenceID):
                reply=[Plain("发生了某些未知问题,建议去寻找管理")]
    else:
        reply=[Plain("语录插入失败")]
    await app.sendGroupMessage(event.sender.group,MessageChain.create(reply),quote=quoted)
    
async def GroupShowSentence(app:GraiaMiraiApplication,event:GroupMessage,regexResult=regexPlain(r"^#群语录[\s]*([\d][\d]*)$")):
    quoted=event.messageChain.get(Source)[0]
    SentenceID=int(regexResult.groups()[0])
    result=GetSentenceFromDBById(app,event.sender.group,SentenceID)
    if result:
        result=StrToMessageChain(result)
    else :
        result=MessageChain.create([
            Plain(f"ID为{SentenceID}的语录不存在")
        ])
    await app.sendGroupMessage(event.sender.group,result,quote=quoted)


async def GroupDeleteSentence(app:GraiaMiraiApplication,event:GroupMessage,regexResult=regexPlain(r"^#删除语录[\s]*([\d]*)")):
    quoted=event.messageChain.get(Source)[0]
    SentenceID=int(regexResult.groups()[0])
    message=GetSentenceFromDBById(app,event.sender.group,SentenceID)
    if message:
        message=StrToMessageChain(message)
    else:
        message=MessageChain.create([])
    if DeleteSentenceById(app,event.sender.group,SentenceID):
        message.__root__.insert(0,Plain("语录删除成功,原内容为:\n"))
    else :
        message.__root__.insert(0,Plain("语录删除失败"))
    await app.sendGroupMessage(event.sender.group,message,quote=quoted)

async def GroupRandomSentence(app:GraiaMiraiApplication,event:GroupMessage):
    quoted=event.messageChain.get(Source)[0]
    SentenceID=GetFromGroupInfoDB(app,event.sender.group,"SentenceID")
    SentenceID=randint(1,SentenceID)
    result=GetSentenceFromDBById(app,event.sender.group,SentenceID)
    if result:
        result=StrToMessageChain(result)
    else :
        result=MessageChain.create([
            Plain(f"ID为{SentenceID}的语录不存在")
        ])
    await app.sendGroupMessage(event.sender.group,result,quote=quoted)

def AddGroupSentenceListener(bcc:Broadcast):
    bcc.receiver("GroupMessage",headless_decoraters=[startWith("#添加群语录")])(GroupAddSentence)
    bcc.receiver("GroupMessage")(GroupShowSentence)
    bcc.receiver("GroupMessage")(GroupDeleteSentence)
    bcc.receiver("GroupMessage",headless_decoraters=[strictPlainCommand("#随机语录")])(GroupRandomSentence)
    