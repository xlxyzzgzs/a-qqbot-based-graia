import aiosqlite
import asyncio
from typing import Iterable, NoReturn
from .Permission import load_permission_from_dataBase, PermissionId
from .Permittee import PermitteeId


async def __check_permittee_permission(db: aiosqlite.Connection, permission: PermissionId, permittee: PermitteeId) -> bool:
    async with db.execute('''
        SELECT * FROM CommandPermission
                WHERE PermissionId=? AND PermitteeId=?
    ''', (permission.id, permittee.id)) as cursor:
        if await cursor.fetchone():
            return True
        return False


async def __get_permittee_from_database(db: aiosqlite.Connection, permission: PermissionId) -> Iterable[PermitteeId]:
    async with db.cursor() as cursor:
        await cursor.execute('''
                SELECT * FROM CommandPermission
                WHERE PermissionId=?
            ''', (permission.id,))
        async for row in cursor:
            yield PermitteeId(id=row[1], directParents=tuple())


async def __get_permission_from_database(db: aiosqlite.Connection, permittee: PermitteeId) -> Iterable[PermissionId]:
    async with db.cursor() as cursor:
        await cursor.execute('''
                    SELECT * FROM CommandPermission
                    WHERE PermissionId=?
                ''', (permittee.id,))
        async for row in cursor:
            yield await load_permission_from_dataBase(db, row[0])


async def __set_permission_with_permittee(db: aiosqlite.Connection, permission: PermissionId, permittee: PermitteeId) -> NoReturn:
    try:
        if await __check_permittee_permission(db, permission, permittee):
            return
        async with db.cursor() as cursor:
            cursor.execute('''
                INSERT INTO CommandPermission (PermissionId,PermitteeId)
                VALUES (?,?)
            ''', (permission.id, permittee.id))
    except:
        await db.rollback()
        raise
    finally:
        await db.commit()


async def check_permission(db: aiosqlite.Connection, permission: PermissionId, permittee: PermitteeId):
    async for _permittee in permittee.get_all_parents_with_self():
        async for _permission in permission.get_all_parents_with_self():
            if await __check_permittee_permission(db, _permission.id, _permittee.id):
                return True
    return False
