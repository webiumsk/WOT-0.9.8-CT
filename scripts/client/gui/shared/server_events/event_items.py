# Embedded file name: scripts/client/gui/shared/server_events/event_items.py
import operator
import time
from abc import ABCMeta
from collections import namedtuple, OrderedDict
from gui.shared.utils import CONST_CONTAINER
import nations
import constants
import ResMgr
import BigWorld
import ArenaType
from account_shared import AmmoIterator, getHistoricalCustomization
from helpers import getLocalizedData, i18n, time_utils, getClientLanguage
from helpers.time_utils import getTimeDeltaFromNow
from gui import makeHtmlString
from gui.shared import g_itemsCache
from gui.shared.server_events.bonuses import getBonusObj
from gui.shared.server_events.modifiers import getModifierObj, compareModifiers
from gui.shared.server_events.parsers import AccountRequirements, VehicleRequirements, PreBattleConditions, PostBattleConditions, BonusConditions
from gui.shared.gui_items import GUI_ITEM_TYPE, GUI_ITEM_TYPE_NAMES
from gui.Scaleform.locale.QUESTS import QUESTS

class _ActivityIntervalsIterator(object):
    WEEK_START = 1
    WEEK_END = 7
    ONE_DAY = 86400
    WHOLE_DAY_INTERVAL = (1, ONE_DAY)

    def __init__(self, currentTime, currentDay, weekDays = None, timeIntervals = None):
        self._currentTime = currentTime
        self._currentDay = currentDay
        self._timeIntervals = timeIntervals or [self.WHOLE_DAY_INTERVAL]
        self._weekDays = weekDays or set(range(self.WEEK_START, self.WEEK_END + 1))
        self._timeLeft = 0

    def __iter__(self):
        return self

    def next(self):
        interval = None
        if self._currentDay in self._weekDays:
            interval = self.__trySearchValidTimeInterval(self._currentTime)
        if interval is not None:
            self._timeLeft += interval[0] - self._currentTime
            self._currentTime = interval[1]
        else:
            self._currentDay += 1
            self._timeLeft += self.ONE_DAY - self._currentTime
            while True:
                if self._currentDay > self.WEEK_END:
                    self._currentDay = self.WEEK_START
                if self._currentDay in self._weekDays:
                    break
                self._currentDay += 1
                self._timeLeft += self.ONE_DAY

            interval = self.__trySearchValidTimeInterval(0)
            if interval is not None:
                self._timeLeft += interval[0]
                self._currentTime = interval[1]
            else:
                self._currentTime = 0
                interval = self.WHOLE_DAY_INTERVAL
        timeLeft = self._timeLeft
        self._timeLeft += interval[1] - interval[0]
        return (timeLeft, interval)

    def __trySearchValidTimeInterval(self, curTime):
        for low, high in self._timeIntervals:
            if curTime < high:
                return (low, high)

        return None


EventBattles = namedtuple('EventBattles', ['vehicleTags',
 'vehicles',
 'enabled',
 'arenaTypeID'])

