from graia.broadcast import Broadcast
from .AnswerBook import AddAnswerBookListener
from .BotHelp import AddBotHelpListener
from .GroupAdmin import AddGroupAdminListener
from .GroupAnswer import AddGroupAnswerListener
from .GroupAppMessageToUrl import AddAppToUrlListener
from .GroupBlockList import AddGroupBlockListListener
from .GroupConfigChange import AddGroupConfigChangeListener
from .GroupMuteMember import AddGroupMuteMemberListener
from .GroupSentence import AddGroupSentenceListener
from .InitDatabase import AddInitDatabaseListener
from .InviteBot import AddInviteBotListener
from .MemberJoin import AddMemberJoinEventListener
from .recallMessage import AddRecallMessageListener
from .Sleep import AddGroupSleepListener


def AddListener(bcc: Broadcast):
    AddAnswerBookListener(bcc)
    AddBotHelpListener(bcc)
    AddGroupAdminListener(bcc)
    AddGroupAnswerListener(bcc)
    AddAppToUrlListener(bcc)
    AddGroupBlockListListener(bcc)
    AddGroupConfigChangeListener(bcc)
    AddGroupMuteMemberListener(bcc)
    AddGroupSentenceListener(bcc)
    AddInitDatabaseListener(bcc)
    AddInviteBotListener(bcc)
    AddMemberJoinEventListener(bcc)
    AddRecallMessageListener(bcc)
    AddGroupSleepListener(bcc)
    pass
