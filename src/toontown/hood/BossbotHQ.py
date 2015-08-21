from src.toontown.coghq.BossbotCogHQLoader import BossbotCogHQLoader
from src.toontown.toonbase import ToontownGlobals
from src.toontown.hood.CogHood import CogHood


class BossbotHQ(CogHood):
    notify = directNotify.newCategory('BossbotHQ')

    ID = ToontownGlobals.BossbotHQ
    LOADER_CLASS = BossbotCogHQLoader
    
    def enter(self, requestStatus):
        CogHood.enter(self, requestStatus)

        base.localAvatar.setCameraFov(ToontownGlobals.CogHQCameraFov)
        base.camLens.setNearFar(ToontownGlobals.BossbotHQCameraNear, ToontownGlobals.BossbotHQCameraFar)
        
	
    def load(self):
        CogHood.load(self)

        self.fog = Fog('BBHQFog')

    def setFog(self):
        if base.wantFog:
            self.fog.setColor(0.640625, 0.355469, 0.269531, 1.0)
            self.fog.setExpDensity(0.012)
            render.clearFog()
            render.setFog(self.fog)
            self.sky.clearFog()
            self.sky.setFog(self.fog)
            
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
