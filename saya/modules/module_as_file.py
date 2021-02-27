from graia.saya import Saya, Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.saya.event import SayaModuleInstalled
from graia.application.entry import FriendMessage, GraiaMiraiApplication, MessageChain, Plain

saya = Saya.current()
channel = Channel.current()


@channel.use(ListenerSchema(
    listening_events=[SayaModuleInstalled]
))
async def module_listener(event: SayaModuleInstalled):
    print(f"{event.module}::模块加载成功!!!")


@channel.use(ListenerSchema(listening_events=[FriendMessage]))
async def hello_world(app: GraiaMiraiApplication, event: FriendMessage):
    await app.sendFriendMessage(event.sender, MessageChain.create([Plain("hello world")]))
