# Embedded file name: scripts/client/gui/shared/server_events/modifiers.py
import operator
from collections import defaultdict
from abc import ABCMeta, abstractmethod
import constants
import nations
from debug_utils import LOG_CURRENT_EXCEPTION, LOG_ERROR, LOG_DEBUG
from items import vehicles, ITEM_TYPE_NAMES
from helpers import i18n
from gui import nationCompareByName
from gui.shared import g_itemsCache, REQ_CRITERIA
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.utils import CONST_CONTAINER, BoundMethodWeakref as bwr
from gui.shared.server_events import formatters
from gui.Scaleform.locale.QUESTS import QUESTS
_VEH_TYPE_IDX = 1
_VEH_TYPE_NAME = ITEM_TYPE_NAMES[_VEH_TYPE_IDX]
_DT = formatters.DISCOUNT_TYPE

class ACTION_MODIFIER_TYPE(CONST_CONTAINER):
    DISCOUNT = 1
    SELLING = 2


class ACTION_SECTION_TYPE(CONST_CONTAINER):
    ECONOMICS = 1
    ALL = 2
    ITEM = 3
    CUSTOMIZATION = 4


def _getDiscountByValue(value, default):
    return int(default - value)


def _getPercentDiscountByValue(value, default):
    return g_itemsCache.items.shop.getActionPrc(value, default)


def _getDiscountByMultiplier(mult, default):
    return int(default - default * float(mult))


def _getPercentDiscountByMultiplier(mult, default):
    price = int(round(float(mult) * default))
    return g_itemsCache.items.shop.getActionPrc(price, default)


def _prepareVehData(vehsList, discounts = None):
    discounts = discounts or {}
    result = []
    for v in vehsList:
        discount, discountType = discounts.get(v, (None, None))
        result.append((v, (True, discount, discountType)))

    return result


class ActionModifier(object):

    def __init__(self, name, params, modType, section = ACTION_SECTION_TYPE.ECONOMICS, itemType = None):
        self._name = name
        self._params = params
        self._type = modType
        self._itemType = itemType
        self._section = section
        self.__extParams = []
        self.__cachedValue = None
        return

    def getName(self):
        return self._name

    def getParams(self):
        return self._params

    def getType(self):
        return self._type

    def getItemType(self):
        return self._itemType

    def getSection(self):
        return self._section

    def getValues(self, action):
        return {}

    def parse(self):
        if self.__cachedValue is None:
            self.__cachedValue = self._parse()
            for p in self.__extParams:
                self.__cachedValue.update(p)

        return self.__cachedValue

    def format(self, event = None):
        return None

    def update(self, modifier):
        p = modifier.parse()
        if p is not None:
            self.__extParams.append(p)
        return

    def _parse(self):
        return None


class _DiscountsListAction(ActionModifier):
    __meta__ = ABCMeta
    MAX_VEH_COUNT = 10
    DEFAULT_PRICE_MULT = 1.0

    @abstractmethod
    def _getParamName(self, idx):
        pass

    @abstractmethod
    def _getMultName(self, idx):
        pass

    @abstractmethod
    def _makeResultItem(self, paramValue):
        pass

    def _parse(self):
        result = {}
        for idx in xrange(self.MAX_VEH_COUNT):
            paramName = self._getParamName(idx)
            if paramName in self._params:
                item = self._makeResultItem(self._params[paramName])
                if item is not None:
                    result[item] = float(self._params.get(self._getMultName(idx), self.DEFAULT_PRICE_MULT))

        return result

    def getValues(self, action):
        result = {}
        for veh, value in self.parse().iteritems():
            result[veh.intCD] = [(value, action.getID())]

        return result


class _PriceOpAbstract(object):
    __meta__ = ABCMeta

    @abstractmethod
    def _getDiscountParams(self, item, value):
        return []


class _BuyPriceSet(_PriceOpAbstract):

    def _getDiscountParams(self, item, value):
        if item.defaultPrice[1]:
            return (_getPercentDiscountByValue(value, item.defaultPrice[1]), _DT.GOLD)
        return (_getPercentDiscountByValue(value, item.defaultPrice[0]), _DT.CREDITS)


