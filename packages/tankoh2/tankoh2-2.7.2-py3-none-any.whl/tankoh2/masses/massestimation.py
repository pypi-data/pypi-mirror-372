# SPDX-FileCopyrightText: 2023 German Aerospace Center (DLR)
#
# SPDX-License-Identifier: MIT

"""very rough estimations of liner and insulation mass"""
import os

import numpy as np

from tankoh2 import programDir
from tankoh2.masses.massdata import fairingDens, insulationDens, linerDens
from tankoh2.service.exception import Tankoh2Error
from tankoh2.settings import settings


def getAuxMaterials(linerMaterial=None, insulationMaterial=None, fairingMaterial=None):
    """
    :param linerMaterial: name of the liner material to be used
    :param insulationMaterial: name of the insulation material to be used
    :param fairingMaterial: name of the fairing material to be used
    """

    if linerMaterial not in linerDens:
        raise Tankoh2Error(f"Liner Material {linerMaterial} not found.")
    elif insulationMaterial not in insulationDens:
        raise Tankoh2Error(f"Insulation Material {insulationMaterial} not found.")
    elif fairingMaterial not in fairingDens:
        raise Tankoh2Error(f"Fairing Material {fairingMaterial} not found.")
    else:
        return linerMaterial, insulationMaterial, fairingMaterial


def getLinerMass(liner, linerMatName=None, linerThickness=0.5):
    """
    :param liner: object of type tankoh2.geometry.liner.Liner
    :param linerMatName: name of liner material in linerDens
    :param linerThickness: thickness of the liner [mm]
    """
    if linerThickness < settings.epsilon:
        return 0
    if linerMatName in linerDens:
        rho = linerDens[linerMatName]  # [kg/m**3]
    else:
        rho = next(iter(linerDens.values()))

    return getVesselMass(liner, linerThickness, rho, thicknessOffset=-linerThickness)


def getInsulationMass(liner, insulationMatName=None, insulationThickness=127):  # source Brewer fig 3-6
    """
    :param liner: object of type tankoh2.geometry.liner.Liner
    :param insulationMatName: name of insulation material in linerDens
    :param insulationThickness: thickness of the insulation [mm]
    """
    if insulationThickness < settings.epsilon:
        return 0
    if insulationMatName in linerDens:
        rho = insulationDens[insulationMatName]  # [kg/m**3]
    else:
        rho = next(iter(insulationDens.values()))

    return getVesselMass(liner, insulationThickness, rho)


def getFairingMass(liner, fairingMatName=None, fairingThickness=0.5, insulationCfrpThickness=127):
    """
    :param liner: object of type tankoh2.geometry.liner.Liner
    :param fairingMatName: name of fairing material in linerDens
    :param fairingThickness: thickness of the fairing [mm]
    :param insulationCfrpThickness: thickness of the cfrp or metal structure and insulation [mm]
    """
    if fairingThickness < settings.epsilon:
        return 0
    if fairingMatName in linerDens:
        rho = fairingDens[fairingMatName]  # [kg/m**3]
    else:
        rho = next(iter(fairingDens.values()))

    return getVesselMass(liner, fairingThickness, rho, thicknessOffset=insulationCfrpThickness)


def getVesselMass(liner, wallThickness, rho, stiffenerAreaMass=None, thicknessOffset=None):
    """
    :param liner: object of type tankoh2.geometry.liner.Liner - Inner contour of the vessel to be measured
    :param wallThickness: thickness of the wall [mm]
    :param rho: density [g/dm**3] or [kg/m**3]
    :param stiffenerAreaMass: mass of the stiffener per area [kg/m**2]
    :param thicknessOffset: offset to the liners contour in order to start at the inner contour of the vessel [mm]
    :return: mass of the vessel [kg]
    """
    if thicknessOffset is not None:
        liner = liner.getLinerResizedByThickness(thicknessOffset)
    if wallThickness == 0:
        mass = 0
    else:
        wallVol = liner.getWallVolume(wallThickness) / 1000 / 1000  # [dm*3]
        mass = rho * wallVol / 1000  # [kg]
    if stiffenerAreaMass is not None:
        stiffenerMass = stiffenerAreaMass * liner.area / 100 / 100 / 100
        mass += stiffenerMass
    return mass


def getFittingMass(vessel, fittingType, fittingMaterial, isMandrel1=True, customBossName=None):
    """Returns the mass of a fitting

    Calculates the mass of the end fitting for a pressure vessel.

    :param: vessel: A pychain vessel object.
    :param: fittingType: The type of fitting to calculate.
    :param: isMandrel1: A boolean indicating whether the fitting is for the first or second mandrel.
    :param: customBossName: The name of a custom boss contour to use for type 'custom'.

    :return: the mass of the fitting.
    """
    fittingVolume = getFittingVolume(vessel, fittingType, isMandrel1, customBossName) / 1000 / 1000 / 1000
    fittingMass = fittingVolume * fittingMaterial["rho"]
    return fittingMass


