from graia.broadcast.interrupt import InterruptControl
from graia.broadcast import Broadcast


def InitInterruptControl(bcc: Broadcast):
    global interruptcontrol
    interruptcontrol = InterruptControl(bcc)
