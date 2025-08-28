# SPDX-FileCopyrightText: 2023 German Aerospace Center (DLR)
#
# SPDX-License-Identifier: MIT

"""generic methods for tank controls"""

import logging
import os

import numpy as np

from tankoh2 import log, programDir, pychain
from tankoh2.arguments import allArgs, resultKeyToUnitDict, windingOnlyKeywords
from tankoh2.design.designutils import getRequiredVolume
from tankoh2.design.existingdesigns import defaultDesign
from tankoh2.design.loads import getHydrostaticPressure
from tankoh2.geometry.dome import DomeGeneric, getDome
from tankoh2.geometry.geoutils import contourLength, getReducedDomePoints
from tankoh2.service.exception import Tankoh2Error
from tankoh2.service.utilities import (
    createRstTable,
    designDir,
    getRunDir,
    indent,
    readParametersFromYAML,
    writeParametersToYAML,
)
from tankoh2.settings import settings


def saveParametersAndResults(runDir, nonDefaultArgs=None, allInputKwArgs=None, results=None):
    """saves all input parameters and results to a file

    :param runDir: directory to save parameters and results files
    :param nonDefaultArgs: dict with non-default input keys and values
    :param allInputKwArgs: dict with all input keys and values
    :param results: list with result values as returned by createDesign() in control_winding and control_metal
    :param createMessage: flag if a log message should be created
    """
    indentFunc = createRstTable if settings.useRstOutput else indent
    np.set_printoptions(linewidth=np.inf)  # to put arrays in one line
    outputStr = ""

    if nonDefaultArgs is not None:
        outputStr += "\n\nNON-DEFAULT INPUTS\n\n" + indentFunc(nonDefaultArgs.items()) + "\n"
        if allInputKwArgs is None:
            log.info(outputStr)
        filename = os.path.join(
            runDir, "designParameters.yaml" if allInputKwArgs is None else (allInputKwArgs["tankname"] + ".yaml")
        )
        writeParametersToYAML(nonDefaultArgs, filename)  # write yaml which allows running the same design
    if allInputKwArgs is not None:
        outputStr += "\nALL INPUTS\n\n" + indentFunc(allInputKwArgs.items()) + "\n"
        if results is None:
            log.info(outputStr)
    if results is not None:
        resultNames = ["Output Name"] + list(results)
        resultUnits = ["Unit"] + list(
            resultKeyToUnitDict[key.replace("outerVessel_", "").replace("innerVessel_", "")] for key in results
        )
        resultValues = ["Value"] + list(results.values())
        outputStr += "\nOUTPUTS\n\n" + indentFunc(zip(resultNames, resultUnits, resultValues))
        log.info(outputStr)

    filename = os.path.join(runDir, "all_parameters_and_results.txt")
    with open(filename, "a") as f:
        f.write(outputStr)
    np.set_printoptions(linewidth=75)  # reset to default


def _parameterNotSet(inputKwArgs, paramKey):
    """A parameter is not set, if it is not present or None"""
    return paramKey not in inputKwArgs or inputKwArgs[paramKey] is None


def parseConfigFile(configFile):
    filepath = os.path.join(programDir, designDir, configFile)
    configArgs = readParametersFromYAML(filepath)
    return configArgs


