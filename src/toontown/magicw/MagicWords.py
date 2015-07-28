#This is for testing purposes. May not work or be present in final version.
from direct.distributed import ClockDelta
from toontown.toonbase import TTLocalizer, ToontownGlobals
from toontown.toontowngui import TTDialog
from otp.ai.MagicWordGlobal import *

#Codes Below is for Testing
@magicWord(category=CATEGORY_MODERATOR)
def magicHead():
 from toontown.toon import LaughingManGlobals
 invoker = spellbook.getTarget()
 LaughingManGlobals.addToonEffect(invoker)
 
@magicWord(category=CATEGORY_MODERATOR)
def noName():
    from otp.avatar import LocalAvatar
    invoker = spellbook.getTarget()
    invoker.setNameVisible(False)
	
@magicWord(category=CATEGORY_MODERATOR)
def clientRun():
  from otp.avatar import LocalAvatar
  base.localAvatar.enterRun()