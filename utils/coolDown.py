import datetime
from typing import Any, Dict, Optional
from graia.broadcast.builtin.decorators import Decorator, DecoratorInterface
from graia.broadcast.interfaces.dispatcher import DispatcherInterface, BaseDispatcher, IDispatcherInterface
from graia.broadcast.exceptions import ExecutionStop
from types import TracebackType


class CoolDownDecorator(Decorator):
    pre = True
    cool_down_time: datetime.timedelta
    cool_down_id: Any

    def __init__(self, cool_down_time: datetime.timedelta, cool_down_id: Any):
        self.cool_down_time = cool_down_time
        self.cool_down_id = cool_down_id

    def target(self, interface: DecoratorInterface):
        last_time = interface.local_storage.get(self.cool_down_id)
        time = datetime.datetime.today()
        if last_time and time - last_time <= self.cool_down_time:
            if interface.name:
                return False
            raise ExecutionStop()
        interface.local_storage[self.cool_down_id] = time
        return True


class CoolDownDispatcher(BaseDispatcher):
    always = True
    local_storage: Dict[Any, Any] = {}
    cool_down_time: datetime.timedelta
    cool_down_id: Any

    def __init__(self, cool_down_time: datetime.timedelta, cool_down_id: Any, target_name: str):
        self.cool_down_time = cool_down_time
        self.cool_down_id = cool_down_id
        self.cool_down_target = target_name
        self.result = False

    def beforeExecution(self, interface: IDispatcherInterface):
        last_time = self.local_storage.get(self.cool_down_id)
        time = datetime.datetime.today()
        self.result = False
        if not last_time or time - last_time > self.cool_down_time:
            self.result = True

    def afterExecution(self, interface: IDispatcherInterface, exception: Optional[Exception], tb: Optional[TracebackType]):
        if exception is None and self.result == True:
            self.result = False
            self.local_storage[self.cool_down_id] = datetime.datetime.today()

    async def catch(self, interface: DispatcherInterface):
        if self.cool_down_target and self.cool_down_target == interface.name:
            return self.result
