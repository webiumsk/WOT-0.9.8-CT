# Embedded file name: scripts/client/gui/battle_control/dyn_squad_arena_controllers.py
from debug_utils import LOG_DEBUG
from gui.Scaleform.locale.MESSENGER import MESSENGER
from gui.battle_control import arena_info, avatar_getter
from gui.battle_control.arena_info.settings import INVALIDATE_OP
from gui.prb_control.prb_helpers import prbInvitesProperty
from gui.prb_control.settings import PRB_INVITE_STATE
from gui.shared.SoundEffectsId import SoundEffectsId
from helpers.i18n import makeString

class DynSquadArenaController(arena_info.IArenaController):

    def __init__(self):
        super(DynSquadArenaController, self).__init__()
        invitesManager = self.prbInvites
        invitesManager.onReceivedInviteListModified += self.__onReceivedInviteModified
        invitesManager.onSentInviteListModified += self.__onSentInviteListModified

    def setBattleCtx(self, battleCtx):
        pass

    @prbInvitesProperty
    def prbInvites(self):
        return None

    def invalidateVehicleInfo(self, flags, playerVehVO, arenaDP):
        voSquadIndex = playerVehVO.squadIndex
        if flags & INVALIDATE_OP.PREBATTLE_CHANGED and voSquadIndex > 0:
            squadMembersCount = arenaDP.getPrbVehCount(playerVehVO.team, playerVehVO.prebattleID)
            if squadMembersCount == 2:
                myAvatarVehicle = arenaDP.getVehicleInfo(avatar_getter.getPlayerVehicleID())
                if playerVehVO.prebattleID == myAvatarVehicle.prebattleID:
                    if myAvatarVehicle.player.isPrebattleCreator:
                        self._squadCreatedImOwner(squadNum=voSquadIndex)
                    else:
                        self._squadCreatedImRecruit(squadNum=voSquadIndex)
                elif myAvatarVehicle.team == playerVehVO.team:
                    self._squadCreatedByAllies(squadNum=voSquadIndex)
                else:
                    self._squadCreatedByEnemies(squadNum=voSquadIndex)
            elif squadMembersCount == 3:
                myAvatarVehicle = arenaDP.getVehicleInfo(avatar_getter.getPlayerVehicleID())
                playerVO = playerVehVO.player
                if playerVO.accountDBID == myAvatarVehicle.player.accountDBID:
                    self._iAmJoinedSquad(squadNum=voSquadIndex)
                elif myAvatarVehicle.team == playerVehVO.team:
                    if myAvatarVehicle.squadIndex == voSquadIndex:
                        self._someoneJoinedMySquad(squadNum=voSquadIndex, receiver=playerVO.name)
                    else:
                        self._someoneJoinedAlliedSquad(squadNum=voSquadIndex, receiver=playerVO.name)
                else:
                    self._someoneJoinedEnemySquad(squadNum=voSquadIndex, receiver=playerVO.name)

    def _inviteReceived(self, invite):
        LOG_DEBUG('Handler: Invite received', invite)

    def _inviteSent(self, invite):
        LOG_DEBUG('Handler: Invite sent', invite)

    def _squadCreatedImOwner(self, **kwargs):
        LOG_DEBUG('Handler: Squad created by myself', kwargs)

    def _squadCreatedImRecruit(self, **kwargs):
        LOG_DEBUG("Handler: Squad created and I'm not commander", kwargs)

    def _squadCreatedByAllies(self, **kwargs):
        LOG_DEBUG('Handler: Allies created new squad', kwargs)

    def _squadCreatedByEnemies(self, **kwargs):
        LOG_DEBUG('Handler: Enemies created new squad', kwargs)

    def _iAmJoinedSquad(self, **kwargs):
        LOG_DEBUG("Handler: I'm just have joined the squad", kwargs)

    def _someoneJoinedAlliedSquad(self, **kwargs):
        LOG_DEBUG('Handler: Someone just have joined a squad', kwargs)

    def _someoneJoinedAlliedSquad(self, **kwargs):
        LOG_DEBUG('Handler: Someone just have joined Allied squad', kwargs)

    def _someoneJoinedEnemySquad(self, **kwargs):
        LOG_DEBUG('Handler: Someone just have joined Enemy squad', kwargs)

    def _someoneJoinedMySquad(self, **kwargs):
        LOG_DEBUG('Handler: Someone just have joined MY squad', kwargs)

    def destroy(self):
        super(DynSquadArenaController, self).destroy()
        invitesManager = self.prbInvites
        invitesManager.onReceivedInviteListModified -= self.__onReceivedInviteModified
        invitesManager.onSentInviteListModified -= self.__onSentInviteListModified

    def __onReceivedInviteModified(self, added, changed, deleted):
        self.__handleModifiedInvitesList(added, changed, deleted, self.prbInvites.getReceivedInvites, self._inviteReceived)

    def __onSentInviteListModified(self, added, changed, deleted):
        self.__handleModifiedInvitesList(added, changed, deleted, self.prbInvites.getSentInvites, self._inviteSent)

    def __handleModifiedInvitesList(self, added, changed, deleted, inviteDataReceiver, callback):
        allChangedInvites = set(added) | set(changed) | set(deleted)
        if len(allChangedInvites) > 0:
            for invite in inviteDataReceiver(allChangedInvites):
                if invite.getState() == PRB_INVITE_STATE.PENDING:
                    callback(invite)


