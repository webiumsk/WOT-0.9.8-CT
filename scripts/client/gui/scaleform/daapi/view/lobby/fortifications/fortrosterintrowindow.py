# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/FortRosterIntroWindow.py
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortViewHelper import FortViewHelper
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.fort_formatters import getDivisionIcon
from gui.Scaleform.daapi.view.meta.FortRosterIntroWindowMeta import FortRosterIntroWindowMeta
from gui.Scaleform.framework.entities.View import View
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.RES_FORT import RES_FORT
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.shared.fortifications.settings import FORT_BATTLE_DIVISIONS
from helpers.i18n import makeString as _ms
import BigWorld

class FortRosterIntroWindow(View, AbstractWindowView, FortViewHelper, FortRosterIntroWindowMeta):
    TYPE_FORT_UPGRADE = 'fort upgrade'
    TYPE_DEFENCE_START = 'defence start'

    def __init__(self, ctx = None):
        super(FortRosterIntroWindow, self).__init__()
        self._type = ctx.get('type', FortRosterIntroWindow.TYPE_DEFENCE_START)

    def _populate(self):
        super(FortRosterIntroWindow, self)._populate()
        self.startFortListening()
        self._updateData()

    def onWindowClose(self):
        self.destroy()

    def _dispose(self):
        self.stopFortListening()
        super(FortRosterIntroWindow, self)._dispose()

    def onDefenceHourChanged(self, hour):
        if not self.isDisposed():
            self._updateData()

    def onOffDayChanged(self, offDay):
        self._updateData()

    def _updateData(self):
        if not self.fortCtrl.getFort().isDefenceHourEnabled():
            self.destroy()
            raise self.fortCtrl.getFort().isDefenceHourEnabled() or AssertionError
            return
        else:
            if self.fortCtrl.getFort().level >= FORT_BATTLE_DIVISIONS.ABSOLUTE.minFortLevel:
                defenceDivisionName = _ms(FORTIFICATIONS.ROSTERINTROWINDOW_ABSOLUTEDIVISIONNAME)
            else:
                defenceDivisionName = _ms(FORTIFICATIONS.ROSTERINTROWINDOW_CHAMPIONDIVISIONNAME)
            defenceStart, defenceEnd = self.fortCtrl.getFort().getDefencePeriod()
            if self._type == FortRosterIntroWindow.TYPE_FORT_UPGRADE:
                bgIcon = RES_FORT.MAPS_FORT_ABSOLUTEROSTERINTRO
                header = _ms(FORTIFICATIONS.ROSTERINTROWINDOW_ABSOLUTE_HEADER)
            else:
                bgIcon = RES_FORT.MAPS_FORT_CHAMPIONROSTERINTRO
                header = _ms(FORTIFICATIONS.ROSTERINTROWINDOW_CHAMPION_HEADER)
            offDay = self.fortCtrl.getFort().getOffDayStr() if self.fortCtrl.getFort().isOffDayEnabled() else None
            if offDay is not None:
                defenceDescription = _ms(FORTIFICATIONS.ROSTERINTROWINDOW_DEFENCEDESCRIPTION_OFFDAY, start=BigWorld.wg_getShortTimeFormat(defenceStart), end=BigWorld.wg_getShortTimeFormat(defenceEnd), offDay=offDay)
            else:
                defenceDescription = _ms(FORTIFICATIONS.ROSTERINTROWINDOW_DEFENCEDESCRIPTION_NOOFFDAY, start=BigWorld.wg_getShortTimeFormat(defenceStart), end=BigWorld.wg_getShortTimeFormat(defenceEnd))
            fortLevel = self.fortCtrl.getFort().level
            self.as_setDataS({'windowTitle': _ms(FORTIFICATIONS.ROSTERINTROWINDOW_WINDOWTITLE),
             'bgIcon': bgIcon,
             'header': header,
             'defenceTitle': _ms(FORTIFICATIONS.ROSTERINTROWINDOW_DEFENCETITLE),
             'defenceIcon': RES_ICONS.MAPS_ICONS_LIBRARY_FORTIFICATION_DEFENCEFUTURE,
             'defenceDescription': defenceDescription,
             'defenceDivisionName': defenceDivisionName,
             'defenceDivisionIcon': getDivisionIcon(fortLevel, FORT_BATTLE_DIVISIONS.ABSOLUTE.minFortLevel, determineAlert=False),
             'attackTitle': _ms(FORTIFICATIONS.ROSTERINTROWINDOW_ATTACKTITLE),
             'attackIcon': _ms(RES_ICONS.MAPS_ICONS_LIBRARY_FORTIFICATION_OFFENCEFUTURE),
             'championDivisionDescription': _ms(FORTIFICATIONS.ROSTERINTROWINDOW_CHAMPIONDIVISIONDESCRIPTION),
             'championDivisionName': _ms(FORTIFICATIONS.ROSTERINTROWINDOW_CHAMPIONDIVISIONNAME),
             'championDivisionIcon': getDivisionIcon(FORT_BATTLE_DIVISIONS.CHAMPION.minFortLevel, fortLevel, determineAlert=True),
             'absoluteDivisionDescription': _ms(FORTIFICATIONS.ROSTERINTROWINDOW_ABSOLUTEDIVISIONDESCRIPTION),
             'absoluteDivisionName': _ms(FORTIFICATIONS.ROSTERINTROWINDOW_ABSOLUTEDIVISIONNAME),
             'absoluteDivisionIcon': getDivisionIcon(FORT_BATTLE_DIVISIONS.ABSOLUTE.minFortLevel, fortLevel, determineAlert=True),
             'acceptBtnLabel': _ms(MENU.AWARDWINDOW_OKBUTTON)})
            return
