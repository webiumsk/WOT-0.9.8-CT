# Embedded file name: scripts/client/RepairPoint.py
import BigWorld
from Math import Vector2

class RepairPoint(BigWorld.UserDataObject):
    _COLOR_YELLOW = 4294945280L
    _DEFAULT_RADIUS_MODEL = 'content/Interface/CheckPoint/CheckPoint.visual'
    _OVER_TERRAIN_HEIGHT = 0.5

    def __init__(self):
        BigWorld.UserDataObject.__init__(self)
        print 'RepairPoint ', self.position, self.radius
        self.__terrainSelectedArea = None
        self.__fakeModel = None
        self.__createTerrainSelectedArea(self.position, self.radius * 2.0)
        return

    def __del__(self):
        if self.__fakeModel is not None:
            BigWorld.delModel(self.__fakeModel)
            self.__fakeModel = None
        self.__terrainSelectedArea = None
        return

    def __createTerrainSelectedArea(self, position, size):
        self.__fakeModel = BigWorld.Model('objects/fake_model.model')
        self.__fakeModel.position = position
        BigWorld.addModel(self.__fakeModel)
        rootNode = self.__fakeModel.node('')
        self.__terrainSelectedArea = BigWorld.PyTerrainSelectedArea()
        self.__terrainSelectedArea.setup(self._DEFAULT_RADIUS_MODEL, Vector2(size, size), self._OVER_TERRAIN_HEIGHT, self._COLOR_YELLOW)
        rootNode.attach(self.__terrainSelectedArea)
