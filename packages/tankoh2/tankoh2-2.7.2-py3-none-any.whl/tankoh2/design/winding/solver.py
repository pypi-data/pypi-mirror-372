# SPDX-FileCopyrightText: 2023 German Aerospace Center (DLR)
#
# SPDX-License-Identifier: MIT

"""solver related methods"""

import itertools

import numpy as np
import pandas as pd
from patme.mechanics.material import Composite, Layer

from tankoh2 import log, pychain
from tankoh2.design.winding.contour import calculateWindability
from tankoh2.design.winding.winding import windLayer
from tankoh2.design.winding.windingutils import (
    getAnglesFromVesselCylinder,
    getLayerAngles,
    getLayerThicknesses,
    isHoopLayer,
)
from tankoh2.mechanics.material import MaterialDefinition
from tankoh2.settings import settings

targetFuncNames = [
    "max puck",
    "max puck at last crit location",
    "puck sum",
    "mass",
    "strain diff",
    "strain diff at last crit location",
    "windable contour",
]
resultNames = targetFuncNames + ["maxPuckIndex", "maxStrainDiffIndex"]


def getMaxPuckByAngle(angle, args):
    """Sets the given angle, winding sim, puck analysis

    :return: maximum puck fibre failure"""
    return getMaxPuckLocalPuckMassIndexByAngle(angle, args)[0]


def getWeightedTargetFuncByAngle(angle, args):
    """Sets the given angle, winding sim, puck analysis

    :return: maximum puck fibre failure"""
    return np.sum(getMaxPuckLocalPuckMassIndexByAngle(angle, args)[:-2])


def getMaxPuckLocalPuckMassIndexByAngle(angle, kwArgs):
    """Sets the given angle, winding sim, puck analysis

    :return: maximum puck fibre failure"""
    vessel, layerNumber, newLayerPosition = (
        kwArgs["vessel"],
        kwArgs["layerNumber"],
        kwArgs["newLayerPosition"],
    )
    if hasattr(angle, "__iter__"):
        angle = angle[0]
    if angle is not None:
        if newLayerPosition < layerNumber:
            log.debug(f"Layer {newLayerPosition}, wind angle {angle}")
            actualPolarOpening = windLayer(vessel, newLayerPosition, angle)
            windLayer(vessel, layerNumber)
        else:
            log.debug(f"Layer {layerNumber}, wind angle {angle}")
            actualPolarOpening = windLayer(vessel, layerNumber, angle)
        if actualPolarOpening is np.inf:
            return 1000000, 0, 0
    result = getTargetFunctionValues(kwArgs)
    log.debug(
        f"Layer {layerNumber}, angle {angle}, " + str([(name, str(val)) for name, val in zip(resultNames, result)])
    )
    return result


def getMaxPuckByShift(shift, args, shiftside2=None):
    """Sets the given hoop shift, winding sim, puck analysis

    :return: maximum puck fibre failure
    """
    return getMaxPuckLocalPuckMassIndexByShift(shift, args, shiftside2)[0]


def getWeightedTargetFuncByShift(shiftSide1, shiftSide2, args):
    """Sets the given shift, winding sim, puck analysis

    :return: maximum puck fibre failure"""
    return np.sum(getMaxPuckLocalPuckMassIndexByShift(shiftSide1, shiftSide2, args)[:-2])


def getMaxPuckLocalPuckMassIndexByShift(shiftSide1, shiftSide2, kwArgs):
    """Sets the given hoop shift, winding sim, puck analysis

    :param shiftside1:
    :param shiftSide2:
    :param kwArgs:
    :return: tuple, (maximum puck fibre failure, index of max FF/IFF)
    """
    if hasattr(shiftSide1, "__iter__"):
        shiftSide1 = shiftSide1[0]
    vessel, layerNumber = kwArgs["vessel"], kwArgs["layerNumber"]
    vessel.setHoopLayerShift(layerNumber, shiftSide1, True)
    if not vessel.isSymmetric():
        vessel.setHoopLayerShift(layerNumber, shiftSide2, False)

    actualPolarOpening = windLayer(vessel, layerNumber)
    if actualPolarOpening is np.inf:
        return np.inf, 0
    result = getTargetFunctionValues(kwArgs)
    log.debug(
        f"Layer {layerNumber}, hoop shift side 1 {shiftSide1}, hoop shift side 2 {shiftSide2} "
        + str([(name, str(val)) for name, val in zip(resultNames, result)])
    )
    return result


