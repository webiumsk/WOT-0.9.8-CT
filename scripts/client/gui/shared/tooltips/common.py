# Embedded file name: scripts/client/gui/shared/tooltips/common.py
import cPickle
import types
import math
from collections import namedtuple
from operator import methodcaller, itemgetter, attrgetter
import BigWorld
import constants
import ArenaType
import fortified_regions
from gui.Scaleform.daapi.view.lobby.profile.ProfileUtils import ProfileUtils
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.managers.UtilsManager import ImageUrlProperties
from gui.Scaleform.framework.managers.TextManager import TextType, TextIcons
from gui.clubs.formatters import getLeagueString, getDivisionString
from gui.clubs.settings import getLadderChevron256x256, getPointsToNextDivision
from gui.prb_control import getBattleID
from gui.shared.economics import getPremiumCostActionPrc
from gui.shared.formatters import text_styles
from gui.shared.formatters.time_formatters import getRentLeftTimeStr
from gui.shared.fortifications.settings import FORT_BATTLE_DIVISIONS
from gui.shared.gui_items.Vehicle import VEHICLE_TAGS, getLevelIconPath
from gui.LobbyContext import g_lobbyContext
from gui.shared.tooltips import efficiency
from messenger.gui.Scaleform.data.contacts_vo_converter import ContactConverter, makeClanFullName, makeClubFullName, makeContactStatusDescription
from predefined_hosts import g_preDefinedHosts
from constants import PREBATTLE_TYPE, WG_GAMES
from debug_utils import LOG_WARNING
from helpers import i18n, time_utils, html, int2roman
from helpers.i18n import makeString as ms, makeString
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortViewHelper import FortViewHelper
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS as FORT
from CurrentVehicle import g_currentVehicle
from UnitBase import SORTIE_DIVISION
from gui import g_htmlTemplates, makeHtmlString, game_control
from gui.Scaleform.daapi.view.lobby.fortifications.components.sorties_dps import makeDivisionData
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils import fort_formatters
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS as I18N_FORTIFICATIONS
from gui.Scaleform.locale.ITEM_TYPES import ITEM_TYPES
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.Scaleform.daapi.view.lobby.rally.vo_converters import makeBuildingIndicatorsVO
from gui.prb_control.items.unit_items import SupportedRosterSettings
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.utils import findFirst, CONST_CONTAINER
from gui.shared.ClanCache import g_clanCache
from gui.shared.tooltips import ToolTipBaseData, TOOLTIP_TYPE, ACTION_TOOLTIPS_TYPE, ToolTipMethodField, ToolTipParameterField, ToolTipData, ToolTipAttrField
from gui.shared import g_itemsCache
from gui.server_events import g_eventsCache
from gui.Scaleform.daapi.view.lobby.customization import CAMOUFLAGES_KIND_TEXTS, CAMOUFLAGES_NATIONS_TEXTS
from gui.Scaleform.locale.VEHICLE_CUSTOMIZATION import VEHICLE_CUSTOMIZATION
from gui.Scaleform.genConsts.CUSTOMIZATION_ITEM_TYPE import CUSTOMIZATION_ITEM_TYPE
from gui.Scaleform.genConsts.BATTLE_EFFICIENCY_TYPES import BATTLE_EFFICIENCY_TYPES
from items import vehicles
from messenger.storage import storage_getter
from messenger.m_constants import USER_TAG
from gui.Scaleform.locale.MESSENGER import MESSENGER

class FortOrderParamField(ToolTipParameterField):

    def _getValue(self):
        return [self._tooltip.item.getParams()]


class IgrTooltipData(ToolTipBaseData):

    def __init__(self, context):
        super(IgrTooltipData, self).__init__(context, TOOLTIP_TYPE.IGR)

    def getDisplayableData(self, *args):
        qLabels, qProgress = [], []
        premVehQuests = []
        if game_control.g_instance.igr.getRoomType() in (constants.IGR_TYPE.PREMIUM, constants.IGR_TYPE.BASE):
            quests = g_eventsCache.getQuests()
            for q in quests.itervalues():
                if game_control.g_instance.igr.getRoomType() == constants.IGR_TYPE.PREMIUM:
                    template = g_htmlTemplates['html_templates:lobby/tooltips']['igr_quest']
                    if q.accountReqs.hasIGRCondition() and not q.hasPremIGRVehBonus():
                        metaList = q.getBonuses('meta')
                        if len(metaList):
                            qLabels.append(metaList[0].format())
                        winCond = None
                        if q.postBattleCond.getConditions().getName() == 'and':
                            winCond = q.postBattleCond.getConditions().find('win')
                        isWin = winCond.getValue() if winCond is not None else False
                        battlesCond = q.bonusCond.getConditions().find('battles')
                        if battlesCond is not None:
                            curBattles, totalBattles = (0, 0)
                            progress = battlesCond.getProgressPerGroup()
                            if None in progress:
                                curBattles, totalBattles, _, _ = progress[None]
                            qProgress.append([curBattles, totalBattles, i18n.makeString('#quests:igr/tooltip/winsLabel') if isWin else i18n.makeString('#quests:igr/tooltip/battlesLabel')])
                if q.hasPremIGRVehBonus():
                    metaList = q.getBonuses('meta')
                    leftTime = time_utils.getTimeDeltaFromNow(q.getFinishTime())
                    if len(metaList) and leftTime > 0:
                        header = makeHtmlString('html_templates:lobby/tooltips', 'prem_igr_veh_quest_header', ctx={'qLabel': metaList[0].format()})
                        text = i18n.makeString('#tooltips:vehicleIgr/specialAbility')
                        localization = '#tooltips:vehicleIgr/%s'
                        actionLeft = getRentLeftTimeStr(localization, leftTime, timeStyle=TextType.STATS_TEXT)
                        text += '\n' + actionLeft
                        premVehQuests.append({'header': header,
                         'descr': text})

        descriptionTemplate = 'igr_description' if len(qLabels) == 0 else 'igr_description_with_quests'
        igrPercent = (game_control.g_instance.igr.getXPFactor() - 1) * 100
        igrType = game_control.g_instance.igr.getRoomType()
        icon = makeHtmlString('html_templates:igr/iconBig', 'premium' if igrType == constants.IGR_TYPE.PREMIUM else 'basic')
        return {'title': i18n.makeString(TOOLTIPS.IGR_TITLE, igrIcon=icon),
         'description': makeHtmlString('html_templates:lobby/tooltips', descriptionTemplate, {'igrValue': '{0}%'.format(BigWorld.wg_getIntegralFormat(igrPercent))}),
         'quests': map(lambda i: i.format(**template.ctx), qLabels),
         'progressHeader': makeHtmlString('html_templates:lobby/tooltips', 'igr_progress_header', {}),
         'progress': qProgress,
         'premVehQuests': premVehQuests}


class EfficiencyTooltipData(ToolTipBaseData):
    _packers = {BATTLE_EFFICIENCY_TYPES.ARMOR: efficiency.ArmorItemPacker,
     BATTLE_EFFICIENCY_TYPES.DAMAGE: efficiency.DamageItemPacker,
     BATTLE_EFFICIENCY_TYPES.DESTRUCTION: efficiency.KillItemPacker,
     BATTLE_EFFICIENCY_TYPES.DETECTION: efficiency.DetectionItemPacker,
     BATTLE_EFFICIENCY_TYPES.ASSIST: efficiency.AssistItemPacker,
     BATTLE_EFFICIENCY_TYPES.CRITS: efficiency.CritsItemPacker,
     BATTLE_EFFICIENCY_TYPES.CAPTURE: efficiency.CaptureItemPacker,
     BATTLE_EFFICIENCY_TYPES.DEFENCE: efficiency.DefenceItemPacker}

    def __init__(self, context):
        super(EfficiencyTooltipData, self).__init__(context, TOOLTIP_TYPE.EFFICIENCY)

    def getDisplayableData(self, _, value):
        dataDict = value.toDict()
        eventType = dataDict['type']
        isGarage = dataDict['isGarage']
        blocksData = self.getPackerData(eventType, dataDict)
        return {'type': eventType,
         'blocksData': blocksData,
         'isGarage': isGarage,
         'contentMargin': {'top': 10,
                           'left': 17,
                           'bottom': 15,
                           'right': 17}}

    def getPackerData(self, packerType, dataDict):
        if packerType in self._packers:
            return self._packers[packerType]().pack(dataDict)
        else:
            return []


