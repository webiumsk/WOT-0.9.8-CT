# Embedded file name: scripts/client/CombatSelectedArea.py
import BigWorld
import Math
from AvatarInputHandler import mathUtils
from debug_utils import LOG_CURRENT_EXCEPTION, LOG_DEBUG
from gui.WindowsManager import g_windowsManager
from constants import SERVER_TICK_LENGTH
OVER_TERRAIN_HEIGHT = 0.5
MARKER_HEIGHT = 5.0
DEFAULT_RADIUS_MODEL = 'content/Interface/CheckPoint/CheckPoint.visual'
DEFAULT_ROTATE_MODEL = 'content/Interface/TargetPoint/rectangle2_1.visual'
COLOR_WHITE = 4294967295L

class CombatSelectedArea(object):
    position = property(lambda self: self.__fakeModel.position)

    def __init__(self):
        self.__terrainSelectedArea = None
        self.__terrainRotatedArea = None
        self.__fakeModel = None
        self.__rotateModelNode = None
        self.__color = None
        self.__size = None
        return

    def setup(self, position, direction, size, visualPath, color, marker):
        self.__fakeModel = model = BigWorld.Model('')
        model.position = position
        model.yaw = direction.yaw
        BigWorld.addModel(model)
        rootNode = model.node('')
        self.__terrainSelectedArea = area = BigWorld.PyTerrainSelectedArea()
        area.setup(visualPath, size, OVER_TERRAIN_HEIGHT, color)
        rootNode.attach(area)
        self.__size = size
        self.__color = color
        self.__nextPosition = position
        self.__speed = Math.Vector3(0.0, 0.0, 0.0)
        self.__time = 0.0

    def setSelectingDirection(self, value = False):
        if value and self.__terrainRotatedArea is None:
            objectSize = Math.Vector2(10.0, 10.0)
            self.__rotateModelNode = self.__fakeModel.node('', mathUtils.createRTMatrix(Math.Vector3(-self.__fakeModel.yaw, 0.0, 0.0), Math.Vector3((-self.__size.x - objectSize.x) * 0.5, 0.0, (self.__size.y + objectSize.y) * 0.5)))
            self.__terrainRotatedArea = area = BigWorld.PyTerrainSelectedArea()
            area.setup(DEFAULT_ROTATE_MODEL, objectSize, OVER_TERRAIN_HEIGHT, self.__color)
            self.__rotateModelNode.attach(area)
        elif not value and self.__terrainRotatedArea is not None:
            self.__rotateModelNode.detach(self.__terrainRotatedArea)
            self.__terrainRotatedArea = None
        return

    def relocate(self, position, direction):
        self.__fakeModel.position = position
        self.__fakeModel.yaw = direction.yaw
        self.__terrainSelectedArea.updateHeights()
        if self.__terrainRotatedArea:
            self.__terrainRotatedArea.updateHeights()

    def setGUIVisible(self, isVisible):
        self.__fakeModel.visible = isVisible

    def setNextPosition(self, nextPosition, direction):
        self.relocate(self.__nextPosition, direction)
        self.__speed = (nextPosition - self.__nextPosition) / SERVER_TICK_LENGTH
        self.__nextPosition = nextPosition
        self.__time = 0.0

    def update(self, deltaTime):
        if self.__time <= SERVER_TICK_LENGTH:
            self.__fakeModel.position = self.__fakeModel.position + self.__speed * deltaTime
            self.__time += deltaTime
        else:
            self.__fakeModel.position = self.__nextPosition

    def setupDefault(self, position, direction, size, marker):
        self.setup(position, direction, size, DEFAULT_RADIUS_MODEL, COLOR_WHITE, marker)

    def destroy(self):
        BigWorld.delModel(self.__fakeModel)
        self.__terrainSelectedArea = None
        self.__terrainRotatedArea = None
        self.__fakeModel = None
        self.__rotateModelNode = None
        return
