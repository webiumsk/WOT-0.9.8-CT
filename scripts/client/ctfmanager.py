# Embedded file name: scripts/client/CTFManager.py
import BigWorld
import Event
from functools import partial
from debug_utils import *
from constants import FLAG_STATE
from Math import Vector3

class _CTFManager:

    def __init__(self):
        self.__flagModelName = 'content/Environment/env_111_02_FalloutFlag/normal/lod0/env_111_02_FalloutFlag.model'
        self.__flags = {}
        self.__vehicles = None
        self.__evtManager = Event.EventManager()
        self.onFlagSpawnedAtBase = Event.Event(self.__evtManager)
        self.onFlagCapturedByVehicle = Event.Event(self.__evtManager)
        self.onFlagDroppedToGround = Event.Event(self.__evtManager)
        self.onFlagAbsorbed = Event.Event(self.__evtManager)
        self.onCarriedFlagsPositionUpdated = Event.Event(self.__evtManager)
        return

    def onEnterArena(self):
        self.__vehicles = BigWorld.player().arena.vehicles

    def onLeaveArena(self):
        self.__clear()

    def onFlagStateChanged(self, data):
        flagID = data[0]
        prevState = data[1]
        newState = data[2]
        stateParams = data[3:]
        self.__switchFlagToState(flagID, prevState, newState, stateParams)

    def updateCarriedFlagPositions(self, flagIDs, positions):
        for i, flagID in enumerate(flagIDs):
            if flagID in self.__flags:
                self.__flags[flagID]['minimapPos'] = Vector3(float(positions[i * 2]), 0.0, float(positions[i * 2 + 1]))

        self.onCarriedFlagsPositionUpdated(flagIDs)

    def getFlags(self):
        return self.__flags.keys()

    def getFlagInfo(self, flagID):
        return self.__flags.get(flagID, None)

    def isFlagBearer(self, vehicleID):
        for flag in self.__flags.itervalues():
            if flag['vehicle'] == vehicleID:
                return True

        return False

    def getFlagMinimapPos(self, flagID):
        if flagID not in self.__flags:
            return
        else:
            flag = self.__flags[flagID]
            vehicleID = flag['vehicle']
            if vehicleID is not None:
                vehicle = self.__getVehicle(vehicleID)
                if vehicle is not None:
                    return vehicle.position
            return flag['minimapPos']

    def __switchFlagToState(self, flagID, prevState, newState, stateParams):
        if flagID not in self.__flags:
            self.__flags[flagID] = {'state': None,
             'prevState': None,
             'minimapPos': None,
             'vehicle': None,
             'respawnTime': 0.0,
             'model': None}
        flag = self.__flags[flagID]
        flag['state'] = newState
        flag['prevState'] = prevState
        if newState == FLAG_STATE.ON_SPAWN:
            flagPos = Vector3(*stateParams[0])
            flag['vehicle'] = None
            flag['minimapPos'] = flagPos
            flag['respawnTime'] = 0.0
            self.__flagModelSet(flagID, flagPos, True)
            self.onFlagSpawnedAtBase(flagID, flagPos)
        elif newState == FLAG_STATE.ON_VEHICLE:
            vehicleID = stateParams[0]
            flag['vehicle'] = vehicleID
            flag['respawnTime'] = 0.0
            self.__flagModelSet(flagID, None, False)
            vehicle = self.__getVehicle(vehicleID)
            if vehicle is not None:
                flag['minimapPos'] = vehicle.position
            self.onFlagCapturedByVehicle(flagID, vehicleID)
        elif newState == FLAG_STATE.ON_GROUND:
            loserVehicleID = stateParams[0]
            flagPos = Vector3(*stateParams[1])
            respawnTime = stateParams[2]
            flag['vehicle'] = None
            flag['respawnTime'] = respawnTime
            flag['minimapPos'] = flagPos
            self.__flagModelSet(flagID, flagPos, True)
            self.onFlagDroppedToGround(flagID, loserVehicleID, flagPos, respawnTime)
        elif newState == FLAG_STATE.ABSORBED:
            vehicleID = stateParams[0]
            respawnTime = stateParams[1]
            flag['vehicle'] = None
            flag['respawnTime'] = respawnTime
            self.__flagModelSet(flagID, None, False)
            self.onFlagAbsorbed(flagID, vehicleID, respawnTime)
        return

    def __createFlagAt(self, flagID, position, isVisible):
        BigWorld.loadResourceListBG((self.__flagModelName,), partial(self.__onFlagModelLoaded, flagID, position, isVisible))

    def __onFlagModelLoaded(self, flagID, position, isVisible, resourceRefs):
        if resourceRefs.failedIDs:
            LOG_ERROR('Failed to load flag model %s' % (resourceRefs.failedIDs,))
        else:
            model = resourceRefs[self.__flagModelName]
            model.visible = isVisible
            if position is not None:
                model.position = position
            BigWorld.addModel(model, BigWorld.player().spaceID)
            try:
                animAction = model.action('FalloutFlagAnimAction')
                animAction()
            except:
                pass

            self.__flags[flagID]['model'] = model
        return

    def __removeFlag(self, flagID):
        if flagID not in self.__flags:
            return
        else:
            flagModel = self.__flags[flagID]['model']
            if flagModel is not None:
                BigWorld.delModel(self.__flags[flagID]['model'])
            del self.__flags[flagID]
            return

    def __clear(self):
        for flag in self.__flags.itervalues():
            flagModel = flag['model']
            if flagModel is not None:
                BigWorld.delModel(flagModel)
                flag['model'] = None

        self.__flags.clear()
        self.__vehicles = None
        self.__evtManager.clear()
        return

    def __getVehicle(self, vehicleID):
        if self.__vehicles is None:
            return
        elif vehicleID not in self.__vehicles:
            return
        else:
            return BigWorld.entities.get(vehicleID)

    def __flagModelSet(self, flagID, flagPos, isVisible):
        if flagID not in self.__flags:
            return
        else:
            flagModel = self.__flags[flagID]['model']
            if flagModel is None:
                self.__createFlagAt(flagID, flagPos, isVisible)
            else:
                flagModel.visible = isVisible
                if flagPos is not None:
                    flagModel.position = flagPos
            return


g_ctfManager = _CTFManager()
