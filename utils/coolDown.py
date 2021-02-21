from graia.broadcast.builtin.decorators import Decorator, DecoratorInterface
from graia.broadcast.builtin.dispatchers
from typing import Any, Optional
import datetime
from asyncio import Lock


class CoolDown(Decorator):
    pre = True
    cool_down_time: datetime.timedelta
    cool_down_id: Any
    cool_down_lock: Optional[Lock]

    def __init__(self, cool_down_time: datetime.timedelta, cool_down_id: Any, *, cool_down_lock: Optional[Lock] = None):
        self.cool_down_time = cool_down_time
        self.cool_down_id = cool_down_id
        self.cool_down_lock = cool_down_lock

    def target(self, interface: DecoratorInterface):
        last_time = interface.local_storage.get(self.cool_down_id)
        time = datetime.datetime.today()
        if last_time and time - last_time <= self.cool_down_time:
            raise ExecutionStop()
        interface.local_storage[self.cool_down_id] = time
        return True
