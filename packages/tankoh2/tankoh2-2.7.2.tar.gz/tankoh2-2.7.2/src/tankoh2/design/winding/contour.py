# SPDX-FileCopyrightText: 2023 German Aerospace Center (DLR)
#
# SPDX-License-Identifier: MIT

"""methods for liners and domes"""

import os

import numpy as np

from tankoh2 import log, programDir, pychain
from tankoh2.design.winding.windingutils import copyAsJson, updateName
from tankoh2.geometry.dome import validDomeTypes
from tankoh2.geometry.geoutils import contourLength
from tankoh2.service.exception import Tankoh2Error
from tankoh2.settings import settings


def domeContourLength(dome):
    """Returns the contour length of a dome"""
    return contourLength(dome.getXCoords(), dome.getRCoords())


def getDome(cylinderRadius, polarOpening, domeType=None, x=None, r=None):
    """creates a µWind dome

    :param cylinderRadius: radius of the cylinder
    :param polarOpening: polar opening radius
    :param domeType: pychain.winding.DOME_TYPES.ISOTENSOID or pychain.winding.DOME_TYPES.CIRCLE
    :param x: x-coordinates of a custom dome contour
    :param r: radius-coordinates of a custom dome contour. r[0] starts at cylinderRadius
    """
    if domeType is None:
        domeType = pychain.winding.DOME_TYPES.ISOTENSOID
    elif isinstance(domeType, str):
        # domeType = domeType.lower()
        if domeType == "isotensoid_MuWind":
            domeType = pychain.winding.DOME_TYPES.ISOTENSOID
        elif domeType == "circle":
            domeType = pychain.winding.DOME_TYPES.CIRCLE
        elif domeType in validDomeTypes:
            if x is None or r is None:
                raise Tankoh2Error(f'For dome type "{domeType}", the contour coordinates x, r must be given.')
            domeType = pychain.winding.DOME_TYPES.CIRCLE
        else:
            raise Tankoh2Error(f'wrong dome type "{domeType}". Valid dome types: {validDomeTypes}')
    # build  dome
    dome = pychain.winding.Dome()
    try:
        dome.buildDome(cylinderRadius, polarOpening, domeType)
    except IndexError as e:
        log.error(
            f"Got an error creating the dome with these parameters: " f"{(cylinderRadius, polarOpening, domeType)}"
        )
        raise

    if x is not None and r is not None and domeType not in ["isotensoid_MuWind", "circle"]:
        if not np.allclose(r[0], cylinderRadius):
            raise Tankoh2Error(f"cylinderRadius {cylinderRadius} and r-vector {r[0]} do not fit")
        if not np.allclose(r[-1], polarOpening):
            raise Tankoh2Error(f"polarOpening {polarOpening} and smallest given radius {r[-1]} do not fit")
        if len(r) != len(x):
            raise Tankoh2Error(f"x and r-vector do not have the same size. len(r): len(x): {len(r), len(x)}")
        dome.setPoints(x, r)
    return dome


def getLiner(dome, length, dome2=None, nodeNumber=500):
    """Creates a liner

    :param dome: dome instance
    :param length: cylindrical length of liner
    :param dome2: dome of type pychain.winding.Dome
    :param nodeNumber: number of nodes of full contour. Might not exactly be matched due to approximations
    :return: liner of type pychain.winding.Liner
    """

    # create a symmetric liner with dome information and cylinder length
    liner = pychain.winding.Liner()

    # spline for winding calculation is based on nodeNumber
    if dome2:
        contourLength = length + domeContourLength(dome) + domeContourLength(dome2)
    else:
        contourLength = length / 2 + domeContourLength(dome)  # use half model (one dome, half cylinder)
        nodeNumber //= 2
    deltaLengthSpline = contourLength / nodeNumber  # just use half side

    if dome2 is not None:
        log.info("Create unsymmetric vessel")
        liner.buildFromDomes(dome, dome2, length, deltaLengthSpline)
    else:
        log.info("Create symmetric vessel")
        liner.buildFromDome(dome, length, deltaLengthSpline)

    # Create a default fitting
    polarOpeningRadius = dome.polarOpening
    scaleFittingRadii = 0.5
    for fitting in [liner.getFitting(True), liner.getFitting(False)]:
        fitting.setFittingTypeA()
        fitting.r0 = polarOpeningRadius / 2 * scaleFittingRadii
        fitting.r1 = polarOpeningRadius * scaleFittingRadii
        fitting.r3 = polarOpeningRadius
        fitting.rP = polarOpeningRadius / 4
        fitting.alphaP = 45
        fitting.rD = polarOpeningRadius + polarOpeningRadius * scaleFittingRadii * 2
        fitting.dx1 = polarOpeningRadius / 2
        fitting.dx2 = polarOpeningRadius
        fitting.dxB = polarOpeningRadius * 2
        fitting.lV = polarOpeningRadius * 2
        fitting.rebuildFitting()
    return liner


