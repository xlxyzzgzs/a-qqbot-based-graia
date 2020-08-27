# a-qqbot-based-graia
一个基于 graia-application 编写的qqbot <br/>
根据AGPL 3.0,源码放在了这里. <br/> 

```
pip install graia-application-mirai --upgrade 
pip install graia-broadcast --upgrade
pip install graia-template
pip install graia-component-selector
pip install httpx
pip install pycryptodome
pip install singledispatchmethod
```
一个写的死烂的代码,就这样吧

忽然想起来一个问题,bot.py引入了一个config.py 就放在这得了(不传github了

```
from graia.application.session import Session
def connection_config():
    return Session(
        host='host:port',       #你mirai-api-http监听的地址以及端口
        authKey='authToken',    #在mirai-api-http设置的authKey
        account=123456789,      #要使用的对应的bot 的qq号
        websocket=True          #记得在mirai-api-http里面设置开启websocket
    ) 
```
将上面的对应项修改成需要的,跟bot.py放在同一个目录

网易云的查找借口来自 
<<<<<<< HEAD
项目链接 : https://github.com/darknessomi/musicbox/tree/master
=======
项目链接 : https://github.com/darknessomi/musicbox/tree/master(https://github.com/darknessomi/musicbox/tree/master

## MIT License

Copyright (c) 2018 omi <mailto:4399.omi@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
>>>>>>> b2b9f8ad6c865a1ad597bef4040d441e304b9515
