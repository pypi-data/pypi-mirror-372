# SPDX-FileCopyrightText: 2023 German Aerospace Center (DLR)
#
# SPDX-License-Identifier: MIT

"""optimizers for various target functions

- optimize frition to achieve a target polar opening
- optimize shift for hoop layers
- optimize layup
"""

import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import differential_evolution, minimize, minimize_scalar

from tankoh2 import log
from tankoh2.design.winding.contour import calculateWindability
from tankoh2.design.winding.solver import (
    getMaxPuckByAngle,
    getMaxPuckByShift,
    getMaxPuckLocalPuckMassIndexByAngle,
    getMaxPuckLocalPuckMassIndexByShift,
    getWeightedTargetFuncByAngle,
)
from tankoh2.design.winding.winding import (
    getNegAngleAndPolarOpeningDiffByAngle,
    getPolarOpeningDiffByAngle,
    getPolarOpeningDiffByAngleBandMid,
    getPolarOpeningDiffHelical,
    getPolarOpeningDiffHelicalUsingLogFriction,
    getPolarOpeningDiffHelicalUsingNegativeLogFriction,
    getPolarOpeningDiffHoop,
    getPolarOpeningXDiffHoop,
    isFittingLayer,
    windHoopLayer,
    windLayer,
)
from tankoh2.geometry.geoutils import getRadiusByShiftOnContour
from tankoh2.service.exception import Tankoh2Error
from tankoh2.settings import settings

_lastMinAngle = None


def calculateMinAngle(vessel, targetPolarOpening, layerNumber, bandWidth):
    if settings.useClairaultAngle:
        return clairaultAngle(vessel, targetPolarOpening, layerNumber, bandWidth)
    else:
        angle, funVal, iterations = optimizeAngle(
            vessel, targetPolarOpening, layerNumber, bandWidth, getPolarOpeningDiffByAngleBandMid
        )
        return angle


def optimizeAngle(vessel, targetPolarOpening, layerNumber, bandWidth, targetFunction=getPolarOpeningDiffByAngle):
    """optimizes the angle of the actual layer to realize the desired polar opening

    :param vessel: vessel object
    :param targetPolarOpening: polar opening radius that should be realized
    :param layerNumber: number of the actual layer
    :param bandWidth: total width of the band (only used for tf getPolarOpeningDiffByAngleBandMid)
    :param targetFunction: target function to be minimized
    :return: 3-tuple (resultAngle, polar opening, number of runs)
    """

    global _lastMinAngle
    angleBounds = (1.0, settings.maxHelicalAngle) if _lastMinAngle is None else (_lastMinAngle - 1, _lastMinAngle)
    tol = 1e-2
    if targetFunction is getPolarOpeningDiffByAngleBandMid:
        args = [vessel, layerNumber, targetPolarOpening, bandWidth]
    else:
        args = [vessel, layerNumber, targetPolarOpening]
    while angleBounds[0] < 30:
        try:
            popt = minimize_scalar(
                targetFunction,
                method="bounded",
                bounds=angleBounds,
                args=args,
                options={"maxiter": 1000, "disp": 1, "xatol": tol},
            )
            break
        except RuntimeError as e:
            # if minBound too small, µWind may raise an error "Polar Opening too small - Thickness Error!"
            if str(e) == "Polar Opening too small - Thickness Error!":
                angleBounds = angleBounds[0] + 0.1, angleBounds[1] + 1
                log.info("Min angle bound of optimization was too low - increased by one deg.")
            else:
                raise
    if not popt.success:
        raise Tankoh2Error("Could not find optimal solution")
    plotTargetFun = False
    if plotTargetFun:
        angles = np.linspace(angleBounds[0], 10, 200)
        tfValues = [targetFunction(angle, args) for angle in angles]
        fig, ax = plt.subplots()
        ax.plot(angles, tfValues, linewidth=2.0)
        plt.show()
    angle, funVal, iterations = popt.x, popt.fun, popt.nfev
    if popt.fun > 1 and targetFunction is getPolarOpeningDiffByAngle:
        # desired polar opening not met. This happens, when polar opening is near fitting.
        # There is a discontinuity at this point. Switch target function to search from the fitting side.
        angle, funVal, iterations = optimizeAngle(
            vessel, targetPolarOpening, layerNumber, getNegAngleAndPolarOpeningDiffByAngle
        )
    else:
        windLayer(vessel, layerNumber, angle)
    log.debug(f"Min angle {angle} at funcVal {funVal}")
    _lastMinAngle = angle
    return angle, funVal, iterations


