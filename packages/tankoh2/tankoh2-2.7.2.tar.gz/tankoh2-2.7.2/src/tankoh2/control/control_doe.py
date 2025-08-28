# SPDX-FileCopyrightText: 2023 German Aerospace Center (DLR)
#
# SPDX-License-Identifier: MIT

"""create DOEs and execute design workflow

Caution:
This module requires fa_pytuils and delismm!
Please contatct the developers for these additional packages.
"""
import csv
import os
from argparse import ArgumentParser
from collections import OrderedDict
from datetime import datetime
from multiprocessing import cpu_count

import numpy as np
from delismm.control.tank import getKrigings
from delismm.model.customsystemfunction import AbstractTargetFunction, BoundsHandler
from delismm.model.doe import AbstractDOE, DOEfromFile, FullFactorialDesign, LatinizedCentroidalVoronoiTesselation
from delismm.model.samplecalculator import getY
from patme.service.systemutils import getRunDir

import tankoh2
from tankoh2 import log, programDir
from tankoh2.arguments import resultKeyToUnitDict
from tankoh2.control.control_metal import createDesign as createDesignMetal
from tankoh2.control.control_winding import createDesign as createDesignWinding
from tankoh2.design.existingdesigns import DLightDOE, vphDesign1_isotensoid
from tankoh2.service.exception import Tankoh2Error
from tankoh2.service.plot.doeplot import plotExact2GeometryRange, plotGeometryRange

useMetal = False
resultNames = [
    "shellMass",
    "linerMass",
    "insulationMass",
    "fairingMass",
    "totalMass",
    "volume",
    "h2Mass",
    "area",
    "lengthAxial",
    "numberOfLayers",
    "cylinderThickness",
    "maxThickness",
    "reserveFactor",
    "gravimetricIndex",
    "stressRatio",
    "hoopHelicalRatio",
    "iterations",
]
if useMetal:
    resultNames = [
        "totalMass",
    ]

allowedDesignNames = {
    "dlight",
    "exact_cyl_isotensoid",
    "exact_conical_isotensoid",
    "vph2",
    "exact2",
    "exact2_large_designspace",
}
argParser = ArgumentParser()
argParser.add_argument(
    "--adaptExact2ParameterKey",
    help="parameter key to adapt in the design space",
    default="",
)
argParser.add_argument(
    "--designName",
    help=f"name of the design and bounds to return. Not case sensitive! Allowed names: {allowedDesignNames}",
    default="exact2",
)
argParser.add_argument(
    "--resumeFolder",
    help=f"path to a folder with sampleY results that should be resumed",
    default="",
)
parsedOptions = argParser.parse_args()
adaptExact2ParameterKey = parsedOptions.adaptExact2ParameterKey
if adaptExact2ParameterKey.lower() == "none":
    adaptExact2ParameterKey = ""
designName = parsedOptions.designName.lower()
resumeFolder = parsedOptions.resumeFolder


class TankWinder(AbstractTargetFunction):
    """"""

    name = "tank winder"

    def __init__(self, lb, ub, runDir, designKwargs):
        """"""
        AbstractTargetFunction.__init__(self, lb, ub, resultNames=resultNames)
        if 0:
            self.doParallelization = []
        else:
            self.doParallelization = ["local"]
            import matplotlib

            # use Agg as backend instead of tkinter.
            # tkinter is not thread safe and causes problems with parallelization when creating plots
            # on the other hand Agg is non-interactive, and thus cannot be shown plt.show()
            matplotlib.use("Agg")

        self.runDir = runDir
        self.allowFailedSample = True
        self.designKwargs = designKwargs
        """keyword arguments defining constants for the tank design"""
        self.asyncMaxProcesses = int(np.ceil(cpu_count() * 2 / 3))

    def _call(self, parameters):
        """call function for the model"""
        runDir = getRunDir(basePath=os.path.join(self.runDir), useMilliSeconds=True)
        paramDict = OrderedDict(zip(self.parameterNames, parameters))
        inputDict = OrderedDict()
        inputDict.update(self.designKwargs)
        inputDict.update(paramDict)
        inputDict["minPressure"] = inputDict["pressure"] / 2

        inputDict["runDir"] = runDir

        resultDict = createDesignWinding(**inputDict)
        result = [resultDict[key] for key in self.resultNames]

        return result

    def getNumberOfNewJobs(self):
        return self.asyncMaxProcesses


