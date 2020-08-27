import sqlite3
from graia.application import GraiaMiraiApplication,Group,Member
from typing import Union,List,Tuple,Optional
from graia.application.group import MemberPerm

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
    except Exception as e:
        app.logger.exception(e)
        conn.rollback()
    finally:
        conn.close()
    return True



def DeleteFromGroupDB(app:GraiaMiraiApplication,group:Group,table:str,paramName:str,param:str)->bool:
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
    except Exception as e:
        app.logger.exception(e)
        result=False
        conn.rollback()
    finally:
        conn.close()
    return result

def CheckIfInGroupDB(app:GraiaMiraiApplication,group:Group,table:str,paramName:str,param:Union[str,int])->bool:
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
        app.logger.exception(e)
        conn.rollback()
    finally:
        conn.close()
    return True if result else False

def GetAllFromGroupDB(app:GraiaMiraiApplication,group:Group,table:str,paramName:str,param:Optional[Union[str,int]]=None)->Optional[Union[str,int]]:
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
        app.logger.exception(e)
        conn.rollback()
    finally:
        conn.close()
    return result

def InsertToGroupDB(app:GraiaMiraiApplication,group:Group,table:str,paramName:str,param:Union[str,int])->bool:
    '''
    用来向 进群答案,群管理 这俩个表中插入数据的.
    '''
    if CheckIfInGroupDB(app,group,table,paramName,param):
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
    except Exception as e:
        app.logger.exception(e)
        result=False
        conn.rollback()
    finally:
        conn.close()
    return result

def UpdateGroupInfoDB(app:GraiaMiraiApplication,group:Group,paramName:str,param:Union[str,int])->bool:
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
    except Exception as e:
        app.logger.exception(e)
        result=False
        conn.rollback()
    finally:
        conn.close()
    return result

def GetFromGroupInfoDB(app:GraiaMiraiApplication,group:Group,paramName:str)->Optional[Union[str,int]]:
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
        app.logger.exception(e)
        conn.rollback()
    finally:
        conn.close()
    return result[0]

def InsertNewGroupToGroupInfoDB(app:GraiaMiraiApplication,group:Group)->bool:
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
    except Exception as e:
        app.logger.exception(e)
        result=False
        conn.rollback()
    finally:
        conn.close()
    return result

def GetMemberStatusFromGrouBlockDB(app:GraiaMiraiApplication,group:Group,target:Member,paramName:str)->int:
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
    except Exception as e:
        app.logger.exception(e)
        conn.rollback()
    finally:
        conn.close()
    return result[0] if result else 0

def InsertMemberStatusToGroupBlockDB(app:GraiaMiraiApplication,group:Group,target:Member,paramName:str,param:int)->bool:
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
    except Exception as e:
        app.logger.exception(e)
        result=False
        conn.rollback()
    finally:
        conn.close()
    return result     

def InsertGroupSentenceIntoDB(app:GraiaMiraiApplication,group:Group,Sentence:str,SentenceID:int)->bool:
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
    except Exception as e:
        app.logger.exception(e)
        result=False
        conn.rollback()
    finally:
        conn.close()
    return result

def GetSentenceFromDBById(app:GraiaMiraiApplication,group:Group,SentenceID:int)->Optional[str]:
    conn=sqlite3.connect("GroupDB.db")
    result=None
    try:
        cursor=conn.cursor()
        cursor.execute(f'''
            SELECT Sentence FROM GroupSentence
            WHERE GroupID=? AND SentenceID=?
        ''',(group.id,SentenceID))
        result=cursor.fetchone()
    except Exception as e:
        app.logger.exception(e)
        conn.rollback()
    finally:
        conn.close()
    return result[0] if result else None

def DeleteSentenceById(app:GraiaMiraiApplication,group:Group,SentenceID:int)->bool:
    conn=sqlite3.connect("GroupDB.db")
    result=False
    try:
        cursor=conn.cursor()
        cursor.execute(f'''
            DELETE FROM GroupSentence WHERE GroupID=? AND SentenceID=?
        ''',(group.id,SentenceID))
        conn.commit()
        result=True
    except Exception as e:
        app.logger.exception(e)
        result=False
        conn.rollback()
    finally:
        conn.close()
    return result

def GetAllFromGroupSentenceDB(app:GraiaMiraiApplication,group:Group)->List[Optional[Tuple[int,str]]]:
    conn=sqlite3.connect("GroupDB.db")
    result=[]
    try:
        cursor=conn.cursor()
        cursor.execute(f'''
            SELECT SentenceID,Sentence From GroupSentence
            WHERE GroupID=?
        ''',group.id)
        result=cursor.fetchall()
    except Exception as e:
        app.logger.exception(e)
        conn.rollback()
    finally:
        conn.close()
    return result

def GetPermissionFromDB(app:GraiaMiraiApplication,member:Member)->str:
    if CheckIfInGroupDB(app,member.group,"GroupPermission","AdminID",member.id):
        return MemberPerm.Administrator
    else:
        return MemberPerm.Member