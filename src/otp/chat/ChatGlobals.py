import string
NORMAL_CHAT = 1
WHISPER_CHAT = 2
ERROR_NONE = None
ERROR_NO_OPEN_CHAT = 1
ERROR_NOT_FRIENDS = 2
ERROR_NO_RECEIVER = 3
TYPEDCHAT = 0
SPEEDCHAT_NORMAL = 1
SPEEDCHAT_EMOTE = 2
SPEEDCHAT_CUSTOM = 3
SYSTEMCHAT = 4
GAMECHAT = 5
PARTYCHAT = 6
SPEEDCHAT_QUEST = 7
FRIEND_UPDATE = 8
AVATAR_UNAVAILABLE = 9
ChatEvent = 'ChatEvent'
NormalChatEvent = 'NormalChatEvent'
SCChatEvent = 'SCChatEvent'
SCCustomChatEvent = 'SCCustomChatEvent'
SCEmoteChatEvent = 'SCEmoteChatEvent'
SCQuestEvent = 'SCQuestEvent'
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