class TankMetal(AbstractTargetFunction):
    """"""

    name = "tank winder"

    def __init__(self, lb, ub, runDir, designKwargs):
        """"""
        AbstractTargetFunction.__init__(self, lb, ub, resultNames=resultNames)

        self.designKwargs = designKwargs

    def _call(self, parameters):
        """call function for the model"""
        paramDict = OrderedDict(zip(self.parameterNames, parameters))
        inputDict = OrderedDict()
        inputDict.update(self.designKwargs)
        inputDict.update(paramDict)
        inputDict["minPressure"] = inputDict["pressure"] / 2

        resultDict = createDesignMetal(**inputDict)
        result = [resultDict[key] for key in self.resultNames]

        return result


def _getExtendedBounds(lb, ub, keys):
    """Extends bounds of all keys in keys"""
    for key in keys:
        lb[key], ub[key] = ub[key], ub[key] + (ub[key] - lb[key])
    return lb, ub


def getDesignAndBounds(name, adaptExact2ParameterKey=None):
    """returns base design properties (like in existingdesigns) of a tank and upper/lower bounds for the doe

    :param name: name of the design and bounds to return. Not case sensitive!
    :return: designKwargs, lowerBoundDict, upperBoundDict, numberOfSamples
    """
    if name not in allowedDesignNames:
        raise Tankoh2Error(f"Parameter name={name} unknown. Allowed names: {allowedDesignNames}")
    name = name.lower()
    numberOfSamples = 101
    units = ["[mm]", "[mm]", "[MPa]"]
    doeClass = LatinizedCentroidalVoronoiTesselation
    if name == "dlight":
        lb = OrderedDict([("dcyl", 100.0), ("lcyl", 800), ("pressure", 50)])  # [mm, mm , MPa]
        ub = OrderedDict([("dcyl", 800.0), ("lcyl", 5000), ("pressure", 200)])
        designKwargs = DLightDOE
    if name == "exact2" or name == "exact2_large_designspace":
        lb = OrderedDict([("dcyl", 800.0), ("lcylByR", 0.1), ("pressure", 0.05)])
        ub = OrderedDict([("dcyl", 4800.0), ("lcylByR", 10.1), ("pressure", 0.65)])
        if name == "exact2_large_designspace":
            ub = {key: value + (value - lb[key]) for key, value in ub.items()}
        if adaptExact2ParameterKey:
            # extend parameter space in one parameter direction
            lb, ub = _getExtendedBounds(lb, ub, [adaptExact2ParameterKey])
            numberOfSamples = 21
        units = ["[mm]", "[-]", "[MPa]"]
        metalStr = "_metal" if useMetal else ""
        designKwargs = OrderedDict([("configFile", f"hytazer_smr_iff_2.0bar_final{metalStr}.yaml")])
        designKwargs["windingOrMetal"] = "metal" if 1 else "winding"
        if designKwargs["windingOrMetal"] == "metal":
            designKwargs["materialName"] = "alu6061T6"
    elif name == "exact_cyl_isotensoid":
        lb = OrderedDict([("dcyl", 1000.0), ("lcyl", 150), ("pressure", 0.1)])  # [mm, mm , MPa]
        ub = OrderedDict([("dcyl", 4000.0), ("lcyl", 3000), ("pressure", 1)])
        designKwargs = vphDesign1_isotensoid.copy()
        designKwargs["targetFuncWeights"] = [1.0, 0.2, 0.0, 0.0, 0, 0]
        designKwargs["verbosePlot"] = True
        designKwargs["numberOfRovings"] = 12
        designKwargs.pop("lcyl")
        designKwargs.pop("safetyFactor")
    elif name == "exact_conical_isotensoid":
        units = ["[mm]", "[mm]", "[MPa]", "[-]", "[-]"]
        lb = OrderedDict([("dcyl", 1000.0), ("lcyl", 150), ("pressure", 0.1), ("alpha", 0.2), ("beta", 0.5)])
        ub = OrderedDict([("dcyl", 4000.0), ("lcyl", 3000), ("pressure", 1), ("alpha", 0.8), ("beta", 2)])
        designKwargs = vphDesign1_isotensoid.copy()
        designKwargs.pop("safetyFactor")
        addArgs = OrderedDict(
            [
                ("targetFuncWeights", [1.0, 0.2, 1.0, 0.0, 0, 0]),
                ("verbosePlot", True),
                ("numberOfRovings", 12),
                ("gamma", 0.3),
                ("domeType", "conicalIsotensoid"),
                ("dome2Type", "isotensoid"),
                ("nodeNumber", 1000),
            ]
        )
        designKwargs.update(addArgs)
    elif name == "vph2":
        lb = OrderedDict([("minPressure", 0.0), ("safetyFactor", 1)])  # [MPa, -]
        ub = OrderedDict([("minPressure", 0.18), ("safetyFactor", 2.5)])
        designKwargs = {"configFile": "vph2_smr_iff_2bar_param_study"}
        doeClass = FullFactorialDesign
        sampleCount1d = 5
        numberOfSamples = sampleCount1d**2

    if 0:  # for testing
        numberOfSamples = 5
        designKwargs["maxLayers"] = 3
    return designKwargs, lb, ub, numberOfSamples, doeClass, units


