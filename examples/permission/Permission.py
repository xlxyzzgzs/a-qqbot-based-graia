import aiosqlite
import asyncio
from pydantic import BaseModel
from typing import Optional, Dict, Union, NoReturn, Sequence, List
from .PermissionConfig import DEFAULT_ROOT_PERMISSION_USER, DATEBASE_PATH, ROOT_PERMISSION_ID
"""
Permissions :
┌────────────┬───────────┬────────────────┐
│PermissionId│Description│PermissionParent│
├────────────┼───────────┼────────────────┤
│TEXT        │TEXT       │TEXT            │
└────────────┴───────────┴────────────────┘

CommandPermission :
┌────────────┬───────────┐
│PermissionId│PermitteeId│
├────────────┼───────────┤
│TEXT        │TEXT       │
└────────────┴───────────┘


Permission/Permittee format like mirai-console


"""
BOT_MASTER = 123456789


class PermissionId(BaseModel):
    id: str
    description: str = ""
    parent: Optional["PermissionId"] = None

    def __str__(self):
        return self.id

    def __repr__(self):
        return self.id

    def __hash__(self):
        return self.id

    def __eq__(self, other):
        return True if self.id == other.id else False

    def get_all_parents(self):
        if not self.parent is None:
            yield from self.parent.get_all_parents_with_self()

    def get_all_parents_with_self(self):
        yield self
        yield from self.get_all_parents()

    async def write_permission_into_dataBase(self, db: Optional[aiosqlite.Connection] = None):
        if db is None:
            async with aiosqlite.connect(DATEBASE_PATH) as db:
                return await write_permission_into_dataBase(db, self)
        return await write_permission_into_dataBase(db, self)


PermissionId.update_forward_refs()


class PermissionCache():
    permissions: Dict[str, PermissionId] = {}


async def init_permission_database(db: aiosqlite.Connection):
    try:
        global ROOT_PERMISSION
        ROOT_PERMISSION = PermissionId(
            id=ROOT_PERMISSION_ID, description="ROOT_PERMISSION")
        PermissionCache.permissions[ROOT_PERMISSION_ID] = ROOT_PERMISSION

        await db.execute('''
            CREATE TABLE IF NOT EXISTS CommandPermission (
                PermissionId TEXT NOT NULL,
                PermitteeId TEXT NOT NULL
            )
            ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS Permissions (
                PermissionId TEXT NOT NULL,
                Description TEXT,
                PermissionParent TEXT NOT NULL
            )
            ''')
        cursor = await db.execute('''
            SELECT PermissionId From CommandPermission
            WHERE PermissionId=?
        ''', (ROOT_PERMISSION.id,))
        row = await cursor.fetchone()
        if not row:
            await db.execute('''
                INSERT INTO CommandPermission (PermissionId,PermitteeId)
                VALUES (?,?)
            ''', (ROOT_PERMISSION.id, DEFAULT_ROOT_PERMISSION_USER))
    except:
        await db.rollback()
        raise
    finally:
        await db.commit()


async def __write_permission_into_dataBase(db: aiosqlite.Connection, id: str, description: str = "", parent: str = ROOT_PERMISSION_ID) -> NoReturn:
    try:
        async with db.cursor() as cursor:
            await cursor.execute('''
                SELECT * FROM Permissions
                WHERE PermissionId=?
            ''', (id,))
            if await cursor.fetchone():
                await cursor.execute('''
                    UPDATE Permissions SET
                    PermissionId=?,Description=?,PermissionParent=?
                    WHERE PermissionId=?
                ''', (id, description, parent, id))
            else:
                await cursor.execute('''
                    INSERT INTO Permissions (PermissionId,Description,PermissionParent)
                    VALUES (?,?,?)
                ''', (id, description, parent))
    except:
        await db.rollback()
        raise
    finally:
        await db.commit()


async def __load_permission_from_dataBase(db: aiosqlite.Connection, id: str) -> Dict[str, str]:
    try:
        async with db.cursor() as cursor:
            await cursor.execute('''
                SELECT * FROM Permissions
                WHERE PermissionId=?
            ''', (id,))
            row = await cursor.fetchone()
            if row:
                return {"id": row[0], "description": row[1], "parent": row[2]}
            await __write_permission_into_dataBase(db, id)
            return await __load_permission_from_dataBase(db, id)
    except:
        await db.rollback()
        raise
    finally:
        await db.commit()


async def load_permission_from_dataBase(db: aiosqlite.Connection, id: str) -> PermissionId:
    try:
        permission_stack: List[str] = []
        permission_stack.append(id)
        while permission_stack:
            tmp_id = permission_stack[-1]
            if PermissionCache.permissions.get(tmp_id):
                permission_stack.pop()
                continue
            tmp_load = await __load_permission_from_dataBase(db, tmp_id)
            if tmp_p := PermissionCache.permissions.get(tmp_load["parent"]):
                PermissionCache.permissions[tmp_id] = PermissionId(
                    id=tmp_load["id"], description=tmp_load["description"], parent=tmp_p)
                permission_stack.pop()
                continue
            permission_stack.append(tmp_load["parent"])
        return PermissionCache.permissions.get(id)
    except:
        await db.rollback()
        raise
    finally:
        await db.commit()


async def write_permission_into_dataBase(db: aiosqlite.Connection, permission: PermissionId) -> NoReturn:
    if permission.id == ROOT_PERMISSION_ID:
        return  # ROOT_PERMISSION is not changable
    await __write_permission_into_dataBase(db, permission.id, permission.description, permission.parent.id)
    PermissionCache.permissions[permission.id] = permission
    for perm_id in PermissionCache.permissions.keys():
        if PermissionCache.permissions[perm_id].parent and PermissionCache.permissions[perm_id].parent.id == permission.id:
            PermissionCache.permissions[perm_id].parent = permission
