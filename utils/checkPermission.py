from graia.application.entry import GraiaMiraiApplication,Group,Source,Member,MemberPerm,Plain,MessageChain
from typing import List,Optional,Union
from .database import GetPermissionFromDB
from config import BotAdmin,BotMaster
async def checkBotPermission(app:GraiaMiraiApplication,group:Group,needPermission:List[MemberPerm],quote:Optional[Union[Source,int]]=None)->bool:
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
    return False

async def checkMemberPermission(app:GraiaMiraiApplication,member:Member,needPermission:List[MemberPerm],quote:Optional[Union[Source,int]]=None)->bool:
    PermissionDict={
        MemberPerm.Member:'普通群员',
        MemberPerm.Administrator:'管理员',
        MemberPerm.Owner:'群主'
    }
    if member.permission in needPermission or \
        member in BotAdmin or \
        member in BotMaster or \
        GetPermissionFromDB(app,member) in needPermission:
        return True
    await app.sendGroupMessage(member.group,MessageChain.create([
        Plain(f'请求失败,你在群组中不具备需要的权限.\n需要的权限为:{"或".join([PermissionDict[i] for i in needPermission])}')
    ]),quote=quote)
    return False

