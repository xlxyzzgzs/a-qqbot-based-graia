from graia.component import Components
from graia.application.entry import *
from graia.broadcast import Broadcast
from graia.application.entities import UploadMethods
from graia.template import Template
from graia.broadcast.builtin.decoraters import Depend
from graia.broadcast.exceptions import ExecutionStop
from graia.application.message.elements import InternalElement,ExternalElement
from graia.application.event.mirai import *
import asyncio
from pathlib import Path
from typing import *
from datetime import *
import random
from functools import reduce
import re
import sqlite3
import json
from html.parser import HTMLParser

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

def getPermissionFromDB(member:Member)->str:
    if CheckIfInGroupDB(member.group,"GroupPermission","AdminID",member.id):
        return MemberPerm.Administrator
    else:
        return MemberPerm.Member

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
    if member.permission in needPermission or getPermissionFromDB(member) in needPermission:
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
        await app.mute(group,target,time*60)
    except Exception as e:
        return False
    return True

async def unMuteMember(app:GraiaMiraiApplication,group:Group,target:Member,quote:Optional[Union[Source,int]]=None)->bool:
    #time is minute
    if not await checkBotPermission(app,group,[MemberPerm.Owner,*([MemberPerm.Administrator] if target.permission==MemberPerm.Member else [] )],quote):
        return False
    if time <= 0 or time >= 43200 :
        time=random.randint(1,43199),
    try:
        await app.unmute(group,target)
    except Exception as e:
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

async def InitGroupDataBase(app:GraiaMiraiApplication)->bool:
    '''
    初始化群组的数据库
    '''
    conn=sqlite3.connect("GroupDB.db")
    cursor=conn.cursor()
    try :
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS GroupInfo (
                GroupID INTEGER PRIMARY KEY NOT NULL,
                MemberJoinMessage TEXT,
                LastCommandTime INTEGER NOT NULL,
                SentenceID INTEGER NOT NULL
            )
        ''')
        GroupList=await app.groupList()
        for group in GroupList:
            cursor.execute('''
                SELECT GroupID FROM GroupInfo
                WHERE GroupID=?
            ''',(group.id,))
            if cursor.fetchone():
                continue
            cursor.execute('''
                INSERT INTO GroupInfo (GroupID,LastCommandTime,SentenceID) 
                VALUES (?,0,0)
            ''',(group.id,))
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS GroupAnswer (
                GroupID INTEGER NOT NULL,
                Answer TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS GroupPermission (
                GroupID INTEGER NOT NULL,
                AdminID INTEGER NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS GroupSentence (
                GroupID INTEGER NOT NULL,
                Sentence TEXT NOT NULL,
                SentenceID INTEGER NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS GroupBlockList(
                GroupID INTEGER NOT NULL,
                BlockID INTEGER NOT NULL,
                Warn INTEGER NOT NULL,
                Blocked INTEGER NOT NULL
            )
        ''')
        conn.commit()
    except :
        conn.rollback()
    finally:
        conn.close()
    return True



def DeleteFromGroupDB(group:Group,table:str,paramName:str,param:str)->bool:
    '''
    用来删除 进群答案,群管理 这俩个表中的数据的.
    '''
    conn=sqlite3.connect("GroupDB.db")
    result=False
    try:
        cursor=conn.cursor()
        cursor.execute(f'''
            DELETE FROM {table} WHERE GroupID=? AND {paramName}=?
        ''',(group.id,paramName,param))
        conn.commit()
        result=True
    except:
        result=False
        conn.rollback()
    finally:
        conn.close()
    return result

def CheckIfInGroupDB(group:Group,table:str,paramName:str,param:Union[str,int])->bool:
    '''
    从 进群答案,群管理 这俩个表中查找是否存在 返回 bool
    '''
    conn=sqlite3.connect("GroupDB.db")
    result=None
    try:
        cursor=conn.cursor()
        cursor.execute(f'''
            SELECT {paramName} From {table} WHERE GroupID=? AND {paramName}=?
        ''',(group.id,param))
        result=cursor.fetchone()
    except Exception as e:
        conn.rollback()
    finally:
        conn.close()
    return True if result else False

