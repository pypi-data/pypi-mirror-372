# SPDX-FileCopyrightText: 2023 German Aerospace Center (DLR)
#
# SPDX-License-Identifier: MIT

"""control a tank optimization"""

import os
from datetime import datetime

import numpy as np
import pandas as pd

from tankoh2 import log, programDir, pychain
from tankoh2.control.genericcontrol import (
    _parameterNotSet,
    getBurstPressure,
    parseDesignArgs,
    saveLayerBook,
    saveParametersAndResults,
)
from tankoh2.design.designutils import getMassByVolume
from tankoh2.design.metal.material import getMaterial as getMaterialMetal
from tankoh2.design.winding.contour import buildFitting, getDome, getLiner, saveLiner
from tankoh2.design.winding.designopt import designLayers
from tankoh2.design.winding.material import checkFibreVolumeContent, getCompositeMuwind, getMaterialPyChain
from tankoh2.design.winding.windingutils import (
    copyAsJson,
    getLayerNodalCoordinates,
    getMandrelNodalCoordinates,
    updateName,
)
from tankoh2.geometry.liner import Liner
from tankoh2.masses.massestimation import (
    getAuxMaterials,
    getFairingMass,
    getFittingMass,
    getInsulationMass,
    getLinerMass,
)
from tankoh2.service.utilities import writeParametersToYAML