def getTargetFunctionValues(kwArgs, puckAndStrainDiff=None, scaleTf=True):
    """Return target function values of the all layers after winding the given angle

    :param kwArgs: dictionary of arguments for the calculation of target function results
    :param puckAndStrainDiff: tuple (puck values, strain Diff, maximum and minimum circumferential strain)
    :param scaleTf: flag to scale target functions
    :return:
    """
    vessel, layerNumber, materialMuWind = kwArgs["vessel"], kwArgs["layerNumber"], kwArgs["materialMuWind"]
    newLayerPosition = kwArgs["newLayerPosition"]
    burstPressure, useIndices = kwArgs["burstPressure"], kwArgs["useIndices"]
    useFibreFailure, symmetricContour = kwArgs["useFibreFailure"], kwArgs["symmetricContour"]
    elemIdxPuckMax, elemIdxBendMax = kwArgs["elemIdxPuckMax"], kwArgs["elemIdxBendMax"]
    helicalDesignFactors = kwArgs["helicalDesignFactors"]
    targetFuncScaling = kwArgs["targetFuncScaling"]
    thickShellScaling = kwArgs["thickShellScaling"]
    contourSmoothingBorders = kwArgs["contourSmoothingBorders"]
    windabilityGoal = kwArgs["windabilityGoal"]
    deltaT = kwArgs["deltaT"]
    if puckAndStrainDiff is None:
        puck, strainDiff = getPuckStrainDiff(
            vessel, materialMuWind, burstPressure, useIndices, symmetricContour, useFibreFailure, True, deltaT
        )
        if thickShellScaling is not None:
            puck.iloc[:, : len(thickShellScaling)] = puck.iloc[:, : len(thickShellScaling)].multiply(
                thickShellScaling, "columns"
            )
        if helicalDesignFactors:
            puck = puck.multiply(helicalDesignFactors, "rows")

    else:
        puck, strainDiff = puckAndStrainDiff

    maxPerElement = puck.max(axis=1)
    maxPuckIndex = maxPerElement.idxmax()

    maxStrainDiff = strainDiff.max()
    maxStrainDiffIndex = np.argmax(strainDiff)
    strainDiffAtCritIdx = strainDiff[elemIdxBendMax]

    maxPuck = maxPerElement.max()
    puckAtCritIdx = maxPerElement[elemIdxPuckMax]

    puckSum = np.sum(maxPerElement)

    layMass = vessel.getVesselLayer(layerNumber).getVesselLayerPropertiesSolver().getWindingLayerResults().fiberMass

    if scaleTf and targetFuncScaling[6] == 0:
        windableContour = 0
    else:
        windableContour = calculateWindability(vessel, newLayerPosition, windabilityGoal, contourSmoothingBorders)
        if not symmetricContour:
            windableContour2 = calculateWindability(
                vessel, newLayerPosition, windabilityGoal, contourSmoothingBorders, isMandrel1=False
            )
            windableContour = max(windableContour2, windableContour)

    tfValues = np.array([maxPuck, puckAtCritIdx, puckSum, layMass, maxStrainDiff, strainDiffAtCritIdx, windableContour])
    if scaleTf:
        tfValues *= targetFuncScaling
    return *tfValues, maxPuckIndex, maxStrainDiffIndex