class _BuyPriceMul(_PriceOpAbstract):

    def _getDiscountParams(self, item, value):
        if item.defaultPrice[1]:
            return (_getPercentDiscountByMultiplier(value, item.defaultPrice[1]), _DT.GOLD)
        return (_getPercentDiscountByMultiplier(value, item.defaultPrice[0]), _DT.CREDITS)


class _SellPriceMul(_PriceOpAbstract):

    def _getDiscountParams(self, item, value):
        isForGold, value = value
        if item.buyPrice[1]:
            if isForGold:
                return (int(item.buyPrice[1] * float(value)), _DT.GOLD)
            else:
                creditsPrice = item.buyPrice[1] * g_itemsCache.items.shop.exchangeRate
                return (int(creditsPrice * float(value)), _DT.CREDITS)
        return (int(item.buyPrice[0] * float(value)), _DT.CREDITS)


class _ItemsPrice(_DiscountsListAction, _PriceOpAbstract):

    def __init__(self, name, params, modType = ACTION_MODIFIER_TYPE.DISCOUNT, section = ACTION_SECTION_TYPE.ITEM, itemType = None):
        super(_ItemsPrice, self).__init__(name, params, modType, section, itemType)

    def format(self, event = None):
        result = []
        for item, value in sorted(self.parse().iteritems(), key=operator.itemgetter(0)):
            dv, dt = self._getDiscountParams(item, value)
            result.append(formatters.packDiscount(self._makeLabelString(item, discountType=dt), value=dv, discountType=_DT.PERCENT))

        return result

    @abstractmethod
    def _makeLabelString(self, item, discountType = None):
        pass

    def _getParamName(self, idx):
        return 'itemName%d' % idx

    def _getMultName(self, idx):
        return 'price%d' % idx


class _ItemsPriceAll(ActionModifier):
    __meta__ = ABCMeta
    DEFAULT_PRICE_MULT = 1.0

    def __init__(self, name, params, modType = ACTION_MODIFIER_TYPE.DISCOUNT, section = ACTION_SECTION_TYPE.ALL, itemType = None):
        super(_ItemsPriceAll, self).__init__(name, params, modType, section, itemType)

    def format(self, event = None):
        result = []
        fmtData = sorted(self.parse().iteritems(), key=operator.itemgetter(0), cmp=lambda a, b: nationCompareByName(a[0], b[0]))
        for (nation, multName), mulVal in fmtData:
            result.append(self._packMultiplier(multName, mulVal, nation))

        return result

    def _parse(self):
        result = {}
        nation = self._params.get(self._getNationName())
        if self._getGoldMultName() in self._params:
            result[nation, self._getGoldMultName()] = float(self._params[self._getGoldMultName()])
        if self._getCreditsMultName() in self._params:
            result[nation, self._getCreditsMultName()] = float(self._params[self._getCreditsMultName()])
        return result

    def _getGoldMultName(self):
        return 'goldPriceMultiplier'

    def _getCreditsMultName(self):
        return 'creditsPriceMultiplier'

    def _getNationName(self):
        return 'nation'

    @abstractmethod
    def _getLabelString(self, multName, nation = None):
        pass

    def _packMultiplier(self, multName, multVal, nation = None):
        return formatters.packDiscount(self._getLabelString(multName, nation), int(round((1 - float(multVal)) * 100)), _DT.PERCENT)

    def getValues(self, action):
        result = defaultdict(list)
        for (nation, multType), value in self.parse().iteritems():
            if nation is None:
                nation = nations.NONE_INDEX
            else:
                nation = nations.INDICES[nation]
            result[nation].append(((multType, value), action.getID()))

        return result


@abstractmethod

