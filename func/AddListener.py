from graia.broadcast import Broadcast
import func
def AddListener(bcc:Broadcast):
    func.AnswerBook.AddAnswerBookListener(bcc)
    func.BotHelp.AddBotHelpListener(bcc)
    func.GroupAdmin.AddGroupAdminListener(bcc)
    func.GroupAnswer.AddGroupAnswerListener(bcc)
    func.GroupAppMessageToUrl.AddAppToUrlListener(bcc)
    func.GroupBlockList.AddGroupBlockList(bcc)
    func.GroupConfigChange.AddGroupConfigChangeListener(bcc)
    func.GroupMuteMember.AddGroupMuteMemberListener(bcc)
    func.GroupSentence.AddGroupSentenceListener(bcc)
    func.InitDatabase.AddInitDatabaseListener(bcc)
    func.InviteBot.AddInviteBotListener(bcc)
    func.MemberJoin.AddMemberJoinEventListener(bcc)
    func.recallMessage.AddRecallMessageListener(bcc)
    func.Sleep.AddGroupSleepListener(bcc)