def GetAllFromGroupDB(group:Group,table:str,paramName:str,param:Optional[Union[str,int]]=None)->Optional[Union[str,int]]:
    '''
    从 进群答案,群管理 这俩个表中查找对应项,存在就返回,不存在返回None.
    '''
    conn=sqlite3.connect("GroupDB.db")
    result=None
    try:
        cursor=conn.cursor()
        cursor.execute(f'''
            SELECT {paramName} From {table} WHERE GroupID=? {('AND '+paramName+' LIKE ? ' if param else '')}
        ''',(group.id,*([param] if param else [])))
        result=cursor.fetchall()
    except Exception as e:
        conn.rollback()
    finally:
        conn.close()
    return result

def InsertToGroupDB(group:Group,table:str,paramName:str,param:Union[str,int])->bool:
    '''
    用来向 进群答案,群管理 这俩个表中插入数据的.
    '''
    if CheckIfInGroupDB(group,table,paramName,param):
        return True
    conn=sqlite3.connect("GroupDB.db")
    result=False
    try:
        cursor=conn.cursor()
        cursor.execute(f'''
            INSERT INTO {table} (GroupID, {paramName})
            VALUES (?,?)
        ''',(group.id,param))
        conn.commit()
        result=True
    except:
        result=False
        conn.rollback()
    finally:
        conn.close()
    return result

def UpdateGroupInfoDB(group:Group,paramName:str,param:Union[str,int])->bool:
    '''
    更新 GroupInfo 表中的数据
    '''
    conn=sqlite3.connect('GroupDB.db')
    result=False
    try:
        cursor=conn.cursor()
        cursor.execute(f'''
            UPDATE GroupInfo SET
            {paramName}=? 
            WHERE GroupID=?
        ''',(param,group.id))
        conn.commit()
        result=True
    except:
        result=False
        conn.rollback()
    finally:
        conn.close()
    return result

def GetFromGroupInfoDB(group:Group,paramName:str)->Optional[Union[str,int]]:
    '''
    从 GroupInfo 中获取信息.
    '''
    conn=sqlite3.connect('GroupDB.db')
    result=None
    try:
        cursor=conn.cursor()
        cursor.execute(f'''
            SELECT {paramName} FROM GroupInfo WHERE GroupID=?
        ''',(group.id,))
        result=cursor.fetchone()
        if result==None:
            cursor.execute(f'''
                INSERT INTO GroupInfo (GroupID,LastCommandTime,SentenceID)
                VALUES (?,0,0)
            ''',group.id)
            conn.commit()
            cursor.execute(f'''
                SELECT {paramName} FROM GroupInfo WHERE GroupID=?
            ''',(group.id,))
            result=cursor.fetchone()
    except Exception as e:
        conn.rollback()
    finally:
        conn.close()
    return result[0]

def InsertNewGroupToGroupInfoDB(group:Group)->bool:
    '''
    向 GroupInfo中插入新项
    '''
    conn=sqlite3.connect("GroupDB.db")
    result=False
    try:
        cursor=conn.cursor()
        cursor.execute(f'''
            INSERT INTO GroupInfo (GroupID,LastCommandTime,SentenceID)
            VALUES (?,0,0)
        ''',(group.id,))
        conn.commit()
        result=True
    except:
        result=False
        conn.rollback()
    finally:
        conn.close()
    return result

def GetMemberStatusFromGrouBlockDB(group:Group,target:Member,paramName:str)->int:
    conn=sqlite3.connect("GroupDB.db")
    result=0
    try:
        cursor=conn.cursor()
        cursor.execute(f'''
            SELECT {paramName} FROM GroupBlockList
            WHERE GroupID=? AND BlockID=?
        ''',(group.id,target.id))
        result=cursor.fetchone()
        if result==None:
            cursor.execute(f'''
                INSERT INTO GroupBlockList (GroupID,BlockID,Warn,Blocked)
                VALUES (?,?,0,0)
            ''',(group.id,target.id))
            conn.commit()
    except:
        conn.rollback()
    finally:
        conn.close()
    return result[0] if result else 0