class ServerEventAbstract(object):
    __metaclass__ = ABCMeta

    def __init__(self, eID, data):
        self._id = eID
        self._data = dict(data)

    def isGuiDisabled(self):
        return self._data.get('disableGui', False)

    def getWeekDays(self):
        return self._data.get('weekDays', set())

    def getActiveTimeIntervals(self):
        if 'activeTimeIntervals' in self._data:
            return map(lambda (l, h): (l[0] * 3600 + l[1] * 60, h[0] * 3600 + h[1] * 60), self._data['activeTimeIntervals'])
        return []

    def getID(self):
        return self._id

    def getData(self):
        return self._data

    def getType(self):
        return self._data.get('type', 0)

    def getStartTime(self):
        if 'startTime' in self._data:
            return time_utils.makeLocalServerTime(self._data['startTime'])
        return time.time()

    def getFinishTime(self):
        if 'finishTime' in self._data:
            return time_utils.makeLocalServerTime(self._data['finishTime'])
        return time.time()

    def getCreationTime(self):
        if 'gStartTime' in self._data:
            return time_utils.makeLocalServerTime(self._data['gStartTime'])
        return time.time()

    def getDestroyingTime(self):
        if 'gFinishTime' in self._data:
            return time_utils.makeLocalServerTime(self._data['gFinishTime'])
        return time.time()

    def getCreationTimeLeft(self):
        return getTimeDeltaFromNow(self.getCreationTime())

    def getDestroyingTimeLeft(self):
        return getTimeDeltaFromNow(self.getDestroyingTime())

    def getUserName(self):
        return getLocalizedData(self._data, 'name')

    def getDescription(self):
        return getLocalizedData(self._data, 'description')

    def getStartTimeLeft(self):
        return getTimeDeltaFromNow(self.getStartTime())

    def getFinishTimeLeft(self):
        return getTimeDeltaFromNow(self.getFinishTime())

    def isOutOfDate(self):
        return self.getFinishTimeLeft() <= 0

    def getUserType(self):
        return ''

    def isIGR(self):
        return self._data.get('isIGR', False)

    def isCompleted(self, progress = None):
        return False

    def getNearestActivityTimeLeft(self):
        timeLeft = None
        if self.getStartTimeLeft() > 0:
            timeLeft = (self.getStartTimeLeft(), (0, _ActivityIntervalsIterator.ONE_DAY))
        else:
            weekDays, timeIntervals = self.getWeekDays(), self.getActiveTimeIntervals()
            if len(weekDays) or len(timeIntervals):
                timeLeft = next(_ActivityIntervalsIterator(time_utils.getServerRegionalTimeCurrentDay(), time_utils.getServerRegionalWeekDay(), weekDays, timeIntervals))
        return timeLeft

    def isAvailable(self):
        if self.getStartTimeLeft() > 0:
            return (False, 'in_future')
        if self.isOutOfDate():
            return (False, 'out_of_date')
        if len(self.getWeekDays()) and time_utils.getServerRegionalWeekDay() not in self.getWeekDays():
            return (False, 'invalid_weekday')
        intervals = self.getActiveTimeIntervals()
        serverTime = time_utils.getServerRegionalTimeCurrentDay()
        if len(intervals):
            for low, high in intervals:
                if low <= serverTime <= high:
                    break
            else:
                return (False, 'invalid_time_interval')

        if not self._checkConditions():
            return (False, 'requirements')
        return (True, '')

    def getBonuses(self, bonusName = None):
        return []

    def _checkConditions(self):
        return True


class Quest(ServerEventAbstract):

    def __init__(self, qID, data, progress = None):
        import copy
        tmpData = copy.deepcopy(data)
        super(Quest, self).__init__(qID, data)
        self._progress = progress
        self._children, self._parents = {}, {}
        conds = dict(tmpData['conditions'])
        preBattle = dict(conds['preBattle'])
        self.accountReqs = AccountRequirements(preBattle['account'])
        self.vehicleReqs = VehicleRequirements(preBattle['vehicle'])
        self.preBattleCond = PreBattleConditions(preBattle['battle'])
        self.bonusCond = BonusConditions(conds['bonus'], self.getProgressData(), self.preBattleCond)
        self.postBattleCond = PostBattleConditions(conds['postBattle'], self.preBattleCond)

    def getUserType(self):
        return i18n.makeString(QUESTS.ITEM_TYPE_QUEST)

    def getProgressExpiryTime(self):
        return self._data.get('progressExpiryTime', time.time())

    def isCompletedByGroup(self, groupByKey):
        bonusLimit = self.bonusCond.getBonusLimit()
        if bonusLimit is not None:
            if self.bonusCond.getGroupByValue() is None:
                return self.isCompleted()
            if self._progress is not None:
                return bonusLimit <= self.getBonusCount(groupByKey)
        return False

    def isCompleted(self, progress = None):
        progress = progress or self._progress
        bonusLimit = self.bonusCond.getBonusLimit()
        if bonusLimit is not None:
            groupBy = self.bonusCond.getGroupByValue()
            if groupBy is None:
                return self.getBonusCount(progress=progress) >= bonusLimit
            if progress is not None:
                if groupBy == 'nation':
                    return self.__checkGroupedCompletion(nations.AVAILABLE_NAMES, progress, bonusLimit)
                if groupBy == 'level':
                    return self.__checkGroupedCompletion(xrange(1, constants.MAX_VEHICLE_LEVEL + 1), progress, bonusLimit, keyMaker=lambda lvl: 'level %d' % lvl)
                if groupBy == 'class':
                    return self.__checkGroupedCompletion(constants.VEHICLE_CLASSES, progress, bonusLimit)
                if groupBy == 'vehicle':
                    pass
        return super(Quest, self).isCompleted()

    def setChildren(self, children):
        self._children = children

    def getChildren(self):
        return self._children

    def setParents(self, parents):
        self._parents = parents

    def getParents(self):
        return self._parents

    def getBonusCount(self, groupByKey = None, progress = None):
        progress = progress or self._progress
        if progress is not None:
            groupBy = self.bonusCond.getGroupByValue()
            if groupBy is None:
                return progress.get(None, {}).get('bonusCount', 0)
            if groupByKey is not None:
                return progress.get(groupByKey, {}).get('bonusCount', 0)
            return sum((p.get('bonusCount', 0) for p in progress.itervalues()))
        else:
            return 0

    def getProgressData(self):
        return self._progress or {}

    def getBonuses(self, bonusName = None):
        result = []
        for n, v in self._data.get('bonus', {}).iteritems():
            if bonusName is not None and n != bonusName:
                continue
            b = getBonusObj(n, v)
            if b is not None:
                result.append(b)

        return result

    def __checkGroupedCompletion(self, values, progress, bonusLimit = None, keyMaker = lambda v: v):
        bonusLimit = bonusLimit or self.bonusCond.getBonusLimit()
        for value in values:
            if bonusLimit > self.getBonusCount(groupByKey=keyMaker(value), progress=progress):
                return False

        return True

    def _checkConditions(self):
        isAccAvailable = self.accountReqs.isAvailable()
        isVehAvailable = self.vehicleReqs.isAnyVehicleAcceptable() or len(self.vehicleReqs.getSuitableVehicles()) > 0
        return isAccAvailable and isVehAvailable


