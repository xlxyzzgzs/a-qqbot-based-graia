from graia.application.entry import GraiaMiraiApplication,MessageChain,MemberPerm,Plain,Group,Source,Member,At
from graia.broadcast import Broadcast,DispatcherInterface
from graia.broadcast.exceptions import ExecutionStop
from graia.application.message.elements import InternalElement,ExternalElement
from graia.application.event.mirai import MiraiEvent
from typing import Union,Optional,List,Tuple,NoReturn
import random
from functools import reduce
import re
import sqlite3
import json

from database import GetPermissionFromDB


def At__Hash(self):
    return self.target
At.__hash__=At__Hash

def startWith(param:str)->callable:
    def func(messageChain:MessageChain)->NoReturn:
        p=messageChain.get(Plain)
        if not p or not  reduce(lambda a,b: bool(a or b),map(lambda plain:plain.text.strip().startswith(param),p)) :
            raise ExecutionStop()
    return func

def containElement(param:Union[InternalElement,ExternalElement])->callable:
    def func(messageChain:MessageChain)->NoReturn:
        if not messageChain.get(param):
            raise ExecutionStop()
    return func

def getElements(param:Union[InternalElement,ExternalElement])->callable:
    def func(messageChain:MessageChain)->NoReturn:
        r=messageChain.get(param)
        if not r:
            raise ExecutionStop()
        return r
    return func

def strictPlainCommand(param:str)->callable:
    def func(messageChain:MessageChain)->NoReturn:
        plains=messageChain.get(Plain)
        haved=False
        for p in plains:
            if p.text.strip()==param:
                haved=True
            elif p.text.strip():
                raise ExecutionStop()
        if not haved:
            raise ExecutionStop()
    return func

def regexPlain(param:str)->callable:
    def func(messageChain:MessageChain):
        p=messageChain.get(Plain)
        for i in p:
            if not i.text.strip():
                continue
            t=re.fullmatch(param,i.text.strip())
            if t:
                return t
        else :
            raise ExecutionStop()
    return func

async def checkBotPermission(app:GraiaMiraiApplication,group:Group,needPermission:List[str],quote:Optional[Union[Source,int]]=None)->bool:
    PermissionDict={
        MemberPerm.Member:'普通群员',
        MemberPerm.Administrator:'管理员',
        MemberPerm.Owner:'群主'
    }
    if group.accountPerm in needPermission:
        return True
    await app.sendGroupMessage(group,MessageChain.create([
        Plain(f'请求失败,机器人在群组中不具备需要的权限.\n需要的权限为:{"或".join([PermissionDict[i] for i in needPermission])}')
    ]),quote=quote)

async def getTargetFromAt(app:GraiaMiraiApplication,group:Group,messageChain:MessageChain)->List[Member]:
    target=set(messageChain.get(At))
    new_target=[]
    for i in target:
        t=await app.getMember(group,i.target)
        if not t:
            t=Member(id=i.target,memberName='UnknownName',permission=MemberPerm.Member,group=group)
        new_target.append(t)
    return new_target

async def checkMemberPermission(app:GraiaMiraiApplication,member:Member,needPermission:List[str],quote:Optional[Union[Source,int]]=None)->bool:
    PermissionDict={
        MemberPerm.Member:'普通群员',
        MemberPerm.Administrator:'管理员',
        MemberPerm.Owner:'群主'
    }
    if member.permission in needPermission or GetPermissionFromDB(app,member) in needPermission:
        return True
    await app.sendGroupMessage(member.group,MessageChain.create([
        Plain(f'请求失败,你在群组中不具备需要的权限.\n需要的权限为:{"或".join([PermissionDict[i] for i in needPermission])}')
    ]),quote=quote)

async def muteMember(app:GraiaMiraiApplication,group:Group,target:Member,time:int,quote:Optional[Union[Source,int]]=None)->bool:
    #time is minute
    if not await checkBotPermission(app,group,[MemberPerm.Owner,*([MemberPerm.Administrator] if target.permission==MemberPerm.Member else [] )],quote):
        return False
    if time <= 0 or time >= 43200 :
        time=random.randint(1,43199),
    try:
        await app.mute(group,target,int(time*60))
    except Exception as e:
        print(e)
        return False
    return True

async def unMuteMember(app:GraiaMiraiApplication,group:Group,target:Member,quote:Optional[Union[Source,int]]=None)->bool:
    if not await checkBotPermission(app,group,[MemberPerm.Owner,*([MemberPerm.Administrator] if target.permission==MemberPerm.Member else [] )],quote):
        return False
    try:
        await app.unmute(group,target)
    except Exception as e:
        app.logger.exception(e)
        return False
    return True

async def kickMember(app:GraiaMiraiApplication,group:Group,target:Member,quote:Optional[Union[Source,int]]=None)->bool:
    if not await checkBotPermission(app,group,[MemberPerm.Owner,*([MemberPerm.Administrator] if target.permission==MemberPerm.Member else [] )],quote):
        return False
    try:
        await app.kick(group,target)
    except Exception as e:
        app.logger.exception(e)
        return False
    return True

async def GroupSettingChanged(app:GraiaMiraiApplication,event:MiraiEvent,
    enable:Optional[MessageChain]=None,
    disable:Optional[MessageChain]=None,
    invalid:Optional[MessageChain]=None):
    if event.origin==event.current and invalid:
        await app.sendGroupMessage(event.group,invalid)
    elif event.current==True and enable:
        await app.sendGroupMessage(event.group,enable)
    elif event.current==False and disable:
        await app.sendGroupMessage(event.group,disable)
    elif invalid:
        await app.sendGroupMessage(event.group,invalid)

async def MessageChainToStr(messageChain:MessageChain,skipStrInPlain:Optional[str]=None)->str:
    '''
    将 MessageChain 转成 str 方便存储的类型.
    '''
    result=await messageChain.asSendable().build()
    result=result.dict()['__root__']
    for i in range(len(result)):
        if result[i]["type"]=='Plain' and skipStrInPlain:
            result[i]["text"]=result[i]["text"].replace(skipStrInPlain,"")
    return json.dumps(result)

def StrToMessageChain(origin:str)->MessageChain:
    '''
    将 str 转成 MessageChain
    '''
    return MessageChain.parse_obj(json.loads(origin)).asMutable()

