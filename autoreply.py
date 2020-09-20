from typing import List
from pydantic import BaseModel
import json
class QQButtonAutoReply(BaseModel):
    slot:int
    action_data:str
    name:str
    action:str='notify'
    def __str__(self):
        s=f'''{{"slot":{self.slot},"action_data":"{self.action_data}","name":"{self.name}","action":"{self.action}"}}'''
        return s
    '''
    def __repr__(self):
        return {
            'slot':self.slot,
            'action_data':self.action_data,
            'name':self.name,
            'action':self.action
        }
    '''
    def to_dict(self)->dict:
        return {
            'slot':self.slot,
            'action_data':self.action_data,
            'name':self.name,
            'action':self.action
        }
def GenerateAutoReplyButton(prompt:str,title:str,button:List[QQButtonAutoReply],forward:bool=True,showSender:bool=True):
    button_str=[]
    for b in button:
        button_str.append(b.to_dict())
    content=f'''{{"app":"com.tencent.autoreply","desc":"","view":"autoreply","ver":"0.0.0.1","prompt":"{prompt}","meta":{{"metadata":{{"title":"{title}","buttons":{json.dumps(button_str)},"type":"guest"}}}},"config":{{"forward":{1 if forward else 0},"showSender":{1 if showSender else 0}}}}}'''
    return content