def getPuckStrainDiff(
    vessel,
    materialMuWind,
    burstPressure,
    useIndices=None,
    symmetricContour=True,
    useFibreFailure=True,
    useMeridianStrain=True,
    deltaT=0,
):
    """returns the puck values and strain diffs for the actual"""
    results = getLinearResults(
        vessel,
        materialMuWind,
        burstPressure,
        useIndices=useIndices,
        symmetricContour=symmetricContour,
        useFibreFailure=useFibreFailure,
        deltaT=deltaT,
    )
    puck = results[7] if useFibreFailure else results[8]
    strainDiff = abs(results[3] - results[4]) if useMeridianStrain else abs(results[5] - results[6])
    return puck, strainDiff


def getThickShellScaling(vessel, burstPressure, composite):
    """Calculates scaling factors for the cylinder stress results from FEM analysis by comparing with MuTube analytical method

    :param vessel: µWind vessel instance
    :param burstPressure: burst pressure in MPa
    :param composite: composite Material (identical to vessel)
    :return: vector with scaling factors
    """
    # Get Material from layer0 (current assumption that all layers have the same material)
    material = composite.getMaterial(0)
    elasticProperties = material.elasticProperties
    # Set Poisson12 to 0 to get only the hoop strain that is directly related to hoop stress (not due to poisson effect)
    oldNu12 = elasticProperties.nu_12
    elasticProperties.nu_12 = 1e-12

    if composite.getMaterial(0).elasticProperties.E_2 != composite.getMaterial(0).elasticProperties.E_3:
        # assume that E2 = E3 (necessary for tube calculation to work, only relevant if the material doesn't follow this)
        materialChanged = True
        oldE2 = elasticProperties.E_2
        elasticProperties.E_2 = elasticProperties.E_3
        oldG12 = elasticProperties.G_12
        elasticProperties.G_12 = elasticProperties.G_13
    else:
        materialChanged = False

    material.elasticProperties = elasticProperties
    composite.setCompositeMaterial(material)
    # initialize model
    liner = vessel.getLiner()
    tubeSolver = initializeTubeSolver(liner, burstPressure)
    tubeResults = getTubeResults(tubeSolver, composite, calculatePuck=False)
    layerPosition = pychain.tube.LAYER_POSITION()
    # calculate circumferential strain for all layers
    tubeStrain = np.array(
        [
            tubeResults.getEpsC(layerNumber, layerPosition.LAYER1_BOTTOM)
            for layerNumber in range(vessel.getNumberOfLayers())
        ]
    )
    angles = getAnglesFromVesselCylinder(vessel)
    meanHoopStrain = np.mean(tubeStrain)
    # set scaling factor for hoop layers
    thickShellScaling = np.array(
        [
            tubeStrain[layerNumber] / meanHoopStrain if isHoopLayer(angles[layerNumber]) else 1
            for layerNumber in range(vessel.getNumberOfLayers())
        ]
    )

    # Reset material values
    elasticProperties.nu_12 = oldNu12
    if materialChanged:
        elasticProperties.E_2 = oldE2
        elasticProperties.G_12 = oldG12
    material.elasticProperties = elasticProperties
    composite.setCompositeMaterial(material)

    # Replace the zeros with the interpolated values
    return thickShellScaling.tolist()


def getHelicalDesignFactors(nrOfElements, hoopStart, hoopEnd, helicalDesignFactor):
    """
    :param nrOfElements: number of elements along contour
    :param hoopStart: start of hoop area
    :param hoopEnd: end of hoop area
    :param helicalDesignFactor: design factor to apply to dome region
    :return:
    """
    helicalDesignFactors = [
        1 if hoopStart <= element <= hoopEnd else helicalDesignFactor for element in range(nrOfElements)
    ]
    return helicalDesignFactors