class ContactTooltipData(ToolTipBaseData):

    def __init__(self, context):
        super(ContactTooltipData, self).__init__(context, TOOLTIP_TYPE.CONTACT)
        self.__converter = ContactConverter()

    @storage_getter('users')
    def usersStorage(self):
        return None

    @storage_getter('playerCtx')
    def playerCtx(self):
        return None

    def getDisplayableData(self, dbID, defaultName):
        userEntity = self.usersStorage.getUser(dbID)
        if userEntity is None:
            return {'userProps': {'userName': defaultName}}
        else:
            commonGuiData = self.__converter.makeVO(userEntity, False)
            tags = userEntity.getTags()
            resourceID = commonGuiData['resource']
            if resourceID == WG_GAMES.TANKS:
                statusDescription = makeContactStatusDescription(userEntity.isOnline(), tags, userEntity.getClientInfo())
            else:
                statusDescription = makeString('#tooltips:Contact/resource/%s' % resourceID)
            commonGuiData['statusDescription'] = statusDescription
            units = []
            currentUnit = ''
            region = g_lobbyContext.getRegionCode(userEntity.getID())
            if region is not None:
                currentUnit += self.__makeUnitStr(TOOLTIPS.CONTACT_UNITS_HOMEREALM, region)
            clanAbbrev = userEntity.getClanAbbrev()
            if clanAbbrev:
                currentUnit += self.__addBR(currentUnit)
                currentUnit += self.__makeUnitStr(TOOLTIPS.CONTACT_UNITS_CLAN, '[{0}]'.format(clanAbbrev))
            if currentUnit != '':
                units.append(currentUnit)
            currentUnit = ''
            if USER_TAG.IGNORED in tags:
                currentUnit += self.__makeIconUnitStr('contactIgnored.png', TOOLTIPS.CONTACT_UNITS_STATUS_DESCRIPTION_IGNORED)
            elif USER_TAG.SUB_TO not in tags and (userEntity.isFriend() or USER_TAG.SUB_PENDING_IN in tags):
                currentUnit += self.__addBR(currentUnit)
                currentUnit += self.__makeIconUnitStr('contactConfirmNeeded.png', TOOLTIPS.CONTACT_UNITS_STATUS_DESCRIPTION_PENDINGFRIENDSHIP)
            if USER_TAG.BAN_CHAT in tags:
                currentUnit += self.__addBR(currentUnit)
                currentUnit += self.__makeIconUnitStr('contactMsgsOff.png', TOOLTIPS.CONTACT_UNITS_STATUS_DESCRIPTION_CHATBAN)
            if USER_TAG.REFERRER in tags:
                currentUnit += self.__addBR(currentUnit)
                currentUnit += self.__makeReferralStr(TOOLTIPS.CONTACT_UNITS_STATUS_DESCRIPTION_RECRUITER)
            elif USER_TAG.REFERRAL in tags:
                currentUnit += self.__addBR(currentUnit)
                currentUnit += self.__makeReferralStr(TOOLTIPS.CONTACT_UNITS_STATUS_DESCRIPTION_RECRUIT)
            if currentUnit != '':
                units.append(currentUnit)
            groupsStr = ''
            userGroups = userEntity.getGroups()
            if len(userGroups) > 0:
                groupsStr += ', '.join(map(lambda group: html.escape(group), userGroups))
            if clanAbbrev and USER_TAG.CLAN_MEMBER in tags:
                groupsStr += self.__addComma(groupsStr)
                groupsStr += makeClanFullName(clanAbbrev)
            if USER_TAG.CLUB_MEMBER in tags:
                clubName = self.playerCtx.getMyClubName()
                if clubName:
                    groupsStr += self.__addComma(groupsStr)
                    groupsStr += makeClubFullName(clubName)
            if USER_TAG.IGNORED in tags:
                groupsStr += self.__addComma(groupsStr)
                groupsStr += makeString(MESSENGER.MESSENGER_CONTACTS_MAINGROPS_OTHER_IGNORED)
            if USER_TAG.SUB_PENDING_IN in tags:
                groupsStr += self.__addComma(groupsStr)
                groupsStr += makeString(MESSENGER.MESSENGER_CONTACTS_MAINGROPS_OTHER_FRIENDSHIPREQUEST)
            if groupsStr != '':
                units.append(self.__makeUnitStr(TOOLTIPS.CONTACT_UNITS_GROUPS, groupsStr + '.'))
            if len(units) > 0:
                commonGuiData['units'] = units
            return commonGuiData

    def __makeUnitStr(self, descr, val):
        return makeHtmlString('html_templates:contacts/contact', 'tooltipUnitTxt', {'descr': makeString(descr),
         'value': val})

    def __makeIconUnitStr(self, icon, descr):
        return self.__converter.makeIconTag(iconPath=icon) + ' ' + makeHtmlString('html_templates:contacts/contact', 'tooltipSimpleTxt', {'descr': makeString(descr)})

    def __makeReferralStr(self, descr):
        return self.__converter.makeIconTag(key='referrTag') + ' ' + makeHtmlString('html_templates:contacts/contact', 'tooltipSimpleTxt', {'descr': makeString(descr)})

    def __addBR(self, currentUnit):
        if currentUnit != '':
            return '<br/>'
        return ''

    def __addComma(self, currStr):
        if currStr != '':
            return ', '
        return ''


class SortieDivisionTooltipData(ToolTipBaseData):

    def __init__(self, context):
        super(SortieDivisionTooltipData, self).__init__(context, TOOLTIP_TYPE.FORTIFICATIONS)

    def getDisplayableData(self):
        divisionsData = []
        divisions = makeDivisionData(I18N_FORTIFICATIONS.sortie_division_name)
        for division in divisions:
            divisionsData.append({'divisName': division['label'],
             'divisLevels': self.__getLevelsStr(division['level']),
             'divisBonus': self.__getBonusStr(division['profit']),
             'divisPlayers': self.__getPlayerLimitsStr(*self.__getPlayerLimits(division['level']))})

        return {'divisions': divisionsData}

    def __getPlayerLimits(self, divisionType):
        divisionIndex = SORTIE_DIVISION._ORDER.index(divisionType)
        division = SupportedRosterSettings.list(PREBATTLE_TYPE.SORTIE)[divisionIndex]
        return (division.getMinSlots(), division.getMaxSlots())

    def __getPlayerLimitsStr(self, minCount, maxCount):
        return self.app.utilsManager.textManager.getText(TextType.MAIN_TEXT, str(minCount) + ' - ' + str(maxCount))

    def __getLevelsStr(self, maxlvl):
        minLevel = 1
        minLevelStr = fort_formatters.getTextLevel(minLevel)
        maxLevelStr = fort_formatters.getTextLevel(maxlvl)
        return self.app.utilsManager.textManager.getText(TextType.MAIN_TEXT, minLevelStr + ' - ' + maxLevelStr)

    def __getBonusStr(self, bonus):
        text = (TextType.DEFRES_TEXT, BigWorld.wg_getIntegralFormat(bonus) + ' ')
        icon = (TextIcons.NUT_ICON,)
        return self.app.utilsManager.textManager.concatStyles((text, icon))


class MapTooltipData(ToolTipBaseData):

    def __init__(self, context):
        super(MapTooltipData, self).__init__(context, TOOLTIP_TYPE.MAP)

    def getDisplayableData(self, arenaID):
        arenaType = ArenaType.g_cache[int(arenaID)]
        return {'mapName': i18n.makeString('#arenas:%s/name' % arenaType.geometryName),
         'gameplayName': i18n.makeString('#arenas:type/%s/name' % arenaType.gameplayName),
         'imageURL': '../maps/icons/map/%s.png' % arenaType.geometryName,
         'description': i18n.makeString('#arenas:%s/description' % arenaType.geometryName)}