class _VehiclePrice(_ItemsPrice):

    def __init__(self, name, params, modType = ACTION_MODIFIER_TYPE.DISCOUNT, section = ACTION_SECTION_TYPE.ITEM):
        super(_VehiclePrice, self).__init__(name, params, modType, section, GUI_ITEM_TYPE.VEHICLE)

    def format(self, event = None):
        vehs = []
        discounts = {}
        for v, value in sorted(self.parse().iteritems(), key=operator.itemgetter(0)):
            dv, dt = self._getDiscountParams(v, value)
            dt = dt if self.getType() == ACTION_MODIFIER_TYPE.SELLING else _DT.PERCENT
            discounts[v] = (dv, dt)
            vehs.append(v)

        return [formatters.packContainer(self._makeLabelString(), isResizable=self._isResizableContainer(), subBlocks=[formatters.packVehiclesBlock(formatters.makeUniqueTableID(event, self.getName()), formatters.VEH_ACTION_HEADER, vehs=_prepareVehData(vehs, discounts), disableChecker=lambda veh: not veh.isInInventory, showNotInHangarCB=True, isShowInHangarCBChecked=True)])]

    def _isResizableContainer(self):
        return True

    def _makeLabelString(self, vehicle = None, discountType = None):
        return i18n.makeString('#quests:details/modifiers/vehicle')

    def _makeResultItem(self, vehName):
        try:
            if ':' in vehName:
                vehIDs = vehicles.g_list.getIDsByName(vehName)
            else:
                vehIDs = vehicles.g_list.getIDsByVehName(vehName)
            vehTypeCompDescr = vehicles.makeIntCompactDescrByID(_VEH_TYPE_NAME, *vehIDs)
            return g_itemsCache.items.getItemByCD(vehTypeCompDescr)
        except Exception:
            LOG_ERROR('There is error while getting vehicle item', vehName)
            LOG_CURRENT_EXCEPTION()

        return None

    def _getParamName(self, idx):
        return 'vehName%d' % idx


class _EquipmentPrice(_ItemsPrice):

    def __init__(self, name, params):
        super(_EquipmentPrice, self).__init__(name, params, itemType=GUI_ITEM_TYPE.EQUIPMENT)

    def _makeLabelString(self, eq, discountType = None):
        return i18n.makeString('#quests:details/modifiers/equipment/%s' % discountType, eqName=eq.userName)

    def _makeResultItem(self, eqName):
        try:
            vehCache = vehicles.g_cache
            idx = vehCache.equipmentIDs().get(eqName)
            if idx is not None:
                return g_itemsCache.items.getItemByCD(vehCache.equipments()[idx]['compactDescr'])
        except Exception:
            LOG_CURRENT_EXCEPTION()

        return


class _OptDevicePrice(_ItemsPrice):

    def __init__(self, name, params):
        super(_OptDevicePrice, self).__init__(name, params, itemType=GUI_ITEM_TYPE.OPTIONALDEVICE)

    def _makeLabelString(self, device, discountType = None):
        return i18n.makeString('#quests:details/modifiers/optDevice', devName=device.userName)

    def _makeResultItem(self, devName):
        try:
            vehCache = vehicles.g_cache
            idx = vehCache.optionalDeviceIDs().get(devName)
            if idx is not None:
                return g_itemsCache.items.getItemByCD(vehCache.optionalDevices()[idx]['compactDescr'])
        except Exception:
            LOG_CURRENT_EXCEPTION()

        return


class _ShellPrice(_ItemsPrice):

    def __init__(self, name, params):
        super(_ShellPrice, self).__init__(name, params, itemType=GUI_ITEM_TYPE.SHELL)

    def _makeLabelString(self, shell, discountType = None):
        return i18n.makeString('#quests:details/modifiers/shell/%s' % discountType, shellName=shell.userName)

    def _getParamName(self, idx):
        return 'shellName%d' % idx

    def _makeResultItem(self, shellName):
        shellNation, shellName = shellName.split(':')
        shellNation = nations.INDICES[shellNation]
        try:
            vehCache = vehicles.g_cache
            idx = vehCache.shellIDs(shellNation).get(shellName)
            if idx is not None:
                return g_itemsCache.items.getItemByCD(vehCache.shells(shellNation)[idx]['compactDescr'])
        except Exception:
            LOG_CURRENT_EXCEPTION()

        return


