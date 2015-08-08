from panda3d.core import VBase4
from direct.gui.DirectGui import DirectButton, DirectFrame, DirectLabel, DirectSlider
from toontown.toonbase.TTLocalizer import SBshuffleBtn
from MakeAToonGlobals import *

preloaded = {}


def loadModels():
    global preloaded
    if not preloaded:
        gui = loader.loadModel('phase_3/models/gui/tt_m_gui_mat_mainGui')
        preloaded['guiRArrowUp'] = gui.find('**/tt_t_gui_mat_arrowUp')
        preloaded['guiRArrowRollover'] = gui.find('**/tt_t_gui_mat_arrowUp')
        preloaded['guiRArrowDown'] = gui.find('**/tt_t_gui_mat_arrowDown')
        preloaded['guiRArrowDisabled'] = gui.find('**/tt_t_gui_mat_arrowDisabled')
        preloaded['shuffleFrame'] = gui.find('**/tt_t_gui_mat_shuffleFrame')
        preloaded['shuffleUp'] = gui.find('**/tt_t_gui_mat_shuffleUp')
        preloaded['shuffleDown'] = gui.find('**/tt_t_gui_mat_shuffleDown')
        preloaded['shuffleArrowUp'] = gui.find('**/tt_t_gui_mat_shuffleArrowUp')
        preloaded['shuffleArrowDown'] = gui.find('**/tt_t_gui_mat_shuffleArrowDown')
        preloaded['shuffleArrowRollover'] = gui.find('**/tt_t_gui_mat_shuffleArrowUp')
        preloaded['shuffleArrowDisabled'] = gui.find('**/tt_t_gui_mat_shuffleArrowDisabled')
        gui.removeNode()
        del gui

class MATFrame(DirectFrame):
    def __init__(self, parent=None, arrowcommand=None, wantArrows=True, text_scale=(-0.001, -0.015), **kw):
        loadModels()

        if parent is None:
            parent = aspect2d

        optiondefs = (
            ('image', preloaded['shuffleFrame'], None),
            ('relief', None, None),
            ('frameColor', (1, 1, 1, 1), None),
            ('image_scale', halfButtonInvertScale, None),
            ('text_fg', (1, 1, 1, 1), None),
            ('text_scale', text_scale, None),
        )

        self.defineoptions(kw, optiondefs)
        DirectFrame.__init__(self, parent)
        self.initialiseoptions(MATFrame)

        if not wantArrows:
            self.leftArrow = None
            self.rightArrow = None
            return

        self.leftArrow = MATArrow(parent=self, command=arrowcommand)
        self.rightArrow = MATArrow(parent=self, inverted=True, command=arrowcommand)

    def destroy(self):
        if self.leftArrow:
            self.leftArrow.destroy()
        if self.rightArrow:
            self.rightArrow.destroy()

        DirectFrame.destroy(self)

class MATArrow(DirectButton):
    def __init__(self, parent=None, inverted=False, **kw):
        loadModels()
        if parent is None:
            parent = aspect2d

        if not inverted:
            scales = (halfButtonScale, halfButtonHoverScale)
            extraArgs = [-1]
            pos = (-0.2, 0, 0)
        else:
            scales = (halfButtonInvertScale, halfButtonInvertHoverScale)
            extraArgs = [1]
            pos = (0.2, 0, 0)

        optiondefs = (
            ('relief', None, None),
            ('image', (
                preloaded['shuffleArrowUp'],
                preloaded['shuffleArrowDown'],
                preloaded['shuffleArrowRollover'],
                preloaded['shuffleArrowDisabled']
            ), None),
            ('image_scale', scales[0], None),
            ('image1_scale', scales[1], None),
            ('image2_scale', scales[1], None),
            ('extraArgs', extraArgs, None),
            ('pos', pos, None),
        )

        self.defineoptions(kw, optiondefs)
        DirectButton.__init__(self, parent)
        self.initialiseoptions(MATArrow)
	
class MATSlider(DirectSlider):
    def __init__(self, parent=None, labelText='', **kw):
        loadModels()
        if parent is None:
            parent = aspect2d

        optiondefs = (
            ('thumb_image', (
                preloaded['shuffleUp'],
                preloaded['shuffleDown'],
                preloaded['shuffleUp']
            ), None),
            ('thumb_relief', None, None),
            ('pageSize', 0.5, None),
            ('scale', 0.32, None)
        )

        self.defineoptions(kw, optiondefs)
        DirectSlider.__init__(self, parent)
        self.initialiseoptions(MATSlider)

        self.label = None

        if labelText:
            self.label = DirectLabel(parent=self, pos=(0, 0, 0.1), text_bg=(0, 0, 0, 0), text_shadow=(0, 0, 0, 1),
                                     text_scale=0.3, text_fg=VBase4(1.0, 1.0, 1.0, 1.0), text=labelText, relief=None)

    def getColor(self):
        return self['value'] / 100.0

    def destroy(self):
        if self.label:
            self.label.destroy()

        DirectSlider.destroy(self)


class MATShuffleButton(DirectButton):
    def __init__(self, wantArrows=True, parent=None, arrowcommand=None, **kw):
        loadModels()
        if parent is None:
            parent = aspect2d

        optiondefs = (
            ('relief', None, None),
            ('image', (
                preloaded['shuffleUp'],
                preloaded['shuffleDown'],
                preloaded['shuffleUp']
            ), None),
            ('image_scale', halfButtonInvertScale, None),
            ('image1_scale', (-0.63, 0.6, 0.6), None),
            ('image2_scale', (-0.63, 0.6, 0.6), None),
            ('text_pos', (0, -0.02), None),
            ('text_fg', (1, 1, 1, 1), None),
            ('text_shadow', (0, 0, 0, 1), None),
            ('text_scale', SBshuffleBtn, None),
        )

        self.defineoptions(kw, optiondefs)
        DirectButton.__init__(self, parent)
        self.initialiseoptions(MATShuffleButton)

        if not wantArrows:
            self.leftArrow = None
            self.rightArrow = None
            self.frame = None
            return

        self.leftArrow = MATArrow(parent=self, command=arrowcommand)
        self.rightArrow = MATArrow(parent=self, command=arrowcommand, inverted=True)

        self.frame = MATFrame(parent=parent, wantArrows=False)

    def destroy(self):
        if self.leftArrow:
            self.leftArrow.destroy()
        if self.rightArrow:
            self.rightArrow.destroy()
        if self.frame:
            self.frame.destroy()
        DirectButton.destroy(self)

    def showArrows(self):
        self.leftArrow.show()
        self.rightArrow.show()

    def hideArrows(self):
        self.leftArrow.hide()
        self.rightArrow.hide()