class HistoricalAmmoTooltipData(ToolTipBaseData):

    def __init__(self, context):
        super(HistoricalAmmoTooltipData, self).__init__(context, TOOLTIP_TYPE.HISTORICAL_AMMO)

    def getDisplayableData(self, battleID, vehicleID):
        battle = g_eventsCache.getHistoricalBattles().get(battleID)
        shellsItems = battle.getShellsLayout(int(vehicleID))
        priceString = battle.getShellsLayoutFormatedPrice(int(vehicleID), self.app.colorManager, True, True)
        data = {'price': priceString,
         'shells': []}
        shells = data['shells']
        for shell, count in shellsItems:
            shells.append({'id': str(shell.intCD),
             'type': shell.type,
             'label': ITEM_TYPES.shell_kindsabbreviation(shell.type),
             'icon': '../maps/icons/ammopanel/ammo/%s' % shell.descriptor['icon'][0],
             'count': count})

        return data


class HistoricalModulesTooltipData(ToolTipBaseData):

    def __init__(self, context):
        super(HistoricalModulesTooltipData, self).__init__(context, TOOLTIP_TYPE.HISTORICAL_MODULES)

    def getDisplayableData(self, battleID):
        templatePath = 'html_templates:lobby/historicalBattles/tooltips'
        template = 'moduleLabel'
        vehicle = g_currentVehicle.item
        battle = g_eventsCache.getHistoricalBattles().get(battleID)
        modules = battle.getModules(vehicle)
        data = {}
        if modules is not None:
            modulesData = []
            for item in modules.itervalues():
                modulesData.append({'type': item.itemTypeName,
                 'label': makeHtmlString(templatePath, template, {'type': item.userType,
                           'name': item.userName})})

            data = {'tankName': vehicle.userName,
             'modules': modulesData}
        return data


class SettingsControlTooltipData(ToolTipBaseData):

    def __init__(self, context):
        super(SettingsControlTooltipData, self).__init__(context, TOOLTIP_TYPE.CONTROL)

    def getDisplayableData(self, controlID):
        result = {}
        key = '#settings:%s/name' % controlID
        if i18n.doesTextExist(key):
            result['header'] = i18n.makeString(key)
        else:
            result['header'] = i18n.makeString('#settings:%s' % controlID)
        result['body'] = i18n.makeString('#settings:%s/description' % controlID)
        key = '#settings:%s/warning' % controlID
        if i18n.doesTextExist(key):
            result['attention'] = i18n.makeString(key)
        return result


class SettingsButtonTooltipData(ToolTipBaseData):

    def __init__(self, context):
        super(SettingsButtonTooltipData, self).__init__(context, TOOLTIP_TYPE.CONTROL)

    def getDisplayableData(self):
        from ConnectionManager import connectionManager
        serverName = ''
        if connectionManager.peripheryID == 0:
            serverName = connectionManager.serverUserName
        else:
            hostsList = g_preDefinedHosts.getSimpleHostsList(g_preDefinedHosts.hostsWithRoaming())
            for key, name, csisStatus, peripheryID in hostsList:
                if connectionManager.peripheryID == peripheryID:
                    serverName = name
                    break

        serversStats = None
        if constants.IS_SHOW_SERVER_STATS:
            serversStats, _ = game_control.g_instance.serverStats.getFormattedStats()
        return {'name': i18n.makeString(TOOLTIPS.HEADER_MENU_HEADER),
         'description': i18n.makeString(TOOLTIPS.HEADER_MENU_DESCRIPTION),
         'serverHeader': i18n.makeString(TOOLTIPS.HEADER_MENU_SERVER),
         'serverName': serverName,
         'playersOnServer': i18n.makeString(TOOLTIPS.HEADER_MENU_PLAYERSONSERVER),
         'serversStats': serversStats}


class CustomizationItemTooltipData(ToolTipBaseData):

    def __init__(self, context):
        super(CustomizationItemTooltipData, self).__init__(context, TOOLTIP_TYPE.CONTROL)

    def _processVehiclesList(self, vehIntCDs):
        vehStrList = []
        for intCD in vehIntCDs:
            vehicle = vehicles.getVehicleType(int(intCD))
            if vehicle and VEHICLE_TAGS.SECRET not in vehicle.tags:
                vehStrList.append(vehicle.shortUserString)

        return vehStrList

    def getDisplayableData(self, type, id, nationId, timeLeft, isPermanent = None, value = None, isUsed = False, boundVehicle = None, boundToCurrentVehicle = False):
        ms = i18n.makeString
        item = self._context.buildItem(nationId, id, type)
        headerText = ''
        typeText = ''
        descriptionText = ''
        allow = None
        deny = None
        usageStr = None
        allowStr = None
        denyStr = None
        footerStr = ''
        footerList = []
        if timeLeft >= 0:
            timeLeftText = self.__getTimeLeftText(timeLeft, isUsed)
            timeLeftText = self.__getText(TextType.MAIN_TEXT, timeLeftText)
        else:
            timeLeftText = ''
        if isPermanent and value > 1:
            footerList.append(ms(VEHICLE_CUSTOMIZATION.CUSTOMIZATION_STORED, quantity=value))
        if type == CUSTOMIZATION_ITEM_TYPE.CAMOUFLAGE:
            headerText = item['description'] + '/label'
            allow = item['allow']
            deny = item['deny']
            typeText = ms(VEHICLE_CUSTOMIZATION.CAMOUFLAGE) + ' ' + ms(CAMOUFLAGES_KIND_TEXTS[item['kind']])
            descriptionText = self.__getText(TextType.STANDARD_TEXT, ms(item['description'] + '/description'))
        elif type == CUSTOMIZATION_ITEM_TYPE.EMBLEM:
            groupName, _, _, _, emblemName, _, _, allow, deny = item
            groups, _, _ = vehicles.g_cache.playerEmblems()
            _, group, _, _, _, _ = groups.get(groupName)
            headerText = emblemName
            typeText = ms(VEHICLE_CUSTOMIZATION.EMBLEM) + ' ' + ms(group)
            descriptionText = ''
        elif type == CUSTOMIZATION_ITEM_TYPE.INSCRIPTION:
            groupName, _, _, _, inscriptionName, _, _, allow, deny = item
            groups = vehicles.g_cache.customization(nationId).get('inscriptionGroups', {})
            _, group, _, _, _ = groups.get(groupName)
            headerText = inscriptionName
            typeText = ms(VEHICLE_CUSTOMIZATION.INSCRIPTION) + ' ' + ms(group)
            descriptionText = ''
        allow = self._processVehiclesList(allow)
        deny = self._processVehiclesList(deny)
        if boundVehicle is None and allow and len(allow) > 0:
            allowStr = ms(TOOLTIPS.CUSTOMIZATION_QUESTAWARD_EXACTVEHICLE, vehicle=', '.join(allow))
        if boundVehicle is None and deny and len(deny) > 0:
            denyStr = ms(TOOLTIPS.CUSTOMIZATION_QUESTAWARD_DENYVEHICLE, vehicle=', '.join(deny))
        if boundToCurrentVehicle:
            usageStr = self.__getText(TextType.STATS_TEXT, ms(TOOLTIPS.CUSTOMIZATION_QUESTAWARD_CURRENTVEHICLE))
        elif boundVehicle:
            vehicle = vehicles.getVehicleType(int(boundVehicle))
            usageStr = self.__getText(TextType.STATS_TEXT, ms(TOOLTIPS.CUSTOMIZATION_QUESTAWARD_EXACTVEHICLE, vehicle=vehicle.shortUserString))
        elif type != CUSTOMIZATION_ITEM_TYPE.EMBLEM and not allowStr:
            usageStr = self.__getText(TextType.STATS_TEXT, ms(CAMOUFLAGES_NATIONS_TEXTS[nationId]))
        if usageStr:
            footerList.append(usageStr)
        if allowStr:
            footerList.append(allowStr)
        if denyStr:
            footerList.append(denyStr)
        if len(footerList):
            footerStr = self.__getText(TextType.STATS_TEXT, '\n'.join(footerList))
        return {'header': self.__getText(TextType.HIGH_TITLE, ms(headerText)),
         'kind': self.__getText(TextType.MAIN_TEXT, typeText),
         'description': descriptionText,
         'timeLeft': timeLeftText,
         'vehicleType': footerStr}

    def __getText(self, type, text):
        return self.app.utilsManager.textManager.getText(type, text)

    def __getTimeLeftText(self, timeLeft, isUsed):
        ms = i18n.makeString
        result = ''
        if timeLeft > 0:
            secondsInDay = 86400
            secondsInHour = 3600
            secondsInMinute = 60
            if timeLeft > secondsInDay:
                timeLeft = int(math.ceil(timeLeft / secondsInDay))
                dimension = ms(VEHICLE_CUSTOMIZATION.TIMELEFT_TEMPORAL_DAYS)
            elif timeLeft > secondsInHour:
                timeLeft = int(math.ceil(timeLeft / secondsInHour))
                dimension = ms(VEHICLE_CUSTOMIZATION.TIMELEFT_TEMPORAL_HOURS)
            else:
                timeLeft = int(math.ceil(timeLeft / secondsInMinute))
                dimension = ms(VEHICLE_CUSTOMIZATION.TIMELEFT_TEMPORAL_MINUTES)
            result = ms(VEHICLE_CUSTOMIZATION.TIMELEFT_TEMPORAL_USED if isUsed else VEHICLE_CUSTOMIZATION.TIMELEFT_TEMPORAL, time=timeLeft, dimension=dimension)
        elif not timeLeft:
            result = ms(VEHICLE_CUSTOMIZATION.TIMELEFT_INFINITY)
        return result