class EconomicsSet(ActionModifier):

    def __init__(self, name, params):
        super(EconomicsSet, self).__init__(name, params, ACTION_MODIFIER_TYPE.DISCOUNT)
        self.__handlers = (('premiumPacket1Cost', bwr(self._handlerPremiumPacket1)),
         ('premiumPacket3Cost', bwr(self._handlerPremiumPacket3)),
         ('premiumPacket7Cost', bwr(self._handlerPremiumPacket7)),
         ('premiumPacket30Cost', bwr(self._handlerPremiumPacket30)),
         ('premiumPacket180Cost', bwr(self._handlerPremiumPacket180)),
         ('premiumPacket360Cost', bwr(self._handlerPremiumPacket360)),
         ('freeXPConversionDiscrecity', bwr(self._handlerFreeXPConversionDiscrecity)),
         ('exchangeRate', bwr(self._handlerExchangeRate)),
         ('exchangeRateForShellsAndEqs', bwr(self._handlerExchangeRateForShellsAndEqs)),
         ('slotsPrices', bwr(self._handlerSlotsPrices)),
         ('creditsTankmanCost', bwr(self._handlerCreditsTankmanCost)),
         ('goldTankmanCost', bwr(self._handlerGoldTankmanCost)),
         ('creditsDropSkillsCost', bwr(self._handlerCreditsDropSkillsCost)),
         ('goldDropSkillsCost', bwr(self._handlerGoldDropSkillsCost)),
         ('clanCreationCost', bwr(self._handlerClanCreationCost)),
         ('paidRemovalCost', bwr(self._handlerPaidRemovalCost)),
         ('berthsPrices', bwr(self._handlerBerthsPrices)),
         ('passportChangeCost', bwr(self._handlerPassportChangeCost)),
         ('freeXPToTManXPRate', bwr(self._handlerFreeXPToTManXPRate)),
         ('camouflagePacketInfCost', bwr(self._handlerCamouflagePacketInfCost)),
         ('camouflagePacket7Cost', bwr(self._handlerCamouflagePacket7Cost)),
         ('camouflagePacket30Cost', bwr(self._handlerCamouflagePacket30Cost)),
         ('inscriptionPacketInfCost', bwr(self._handlerInscriptionPacketInfCost)),
         ('inscriptionPacket7Cost', bwr(self._handlerInscriptionPacket7Cost)),
         ('inscriptionPacket30Cost', bwr(self._handlerInscriptionPacket30Cost)),
         ('emblemPacketInfCost', bwr(self._handlerEmblemPacketInfCost)),
         ('emblemPacket7Cost', bwr(self._handlerEmblemPacket7Cost)),
         ('emblemPacket30Cost', bwr(self._handlerEmblemPacket30Cost)))

    def format(self, event = None):
        result = []
        data = self.parse()
        for name, handler in self.__handlers:
            wrappedName = self._wrapParamName(name)
            if wrappedName in data:
                try:
                    result.append(handler(data[wrappedName]))
                except Exception:
                    LOG_ERROR('Error while formatting economics param', name, wrappedName)
                    LOG_CURRENT_EXCEPTION()

        return result

    def _parse(self):
        return dict(map(lambda (k, v): (k, float(v)), self._params.iteritems()))

    def _wrapParamName(self, name):
        return name

    def _calcDiscountValue(self, value, default):
        return _getPercentDiscountByValue(float(value), default)

    def _calcCustomizationDiscountValue(self, value, default):
        return int(100 * _getDiscountByValue(int(value), default) / default)

    def _handlerSlotsPrices(self, value):
        default = g_itemsCache.items.shop.defaults.getVehicleSlotsPrice(g_itemsCache.items.stats.vehicleSlots)
        return self.__pack('slotsPrices', value, default, _DT.PERCENT)

    def _handlerBerthsPrices(self, value):
        default, _ = g_itemsCache.items.shop.defaults.getTankmanBerthPrice(g_itemsCache.items.stats.tankmenBerthsCount)
        return self.__pack('berthsPrices', value, default, _DT.PERCENT)

    def _handlerCreditsTankmanCost(self, value):
        tankmanCost = g_itemsCache.items.shop.defaults.tankmanCost
        if tankmanCost is not None:
            return self.__pack('creditsTankmanCost', value, tankmanCost[1]['credits'], _DT.PERCENT)
        else:
            return float(value)

    def _handlerGoldTankmanCost(self, value):
        tankmanCost = g_itemsCache.items.shop.defaults.tankmanCost
        if tankmanCost is not None:
            return self.__pack('goldTankmanCost', value, tankmanCost[2]['gold'], _DT.PERCENT)
        else:
            return float(value)

    def _handlerCreditsDropSkillsCost(self, value):
        dropSkillsCost = g_itemsCache.items.shop.defaults.dropSkillsCost
        if dropSkillsCost is not None:
            return self.__pack('creditsDropSkillsCost', value, dropSkillsCost[1]['credits'], _DT.PERCENT)
        else:
            return float(value)

    def _handlerGoldDropSkillsCost(self, value):
        dropSkillsCost = g_itemsCache.items.shop.defaults.dropSkillsCost
        if dropSkillsCost is not None:
            return self.__pack('goldDropSkillsCost', value, dropSkillsCost[2]['gold'], _DT.PERCENT)
        else:
            return float(value)

    def _handlerExchangeRate(self, value):
        default = g_itemsCache.items.shop.defaults.exchangeRate
        return self.__pack('exchangeRate', value, default, _DT.PERCENT)

    def _handlerExchangeRateForShellsAndEqs(self, value):
        default = g_itemsCache.items.shop.defaults.exchangeRateForShellsAndEqs
        return self.__pack('exchangeRateForShellsAndEqs', value, default, _DT.PERCENT)

    def _handlerPaidRemovalCost(self, value):
        default = g_itemsCache.items.shop.defaults.paidRemovalCost
        return self.__pack('paidRemovalCost', value, default, _DT.PERCENT)

    def _handlerPassportChangeCost(self, value):
        default = g_itemsCache.items.shop.defaults.passportChangeCost
        return self.__pack('passportChangeCost', value, default, _DT.PERCENT)

    def _handlerClanCreationCost(self, value):
        default = 2500
        return self.__pack('clanCreationCost', value, default, _DT.PERCENT)

    def _handlerFreeXPConversionDiscrecity(self, value):
        default, _ = g_itemsCache.items.shop.defaults.freeXPConversion
        return self.__pack('freeXPConversionDiscrecity', value, default, _DT.PERCENT)

    def _handlerFreeXPToTManXPRate(self, value):
        default = g_itemsCache.items.shop.defaults.freeXPToTManXPRate
        return self.__pack('freeXPToTManXPRate', value, default, _DT.PERCENT)

    def _handlerPremiumPacket1(self, value):
        default = g_itemsCache.items.shop.defaults.getPremiumPacketCost(1)
        return self.__pack('premiumPacket1', value, default, _DT.PERCENT)

    def _handlerPremiumPacket3(self, value):
        default = g_itemsCache.items.shop.defaults.getPremiumPacketCost(3)
        return self.__pack('premiumPacket3', value, default, _DT.PERCENT)

    def _handlerPremiumPacket7(self, value):
        default = g_itemsCache.items.shop.defaults.getPremiumPacketCost(7)
        return self.__pack('premiumPacket7', value, default, _DT.PERCENT)

    def _handlerPremiumPacket30(self, value):
        default = g_itemsCache.items.shop.defaults.getPremiumPacketCost(30)
        return self.__pack('premiumPacket30', value, default, _DT.PERCENT)

    def _handlerPremiumPacket180(self, value):
        default = g_itemsCache.items.shop.defaults.getPremiumPacketCost(180)
        return self.__pack('premiumPacket180', value, default, _DT.PERCENT)

    def _handlerPremiumPacket360(self, value):
        default = g_itemsCache.items.shop.defaults.getPremiumPacketCost(360)
        return self.__pack('premiumPacket360', value, default, _DT.PERCENT)

    def _handlerCamouflagePacketInfCost(self, value):
        default = g_itemsCache.items.shop.defaults.getCamouflageCost()
        return self.__pack('camouflagePacketInfCost', value, default[0], _DT.PERCENT, self._calcCustomizationDiscountValue)

    def _handlerCamouflagePacket7Cost(self, value):
        default = g_itemsCache.items.shop.defaults.getCamouflageCost(7)
        return self.__pack('camouflagePacket7Cost', value, default[0], _DT.PERCENT, self._calcCustomizationDiscountValue)

    def _handlerCamouflagePacket30Cost(self, value):
        default = g_itemsCache.items.shop.defaults.getCamouflageCost(30)
        return self.__pack('camouflagePacket30Cost', value, default[0], _DT.PERCENT, self._calcCustomizationDiscountValue)

    def _handlerInscriptionPacketInfCost(self, value):
        default = g_itemsCache.items.shop.defaults.getInscriptionCost()
        return self.__pack('inscriptionPacketInfCost', value, default[0], _DT.PERCENT, self._calcCustomizationDiscountValue)

    def _handlerInscriptionPacket7Cost(self, value):
        default = g_itemsCache.items.shop.defaults.getInscriptionCost(7)
        return self.__pack('inscriptionPacket7Cost', value, default[0], _DT.PERCENT, self._calcCustomizationDiscountValue)

    def _handlerInscriptionPacket30Cost(self, value):
        default = g_itemsCache.items.shop.defaults.getInscriptionCost(30)
        return self.__pack('inscriptionPacket30Cost', value, default[0], _DT.PERCENT, self._calcCustomizationDiscountValue)

    def _handlerEmblemPacketInfCost(self, value):
        default = g_itemsCache.items.shop.defaults.getEmblemCost()
        return self.__pack('emblemPacketInfCost', value, default[0], _DT.PERCENT, self._calcCustomizationDiscountValue)

    def _handlerEmblemPacket7Cost(self, value):
        default = g_itemsCache.items.shop.defaults.getEmblemCost(7)
        return self.__pack('emblemPacket7Cost', value, default[0], _DT.PERCENT, self._calcCustomizationDiscountValue)

    def _handlerEmblemPacket30Cost(self, value):
        default = g_itemsCache.items.shop.defaults.getEmblemCost(30)
        return self.__pack('emblemPacket30Cost', value, default[0], _DT.PERCENT, self._calcCustomizationDiscountValue)

    def __pack(self, paramName, discountVal, defaultVal, discountType, discountValueCalculator = None):
        calculator = discountValueCalculator or self._calcDiscountValue
        return formatters.packDiscount(i18n.makeString('#quests:details/modifiers/economics/%s' % paramName), value=calculator(discountVal, defaultVal), discountType=discountType)

    def getValues(self, action):
        result = defaultdict(dict)
        for key, value in self.parse().iteritems():
            result[key] = [(value, action.getID())]

        return result


