from direct.gui.DirectGui import OnscreenImage, DirectLabel, DirectButton
from toontown.toonbase import ToontownGlobals, TTLocalizer
from toontown.toontowngui import TTDialog
import os

class PackSelector:

    def __init__(self, leaveFunction):
        self.title = None
        self.current = None
        self.available = None
        self.comingsoon = None
        self.backButton = None
        self.confirmDialog = None
        self.leaveFunction = leaveFunction

    def create(self):
        self.background = OnscreenImage(parent=render2d, image="phase_10/maps/GreenInk.jpg")
        self.gui = loader.loadModel('phase_3/models/gui/tt_m_gui_mat_mainGui')
        self.shuffleUp = self.gui.find('**/tt_t_gui_mat_shuffleUp')
        self.shuffleDown = self.gui.find('**/tt_t_gui_mat_shuffleDown')

        self.title = DirectLabel(aspect2d, relief=None, text=TTLocalizer.LanguageSelectorTitle,
                     text_fg=(0, 1, 0, 1), text_scale=0.15, text_font=ToontownGlobals.getSuitFont(),
                     pos=(0, 0, 0.70), text_shadow=(0, 0.392, 0, 1))

        self.current = DirectLabel(aspect2d, relief=None, text=TTLocalizer.LanguageSelectorCurrent % settings['pack'],
                       text_fg=(0, 1, 0, 1), text_scale=0.09, text_font=ToontownGlobals.getSuitFont(),
                       pos=(0, 0, 0.55), text_shadow=(0, 0.392, 0, 1))

        self.available = DirectLabel(aspect2d, relief=None, text=TTLocalizer.LanguageSelectorAvailable,
                         text_fg=(1, 0, 0, 1), text_scale=0.09, text_font=ToontownGlobals.getSuitFont(),
                         pos=(0, 0, 0), text_shadow=(0.545, 0, 0, 1))

        self.comingsoon = DirectButton(aspect2d, relief=None, text='Coming Soon... (Click will crash)',
                       text_fg=(1, 0.549, 0, 1), text_scale=0.09, text_font=ToontownGlobals.getSuitFont(),
                       pos=(0, 0, -0.15), text_shadow=(1, 0.27, 0, 1), command=self.switchLanguage, extraArgs=['NothingHere'])

    def destroy(self):
        for element in [self.background, self.title, self.current, self.available, self.english, self.french, self.portuguese, self.german, self.backButton, self.confirmDialog]:
            if element:
                element.destroy()
                element = None

        self.leaveFunction()

    def switchPack(self, pack):
        if pack == settings['pack']:
            self.confirmDialog = TTDialog.TTDialog(style=TTDialog.Acknowledge, text=TTLocalizer.LanguageSelectorSameLanguage, command=self.cleanupDialog)
        else:
            self.confirmDialog = TTDialog.TTDialog(style=TTDialog.YesNo, text=TTLocalizer.LanguageSelectorConfirm % pack, command=self.confirmSwitchLanguage, extraArgs=[pack])
        self.confirmDialog.show()

    def confirmSwitchLanguage(self, value, pack):
        if value > 0:
            settings['pack'] = pack
            os._exit(1)
        else:
            self.cleanupDialog()

    def cleanupDialog(self, value=0):
        self.confirmDialog.cleanup()
