# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/CyberSportUnitsListMeta.py
from gui.Scaleform.daapi.view.lobby.rally.BaseRallyListView import BaseRallyListView

class CyberSportUnitsListMeta(BaseRallyListView):

    def getTeamData(self, index):
        self._printOverrideError('getTeamData')

    def refreshTeams(self):
        self._printOverrideError('refreshTeams')

    def filterVehicles(self):
        self._printOverrideError('filterVehicles')

    def setTeamFilters(self, showOnlyStatic):
        self._printOverrideError('setTeamFilters')

    def loadPrevious(self):
        self._printOverrideError('loadPrevious')

    def loadNext(self):
        self._printOverrideError('loadNext')

    def showRallyProfile(self, id):
        self._printOverrideError('showRallyProfile')

    def as_setSearchResultTextS(self, text, descrText, filterData):
        if self._isDAAPIInited():
            return self.flashObject.as_setSearchResultText(text, descrText, filterData)

    def as_setHeaderS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setHeader(data)

    def as_setSelectedVehiclesInfoS(self, infoText, selectedVehiclesCount):
        if self._isDAAPIInited():
            return self.flashObject.as_setSelectedVehiclesInfo(infoText, selectedVehiclesCount)

    def as_updateNavigationBlockS(self, value):
        if self._isDAAPIInited():
            return self.flashObject.as_updateNavigationBlock(value)

    def as_updateRallyIconS(self, iconPath):
        if self._isDAAPIInited():
            return self.flashObject.as_updateRallyIcon(iconPath)