class EconomicsMul(EconomicsSet):

    def _wrapParamName(self, name):
        if name not in ('exchangeRateForShellsAndEqs',):
            name = '%sMultiplier' % name
        return name

    def _calcDiscountValue(self, value, default):
        return _getPercentDiscountByMultiplier(value, default)

    def _calcCustomizationDiscountValue(self, value, default):
        return _getDiscountByMultiplier(float(value), 100)


class CamouflagePriceMul(_VehiclePrice):

    def __init__(self, name, params):
        super(_VehiclePrice, self).__init__(name, params, section=ACTION_SECTION_TYPE.CUSTOMIZATION)

    def format(self, event = None):
        result = []
        for vehicle, priceMult in sorted(self.parse().iteritems(), key=operator.itemgetter(0)):
            result.append(formatters.packDiscount(i18n.makeString('#quests:details/modifiers/customization/vehCamouflage', vehName=vehicle.userName), value=int((1 - priceMult) * 100), discountType=_DT.PERCENT))

        return result

    def _getMultName(self, idx):
        return 'priceFactorMultiplier%d' % idx


class EmblemPriceByGroupsMul(_DiscountsListAction):

    def __init__(self, name, params):
        super(EmblemPriceByGroupsMul, self).__init__(name, params, ACTION_MODIFIER_TYPE.DISCOUNT, ACTION_SECTION_TYPE.CUSTOMIZATION)

    def format(self, event = None):
        result = []
        groups, _, _ = vehicles.g_cache.playerEmblems()
        for groupName, priceMult in self.parse().iteritems():
            if groupName in groups:
                groupName = i18n.makeString(groups[groupName][1])
                result.append(formatters.packDiscount(i18n.makeString('#quests:details/modifiers/customization/groupEmblem', groupName=groupName), value=int((1 - priceMult) * 100), discountType=_DT.PERCENT))
            else:
                LOG_ERROR('Given group name is not available: ', groupName)

        return sorted(result, key=operator.methodcaller('getLabel'))

    def _makeResultItem(self, paramValue):
        return str(paramValue)

    def _getParamName(self, idx):
        return 'name%d' % idx

    def _getMultName(self, idx):
        return 'priceFactorMultiplier%d' % idx

    def getValues(self, action):
        result = {}
        for group, value in self.parse().iteritems():
            result[group] = [(value, action.getID())]

        return result