class ClanInfoTooltipData(ToolTipBaseData, FortViewHelper):

    def __init__(self, context):
        super(ClanInfoTooltipData, self).__init__(context, TOOLTIP_TYPE.FORTIFICATIONS)

    def getDisplayableData(self, clanDBID):
        fortCtrl = g_clanCache.fortProvider.getController()
        isFortFrozen = False
        if clanDBID is None:
            fort = fortCtrl.getFort()
            fortDossier = fort.getFortDossier()
            battlesStats = fortDossier.getBattlesStats()
            isFortFrozen = self._isFortFrozen()
            clanName, clanMotto, clanTag = g_clanCache.clanName, g_clanCache.clanMotto, g_clanCache.clanTag
            clanLvl = fort.level if fort is not None else 0
            homePeripheryID = fort.peripheryID
            playersAtClan, buildingsNum = len(g_clanCache.clanMembers), len(fort.getBuildingsCompleted())
            wEfficiencyVal = ProfileUtils.getFormattedWinsEfficiency(battlesStats)
            combatCount, winsEff, profitEff = battlesStats.getBattlesCount(), ProfileUtils.UNAVAILABLE_SYMBOL if wEfficiencyVal == str(ProfileUtils.UNAVAILABLE_VALUE) else wEfficiencyVal, battlesStats.getProfitFactor()
            creationTime = fortDossier.getGlobalStats().getCreationTime()
            defence, vacation, offDay = fort.getDefencePeriod(), fort.getVacationDate(), fort.getLocalOffDay()
        elif type(clanDBID) in (types.IntType, types.LongType, types.FloatType):
            clanInfo = fortCtrl.getPublicInfoCache().getItem(clanDBID)
            if clanInfo is None:
                LOG_WARNING('Requested clan info is empty', clanDBID)
                return
            clanName, clanMotto = clanInfo.getClanName(), clanInfo.getClanMotto()
            clanMotto = html.escape(clanMotto)
            clanTag, clanLvl = '[%s]' % clanInfo.getClanAbbrev(), clanInfo.getLevel()
            homePeripheryID = clanInfo.getHomePeripheryID()
            playersAtClan, buildingsNum = (None, None)
            combatCount, profitEff = clanInfo.getBattleCount(), clanInfo.getProfitFactor()
            creationTime = None
            timestamp = clanInfo.getAvailability()
            defHour, defMin = clanInfo.getDefHourFor(timestamp)
            defenceStart = time_utils.getTimeForLocal(timestamp, defHour, defMin)
            defenceFinish = defenceStart + time_utils.ONE_HOUR
            defence = (defenceStart, defenceFinish)
            offDay = clanInfo.getLocalOffDayFor(timestamp)
            vacation = clanInfo.getVacationPeriod()
            winsEff = None
        else:
            LOG_WARNING('Invalid clanDBID identifier', clanDBID, type(clanDBID))
            return
        topStats = []
        host = g_preDefinedHosts.periphery(homePeripheryID)
        if host is not None:
            topStats.append((i18n.makeString(TOOLTIPS.FORTIFICATION_TOOLTIPENEMYCLANINFO_HOMEPEREPHIRY), host.name))
        if playersAtClan is not None:
            topStats.append((i18n.makeString(TOOLTIPS.FORTIFICATION_TOOLTIPENEMYCLANINFO_PLAYERSATCLAN), playersAtClan))
        if buildingsNum is not None:
            topStats.append((i18n.makeString(TOOLTIPS.FORTIFICATION_TOOLTIPENEMYCLANINFO_BUILDINGSATFORTIFICATION), buildingsNum))
        if combatCount is not None:
            topStats.append((i18n.makeString(TOOLTIPS.FORTIFICATION_TOOLTIPENEMYCLANINFO_FIGHTSFORFORTIFICATION), combatCount))
        if winsEff is not None:
            topStats.append((i18n.makeString(TOOLTIPS.FORTIFICATION_TOOLTIPENEMYCLANINFO_WINPERCENTAGE), winsEff))
        if profitEff is not None:
            topStats.append((i18n.makeString(TOOLTIPS.FORTIFICATION_TOOLTIPENEMYCLANINFO_PROFITPERCENTAGE), BigWorld.wg_getNiceNumberFormat(profitEff) if profitEff > 0 else ProfileUtils.UNAVAILABLE_SYMBOL))
        if creationTime is not None:
            fortCreationData = self.app.utilsManager.textManager.getText(TextType.NEUTRAL_TEXT, i18n.makeString(TOOLTIPS.FORTIFICATION_TOOLTIPCLANINFO_FORTCREATIONDATE, creationDate=BigWorld.wg_getLongDateFormat(creationTime)))
        else:
            fortCreationData = None

        def _makeLabels(stats, itemIdx):
            return '\n'.join((str(a[itemIdx]) for a in stats))

        infoTexts, protectionHeader = [], ''
        if defence[0]:
            if isFortFrozen:
                protectionHeader = self.app.utilsManager.textManager.getText(TextType.ERROR_TEXT, i18n.makeString(TOOLTIPS.FORTIFICATION_TOOLTIPENEMYCLANINFO_DEFENSETIMESTOPPED))
            else:
                protectionHeader = self.app.utilsManager.textManager.getText(TextType.HIGH_TITLE, i18n.makeString(TOOLTIPS.FORTIFICATION_TOOLTIPENEMYCLANINFO_DEFENSETIME))
            statsValueColor = TextType.DISABLE_TEXT if isFortFrozen else TextType.STATS_TEXT
            defencePeriodString = i18n.makeString(TOOLTIPS.FORTIFICATION_TOOLTIPENEMYCLANINFO_PERIOD, startTime=BigWorld.wg_getShortTimeFormat(defence[0]), finishTime=BigWorld.wg_getShortTimeFormat(defence[1]))
            defencePeriodString = self.app.utilsManager.textManager.getText(statsValueColor, defencePeriodString)
            infoTexts.append(i18n.makeString(TOOLTIPS.FORTIFICATION_TOOLTIPENEMYCLANINFO_DEFENSEHOUR, period=defencePeriodString))
            if offDay > -1:
                dayOffString = i18n.makeString('#menu:dateTime/weekDays/full/%d' % (offDay + 1))
            else:
                dayOffString = i18n.makeString(TOOLTIPS.FORTIFICATION_TOOLTIPENEMYCLANINFO_NODAYOFF)
            dayOffString = self.app.utilsManager.textManager.getText(statsValueColor, dayOffString)
            infoTexts.append(i18n.makeString(TOOLTIPS.FORTIFICATION_TOOLTIPENEMYCLANINFO_DAYOFF, dayOff=dayOffString))
            if vacation[0] and vacation[1]:
                vacationString = i18n.makeString(TOOLTIPS.FORTIFICATION_TOOLTIPENEMYCLANINFO_PERIOD, startTime=BigWorld.wg_getShortDateFormat(vacation[0]), finishTime=BigWorld.wg_getShortDateFormat(vacation[1]))
            else:
                vacationString = i18n.makeString(TOOLTIPS.FORTIFICATION_TOOLTIPENEMYCLANINFO_NOVACATION)
            vacationString = self.app.utilsManager.textManager.getText(statsValueColor, vacationString)
            infoTexts.append(i18n.makeString(TOOLTIPS.FORTIFICATION_TOOLTIPENEMYCLANINFO_VACATION, period=vacationString))
        return {'headerText': self.app.utilsManager.textManager.getText(TextType.HIGH_TITLE, i18n.makeString(TOOLTIPS.FORTIFICATION_TOOLTIPENEMYCLANINFO_HEADER, clanTag=clanTag, clanLevel=fort_formatters.getTextLevel(clanLvl))),
         'fullClanName': self.app.utilsManager.textManager.getText(TextType.NEUTRAL_TEXT, clanName),
         'sloganText': self.app.utilsManager.textManager.getText(TextType.STANDARD_TEXT, clanMotto),
         'infoDescriptionTopText': self.app.utilsManager.textManager.getText(TextType.MAIN_TEXT, _makeLabels(topStats, 0)),
         'infoTopText': self.app.utilsManager.textManager.getText('statsText', _makeLabels(topStats, 1)),
         'infoDescriptionBottomText': '',
         'infoBottomText': '',
         'protectionHeaderText': protectionHeader,
         'infoText': makeHtmlString('html_templates:lobby/fortifications/tooltips/defense_description', 'main', {'text': '\n'.join(infoTexts)}),
         'fortCreationDate': fortCreationData}


