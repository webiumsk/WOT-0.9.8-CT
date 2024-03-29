# Embedded file name: scripts/client/messenger/proto/FiltersChain.py
from debug_utils import LOG_WARNING, LOG_DEBUG
from messenger.proto.interfaces import IIncomingMessageFilter, IOutgoingMessageFilter

class FiltersChain(object):

    def __init__(self, inFilters, outFilters):
        super(FiltersChain, self).__init__()
        self.__inFilters = inFilters
        self.__outFilters = outFilters
        self.__inFilterNames = {}
        self.__outFilterNames = {}
        self.__prepareInFilters()
        self.__prepareOutFilters()

    def addFilter(self, name, filterObj, order = -1, removed = None):
        inFilter = isinstance(filterObj, IIncomingMessageFilter)
        outFilter = isinstance(filterObj, IOutgoingMessageFilter)
        if removed is None:
            removed = []
        if not inFilter and not outFilter or inFilter and outFilter:
            LOG_WARNING('Invalid filter (name = {0:>s}, object = {1!r:s}))'.format(name, filterObj))
            return
        else:
            if inFilter and not self.__inFilterNames.has_key(name):
                if self.__outFilterNames.has_key(name):
                    LOG_WARNING('Invalid filter (name = {0:>s}, object = {1!r:s})).Filter name must be unique.'.format(name, filterObj))
                    return
                self.__inFilters.append({'name': name,
                 'filter': filterObj,
                 'order': order if order > 0 else len(self.__inFilters) + 1,
                 'lock': False})
                LOG_DEBUG('Incoming filter added', name)
                for removedName in removed:
                    self.__doRemoveInFilter(removedName)

                self.__prepareInFilters()
            elif inFilter:
                LOG_DEBUG('Filter (name = {0:>s}, object = {1!r:s})) is already added to chain of incoming filters'.format(name, filterObj))
            if outFilter and not self.__outFilterNames.has_key(name):
                if self.__inFilterNames.has_key(name):
                    LOG_WARNING('Invalid filter (name = {0:>s}, object = {1!r:s})).Filter name must be unique.'.format(name, filterObj))
                    return
                self.__outFilters.append({'name': name,
                 'filter': filterObj,
                 'order': order if order > 0 else len(self.__outFilters) + 1,
                 'lock': False})
                LOG_DEBUG('Outgoing filter added', name)
                for removedName in removed:
                    self.__doRemoveOutFilter(removedName)

                self.__prepareOutFilters()
            elif outFilter:
                LOG_DEBUG('Filter (name = {0:>s}, object = {1!r:s})) is already added to chain of outgoing filters'.format(name, filterObj))
            return

    def removeFilter(self, name):
        if self.__doRemoveInFilter(name):
            self.__prepareInFilters()
        elif self.__doRemoveOutFilter(name):
            self.__prepareOutFilters()

    def hasFilter(self, name):
        return self.__inFilterNames.has_key(name) or self.__outFilterNames.has_key(name)

    def chainIn(self, action):
        for filterInfo in self.__inFilters:
            action.data = filterInfo['filter'].filter(action)

        return action

    def chainOut(self, message):
        for filterInfo in self.__outFilters:
            message = filterInfo['filter'].filter(message)

        return message

    def __doRemoveInFilter(self, name):
        result = False
        if self.__inFilterNames.has_key(name):
            idx = self.__inFilterNames[name]
            if not self.__inFilters[idx]['lock']:
                self.__inFilters.pop(idx)
                LOG_DEBUG('Incoming filter removed', name)
                result = True
            else:
                LOG_WARNING('Incoming filter (name = {0:>s}) can not remove.It is locked.'.format(name))
        return result

    def __doRemoveOutFilter(self, name):
        result = False
        if self.__outFilterNames.has_key(name):
            idx = self.__outFilterNames[name]
            if not self.__outFilters[idx]['lock']:
                self.__outFilters.pop(idx)
                LOG_DEBUG('Outgoing filter removed', name)
                result = True
            else:
                LOG_WARNING('Outgoing filter (name = {0:>s}) can not remove.It is locked.'.format(name))
        return result

    def __prepareInFilters(self):
        self.__inFilters = sorted(self.__inFilters, cmp=lambda item, other: cmp(item['order'], other['order']))
        self.__inFilterNames = dict(((f['name'], idx) for idx, f in enumerate(self.__inFilters)))

    def __prepareOutFilters(self):
        self.__outFilters = sorted(self.__outFilters, cmp=lambda item, other: cmp(item['order'], other['order']))
        self.__outFilterNames = dict(((f['name'], idx) for idx, f in enumerate(self.__outFilters)))
