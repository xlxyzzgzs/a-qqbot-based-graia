import asyncio

from graia.saya import Saya
from graia.broadcast import Broadcast
from graia.saya.builtins.broadcast import BroadcastBehaviour
from graia.application.entry import GraiaMiraiApplication
from config import connection_config

loop = asyncio.get_event_loop()
broadcast = Broadcast(loop=loop)
saya = Saya(broadcast)
saya.install_behaviours(BroadcastBehaviour(broadcast))

app = GraiaMiraiApplication(
    broadcast=broadcast, connect_info=connection_config(), enable_chat_log=True, debug=True
)

with saya.module_context():
    saya.require("modules.module_as_file")

try:
    app.launch_blocking()
except KeyboardInterrupt:
    exit()