def InsertMemberStatusToGroupBlockDB(group:Group,target:Member,paramName:str,param:int)->bool:
    conn=sqlite3.connect("GroupDB.db")
    result=False
    try:
        cursor=conn.cursor()
        cursor.execute(f'''
            UPDATE GroupBlockList SET 
            {paramName}=?
            WHERE GroupID=?,BlockID=?
        ''',(param,group.id,target.id))
        conn.commit()
        result=True
    except:
        result=False
        conn.rollback()
    finally:
        conn.close()
    return result     

def InsertGroupSentenceIntoDB(group:Group,Sentence:str,SentenceID:int)->bool:
    conn=sqlite3.connect("GroupDB.db")
    result=False
    try:
        cursor=conn.cursor()
        cursor.execute(f'''
            INSERT INTO GroupSentence (GroupID,Sentence,SentenceID)
            VALUES (?,?,?)
        ''',(group.id,Sentence,SentenceID))
        conn.commit()
        result=True
    except:
        result=False
        conn.rollback()
    finally:
        conn.close()
    return result

def GetSentenceFromDBById(group:Group,SentenceID:int)->Optional[str]:
    conn=sqlite3.connect("GroupDB.db")
    result=None
    try:
        cursor=conn.cursor()
        cursor.execute(f'''
            SELECT Sentence FROM GroupSentence
            WHERE GroupID=? AND SentenceID=?
        ''',(group.id,SentenceID))
        result=cursor.fetchone()
    except:
        conn.rollback()
    finally:
        conn.close()
    return result[0] if result else None

def DeleteSentenceById(group:Group,SentenceID:int)->bool:
    conn=sqlite3.connect("GroupDB.db")
    result=False
    try:
        cursor=conn.cursor()
        cursor.execute(f'''
            DELETE FROM GroupSentence WHERE GroupID=? AND SentenceID=?
        ''',(group.id,SentenceID))
        conn.commit()
        result=True
    except:
        result=False
        conn.rollback()
    finally:
        conn.close()
    return result

def GetAllFromGroupSentenceDB(group:Group)->List[Optional[Tuple[int,str]]]:
    conn=sqlite3.connect("GroupDB.db")
    result=[]
    try:
        cursor=conn.cursor()
        cursor.execute(f'''
            SELECT SentenceID,Sentence From GroupSentence
            WHERE GroupID=?
        ''',group.id)
        result=cursor.fetchall()
    except:
        conn.rollback()
    finally:
        conn.close()
    return result

async def MessageChainToStr(messageChain:MessageChain,skipStrInPlain:Optional[str]=None)->str:
    '''
    将 MessageChain 转成 str 方便存储的类型.
    '''
    result=await messageChain.asSendable().build()
    result=result.dict()['__root__']
    for i in range(len(result)):
        if result[i]["type"]=='Plain' and skipStrInPlain:
            result[i]["text"]=result[i]["text"].replace(skipStrInPlain,"").strip()
    return json.dumps(result)

def StrToMessageChain(origin:str)->MessageChain:
    '''
    将 str 转成 MessageChain
    '''
    return MessageChain.parse_obj(json.loads(origin)).asMutable()

class daanshuHtmlParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self._flags=""
        self.result=""

    def handle_starttag(self,tag,attrs):
        if tag=="div" and attrs.__contains__(("class","content")):
            self._flags="div"
        elif self._flags=="div" and tag=="p":
            self._flags="p"
    
    def handle_data(self,data):
        if self._flags=="p" :
            self.result=data
    
    def handle_endtag(self,tag):
        if self._flags:
            self._flags=""