def getFittingVolume(vessel, fittingType, isMandrel1=True, customBossName=None):
    """
    Calculates the volume of the end fitting for a pressure vessel.

    :param: vessel: A pychain vessel object.
    :param: fittingType: The type of fitting to calculate.
    :param: isMandrel1: A boolean indicating whether the fitting is for the first or second mandrel.
    :param: customBossName: The name of a custom boss contour to use for type 'custom'.

    :return: the volume of the fitting.
    """
    liner = vessel.getLiner()
    fitting = liner.getFitting(isMandrel1)
    if isMandrel1:
        mandrel = liner.getMandrel1()
    else:
        mandrel = liner.getMandrel2()

    windingMandrel = list(zip(mandrel.getXArray(), mandrel.getRArray()))
    windingMandrel = windingMandrel[vessel.getFittingStartID(isMandrel1) - 1 :]
    xStartOfFitting = np.interp(
        fitting.rD, [windingMandrel[1][1], windingMandrel[0][1]], [windingMandrel[1][0], windingMandrel[0][0]]
    )
    windingMandrel[0] = (xStartOfFitting, fitting.rD)
    polarOpeningR = windingMandrel[-1][1]
    windingMandrelLength = windingMandrel[-1][0] - windingMandrel[0][0]
    totalVolume = 0.0

    # Calculate volume of the frustum inside the vessel
    totalVolume += getVolumeOfRotationalSolid([(0, fitting.rD), (fitting.dx1, fitting.r1)])

    # Calculate volume of the winding mandrel (approximated by frustums)
    totalVolume += getVolumeOfRotationalSolid(windingMandrel)

    if fittingType == "A":
        # Calculate volume of the cylindrical section (outer)
        cylinderLength = max(fitting.dxB - windingMandrelLength, 0)
        totalLength = fitting.dx1 + windingMandrelLength + cylinderLength
        totalVolume += np.pi * (fitting.r2**2) * cylinderLength
    elif fittingType == "B":
        # Calculate the volume of the transition curve
        transitionCurveLength = np.sqrt(fitting.rP**2 - (fitting.rP - (polarOpeningR - fitting.r2)) ** 2)
        transitionCurveX = np.linspace(0, transitionCurveLength, 25)
        transitionCurveY = fitting.r2 + fitting.rP - np.sqrt(fitting.rP**2 - transitionCurveX**2)
        transitionCurveCoordinates = list(zip(transitionCurveX, transitionCurveY))
        transitionCurveVolume = getVolumeOfRotationalSolid(transitionCurveCoordinates)
        # Calculate the volume of the smaller cylinder
        smallerCylinderLength = max(fitting.dx2 - transitionCurveLength - windingMandrelLength, 0)
        smallerCylinderVolume = np.pi * (fitting.r2**2) * smallerCylinderLength
        # Calculate the volume of the frustum
        frustumLength = (fitting.r3 - fitting.r2) / np.tan(np.radians(90 - fitting.alphaP))
        frustumVolume = getVolumeOfRotationalSolid([(0, fitting.r2), (frustumLength, fitting.r3)])
        # Calculate the volume of the larger cylinder
        largerCylinderLength = max(
            fitting.dxB - frustumLength - smallerCylinderLength - transitionCurveLength - windingMandrelLength, 0
        )
        largerCylinderVolume = np.pi * (fitting.r3**2) * largerCylinderLength
        totalLength = (
            fitting.dx1
            + windingMandrelLength
            + transitionCurveLength
            + smallerCylinderLength
            + frustumLength
            + largerCylinderLength
        )
        totalVolume += transitionCurveVolume + smallerCylinderVolume + frustumVolume + largerCylinderVolume
    elif fittingType == "custom":
        customContourCoordinates = [(0, windingMandrel[-1][1])]
        if customBossName is not None:
            customBossFilename = customBossName if customBossName.endswith(".bcon") else customBossName + ".bcon"
            customBossFilename = os.path.join(programDir, "data", customBossFilename)
            if os.path.isfile(customBossFilename):
                with open(customBossFilename, "r") as f:
                    for line in f:
                        try:
                            x_diff, r_diff = map(float, line.split())
                            customContourCoordinates.append(
                                (customContourCoordinates[-1][0] + x_diff, customContourCoordinates[-1][1] + r_diff)
                            )
                        except ValueError:
                            continue  # Skip invalid lines
            else:
                raise FileNotFoundError(f" The file {customBossFilename} does not exist.")
        else:
            raise Tankoh2Error(
                "No custom boss file was provided for a fitting of type 'custom'. Please provide a custom boss file."
            )
        totalLength = fitting.dx1 + windingMandrelLength + customContourCoordinates[-1][0]
        totalVolume += getVolumeOfRotationalSolid(customContourCoordinates)
    else:
        raise Tankoh2Error(f"Fitting type must be one of 'A', 'B', or 'custom'. Got {fittingType} instead.")

    # Subtract the volume of the inner opening
    openingVolume = np.pi * (fitting.r0**2) * totalLength
    totalVolume -= openingVolume

    return totalVolume


def getVolumeOfRotationalSolid(coordinateList):
    """Calculate the volume of a rotational solid from a list of x, r coordinates."""
    volume = 0.0
    for i in range(len(coordinateList) - 1):
        x1, r1 = coordinateList[i]
        x2, r2 = coordinateList[i + 1]
        dx = x2 - x1
        # Approximate each segment as a frustum
        volume += (1 / 3) * np.pi * dx * (r1**2 + r2**2 + r1 * r2)
    return volume
