from graia.broadcast.entities.dispatcher import BaseDispatcher
from typing import Callable, Any, Hashable
from graia.broadcast.utilles import isasyncgen, iscoroutinefunction, isgenerator
from graia.broadcast.interfaces.dispatcher import DispatcherInterface
from graia.broadcast.entities.signatures import Force
import inspect


class CustomDispatcher(BaseDispatcher):
    always = True

    def __init__(self, custom_function: Callable[[Any], Any], *, target_name=None, target_annotation=None):
        self.custom_function = custom_function
        self.target_name = target_name
        self.target_annotation = target_annotation

    async def catch(self, interface: DispatcherInterface):
        if self.target_name and self.target_name != interface.name:
            return
        elif self.target_annotation and self.target_annotation != interface.annotation:
            return
        elif not self.target_name and not self.target_annotation:
            return
        result = await interface.broadcast.Executor(
            target=self.custom_function,
            event=interface.event,
            post_exception_event=True,
            use_inline_generator=True
        )

        result_is_asyncgen = [inspect.isasyncgen,
                              isasyncgen][isinstance(result, Hashable)](result)
        result_is_generator = [inspect.isgenerator,
                               isgenerator][isinstance(result, Hashable)](result)
        if result_is_asyncgen or (result_is_generator and not iscoroutinefunction(self.custom_function)):
            if result_is_generator(result):
                for i in result:
                    yield Force(i)
            elif result_is_asyncgen(result):
                async for i in result:
                    yield Force(i)
        yield Force(result)
