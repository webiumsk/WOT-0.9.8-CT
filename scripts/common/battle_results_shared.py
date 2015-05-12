# Embedded file name: scripts/common/battle_results_shared.py
import struct
from itertools import izip
VEH_INTERACTION_DETAILS = (('spotted', 'B', 1, 0),
 ('deathReason', 'b', 10, -1),
 ('directHits', 'H', 65535, 0),
 ('explosionHits', 'H', 65535, 0),
 ('piercings', 'H', 65535, 0),
 ('damageDealt', 'H', 65535, 0),
 ('damageAssistedTrack', 'H', 65535, 0),
 ('damageAssistedRadio', 'H', 65535, 0),
 ('crits', 'I', 4294967295L, 0),
 ('fire', 'H', 65535, 0),
 ('damageBlockedByArmor', 'I', 4294967295L, 0),
 ('damageTaken', 'H', 65535, 0),
 ('rickochetsReceived', 'H', 65535, 0),
 ('noDamageDirectHitsReceived', 'H', 65535, 0),
 ('targetKills', 'B', 255, 0))
VEH_INTERACTION_DETAILS_NAMES = [ x[0] for x in VEH_INTERACTION_DETAILS ]
VEH_INTERACTION_DETAILS_MAX_VALUES = dict(((x[0], x[2]) for x in VEH_INTERACTION_DETAILS))
VEH_INTERACTION_DETAILS_INIT_VALUES = [ x[3] for x in VEH_INTERACTION_DETAILS ]
VEH_INTERACTION_DETAILS_LAYOUT = ''.join([ x[1] for x in VEH_INTERACTION_DETAILS ])
VEH_INTERACTION_DETAILS_INDICES = dict(((x[1][0], x[0]) for x in enumerate(VEH_INTERACTION_DETAILS)))
_VEH_CELL_RESULTS_PUBLIC = ('health', 'credits', 'xp', 'achievementCredits', 'achievementXP', 'achievementFreeXP', 'shots', 'directHits', 'directTeamHits', 'explosionHits', 'piercings', 'damageDealt', 'sniperDamageDealt', 'damageAssistedRadio', 'damageAssistedTrack', 'damageReceived', 'damageBlockedByArmor', 'directHitsReceived', 'noDamageDirectHitsReceived', 'explosionHitsReceived', 'piercingsReceived', 'spotted', 'damaged', 'kills', 'tdamageDealt', 'tdestroyedModules', 'tkills', 'isTeamKiller', 'capturePoints', 'droppedCapturePoints', 'mileage', 'lifeTime', 'killerID', 'achievements', 'potentialDamageReceived', 'isPrematureLeave', 'fortResource', 'influencePoints', 'rolloutsCount', 'deathCount', 'flagActions', 'winPoints')
_VEH_CELL_RESULTS_PRIVATE = ('repair', 'freeXP', 'details')
_VEH_CELL_RESULTS_SERVER = ('protoAchievements', 'potentialDamageDealt', 'soloHitsAssisted', 'isEnemyBaseCaptured', 'stucks', 'autoAimedShots', 'presenceTime', 'spot_list', 'damage_list', 'kill_list', 'ammo', 'crewActivityFlags', 'series', 'tkillRating', 'tkillLog', 'destroyedObjects', 'committedSuicide', 'discloseShots', 'guerrillaShots', 'critsCount', 'aimerSeries', 'critsByType', 'innerModuleCritCount', 'innerModuleDestrCount', 'isAnyOurCrittedInnerModules', 'killsAssistedTrack', 'killsAssistedRadio', 'killedAndDamagedByAllSquadmates', 'damagedWhileMoving', 'damagedWhileEnemyMoving', 'damagedVehicleCntAssistedTrack', 'damagedVehicleCntAssistedRadio', 'isNotSpotted', 'spottedBeforeWeBecameSpotted', 'isAnyHitReceivedWhileCapturing', 'spottedAndDamagedSPG', 'damageAssistedRadioWhileInvisible', 'damageAssistedTrackWhileInvisible', 'damage_event_list', 'multi_damage_events', 'inBattleMaxSniperSeries', 'inBattleMaxKillingSeries', 'inBattleMaxPiercingSeries', 'damageBeforeTeamWasDamaged', 'killsBeforeTeamWasDamaged', 'percentFromTotalTeamDamage', 'percentFromSecondBestDamage', 'firstDamageTime', 'consumedAmmo')
VEH_CELL_RESULTS = _VEH_CELL_RESULTS_PUBLIC + _VEH_CELL_RESULTS_PRIVATE + _VEH_CELL_RESULTS_SERVER
VEH_CELL_RESULTS_INDICES = dict(((x[1], x[0]) for x in enumerate(VEH_CELL_RESULTS)))
_VEH_BASE_RESULTS_PUBLIC = ('accountDBID', 'team', 'typeCompDescr', 'gold', 'deathReason', 'fortBuilding')
_VEH_BASE_RESULTS_PRIVATE = ('xpPenalty', 'creditsPenalty', 'creditsContributionIn', 'creditsContributionOut', 'creditsToDraw', 'club', 'enemy_club', 'xpByTmen')
_VEH_BASE_RESULTS_SERVER = ('eventIndices', 'vehLockTimeFactor', 'misc', 'cybersportRatingDeltas', 'clanDBID', 'vehsByClass')
VEH_BASE_RESULTS = _VEH_CELL_RESULTS_PUBLIC + _VEH_BASE_RESULTS_PUBLIC + _VEH_CELL_RESULTS_PRIVATE + _VEH_BASE_RESULTS_PRIVATE + _VEH_CELL_RESULTS_SERVER + _VEH_BASE_RESULTS_SERVER
VEH_BASE_RESULTS_INDICES = dict(((x[1], x[0]) for x in enumerate(VEH_BASE_RESULTS)))
VEH_PUBLIC_RESULTS = _VEH_CELL_RESULTS_PUBLIC + _VEH_BASE_RESULTS_PUBLIC
VEH_PUBLIC_RESULTS_INDICES = dict(((x[1], x[0]) for x in enumerate(VEH_PUBLIC_RESULTS)))
VEH_FULL_RESULTS_UPDATE = ('tmenXP', 'isPremium', 'eventCredits', 'eventGold', 'eventXP', 'eventFreeXP', 'eventTMenXP', 'autoRepairCost', 'autoLoadCost', 'autoEquipCost', 'histAmmoCost', 'premiumVehicleXP', 'premiumXPFactor10', 'premiumCreditsFactor10', 'dailyXPFactor10', 'igrXPFactor10', 'aogasFactor10', 'prevMarkOfMastery', 'markOfMastery', 'dossierPopUps', 'vehTypeLockTime', 'serviceProviderID', 'marksOnGun', 'movingAvgDamage', 'damageRating', 'orderCredits', 'orderXP', 'orderTMenXP', 'orderFreeXP', 'orderFortResource', 'boosterCredits', 'boosterXP', 'boosterTMenXP', 'boosterFreeXP', 'fairplayViolations', 'refSystemXPFactor10', 'battleNum', 'originalXP', 'originalFreeXP', 'originalCredits')
VEH_FULL_RESULTS_UPDATE_INDICES = dict(((x[1], x[0]) for x in enumerate(VEH_FULL_RESULTS_UPDATE)))
_VEH_FULL_RESULTS_PRIVATE = ('questsProgress',)
VEH_FULL_RESULTS_SERVER = ('eventGoldByEventID',)
VEH_FULL_RESULTS = _VEH_CELL_RESULTS_PUBLIC + _VEH_BASE_RESULTS_PUBLIC + _VEH_CELL_RESULTS_PRIVATE + _VEH_BASE_RESULTS_PRIVATE + VEH_FULL_RESULTS_UPDATE + _VEH_FULL_RESULTS_PRIVATE
VEH_FULL_RESULTS_INDICES = dict(((x[1], x[0]) for x in enumerate(VEH_FULL_RESULTS)))
PLAYER_INFO = ('name', 'clanDBID', 'clanAbbrev', 'prebattleID', 'team', 'igrType')
PLAYER_INFO_INDICES = dict(((x[1], x[0]) for x in enumerate(PLAYER_INFO)))
COMMON_RESULTS = ('arenaTypeID', 'arenaCreateTime', 'winnerTeam', 'finishReason', 'duration', 'bonusType', 'guiType', 'vehLockMode', 'sortieDivision')
COMMON_RESULTS_INDICES = dict(((x[1], x[0]) for x in enumerate(COMMON_RESULTS)))
raise not set(VEH_FULL_RESULTS) & set(COMMON_RESULTS) or AssertionError
INTERACTIVE_STATS = ('xp', 'damageDealt', 'capturePts', 'flagActions', 'winPoints', 'deathCount')
INTERACTIVE_STATS_INDICES = dict(((x[1], x[0]) for x in enumerate(INTERACTIVE_STATS)))

