import httpx
from html.parser import HTMLParser
import asyncio

'''
直接调用的接口,想大范围使用还得去找站长同意
原网址: "https://www.daanshu.com/"
'''

class daanshuHtmlParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self._flags=""
        self.result=""

    def handle_starttag(self,tag,attrs):
        if tag=="div" and attrs.__contains__(("class","content")):
            self._flags="div"
        elif self._flags=="div" and tag=="p":
            self._flags="p"
    
    def handle_data(self,data):
        if self._flags=="p" :
            self.result=data
    
    def handle_endtag(self,tag):
        self._flags=""

async def AskDaanshu(question:str)->str:
    url="https://www.daanshu.com/"
    question={"text":question}
    async with httpx.AsyncClient() as client:
        r=await client.post(url,data=question)
    parser=daanshuHtmlParser()
    parser.feed(r.text)
    parser.close()
    return parser.result.strip()