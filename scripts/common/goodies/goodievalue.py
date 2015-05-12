# Embedded file name: scripts/common/goodies/GoodieValue.py
from math import floor

class GoodieValue(object):
    __slots__ = ['value', 'isAbsolute']

    def __init__(self, value, isAbsolute = True):
        self.isAbsolute = isAbsolute
        if isAbsolute:
            self.value = value
        else:
            if value < 0:
                raise Exception, 'Bad goodie value <%s>' % value
            self.value = float(value) / 100

    @staticmethod
    def percent(value):
        return GoodieValue(value, False)

    @staticmethod
    def absolute(value):
        return GoodieValue(value, True)

    def increase(self, x):
        if self.isAbsolute:
            return int(floor(x + self.value))
        else:
            return int(floor(x + float(x) * self.value))

    def reduce(self, x):
        if self.isAbsolute:
            result = int(floor(x - self.value))
            if result < 0:
                raise Exception, 'Goodie is negative %d > %d' % (self.value, x)
            return result
        else:
            return int(floor(x - float(x) * self.value))
