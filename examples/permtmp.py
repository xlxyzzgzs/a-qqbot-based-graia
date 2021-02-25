from graia.application.entry import GraiaMiraiApplication, GroupMessage
from graia.application.event.lifecycle import ApplicationLaunched
from graia.broadcast import Broadcast
import aiosqlite
import asyncio
import permission as permission_custom


loop = asyncio.get_event_loop()
bcc = Broadcast(loop=loop)
app = GraiaMiraiApplication(
    broadcast=bcc, connect_info=connection_config(), enable_chat_log=True, debug=False
)


@bcc.receiver(ApplicationLaunched)
async def __init_database():
    await permission_custom.init_database()


bcc.receiver("GroupMessage", headless_decorators=[
             permission_custom.MessagePermissionCheckDecorator("测试权限1",)])