def saveLiner(liner, linerFilename, linerName):
    """Saves liner as a file

    :param liner: liner instance
    :param linerFilename: if given, the liner is saved to this file for visualization in µChainWind
    :param linerName: name of the liner written to the file
    """

    if linerFilename and linerName:
        liner.saveToFile(linerFilename)
        updateName(linerFilename, linerName, ["liner"])
        copyAsJson(linerFilename, "liner")
        liner.loadFromFile(linerFilename)


def buildFitting(
    liner,
    fittingType="A",
    r0=None,
    r1=None,
    r3=None,
    rD=None,
    dx1=None,
    dxB=None,
    dx2=None,
    lV=None,
    alphaP=None,
    rP=None,
    customBossName=None,
):
    """builds a fitting for the liner

    :param liner: liner instance
    :param fittingType: type of Fitting (A, B, or custom)
    :param r0:
    :param r1:
    :param r3:
    :param rD:
    :param dx1:
    :param dxB:
    :param dx2:
    :param lV:
    :param alphaP:
    :param rP:
    :param customBossName: Name of data file specifying custom boss contour as  [x y] differences
        starting from the polar opening

    """

    for fitting in [liner.getFitting(True), liner.getFitting(False)]:
        # Set Fitting Type
        if fittingType == "A":
            fitting.setFittingTypeA()
        elif fittingType == "B":
            fitting.setFittingTypeB()
        elif fittingType == "custom":
            fitting.setFittingTypeCustom()
            if customBossName is not None:
                customBossFilename = customBossName if customBossName.endswith(".bcon") else customBossName + ".bcon"
                customBossFilename = os.path.join(programDir, "data", customBossFilename)
                if os.path.isfile(customBossFilename):
                    fitting.loadCustomBossPointsFromFile(customBossFilename)
                else:
                    raise FileNotFoundError(f" The file {customBossFilename} does not exist.")
            else:
                raise Tankoh2Error("Fitting type set to custom, but no custom boss file was specified.")
        else:
            raise Tankoh2Error(f"The parameter should be one of [A, B, custom] but got [{fittingType}] instead.")

        # Overwrite Standard Values if not None
        if r0 is not None:
            fitting.r0 = r0
        if r1 is not None:
            fitting.r1 = r1
        if r3 is not None:
            fitting.r3 = r3
        if rD is not None:
            fitting.rD = rD
        if dx1 is not None:
            fitting.dx1 = dx1
        if dxB is not None:
            fitting.dxB = dxB
        if dx2 is not None:
            fitting.dx2 = dx2
        if lV is not None:
            fitting.lV = lV
        if alphaP is not None:
            fitting.alphaP = alphaP
        if rP is not None:
            fitting.rP = rP
        fitting.rebuildFitting()
    return liner.getFitting(True), liner.getFitting(False)


def getReducedCylinderLength(
    originalCylinderLength, symmetricContour, puckArray, x, middleNode, maxHoopShift1, maxHoopShift2
):
    """finds the minimum cylindrical length at which the domes no longer influence the stresses

    :param originalCylinderLength: original cylinder length
    :param symmetricContour: Flag if the contour is symmetric
    :param puckArray: array of puck values across the vessel
    :param x: array of x values across the vessel
    :param middleNode: node which lies between mandrel1 and mandrel2 (for nonsymmetric contours)
    :param maxHoopShift: maximum allowedHoopShift
    :return: reducedCylinderLength: length of the reduced cylinder part of liner
    """
    reducedCylinderLength = originalCylinderLength
    if symmetricContour:
        for idx, puckElement in enumerate(puckArray):
            if abs(puckElement - puckArray[0]) / puckArray[0] > 1e-4:
                reducedCylinderLength = max(
                    originalCylinderLength - 2 * x[idx] + 50, settings.minCylindricalLength, 4 * maxHoopShift1 + 50
                )
                break
    else:
        for idx, puckElement in enumerate(puckArray[middleNode::-1]):
            if abs(puckElement - puckArray[middleNode]) / puckArray[middleNode] > 1e-4:
                reducedCylinderCutoffMandrel1 = x[middleNode - idx]
                break
        else:
            reducedCylinderCutoffMandrel1 = x[middleNode]
        for idx, puckElement in enumerate(puckArray[middleNode::1]):
            if abs(puckElement - puckArray[middleNode]) / puckArray[middleNode] > 1e-4:
                reducedCylinderCutoffMandrel2 = x[middleNode + idx]
                break
        else:
            reducedCylinderCutoffMandrel2 = x[middleNode]
        reducedCylinderLength = max(
            originalCylinderLength - (reducedCylinderCutoffMandrel2 - reducedCylinderCutoffMandrel1) + 50,
            settings.minCylindricalLength,
            2 * maxHoopShift1 + 2 * maxHoopShift2 + 50,
        )
    return reducedCylinderLength