class EquipmentPriceSet(_EquipmentPrice, _BuyPriceSet):
    pass


class EquipmentPriceMul(_EquipmentPrice, _BuyPriceMul):

    def _getMultName(self, idx):
        return 'priceMultiplier%d' % idx


class EquipmentPriceAll(_ItemsPriceAll):

    def __init__(self, name, params):
        super(EquipmentPriceAll, self).__init__(name, params, itemType=GUI_ITEM_TYPE.EQUIPMENT)

    def _getLabelString(self, multName, nation = None):
        return i18n.makeString('#quests:details/modifiers/equipment/%s' % multName)


class OptDevicePriceAll(_ItemsPriceAll):

    def __init__(self, name, params):
        super(OptDevicePriceAll, self).__init__(name, params, itemType=GUI_ITEM_TYPE.OPTIONALDEVICE)

    def _getLabelString(self, multName, nation = None):
        return i18n.makeString('#quests:details/modifiers/optDevice/%s' % multName)


class OptDevicePriceSet(_OptDevicePrice, _BuyPriceSet):
    pass


class OptDevicePriceMul(_OptDevicePrice, _BuyPriceMul):

    def _getMultName(self, idx):
        return 'priceMultiplier%d' % idx


class ShellPriceAll(_ItemsPriceAll):

    def __init__(self, name, params):
        super(ShellPriceAll, self).__init__(name, params, itemType=GUI_ITEM_TYPE.SHELL)

    def _getLabelString(self, multName, nation = None):
        return i18n.makeString('#quests:details/modifiers/shell/%s' % multName)