def getStresses(
    vessel,
    materialMuWind,
    OperationalPressure,
    thickShellScaling=None,
    useIndices=None,
    symmetricContour=True,
    deltaT=0,
):
    """returns stresses"""
    S11, S22, S12, *_ = getLinearResults(
        vessel,
        materialMuWind,
        OperationalPressure,
        useIndices=useIndices,
        symmetricContour=symmetricContour,
        deltaT=deltaT,
    )
    if thickShellScaling:
        S11 = S11 * thickShellScaling
    stresses = S11, S22, S12
    return stresses


def getLinearResults(
    vessel, materialMuWind, burstPressure, useIndices=None, symmetricContour=True, useFibreFailure=False, deltaT=0
):
    """Calculates puck results and returns them as dataframe

    :param vessel: µWind vessel instance
    :param materialMuWind: µWind material instance
    :param burstPressure: burst pressure in MPa
    :param useIndices: list of element indicies that should be used for evaluation
    :param symmetricContour: flag if contour is symmetric
    :return: 2-tuple with dataframes (fibre failure, inter fibre failure)
    """

    shellModel, shellModel2 = _getShellModels(vessel, burstPressure, symmetricContour)
    # get stresses in the fiber COS (elemNr, layerNr)
    muversion = pychain.utility.MyCrOVersionInfo()
    stressesMandrel1 = shellModel.calculateLayerStressesBottom()
    S11, S22, S12 = stressesMandrel1[0], stressesMandrel1[1], stressesMandrel1[2]
    if not symmetricContour:
        stressesMandrel2 = shellModel2.calculateLayerStressesBottom()
        S11 = np.append(S11[::-1], stressesMandrel2[0], axis=0)
        S22 = np.append(S22[::-1], stressesMandrel2[1], axis=0)
        S12 = np.append(S12[::-1], stressesMandrel2[2], axis=0)
    numberOfElements, numberOfLayers = S11.shape

    if not useFibreFailure and deltaT > 0 and settings.useThermomechanicalStress:
        log.info("Start superpose thermomechanical stresses due to deltaT")
        # superpose thermomechanical stresses due to deltaT
        S11Therm, S22Therm, S12Therm = [], [], []

        materialPatme = MaterialDefinition().getFromMuWindMaterial(materialMuWind)

        # get layer angles and thicknesses for each element
        angles = getLayerAngles(vessel, symmetricContour)
        thicknesses = getLayerThicknesses(vessel, symmetricContour)
        thicknessMean = thicknesses.mean()
        for elementAngles, elementThicknesses in zip(angles.to_numpy(), thicknesses.to_numpy()):
            # fac is for alternating whether + or - angle starts in consecutive layers
            layers = [
                (
                    Layer(phi=fac * angle, thickness=thickness, materialDefinition=materialPatme),
                    Layer(phi=fac * angle, thickness=thickness, materialDefinition=materialPatme),
                )
                for angle, thickness, fac in zip(elementAngles, elementThicknesses, [1, -1, -1, 1] * len(elementAngles))
                # if thickness > settings.epsilon
            ]
            layers = list(itertools.chain(*layers))  # flatten layers
            compositePatme = Composite(layers=layers)
            stresses = np.mean(compositePatme.getThermalLayerStresses(-300), axis=0).T
            S11Therm.append(stresses[0])
            S22Therm.append(stresses[1])
            S12Therm.append(stresses[2])

        S11Therm = np.array(S11Therm)[:, ::2]
        S22Therm = np.array(S22Therm)[:, ::2]
        S12Therm = np.array(S12Therm)[:, ::2]

        # do not check ending of fibres
        S11Therm[thicknesses < thicknessMean / 4] = 0
        S22Therm[thicknesses < thicknessMean / 4] = 0
        S12Therm[thicknesses < thicknessMean / 4] = 0

        S11 = S11Therm
        S22 = S22Therm
        S12 = S12Therm

        log.info("End superpose thermomechanical stresses due to deltaT")

    # modify array since puck criterion requires 6 stress items as input
    stresses = np.zeros((numberOfElements, numberOfLayers, 6))
    stresses[:, :, 0] = S11
    stresses[:, :, 1] = S22
    stresses[:, :, 5] = S12

    if useIndices is not None:
        useIndicesSet = set(useIndices)
    if useFibreFailure and muversion.revisionNumber >= 2489:
        puckFF = stressesMandrel1[3]
        if not symmetricContour:
            puckFF = np.append(puckFF[::-1], stressesMandrel2[3], axis=0)
        if useIndices is not None:
            allIndicesSet = set(range(numberOfElements))
            dontUseIndicesSet = allIndicesSet - useIndicesSet
            for elemIdx in dontUseIndicesSet:
                puckFF[elemIdx] = np.zeros(numberOfLayers)
        puckFF[-1] = 0  # remove, because it's inf sometimes
        if not symmetricContour:
            puckFF[0] = 0
        puckIFF = np.zeros((numberOfElements, numberOfLayers))
    else:
        puck = pychain.failure.PuckFailureCriteria2D()
        puck.setPuckProperties(materialMuWind.puckProperties)
        puckFF, puckIFF = [], []
        stressVec = pychain.utility.StressVector()
        for elemIdx, elemStresses in enumerate(stresses):
            if useIndices is not None and elemIdx not in useIndicesSet:
                failures = np.zeros((numberOfLayers, 2))
            else:
                failures = []
                for layerStress in elemStresses:
                    stressVec.fromVector(layerStress)
                    puckResult = puck.getExposure(stressVec)
                    failures.append([puckResult.f_FF, puckResult.f_E0_IFF])
                failures = np.array(failures)
            puckFF.append(failures[:, 0])
            puckIFF.append(failures[:, 1])
        puckFF = np.array(puckFF)
        puckIFF = np.array(puckIFF)
    if settings.ignoreLastElements:
        puckFF[-settings.ignoreLastElements :] = 0
        if not symmetricContour:
            puckFF[: settings.ignoreLastElements] = 0
    columns = [f"puckFFlay{layerNumber}" for layerNumber in range(numberOfLayers)]
    puckFF = pd.DataFrame(puckFF, columns=columns)
    columns = [f"puckIFFlay{layerNumber}" for layerNumber in range(numberOfLayers)]
    puckIFF = pd.DataFrame(puckIFF, columns=columns)

    epsAxialBot = shellModel.getEpsAxialBottom(0)
    epsAxialTop = shellModel.getEpsAxialTop(0)
    epsCircBot = shellModel.getEpsCircBottom(0)
    epsCircTop = shellModel.getEpsCircTop(0)
    if not symmetricContour:
        epsAxialBot = np.append(epsAxialBot[::-1], shellModel2.getEpsAxialBottom(0))
        epsAxialTop = np.append(epsAxialTop[::-1], shellModel2.getEpsAxialTop(0))
        epsCircBot = np.append(epsCircBot[::-1], shellModel2.getEpsCircBottom(0))
        epsCircTop = np.append(epsCircTop[::-1], shellModel2.getEpsCircTop(0))
    if useIndices is not None:
        zeroIndices = np.array([idx not in useIndicesSet for idx in range(len(epsAxialBot))])
        epsAxialBot[zeroIndices] = 0.0
        epsAxialTop[zeroIndices] = 0.0
        epsCircBot[zeroIndices] = 0.0
        epsCircTop[zeroIndices] = 0.0

    if settings.ignoreLastElements:
        epsAxialBot[-settings.ignoreLastElements :] = 0
        epsAxialTop[-settings.ignoreLastElements :] = 0
        if not symmetricContour:
            epsAxialBot[: settings.ignoreLastElements] = 0
            epsAxialTop[: settings.ignoreLastElements] = 0

    return S11, S22, S12, epsAxialBot, epsAxialTop, epsCircBot, epsCircTop, puckFF, puckIFF


