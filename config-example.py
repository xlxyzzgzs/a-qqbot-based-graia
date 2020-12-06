from graia.application.session import Session


def connection_config():
    return Session(
        host="http://127.0.0.1:65536",  # 你mirai-api-http监听的地址以及端口
        authKey="mirai-api-http-token",  # 在mirai-api-http设置的authKey
        account=123456789,  # 要使用的对应的bot 的qq号
        websocket=True,  # 记得在mirai-api-http里面设置开启websocket
    )


BotMaster = [123456789]  # 在某些场合会有特权
BotAdmin = [123465789]  # 在某些场合会有特权