class ToolTipRefSysDescription(ToolTipBaseData):
    BONUSES_PRIORITY = ('vehicles', 'tankmen', 'credits')

    def __init__(self, context):
        super(ToolTipRefSysDescription, self).__init__(context, TOOLTIP_TYPE.REF_SYSTEM)

    def getDisplayableData(self):
        return {'titleTF': self.__makeTitle(),
         'actionTF': self.__makeMainText(TOOLTIPS.TOOLTIPREFSYSDESCRIPTION_HEADER_ACTIONTF),
         'conditionsTF': self.__makeConditions(),
         'awardsTitleTF': self.__makeStandardText(TOOLTIPS.TOOLTIPREFSYSDESCRIPTION_HEADER_AWARDSTITLETF),
         'blocksVOs': self.__makeBlocks(),
         'bottomTF': self.__makeMainText(TOOLTIPS.TOOLTIPREFSYSDESCRIPTION_BOTTOM_BOTTOMTF)}

    def __makeTitle(self):
        localMsg = ms(TOOLTIPS.TOOLTIPREFSYSDESCRIPTION_HEADER_TITLETF)
        return self.app.utilsManager.textManager.getText(TextType.HIGH_TITLE, localMsg)

    def __makeMainText(self, value):
        localMsg = ms(value)
        return self.app.utilsManager.textManager.getText(TextType.MAIN_TEXT, localMsg)

    def __makeConditions(self):
        txt = ms(TOOLTIPS.TOOLTIPREFSYSAWARDS_INFOBODY_CONDITIONS, top=game_control.g_instance.refSystem.getPosByXPinTeam())
        return self.app.utilsManager.textManager.getText(TextType.STANDARD_TEXT, txt)

    def __makeStandardText(self, value):
        localMsg = ms(value)
        return self.app.utilsManager.textManager.getText(TextType.STANDARD_TEXT, localMsg)

    def __makeBlocks(self):
        result = []
        for xp, quests in game_control.g_instance.refSystem.getQuests():
            xpCost = BigWorld.wg_getIntegralFormat(xp)
            awardDescrPars = []
            for quest in quests:
                for bonusName in self.BONUSES_PRIORITY:
                    bonuses = quest.getBonuses(bonusName)
                    if bonuses:
                        awardDescrPars.append(', '.join(map(methodcaller('getDescription'), bonuses)))

            awardDescr = ', '.join(awardDescrPars)
            result.append({'leftTF': self.app.utilsManager.textManager.getText(TextType.CREDITS_TEXT, xpCost),
             'rightTF': awardDescr,
             'iconSource': RES_ICONS.MAPS_ICONS_LIBRARY_NORMALXPICON})

        return result


class ToolTipRefSysAwards(ToolTipBaseData):
    BONUSES_PRIORITY = ('vehicles', 'tankmen', 'credits')

    def __init__(self, context):
        super(ToolTipRefSysAwards, self).__init__(context, TOOLTIP_TYPE.REF_SYSTEM)

    def getDisplayableData(self, data):
        xp, questIDs = cPickle.loads(data)

        def filterFunc(q):
            return q.getID() in questIDs

        quests = g_eventsCache.getHiddenQuests(filterFunc)
        icon = ''
        awardDescrPars = []
        isCompleted = True
        for quest in quests.itervalues():
            for bonusName in self.BONUSES_PRIORITY:
                bonuses = quest.getBonuses(bonusName)
                if bonuses:
                    awardDescrPars.append(', '.join(map(methodcaller('getDescription'), bonuses)))
                    if not icon:
                        icon = bonuses[0].getTooltipIcon()

            if isCompleted and not quest.isCompleted():
                isCompleted = False

        awardDescr = ', '.join(awardDescrPars)
        return {'iconSource': icon,
         'infoTitle': self.__makeTitle(awardDescr),
         'infoBody': self.__makeBody(xp, isCompleted),
         'conditions': self.__makeConditions(),
         'awardStatus': self.__makeStatus(isCompleted)}

    def __makeTitle(self, value):
        award = self.app.utilsManager.textManager.getText(TextType.HIGH_TITLE, value)
        return self.__makeTitleGeneralText(award)

    def __makeTitleGeneralText(self, award):
        text = i18n.makeString(TOOLTIPS.TOOLTIPREFSYSAWARDS_TITLE_GENERAL, awardMsg=award)
        return self.app.utilsManager.textManager.getText(TextType.HIGH_TITLE, text)

    def __makeBody(self, expCount, isCompleted):
        howManyExp = expCount - game_control.g_instance.refSystem.getReferralsXPPool()
        notEnoughMsg = ''
        if not isCompleted and howManyExp > 0:
            notEnough = self.app.utilsManager.textManager.getText(TextType.ERROR_TEXT, i18n.makeString(TOOLTIPS.TOOLTIPREFSYSAWARDS_INFOBODY_REQUIREMENTS_NOTENOUGH))
            notEnoughMsg = i18n.makeString(TOOLTIPS.TOOLTIPREFSYSAWARDS_INFOBODY_REQUIREMENTS_NOTENOUGHMSG, notEnough=notEnough, howMany=self.__formatExpCount(howManyExp))
        resultFormatter = self.app.utilsManager.textManager.getText(TextType.MAIN_TEXT, i18n.makeString(TOOLTIPS.TOOLTIPREFSYSAWARDS_INFOBODY_REQUIREMENTS, expCount=self.__formatExpCount(expCount), notEnoughMsg=notEnoughMsg))
        return resultFormatter

    def __formatExpCount(self, value):
        value = BigWorld.wg_getIntegralFormat(value)
        value = self.app.utilsManager.textManager.getText(TextType.CREDITS_TEXT, value)
        iconLocal = RES_ICONS.MAPS_ICONS_LIBRARY_NORMALXPICON
        utilsManager = self.app.utilsManager
        icon = utilsManager.getHtmlIconText(ImageUrlProperties(iconLocal, 16, 16, -3, 0))
        return value + icon

    def __makeConditions(self):
        txt = i18n.makeString(TOOLTIPS.TOOLTIPREFSYSAWARDS_INFOBODY_CONDITIONS, top=game_control.g_instance.refSystem.getPosByXPinTeam())
        return self.app.utilsManager.textManager.getText(TextType.STANDARD_TEXT, txt)

    def __makeStatus(self, isReceived):
        loc = TOOLTIPS.TOOLTIPREFSYSAWARDS_INFOBODY_NOTACCESS
        if isReceived:
            loc = TOOLTIPS.TOOLTIPREFSYSAWARDS_INFOBODY_ACCESS
        txt = i18n.makeString(loc)
        txt = self.app.utilsManager.textManager.getText(TextType.MAIN_TEXT, txt)
        return txt