def clairaultAngle(vessel, targetPolarOpening, layerNumber, bandWidth):
    """finds the angle of a layer to realize the desired polar opening using the clairault relation

    :param vessel: vessel object
    :param targetPolarOpening: polar opening radius that should be realized
    :param layerNumber: number of the actual layer
    :param bandWidth: total width of the band (only used for tf getPolarOpeningDiffByAngleBandMid)
    :return: angle: cylinder angle that leads to target polar opening according to clairault relation
    """

    windLayer(vessel, layerNumber, 90)
    r = vessel.getVesselLayer(layerNumber).getInnerMandrel1().getRArray()[0]
    bandMidPolarOpening = getRadiusByShiftOnContour(
        vessel.getVesselLayer(layerNumber).getInnerMandrel1().getRArray(),
        vessel.getVesselLayer(layerNumber).getInnerMandrel1().getLArray(),
        targetPolarOpening,
        -bandWidth / 2,
    )
    angle = np.rad2deg(np.arcsin(bandMidPolarOpening / r))
    while True:
        if windLayer(vessel, layerNumber, angle) < np.inf:
            break
        else:
            angle += 0.01

    return angle


def minimizeUtilization(bounds, targetFunction, optKwArgs, localOptimization=False):
    """Minimizes puck (inter) fibre failure criterion in defined bounds (angles or hoop shifts)

    This method calls the optimization routines. There is a distinction between local and global
    optimization.

    :param bounds: iterable with 2 items: lower and upper bound
    :param targetFunction: function to be used as target function
    :param optKwArgs: dict with these items:
        - vessel: µWind vessel instance
        - layerNumber: actual layer (zero based counting)
        - materialMuWind: µWind material instance
        - burstPressure: burst pressure in MPa
        - useIndices: list of element indicies that will be used for stress and puck evaluation
        - useFibreFailure: flag if fibrefailure or interfibrefailure is used
        - verbosePlot: flag if additional plot output values should be created
        - symmetricContour: flag if the conour is symmetric or unsymmetric
        - elemIdxPuckMax: index of the most critical element (puck) before adding the actual layer
        - elemIdxBendMax: index of the most critical element (strain diff) before adding the actual layer
        - targetFuncScaling: scaling of the target function constituents for the weighted sum
    :param localOptimization: can be (True, False, 'both'). Performs a local or global optimization. If 'both'
        is selected, both optimizations are performed and the result with the lowest function value is used.
    :return: 4-tuple
        - x optimization result
        - funVal: target function value at x
        - iterations: number of iterations used
        - tfPlotVals: plot values of the target function if verbosePlot==True else None

    """

    helicalTargetFunctions = [getWeightedTargetFuncByAngle, getMaxPuckByAngle]
    verbosePlot = optKwArgs["verbosePlot"]
    if verbosePlot:
        tfX = np.linspace(*bounds, 50)
        targetFunctionPlot = (
            getMaxPuckLocalPuckMassIndexByAngle
            if targetFunction in helicalTargetFunctions
            else getMaxPuckLocalPuckMassIndexByShift
        )
        tfPlotVals = [targetFunctionPlot(angleParam, optKwArgs) for angleParam in tfX]
        isInfArray = [val[0] == np.inf for val in tfPlotVals]
        tfX = np.array([x for x, isInf in zip(tfX, isInfArray) if not isInf])
        tfPlotVals = np.array([val for val, isInf in zip(tfPlotVals, isInfArray) if not isInf]).T
        if targetFunction in [getMaxPuckByAngle, getMaxPuckByShift]:
            tfPlotVals = np.append(tfPlotVals[:1], tfPlotVals[-1:], axis=0)
        tfPlotVals = np.append([tfX], tfPlotVals, axis=0)
    else:
        tfPlotVals = None

    if localOptimization not in [True, False, "both"]:
        raise Tankoh2Error("no proper value for localOptimization")
    tol = 1e-3
    if localOptimization is True or localOptimization == "both":
        popt_loc = minimize(
            targetFunction,
            bounds[:1],
            bounds=[bounds],  # bounds of the angle or hoop shift
            args=optKwArgs,
            tol=tol,
        )
        if localOptimization is True:
            popt = popt_loc
    if localOptimization is False or localOptimization == "both":
        popt_glob = differential_evolution(
            targetFunction, bounds=(bounds,), args=[optKwArgs], atol=tol * 10, seed=settings.optimizerSeed
        )
        if localOptimization is False:
            popt = popt_glob
    if localOptimization == "both":
        popt = popt_loc if popt_loc.fun < popt_glob.fun else popt_glob
        if not popt.success:
            popt = popt_loc if popt_loc.fun > popt_glob.fun else popt_glob
    if not popt.success:
        from tankoh2.service.plot.muwind import plotTargetFunc

        errMsg = "Could not find optimal solution"
        log.error(errMsg)
        plotTargetFunc(
            None, tfPlotVals, [(popt.x, 0)], "label Name", ([0] * 4, optKwArgs["targetFuncScaling"]), None, None, True
        )
        raise Tankoh2Error(errMsg)
    x, funVal, iterations = popt.x, popt.fun, popt.nfev
    if hasattr(x, "__iter__"):
        x = x[0]
    vessel, layerNumber = optKwArgs["vessel"], optKwArgs["layerNumber"]
    if targetFunction in helicalTargetFunctions:
        windLayer(vessel, layerNumber, x)
    else:
        windHoopLayer(vessel, layerNumber, x)

    return x, funVal, iterations, tfPlotVals