def _getShellModels(vessel, burstPressure, symmetricContour):
    """build shell model for internal calculation

    :param vessel
    :param burstPressure
    :param symmetricContour

    :return shellmodel, shellmodel2 (if nonsymmetric)
    """
    converter = pychain.mycrofem.VesselConverter()
    muversion = pychain.utility.MyCrOVersionInfo()
    if muversion.revisionNumber == 2337:
        shellModel = converter.buildAxShellModell(vessel, burstPressure, True)  # pressure in MPa (bar / 10.)
        shellModel2 = None if symmetricContour else converter.buildAxShellModell(vessel, burstPressure, False)
    else:
        if settings.useSectionPhi:
            shellModel = converter.buildAxShellModell(vessel, burstPressure, False, True)  # pressure in MPa (bar / 10.)
            shellModel2 = (
                None if symmetricContour else converter.buildAxShellModell(vessel, burstPressure, False, False)
            )
        else:
            shellModel = converter.buildAxShellModell(vessel, burstPressure, True, True)  # pressure in MPa (bar / 10.)
            shellModel2 = None if symmetricContour else converter.buildAxShellModell(vessel, burstPressure, True, False)
    # run linear solver
    linerSolver = pychain.mycrofem.LinearSolver(shellModel)
    linerSolver.run(True)
    if not symmetricContour:
        linerSolver = pychain.mycrofem.LinearSolver(shellModel2)
        linerSolver.run(True)
    return shellModel, shellModel2


