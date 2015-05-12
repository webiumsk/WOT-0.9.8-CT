# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/InfoImageWindow.py
__author__ = 's_sagataev'
from gui.Scaleform.framework.entities.View import View
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView
from gui.Scaleform.daapi.view.meta.InfoImageWindowMeta import InfoImageWindowMeta
from gui.Scaleform.locale.RES_TUTORIAL import RES_TUTORIAL
from gui.Scaleform.locale.TUTORIAL import TUTORIAL
from helpers.i18n import makeString as _ms

class InfoImageWindow(View, AbstractWindowView, InfoImageWindowMeta):

    def __init__(self, ctx = None):
        super(InfoImageWindow, self).__init__()

    def _populate(self):
        super(InfoImageWindow, self)._populate()
        self.as_setDataS({'windowTitle': _ms(TUTORIAL.EMERGENCYBRAKEINFO_WINDOWTITLE),
         'image': RES_TUTORIAL.MAPS_TUTORIAL_POLICE_U_TURN_FIN,
         'btnTitle': _ms(TUTORIAL.EMERGENCYBRAKEINFO_BUTTON)})

    def _dispose(self):
        super(InfoImageWindow, self)._dispose()

    def onWindowClose(self):
        self.destroy()
