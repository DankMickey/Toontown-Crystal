from src.toontown.coghq.CashbotCogHQLoader import CashbotCogHQLoader
from src.toontown.toonbase import ToontownGlobals, TTLocalizer
from src.toontown.hood.CogHood import CogHood
from src.toontown.hood import ZoneUtil


class CashbotHQ(CogHood):
    notify = directNotify.newCategory('CashbotHQ')

    ID = ToontownGlobals.CashbotHQ
    LOADER_CLASS = CashbotCogHQLoader
    SKY_FILE = 'phase_3.5/models/props/TT_sky'

    def enter(self, requestStatus):
        CogHood.enter(self, requestStatus)

        base.localAvatar.setCameraFov(ToontownGlobals.CogHQCameraFov)
        base.camLens.setNearFar(ToontownGlobals.CashbotHQCameraNear, ToontownGlobals.CashbotHQCameraFar)

    def spawnTitleText(self, zoneId, floorNum=None):
        if ZoneUtil.isMintInteriorZone(zoneId):
            text = '%s\n%s' % (ToontownGlobals.StreetNames[zoneId][-1], TTLocalizer.MintFloorTitle % (floorNum + 1))
            self.doSpawnTitleText(text)
            return

        CogHood.spawnTitleText(self, zoneId)
        
@magicWord(category=CATEGORY_CREATIVE)
def spooky():
    """
    Activates the 'spooky' effect on the current area.
    """
    hood = base.cr.playGame.hood
    if not hasattr(hood, 'startSpookySky'):
        return "Couldn't find spooky sky."
    if hasattr(hood, 'magicWordSpookyEffect'):
        return 'The spooky effect is already active!'
    hood.magicWordSpookyEffect = True
    hood.startSpookySky()
    fadeOut = base.cr.playGame.getPlace().loader.geom.colorScaleInterval(
        1.5, Vec4(0.55, 0.55, 0.65, 1), startColorScale=Vec4(1, 1, 1, 1),
        blendType='easeInOut')
    fadeOut.start()
    spookySfx = base.loadSfx('phase_4/audio/sfx/spooky.ogg')
    spookySfx.play()
    return 'Activating the spooky effect...'