def collectYResults(runDir):

    results = list()
    results_path = runDir
    all_folders = [name for name in os.listdir(results_path) if os.path.isdir(os.path.join(results_path, name))]

    for count, filePath in enumerate(all_folders):
        worker_results_path = results_path + "/" + filePath
        all_sub_folders = [
            name for name in os.listdir(worker_results_path) if os.path.isdir(os.path.join(worker_results_path, name))
        ]
        for count, filePath in enumerate(all_sub_folders):

            with open(worker_results_path + "/" + filePath + "/all_parameters_and_results.txt", "r") as file:
                reader = csv.reader(file, delimiter="|")
                txt_reader = [x for x in reader]

            run_results = []
            for row in txt_reader:
                try:
                    entry = row[0].replace(" ", "")
                    if entry in resultNames:
                        run_results.append(float(row[2].replace(" ", "")))
                except (IndexError, ValueError):
                    continue

            results.append(run_results)
    return results


def createTankResults(name, sampleXFile, sampleYFolder="", basePath=None, adaptExact2ParameterKey=None):
    """

    :param name: name of the design and bounds to return. Not case sensitive!
    :param sampleXFile: path and filename to a list with sampleX vaules
    :param sampleYFolder: path to a folder with sampleY results
    :param basePath: path to the base folder
    """
    startTime = datetime.now()

    designKwargs, lb, ub, numberOfSamples, doeClass, _ = getDesignAndBounds(name, adaptExact2ParameterKey)

    names = list(lb.keys())
    if resumeFolder:
        runDir = resumeFolder
        resumeSamples = True
        if not sampleXFile:
            raise Tankoh2Error(
                "You're attempting to resume a doe without setting the previously used sampleXFile. This will lead to errors."
            )
    else:
        runDir = getRunDir(
            f"doe_{name}", basePath=basePath if basePath is not None else os.path.join(programDir, "tmp")
        )
        resumeSamples = False

    winderClass = TankMetal if designKwargs["windingOrMetal"] == "metal" else TankWinder
    winder = winderClass(lb, ub, runDir, designKwargs)
    if sampleXFile:
        doe = DOEfromFile(sampleXFile)
    else:
        doe = doeClass(numberOfSamples, len(names))
        sampleXFile = os.path.join(runDir, "sampleX.txt")

    sampleX = BoundsHandler.scaleToBoundsStatic(doe.sampleXNormalized, list(lb.values()), list(ub.values()))
    doe.xToFile(os.path.join(runDir, "sampleX.txt"))
    doe.xToFileStatic(os.path.join(runDir, "sampleX_bounds.txt"), sampleX)
    if sampleYFolder:
        sampleY = collectYResults(sampleYFolder)
    else:
        sampleY = getY(sampleX, winder, verbose=True, runDir=runDir, resumeSamples=resumeSamples, staggerStart=2)

    # store samples
    doe.yToFile(os.path.join(runDir, "sampleY.txt"), winder, sampleY)

    doe.xyToFile(
        os.path.join(runDir, "full_doe.txt"),
        sampleY,
        headerNames=names + winder.resultNames,
        lb=lb,
        ub=ub,
        scaleToBounds=True,
    )

    duration = datetime.now() - startTime
    log.info(f"runtime {duration.seconds} seconds")
    return sampleXFile


