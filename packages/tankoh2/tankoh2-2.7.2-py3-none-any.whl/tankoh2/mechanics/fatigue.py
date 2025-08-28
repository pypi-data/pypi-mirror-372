# SPDX-FileCopyrightText: 2023 German Aerospace Center (DLR)
#
# SPDX-License-Identifier: MIT

"""
Fatigue analysis
================

Metal
-----

The metal fatigue analysis is based on a stress-life approach.
It uses the given load cycles and fits SN-curves to calculate the
number of cycles to failure for each type of load cycle.
This number is accumulated to a structural damage factor using the palmgren-miner rule.

FRP
---

The fatigue calculation for fibre reinforced plastics (FRP), the method of using haigh diargams is
implemented. It is based on the work of Schokrih and Lessard :cite:`shokrieh2000progressive` and Lüders
:cite:`luders2020mehrskalige` (especially chapter 8.1.2).

It describes a fatigue stress factor f, that is dependent on the normalized amplitude and normalized
mean stress.

.. math::
    f = \\frac{normAmplitude} {(1 - normMeanstress)^u \\cdot (c + normMeanstress)^v}

.. math::
    normAmplitude = \\frac{(\\sigma_{Max} - \\sigma_{Min}} {2 \\cdot tensileStrength}

.. math::
    normMeanstress = \\frac{(\\sigma_{Max} + \\sigma_{Min}} {2 \\cdot tensileStrength}

Here u, v are fitted parameters and c is the strength ratio (compressionStrength / tensileStrength).
This fatigue stress factor f can be applied in the master curve

.. math::
    f = C\\cdot N_f^D

to obtain the number of cycles till failure. C and D are fitted parameters again.

.. mermaid::

    flowchart TB
        a[define cycles & occurences]
        b[obtain strength, fatigue properties]
        c[calculate stresses for each load level]
        d["calculate cycles to failure
        for each layer, element, stress direction"]
        e["perform linear damage accumulation
        for each layer, element, stress direction"]
        f[return maximum fatigue damage]
        a --> b
        b --> c
        c --> d
        d --> e
        e --> f


"""

import os
from collections import OrderedDict

import numpy as np
import pandas as pd

from tankoh2 import log, programDir
from tankoh2.design.winding.material import getMaterialPyChain
from tankoh2.design.winding.solver import getLocalFVC, getStresses
from tankoh2.mechanics.material import FrpMaterialFatigueProperties, directions
from tankoh2.service.exception import Tankoh2Error
from tankoh2.service.physicalprops import MPaToPsiFac

dirIndexToDirection = OrderedDict([(v, k) for k, v in directions.items()])


def getFatigueLifeMetalTankLevel(
    material, sigMaxOperation, sigMinOperation, flightCycles, heatUpCycles, Kt=None, vessel=None
):
    """Calculate fatigue life for aircraft applications using LH2 tanks

    :param material: material dict as defined in tankoh2.design.metal.material
    :param sigMaxOperation: max stress at max operating pressure [MPa]
    :param sigMinOperation: max stress at min operating pressure [MPa]
    :param flightCycles: number of flight cycles
    :param heatUpCycles: number of cycles where a cryo tank is heated up.
        This leads to the pressure cycle [0, pMaxOperation]
    :param Kt: stress concentration factor
    :param vessel: µWind vessel instance
    :return: fatigue life factor. If it is larger than 1, the fatigue life is exceeded
    """
    sigMax = [sigMaxOperation] * 2
    sigMin = [sigMinOperation, 0]
    occurences = [flightCycles, heatUpCycles]

    return getFatigueLifeMetal(material, sigMax, sigMin, occurences, Kt)