class ToolTipRefSysXPMultiplier(ToolTipBaseData):

    def __init__(self, context):
        super(ToolTipRefSysXPMultiplier, self).__init__(context, TOOLTIP_TYPE.REF_SYSTEM)

    def getDisplayableData(self):
        refSystem = game_control.g_instance.refSystem
        xpIcon = RES_ICONS.MAPS_ICONS_LIBRARY_NORMALXPICON
        icon = self.app.utilsManager.getHtmlIconText(ImageUrlProperties(xpIcon, 16, 16, -3, 0))
        expNum = self.app.utilsManager.textManager.getText(TextType.CREDITS_TEXT, ms(BigWorld.wg_getNiceNumberFormat(refSystem.getMaxReferralXPPool())))
        titleText = self.app.utilsManager.textManager.getText(TextType.HIGH_TITLE, ms(TOOLTIPS.TOOLTIPREFSYSXPMULTIPLIER_TITLE))
        descriptionText = self.app.utilsManager.textManager.getText(TextType.MAIN_TEXT, ms(TOOLTIPS.TOOLTIPREFSYSXPMULTIPLIER_DESCRIPTION))
        conditionsText = self.app.utilsManager.textManager.getText(TextType.STANDARD_TEXT, ms(TOOLTIPS.TOOLTIPREFSYSXPMULTIPLIER_CONDITIONS))
        bottomText = self.app.utilsManager.textManager.getText(TextType.MAIN_TEXT, ms(TOOLTIPS.TOOLTIPREFSYSXPMULTIPLIER_BOTTOM, expNum=expNum + '<nobr>' + icon))
        xpBlocks = []
        for i, (period, bonus) in enumerate(refSystem.getRefPeriods()):
            xpBonus = 'x%s' % BigWorld.wg_getNiceNumberFormat(bonus)
            condition = self.__formatPeriod(period)
            xpBlocks.append({'xpIconSource': RES_ICONS.MAPS_ICONS_LIBRARY_NORMALXPICON,
             'multiplierText': self.app.utilsManager.textManager.getText(TextType.CREDITS_TEXT, xpBonus),
             'descriptionText': self.app.utilsManager.textManager.getText(TextType.MAIN_TEXT, condition)})

        return {'titleText': titleText,
         'descriptionText': descriptionText,
         'conditionsText': conditionsText,
         'bottomText': bottomText,
         'xpBlocksVOs': xpBlocks}

    def __formatPeriod(self, period):
        if period <= 24:
            return ms(TOOLTIPS.TOOLTIPREFSYSXPMULTIPLIER_CONDITIONS_HOURS, hoursNum=period)
        if period <= 8760:
            return ms(TOOLTIPS.TOOLTIPREFSYSXPMULTIPLIER_CONDITIONS_DAYS, daysNum=period / 24)
        return ms(TOOLTIPS.TOOLTIPREFSYSXPMULTIPLIER_CONDITIONS_OTHER)


_battleStatus = namedtuple('_battleStatus', ('level', 'msg', 'color', 'prefix'))

class ToolTipFortBuildingData(ToolTipBaseData, FortViewHelper):

    class BATTLE_STATUSES(CONST_CONTAINER):
        NO_BATTLE = _battleStatus('warning', FORT.TOOLTIPBUILDINGINFO_STATUSMSG_WASNOTBATTLE, TextType.DEFRES_TEXT, '')
        LOST = _battleStatus('critical', FORT.TOOLTIPBUILDINGINFO_STATUSMSG_DEFEAT, TextType.ERROR_TEXT, '-')
        WON = _battleStatus('info', FORT.TOOLTIPBUILDINGINFO_STATUSMSG_VICTORY, TextType.SUCCESS_TEXT, '+')

    def __init__(self, context):
        super(ToolTipFortBuildingData, self).__init__(context, TOOLTIP_TYPE.FORTIFICATIONS)

    def getDisplayableData(self, buildingUID, isMine):
        ms = i18n.makeString
        fort = self.fortCtrl.getFort()
        battleID = getBattleID()
        battle = fort.getBattle(battleID)
        buildingTypeID = self.getBuildingIDbyUID(buildingUID)
        if battle.isDefence():
            isAttack = not isMine
        else:
            isAttack = isMine
        if isAttack:
            buildingsList = battle.getAttackerBuildList()
            buildingsFullList = battle.getAttackerFullBuildList()
        else:
            buildingsList = battle.getDefenderBuildList()
            buildingsFullList = battle.getDefenderFullBuildList()
        buildingFullData = findFirst(lambda x: x[0] == buildingTypeID, buildingsFullList)
        _, status, buildingLevel, hpVal, defResVal = buildingFullData
        isReadyForBattle = status == constants.FORT_BUILDING_STATUS.READY_FOR_BATTLE
        buildingData = None
        resCount, arenaTypeID = (None, None)
        if isReadyForBattle:
            buildingData = findFirst(lambda x: x[0] == buildingTypeID, buildingsList)
            _, resCount, arenaTypeID = buildingData
        _, status, buildingLevel, hpVal, defResVal = buildingFullData
        progress = self._getProgress(buildingTypeID, buildingLevel)
        normLevel = max(buildingLevel, 1)
        buildingLevelData = fortified_regions.g_cache.buildings[buildingTypeID].levels[normLevel]
        hpTotalVal = buildingLevelData.hp
        maxDefResVal = buildingLevelData.storage
        buildingName = self.app.utilsManager.textManager.getText(TextType.HIGH_TITLE, ms(FORT.buildings_buildingname(buildingUID)))
        currentMapTxt = None
        buildingLevelTxt = self.app.utilsManager.textManager.getText(TextType.MAIN_TEXT, ms(FORT.FORTMAINVIEW_HEADER_LEVELSLBL, buildLevel=str(fort_formatters.getTextLevel(buildingLevel))))
        descrActionTxt = None
        statusTxt = None
        statusLevel = None
        indicatorsModel = None
        infoMessage = None
        if status == constants.FORT_BUILDING_STATUS.LOW_LEVEL:
            minBuildingLevel = fortified_regions.g_cache.defenceConditions.minRegionLevel
            minLevel = fort_formatters.getTextLevel(1)
            maxLevel = fort_formatters.getTextLevel(minBuildingLevel - 1)
            infoMessage = ms(FORT.TOOLTIPBUILDINGINFO_LOWLEVELMESSAGE, minLevel=minLevel, maxLevel=maxLevel)
        else:
            indicatorsModel = makeBuildingIndicatorsVO(buildingLevel, progress, hpVal, hpTotalVal, defResVal, maxDefResVal)
            if isReadyForBattle:
                lootedBuildings = battle.getLootedBuildList()
                battleStatus = self.BATTLE_STATUSES.NO_BATTLE
                if (buildingData, isAttack) in lootedBuildings:
                    battleStatus = self.BATTLE_STATUSES.LOST
                    if battle.isDefence() and isAttack or not battle.isDefence() and not isAttack:
                        battleStatus = self.BATTLE_STATUSES.WON
                arenaType = ArenaType.g_cache.get(arenaTypeID)
                prefix = self.app.utilsManager.textManager.getText(TextType.STANDARD_TEXT, ms(FORT.TOOLTIPBUILDINGINFO_MEP_MAPPREFIX))
                mapName = self.app.utilsManager.textManager.getText(TextType.NEUTRAL_TEXT, arenaType.name)
                currentMapTxt = prefix + mapName
                statusLevel = battleStatus.level
                statusTxt = ms(battleStatus.msg)
                defResStatusTxt = self.app.utilsManager.textManager.concatStyles(((battleStatus.color, '%s %s' % (battleStatus.prefix, BigWorld.wg_getIntegralFormat(resCount))), (TextIcons.NUT_ICON,)))
                descrActionTxt = self.app.utilsManager.textManager.getText(TextType.MAIN_TEXT, ms(FORT.TOOLTIPBUILDINGINFO_DESCRACTION))
                descrActionTxt = descrActionTxt % {'value': defResStatusTxt}
            else:
                minResCount = hpTotalVal * 0.2
                minResStatusTxt = self.app.utilsManager.textManager.concatStyles(((TextType.NEUTRAL_TEXT, BigWorld.wg_getIntegralFormat(minResCount)), (TextIcons.NUT_ICON,)))
                infoMessage = self.app.utilsManager.textManager.getText(TextType.MAIN_TEXT, ms(FORT.TOOLTIPBUILDINGINFO_DESTROYEDMESSAGE))
                infoMessage = infoMessage % {'value': minResStatusTxt}
        result = {'buildingUID': buildingUID,
         'buildingName': buildingName,
         'currentMap': currentMapTxt,
         'buildingLevel': buildingLevelTxt,
         'descrAction': descrActionTxt,
         'statusMsg': statusTxt,
         'statusLevel': statusLevel,
         'indicatorModel': indicatorsModel,
         'isAvailable': isReadyForBattle,
         'infoMessage': infoMessage}
        return result