class DynSquadMessagesController(DynSquadArenaController):

    def __init__(self, callback):
        super(DynSquadMessagesController, self).__init__()
        self.__updateCallback = callback

    def _inviteReceived(self, invite):
        self.__invokeUpdate(makeString(MESSENGER.CLIENT_DYNSQUAD_INVITERECEIVED, creator=invite.creator))

    def _inviteSent(self, invite):
        self.__invokeUpdate(makeString(MESSENGER.CLIENT_DYNSQUAD_INVITESENT, receiver=invite.receiver))

    def _squadCreatedImOwner(self, **kwargs):
        self.__invokeUpdate(MESSENGER.CLIENT_DYNSQUAD_CREATED_OWNER, **kwargs)

    def _squadCreatedImRecruit(self, **kwargs):
        self.__invokeUpdate(MESSENGER.CLIENT_DYNSQUAD_CREATED_RECRUIT, **kwargs)

    def _squadCreatedByAllies(self, **kwargs):
        self.__invokeUpdate(MESSENGER.CLIENT_DYNSQUAD_CREATED_ALLIES, **kwargs)

    def _squadCreatedByEnemies(self, **kwargs):
        self.__invokeUpdate(MESSENGER.CLIENT_DYNSQUAD_CREATED_ENEMIES, **kwargs)

    def _iAmJoinedSquad(self, **kwargs):
        self.__invokeUpdate(MESSENGER.CLIENT_DYNSQUAD_INVITEACCEPTED_MYSELF, **kwargs)

    def _someoneJoinedAlliedSquad(self, **kwargs):
        self.__invokeUpdate(MESSENGER.CLIENT_DYNSQUAD_INVITEACCEPTED_USER, **kwargs)

    def _someoneJoinedMySquad(self, **kwargs):
        self.__invokeUpdate(MESSENGER.CLIENT_DYNSQUAD_INVITEACCEPTED_USER, **kwargs)

    def destroy(self):
        super(DynSquadMessagesController, self).destroy()
        self.__updateCallback = None
        return

    def __invokeUpdate(self, key, **kwargs):
        self.__updateCallback(makeString(key, **kwargs))


class DynSquadSoundsController(DynSquadArenaController):

    def __init__(self, soundMgr):
        super(DynSquadSoundsController, self).__init__()
        self.__soundManager = soundMgr

    def _squadCreatedImOwner(self, **kwargs):
        self.__playSound()

    def _squadCreatedImRecruit(self, **kwargs):
        self.__playSound()

    def _inviteReceived(self, invite):
        self.__playSound()

    def _iAmJoinedSquad(self, **kwargs):
        self.__playSound()

    def _someoneJoinedMySquad(self, **kwargs):
        self.__playSound()

    def __playSound(self):
        self.__soundManager.playSound('effects.%s' % SoundEffectsId.DYN_SQUAD_STARTING_DYNAMIC_PLATOON)