def setReducedCylinder(vessel, composite, reducedCylinderLength, symmetricContour, bandWidth, nodesPerBand):
    """replaces the liner of an existing vessel with a shorter cylinder length to speed up calculations

    :param vessel: original vessel
    :param composite: composite to rebuild original vessel
    :param reducedCylinderLength: length of reduced cylinder part of liner
    :param symmetricContour: Flag if the contour is symmetric
    :param bandWidth: bandwidth for finding the node spacing
    :param nodesPerBand: nodes per Band setting for finding the node spacing

    :return: reducedCylinderLength: length of the reduced cylinder
    """
    reducedLiner = pychain.winding.Liner()
    if symmetricContour:
        dome = vessel.getLiner().getDome1()
        reducedLiner.buildFromDome(dome, reducedCylinderLength, bandWidth / nodesPerBand)
    else:
        dome = vessel.getLiner().getDome1()
        dome2 = vessel.getLiner().getDome2()
        reducedLiner.buildFromDomes(dome, dome2, reducedCylinderLength, bandWidth / nodesPerBand)
    vessel.setLiner(reducedLiner)
    vessel.setComposite(composite)
    vessel.finishWinding()


def calculateWindability(vessel, layer, allowedThicknessDerivative, contourSmoothingBorders, isMandrel1=True):
    """replaces the liner of an existing vessel with a shorter cylinder length to speed up calculations

    :param vessel: original vessel
    :param layer: layer number of surface contour
    :param allowedThicknessDerivative: allowed maximum derivative of thickness
    :param contourSmoothingBorders: index at which to start the windability analysis
    :param isMandrel1: use mandrel 1 for

    :return: contour windability (1-3+ if not windable, 0 if windable)
    """
    if isMandrel1:
        xDome = vessel.getVesselLayer(layer).getOuterMandrel1().getXArray()[contourSmoothingBorders[0] :]
        rDome = vessel.getVesselLayer(layer).getOuterMandrel1().getRArray()[contourSmoothingBorders[0] :]
        xLiner = vessel.getLiner().getMandrel1().getXArray()[contourSmoothingBorders[0] :]
        rLiner = vessel.getLiner().getMandrel1().getRArray()[contourSmoothingBorders[0] :]
        lLiner = vessel.getLiner().getMandrel1().getLArray()[contourSmoothingBorders[0] :]
    else:
        xDome = vessel.getVesselLayer(layer).getOuterMandrel2().getXArray()[contourSmoothingBorders[1] :]
        rDome = vessel.getVesselLayer(layer).getOuterMandrel2().getRArray()[contourSmoothingBorders[1] :]
        xLiner = vessel.getLiner().getMandrel2().getXArray()[contourSmoothingBorders[1] :]
        rLiner = vessel.getLiner().getMandrel2().getRArray()[contourSmoothingBorders[1] :]
        lLiner = vessel.getLiner().getMandrel2().getLArray()[contourSmoothingBorders[1] :]
    lLiner = lLiner - lLiner[0]
    rRel = np.sqrt((xDome - xLiner) ** 2 + (rDome - rLiner) ** 2)
    thicknessDerivative = np.gradient(rRel, lLiner)
    for idx, value in enumerate(thicknessDerivative[::-1]):
        if abs(value) > 1e-6:
            endOfThicknessBuildup = thicknessDerivative.size - idx
            break
    else:
        endOfThicknessBuildup = 1

    locationOfMaxThicknessDerivative = np.argmax(thicknessDerivative)
    contourDerivative = np.gradient(xDome, lLiner)
    maxContourDerivative = contourDerivative[locationOfMaxThicknessDerivative]
    minThicknessDerivative = np.min(thicknessDerivative[:endOfThicknessBuildup])
    minContourDerivativeRight = min(contourDerivative[: locationOfMaxThicknessDerivative + 1])
    minContourDerivative = min(contourDerivative)
    endContourDerivative = min(contourDerivative[endOfThicknessBuildup:])

    if minContourDerivative < endContourDerivative:
        windabilityTargetFunction = 3 - (minContourDerivative - endContourDerivative)  # not windable - negative slope
    elif minThicknessDerivative < -1e-3 and settings.enforceRisingContourThickness:
        windabilityTargetFunction = 2 - minThicknessDerivative  # not windable - decreasing thickness
    elif maxContourDerivative - minContourDerivativeRight > allowedThicknessDerivative:
        windabilityTargetFunction = 1 + maxContourDerivative - minContourDerivativeRight  # not windable - too steep
    else:
        windabilityTargetFunction = 0  # windable
    return windabilityTargetFunction
