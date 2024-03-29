# Embedded file name: scripts/common/unit_helpers/ExtrasHandler.py
import cPickle
from debug_utils import LOG_OGNICK_DEV

class EmptyExtrasHandler(object):

    def __init__(self, unit):
        pass

    def new(self):
        return {}

    def pack(self, extras):
        return ''

    def unpack(self, extrasStr):
        return None

    def reset(self, extras):
        return self.new()

    def updateUnitExtras(self, extras, updateStr):
        pass


class FortBattleExtrasHandler(EmptyExtrasHandler):

    def __init__(self, unit):
        self._unit = unit
        from unit_helpers.MsgProcessor import FortBattleMgrMsgProcessor
        self._processor = FortBattleMgrMsgProcessor(unit)

    def new(self):
        return {'isBattleRound': 0,
         'prevBuildNum': 0,
         'currentBuildNum': 0,
         'roundStart': 0,
         'battleResultList': [],
         'isEnemyReadyForBattle': 0,
         'clanEquipments': None,
         'lastEquipRev': 0}

    def pack(self, extras):
        return cPickle.dumps(extras, -1)

    def unpack(self, extrasStr):
        return cPickle.loads(extrasStr)

    def reset(self, extras):
        return extras

    def updateUnitExtras(self, extras, updateStr):
        self._processor.unpackOps(updateStr)


class ClubExtrasHandler(EmptyExtrasHandler):

    def __init__(self, unit = None):
        self._unit = unit

    def new(self):
        return {'clubDBID': None,
         'divisionID': None,
         'clubName': None,
         'accDBIDtoRole': None,
         'isRatedBattle': True,
         'accDBIDtoClubTimestamp': None,
         'clubEmblemIDs': None,
         'mapID': None,
         'isEnemyReady': False,
         'isBaseDefence': None,
         'startTime': None}

    def pack(self, extras):
        return cPickle.dumps(extras, -1)

    def unpack(self, extrasStr):
        return cPickle.loads(extrasStr)

    def reset(self, extras):
        return {'clubDBID': extras['clubDBID'],
         'divisionID': extras['divisionID'],
         'clubName': extras['clubName'],
         'accDBIDtoRole': extras['accDBIDtoRole'],
         'isRatedBattle': extras['isRatedBattle'],
         'accDBIDtoClubTimestamp': extras['accDBIDtoClubTimestamp'],
         'clubEmblemIDs': extras['clubEmblemIDs'],
         'mapID': None,
         'isEnemyReady': False,
         'isBaseDefence': None,
         'startTime': extras['startTime']}

    def updateUnitExtras(self, extras, updateStr):
        update = cPickle.loads(updateStr)
        if isinstance(update, tuple):
            extras[update[0]] = update[1]
        else:
            extras.update(update)


class SortieExtrasHandler(EmptyExtrasHandler):

    def __init__(self, unit = None):
        self._unit = unit

    def new(self):
        return {'clanEquipments': None,
         'lastEquipRev': 0}

    def pack(self, extras):
        return cPickle.dumps(extras, -1)

    def unpack(self, extrasStr):
        return cPickle.loads(extrasStr)

    def reset(self, extras):
        return extras

    def updateUnitExtras(self, extras, updateStr):
        update = cPickle.loads(updateStr)
        LOG_OGNICK_DEV('updateUnitExtras', update)
        extras.update(update)