class ActionTooltipData(ToolTipBaseData):

    def __init__(self, context):
        super(ActionTooltipData, self).__init__(context, TOOLTIP_TYPE.CONTROL)

    def getDisplayableData(self, type, key, newPrice, oldPrice, isBuying, forCredits = False, rentPackage = None):
        actionNames = None
        body = ''
        descr = ''
        newCredits, newGold = newPrice
        oldCredits, oldGold = oldPrice
        newPriceValue = 0
        newPriceCurrency = None
        oldPriceValue = 0
        oldPriceCurrency = None
        hasRentCompensation = False
        rentCompensation = None
        if type == ACTION_TOOLTIPS_TYPE.ECONOMICS:
            actions = g_eventsCache.getEconomicsAction(key)
            newPriceValue = newCredits if forCredits else newGold
            oldPriceValue = oldCredits if forCredits else oldGold
            newPriceCurrency = oldPriceCurrency = 'credits' if forCredits else 'gold'
            if actions:
                actionNames = map(lambda x: x[1], actions)
                if key == 'freeXPToTManXPRate':
                    newPriceCurrency = oldPriceCurrency = 'freeXp'
        if type == ACTION_TOOLTIPS_TYPE.RENT:
            item = g_itemsCache.items.getItemByCD(int(key))
            actions = g_eventsCache.getRentAction(item, rentPackage)
            if actions:
                actionNames = map(itemgetter(1), actions)
                newPriceValue = newCredits if forCredits else newGold
                oldPriceValue = oldCredits if forCredits else oldGold
                newPriceCurrency = oldPriceCurrency = 'credits' if forCredits else 'gold'
        elif type == ACTION_TOOLTIPS_TYPE.ITEM:
            item = g_itemsCache.items.getItemByCD(int(key))
            useGold = item.isPremium and not forCredits and isBuying
            newPriceValue = newGold if useGold else newCredits
            newPriceCurrency = 'gold' if useGold else 'credits'
            oldPriceValue = oldGold if useGold else oldCredits
            oldPriceCurrency = 'gold' if useGold else 'credits'
            actions = g_eventsCache.getItemAction(item, True, forCredits)
            if item.itemTypeID in (GUI_ITEM_TYPE.SHELL, GUI_ITEM_TYPE.OPTIONALDEVICE, GUI_ITEM_TYPE.EQUIPMENT) and item.isPremium and not useGold:
                actions += g_eventsCache.getEconomicsAction('exchangeRateForShellsAndEqs')
            if item.itemTypeID == GUI_ITEM_TYPE.VEHICLE and item.isPremium and not isBuying:
                actions += g_eventsCache.getEconomicsAction('exchangeRate')
            if actions:
                actionNames = map(lambda x: x[1], actions)
            if not isBuying:
                sellingActions = g_eventsCache.getItemAction(item, False, forCredits)
                if sellingActions:
                    actionNames = map(lambda x: x[1], sellingActions)

                    def filter(item):
                        (forGold, _), _ = item
                        return forGold

                    sellForGoldAction = findFirst(filter, sellingActions)
                    if sellForGoldAction:
                        newPriceValue = newGold
                        newPriceCurrency = 'gold'
            if item.itemTypeID == GUI_ITEM_TYPE.VEHICLE and isBuying:
                if item.isRented and not item.rentalIsOver and item.rentCompensation[1] > 0:
                    hasRentCompensation = True
                    rentCompensation = item.rentCompensation[1]
        elif type == ACTION_TOOLTIPS_TYPE.CAMOUFLAGE:
            intCD, type = cPickle.loads(key)
            actions = g_eventsCache.getCamouflageAction(intCD) + g_eventsCache.getEconomicsAction(type)
            if actions:
                actionNames = map(lambda x: x[1], actions)
                newPriceValue = newCredits if forCredits else newGold
                oldPriceValue = oldCredits if forCredits else oldGold
                newPriceCurrency = oldPriceCurrency = 'credits' if forCredits else 'gold'
        elif type == ACTION_TOOLTIPS_TYPE.EMBLEMS:
            group, type = cPickle.loads(key)
            actions = g_eventsCache.getEmblemsAction(group) + g_eventsCache.getEconomicsAction(type)
            if actions:
                actionNames = map(lambda x: x[1], actions)
                newPriceValue = newCredits if forCredits else newGold
                oldPriceValue = oldCredits if forCredits else oldGold
                newPriceCurrency = oldPriceCurrency = 'credits' if forCredits else 'gold'
        elif type == ACTION_TOOLTIPS_TYPE.AMMO:
            item = g_itemsCache.items.getItemByCD(int(key))
            actions = []
            for shell in item.gun.defaultAmmo:
                actions += g_eventsCache.getItemAction(shell, isBuying, True)

            if actions:
                actionNames = map(lambda x: x[1], actions)
                newPriceValue = newCredits
                oldPriceValue = oldCredits
                newPriceCurrency = oldPriceCurrency = 'credits'
        if actionNames:
            actionNames = set(actionNames)
        if newPriceCurrency and oldPriceCurrency and newPriceValue is not None and oldPriceValue:
            formatedNewPrice = makeHtmlString('html_templates:lobby/quests/actions', newPriceCurrency, {'value': BigWorld.wg_getGoldFormat(newPriceValue)})
            formatedOldPrice = makeHtmlString('html_templates:lobby/quests/actions', oldPriceCurrency, {'value': BigWorld.wg_getGoldFormat(oldPriceValue)})
            body = i18n.makeString(TOOLTIPS.ACTIONPRICE_BODY, oldPrice=formatedOldPrice, newPrice=formatedNewPrice)
        if actionNames:

            def mapName(item):
                action = g_eventsCache.getActions().get(item)
                return i18n.makeString(TOOLTIPS.ACTIONPRICE_ACTIONNAME, actionName=action.getUserName())

            actionUserNames = ', '.join(map(mapName, actionNames))
            if len(actionNames) > 1:
                descr = i18n.makeString(TOOLTIPS.ACTIONPRICE_FORACTIONS, actions=actionUserNames)
            else:
                descr = i18n.makeString(TOOLTIPS.ACTIONPRICE_FORACTION, action=actionUserNames)
        if hasRentCompensation:
            formattedRentCompensation = makeHtmlString('html_templates:lobby/quests/actions', 'gold', {'value': BigWorld.wg_getGoldFormat(rentCompensation)})
            descr += '\n' + i18n.makeString(TOOLTIPS.ACTIONPRICE_RENTCOMPENSATION, rentCompensation=formattedRentCompensation)
        return {'header': i18n.makeString(TOOLTIPS.ACTIONPRICE_HEADER),
         'body': body + '\n' + descr if descr else body}


