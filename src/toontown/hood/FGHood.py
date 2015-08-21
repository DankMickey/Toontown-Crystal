from src.toontown.safezone.FGSafeZoneLoader import FGSafeZoneLoader
from src.toontown.town.FGTownLoader import FGTownLoader
from src.toontown.toonbase import ToontownGlobals
from src.toontown.hood.ToonHood import ToonHood

class DLHood(ToonHood):
    notify = directNotify.newCategory('FGHood')

    ID = ToontownGlobals.F
    TOWNLOADER_CLASS = DLTownLoader
    SAFEZONELOADER_CLASS = DLSafeZoneLoader
    STORAGE_DNA = 'phase_2/dna/storage_FG.pdna'
    SKY_FILE = 'phase_8/models/props/DL_sky'
    TITLE_COLOR = (0.2627, 0.8039, 0.5019, 1.0)

    HOLIDAY_DNA = {
      ToontownGlobals.CHRISTMAS: ['phase_8/dna/winter_storage_DL.pdna'],
      ToontownGlobals.HALLOWEEN: ['phase_8/dna/halloween_props_storage_DL.pdna']}

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
