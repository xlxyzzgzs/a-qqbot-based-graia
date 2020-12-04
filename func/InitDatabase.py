from graia.application import GraiaMiraiApplication
from graia.broadcast import Broadcast
from graia.application.event.lifecycle import ApplicationLaunched
from utils.database import InitGroupDataBase

async def InitDataBase(app:GraiaMiraiApplication):
    await InitGroupDataBase(app)

def AddInitDatabaseListener(bcc:Broadcast):
    bcc.receiver(ApplicationLaunched)(InitGroupDataBase)