def getFatigueLifeMetal(material, sigMax, sigMin, occurences, Kt=None):
    """Assess fatigue life calculating the damage for each amplitude, use miner rule for damage accumulation

    According to: Rice, Richard C., et al. "Metallic materials properties development and standardization." MMPDS). National Technical Information Service, cap (2003): 1-4.

    A1 and A4 are corrected according to the given Kt value.
    The new A1 and A4 is obtained by considering that the new Smax is (Kt/Kt_curve) x Smax in the S-N equation

    .. math::
        A_{1 Kt} = A_1 + A_2 \\cdot log_{10} \\frac{K_t}{K_t^{Curve}}

    .. math::
        A_{4 Kt} = A_1 + A_2 \\cdot log_{10} K_t

    :math:`K_t^{Curve}` ist the :math:`K_t` where the SN_parameters (defined in material) are measured

    :param material: material dict as defined in tankoh2.design.metal.material
    :param sigMax: list of maximal stresses
    :param sigMin: list of minimal stresses
    :param occurences: list of occurences
    :param Kt: stress intensity factor
        Pilkey, Walter D.; Pilkey, Deborah F.; Peterson, Rudolph E.: Peterson's stress concentration factors
    :return: accumulated damage factor. If this value is above 1, the structure is seen to be failed
    """
    A1, A2, A3, A4 = material["SN_parameters"]
    Kt_curve = material["Kt_curve"]  # Kt where the parameters where taken
    if Kt is not None:
        if Kt < Kt_curve:
            log.warning(
                f"Scaling the measured SN curves from higher Kt {Kt_curve} to lower Kt {Kt} is not "
                f"conservative. Please check if you can use SN-curves with a Kt smaller or equal"
                f"than the requested Kt"
            )
        A1, A4 = correctSnParameters(A1, A2, A4, Kt_curve, Kt)

    critCycles = getCyclesToFailure(sigMax, sigMin, A1, A2, A3, A4)
    return stressLifeMinerRule(occurences, critCycles)


def correctSnParameters(A1, A2, A4, Kt_curve, Kt):
    A1 = A1 + A2 * np.log10(Kt / Kt_curve)
    A4 = Kt_curve * A4 / Kt
    return A1, A4


def stressLifeMinerRule(occurences, critCycles, sumAxis=None):
    """Calculate the damage factor for each load cycles and the total damage factor according to miner rule

    .. math::
        c = \\sum\\frac{n_i}{n_{ic}}

    :param occurences: list of occurences of the related serr
    :param critCycles: list with number of cycles to failue. Same length as occurences
    :param sumAxis: axis used for damage sum. If None, last axis is used
    :return: accumulated damage factor. If this value is above 1, the structure is seen to be failed
    """
    occurences = np.array(occurences)
    critCycles = np.array(critCycles)

    damageFac = occurences / critCycles
    log.debug(f"Damage of each amplitude+occurence {damageFac}")

    if sumAxis is None:
        sumAxis = damageFac.ndim - 1

    return np.sum(damageFac, axis=sumAxis)


def lessardShokriehRemainingStrength(sigMax, cycles, cyclesToFailure, beta1, beta2, startingStrengths):
    """Calculate the remaining strength of a material based on the Lessard-Shokrieh model.

    The Lessard-Shokrieh model accounts for the degradation of material strength due to cyclic loading,
    considering the number of cycles experienced, the maximum stress applied, and material-specific constants.

    .. math::
        R = \\sigma_{max} + \\left( 1 - \\left( \\frac{\\log_{10}(N) - \\log_{10}(0.25)}{\\log_{10}(N_{fail}) - \\log_{10}(0.25)} \\right)^{\\beta_1} \\right)^{\\frac{1}{\\beta_2}} \\cdot (\\sigma_0 - \\sigma_{max})

    Where:

    - :math:`R` is the remaining strength of the material.
    - :math:`\\sigma_{max}` is the maximum stress applied during loading.
    - :math:`N` is the number of cycles the material has undergone.
    - :math:`N_{fail}` is the number of cycles to failure at a given maximum stress.
    - :math:`\\beta_1` and :math:`\\beta_2` are material constants.
    - :math:`\\sigma_0` is the starting strength of the material before any loading.

    :param sigMax: Maximum stress experienced during the loading cycle.
    :param cycles: Number of loading cycles the material has undergone.
    :param cyclesToFailure: Number of cycles to failure at a given maximum stress.
    :param beta1: Material constant
    :param beta2: Material constant
    :param startingStrengths: The starting strength(s) of the material before any loading.
    :return: The remaining strength(s) of the material after considering the effect of cyclic loading.
    """
    remainingStrengths = sigMax + (
        1 - ((np.log10(cycles) - np.log10(0.25)) / (np.log10(cyclesToFailure) - np.log10(0.25))) ** beta1
    ) ** (1 / beta2) * (startingStrengths - sigMax)
    return remainingStrengths