def optimizeFriction(vessel, wendekreisradius, layerindex):
    # popt, pcov = curve_fit(getPolarOpeningDiff, layerindex, wk_goal, bounds=([0.], [1.]))
    #
    # popt  = minimize(getPolarOpeningDiff, x0 = (1.), method = 'BFGS', args=[vessel, wendekreisradius],
    #                   options={'gtol': 1e-6, 'disp': True})
    tol = 1e-7
    popt = minimize_scalar(
        getPolarOpeningDiffHelical,
        method="bounded",
        bounds=[0.0, 1e-5],
        args=[vessel, wendekreisradius, layerindex],
        options={"maxiter": 1000, "disp": 1, "xatol": tol},
    )
    friction = popt.x
    return friction, popt.fun, popt.nfev


def optimizeHoopShift(vessel, krempenradius, layerindex):
    popt = minimize_scalar(
        getPolarOpeningDiffHoop, method="brent", options={"xtol": 1e-2}, args=[vessel, krempenradius, layerindex]
    )
    shift = popt.x
    return shift, popt.fun, popt.nit


def optimizeHoopShiftForPolarOpeningX(vessel, polarOpeningX, layerindex):
    popt = minimize_scalar(
        getPolarOpeningXDiffHoop, method="brent", options={"xtol": 1e-2}, args=[vessel, polarOpeningX, layerindex]
    )
    shift = popt.x
    return shift, popt.fun, popt.nit


# write new optimasation with scipy.optimize.differential_evolution


def optimizeFrictionGlobal_differential_evolution(vessel, wendekreisradius, layerindex):
    """
    optimize friction value for given polarOpening
    using global optimizer scipy.optimize.differential_evolution
    """
    tol = 1e-15
    args = (vessel, wendekreisradius, layerindex)
    popt = differential_evolution(
        getPolarOpeningDiffHelicalUsingLogFriction,
        bounds=[(-10, -4)],
        args=[args],
        strategy="best1bin",
        mutation=1.9,
        recombination=0.9,
        seed=settings.optimizerSeed,
        tol=tol,
        atol=tol,
    )
    friction = popt.x
    return 10**friction, popt.fun, popt.nfev


def optimizeNegativeFrictionGlobal_differential_evolution(vessel, wendekreisradius, layerindex):
    """
    optimize friction value for given polarOpening
    using global optimizer scipy.optimize.differential_evolution
    """
    tol = 1e-15
    args = (vessel, wendekreisradius, layerindex)
    popt = differential_evolution(
        getPolarOpeningDiffHelicalUsingNegativeLogFriction,
        bounds=[(-10, -3.6)],
        args=[args],
        strategy="best1bin",
        mutation=1.9,
        recombination=0.9,
        seed=settings.optimizerSeed,
        tol=tol,
        atol=tol,
    )
    friction = popt.x
    return -1.0 * abs(10**friction), popt.fun, popt.nfev