def initializeTubeSolver(liner, burstPressure):
    """setup muTube solver with liner and burst Pressure

    :param vessel
    :param burstPressure
    :param symmetricContour

    :return DwRohrSolver object
    """

    tubeSolver = pychain.tube.DwRohrSolver()
    # Set Geometry
    tubeSolver.setInnerRadius(liner.cylinderRadius)
    tubeSolver.setLength(liner.cylinderLength)
    # Set Loads
    tubeSolver.setInnerPressureMPa(burstPressure)
    tubeSolver.setAxialForce(burstPressure * liner.cylinderRadius**2 * np.pi)
    return tubeSolver


def getTubeResults(tubeSolver, composite, calculatePuck=True):
    """apply composite to tubeSolver, get results

    :param tubeSolver: initialized DwRohrObject
    :param composite: composite design
    :param calculatePuck: flag whether to calculate puck results or just strain & stress

    :return DwRohrSolver object
    """

    tubeSolver.setComposite(composite)
    tubeSolver.runLinear()
    if calculatePuck:
        tubeSolver.calculatePuckResults(1)
    return tubeSolver.getResults(1)


def getLocalFVC(vessel, symmetricContour=True):
    """get local fiber volume content from the winding simulation

    :param vessel
    :param symmetricContour

    :return FVC: nparray of the local fiber volume contents of the sections
    """

    windingResults = pychain.winding.VesselWindingResults()
    windingResults.buildFromVessel(vessel)
    totalSections = vessel.getLiner().getMandrel1().numberOfNodes - 1
    layers = windingResults.getNumberOfLayers()
    FVC = np.ones((totalSections, layers)) * 1e-9
    for layerNumber in range(layers):
        sections = windingResults.getNumberOfSectionsInLayer(layerNumber + 1, True)
        for sectionNumber in range(sections):
            FVC[sectionNumber][layerNumber] = windingResults.getSectionData(
                layerNumber + 1, sectionNumber + 1, True
            ).phi
    if not symmetricContour:
        totalSectionsSide2 = vessel.getLiner().getMandrel2().numberOfNodes - 1
        FVCSide2 = np.ones((totalSectionsSide2, layers)) * 1e-9
        for layerNumber in range(layers):
            sections = windingResults.getNumberOfSectionsInLayer(layerNumber + 1, False)
            for sectionNumber in range(sections):
                FVCSide2[sectionNumber][layerNumber] = windingResults.getSectionData(
                    layerNumber + 1, sectionNumber + 1, False
                ).phi
        FVC = np.append(np.flip(FVC, axis=0), FVCSide2, axis=0)

    return FVC
