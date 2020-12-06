from graia.application.entry import MessageChain, Plain
from graia.broadcast.exceptions import ExecutionStop
from graia.application.message.elements import InternalElement, ExternalElement
from graia.broadcast.builtin.decoraters import Depend
from typing import NoReturn, Union
from functools import reduce
import re


def startWith(param: str) -> callable:
    """
    used in headless_decotator
    """

    @Depend
    def func(messageChain: MessageChain) -> NoReturn:
        p = messageChain.get(Plain)
        if not p or not reduce(
            lambda a, b: bool(a or b),
            map(lambda plain: plain.text.strip().startswith(param), p),
        ):
            raise ExecutionStop()

    return func


def containElement(param: Union[InternalElement, ExternalElement]) -> callable:
    """
    used in headless_decotator
    """

    @Depend
    def func(messageChain: MessageChain) -> NoReturn:
        if not messageChain.get(param):
            raise ExecutionStop()

    return func


def getElements(param: Union[InternalElement, ExternalElement]) -> callable:
    """
    used in headless_decotator
    """

    @Depend
    def func(messageChain: MessageChain) -> NoReturn:
        r = messageChain.get(param)
        if not r:
            raise ExecutionStop()
        return r

    return func


def strictPlainCommand(param: str) -> callable:
    """
    used in headless_decotator
    """

    @Depend
    def func(messageChain: MessageChain) -> NoReturn:
        plains = messageChain.get(Plain)
        haved = False
        for p in plains:
            if p.text.strip() == param:
                haved = True
            elif p.text.strip():
                raise ExecutionStop()
        if not haved:
            raise ExecutionStop()

    return func


def regexPlain(param: str) -> callable:
    """
    used in headless_decotator
    """

    @Depend
    def func(messageChain: MessageChain):
        p = messageChain.get(Plain)
        for i in p:
            if not i.text.strip():
                continue
            t = re.fullmatch(param, i.text.strip())
            if t:
                return t
        else:
            raise ExecutionStop()

    return func
