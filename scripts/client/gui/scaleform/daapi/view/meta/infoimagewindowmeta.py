# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/InfoImageWindowMeta.py
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class InfoImageWindowMeta(DAAPIModule):

    def as_setDataS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setData(data)
