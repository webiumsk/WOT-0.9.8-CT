# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/LobbyHeaderMeta.py
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class LobbyHeaderMeta(DAAPIModule):

    def menuItemClick(self, alias):
        self._printOverrideError('menuItemClick')

    def showLobbyMenu(self):
        self._printOverrideError('showLobbyMenu')

    def showExchangeWindow(self):
        self._printOverrideError('showExchangeWindow')

    def showExchangeXPWindow(self):
        self._printOverrideError('showExchangeXPWindow')

    def showPremiumDialog(self):
        self._printOverrideError('showPremiumDialog')

    def onPayment(self):
        self._printOverrideError('onPayment')

    def showSquad(self):
        self._printOverrideError('showSquad')

    def fightClick(self, mapID, actionName):
        self._printOverrideError('fightClick')

    def as_setScreenS(self, alias):
        if self._isDAAPIInited():
            return self.flashObject.as_setScreen(alias)

    def as_creditsResponseS(self, credits):
        if self._isDAAPIInited():
            return self.flashObject.as_creditsResponse(credits)

    def as_goldResponseS(self, gold):
        if self._isDAAPIInited():
            return self.flashObject.as_goldResponse(gold)

    def as_doDisableNavigationS(self):
        if self._isDAAPIInited():
            return self.flashObject.as_doDisableNavigation()

    def as_doDisableHeaderButtonS(self, btnId, isEnabled):
        if self._isDAAPIInited():
            return self.flashObject.as_doDisableHeaderButton(btnId, isEnabled)

    def as_updateSquadS(self, isInSquad):
        if self._isDAAPIInited():
            return self.flashObject.as_updateSquad(isInSquad)

    def as_nameResponseS(self, fullName, name, clan, isTeamKiller, isClan, hasNew, hasActiveBooster):
        if self._isDAAPIInited():
            return self.flashObject.as_nameResponse(fullName, name, clan, isTeamKiller, isClan, hasNew, hasActiveBooster)

    def as_setClanEmblemS(self, tID):
        if self._isDAAPIInited():
            return self.flashObject.as_setClanEmblem(tID)

    def as_setPremiumParamsS(self, isPremiumAccount, btnLabel, doLabel, isYear, disableTTHeader, disableTTBody, isHasAction):
        if self._isDAAPIInited():
            return self.flashObject.as_setPremiumParams(isPremiumAccount, btnLabel, doLabel, isYear, disableTTHeader, disableTTBody, isHasAction)

    def as_updateBattleTypeS(self, battleTypeName, battleTypeIcon, isEnabled):
        if self._isDAAPIInited():
            return self.flashObject.as_updateBattleType(battleTypeName, battleTypeIcon, isEnabled)

    def as_setServerS(self, name):
        if self._isDAAPIInited():
            return self.flashObject.as_setServer(name)

    def as_setWalletStatusS(self, walletStatus):
        if self._isDAAPIInited():
            return self.flashObject.as_setWalletStatus(walletStatus)

    def as_setFreeXPS(self, freeXP):
        if self._isDAAPIInited():
            return self.flashObject.as_setFreeXP(freeXP)

    def as_disableFightButtonS(self, isDisabled):
        if self._isDAAPIInited():
            return self.flashObject.as_disableFightButton(isDisabled)

    def as_setFightButtonS(self, label):
        if self._isDAAPIInited():
            return self.flashObject.as_setFightButton(label)

    def as_setCoolDownForReadyS(self, value):
        if self._isDAAPIInited():
            return self.flashObject.as_setCoolDownForReady(value)

    def as_showBubbleTooltipS(self, message, duration):
        if self._isDAAPIInited():
            return self.flashObject.as_showBubbleTooltip(message, duration)

    def as_setFightBtnTooltipDataS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setFightBtnTooltipData(data)
