from graia.application.entry import GraiaMiraiApplication,MessageChain,MemberPerm,Plain,Group,Source,Member,At
from graia.broadcast import Broadcast,DispatcherInterface
from graia.broadcast.exceptions import ExecutionStop
from graia.application.message.elements import InternalElement,ExternalElement
from graia.application.event.mirai import MiraiEvent
from typing import Union,Optional,List,Tuple,NoReturn
import random
from functools import reduce
import re
import json

from .database import GetPermissionFromDB
from .checkPermission import checkBotPermission


def At__Hash(self):
    return self.target
At.__hash__=At__Hash


async def getTargetFromAt(app:GraiaMiraiApplication,group:Group,messageChain:MessageChain)->List[Member]:
    target=set(messageChain.get(At))
    new_target=[]
    tmpDict={}
    data = await app.memberList(group)
    for i in data:
        tmpDict[i.id]=i
    for i in target:
        try:
            t=tmpDict[i.target]
        except KeyError:
            t=Member(id=i.target,memberName='UnknownName',permission=MemberPerm.Member,group=group)
        new_target.append(t)
    return new_target

async def muteMember(app:GraiaMiraiApplication,group:Group,target:Member,time:int,quote:Optional[Union[Source,int]]=None)->bool:
    #time is minute
    if not await checkBotPermission(app,group,[MemberPerm.Owner,*([MemberPerm.Administrator] if target.permission==MemberPerm.Member else [] )],quote):
        return False
    if time <= 0 or time >= 43200 :
        time=random.randint(1,43199),
    try:
        await app.mute(group,target,int(time*60))
    except Exception as e:
        app.logger.exception(e)
        return False
    return True

async def unmuteMember(app:GraiaMiraiApplication,group:Group,target:Member,quote:Optional[Union[Source,int]]=None)->bool:
    if not await checkBotPermission(app,group,[MemberPerm.Owner,*([MemberPerm.Administrator] if target.permission==MemberPerm.Member else [] )],quote):
        return False
    try:
        await app.unmute(group,target)
    except Exception as e:
        app.logger.exception(e)
        return False
    return True

async def muteAll(app:GraiaMiraiApplication,group:Group,quote:Optional[Union[Source,int]]=None)->bool:
    if not await checkBotPermission(app,group,[MemberPerm.Owner,MemberPerm.Administrator],quote):
        return False
    try:
        await app.muteAll(group)
    except Exception as e:
        app.logger.exception(e)
        return False
    return True

async def unmuteAll(app:GraiaMiraiApplication,group:Group,quote:Optional[Union[Source,int]]=None)->bool:
    if not await checkBotPermission(app,group,[MemberPerm.Owner,MemberPerm.Administrator],quote):
        return False
    try:
        await app.unmuteAll(group)
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


