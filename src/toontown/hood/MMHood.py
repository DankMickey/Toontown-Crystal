from src.toontown.safezone.MMSafeZoneLoader import MMSafeZoneLoader
from src.toontown.town.MMTownLoader import MMTownLoader
from src.toontown.toonbase import ToontownGlobals
from src.toontown.hood.ToonHood import ToonHood


class MMHood(ToonHood):
    notify = directNotify.newCategory('MMHood')

    ID = ToontownGlobals.MinniesMelodyland
    TOWNLOADER_CLASS = MMTownLoader
    SAFEZONELOADER_CLASS = MMSafeZoneLoader
    STORAGE_DNA = 'phase_6/dna/storage_MM.pdna'
    SKY_FILE = 'phase_6/models/props/MM_sky'
    SPOOKY_SKY_FILE = 'phase_6/models/props/MM_sky'
    TITLE_COLOR = (1.0, 0.4117647058823529, 0.7058823529411765, 1.0)

    HOLIDAY_DNA = {
      ToontownGlobals.CHRISTMAS: ['phase_6/dna/winter_storage_MM.pdna'],
      ToontownGlobals.HALLOWEEN: ['phase_6/dna/halloween_props_storage_MM.pdna']}

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