def getCyclesToFailure(sigMax, sigMin, A1, A2, A3, A4):
    """Evaluates S-N equation with p1-p4 for Kt==1. The function is modified accordingly to the given Kt

    Calculates number of cycles to failure according to

        MMPDS (2012): MMPDS Metallic Materials Properties Development and Standardization.
        Chapter 9.6.1.4

    .. math::
        log N_f = A_1+A_2\\cdot log_{10}(\\sigma_{max}\\cdot (1-R)^{A_3}-A_4)

    with

    .. math::
        R = \\frac{\\sigma_{min}}{\\sigma_{max}}

    .. note::

        The calculation of the cycles to failure is highly dependend on

        - Valid test data basis which created A1-A4.
          Caution should be taken, when interpolating and especially extrapolating these values
        - A correct load assumption, since this is not linear.
          Little increases in load can have a significant effect on the cycles to failure

        PLease refer to the literature above for more details.

    :param sigMax: max stress [MPa]
    :param sigMin: min stress [MPa]
    :param A1: see equation
    :param A2: see equation
    :param A3: see equation
    :param A4: see equation
    :return: number of cycles to failure
    """
    sigMin, sigMax = np.array(sigMin), np.array(sigMax)
    if np.any(sigMax < 1e-20):
        raise Tankoh2Error(f"sigMax must be positive but got: {sigMax}")

    R = sigMin / sigMax

    return np.power(10, A1 + A2 * np.log10((sigMax * MPaToPsiFac * (1 - R) ** A3) - A4))


def getFatigueLifeFRPTankLevel(
    materialName,
    pressureMaxOperation,
    pressureMinOperation,
    flightCycles,
    heatUpCycles,
    scatterAircraftLifes,
    vessel,
    symmetricContour,
    useFibreFailure,
    thickShellScaling,
    testPressureAfterFatigue,
):
    """Calculate fatigue life for aircraft applications using LH2 tanks

    :param materialName: name of the material in tankoh2/data OR
        filename of a material json file as defined by µWind
    :param pressureMaxOperation: max operating pressure [MPa]
    :param pressureMinOperation: min operating pressure [MPa]
    :param flightCycles: number of flight cycles
    :param heatUpCycles: number of cycles where a cryo tank is heated up.
        This leads to the pressure cycle [0, pMaxOperation]
    :param scatterAircraftLifes:
    :param vessel: µWind vessel instance
    :param symmetricContour: flag if the tank geometry is symmetric
    :param useFibreFailure: flag if fibre failure or inter fibre failure is used. For fibre failure, only
        the results in 11-direction are used.
    :param thickShellScaling: List of scaling factors for analysis of thick shells
    :return: fatigue life factor. If it is larger than 1, the fatigue life is exceeded
    """
    maxPressures = [pressureMaxOperation] * 2
    minPressures = [pressureMinOperation, 0]
    occurences = np.array([flightCycles, heatUpCycles]) * scatterAircraftLifes

    damageByDirectionElemLayer = getFatigueLifeFRP(
        materialName,
        maxPressures,
        minPressures,
        occurences,
        vessel,
        symmetricContour,
        thickShellScaling,
        testPressureAfterFatigue,
    )
    direction, elem, layer = np.unravel_index(damageByDirectionElemLayer.argmax(), damageByDirectionElemLayer.shape)
    log.info(
        f"Max fatigue damage in direction, elementNr, layerNr: {dirIndexToDirection[direction]}, " f"{elem}, {layer}"
    )
    if useFibreFailure:
        damageByDirectionElemLayer = damageByDirectionElemLayer[:1, :, :]
    return np.max(damageByDirectionElemLayer)