def createDesign(**kwargs):
    """Create a winding design

    For a list of possible parameters, please refer to tankoh2.design.existingdesigns.allDesignKeywords
    """
    startTime = datetime.now()
    # #########################################################################################
    # SET Parameters of vessel
    # #########################################################################################
    designArgs, nonDefaultArgs, domeObjects = parseDesignArgs(kwargs)
    saveParametersAndResults(designArgs["runDir"], nonDefaultArgs, designArgs)
    domeContourFilename = os.path.join(designArgs["runDir"], f"domeContour" + ".yaml")
    writeParametersToYAML(
        {
            f"{domeName}Contour": domeObjects[f"{domeName}Contour"]
            for domeName in ["dome2", "dome"]
            if domeName in domeObjects and domeObjects[domeName] is not None
        },
        domeContourFilename,
    )
    # General
    tankname = designArgs["tankname"]
    nodeNumber = designArgs["nodeNumber"]  # number of nodes of full model.
    runDir = designArgs["runDir"]
    verbosePlot = designArgs["verbosePlot"]
    if designArgs["initialAnglesAndShifts"] is None:
        initialAnglesAndShifts = None
    else:
        initialAnglesAndShifts = list(zip(*designArgs.get("initialAnglesAndShifts", None)))
        if len(initialAnglesAndShifts[0]) == 2:  # convert to 3-Tuple if given as a 2-Tuple
            initialAnglesAndShifts = [(angle, shift, shift) for (angle, shift) in initialAnglesAndShifts]
    # Transpose

    # Optimization
    layersToWind = designArgs["maxLayers"]
    relRadiusHoopLayerEnd = designArgs["relRadiusHoopLayerEnd"]
    targetFuncWeights = designArgs["targetFuncWeights"]
    if designArgs["enforceWindableContour"]:
        targetFuncWeights.append(1.0)
    else:
        targetFuncWeights.append(0.0)
    sortLayers = designArgs["sortLayers"]
    sortLayersAboveAngle = designArgs["sortLayersAboveAngle"]
    angleStartOfShoulderZone = designArgs["angleStartOfShoulderZone"]
    findValidWindingAngles = designArgs["findValidWindingAngles"]
    doHoopShiftOptimization = designArgs["optimizeHoopShifts"]
    hoopShiftRange = designArgs["hoopShiftRange"]
    hoopLayerCluster = designArgs["hoopLayerCluster"]

    # Geometry - generic
    polarOpeningRadius = designArgs["polarOpeningRadius"]  # mm
    dcyl = designArgs["dcyl"]  # mm
    lcylinder = designArgs["lcyl"]  # mm

    # Design Args
    pMinOperation = designArgs["minPressure"]
    pMaxOperation = designArgs["fatigueCyclePressure"] if designArgs["fatigueCyclePressure"] else designArgs["pressure"]
    burstPressure = getBurstPressure(designArgs, designArgs["tankLength"])
    helicalDesignFactor = designArgs["helicalDesignFactor"]
    failureMode = designArgs["failureMode"]
    useFibreFailure = failureMode.lower() == "fibrefailure"
    deltaT = 0 if designArgs["temperature"] is None else 273 - designArgs["temperature"]

    # Material
    materialName = designArgs["materialName"]
    materialName = materialName if materialName.endswith(".json") else materialName + ".json"
    materialFilename = materialName
    if not os.path.exists(materialName):
        materialFilename = os.path.join(programDir, "data", materialName)

    # fatigue
    operationalCycles = designArgs["operationalCycles"]
    zeroPressureCycles = designArgs["zeroPressureCycles"]
    simulatedTankLives = designArgs["simulatedTankLives"]
    testPressureAfterFatigue = designArgs["testPressureAfterFatigue"]

    # Fiber roving parameter
    layerThkHoop = designArgs["layerThkHoop"]
    layerThkHelical = designArgs["layerThkHelical"]
    rovingWidthHoop = designArgs["rovingWidthHoop"]
    rovingWidthHelical = designArgs["rovingWidthHelical"]
    numberOfRovings = designArgs["numberOfRovings"]
    bandWidth = rovingWidthHoop * numberOfRovings
    tex = designArgs["tex"]  # g / km
    rho = designArgs["fibreDensity"]  # g / cm^3
    sectionAreaFibre = tex / (1000.0 * rho)
    checkFibreVolumeContent(layerThkHoop, layerThkHelical, sectionAreaFibre, rovingWidthHoop, rovingWidthHelical)

    # output files
    linerFilename = os.path.join(runDir, tankname + ".liner")
    designFilename = os.path.join(runDir, tankname + ".design")
    vesselFilename = os.path.join(runDir, tankname + ".vessel")
    windingResultFilename = os.path.join(runDir, tankname + ".wresults")

    # #########################################################################################
    # Create Liner
    # #########################################################################################
    # Geometry - domes
    dome = getDome(dcyl / 2.0, polarOpeningRadius, designArgs["domeType"], *domeObjects["domeContour"])
    dome2 = (
        None
        if designArgs["dome2Type"] is None
        else getDome(dcyl / 2.0, polarOpeningRadius, designArgs["dome2Type"], *domeObjects["dome2Contour"])
    )

    liner = getLiner(dome, lcylinder, dome2=dome2, nodeNumber=nodeNumber)
    fittingMaterial = getMaterialMetal(designArgs["fittingMaterial"])
    buildFitting(
        liner,
        designArgs["fittingType"],
        designArgs["r0"],
        designArgs["r1"],
        designArgs["r3"],
        designArgs["rD"],
        designArgs["dX1"],
        designArgs["dXB"],
        designArgs["dX2"],
        designArgs["lV"],
        designArgs["alphaP"],
        designArgs["rP"],
        designArgs["customBossName"],
    )
    saveLiner(
        liner,
        linerFilename,
        "liner_" + tankname,
    )
    # ###########################################
    # Create material
    # ###########################################
    materialMuWind = getMaterialPyChain(materialFilename)
    linerMat, insMat, fairMat = getAuxMaterials(
        designArgs["linerMaterial"], designArgs["insulationMaterial"], designArgs["fairingMaterial"]
    )

    compositeArgs = [
        layerThkHoop,
        layerThkHelical,
        materialMuWind,
        sectionAreaFibre,
        rovingWidthHoop,
        rovingWidthHelical,
        numberOfRovings,
        numberOfRovings,
        tex,
        designFilename,
        tankname,
    ]
    composite = getCompositeMuwind([90.0], *compositeArgs)
    # create vessel and set liner and composite
    vessel = pychain.winding.Vessel()
    vessel.setLiner(liner)
    mandrel = liner.getMandrel1()
    df = pd.DataFrame(
        np.array([mandrel.getXArray(), mandrel.getRArray(), mandrel.getLArray()]).T, columns=["x", "r", "l"]
    )
    df.to_csv(os.path.join(runDir, "nodalResults.csv"), sep=";")

    vessel.setComposite(composite)

    if designArgs["dome2Type"] is None:
        fittingMass = 2 * getFittingMass(
            vessel, designArgs["fittingType"], fittingMaterial, True, designArgs["customBossName"]
        )
    else:
        fitting1Mass = getFittingMass(
            vessel, designArgs["fittingType"], fittingMaterial, True, designArgs["customBossName"]
        )
        fitting2Mass = getFittingMass(
            vessel, designArgs["fittingType"], fittingMaterial, False, designArgs["customBossName"]
        )
        fittingMass = fitting1Mass + fitting2Mass
    # #############################################################################
    # run winding simulation
    # #############################################################################
    vessel.saveToFile(vesselFilename)  # save vessel
    copyAsJson(vesselFilename, "vessel")
    results = designLayers(
        vessel,
        layersToWind,
        polarOpeningRadius,
        bandWidth,
        materialMuWind,
        burstPressure,
        pMinOperation,
        pMaxOperation,
        helicalDesignFactor,
        dome2 is None,
        runDir,
        compositeArgs,
        verbosePlot,
        useFibreFailure,
        relRadiusHoopLayerEnd,
        initialAnglesAndShifts,
        targetFuncWeights,
        materialName,
        sortLayers,
        sortLayersAboveAngle,
        angleStartOfShoulderZone,
        hoopShiftRange,
        hoopLayerCluster,
        doHoopShiftOptimization,
        findValidWindingAngles,
        operationalCycles,
        zeroPressureCycles,
        simulatedTankLives,
        testPressureAfterFatigue,
        deltaT,
    )

    (
        frpMass,
        area,
        iterations,
        reserveFac,
        stressRatio,
        cylinderThickness,
        maxThickness,
        frpMassStrengthOnly,
        frpMassFatigueOnly,
        puckMax,
        angles,
        hoopLayerShiftsSide1,
        hoopLayerShiftsSide2,
    ) = results
    angles = np.around(angles, decimals=3)
    hoopByHelicalFrac = len([a for a in angles if a > 89]) / len([a for a in angles if a < 89])
    hoopLayerShiftsSide1 = np.around(hoopLayerShiftsSide1, decimals=3)
    hoopLayerShiftsSide2 = np.around(hoopLayerShiftsSide2, decimals=3)
    duration = datetime.now() - startTime

    # #############################################################################
    # postprocessing
    # #############################################################################

    linerTankoh = Liner(domeObjects["dome"], lcylinder, domeObjects["dome2"])
    linerThk, insThk, fairThk = (
        designArgs["linerThickness"],
        designArgs["insulationThickness"],
        designArgs["fairingThickness"],
    )
    if designArgs["temperature"] is None:  # liquid, cryo vessel
        auxMasses = [
            getLinerMass(linerTankoh, linerMatName=linerMat, linerThickness=linerThk),
            getInsulationMass(linerTankoh, insulationMatName=insMat, insulationThickness=insThk),
            getFairingMass(linerTankoh, fairingMatName=fairMat, fairingThickness=fairThk),
        ]
    else:
        if designArgs["temperature"] > 33.145:  # compressed gas vessel
            auxMasses = [
                getLinerMass(linerTankoh, linerMatName=linerMat, linerThickness=linerThk),
                0.0,
                0.0,
            ]
        else:  # liquid, cryo vessel
            auxMasses = [
                getLinerMass(linerTankoh, linerMatName=linerMat, linerThickness=linerThk),
                getInsulationMass(linerTankoh, insulationMatName=insMat, insulationThickness=insThk),
                getFairingMass(linerTankoh, fairingMatName=fairMat, fairingThickness=fairThk),
            ]
    totalMass = np.sum([frpMass] + auxMasses + [fittingMass])
    linerInnerTankoh = linerTankoh.getLinerResizedByThickness(-1 * linerThk)
    volume = linerInnerTankoh.volume / 1e6  # Volume considering liner
    if not _parameterNotSet(designArgs, "h2Mass"):
        h2Mass = designArgs["h2Mass"]
        gravimetricIndex = h2Mass / (totalMass + h2Mass)
    else:
        h2Mass = getMassByVolume(
            volume / 1e3, designArgs["pressure"], designArgs["maxFill"], temperature=designArgs["temperature"]
        )
        gravimetricIndex = h2Mass / (totalMass + h2Mass)

    results = {
        "shellMass": frpMass,
        "linerMass": auxMasses[0],
        "insulationMass": auxMasses[1],
        "fairingMass": auxMasses[2],
        "fittingMass": fittingMass,
        "totalMass": totalMass,
        "volume": volume,
        "h2Mass": h2Mass,
        "area": area,
        "lengthAxial": liner.linerLength,
        "numberOfLayers": vessel.getNumberOfLayers(),
        "cylinderThickness": cylinderThickness,
        "maxThickness": maxThickness,
        "reserveFactor": reserveFac,
        "gravimetricIndex": gravimetricIndex,
        "stressRatio": stressRatio,
        "hoopHelicalRatio": hoopByHelicalFrac,
        "iterations": iterations,
        "duration": duration,
        "frpMassStrengthOnly": frpMassStrengthOnly,
        "frpMassFatigueOnly": frpMassFatigueOnly,
        "puckMax": puckMax,
        "fatigueFactor": frpMassFatigueOnly / frpMassStrengthOnly,
        "angles": angles,
        "hoopLayerShifts1": hoopLayerShiftsSide1,
        "hoopLayerShifts2": hoopLayerShiftsSide2,
    }

    saveParametersAndResults(designArgs["runDir"], results=results)
    anglesShiftsFilename = os.path.join(designArgs["runDir"], "anglesAndShifts" + ".yaml")
    writeParametersToYAML(
        {"initialAnglesAndShifts": [angles, hoopLayerShiftsSide1, hoopLayerShiftsSide2]}, anglesShiftsFilename
    )
    vessel.securityFactor = designArgs["safetyFactor"] * designArgs["valveReleaseFactor"]
    vessel.burstPressure = burstPressure * 10
    vessel.calculateVesselStatistics()
    vessel.saveToFile(vesselFilename)  # save vessel
    updateName(vesselFilename, tankname, ["vessel"])
    copyAsJson(vesselFilename, "vessel")

    # save winding results
    windingResults = pychain.winding.VesselWindingResults()
    windingResults.buildFromVessel(vessel)
    windingResults.saveToFile(windingResultFilename)
    copyAsJson(windingResultFilename, "wresults")

    # write nodal layer results dataframe to csv
    mandrelCoordinatesDataframe = getMandrelNodalCoordinates(liner, dome2 is None)
    layerCoordinatesDataframe = getLayerNodalCoordinates(windingResults, dome2 is None)
    nodalResultsDataframe = pd.concat([mandrelCoordinatesDataframe, layerCoordinatesDataframe], join="outer", axis=1)
    nodalResultsDataframe.to_csv(os.path.join(runDir, "nodalResults.csv"), sep=";")

    saveLayerBook(runDir, tankname)

    log.info(f"iterations {iterations}, runtime {duration.seconds} seconds")
    log.info("FINISHED")

    return results


if __name__ == "__main__":
    if 0:
        # params = parameters.defaultDesign.copy()
        params = parameters.hytazerSMR1.copy()
        createDesign(**params)
    elif 1:
        # params = parameters.defaultUnsymmetricDesign.copy()
        params = {"configFile": "hytazer_smr_iff_2.0bar_final.yaml"}
        createDesign(**params)
    elif 0:
        createDesign(pressure=5)
    elif 1:
        parameters.vphDesign1["polarOpeningRadius"] = 23
        createDesign(**parameters.vphDesign1)
    else:
        rs = []
        lengths = np.linspace(1000.0, 6000, 11)
        # np.array([1]) * 1000
        for l in lengths:
            r = createWindingDesign(
                useFibreFailure=False,
                safetyFactor=1.0,
                burstPressure=0.5,
                domeType=pychain.winding.DOME_TYPES.ISOTENSOID,
                lcyl=l,
                dcyl=2400,
                # polarOpeningRadius=30.,
            )
            rs.append(r)
        print(indent(results))
