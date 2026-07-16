import logging

from aih_constants import GUN_MARKER_TYPE
from gui.Scaleform.daapi.view.battle.shared.crosshair import CrosshairPanelContainer, gm_factory
from debug_utils import LOG_WARNING
from gui.Scaleform.daapi.view.meta.CrosshairPanelContainerMeta import CrosshairPanelContainerMeta

from dispersionreticle.flash.dispersion_reticle_flash import DispersionReticleFlash
from dispersionreticle.utils import *
from dispersionreticle.utils.reticle_registry import ReticleRegistry
from dispersionreticle.utils.reticle_types import ReticleTypes


logger = logging.getLogger(__name__)


###########################################################
# This is needed to add possibility of invalidating entire gun marker set
# to maintain exact order of gun markers displayed in CrosshairPanelContainer.
#
# Normally, CrosshairPanelContainer would only clear those gun markers
# that are not present in new GunMarkersComponents, in effect, we wouldn't have
# control over order of gun marker rendering.
#
# This method is modification of standard invalidateGunMarkers
# which will instead clear all current gun markers and recreate all of them in our order by getViewSettings().
###########################################################

@addMethodTo(CrosshairPanelContainer)
def fullyInvalidateGunMarkers(self, markersInfo, vehicleInfo):
    if self._CrosshairPanelContainer__gunMarkers is None:
        LOG_WARNING('Set of gun markers is not created')
        return
    else:
        logger.info("Performing full gun marker invalidation")
        self._CrosshairPanelContainer__clearGunMarkers()

        newSet = gm_factory.createComponents(markersInfo, vehicleInfo)
        self._CrosshairPanelContainer__setGunMarkers(newSet)


###########################################################
# Responsible for changing penetration indicator (that mark on the
# middle of the reticle) to proper color (red, orange, green) on new markerType.
#
# Without this override, new gun markers would
# always be red and because most of the time they are displayed in front of vanilla reticles, color of
# vanilla reticle penetration indicator wouldn't be visible.
###########################################################

@overrideIn(CrosshairPanelContainer)
def setGunMarkerColor(func, self, markerType, color):
    if self._CrosshairPanelContainer__gunMarkers is None:
        return False
    else:
        component = self._CrosshairPanelContainer__gunMarkers.getComponentByType(markerType, isActive=True)
        if component is not None:
            self.as_setGunMarkerColorS(component.getName(), color)

        isServerMarkerStateUpdate = markerType == GUN_MARKER_TYPE.SERVER

        for reticle in ReticleRegistry.ADDITIONAL_RETICLES:
            if reticle.isServerReticle() == isServerMarkerStateUpdate:
                component = self._CrosshairPanelContainer__gunMarkers.getComponentByType(reticle.gunMarkerType, isActive=True)
                if component is not None:
                    self.as_setGunMarkerColorS(component.getName(), color)

        return True


###########################################################
# This is needed to redirect marker instantiation to our swf app instead
# of CrosshairPanelContainer when spawning extended markers.
#
# For more explanation, check gun_marker_components_hooks.py
###########################################################

@overrideIn(CrosshairPanelContainerMeta)
def as_createGunMarkerS(func, self, viewID, linkage, name):
    reticleType = ReticleTypes.getByExtendedFlashMarkerName(name)
    if reticleType:
        DispersionReticleFlash.onMarkerCreate(name, reticleType)
        return True

    return func(self, viewID, linkage, name)


@overrideIn(CrosshairPanelContainerMeta)
def as_destroyGunMarkerS(func, self, name):
    reticleType = ReticleTypes.getByExtendedFlashMarkerName(name)
    if reticleType:
        DispersionReticleFlash.onMarkerDestroy(name, reticleType)
        return True

    return func(self, name)