def findValidWindingAngle(vessel, layerNumber, angle, minimumPolarOpeningRadius, contourSmoothingBorders=None):
    """find the nearest angle which gives a valid winding pattern

    :param vessel: µWind vessel instance
    :param layerNumber: number of the layer to adjust (0-based indexed)
    :param angle: angle of the layer to adjust [°].
    :param polarOpeningRadius: polarOpeningRadius as minimum for the search
    :param contourSmoothingBorders: if contour smoothing borders are given, then windability is assessed
    :return: nearest angle which gives a valid winding pattern
    """

    def targetfunction(currentAngle):
        if settings.maxHelicalAngle < currentAngle < minAngle:
            return 1e6
        polarOpening = windLayer(vessel, layerNumber, currentAngle)
        if np.isinf(polarOpening):
            return 1e6
        if contourSmoothingBorders:
            windability = calculateWindability(
                vessel, layerNumber, settings.maxThicknessDerivative, contourSmoothingBorders
            )
            if windability > 1:
                return 1e6
        layer = vessel.getVesselLayer(layerNumber)
        layerResults = layer.getVesselLayerPropertiesSolver().getWindingLayerResults()
        progress = layerResults.progressNPerCycle
        cycles = layerResults.cycles
        if cycles == attemptCycles:
            # If number of cycles has not changed with this angle,
            # Return difference between current winding progress and integer goal
            return abs(progress - patternProgress)
        else:
            return 1e6

    def resetSearch():
        if initialProgress - lowerPatternProgress < 0.5:
            patternProgress = lowerPatternProgress
            step = 1
        else:
            patternProgress = lowerPatternProgress + 1
            step = -1
        lowerBound = max(
            np.rad2deg(np.arccos(min([max([(attemptCycles * bandWidth) / (radius * 2 * np.pi), 0]), 1]))), minAngle
        )
        upperBound = min(
            np.rad2deg(np.arccos(min([max([((attemptCycles - 1) * bandWidth) / (radius * 2 * np.pi), 0]), 1]))),
            settings.maxHelicalAngle,
        )
        return patternProgress, step, lowerBound, upperBound

    minAngle = calculateMinAngle(vessel, minimumPolarOpeningRadius, layerNumber, 5)
    # Check if it's a fitting layer
    windLayer(vessel, layerNumber, angle)
    fittingLayer = isFittingLayer(vessel, layerNumber)
    # Get initial values
    layer = vessel.getVesselLayer(layerNumber)
    initialLayerResults = layer.getVesselLayerPropertiesSolver().getWindingLayerResults()
    initialProgress = initialLayerResults.progressNPerCycle
    initialCycles = initialLayerResults.cycles
    initialOverlap = initialLayerResults.bandOverlap
    bandWidth = initialLayerResults.cylinderBandWidth
    lowerPatternProgress = int(np.floor(initialProgress))
    radius = layer.getInnerMandrel1().getRArray()[0]

    # Try to reach closest integer progress value
    patternFound = False
    failedToFindPattern = 0
    attemptCycles = initialCycles
    patternProgress, step, lowerBound, upperBound = resetSearch()

    if abs(initialProgress - patternProgress) < 0.05 and np.gcd(patternProgress % attemptCycles, attemptCycles) == 1:
        log.debug(f"Angle was {angle}, already is windable")
        return angle

    while not patternFound:
        # Must not have common denominators with number of cycles to be a valid pattern
        if np.gcd(patternProgress % attemptCycles, attemptCycles) == 1:
            res = minimize_scalar(targetfunction, bounds=(lowerBound, upperBound), method="bounded")
            if res.fun < 0.05:
                patternFound = True
        if not patternFound:
            # Try next progress value
            patternProgress = patternProgress + step
            if step < 0:
                step = -step + 1
            else:
                step = -step - 1
            failedToFindPattern = failedToFindPattern + 1
            if failedToFindPattern == 7:
                # If failed 7 times to reach valid integer pattern with current amount of cycles,
                # try again with 1 more or less cycle
                if initialOverlap > 1 / initialCycles / 2:
                    attemptCycles = initialCycles - 1  # high overlap, try with one less cycle
                else:
                    attemptCycles = initialCycles + 1  # low overlap, try with one more cycle
                patternProgress, step, lowerBound, upperBound = resetSearch()
                if upperBound < lowerBound:
                    failedToFindPattern = 14
            if failedToFindPattern == 14:
                # If failed 14 times to reach valid integer pattern with current amount of cycles,
                # try again with 1 less or more cycle
                if initialOverlap > 1 / initialCycles / 2:
                    attemptCycles = initialCycles + 1  # high overlap, try with one less cycle
                else:
                    attemptCycles = initialCycles - 1  # low overlap, try with one more cycle
                patternProgress, step, lowerBound, upperBound = resetSearch()
                if upperBound < lowerBound:
                    failedToFindPattern = 21
            if failedToFindPattern == 21:
                break

    if patternFound:
        log.debug(f"Angle was {angle}, Found windable Angle {res.x}")
        return res.x
    else:
        if fittingLayer:
            log.debug(f"Angle remains {angle}, Could not find windable angle which reaches the fitting")
        else:
            log.debug(f"Angle remains {angle}, Could not find windable angle")
        return angle