class ShellPriceNation(ShellPriceAll):

    def _getLabelString(self, multName, nation = None):
        return i18n.makeString('#quests:details/modifiers/shell/nation/%s' % multName, nation=formatters.getNationName(nation))


class ShellPriceSet(_ShellPrice, _BuyPriceSet):
    pass


class ShellPriceMul(_ShellPrice, _BuyPriceMul):

    def _getMultName(self, idx):
        return 'priceMultiplier%d' % idx


class VehPriceAll(_ItemsPriceAll):

    def __init__(self, name, params):
        super(VehPriceAll, self).__init__(name, params, itemType=GUI_ITEM_TYPE.VEHICLE)

    def _getLabelString(self, multName, nation = None):
        return i18n.makeString('#quests:details/modifiers/vehicle/%s' % multName)


class VehPriceNation(_ItemsPriceAll):

    def __init__(self, name, params):
        super(VehPriceNation, self).__init__(name, params, itemType=GUI_ITEM_TYPE.VEHICLE)

    def _getLabelString(self, multName, nation = None):
        return i18n.makeString('#quests:details/modifiers/vehicle/nation/%s' % multName, nation=formatters.getNationName(nation))


class VehPriceSet(_VehiclePrice, _BuyPriceSet):
    pass


class VehPriceMul(_VehiclePrice, _BuyPriceMul):

    def _getMultName(self, idx):
        return 'priceMultiplier%d' % idx