def getFatigueLifeFRP(
    materialName,
    maxPressures,
    minPressures,
    occurences,
    vessel,
    symmetricContour,
    thickShellScaling=None,
    testPressureAfterFatigue=None,
    pressure2stressDict=None,
):
    """calculate stresses according to pressures, calc damage level for each (direction, element, layer),
    assess max damage level, print location of max, output puck failure at test after fatigue if requested

    see getFatigueLifeFRPTankLevel for a description of most parameters

    :param pressure2stressDict: pressureLevel → StressForEachLayerAndElement
        This parameter is only used for testing

    :return: fatigue life factor for each direction, element, layer.
        If it is larger than 1, the fatigue life is exceeded
    """
    materialFilename = materialName if materialName.endswith(".json") else materialName + ".json"
    if not os.path.exists(materialName):
        materialFilename = os.path.join(programDir, "data", materialName)

    material = FrpMaterialFatigueProperties().readMaterial(materialFilename)
    materialMuWind = None
    if pressure2stressDict is None:
        materialMuWind = getMaterialPyChain(materialFilename)
        pressure2stressDict = OrderedDict()
        for pressureMax, pressureMin in zip(maxPressures, minPressures):
            if pressureMax not in pressure2stressDict:
                # stresses are saved as (S11, S22, S12),
                # where each matrix has shape (numberOfElements, numberOfLayers)
                pressure2stressDict[pressureMax] = getStresses(
                    vessel,
                    materialMuWind,
                    pressureMax,
                    thickShellScaling,
                    useIndices=None,
                    symmetricContour=symmetricContour,
                )
            if pressureMin not in pressure2stressDict:
                pressure2stressDict[pressureMin] = getStresses(
                    vessel,
                    materialMuWind,
                    pressureMin,
                    thickShellScaling,
                    useIndices=None,
                    symmetricContour=symmetricContour,
                )

    critCycles = getCyclesToFailureAllDirectionsFRP(material, maxPressures, minPressures, pressure2stressDict)
    occurenceArray = _extendOccurences(occurences, critCycles.shape)

    if testPressureAfterFatigue and np.all(occurenceArray[0][0] < critCycles[0][0]):
        if not materialMuWind:
            materialMuWind = getMaterialPyChain(materialFilename)

        beta1 = material.beta_1_11t
        beta2 = material.beta_2_11t
        localFVC = getLocalFVC(vessel, symmetricContour=symmetricContour)
        startingStrengths = materialMuWind.puckProperties.R_1_t * localFVC / materialMuWind.phi
        remainingStrengths = lessardShokriehRemainingStrength(
            pressure2stressDict[(maxPressures[0])][0],
            occurenceArray[0][0],
            critCycles[0][0],
            beta1,
            beta2,
            startingStrengths,
        )
        stresses = getStresses(
            vessel,
            materialMuWind,
            testPressureAfterFatigue,
            thickShellScaling,
            useIndices=None,
            symmetricContour=symmetricContour,
        )
        S_11 = stresses[0]
        Puck_FF = S_11 / remainingStrengths
        log.info(
            f"Maximum Puck FF at test pressure {testPressureAfterFatigue} MPa after {occurences[0]} cycles to {pressureMax} MPa: {np.max(Puck_FF)}"
        )

    damageByDirectionElementLayer = stressLifeMinerRule(occurenceArray, critCycles, sumAxis=1)

    return damageByDirectionElementLayer


def getCyclesToFailureAllDirectionsFRP(material, maxPressures, minPressures, p2sigDict, usedDirections=directions):
    """Calculates the number of cycles to failure

    see getFatigueLifeFRPTankLevel for a description of most parameters

    :return: number cycles to failure for each direction, pressureCycle, element and layer
    """
    critCycles = []  # shape (direction, cycleCase, numberOfElements, numberOfLayers)
    for direction in usedDirections:
        critCyclesDir = []
        for pressureMax, pressureMin in zip(maxPressures, minPressures):
            directionIndex = directions[direction]

            stressUpper = p2sigDict[pressureMax][directionIndex]
            numberOfElements, numberOfLayers = stressUpper.shape
            stressUpper = stressUpper.flatten()
            stressLower = p2sigDict[pressureMin][directionIndex].flatten()

            # swap stress entries if stress upper is not absolute higher stress level
            stresses = np.array([stressUpper, stressLower])
            stresses = np.sort(stresses, axis=0)

            df = pd.DataFrame(stresses.T, columns=["stressLower", "stressUpper"])

            df = addCyclesToFailureFRP(df, material, direction)
            Nf = df["Nf"]

            Nf = Nf.to_numpy().reshape((numberOfElements, numberOfLayers))
            critCyclesDir.append(Nf)
        critCycles.append(critCyclesDir)
    critCycles = np.array(critCycles)
    log.debug(f"NaN count: {np.isnan(critCycles).sum()}")
    return critCycles


def addCyclesToFailureFRP(upperLowerStressDf, material, direction):
    """
    :param upperLowerStressDf: dataframe with at least these columns: "stressUpper", "stressLower"
    :param material: instance of tankoh2.mechanics.material.FrpMaterialProperties
    :param direction: int, direction of the stresses to be added

    """
    df = upperLowerStressDf
    tensileStrength, compressionStrength = material.getStrengths(direction)
    df = addMeanstressesAndAmplitudesNorm(df, tensileStrength)
    strengthRatio = compressionStrength / tensileStrength
    u, v = material.getUV(direction)
    df["fatigueStressFactor"] = getFatigueStressFactor(
        df["stressAmplitudeNorm"], df["meanStressNorm"], strengthRatio, u, v
    )
    C, D = material.getCD(direction)
    df["Nf"] = masterCurveInv(df["fatigueStressFactor"], C, D)
    return df