class Action(ServerEventAbstract):

    def getUserType(self):
        return i18n.makeString(QUESTS.ITEM_TYPE_ACTION)

    def getModifiers(self):
        result = {}
        for stepData in self._data.get('steps'):
            mName = stepData.get('name')
            m = getModifierObj(mName, stepData.get('params'))
            if m is None:
                continue
            if mName in result:
                result[mName].update(m)
            else:
                result[mName] = m

        return sorted(result.itervalues(), key=operator.methodcaller('getName'), cmp=compareModifiers)


class HistoricalBattle(ServerEventAbstract):
    ICONS_FOLDER = 'gui/maps/icons/historicalBattles/'
    ICONS_FORMAT = '%s.png'
    ICONS_MASK = '../maps/icons/historicalBattles/%s.png'
    MAP_ICONS_MASK = '../maps/icons/map/stats/%(prefix)s%(geometryName)s.png'

    class SIDES(CONST_CONTAINER):
        A = 'A'
        B = 'B'

    def getUserName(self):
        return getLocalizedData(self._data['localized_data'], 'title')

    def getDescription(self):
        return getLocalizedData(self._data['localized_data'], 'shortDescr')

    def getLongDescription(self):
        return getLocalizedData(self._data['localized_data'], 'longDescr')

    def getSideUserName(self, side):
        return getLocalizedData(self._data['localized_data'], 'sideNames').get(side)

    def getDescriptionUrl(self):
        histNote = self._data.get('urls', {}).get('histNote')
        if histNote is not None:
            return histNote % {'langID': getClientLanguage()}
        else:
            return

    def getIcon(self):
        iconID = self._data.get('backgroundName', 'default')
        icon = self.ICONS_MASK % iconID
        if self.ICONS_FORMAT % iconID not in ResMgr.openSection(self.ICONS_FOLDER).keys():
            icon = self.ICONS_MASK % 'default'
        return icon

    def isFuture(self):
        return self.getStartTimeLeft() > 0

    def getDatesInfo(self):
        return '%(startDate)s - %(endDate)s' % {'startDate': self.getStartDate(),
         'endDate': self.getFinishDate()}

    def getStartDate(self):
        return BigWorld.wg_getShortDateFormat(self.getStartTime())

    def getFinishDate(self):
        return BigWorld.wg_getShortDateFormat(self.getFinishTime())

    def getArenaTypeID(self):
        return self._data['arenaTypeID']

    def getArenaType(self):
        return ArenaType.g_cache[self.getArenaTypeID()]

    def getMapName(self):
        return i18n.makeString('#arenas:%s/name' % self.getArenaType().geometryName)

    def getMapInfo(self):
        arenaType = self.getArenaType()
        battleType = i18n.makeString('#arenas:type/%s/name' % arenaType.gameplayName)
        defTeam = self.SIDES.A
        assaultTeam = self.SIDES.B
        additionalInfo = ''
        if arenaType.gameplayName == 'assault':
            if self._data['arenaTeam1'] == self.SIDES.B:
                defTeam, assaultTeam = assaultTeam, defTeam
            additionalInfo = i18n.makeString('#historical_battles:map/assaultInfo', defTeam=self.getSideUserName(defTeam), assaultTeam=self.getSideUserName(assaultTeam))
        return '<b>%s</b>\n%s' % (battleType, additionalInfo)

    def getMapIcon(self):
        return self.MAP_ICONS_MASK % {'geometryName': self.getArenaType().geometryName,
         'prefix': ''}

    def getTeamRoster(self, side):
        result = []
        for intCD, team in self._data['vehSides'].iteritems():
            if team == side:
                result.append(intCD)

        return result

    def getVehiclesData(self):
        return self._data['vehicles']

    def getVehicleData(self, intCD):
        return self._data['vehicles'].get(intCD)

    def canParticipateWith(self, vehicleCompDescr):
        return vehicleCompDescr in self._data['vehicles']

    def getShellsLayout(self, intCD):
        vehicleData = self._data['vehicles'].get(intCD)
        if vehicleData is None:
            return tuple()
        else:
            return map(lambda data: (g_itemsCache.items.getItemByCD(data[0]), data[1]), AmmoIterator(vehicleData['ammoList']))

    def getShellsLayoutPrice(self, intCD):
        vehicleData = self._data['vehicles'].get(intCD)
        if vehicleData is None:
            return tuple()
        else:
            shellsLayout = vehicleData['ammoList']

            def calculateLayout(isBoughtForCredits):
                goldPrice = 0
                creditsPrice = 0
                for shellCompDescr, count in AmmoIterator(shellsLayout):
                    if not shellCompDescr or not count:
                        continue
                    shell = g_itemsCache.items.getItemByCD(shellCompDescr)
                    if shell.buyPrice[1] and not isBoughtForCredits:
                        goldPrice += shell.buyPrice[1] * count
                    elif shell.buyPrice[1] and isBoughtForCredits:
                        creditsPrice += shell.buyPrice[1] * count * g_itemsCache.items.shop.exchangeRateForShellsAndEqs
                    elif shell.buyPrice[0]:
                        creditsPrice += shell.buyPrice[0] * count

                return (creditsPrice, goldPrice)

            forCredits = calculateLayout(True)
            forGold = calculateLayout(False)
            if forCredits != forGold:
                return [calculateLayout(False), calculateLayout(True)]
            return [calculateLayout(True)]
            return

    def getShellsLayoutPriceStatus(self, intCD):
        userCredits = g_itemsCache.items.stats.credits
        userGold = g_itemsCache.items.stats.gold
        result = []
        for c, g in self.getShellsLayoutPrice(intCD):
            result.append((userGold >= g, userCredits >= c))

        return result

    def getShellsLayoutFormatedPrice(self, intCD, colorManager, checkMoney = True, joinString = False):
        userCredits = g_itemsCache.items.stats.credits
        userGold = g_itemsCache.items.stats.gold
        creditsColor = colorManager.getColorScheme('textColorCredits').get('rgb')
        goldColor = colorManager.getColorScheme('textColorGold').get('rgb')
        errorColor = colorManager.getColorScheme('textColorError').get('rgb')
        result = []
        for c, g in self.getShellsLayoutPrice(intCD):
            priceLabel = ''
            if g:
                params = {'value': BigWorld.wg_getGoldFormat(g),
                 'color': goldColor if not checkMoney or userGold >= g else errorColor,
                 'icon': 'img://gui/maps/icons/library/GoldIcon-2.png'}
                priceLabel += makeHtmlString('html_templates:lobby/historicalBattles/ammoStatus', 'priceLabel', params)
            if c:
                params = {'value': BigWorld.wg_getIntegralFormat(c),
                 'color': creditsColor if not checkMoney or userCredits >= c else errorColor,
                 'icon': 'img://gui/maps/icons/library/CreditsIcon-2.png'}
                priceLabel += makeHtmlString('html_templates:lobby/historicalBattles/ammoStatus', 'priceLabel', params)
            result.append(priceLabel)

        if joinString:
            return i18n.makeString('#historical_battles:ammoPreset/priceConcat').join(result)
        return result

    def getModules(self, vehicle):
        vehicleData = self._data['vehicles'].get(vehicle.intCD)
        if vehicleData is None:
            return
        else:
            vDescr = self.getVehicleModifiedDescr(vehicle)
            result = OrderedDict()
            for guiItemType in GUI_ITEM_TYPE.VEHICLE_MODULES:
                if guiItemType == GUI_ITEM_TYPE.TURRET and not vehicle.hasTurrets:
                    continue
                itemDescr, _ = vDescr.getComponentsByType(GUI_ITEM_TYPE_NAMES[guiItemType])
                result[guiItemType] = g_itemsCache.items.getItemByCD(itemDescr['compactDescr'])

            return result

    def getVehicleModifiedDescr(self, vehicle):
        updatedVehDescr = vehicle.descriptor
        if self.canParticipateWith(vehicle.intCD):
            from gui import game_control
            igrRoomType = game_control.g_instance.igr.getRoomType()
            igrLayout = g_itemsCache.items.inventory.getIgrCustomizationsLayout()
            updatedVehDescr = getHistoricalCustomization(igrLayout, vehicle.invID, igrRoomType, updatedVehDescr.makeCompactDescr(), self._data)
        return updatedVehDescr

    def __cmp__(self, other):
        return cmp(self.getStartTime(), other.getStartTime())
