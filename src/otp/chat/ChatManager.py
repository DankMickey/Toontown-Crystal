from direct.directnotify import DirectNotifyGlobal
from direct.fsm import ClassicFSM
from direct.fsm import State
from direct.gui.DirectGui import *
from direct.showbase import DirectObject
from pandac.PandaModules import *
from otp.otpbase import OTPLocalizer
from toontown.chat.ChatGlobals import *


ChatEvent = 'ChatEvent'
NormalChatEvent = 'NormalChatEvent'
SCChatEvent = 'SCChatEvent'
SCCustomChatEvent = 'SCCustomChatEvent'
SCEmoteChatEvent = 'SCEmoteChatEvent'
OnScreen = 0
OffScreen = 1
Thought = 2
ThoughtPrefix = '.'

def isThought(message):
    if len(message) == 0:
        return 0
    elif message.find(ThoughtPrefix, 0, len(ThoughtPrefix)) >= 0:
        return 1
    else:
        return 0


def removeThoughtPrefix(message):
    if isThought(message):
        return message[len(ThoughtPrefix):]
    else:
        return message


class ChatManager(DirectObject.DirectObject):
    notify = DirectNotifyGlobal.directNotify.newCategory('ChatManager')

    def __init__(self, cr, localAvatar):
        self.cr = cr
        self.localAvatar = localAvatar
        self.wantBackgroundFocus = 1
        self.__scObscured = 0
        self.__normalObscured = 0
        self.noTrueFriendsAtAll = None
        self.noTrueFriendsAtAllAndNoWhitelist = None
        self.fsm = ClassicFSM.ClassicFSM('chatManager', [State.State('off', self.enterOff, self.exitOff),
         State.State('mainMenu', self.enterMainMenu, self.exitMainMenu),
         State.State('speedChat', self.enterSpeedChat, self.exitSpeedChat),
         State.State('normalChat', self.enterNormalChat, self.exitNormalChat),
         State.State('whisper', self.enterWhisper, self.exitWhisper),
         State.State('whisperChat', self.enterWhisperChat, self.exitWhisperChat),
         State.State('whisperSpeedChat', self.enterWhisperSpeedChat, self.exitWhisperSpeedChat),
         State.State('noTrueFriendsAtAll', self.enterNoTrueFriendsAtAll, self.exitNoTrueFriendsAtAll),
         State.State('noTrueFriendsAtAllAndNoWhitelist', self.enterNoTrueFriendsAtAllAndNoWhitelist, self.exitNoTrueFriendsAtAllAndNoWhitelist),
         State.State('otherDialog', self.enterOtherDialog, self.exitOtherDialog),
         State.State('whiteListOpenChat', self.enterWhiteListOpenChat, self.exitWhiteListOpenChat),
         State.State('whiteListAvatarChat', self.enterWhiteListAvatarChat, self.exitWhiteListAvatarChat)], 'off', 'off')
        self.fsm.enterInitialState()
        return

    def delete(self):
        self.ignoreAll()
        del self.fsm
        if hasattr(self.chatInputNormal, 'destroy'):
            self.chatInputNormal.destroy()
        self.chatInputNormal.delete()
        del self.chatInputNormal
        self.chatInputSpeedChat.delete()
        del self.chatInputSpeedChat
        if self.noTrueFriendsAtAll:
            self.noTrueFriendsAtAll.destroy()
            self.noTrueFriendsAtAll = None
        if self.noTrueFriendsAtAllAndNoWhitelist:
            self.noTrueFriendsAtAllAndNoWhitelist.destroy()
            self.noTrueFriendsAtAllAndNoWhitelist = None
        del self.localAvatar
        del self.cr
        return

    def obscure(self, normal, sc):
        self.__scObscured = sc
        if self.__scObscured:
            self.scButton.hide()
        self.__normalObscured = normal
        if self.__normalObscured:
            self.normalButton.hide()

    def isObscured(self):
        return (self.__normalObscured, self.__scObscured)

    def stop(self):
        self.fsm.request('off')
        self.ignoreAll()

    def start(self):
        self.fsm.request('mainMenu')

    def announceChat(self):
        messenger.send(ChatEvent)

    def announceSCChat(self):
        messenger.send(SCChatEvent)
        self.announceChat()

    def sendChatString(self, message):
        chatFlags = CFSpeech | CFTimeout
        if isThought(message):
            message = removeThoughtPrefix(message)
            chatFlags = CFThought
        messenger.send(NormalChatEvent)
        self.announceChat()

    def sendWhisperString(self, message, whisperAvatarId):
        pass

    def sendSCChatMessage(self, msgIndex):
        base.talkAssistant.sendOpenSpeedChat(1, msgIndex)

    def sendSCWhisperMessage(self, msgIndex, whisperAvatarId):
        base.talkAssistant.sendAvatarWhisperSpeedChat(1, msgIndex, whisperAvatarId)

    def sendSCCustomChatMessage(self, msgIndex):
        base.talkAssistant.sendOpenSpeedChat(3, msgIndex)

    def sendSCCustomWhisperMessage(self, msgIndex, whisperAvatarId):
        base.talkAssistant.sendAvatarWhisperSpeedChat(3, msgIndex, whisperAvatarId)

    def sendSCEmoteChatMessage(self, emoteId):
        base.talkAssistant.sendOpenSpeedChat(2, emoteId)

    def sendSCEmoteWhisperMessage(self, emoteId, whisperAvatarId):
        base.talkAssistant.sendAvatarWhisperSpeedChat(2, emoteId, whisperAvatarId)

    def enterOff(self):
        self.scButton.hide()
        self.normalButton.hide()
        self.ignoreAll()

    def exitOff(self):
        pass

    def enterMainMenu(self):
        self.checkObscurred()
        if self.localAvatar.canChat() or self.cr.wantMagicWords:
            if self.wantBackgroundFocus:
                self.chatInputNormal.chatEntry['backgroundFocus'] = 1
            self.acceptOnce('enterNormalChat', self.fsm.request, ['normalChat'])

    def checkObscurred(self):
        if not self.__scObscured:
            self.scButton.show()
        if not self.__normalObscured:
            self.normalButton.show()

    def exitMainMenu(self):
        self.scButton.hide()
        self.normalButton.hide()
        self.ignore('enterNormalChat')
        if self.wantBackgroundFocus:
            self.chatInputNormal.chatEntry['backgroundFocus'] = 0

    def whisperTo(self, avatarName, avatarId):
        self.fsm.request('whisper', [avatarName, avatarId])

    def noWhisper(self):
        self.fsm.request('mainMenu')

    def handleWhiteListSelect(self):
        self.fsm.request('whiteListOpenChat')

    def enterWhiteListOpenChat(self):
        self.checkObscurred()
        if self.wantBackgroundFocus:
            self.chatInputNormal.chatEntry['backgroundFocus'] = 0
        base.localAvatar.chatMgr.chatInputWhiteList.activateByData()

    def exitWhiteListOpenChat(self):
        pass

    def enterWhiteListAvatarChat(self, receiverId):
        if self.wantBackgroundFocus:
            self.chatInputNormal.chatEntry['backgroundFocus'] = 0
        base.localAvatar.chatMgr.chatInputWhiteList.activateByData(receiverId)

    def exitWhiteListAvatarChat(self):
        pass

    def enterWhisper(self, avatarName, avatarId):
        self.whisperScButton['extraArgs'] = [avatarName, avatarId]
        self.whisperButton['extraArgs'] = [avatarName, avatarId]
        online = 0
        if avatarId in self.cr.doId2do:
            online = 1
        elif self.cr.isFriend(avatarId):
            online = self.cr.isFriendOnline(avatarId)
        avatarUnderstandable = 0
        av = None
        if avatarId:
            av = self.cr.identifyAvatar(avatarId)
        if av != None:
            avatarUnderstandable = av.isUnderstandable()
        chatName = avatarName
        normalButtonObscured, scButtonObscured = self.isObscured()
        if avatarUnderstandable and online and not normalButtonObscured:
            self.whisperButton['state'] = 'normal'
            self.enablewhisperButton()
        else:
            self.whisperButton['state'] = 'inactive'
            self.disablewhisperButton()
        if online:
            self.whisperScButton['state'] = 'normal'
            self.whisperButton['state'] = 'normal'
            self.changeFrameText(OTPLocalizer.ChatManagerWhisperToName % chatName)
        else:
            self.whisperScButton['state'] = 'inactive'
            self.whisperButton['state'] = 'inactive'
            self.changeFrameText(OTPLocalizer.ChatManagerWhisperOffline % chatName)
        self.whisperFrame.show()
        self.refreshWhisperFrame()
        if avatarUnderstandable and online:
            if self.wantBackgroundFocus:
                self.chatInputNormal.chatEntry['backgroundFocus'] = 1
            self.acceptOnce('enterNormalChat', self.fsm.request, ['whisperChat', [avatarName, avatarId]])

    def disablewhisperButton(self):
        pass

    def enablewhisperButton(self):
        pass

    def refreshWhisperFrame(self):
        pass

    def changeFrameText(self, newText):
        self.whisperFrame['text'] = newText

    def exitWhisper(self):
        self.whisperFrame.hide()
        self.ignore('enterNormalChat')
        self.chatInputNormal.chatEntry['backgroundFocus'] = 0

    def enterWhisperSpeedChat(self, avatarId):
        self.whisperFrame.show()
        if self.wantBackgroundFocus:
            self.chatInputNormal.chatEntry['backgroundFocus'] = 0
        self.chatInputSpeedChat.show(avatarId)

    def exitWhisperSpeedChat(self):
        self.whisperFrame.hide()
        self.chatInputSpeedChat.hide()

    def enterWhisperChat(self, avatarName, avatarId):
        result = self.chatInputNormal.activateByData(avatarId)
        return result

    def exitWhisperChat(self):
        self.chatInputNormal.deactivate()

    def enterSpeedChat(self):
        messenger.send('enterSpeedChat')
        if not self.__scObscured:
            self.scButton.show()
        if not self.__normalObscured:
            self.normalButton.show()
        if self.wantBackgroundFocus:
            self.chatInputNormal.chatEntry['backgroundFocus'] = 0
        self.chatInputSpeedChat.show()

    def exitSpeedChat(self):
        self.scButton.hide()
        self.normalButton.hide()
        self.chatInputSpeedChat.hide()

    def enterNormalChat(self):
        result = self.chatInputNormal.activateByData()
        return result

    def exitNormalChat(self):
        self.chatInputNormal.deactivate()

    def enterNoTrueFriendsAtAll(self):
        self.notify.error('called enterNoTrueFriendsAtAll() on parent class')

    def exitNoTrueFriendsAtAll(self):
        self.notify.error('called exitNoTrueFriendsAtAll() on parent class')

    def enterNoTrueFriendsAtAllAndNoWhitelist(self):
        self.notify.error('called enterNoTrueFriendsAtAllAndNoWhitelist() on parent class')

    def exitNoTrueFriendsAtAllAndNoWhitelist(self):
        self.notify.error('called exitNoTrueFriendsAtAllAndNoWhitelist() on parent class')

    def enterOtherDialog(self):
        pass

    def exitOtherDialog(self):
        pass