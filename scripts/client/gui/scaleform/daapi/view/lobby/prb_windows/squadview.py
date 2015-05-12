# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/prb_windows/SquadView.py
from CurrentVehicle import g_currentVehicle
from gui.Scaleform.daapi.view.lobby.rally.vo_converters import makeVehicleVO
from gui.Scaleform.framework.managers.TextManager import TextManager, TextType
from gui.Scaleform.genConsts.PREBATTLE_ALIASES import PREBATTLE_ALIASES
from gui.Scaleform.locale.CYBERSPORT import CYBERSPORT
from gui.Scaleform.locale.MESSENGER import MESSENGER
from gui.prb_control.context import unit_ctx
from gui.Scaleform.daapi.view.meta.SquadViewMeta import SquadViewMeta
from gui.Scaleform.daapi.view.lobby.rally import vo_converters
from gui.Scaleform.locale.MENU import MENU
from gui.prb_control.settings import CTRL_ENTITY_TYPE, REQUEST_TYPE, FUNCTIONAL_EXIT
from gui.shared import events, EVENT_BUS_SCOPE
from gui.shared.ItemsCache import g_itemsCache
from helpers import i18n
from gui.prb_control import settings

class SquadView(SquadViewMeta):

    def inviteFriendRequest(self):
        if self.__canSendInvite():
            self.fireEvent(events.LoadViewEvent(PREBATTLE_ALIASES.SEND_INVITES_WINDOW_PY, ctx={'prbName': 'squad',
             'ctrlType': CTRL_ENTITY_TYPE.UNIT}), scope=EVENT_BUS_SCOPE.LOBBY)

    def toggleReadyStateRequest(self):
        self.unitFunctional.togglePlayerReadyAction(True)

    def onUnitVehicleChanged(self, dbID, vInfo):
        functional = self.unitFunctional
        pInfo = functional.getPlayerInfo(dbID=dbID)
        if pInfo.isInSlot:
            slotIdx = pInfo.slotIdx
            if not vInfo.isEmpty():
                vehicleVO = makeVehicleVO(g_itemsCache.items.getItemByCD(vInfo.vehTypeCD), functional.getRosterSettings().getLevelsRange())
                slotCost = vInfo.vehLevel
            else:
                slotState = functional.getSlotState(slotIdx)
                vehicleVO = None
                if slotState.isClosed:
                    slotCost = settings.UNIT_CLOSED_SLOT_COST
                else:
                    slotCost = 0
            self.as_setMemberVehicleS(slotIdx, slotCost, vehicleVO)
        return

    def chooseVehicleRequest(self):
        pass

    def leaveSquad(self):
        self.prbDispatcher.doLeaveAction(unit_ctx.LeaveUnitCtx(waitingID='prebattle/leave', funcExit=FUNCTIONAL_EXIT.NO_FUNC))

    def onUnitPlayerAdded(self, pInfo):
        super(SquadView, self).onUnitPlayerAdded(pInfo)
        self._setActionButtonState()

    def onUnitPlayerRemoved(self, pInfo):
        super(SquadView, self).onUnitPlayerRemoved(pInfo)
        self._setActionButtonState()

    def onUnitPlayerStateChanged(self, pInfo):
        self._updateRallyData()
        self._setActionButtonState()

    def onUnitFlagsChanged(self, flags, timeLeft):
        super(SquadView, self).onUnitFlagsChanged(flags, timeLeft)
        self._setActionButtonState()
        if flags.isInQueue():
            self._closeSendInvitesWindow()

    def onUnitRosterChanged(self):
        super(SquadView, self).onUnitRosterChanged()
        self._setActionButtonState()
        if not self.__canSendInvite():
            self._closeSendInvitesWindow()

    def onUnitMembersListChanged(self):
        super(SquadView, self).onUnitMembersListChanged()
        self._updateRallyData()
        self._setActionButtonState()

    def _populate(self):
        super(SquadView, self)._populate()
        self.addListener(events.CoolDownEvent.PREBATTLE, self.__handleSetPrebattleCoolDown, scope=EVENT_BUS_SCOPE.LOBBY)
        self.as_updateBattleTypeS(MENU.HEADERBUTTONS_BATTLE_MENU_STANDART)

    def _dispose(self):
        self.removeListener(events.CoolDownEvent.PREBATTLE, self.__handleSetPrebattleCoolDown, scope=EVENT_BUS_SCOPE.LOBBY)
        super(SquadView, self)._dispose()

    def _setActionButtonState(self):
        self.as_updateInviteBtnStateS(self._isInviteBtnEnabled())
        self.as_setActionButtonStateS(self.__getActionButtonStateVO())

    def _updateRallyData(self):
        functional = self.unitFunctional
        data = vo_converters.makeUnitVO(functional, unitIdx=functional.getUnitIdx(), app=self.app)
        self.as_updateRallyS(data)

    def _isInviteBtnEnabled(self):
        functional = self.unitFunctional
        enabled = not (functional.getFlags().isInIdle() and functional.getPlayerInfo().isReady) and self.__canSendInvite()
        if enabled:
            enabled = False
            for slot in functional.getSlotsIterator(*functional.getUnit(unitIdx=functional.getUnitIdx())):
                if not slot.player:
                    enabled = True
                    break

        return enabled

    def __getActionButtonStateVO(self):
        stateString = ''
        unitFunctional = self.unitFunctional
        pInfo = unitFunctional.getPlayerInfo()
        isInQueue = unitFunctional.getFlags().isInIdle()
        isEnabled = g_currentVehicle.isReadyToPrebattle() and not isInQueue
        playerReady = pInfo.isReady
        if not g_currentVehicle.isPresent():
            stateString = i18n.makeString('#cybersport:window/unit/message/vehicleNotSelected')
        elif not g_currentVehicle.isReadyToPrebattle():
            stateString = i18n.makeString('#cybersport:window/unit/message/vehicleNotValid')
        elif not playerReady:
            stateString = i18n.makeString(MESSENGER.DIALOGS_SQUAD_MESSAGE_GETREADY)
        elif playerReady and not isInQueue:
            stateString = i18n.makeString(MESSENGER.DIALOGS_SQUAD_MESSAGE_GETNOTREADY)
        stateString = TextManager.getText(TextType.MAIN_TEXT if isEnabled else TextType.ERROR_TEXT, stateString)
        if playerReady:
            label = CYBERSPORT.WINDOW_UNIT_NOTREADY
        else:
            label = CYBERSPORT.WINDOW_UNIT_READY
        return {'stateString': stateString,
         'label': label,
         'isEnabled': isEnabled,
         'isReady': playerReady}

    def __canSendInvite(self):
        return self.unitFunctional.getPermissions().canSendInvite()

    def __handleSetPrebattleCoolDown(self, event):
        if event.requestID is REQUEST_TYPE.SET_PLAYER_STATE:
            self.as_setCoolDownForReadyButtonS(event.coolDown)