def parseDesignArgs(inputKwArgs, windingOrMetal="winding"):
    """Parse keyworded arguments, add missing parameters with defaults and return a new dict.

    :param inputKwArgs: dict with input keyworded arguments
    :param windingOrMetal: flag to switch between FRP winding and metal calculations.
        For metal calculations, all winding parameters are removed.
    :return: dict with all keyworded arguments
    :return: dict with non-default keyworded arguments
    :return: dict with dome and contour objects

    """
    # load a config file if given
    if "configFile" in inputKwArgs and inputKwArgs["configFile"] is not None:
        configArgs = parseConfigFile(inputKwArgs["configFile"])
        inputKwArgs.pop("configFile")
        configArgs.update(inputKwArgs)
        nonDefaultArgs = configArgs
    else:
        nonDefaultArgs = inputKwArgs
    # check if unknown args are used
    updatedArgs = ["tankLength"]  # args that are updated within this method but they are no external argument
    notDefinedArgs = set(nonDefaultArgs.keys()).difference(list(allArgs["name"]) + updatedArgs)
    notDefinedArgs.discard("runDir")
    if notDefinedArgs:
        raise Tankoh2Error(f"These input keywords are unknown: {notDefinedArgs}")
    # read args from CPACS File and overwrite already given parameters
    if (
        "CPACSConfigFile"
        and "tankuID" in nonDefaultArgs
        and nonDefaultArgs["CPACSConfigFile"]
        and nonDefaultArgs["tankuID"] is not None
    ):
        CPACSTank = cpacstank.configFromCpacs(nonDefaultArgs["CPACSConfigFile"], nonDefaultArgs["tankuID"])
        CPACSParams = CPACSTank.outputData()
        nonDefaultArgs.update(CPACSParams)

    # update missing args with default design args
    designArgs = defaultDesign.copy()

    removeIfIncluded = np.array(
        [("lcylByR", "lcyl"), ("domeContourFile", "domeContour"), ("dome2ContourFile", "dome2Contour")]
    )

    # cleanup default args, so they don't interfere with dependent args from nonDefaultArgs
    for arg, supersedeArg in removeIfIncluded:
        if arg in nonDefaultArgs and supersedeArg not in nonDefaultArgs and supersedeArg in designArgs:
            designArgs.pop(supersedeArg)

    designArgs.update(nonDefaultArgs)

    # create advanced settings dictionary
    settingsKeys = list(allArgs[allArgs["group"] == "Advanced Settings"]["name"])
    settings.applySettings(dict((name, nonDefaultArgs[name]) for name in settingsKeys if name in nonDefaultArgs.keys()))

    # set RunDir if not provided
    if designArgs.get("runDir", None) is None:
        if windingOrMetal == "metal":
            designArgs["runDir"] = getRunDir(designArgs.get("tankname", ""), useMilliSeconds=True)
        else:
            designArgs["runDir"] = getRunDir(designArgs.get("tankname", ""))
    os.makedirs(designArgs["runDir"], exist_ok=True)

    # remove args that are superseded by other args (e.g. due to inclusion of default design args)
    for removeIt, included in removeIfIncluded:
        if included in designArgs:
            designArgs.pop(removeIt)

    if designArgs["domeType"] != "ellipse":
        designArgs.pop("domeLengthByR")

    # remove frp-only arguments
    if windingOrMetal not in ["winding", "metal"]:
        raise Tankoh2Error(
            f'The parameter windingOrMetal can only be one of {["winding", "metal"]} but got '
            f'"{windingOrMetal}" instead.'
        )
    if windingOrMetal == "metal":
        for key in windingOnlyKeywords:
            designArgs.pop(key, None)

    if designArgs["numberOfRings"] < 2:
        raise Tankoh2Error(f"Parameter numberOfRings must be at least 2. Got: {designArgs['numberOfRings']}")

    if _parameterNotSet(designArgs, "lcyl"):
        designArgs["lcyl"] = designArgs["lcylByR"] * designArgs["dcyl"] / 2
    if windingOrMetal == "winding":
        # width
        if _parameterNotSet(designArgs, "rovingWidthHoop"):
            designArgs["rovingWidthHoop"] = designArgs["rovingWidth"]
        if _parameterNotSet(designArgs, "rovingWidthHelical"):
            designArgs["rovingWidthHelical"] = designArgs["rovingWidth"]
        # thickness
        if _parameterNotSet(designArgs, "layerThkHoop"):
            designArgs["layerThkHoop"] = designArgs["layerThk"]
        if _parameterNotSet(designArgs, "layerThkHelical"):
            designArgs["layerThkHelical"] = designArgs["layerThk"]
        # check missing target function weights
        if len(designArgs["targetFuncWeights"]) < len(defaultDesign["targetFuncWeights"]):
            missingWeights = len(defaultDesign["targetFuncWeights"]) - len(designArgs["targetFuncWeights"])
            log.info(
                f"You seem to be using an older list of target function weights. Adding {missingWeights} Weights with value of 0.0"
            )
            designArgs["targetFuncWeights"].extend([0.0] * missingWeights)
        elif len(designArgs["targetFuncWeights"]) > len(defaultDesign["targetFuncWeights"]):
            additionalWeights = len(designArgs["targetFuncWeights"]) - len(defaultDesign["targetFuncWeights"])
            log.info(
                f"You seem to be using an older list of target function weights. Removing {additionalWeights} Weights"
            )
            designArgs["targetFuncWeights"] = designArgs["targetFuncWeights"][: len(defaultDesign["targetFuncWeights"])]
    linerThk = designArgs["linerThickness"]
    domeObjects = {}  # "dome" and "dome2" objects will be saved in this dict
    domeVolumes = []

    for domeName in ["dome2", "dome"]:
        if (
            f"{domeName}Contour" in designArgs
            and designArgs[f"{domeName}Contour"][0] is not None
            and designArgs[f"{domeName}Contour"][1] is not None
        ):
            # contour given via coordinates
            domeObjects[f"{domeName}Contour"] = np.array(designArgs[f"{domeName}Contour"])
            dome = DomeGeneric(*domeObjects[f"{domeName}Contour"])
        elif f"{domeName}ContourFile" in designArgs and designArgs[f"{domeName}ContourFile"] is not None:
            # contour given by coordinate file
            designArgs[f"{domeName}Contour"] = getReducedDomePoints(
                os.path.join(programDir, "data", designArgs[f"{domeName}ContourFile"]), settings.contourFileSampling
            )
            domeObjects[f"{domeName}Contour"] = designArgs[f"{domeName}Contour"]
            dome = DomeGeneric(*domeObjects[f"{domeName}Contour"])
        else:
            # contour given by dome type and parameters
            if f"{domeName}Type" not in designArgs or designArgs[f"{domeName}Type"] is None:
                domeObjects[f"{domeName}"] = None
                domeObjects[f"{domeName}Contour"] = None
                continue
            elif designArgs[f"{domeName}Type"] == "custom":
                raise Tankoh2Error(
                    f'{domeName}Type == "custom" but no {domeName}Contour or {domeName}ContourFile given'
                )
            elif designArgs[f"{domeName}Type"] == "ellipse":
                if not designArgs[f"{domeName}LengthByR"]:
                    raise Tankoh2Error(f'{domeName}Type == "ellipse" but "{domeName}LengthByR" is not defined')
            elif designArgs[f"{domeName}Type"] == "conicalElliptical":
                params = ["alpha", "beta", "gamma", "delta1"]
                for param in params:
                    if not designArgs[param]:
                        raise Tankoh2Error(f'domeType == "conicalElliptical" but "{param}" is not defined')
            r = designArgs["dcyl"] / 2
            dome = getDome(
                r,
                designArgs["polarOpeningRadius"],
                designArgs[f"{domeName}Type"],
                lDomeHalfAxis=designArgs.get(f"{domeName}LengthByR", 0.0) * r,
                delta1=designArgs["delta1"],
                rSmall=r - designArgs["alpha"] * r,
                lRad=designArgs["beta"] * designArgs["gamma"] * designArgs["dcyl"],
                lCone=designArgs["beta"] * designArgs["dcyl"]
                - designArgs["beta"] * designArgs["gamma"] * designArgs["dcyl"],
                r1ToD0=designArgs["r1ToD0"],
                r2ToD0=designArgs["r2ToD0"],
            )

        domeVolumes.append(dome.getDomeResizedByThickness(-linerThk).volume)

        domeObjects[f"{domeName}Contour"] = dome.getContour(designArgs["nodeNumber"] // 2)
        domeObjects[f"{domeName}"] = dome

    # get h2 Volume from Mass and Pressure
    if not _parameterNotSet(designArgs, "h2Mass"):
        designArgs["volume"] = getRequiredVolume(
            designArgs["h2Mass"], designArgs["pressure"], designArgs["maxFill"], temperature=designArgs["temperature"]
        )
    if not _parameterNotSet(designArgs, "volume"):
        volumeReq = designArgs["volume"]
        # use volume in order to scale tank length → resets lcyl
        requiredCylVol = volumeReq * 1e9 - domeVolumes[0] - domeVolumes[-1]
        designArgs["lcyl"] = requiredCylVol / (np.pi * ((designArgs["dcyl"] - 2 * linerThk) / 2) ** 2)

        if designArgs["lcyl"] > settings.minCylindricalLength:
            log.info(
                f'Due to volume requirement (V={designArgs["volume"]} m^3), the cylindrical length'
                f' was set to {designArgs["lcyl"]}[mm].'
            )
        else:
            # if the tank volume given in the designArgs is so low that is already fits into the domes,
            # the tank diameter is scaled down to achieve a minimum of minCylindricalLength
            # cylindrical length needed to run simulation with muWind.
            # For conical domes, the parameters alpha, beta, gamma and delta are kept constant while the
            # cylindrical diameter is changed.

            designArgs["lcyl"] = settings.minCylindricalLength

            # The diameter is reduced first in 10 mm steps until the volume falls below the requirement.
            # The loop continues in 1 mm steps from the previous design values until the requirement is again reached.
            for step in [10, 1]:
                while True:
                    domeVolumes = []
                    domeObjects["dome"] = domeObjects["dome"].getDomeResizedByRCyl(-step)
                    domeVolumes.append(domeObjects["dome"].getDomeResizedByThickness(-linerThk).volume)
                    if domeObjects["dome2"] is not None:
                        domeObjects["dome2"] = domeObjects["dome2"].getDomeResizedByRCyl(-step)
                        domeVolumes.append(domeObjects["dome2"].getDomeResizedByThickness(-linerThk).volume)
                    newVolume = (
                        domeVolumes[0] * 1e-9
                        + domeVolumes[-1] * 1e-9
                        + np.pi * (domeObjects["dome"].rCyl - linerThk) ** 2 * designArgs["lcyl"] * 1e-9
                    )
                    if newVolume < volumeReq:
                        break
                    domeObjects["domeContour"] = domeObjects["dome"].getContour(designArgs["nodeNumber"] // 2)
                    if domeObjects["dome2"] is not None:
                        domeObjects["dome2Contour"] = domeObjects["dome2"].getContour(designArgs["nodeNumber"] // 2)
                    designArgs["dcyl"] = 2 * domeObjects["dome"].rCyl

            log.warning(
                f'Due to volume requirement (V={designArgs["volume"]} m^3) and high cylindrical diameter, '
                f'the cylindrical length was reduced to {designArgs["lcyl"]} [mm] and '
                f'the cylindrical diameter was reduced to {designArgs["dcyl"]} [mm].'
            )

    designArgs["tankLength"] = (
        designArgs["lcyl"]
        + domeObjects["dome"].domeLength
        + (domeObjects["dome"].domeLength if domeObjects["dome2"] is None else domeObjects["dome2"].domeLength)
    )

    if windingOrMetal == "winding":
        minimumNodeNumber = calculateMinimumNodeNumber(settings.nodesPerBand, designArgs, domeObjects)
        if designArgs["nodeNumber"] < minimumNodeNumber:
            designArgs["nodeNumber"] = minimumNodeNumber
            log.info(
                f"Node Number was increased to  {minimumNodeNumber} so that band resolution is high enough to prevent"
                f" muWind errors near the fitting ({settings.nodesPerBand} Nodes per Bandwidth)."
            )
            domeObjects["domeContour"] = domeObjects["dome"].getContour(designArgs["nodeNumber"] // 2)
            if domeObjects["dome2"] is not None:
                domeObjects["dome2Contour"] = domeObjects["dome2"].getContour(designArgs["nodeNumber"] // 2)

    if "verbose" in designArgs and designArgs["verbose"]:
        log.setLevel(logging.DEBUG)
        for handler in log.handlers:
            handler.setLevel(logging.DEBUG)
    designArgs.pop("help", None)

    nonDefaultArgs = dict(sorted(nonDefaultArgs.items()))
    designArgs = dict(sorted(designArgs.items()))
    return designArgs, nonDefaultArgs, domeObjects


def calculateMinimumNodeNumber(nodesPerBand, designArgs, domeObjects):
    """Calculates the minimum node number which is needed to reach a desired number of nodes per bandwidth,

    :param nodesPerBand: desired nodes per bandwidth (5-8 should prevent  errors in Muwind near the polar opening)

    :param designArgs: the design Arguments dict
    :return: minimumNodeNumber
    """
    if domeObjects["dome2Contour"] is not None:
        x, r = domeObjects["domeContour"]
        x2, r2 = domeObjects["dome2Contour"]
        tankContourLength = designArgs["lcyl"] + contourLength(x, r) + contourLength(x2, r2)
    else:
        x, r = domeObjects["domeContour"]
        tankContourLength = designArgs["lcyl"] + 2 * contourLength(x, r)
    bandWidth = designArgs["rovingWidthHelical"] * designArgs["numberOfRovings"]
    minimumNodeNumber = int(np.ceil(tankContourLength * nodesPerBand / bandWidth))

    return minimumNodeNumber


def getBurstPressure(designArgs, length):
    """Calculate burst pressure

    The limit and ultimate pressure is calculated as

    .. math::

        p_{limit} = (p_{des} * f_{valve} + p_{hyd})

    .. math::

        p_{ult} = p_{limit} * f_{ult}

    - :math:`p_{des}` maximum operating pressure [MPa] (pressure in designArgs)
    - :math:`f_{valve}` factor for valve release (valveReleaseFactor in designArgs)
    - :math:`p_{hyd}` hydrostatic pressure according to CS 25.963 (d)
    - :math:`f_{ult}` ultimate load factor (safetyFactor in designArgs)
    """
    dcyl = designArgs["dcyl"]
    safetyFactor = designArgs["safetyFactor"]
    pressure = designArgs["pressure"]  # pressure in MPa (bar / 10.)
    temperature = designArgs["temperature"]
    valveReleaseFactor = designArgs["valveReleaseFactor"]
    useHydrostaticPressure = designArgs["useHydrostaticPressure"]
    tankLocation = designArgs["tankLocation"]
    hydrostaticPressure = (
        getHydrostaticPressure(tankLocation, length, dcyl, pressure, temperature) if useHydrostaticPressure else 0.0
    )
    return (pressure + hydrostaticPressure) * safetyFactor * valveReleaseFactor


def saveLayerBook(runDir, vesselName):
    """Writes a text file with layer information for manufacturing"""
    vessel = pychain.winding.Vessel()
    filename = runDir + "//" + vesselName + ".vessel"
    log.info(f"Load vessel from {filename}")
    vessel.loadFromFile(filename)
    vessel.finishWinding()

    # get composite design of vessel
    composite = pychain.material.Composite()
    filename = runDir + "//" + vesselName + ".design"
    composite.loadFromFile(filename)

    linerOuterDiameter = 2.0 * vessel.getLiner().cylinderRadius

    outputFileName = runDir + "//" + vesselName + "LayupBook.txt"

    outArr = []
    vesselDiameter = linerOuterDiameter
    for layerNo in range(vessel.getNumberOfLayers()):
        woundedPlyThickness = composite.getLayerThicknessFromWindingProps(
            layerNo
        )  # composite.getOrthotropLayer(layerNo).thickness
        vesselDiameter = vesselDiameter + 2.0 * woundedPlyThickness
        outArr.append(
            [
                layerNo + 1,
                composite.getAngle(layerNo),
                vessel.getHoopLayerShift(layerNo, True),
                vessel.getHoopLayerShift(layerNo, True),
                woundedPlyThickness / 2.0,
                woundedPlyThickness,
                vessel.getPolarOpeningR(layerNo, True),
                vesselDiameter,
            ]
        )

    layerBookMsg = indent(
        [
            [
                "No. Layer",
                "Angle in Cylinder",
                "HoopLayerShift left",
                "HoopLayerShift right",
                "Single Ply Thickness",
                "Wounded Layer Thickness",
                "Polar Opening Radius",
                "Vessel Cylinder Diameter",
            ]
        ]
        + outArr
    )
    log.debug(layerBookMsg)

    with open(outputFileName, "w") as file:
        file.write(layerBookMsg)
