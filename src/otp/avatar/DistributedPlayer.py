from direct.showbase import PythonUtil
from direct.task import Task
from pandac.PandaModules import *
import string
import time

from otp.ai.MagicWordGlobal import *
from otp.avatar import Avatar, PlayerBase
from otp.avatar import DistributedAvatar
from otp.avatar.Avatar import teleportNotify
from otp.chat import ChatGarbler
from otp.chat import TalkAssistant
from otp.distributed.TelemetryLimited import TelemetryLimited
from otp.otpbase import OTPGlobals
from otp.otpbase import OTPLocalizer
from otp.speedchat import SCDecoders
from toontown.chat.ChatGlobals import *
from toontown.chat.WhisperPopup import WhisperPopup

class DistributedPlayer(DistributedAvatar.DistributedAvatar, PlayerBase.PlayerBase, TelemetryLimited):
    TeleportFailureTimeout = 60.0
    chatGarbler = ChatGarbler.ChatGarbler()

    def __init__(self, cr):
        try:
            self.DistributedPlayer_initialized
        except:
            self.DistributedPlayer_initialized = 1
            DistributedAvatar.DistributedAvatar.__init__(self, cr)
            PlayerBase.PlayerBase.__init__(self)
            TelemetryLimited.__init__(self)
            self.__teleportAvailable = 0
            self.inventory = None
            self.experience = None
            self.friendsList = []
            self.oldFriendsList = None
            self.timeFriendsListChanged = None
            self.lastFailedTeleportMessage = {}
            self._districtWeAreGeneratedOn = None
            self.DISLname = ''
            self.DISLid = 0
            self.adminAccess = 0
            self.autoRun = 0
            self.whiteListEnabled = base.config.GetBool('whitelist-chat-enabled', 1)
            self.lastTeleportQuery = time.time()

    @staticmethod
    def GetPlayerGenerateEvent():
        return 'DistributedPlayerGenerateEvent'

    @staticmethod
    def GetPlayerNetworkDeleteEvent():
        return 'DistributedPlayerNetworkDeleteEvent'

    @staticmethod
    def GetPlayerDeleteEvent():
        return 'DistributedPlayerDeleteEvent'

    def networkDelete(self):
        DistributedAvatar.DistributedAvatar.networkDelete(self)
        messenger.send(self.GetPlayerNetworkDeleteEvent(), [self])

    def disable(self):
        DistributedAvatar.DistributedAvatar.disable(self)
        messenger.send(self.GetPlayerDeleteEvent(), [self])

    def delete(self):
        try:
            self.DistributedPlayer_deleted
        except:
            self.DistributedPlayer_deleted = 1
            del self.experience
            if self.inventory:
                self.inventory.unload()
            del self.inventory
            DistributedAvatar.DistributedAvatar.delete(self)

    def generate(self):
        DistributedAvatar.DistributedAvatar.generate(self)

    def announceGenerate(self):
        DistributedAvatar.DistributedAvatar.announceGenerate(self)
        messenger.send(self.GetPlayerGenerateEvent(), [self])

    def setLocation(self, parentId, zoneId):
        DistributedAvatar.DistributedAvatar.setLocation(self, parentId, zoneId)
        if not (parentId in (0, None) and zoneId in (0, None)):
            if not self.cr._isValidPlayerLocation(parentId, zoneId):
                self.cr.disableDoId(self.doId)
                self.cr.deleteObject(self.doId)
        return None

    def isGeneratedOnDistrict(self, districtId = None):
        return True # fix for the task button
        if districtId is None:
            return self._districtWeAreGeneratedOn is not None
        else:
            return self._districtWeAreGeneratedOn == districtId
        return

    def getArrivedOnDistrictEvent(self, districtId = None):
        if districtId is None:
            return 'arrivedOnDistrict'
        else:
            return 'arrivedOnDistrict-%s' % districtId
        return

    def arrivedOnDistrict(self, districtId):
        curFrameTime = globalClock.getFrameTime()
        if hasattr(self, 'frameTimeWeArrivedOnDistrict') and curFrameTime == self.frameTimeWeArrivedOnDistrict:
            if districtId == 0 and self._districtWeAreGeneratedOn:
                self.notify.warning('ignoring arrivedOnDistrict 0, since arrivedOnDistrict %d occured on the same frame' % self._districtWeAreGeneratedOn)
                return
        self._districtWeAreGeneratedOn = districtId
        self.frameTimeWeArrivedOnDistrict = globalClock.getFrameTime()
        messenger.send(self.getArrivedOnDistrictEvent(districtId))
        messenger.send(self.getArrivedOnDistrictEvent())

    def setLeftDistrict(self):
        self._districtWeAreGeneratedOn = None
        return

    def hasParentingRules(self):
        if self is localAvatar:
            return True

    def setAccountName(self, accountName):
        self.accountName = accountName

    def setSystemMessage(self, aboutId, chatString, whisperType = WTSystem):
        self.displayWhisper(aboutId, chatString, whisperType)

    def displayWhisper(self, fromId, chatString, whisperType):
        print 'Whisper type %s from %s: %s' % (whisperType, fromId, chatString)

    def whisperSCTo(self, msgIndex, sendToId):
        messenger.send('wakeup')
        base.cr.ttsFriendsManager.d_whisperSCTo(sendToId, msgIndex)

    def setWhisperSCFrom(self, fromId, msgIndex):
        handle = base.cr.identifyAvatar(fromId)
        if handle == None or base.localAvatar.isIgnored(fromId):
            return
        chatString = SCDecoders.decodeSCStaticTextMsg(msgIndex)
        if chatString:
            self.displayWhisper(fromId, chatString, WTQuickTalker)
            base.talkAssistant.receiveAvatarWhisperSpeedChat(TalkAssistant.SPEEDCHAT_NORMAL, msgIndex, fromId)
        return

    def whisperSCCustomTo(self, msgIndex, sendToId):
        messenger.send('wakeup')
        base.cr.ttsFriendsManager.d_whisperSCCustomTo(sendToId, msgIndex)

    def _isValidWhisperSource(self, source):
        return True

    def setWhisperSCCustomFrom(self, fromId, msgIndex):
        handle = base.cr.identifyAvatar(fromId)
        if handle == None:
            return
        if not self._isValidWhisperSource(handle):
            self.notify.warning('displayWhisper from non-toon %s' % fromId)
            return
        if base.localAvatar.isIgnored(fromId):
            return
        chatString = SCDecoders.decodeSCCustomMsg(msgIndex)
        if chatString:
            self.displayWhisper(fromId, chatString, WTQuickTalker)
            base.talkAssistant.receiveAvatarWhisperSpeedChat(TalkAssistant.SPEEDCHAT_CUSTOM, msgIndex, fromId)
        return

    def whisperSCEmoteTo(self, emoteId, sendToId):
        messenger.send('wakeup')
        base.cr.ttsFriendsManager.d_whisperSCEmoteTo(sendToId, emoteId)

    def setWhisperSCEmoteFrom(self, fromId, emoteId):
        handle = base.cr.identifyAvatar(fromId)
        if handle == None or base.localAvatar.isIgnored(fromId):
            return
        chatString = SCDecoders.decodeSCEmoteWhisperMsg(emoteId, handle.getName())
        if chatString:
            self.displayWhisper(fromId, chatString, WTEmote)
            base.talkAssistant.receiveAvatarWhisperSpeedChat(TalkAssistant.SPEEDCHAT_EMOTE, emoteId, fromId)
        return

    def setChatAbsolute(self, chatString, chatFlags, dialogue = None, interrupt = 1, quiet = 0):
        DistributedAvatar.DistributedAvatar.setChatAbsolute(self, chatString, chatFlags, dialogue, interrupt)
        if not quiet:
            pass

    def b_setChat(self, chatString, chatFlags):
        if self.cr.wantMagicWords and len(chatString) > 0 and chatString[0] == '~':
            messenger.send('magicWord', [chatString])
        else:
            if base.config.GetBool('want-chatfilter-hacks', 0):
                if base.config.GetBool('want-chatfilter-drop-offending', 0):
                    if badwordpy.test(chatString):
                        return
                else:
                    chatString = badwordpy.scrub(chatString)
            messenger.send('wakeup')
            self.setChatAbsolute(chatString, chatFlags)
            self.d_setChat(chatString, chatFlags)

    def d_setChat(self, chatString, chatFlags):
        self.sendUpdate('setChat', [chatString, chatFlags, 0])

    def setTalk(self, fromAV, fromAC, avatarName, chat, mods, flags):
        if base.localAvatar.isIgnored(fromAV):
            return
        newText, scrubbed = self.scrubTalk(chat, mods)
        self.displayTalk(newText)
        if base.talkAssistant.isThought(newText):
            newText = base.talkAssistant.removeThoughtPrefix(newText)
            base.talkAssistant.receiveThought(fromAV, avatarName, fromAC, None, newText, scrubbed)
        else:
            base.talkAssistant.receiveOpenTalk(fromAV, avatarName, fromAC, None, newText, scrubbed)
        return

    def setTalkWhisper(self, fromAV, fromAC, avatarName, chat, mods, flags):
        if base.localAvatar.isIgnored(fromAV):
            return
        newText, scrubbed = self.scrubTalk(chat, mods)
        self.displayTalkWhisper(fromAV, avatarName, chat, mods)
        base.talkAssistant.receiveWhisperTalk(fromAV, avatarName, fromAC, None, self.doId, self.getName(), newText, scrubbed)
        return

    def displayTalkWhisper(self, fromId, avatarName, chatString, mods):
        print 'TalkWhisper from %s: %s' % (fromId, chatString)

    def scrubTalk(self, chat, mods):
        return chat

    def setChat(self, chatString, chatFlags, DISLid):
        self.notify.error('Should call setTalk')
        chatString = base.talkAssistant.whiteListFilterMessage(chatString)
        if base.localAvatar.isIgnored(self.doId):
            return
        if base.localAvatar.garbleChat and not self.isUnderstandable():
            chatString = self.chatGarbler.garble(self, chatString)
        chatFlags &= ~(CFQuicktalker | CFPageButton | CFQuitButton)
        if chatFlags & CFThought:
            chatFlags &= ~(CFSpeech | CFTimeout)
        else:
            chatFlags |= CFSpeech | CFTimeout
        self.setChatAbsolute(chatString, chatFlags)

    def b_setSC(self, msgIndex):
        self.setSC(msgIndex)
        self.d_setSC(msgIndex)

    def d_setSC(self, msgIndex):
        messenger.send('wakeup')
        self.sendUpdate('setSC', [msgIndex])

    def setSC(self, msgIndex):
        if base.localAvatar.isIgnored(self.doId):
            return
        chatString = SCDecoders.decodeSCStaticTextMsg(msgIndex)
        if chatString:
            self.setChatAbsolute(chatString, CFSpeech | CFQuicktalker | CFTimeout, quiet=1)
        base.talkAssistant.receiveOpenSpeedChat(TalkAssistant.SPEEDCHAT_NORMAL, msgIndex, self.doId)

    def b_setSCCustom(self, msgIndex):
        self.setSCCustom(msgIndex)
        self.d_setSCCustom(msgIndex)

    def d_setSCCustom(self, msgIndex):
        messenger.send('wakeup')
        self.sendUpdate('setSCCustom', [msgIndex])

    def setSCCustom(self, msgIndex):
        if base.localAvatar.isIgnored(self.doId):
            return
        chatString = SCDecoders.decodeSCCustomMsg(msgIndex)
        if chatString:
            self.setChatAbsolute(chatString, CFSpeech | CFQuicktalker | CFTimeout)
        base.talkAssistant.receiveOpenSpeedChat(TalkAssistant.SPEEDCHAT_CUSTOM, msgIndex, self.doId)

    def b_setSCEmote(self, emoteId):
        self.b_setEmoteState(emoteId, animMultiplier=self.animMultiplier)

    def d_friendsNotify(self, avId, status):
        self.sendUpdate('friendsNotify', [avId, status])

    def friendsNotify(self, avId, status):
        avatar = base.cr.identifyFriend(avId)
        if avatar != None:
            if status == 1:
                self.setSystemMessage(avId, OTPLocalizer.WhisperNoLongerFriend % avatar.getName())
            elif status == 2:
                self.setSystemMessage(avId, OTPLocalizer.WhisperNowSpecialFriend % avatar.getName())
        return

    def d_teleportQuery(self, requesterId, sendToId = None):
        lastQuery = self.lastTeleportQuery
        currentQuery = time.time()

        if currentQuery - lastQuery < 0.1: # Oh boy! We found a skid!
            self.cr.stopReaderPollTask()
            self.cr.lostConnection()

        self.lastTeleportQuery = time.time()

        base.cr.ttsFriendsManager.d_teleportQuery(sendToId)

    def teleportQuery(self, requesterId):
        avatar = base.cr.identifyFriend(requesterId)
        
        if avatar is None:
            self.d_teleportResponse(self.doId, 0, 0, 0, 0, sendToId=requesterId)
        elif base.localAvatar.isIgnored(requesterId):
            self.d_teleportResponse(self.doId, 2, 0, 0, 0, sendToId=requesterId)
        elif hasattr(base, 'distributedParty') and ((base.distributedParty.partyInfo.isPrivate and requesterId not in base.distributedParty.inviteeIds) or base.distributedParty.isPartyEnding):
            self.d_teleportResponse(self.doId, 0, 0, 0, 0, sendToId=requesterId)
        elif self.__teleportAvailable and not self.ghostMode:
            self.setSystemMessage(requesterId, OTPLocalizer.WhisperComingToVisit % avatar.getName())
            messenger.send('teleportQuery', [avatar, self])
        else:
            if self.failedTeleportMessageOk(requesterId):
                self.setSystemMessage(requesterId, OTPLocalizer.WhisperFailedVisit % avatar.getName())
            
            self.d_teleportResponse(self.doId, 0, 0, 0, 0, sendToId=requesterId)

    def failedTeleportMessageOk(self, fromId):
        now = globalClock.getFrameTime()
        lastTime = self.lastFailedTeleportMessage.get(fromId, None)
        if lastTime != None:
            elapsed = now - lastTime
            if elapsed < self.TeleportFailureTimeout:
                return 0
        self.lastFailedTeleportMessage[fromId] = now
        return 1

    def d_teleportResponse(self, avId, available, shardId, hoodId, zoneId, sendToId):
        teleportNotify.debug('sending teleportResponse%s' % ((avId, available,
            shardId, hoodId, zoneId, sendToId),)
        )

        base.cr.ttsFriendsManager.d_teleportResponse(sendToId, available,
            shardId, hoodId, zoneId
        )

    def teleportResponse(self, avId, available, shardId, hoodId, zoneId):
        teleportNotify.debug('received teleportResponse%s' % ((avId, available,
            shardId, hoodId, zoneId),)
        )

        messenger.send('teleportResponse', [avId, available, shardId, hoodId, zoneId])

    def d_teleportGiveup(self, requesterId, sendToId):
        teleportNotify.debug('sending teleportGiveup(%s) to %s' % (requesterId, sendToId))

        base.cr.ttsFriendsManager.d_teleportGiveup(sendToId)

    def teleportGiveup(self, requesterId):
        teleportNotify.debug('received teleportGiveup(%s)' % (requesterId,))
        avatar = base.cr.identifyAvatar(requesterId)

        if not self._isValidWhisperSource(avatar):
            self.notify.warning('teleportGiveup from non-toon %s' % requesterId)
            return

        if avatar is not None:
            self.setSystemMessage(requesterId,
                OTPLocalizer.WhisperGiveupVisit % avatar.getName()
            )

    def b_teleportGreeting(self, avId):
        if hasattr(self, 'ghostMode') and self.ghostMode:
            return
        self.d_teleportGreeting(avId)
        self.teleportGreeting(avId)

    def d_teleportGreeting(self, avId):
        self.sendUpdate('teleportGreeting', [avId])

    def teleportGreeting(self, avId):
        avatar = base.cr.getDo(avId)
        if isinstance(avatar, Avatar.Avatar):
            self.setChatAbsolute(OTPLocalizer.TeleportGreeting % avatar.getName(), CFSpeech | CFTimeout)
        elif avatar is not None:
            self.notify.warning('got teleportGreeting from %s referencing non-toon %s' % (self.doId, avId))
        return

    def setTeleportAvailable(self, available):
        self.__teleportAvailable = available

    def getTeleportAvailable(self):
        return self.__teleportAvailable

    def getFriendsList(self):
        return self.friendsList

    def setFriendsList(self, friendsList):
        self.oldFriendsList = self.friendsList
        self.friendsList = friendsList
        self.timeFriendsListChanged = globalClock.getFrameTime()
        messenger.send('friendsListChanged')
        Avatar.reconsiderAllUnderstandable()

    def setDISLname(self, name):
        self.DISLname = name

    def setDISLid(self, id):
        self.DISLid = id

    def setAdminAccess(self, access):
        self.adminAccess = access
        if self.isLocal():
            self.cr.wantMagicWords = self.adminAccess >= MINIMUM_MAGICWORD_ACCESS

    def getAdminAccess(self):
        return self.adminAccess

    def setAutoRun(self, value):
        self.autoRun = value

    def getAutoRun(self):
        return self.autoRun
