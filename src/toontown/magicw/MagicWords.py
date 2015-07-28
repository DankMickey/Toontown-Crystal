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
    invoker = spellbook.getTarget()
    invoker.hideNametag2d()
    invoker.hideNametag3d()