from graia.application.entry import GraiaMiraiApplication
from graia.broadcast import Broadcast
import asyncio
from graia.application.session import Session

loop=asyncio.get_event_loop()
bcc=Broadcast(loop=loop)
app=GraiaMiraiApplication(
    broadcast=bcc,
    connect_info=Session(
        host='http://127.0.0.1:65536',   #你mirai-api-http监听的地址以及端口
        authKey='mirai-api-http-token',      #在mirai-api-http设置的authKey
        account="qq number",             #要使用的对应的bot 的qq号
        websocket=True                  #记得在mirai-api-http里面设置开启websocket
    ),
    enable_chat_log=True,
    debug=True
)
app.launch_blocking()