class ToolTipFortWrongTime(ToolTipBaseData):

    def __init__(self, context):
        super(ToolTipFortWrongTime, self).__init__(context, TOOLTIP_TYPE.FORTIFICATIONS)

    def getDisplayableData(self):
        return {'header': i18n.makeString(TOOLTIPS.FORTWRONGTIME_HEADER),
         'body': i18n.makeString(TOOLTIPS.FORTWRONGTIME_BODY, local=BigWorld.wg_getShortTimeFormat(time_utils.getCurrentTimestamp()), server=BigWorld.wg_getShortTimeFormat(time_utils.getCurrentLocalServerTimestamp()))}


class MapSmallTooltipData(ToolTipBaseData):

    def __init__(self, context):
        super(MapSmallTooltipData, self).__init__(context, TOOLTIP_TYPE.FORTIFICATIONS)

    def getDisplayableData(self, data):
        return {'mapName': data.mapName,
         'description': data.description,
         'imageURL': data.imageURL}


class QuestVehiclesBonusTooltipData(ToolTipBaseData):

    def __init__(self, context):
        super(QuestVehiclesBonusTooltipData, self).__init__(context, TOOLTIP_TYPE.QUESTS)

    def getDisplayableData(self, questID):
        quest = self._context.buildItem(questID)
        bonuses = quest.getBonuses('vehicles')
        vehiclesList = []
        oneColumnLen = 20
        maxItemsLen = 60
        maxColumnLen = maxItemsLen / 2
        for b in bonuses:
            if b.isShowInGUI():
                flist = b.formattedList()
                if flist:
                    vehiclesList.extend(flist)

        vehiclesListLen = len(vehiclesList)
        if vehiclesListLen <= oneColumnLen:
            columns = ['<br>'.join(vehiclesList)]
        elif vehiclesListLen <= maxItemsLen:
            col1Len = int(math.ceil(vehiclesListLen / float(2)))
            col2Len = vehiclesListLen - col1Len
            col1Str = '<br>'.join(vehiclesList[:col1Len])
            col2Str = '<br>'.join(vehiclesList[col1Len:vehiclesListLen])
            columns = [col1Str, col2Str]
        else:
            col1Str = '<br>'.join(vehiclesList[:maxColumnLen])
            col2 = vehiclesList[maxColumnLen:maxItemsLen - 1]
            vehiclesLeft = vehiclesListLen - maxItemsLen - 1
            moreVehsStr = makeString(TOOLTIPS.QUESTS_VEHICLESBONUS_VEHICLESLEFT, count=vehiclesLeft)
            col2.append(text_styles.warning(moreVehsStr))
            col2Str = '<br>'.join(col2)
            columns = [col1Str, col2Str]
        return {'name': makeString(TOOLTIPS.QUESTS_VEHICLESBONUS_TITLE),
         'columns': columns}


class FortConsumableOrderTooltipData(ToolTipData):

    def __init__(self, context):
        super(FortConsumableOrderTooltipData, self).__init__(context, TOOLTIP_TYPE.EQUIPMENT)
        self.fields = (ToolTipAttrField(self, 'name', 'userName'), ToolTipMethodField(self, 'type', 'getUserType'), FortOrderParamField(self, 'params'))


class LadderTooltipData(ToolTipBaseData):

    def __init__(self, context):
        super(LadderTooltipData, self).__init__(context, TOOLTIP_TYPE.CYBER_SPORT)

    def getDisplayableData(self, clubDbID):
        from gui.clubs.ClubsController import g_clubsCtrl
        club = g_clubsCtrl.getClub(clubDbID)
        if club is None:
            return
        else:
            ladderInfo = club.getLadderInfo()
            ladderIconSource = getLadderChevron256x256(ladderInfo.getDivision())
            if ladderInfo.isInLadder():
                isActive = True
                league = getLeagueString(ladderInfo.getLeague())
                division = getDivisionString(ladderInfo.division)
            else:
                isActive = False
                league = division = ''
            if not ladderInfo.isTop():
                toNextLevel = getPointsToNextDivision(ladderInfo.getRatingPoints())
            else:
                toNextLevel = None
            return {'isActive': isActive,
             'place': ladderInfo.position,
             'league': league,
             'division': division,
             'points': ladderInfo.getRatingPoints(),
             'icon': ladderIconSource,
             'name': i18n.makeString(TOOLTIPS.LADDER_HEADER),
             'descr': i18n.makeString(TOOLTIPS.LADDER_DESCR),
             'toNextLevel': toNextLevel}


class FortDivisionTooltipData(ToolTipBaseData):

    def __init__(self, context):
        super(FortDivisionTooltipData, self).__init__(context, TOOLTIP_TYPE.FORTIFICATIONS)

    def getDisplayableData(self, divisionID, showWarning):
        if divisionID == FORT_BATTLE_DIVISIONS.ABSOLUTE.divisionID:
            division = FORT_BATTLE_DIVISIONS.ABSOLUTE
            divisionType = 'absolute'
            warning = i18n.makeString('#tooltips:fortDivision/warning/lowBacklog')
        else:
            division = FORT_BATTLE_DIVISIONS.CHAMPION
            divisionType = 'champion'
            warning = i18n.makeString('#tooltips:fortDivision/warning/forbiddenEquipment')
        result = {'name': i18n.makeString('#tooltips:fortDivision/%s/header' % divisionType),
         'descr': i18n.makeString('#tooltips:fortDivision/%s/description' % divisionType),
         'params': [[i18n.makeString('#tooltips:fortDivision/params/vehicleLevel'), int2roman(1) + ' - ' + int2roman(division.maxVehicleLevel)], [i18n.makeString('#tooltips:fortDivision/params/vehiclesCount'), division.maxCombatants]]}
        if showWarning:
            result['warning'] = warning
        return result


class FortSortieTooltipData(ToolTipBaseData):

    def __init__(self, context):
        super(FortSortieTooltipData, self).__init__(context, TOOLTIP_TYPE.FORTIFICATIONS)

    def getDisplayableData(self, data):
        _ms = i18n.makeString
        _gt = self.app.utilsManager.textManager.getText
        division = _gt(TextType.MAIN_TEXT, _ms(data.divisionName))
        inBattleIcon = self.app.utilsManager.getHtmlIconText(ImageUrlProperties(RES_ICONS.MAPS_ICONS_LIBRARY_SWORDSICON, 16, 16, -3, 0))
        descriptionText = _gt(TextType.MAIN_TEXT, _ms(data.descriptionForTT)) if data.descriptionForTT != '' else ''
        return {'titleText': _gt(TextType.HIGH_TITLE, _ms(TOOLTIPS.FORTIFICATION_TOOLTIPFORTSORTIE_TITLE, name=data.creatorName)),
         'divisionText': _gt(TextType.STANDARD_TEXT, _ms(TOOLTIPS.FORTIFICATION_TOOLTIPFORTSORTIE_DIVISION, division=division)),
         'descriptionText': html.escape(descriptionText),
         'hintText': _gt(TextType.STANDARD_TEXT, _ms(TOOLTIPS.FORTIFICATION_TOOLTIPFORTSORTIE_HINT)),
         'inBattleText': _gt(TextType.ERROR_TEXT, _ms(TOOLTIPS.FORTIFICATION_TOOLTIPFORTSORTIE_INBATTLE) + ' ' + inBattleIcon) if data.isInBattle else '',
         'isInBattle': data.isInBattle}
