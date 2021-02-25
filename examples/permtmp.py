from permission.Permission import init_permission_database, load_permission_from_dataBase, PermissionCache
import aiosqlite
import asyncio


async def main():
    async with aiosqlite.connect("CommandPermission.db") as db:
        await init_permission_database(db)
        await load_permission_from_dataBase(db, "test")
        print(PermissionCache.permissions)
asyncio.get_event_loop().run_until_complete(main())
