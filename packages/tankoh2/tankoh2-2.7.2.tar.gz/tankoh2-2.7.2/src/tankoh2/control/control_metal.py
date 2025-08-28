# SPDX-FileCopyrightText: 2023 German Aerospace Center (DLR)
#
# SPDX-License-Identifier: MIT

"""control a tank optimization"""

from datetime import datetime

import numpy as np

from tankoh2 import log
from tankoh2.control.genericcontrol import _parameterNotSet, getBurstPressure, parseDesignArgs, saveParametersAndResults
from tankoh2.design.designutils import getMassByVolume
from tankoh2.design.metal.material import getMaterial, getMaterialDefinitionMetal
from tankoh2.design.metal.mechanics import getMaxWallThickness
from tankoh2.geometry.dome import DomeGeneric, getDome
from tankoh2.geometry.liner import Liner
from tankoh2.masses.massestimation import getFairingMass, getInsulationMass, getVesselMass
from tankoh2.mechanics.pbucklcritcyl_SP8007 import checkStabilityMetal, getCrossSection, getPitch, getRingParameterDict
from tankoh2.settings import settings


def createDesign(**kwargs):
    """Create a winding design

    For a list of possible parameters, please refer to tankoh2.design.existingdesigns.allDesignKeywords
    """
    startTime = datetime.now()
    # #########################################################################################
    # SET Parameters of vessel
    # #########################################################################################

    designArgs, nonDefaultArgs, domeObjects = parseDesignArgs(kwargs, "metal")

    # General
    tankname = designArgs["tankname"]
    nodeNumber = designArgs["nodeNumber"]  # number of nodes of full model.
    runDir = designArgs["runDir"]

    # Geometry
    domeType = designArgs["domeType"].lower()
    domeX, domeR = domeObjects["domeContour"]
    polarOpeningRadius = designArgs["polarOpeningRadius"]  # mm
    dcyl = designArgs["dcyl"]  # mm
    if "lcyl" not in designArgs:
        designArgs["lcyl"] = designArgs["lcylByR"] * dcyl / 2
    lcylinder = designArgs["lcyl"]  # mm
    if domeX is not None and domeR is not None:
        dome = DomeGeneric(domeX, domeR)
    else:
        dome = getDome(dcyl / 2, polarOpeningRadius, domeType, designArgs.get("domeLengthByR", 0.0) * dcyl / 2)
    dome2 = (
        None
        if designArgs["dome2Type"] is None
        else getDome(polarOpeningRadius, dcyl / 2, designArgs["dome2Type"].lower(), dome.domeLength)
    )
    length = lcylinder + dome.domeLength + (dome.domeLength if dome2 is None else dome2.domeLength)

    # Pressure Args
    burstPressure = getBurstPressure(designArgs, length)
    designPressure = designArgs["pressure"]

    materialName = designArgs["materialName"]
    material = getMaterial(materialName)

    # Fatigue params
    operationalCycles = designArgs["operationalCycles"]
    zeroPressureCycles = designArgs["zeroPressureCycles"]
    simulatedTankLives = designArgs["simulatedTankLives"]
    minPressure = designArgs["minPressure"]
    Kt = designArgs["Kt"]

    # #########################################################################################
    # Create Liner
    # #########################################################################################
    liner = Liner(dome, lcylinder, dome2)

    # #############################################################################
    # run calculate wall thickness
    # #############################################################################
    volume, area, linerLength = liner.volume / 1000 / 1000, liner.area / 100 / 100 / 100, liner.length
    wallThickness, fatigueFactor = getMaxWallThickness(
        designPressure,
        burstPressure,
        material,
        dcyl,
        operationalCycles=operationalCycles,
        zeroPressureCycles=zeroPressureCycles,
        simulatedTankLives=simulatedTankLives,
        minPressure=minPressure,
        Kt=Kt,
    )

    massMetal = getVesselMass(liner, wallThickness, material["rho"], None)

    bucklingFactorMass, bucklingFactorSkinThickness, numberOfRings, ringMass, buckResultDict = 1, 1, 0, 0, {}
    if designArgs["useBucklingCriterion"]:
        materialPatme = getMaterialDefinitionMetal(material)
        ringParameterDict = getRingParameterDict(designArgs)
        buckResultDict = checkStabilityMetal(
            burstPressure,
            liner,
            wallThickness,
            materialPatme,
            ringParameterDict,
            True,
            False,
        )

        pitch = getPitch(liner.lcyl, buckResultDict["numberOfRings"])
        cross_section = getCrossSection(
            ringParameterDict["ringCrossSectionType"],
            buckResultDict["ringWebHalfLayerThickness"],
            [0],
            ringParameterDict["ringHeight"],
            ringParameterDict["ringFootWidth"],
        )
        stiffenerAreaMass = cross_section.getAreaMass(materialPatme, pitch)

        bucklingFactorSkinThickness = buckResultDict["wallThickness"] / wallThickness
        wallThickness = buckResultDict["wallThickness"]
        massWithBuckling = getVesselMass(liner, wallThickness, materialPatme.rho, stiffenerAreaMass)
        ringMass = getVesselMass(liner, 0, materialPatme.rho, stiffenerAreaMass)
        bucklingFactorMass = massWithBuckling / massMetal
        massMetal = massWithBuckling

    duration = datetime.now() - startTime

    # compressed gas vessel or LH2 vessels without insulation material
    auxMasses = [0.0, 0.0]
    if (
        designArgs["temperature"] is not None
        and designArgs["temperature"] < 33.145
        and designArgs["insulationThickness"] > settings.epsilon
    ):
        # LH2 vessels with insulation material
        auxMasses = [
            getInsulationMass(liner, insulationThickness=designArgs["insulationThickness"]),
            getFairingMass(liner),
        ]
    totalMass = np.sum([massMetal] + auxMasses)
    if not _parameterNotSet(designArgs, "h2Mass"):
        h2Mass = designArgs["h2Mass"]
        gravimetricIndex = h2Mass / (totalMass + h2Mass)
    else:
        h2Mass = getMassByVolume(
            volume / 1e3, designArgs["pressure"], designArgs["maxFill"], temperature=designArgs["temperature"]
        )
        gravimetricIndex = h2Mass / (totalMass + h2Mass)

    results = {
        "metalMass": massMetal,
        "insulationMass": auxMasses[0],
        "fairingMass": auxMasses[1],
        "totalMass": totalMass,
        "volume": volume,
        "h2Mass": h2Mass,
        "area": area,
        "lengthAxial": linerLength,
        "wallThickness": wallThickness,
        "fatigueFactor": fatigueFactor,
        "gravimetricIndex": gravimetricIndex,
        "duration": duration,
    }
    if designArgs["useBucklingCriterion"]:
        results.update(
            {
                "bucklingFactorMass": bucklingFactorMass,
                "bucklingFactorSkinThickness": bucklingFactorSkinThickness,
                "numberOfRings": buckResultDict["numberOfRings"],
                "ringWebThickness": buckResultDict["ringWebHalfLayerThickness"] * 2,
                "ringMass": ringMass,
            }
        )

    saveParametersAndResults(runDir, nonDefaultArgs, designArgs, results)

    log.info("FINISHED")

    return results


if __name__ == "__main__":
    if 1:
        params = {}
        params = {"configFile": "hytazer_smr_iff_2.0bar_final.yaml"}
        params["materialName"] = "alu2219"
        createDesign(**params)
    elif 1:
        params = defaultDesign.copy()
        params["domeType"] = "ellipse"
        params["domeLengthByR"] = 0.5
        params["materialName"] = "alu2219"
        createDesign(**params)
    elif 1:
        r = h = 100
        asp = 4 * np.pi * r**2
        vs = 4 / 3 * np.pi * r**3
        ac = 2 * np.pi * r * h
        vc = np.pi * r**2 * h

        params = defaultDesign.copy()
        params["materialName"] = "alu2219"
        params["domeType"] = "ellipse"
        params["polarOpeningRadius"] = 0
        params["domeLengthByR"] = 1
        params["dcyl"] = 2 * r
        params["lcyl"] = h
        params["safetyFactor"] = 2.25
        params["pressure"] = 0.2
        createDesign(**params)
        print("volumne", vc + vs, "area", ac + asp)
