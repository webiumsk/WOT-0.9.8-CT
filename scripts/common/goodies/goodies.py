# Embedded file name: scripts/common/goodies/Goodies.py
from goodie_constants import GOODIE_STATE, MAX_ACTIVE_GOODIES
from debug_utils import LOG_AQ

class Goodies(object):

    def __init__(self, definedGoodies):
        self.definedGoodies = definedGoodies
        self.actualGoodies = {}
        self._updateCallback = None
        self._removeCallback = None
        return

    def setHandlers(self, u, r):
        self._updateCallback = u
        self._removeCallback = r

    def __updateCallback(self, goodie):
        if self._updateCallback is not None:
            return self._updateCallback(goodie)
        else:
            return

    def __removeCallback(self, goodieId):
        if self._removeCallback is not None:
            return self._removeCallback(goodieId)
        else:
            return

    def __append(self, goodieDefinition, state = None, expiration = None, counter = None):
        goodie = goodieDefinition.createGoodie(state, expiration, counter)
        if goodie is None:
            return
        else:
            self.actualGoodies[goodieDefinition.uid] = goodie
            self.__updateCallback(goodie)
            return

    def __remove(self, goodieId):
        del self.actualGoodies[goodieId]
        self.__removeCallback(goodieId)

    def __updateCounter(self, goodieDefinition, counter):
        goodie = goodieDefinition.createGoodie(counter=counter)
        if goodie is None:
            return
        else:
            self.actualGoodies[goodieDefinition.uid] = goodie
            self.__updateCallback(goodie)
            return

    def __update(self, goodieId):
        goodieDefinition = self.definedGoodies.get(goodieId, None)
        if goodieDefinition is None:
            return
        else:
            goodie = self.actualGoodies.get(goodieId, None)
            if goodie is None:
                return
            if goodieDefinition.isActivatable() and goodie.isActive() and not goodie.isExpired():
                return
            counter = self.actualGoodies[goodieId].counter - 1
            if counter <= 0:
                self.__remove(goodieId)
            else:
                self.__updateCounter(goodieDefinition, counter)
            return

    def __checkDuplicateResources(self, allResourcesByType, affectedResources):
        for r in affectedResources:
            if r.__class__ in allResourcesByType:
                return True
            allResourcesByType.add(r.__class__)

        return False

    def __show(self, target, resources):
        toUpdate = []
        result = set()
        allResourcesByType = set()
        for goodie in self.actualGoodies.itervalues():
            goodieDefinition = self.definedGoodies[goodie.uid]
            if goodieDefinition.isActivatable() and not goodie.isActive():
                continue
            if goodieDefinition.target == target:
                affectedResources = goodieDefinition.apply(resources)
                if not self.__checkDuplicateResources(allResourcesByType, affectedResources):
                    result.update(affectedResources)
                    toUpdate.append(goodie.uid)

        return (result, toUpdate)

    def actual(self):
        return self.actualGoodies.itervalues()

    def actualIds(self):
        return set(self.actualGoodies.iterkeys())

    def load(self, goodieId, state, expiration, counter):
        goodieDefinition = self.definedGoodies[goodieId]
        self.__append(goodieDefinition, state, expiration, counter)

    def extend(self, goodieId, state, expiration, counter):
        goodieDefinition = self.definedGoodies[goodieId]
        goodie = self.actualGoodies.get(goodieId, None)
        if goodie is not None:
            counter += goodie.counter
        self.__append(goodieDefinition, state, expiration, counter)
        return

    def test(self, target, resource):
        return self.__show(target, resource)[0]

    def apply(self, target, resources):
        affectedResources, toUpdate = self.__show(target, resources)
        for goodieId in toUpdate:
            self.__update(goodieId)

        return affectedResources

    def evaluate(self, condition):
        result = []
        for defined in self.definedGoodies.itervalues():
            if defined.uid in self.actualGoodies:
                continue
            if defined.condition is not None and defined.condition.check(condition):
                self.__append(defined)
                result.append(defined.uid)

        return result

    def expire(self):
        toUpdate = []
        toRemove = []
        for goodieId, goodie in self.actualGoodies.iteritems():
            defined = self.definedGoodies[goodieId]
            if defined.isTimeLimited():
                if defined.isExpired():
                    toRemove.append(goodieId)
                elif goodie.isExpired():
                    toUpdate.append(goodieId)

        for goodieId in toUpdate:
            self.__update(goodieId)

        for goodieId in toRemove:
            self.__remove(goodieId)

    def activeGoodiesCount(self):
        result = 0
        for goodie in self.actualGoodies.itervalues():
            if goodie.isActive():
                result += 1

        return result

    def activate(self, goodieId):
        if self.activeGoodiesCount() > MAX_ACTIVE_GOODIES:
            return
        else:
            goodie = self.actualGoodies.get(goodieId, None)
            if goodie is None:
                return
            if goodie.isActive():
                return
            defined = self.definedGoodies[goodieId]
            if not defined.isTimeLimited():
                return
            goodie = defined.createGoodie(state=GOODIE_STATE.ACTIVE, counter=goodie.counter)
            self.actualGoodies[goodieId] = goodie
            self.__updateCallback(goodie)
            return goodie

    def remove(self, goodieId):
        goodie = self.actualGoodies.get(goodieId, None)
        if goodie is None:
            return
        else:
            self.__remove(goodieId)
            return