def _extendOccurences(occurences, critCyclesShape):
    """Creates an array of occurences based on the shape of the array describing the number of critical cycles

    The occurences have index 1 of the targeted array. len(occurences) must be equal to critCyclesShape[1].
    This method swaps axes to perform element wise multiplication which is always done on the last index by
    numpy.

    :param occurences: list with number of occurences
    :param critCyclesShape: shape of the crit cycles array (direction, pressureCycle, element, layer)
    :return: array with occurences (direction, pressureCycle, element, layer)

    >>> occurences = [1,10]
    >>> critCyclesShape = (1,2,3,4)

    >>> _extendOccurences(occurences, critCyclesShape)
    array([[[[ 1.,  1.,  1.,  1.],
             [ 1.,  1.,  1.,  1.],
             [ 1.,  1.,  1.,  1.]],
    <BLANKLINE>
            [[10., 10., 10., 10.],
             [10., 10., 10., 10.],
             [10., 10., 10., 10.]]]])
    """
    occurencesArray = np.ones(critCyclesShape)

    occurencesArraySwap = np.swapaxes(occurencesArray, 1, 3)
    # occurencesArraySwap is only a view on occurencesArray, so no swap back is needed
    occurencesArraySwap *= occurences
    return occurencesArray


def masterCurveLog10(Nf, C_Log10, D):
    """Defines log 10 based the fatigue master curve

    .. math::
        log_{10}f = log_{10}C + D \\cdot log_{10}N_f
    """
    return C_Log10 + D * np.log10(Nf)


def masterCurve(Nf, C, D):
    """Defines the fatigue master curve

    .. math::
        f = C\\cdot N_f^D
    """
    return C * Nf**D


def masterCurveInv(f, C, D):
    """

    .. math::
        criticalCycles = \\frac{f}{C}^\\frac{1}{D}

    :param f:
    :param C:
    :param D:
    :return:
    """
    return (f / C) ** (1 / D)


def woehler(cycles, A, B):
    """wohler equation from eq. 5.20

    :return: sig_max
    """
    return A * cycles**B


def woehlerLog(cyclesLog, Alog, B):
    """logarithmic form of eq. 5.20

    :return: log(sig_max)
    """
    return Alog + B * cyclesLog


def woehlerLogCycles(logCycles, A, B):
    """modified wohler equation from eq. 5.20

    :return: sig_max
    """
    return A * np.exp(logCycles * B)


def addMeanstressesAndAmplitudesNorm(testDataDf, tensileStrength):
    """Calculates normalized stress amplitude and normalized mean stress by woehler curve

    Lüders - Mehrskalige Betrachtung des Ermüdungsverhaltens thermisch zyklierter Faserkunststoffverbunde - 2020
    Chapter 8.1.2

    .. math::
        normAmplitude = \\frac{(\\sigma_{Max} - \\sigma_{Min}} {2 \\cdot tensileStrength}

    .. math::
        normMeanstress = \\frac{(\\sigma_{Max} + \\sigma_{Min}} {2 \\cdot tensileStrength}

    :param testDataDf: dataframe at least with columns ['stressUpper', 'stressLower']
    :param tensileStrength: tensileStrength of material that is evaluated
    :return: extends testDataDf with columns ['meanStressNorm', 'stressAmplitudeNorm']
    """
    df = testDataDf
    df["meanStressNorm"] = df.loc[:, ["stressUpper", "stressLower"]].mean(axis=1) / tensileStrength
    df["stressAmplitudeNorm"] = (df["stressUpper"] - df["stressLower"]) / 2 / tensileStrength
    return df


def getFatigueStressFactor(a, q, c, u, v):
    """according to eq 8.7

    Lüders - Mehrskalige Betrachtung des Ermüdungsverhaltens thermisch zyklierter Faserkunststoffverbunde - 2020
    Chapter 8.1.2

    .. math::
        f = \\frac{normAmplitude} {(1 - normMeanstress)^u \\cdot (c + normMeanstress)^v}

    :param a: normalized stress amplitude
    :param q: normalized mean stress
    :param c: strength ratio : compressionStrength / tensileStrength
    :param u: fitting parameter
    :param v: fitting parameter
    :return: fatique stress factor
    """
    return a / ((1 - q) ** u * (c + q) ** v)
