# Embedded file name: scripts/client/FlagSpawnPoint.py
import BigWorld

class FlagSpawnPoint(BigWorld.UserDataObject):

    def __init__(self):
        BigWorld.UserDataObject.__init__(self)
        print 'FlagSpawnPoint ', self.position