class UNIT_CLAN_MEMBERSHIP:
    NONE = 0
    ANY = 1
    SAME = 2


def dictToList(indices, d):
    l = [None] * len(indices)
    for name, index in indices.iteritems():
        l[index] = d[name]

    return l


def listToDict(names, l):
    d = {}
    for x in enumerate(names):
        d[x[1]] = l[x[0]]

    return d


class _VehicleInteractionDetailsItem(object):

    def __init__(self, values, offset):
        self.__values = values
        self.__offset = offset

    def __getitem__(self, key):
        return self.__values[self.__offset + VEH_INTERACTION_DETAILS_INDICES[key]]

    def __setitem__(self, key, value):
        self.__values[self.__offset + VEH_INTERACTION_DETAILS_INDICES[key]] = min(int(value), VEH_INTERACTION_DETAILS_MAX_VALUES[key])

    def __str__(self):
        return str(dict(self))

    def __iter__(self):
        return izip(VEH_INTERACTION_DETAILS_NAMES, self.__values[self.__offset:])


class VehicleInteractionDetails(object):

    def __init__(self, uniqueVehIDs, values):
        self.__uniqueVehIDs = uniqueVehIDs
        self.__values = values
        size = len(VEH_INTERACTION_DETAILS)
        self.__offsets = dict(((x[1], x[0] * size) for x in enumerate(uniqueVehIDs)))

    @staticmethod
    def fromPacked(packed):
        count = len(packed) / struct.calcsize(''.join(['<2I', VEH_INTERACTION_DETAILS_LAYOUT]))
        packedVehIDsLayout = '<%dI' % (2 * count,)
        packedVehIDsLen = struct.calcsize(packedVehIDsLayout)
        flatIDs = struct.unpack(packedVehIDsLayout, packed[:packedVehIDsLen])
        uniqueVehIDs = []
        for i in xrange(0, len(flatIDs), 2):
            uniqueVehIDs.append((flatIDs[i], flatIDs[i + 1]))

        values = struct.unpack('<' + VEH_INTERACTION_DETAILS_LAYOUT * count, packed[packedVehIDsLen:])
        return VehicleInteractionDetails(uniqueVehIDs, values)

    def __getitem__(self, uniqueVehID):
        if not type(uniqueVehID) == tuple:
            raise AssertionError
            offset = self.__offsets.get(uniqueVehID, None)
            offset is None and self.__uniqueVehIDs.append(uniqueVehID)
            offset = len(self.__values)
            self.__values += VEH_INTERACTION_DETAILS_INIT_VALUES
            self.__offsets[uniqueVehID] = offset
        return _VehicleInteractionDetailsItem(self.__values, offset)

    def __contains__(self, uniqueVehID):
        raise type(uniqueVehID) == tuple or AssertionError
        return uniqueVehID in self.__offsets

    def __str__(self):
        return str(self.toDict())

    def pack(self):
        count = len(self.__uniqueVehIDs)
        flatIDs = []
        for uniqueID in self.__uniqueVehIDs:
            flatIDs.append(uniqueID[0])
            flatIDs.append(uniqueID[1])

        packed = struct.pack(('<%dI' % (2 * count)), *flatIDs) + struct.pack(('<' + VEH_INTERACTION_DETAILS_LAYOUT * count), *self.__values)
        return packed

    def toDict(self):
        return dict([ ((vehID, vehTypeCompDescr), dict(_VehicleInteractionDetailsItem(self.__values, offset))) for (vehID, vehTypeCompDescr), offset in self.__offsets.iteritems() ])