class VehPriceCond(_VehiclePrice, _BuyPriceMul):
    DEFAULT_PRICE_MULT = 1.0

    def _parse(self):
        result = {}
        try:
            goldPriceMult = self._params.get('goldPriceMultiplier')
            creditsPriceMult = self._params.get('creditsPriceMultiplier')
            criteria = ~REQ_CRITERIA.SECRET | ~REQ_CRITERIA.HIDDEN
            if 'nation' in self._params:
                criteria |= REQ_CRITERIA.NATIONS([nations.INDICES[self._params['nation']]])
            if 'levelEqual' in self._params:
                criteria |= REQ_CRITERIA.VEHICLE.LEVELS([int(self._params['levelEqual'])])
            else:
                criteria |= REQ_CRITERIA.VEHICLE.LEVELS(range(int(self._params.get('levelMoreThan', 0)) + 1, int(self._params.get('levelLessThan', constants.MAX_VEHICLE_LEVEL + 1))))
            if 'vehClass' in self._params:
                criteria |= REQ_CRITERIA.VEHICLE.CLASSES([self._params['vehClass']])
            for v in g_itemsCache.items.getVehicles(criteria).itervalues():
                if v.buyPrice[1] and goldPriceMult is not None:
                    result[v] = float(goldPriceMult)
                elif v.buyPrice[0] and creditsPriceMult is not None:
                    result[v] = float(creditsPriceMult)

        except Exception:
            LOG_ERROR('There is error while vehicles getting')
            LOG_CURRENT_EXCEPTION()

        return result


class VehSellPriceSet(_VehiclePrice, _SellPriceMul):
    DEFAULT_PRICE_MULT = 0.5

    def __init__(self, name, params):
        super(VehSellPriceSet, self).__init__(name, params, ACTION_MODIFIER_TYPE.SELLING)

    def format(self, event = None):
        vehs = []
        discounts = {}
        for v, value in sorted(self.parse().iteritems(), key=operator.itemgetter(0)):
            discounts[v] = self._getDiscountParams(v, value)
            vehs.append(v)

        return [formatters.packTopLevelContainer(QUESTS.DETAILS_MODIFIERS_TITLE_SELLING, subBlocks=[formatters.packVehiclesBlock(formatters.makeUniqueTableID(event, self.getName()), formatters.VEH_ACTION_HEADER, vehs=_prepareVehData(vehs, discounts), disableChecker=lambda veh: not veh.isInInventory, showInHangarCB=True, isShowInHangarCBChecked=True)])]

    def _parse(self):
        isForGold = self._params.get('sellForGold', 'false') != 'false'
        result = {}
        for v, value in super(VehSellPriceSet, self)._parse().iteritems():
            result[v] = (isForGold, value)

        return result

    def _getMultName(self, idx):
        return 'sellPriceFactor'


_MODIFIERS = (('mul_EconomicsParams', EconomicsMul),
 ('set_EconomicsParams', EconomicsSet),
 ('cond_VehPrice', VehPriceCond),
 ('mul_VehPrice', VehPriceMul),
 ('set_VehPrice', VehPriceSet),
 ('mul_VehPriceAll', VehPriceAll),
 ('mul_VehPriceNation', VehPriceNation),
 ('set_VehSellPrice', VehSellPriceSet),
 ('mul_EquipmentPriceAll', EquipmentPriceAll),
 ('mul_EquipmentPrice', EquipmentPriceMul),
 ('set_EquipmentPrice', EquipmentPriceSet),
 ('mul_OptionalDevicePriceAll', OptDevicePriceAll),
 ('mul_OptionalDevicePrice', OptDevicePriceMul),
 ('set_OptionalDevicePrice', OptDevicePriceSet),
 ('mul_ShellPriceAll', ShellPriceAll),
 ('mul_ShellPriceNation', ShellPriceNation),
 ('mul_ShellPrice', ShellPriceMul),
 ('set_ShellPrice', ShellPriceSet),
 ('mul_CamouflagePriceFactor', CamouflagePriceMul),
 ('mul_EmblemPriceFactorByGroups', EmblemPriceByGroupsMul))
_MODIFIERS_DICT = dict(_MODIFIERS)
_MODIFIERS_ORDER = dict(((n, idx) for idx, (n, _) in enumerate(_MODIFIERS)))

def compareModifiers(modName1, modName2):
    if modName1 not in _MODIFIERS_ORDER:
        return -1
    if modName2 not in _MODIFIERS_ORDER:
        return 1
    return _MODIFIERS_ORDER[modName1] - _MODIFIERS_ORDER[modName2]


def getModifierObj(name, params):
    if name in _MODIFIERS_DICT:
        return _MODIFIERS_DICT[name](name, params)
    else:
        return None
