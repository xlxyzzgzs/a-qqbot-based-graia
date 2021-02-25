from graia.broadcast.interfaces.decorator import Decorator, DecoratorInterface
from graia.broadcast.interfaces.dispatcher import DispatcherInterface, BaseDispatcher
from graia.broadcast.exceptions import ExecutionStop
from graia.application.entry import FriendMessage, GroupMessage, TempMessage
from typing import Optional
import aiosqlite
from .PermissionConfig import DATEBASE_PATH
from .Permission import load_permission_from_dataBase, PermissionId, PermissionCache, write_permission_into_dataBase
from .Permittee import friend_message_permittee, group_message_permittee, temp_message_permittee, str_to_permittee
from .CheckPermission import check_permission, __set_permission_with_permittee


class MessagePermissionCheckDecorator(Decorator):
    pre = True
    need_load_from_database: bool = True
    permission_id: str
    description: Optional[str]
    permission_parent_id: Optional[str]
    permission: Optional[PermissionId]

    def __init__(self, permission: str, description: Optional[str] = None, parent: Optional[str] = None):
        self.need_load_from_database = True
        self.permission_id = permission
        self.description = description
        self.permission_parent_id = parent
        self.permission = None

    async def target(self, interface: DecoratorInterface):
        if self.need_load_from_database:
            self.need_load_from_database = False
            await self.__load_permission_from_dataBase()
        self.permission = PermissionCache.get(self.permission_id)
        async with aiosqlite.connect(DATEBASE_PATH) as db:
            if await check_permission(db, self.permission, self.__make_permittee(interface.event)):
                return True
            if interface.name:
                return False
            raise ExecutionStop()

    def __make_permittee(self, event):
        if isinstance(event, FriendMessage):
            return friend_message_permittee(event)
        elif isinstance(event, GroupMessage):
            return group_message_permittee(event)
        elif isinstance(event, TempMessage):
            return temp_message_permittee(event)
        else:
            raise ValueError("use this class on message event")

    async def __load_permission_from_dataBase(self):
        async with aiosqlite.connect(DATEBASE_PATH) as db:
            self.permission = await load_permission_from_dataBase(db, self.permission_id)
            if not self.description is None:
                self.permission.description = self.description
            if not self.permission_parent_id is None:
                p_perm = await load_permission_from_dataBase(db, self.permission_parent_id)
                self.permission.parent = p_perm
            write_permission_into_dataBase(db, self.permission)


class MessagePermissionCheckDispatcher(BaseDispatcher):
    always = True
    need_load_from_database: bool = True
    permission_id: str
    description: Optional[str]
    permission_parent_id: Optional[str]
    permission: Optional[PermissionId]
    allow: bool
    target_name: str

    def __init__(self, target_name: str, permission: str, description: Optional[str] = None, parent: Optional[str] = None):
        self.need_load_from_database = True
        self.target_name = target_name
        self.permission_id = permission
        self.description = description
        self.permission_parent_id = parent
        self.permission = None
        self.allow = False

    async def beforeExecution(self, interface: DispatcherInterface):
        self.allow = False
        if self.need_load_from_database:
            self.need_load_from_database = False
            await self.__load_permission_from_dataBase()
        self.permission = PermissionCache.get(self.permission_id)
        async with aiosqlite.connect(DATEBASE_PATH) as db:
            if await check_permission(db, self.permission, self.__make_permittee(interface.event)):
                self.allow = True

    async def catch(self, interface: DispatcherInterface):
        if self.target_name and interface.name == self.target_name:
            return self.allow

    def __make_permittee(self, event):
        if isinstance(event, FriendMessage):
            return friend_message_permittee(event)
        elif isinstance(event, GroupMessage):
            return group_message_permittee(event)
        elif isinstance(event, TempMessage):
            return temp_message_permittee(event)
        else:
            raise ValueError("use this class on message event")

    async def __load_permission_from_dataBase(self):
        async with aiosqlite.connect(DATEBASE_PATH) as db:
            self.permission = await load_permission_from_dataBase(db, self.permission_id)
            if not self.description is None:
                self.permission.description = self.description
            if not self.permission_parent_id is None:
                p_perm = await load_permission_from_dataBase(db, self.permission_parent_id)
                self.permission.parent = p_perm
            write_permission_into_dataBase(db, self.permission)


async def set_permission_with_permittee(permission: str, permittee: str):
    async with aiosqlite.connect(DATEBASE_PATH) as db:
        try:
            permission = await load_permission_from_dataBase(db, permission)
            permittee = str_to_permittee(permittee)
            __set_permission_with_permittee(db, permission, permittee)
        except:
            await db.rollback()
            raise
        finally:
            await db.commit()


async def set_permission(permission: str, description: str = "", parent: str = "ROOT_PERMISSION") -> NoReturn:
    async with aiosqlite.connect(DATEBASE_PATH) as db:
        try:
            p_perm = await load_permission_from_dataBase(db, parent)
            perm = PermissionId(
                id=permission, description=description, parent=p_perm)
            await write_permission_into_dataBase(db, perm)
        except:
            await db.rollback()
            raise
        finally:
            await db.commit()


async def get_permission(permission: str) -> PermissionId:
    async with aiosqlite.connect(DATEBASE_PATH) as db:
        try:
            return await load_permission_from_dataBase(db, permission)
        except:
            await db.rollback()
            raise
        finally:
            await db.commit()
