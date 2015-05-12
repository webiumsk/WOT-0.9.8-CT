# Embedded file name: scripts/client/gui/arena_info/__init__.py
import BigWorld
import constants

def getClientArena():
    return getattr(BigWorld.player(), 'arena', None)


def getArenaTypeID():
    return getattr(BigWorld.player(), 'arenaTypeID', 0)


def getPlayerName():
    return getattr(BigWorld.player(), 'name', '')


def getPlayerTeam():
    return getattr(BigWorld.player(), 'team', 0)


def getPlayerVehicleID():
    return getattr(BigWorld.player(), 'playerVehicleID', 0)


def isPlayerTeamKillSuspected():
    return bool(getattr(BigWorld.player(), 'tkillIsSuspected', 0))


def isEventBattle():
    arena = getClientArena()
    return arena is not None and arena.guiType == constants.ARENA_GUI_TYPE.EVENT_BATTLES


class IArenaController(object):

    def destroy(self):
        pass

    def invalidateArenaInfo(self):
        pass

    def invalidateVehiclesInfo(self, arenaDP):
        pass

    def invalidateStats(self, arenaDP):
        pass

    def addVehicleInfo(self, vo, arenaDP):
        pass

    def invalidateVehicleInfo(self, flags, vo, arenaDP):
        pass

    def invalidateVehicleStatus(self, flags, vo, arenaDP):
        pass

    def invalidateVehicleStats(self, flags, vo, arenaDP):
        pass

    def invalidatePlayerStatus(self, flags, vo, arenaDP):
        pass

    def invalidateChatRosters(self):
        pass

    def invalidateChatRoster(self, user):
        pass

    def spaceLoadStarted(self):
        pass

    def spaceLoadCompleted(self):
        pass

    def updateSpaceLoadProgress(self, progress):
        pass

    def arenaLoadCompleted(self):
        pass
