# Embedded file name: scripts/client/OcclusionDecal.py
import BigWorld

class OcclusionDecal:

    @staticmethod
    def isEnabled():
        return BigWorld.isForwardPipeline() is False and BigWorld.isSSAOEnabled()

    def __init__(self):
        self.__attached = False
        self.__vehicle = None
        self.__desc = None
        self.__chassisDecals = []
        self.__chassisParent = None
        self.__hullDecals = []
        self.__hullParent = None
        self.__turretDecals = []
        self.__turretParent = None
        from account_helpers.settings_core.SettingsCore import g_settingsCore
        g_settingsCore.onSettingsChanged += self.onSettingsChanged
        return

    def destroy(self):
        from account_helpers.settings_core.SettingsCore import g_settingsCore
        g_settingsCore.onSettingsChanged -= self.onSettingsChanged
        self.__vehicle = None
        self.__desc = None
        self.detach()
        return

    def attach(self, vehicle, desc):
        self.__vehicle = vehicle
        self.__desc = desc
        if not OcclusionDecal.isEnabled() or self.__attached:
            return
        self.__attached = True
        self.__chassisParent = desc['chassis']['model']
        for transform in vehicle.typeDescriptor.chassis['AODecals']:
            decal = OcclusionDecal.__createDecal(transform, self.__chassisParent, False)
            self.__chassisDecals.append(decal)

        self.__hullParent = desc['hull']['model']
        for transform in vehicle.typeDescriptor.hull['AODecals']:
            decal = OcclusionDecal.__createDecal(transform, self.__hullParent, True)
            self.__hullDecals.append(decal)

        self.__turretParent = desc['turret']['model']
        for transform in vehicle.typeDescriptor.turret['AODecals']:
            decal = OcclusionDecal.__createDecal(transform, self.__turretParent, True)
            self.__turretDecals.append(decal)

    def detach(self):
        if not self.__attached:
            return
        else:
            self.__attached = False
            for decal in self.__chassisDecals:
                self.__chassisParent.root.detach(decal)

            self.__chassisDecals = []
            self.__chassisParent = None
            for decal in self.__hullDecals:
                self.__hullParent.root.detach(decal)

            self.__hullDecals = []
            self.__hullParent = None
            for decal in self.__turretDecals:
                self.__turretParent.root.detach(decal)

            self.__turretDecals = []
            self.__turretParent = None
            return

    def __reattach(self):
        if self.__attached:
            return
        elif self.__vehicle is None or self.__desc is None:
            return
        else:
            self.attach(self.__vehicle, self.__desc)
            return

    def onSettingsChanged(self, diff = None):
        if OcclusionDecal.isEnabled():
            self.__reattach()
        else:
            self.detach()

    @staticmethod
    def __createDecal(transform, parent, applyToAll):
        diffuseTexture = 'maps/spots/TankOcclusion/TankOcclusionMap.dds'
        bumpTexture = ''
        hmTexture = ''
        priority = 0
        materialType = 4
        visibilityMask = 4294967295L
        accuracy = 2
        influence = 30
        if applyToAll:
            influence = 62
        decal = BigWorld.WGOcclusionDecal()
        decal.setup(diffuseTexture, bumpTexture, hmTexture, priority, materialType, influence, visibilityMask, accuracy)
        decal.setLocalTransform(transform)
        parent.root.attach(decal)
        return decal