def main():
    import delismm.model.samplecalculator

    delismm.model.samplecalculator.manualMinParallelProcesses = int(np.ceil(cpu_count() / 2))
    createDoe = True
    plotDoe = False
    plotExact2Doe = False
    createSurrogate = True
    sampleXFile = ""
    if resumeFolder:
        runDir = None
    else:
        runDir = getRunDir(
            "tank_surrogates" + (f"_{adaptExact2ParameterKey}" if adaptExact2ParameterKey and createDoe else ""),
            basePath=os.path.join(tankoh2.programDir, "tmp"),
        )
    if plotExact2Doe:
        if adaptExact2ParameterKey != "":
            raise Tankoh2Error("plotExact2Doe is not supported for adaptExact2ParameterKey")
    # mmRunDir = mmRunDir[:-7]
    resultNamesLog10 = [
        ("totalMass", True),
        # ("volume", True),
        # ("area", False),
        # ("lengthAxial", False),
        # ("cylinderThickness", False),
        # ("gravimetricIndex", False),
    ]
    resultNamesIndexesLog10 = [
        (f"{resultName}[{resultKeyToUnitDict[resultName]}]", resultNames.index(resultName), doLog10)
        for resultName, doLog10 in resultNamesLog10
    ]
    designKwargs, lb, ub, numberOfSamples, doeClass, units = getDesignAndBounds(designName, adaptExact2ParameterKey)
    if designName == "exact_cyl_isotensoid":
        sampleXFile = "" + r"C:\PycharmProjects\tankoh2\tmp\doe_exact_cyl_isotensoid_20230106_230150/sampleX.txt"
        surrogateDir = "" + r"C:\PycharmProjects\tankoh2\tmp\tank_surrogates_20230109_180336"
    elif designName == "exact_conical_isotensoid":
        sampleXFile = "" + r"C:\PycharmProjects\tankoh2\tmp\doe_exact_conical_isotensoid_20230111_180256/sampleX.txt"
        surrogateDir = ""  # + r'C:\PycharmProjects\tankoh2\tmp\tank_surrogates_20230109_180336'
    elif designName == "exact2_large_designspace":
        sampleXFile = r"C:\Users\freu_se\Documents\Projekte\EXACT2\05_Abwicklung\STM\Surrogate models\Model v1.1\Metal\sampleX.txt"
    elif designName == "exact2":
        sampleXFile = r"C:\PycharmProjects\tankoh2\tmp\exact2_doe_complete_20250409\sampleX.txt"
        surrogateDir = ""
        if createSurrogate:
            lb, ub = _getExtendedBounds(lb, ub, lb.keys())
        if adaptExact2ParameterKey:
            sampleXFile = (
                r"C:\PycharmProjects\tankoh2\tmp\exact2_doe_" + adaptExact2ParameterKey + r"_20250409\doe\sampleX.txt"
            )
    elif designName == "dlight":
        sampleXFile = (
            r"C:\Users\jaco_li\Tools\tankoh2\tmp\tank_surrogates_20250801_175648\doe_dlight_20250801_175648\sampleX.txt"
        )
        pass
    else:
        raise Tankoh2Error(f"designName {designName} not supported. Supported are {allowedDesignNames}")

    if createDoe:
        sampleXFile = createTankResults(
            designName, sampleXFile, basePath=runDir, adaptExact2ParameterKey=adaptExact2ParameterKey
        )
    if plotDoe:
        doe = DOEfromFile(sampleXFile)
        sampleX = BoundsHandler(lb, ub).scaleToBounds(doe.sampleXNormalized)
        plotGeometryRange(lb, ub, show=True, samples=sampleX, addBox=("exact" in designName), plotDir=runDir)
    if plotExact2Doe:
        plotExact2GeometryRange(lb, ub, runDir, sampleXFile)
        plotExact2GeometryRange(lb, ub, runDir, sampleXFile, useLogScale=False)
    if createSurrogate:
        parameterNames = lb.keys()
        parameterNames = [name + unit for name, unit in zip(parameterNames, units)]
        krigings = getKrigings(
            os.path.dirname(sampleXFile), os.path.dirname(sampleXFile), parameterNames, resultNamesIndexesLog10
        )


if __name__ == "__main__":
    runMain = True
    if runMain:
        main()
    else:
        targetDoeDir_ = r"C:\PycharmProjects\tankoh2\tmp\exact2_doe_complete_20250409"
        baseDir = r"C:\PycharmProjects\tankoh2\tmp"
        _, lb, ub, _, _, _ = getDesignAndBounds("exact2")
        lb, ub = _getExtendedBounds(lb, ub, lb.keys())
        AbstractDOE.joinDoeResults(
            [
                os.path.join(baseDir, doeDir, "run")
                for doeDir in [
                    "exact2_doe_20250409",
                    "exact2_doe_dcyl_20250409",
                    "exact2_doe_lcylByR_20250409",
                    "exact2_doe_pressure_20250409",
                ]
            ],
            targetDoeDir_,
            TankWinder(lb, ub, targetDoeDir_, {}),
            list(lb.keys()),
        )
