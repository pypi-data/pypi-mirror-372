# SPDX-FileCopyrightText: 2023 German Aerospace Center (DLR)
#
# SPDX-License-Identifier: MIT

"""control a tank optimization"""

import copy
import os
from datetime import datetime

from patme.service.systemutils import getRunDir

from tankoh2 import log, programDir
from tankoh2.control.control_metal import createDesign as createDesignMetal
from tankoh2.control.control_winding import createDesign as createDesignWinding
from tankoh2.control.genericcontrol import (
    parseConfigFile,
    parseDesignArgs,
    saveParametersAndResults,
)


def updateKwargsForOuterVessel(kwargs):
    """

    :param kwargs: dict which will be updated to suit for outer vessel analysis
    :return: None, input dict will be modified
    """

    kwargs["useBucklingCriterion"] = True
    kwargs["pressure"] = 0.1  #  0.075  # abs pressure (std atmosphere in 34000ft) - pressure(groundlevel)
    kwargs["useHydrostaticPressure"] = False
    kwargs["minPressure"] = 0  # used in combination with operationalCycles
    kwargs["zeroPressureCycles"] = 0
    kwargs["linerThickness"] = 0
    kwargs["insulationThickness"] = 0
    kwargs["fairingThickness"] = 0


def createDesign(**kwargs):
    """Create a winding design

    For a list of possible parameters, please refer to tankoh2.design.existingdesigns.allDesignKeywords
    """
    startTime = datetime.now()
    # #########################################################################################
    # SET Parameters of vessel
    # #########################################################################################
    windingOrMetal = kwargs.get("windingOrMetal", "winding")

    if "configFile" in kwargs and kwargs["configFile"] is not None:
        configArgs = parseConfigFile(kwargs["configFile"])
        if "windingOrMetal" in configArgs:
            windingOrMetal = configArgs["windingOrMetal"].lower()
        if "runDir" in configArgs:
            baseRunDir = configArgs["runDir"]
        else:
            baseRunDir = getRunDir(kwargs.get("tankname", ""), basePath=os.path.join(programDir, "tmp"))

    useMilliSeconds = windingOrMetal == "metal"
    callMethod = createDesignMetal if windingOrMetal == "metal" else createDesignWinding

    log.info("INNER VESSEL")
    kwargsInner = copy.deepcopy(kwargs)
    runDirInner = getRunDir(
        "innerVessel_" + kwargsInner.get("tankname", ""), basePath=baseRunDir, useMilliSeconds=useMilliSeconds
    )
    kwargsInner["useBucklingCriterion"] = False
    if (
        "domeContourFile" in kwargsInner
        or "dome2ContourFile" in kwargsInner
        or "domeContour" in kwargsInner
        or "dome2Contour" in kwargsInner
    ):
        raise NotImplementedError(
            f"The parameters [domeContourFile, dome2ContourFile, domeContour, dome2Contour] are not supported with calculating inner and outer vessel (parameter singleOrDoubleVessels == double)"
        )

    kwargsInner["runDir"] = runDirInner
    resultsInnerVessel = callMethod(**kwargsInner)
    resultsInnerVessel = {"innerVessel_" + key: value for key, value in resultsInnerVessel.items()}

    log.info("OUTER VESSEL")
    runDirOuter = getRunDir(
        "outerVessel_" + kwargs.get("tankname", ""), basePath=baseRunDir, useMilliSeconds=useMilliSeconds
    )
    kwargsOuter, nonDefaultArgs, domeObjects = parseDesignArgs(kwargs)
    updateKwargsForOuterVessel(kwargsOuter)

    # increase diameter and length of the tank
    vesselPitch = kwargsOuter["vesselPitch"]
    kwargsOuter["lcyl"] += vesselPitch * 2
    kwargsOuter["dcyl"] += vesselPitch * 2

    kwargsOuter.pop("lcylByR", None)
    kwargsOuter.pop("tankLength", None)
    kwargsOuter.pop("volume", None)
    kwargsOuter.pop("h2Mass", None)

    kwargsOuter["runDir"] = runDirOuter
    resultsOuterVessel = callMethod(**kwargsOuter)
    resultsOuterVessel = {"outerVessel_" + key: value for key, value in resultsOuterVessel.items()}

    # POSTPROCESSING
    duration = datetime.now() - startTime
    results = {
        "totalMass": resultsInnerVessel["innerVessel_totalMass"] + resultsOuterVessel["outerVessel_totalMass"],
        "duration": duration,
    }
    results.update(resultsInnerVessel)
    results.update(resultsOuterVessel)

    saveParametersAndResults(baseRunDir, nonDefaultArgs, None, results)

    log.info(f"runtime {duration.seconds} seconds")
    log.info(f"FINISHED")

    return results


if __name__ == "__main__":
    if 1:
        # params = parameters.defaultUnsymmetricDesign.copy()
        params = {"configFile": "hytazer_smr_iff_2.0bar_final_metal.yaml"}
        createDesign(**params)
