"""

.. mermaid::

    flowchart TB
        a{"test
        data?"}
        subgraph s1 ["fitFatigueParameters()"]
        b("read test data
        readFatigueTestData()")
        c1("fit woehler curve parameters
        getWoehlerParameters()")
        c2("obtain N_f on woheler curve
        for different stress ratio")
        c3("fit fatigue stress factor,u,v
        FatigueParamFitter()")
        c4("fit master curve parameters
        fitMastercurveParameters()")
        end
        subgraph s2 ["scaleFatigueParameters()"]
        d("read fatigue data
        from other material")
        e(scale fatigue parameters)
        end
        r(save fatigue parameters)
        a -- yes --> b
        b --> c1
        c1 --> c2
        c2 --> c3
        c3 --> c4
        c4 --> r
        a -- no --> d
        d --> e
        e --> r


"""

import glob
import json
from os.path import basename, exists, join

import numpy as np
import pandas as pd
from scipy.optimize import curve_fit

from tankoh2 import log, programDir
from tankoh2.mechanics.fatigue import (
    addMeanstressesAndAmplitudesNorm,
    getFatigueStressFactor,
    masterCurve,
    masterCurveLog10,
    woehler,
    woehlerLog,
)
from tankoh2.mechanics.material import FrpMaterialFatigueProperties
from tankoh2.mechanics.material import directions as allDirections
from tankoh2.service.exception import Tankoh2Error
from tankoh2.service.utilities import addDictHierarchyIfNotPresent


def readFatigueTestDataTxtFiles(testDir):
    """opens all \*.txt files in testDir, loads is data using np.loadtxt() and returns them as 3D dataset

    :param testDir: directory containing test data.
        The test data is a 2-colunm dataset containing these columns: [cycleCount, loadlevel]

    """
    data = []
    for filename in glob.glob(testDir + "/*.txt"):
        with open(filename) as f:
            direction = float(basename(filename)[2:4])
            r = float(filename.rsplit("R=")[-1][:-4])
            readData = np.loadtxt(filename, delimiter=",")
            data += [(direction, r, *items) for items in readData]
    df = pd.DataFrame(data, columns=["direction", "stressRatio", "cycles", "stressUpper"])
    df["stressLower"] = df["stressUpper"] * df["stressRatio"]
    df["direction"] = df["direction"].astype(int)
    return df


def readFatigueTestData(testFilenameOrBuf):
    """reads fatigue test data from a pandas confrom csv file"""
    return pd.read_csv(testFilenameOrBuf, index_col=0)


def writeFatigueParametersToFile(targetMaterialFile, fatigueParamDataFrame):
    """Writes fatigue parameters to a µWind like material file.
    The base structure of the file is used, extended and
    the result is written to a file adding "_fatigue_fit" to the file name.

    :param targetMaterialFile: base material file in µWind material json format
    :param fatigueParamDataFrame: dataframe with columns ["direction", "u", "v", "C", "D"]
    """
    if not exists(targetMaterialFile):
        targetMaterialFile = join(programDir, "data", targetMaterialFile)
    with open(targetMaterialFile) as f:
        materialDict = json.load(f)
    fatigueHierarchy = ["materials", "1", "umatProperties", "data_sets", "1", "fatigueProperties"]
    addDictHierarchyIfNotPresent(materialDict, fatigueHierarchy)
    for index, (direction, u, v, C, D) in fatigueParamDataFrame.loc[:, ["direction", "u", "v", "C", "D"]].iterrows():
        direction = int(direction)
        fatigue_props = {f"A_{direction}": C, f"B_{direction}": D, f"u_{direction}": u, f"v_{direction}": v}
        materialDict["materials"]["1"]["umatProperties"]["data_sets"]["1"]["fatigueProperties"].update(fatigue_props)

    targetMaterialFile = targetMaterialFile[:-5] + "_fatigue_fit.json"
    with open(targetMaterialFile, "w") as f:
        json.dump(materialDict, f, indent=2)


def fitFatigueParameters(cyclicTestDataFrame, materialName, directions=allDirections):
    """fits the fatigue parameters based on test data

    :param cyclicTestDataFrame: test data. pandas DataFrame with columns
        ["direction", "stressRatio", "cycles", "stressUpper", "stressLower"]
    :param materialName: name of the material file either in tankoh2/data or full filename+path
    :param directions: directions to be used [11, 22, 12]
    :return: dataframe with fitted parameters. columns: ["direction", "u", "v", "C", "D"]
    """
    Cs, Ds = [], []
    result = []
    Nf_fit = np.array([100.0, 1000.0, 10000.0, 100000.0, 1000000.0])
    """Nf_fit is the cycle count used for CLL, master curve fitting"""
    for direction in directions:
        if direction not in allDirections:
            raise Tankoh2Error(
                f'the direction "{direction}" is unknown. Only these directions are used: ' f"{allDirections.keys()}"
            )
        material = FrpMaterialFatigueProperties().readMaterial(materialName)
        tensileStrength, compressionStrength = material.getStrengths(direction)
        strengthRatio = compressionStrength / tensileStrength
        testDataDf = cyclicTestDataFrame[cyclicTestDataFrame["direction"] == direction].copy()

        As, Bs, Rs = getWoehlerParameters(testDataDf)
        fatigueParamDf = getMeanstressesAndAmplitudesNormWoehler(As, Bs, Rs, Nf_fit, tensileStrength)

        ff = FatigueParamFitter(strengthRatio, len(fatigueParamDf["stressRatio"].unique()))
        fatigueStressfactor, u, v = ff.getFatigueParameters(
            fatigueParamDf["meanStressNorm"], fatigueParamDf["stressAmplitudeNorm"]
        )
        C, D = fitMastercurveParameters(Nf_fit, np.log10(fatigueStressfactor))
        Cs.append(C)
        Ds.append(D)
        log.info(f"f {fatigueStressfactor}, u {u}, v {v}, C {C}, D {D}")
        result.append([direction, u, v, C, D])
    resultDf = pd.DataFrame(result, columns=["direction", "u", "v", "C", "D"])
    return resultDf


def getWoehlerParameters(cyclesStressesDataFrame, tensileStrengthScaling=1, compressionStrengthScaling=1):
    """Calculates A and B for Woehler calculations according eq. 5.20 for each given stress ratio

    :param cyclesStressesDataFrame: dataframe with these required columns ['stressRatio','cycles','stress']
    :param tensileStrengthScaling: scaling to strengths for non-compression cases including alternating case
    :param compressionStrengthScaling: scaling to strengths fo compression cases
    :return: woehlerA, woehlerB
    """
    woehlerAvalues = []
    woehlerBvalues = []
    stressRatios = []

    df = cyclesStressesDataFrame
    for direction in df["direction"].unique():
        for stressRatio in df["stressRatio"].unique():
            log.info(f"direction {direction}, stressRatio {stressRatio}")
            dfUse = df[(df["stressRatio"] == stressRatio) & (df["direction"] == direction)]
            if len(dfUse) == 0:
                continue
            cycles, stressesUpper, stressesLower = dfUse["cycles"], dfUse["stressUpper"], dfUse["stressLower"]
            stressRatios.append(stressRatio)
            if (stressesUpper < 0).any():
                # compression amplitude
                if not (stressesUpper < 0).all():
                    raise Tankoh2Error(
                        f"Not all given strengths are either positive or negative. Strengths: {stressesUpper}"
                    )
                stresses = np.abs(stressesLower * compressionStrengthScaling)
            elif stressRatio < -1:
                # mixed amplitude with higher lower stress
                stresses = np.abs(stressesLower) * tensileStrengthScaling
            else:
                # mixed amplitude with higher upper stress OR tension amplitude
                stresses = stressesUpper * tensileStrengthScaling

            A, B = fitWoehler(cycles, stresses)
            woehlerAvalues.append(A)
            woehlerBvalues.append(B)

    return woehlerAvalues, woehlerBvalues, stressRatios


def fitWoehler(cycles, strengths):
    """

    :param cycles:
    :param strengths:
    :return: A, B
    """
    popt, pcov = curve_fit(woehlerLog, np.log(cycles), np.log(strengths))
    A, B = popt
    A = np.exp(A)
    # popt, pcov = curve_fit(woehlerLogCycles, np.log(cycles), strengths)
    return A, B


def getMeanstressesAndAmplitudesNormWoehler(A, B, stressRatio, Nf_fit, tensileStrength):
    """Calculates normalized stress amplitude and normalized mean stress by woehler curve

    :param A: parameter Woehler-fitting
    :param B: parameter Woehler-fitting
    :param stressRatio: stress ratio
    :param Nf_fit: cycle number for generating CLDs and cycle range for fitting
    :param tensileStrength: tensileStrength of material that is evaluated
    :return: normalizedMeanstresses, normalizedAmplitudes
    """
    df = pd.DataFrame(
        {
            "cycles": np.array([[Nf] * len(A) for Nf in Nf_fit]).flatten(),
            "stressRatio": stressRatio * len(Nf_fit),
            "A": A * len(Nf_fit),
            "B": B * len(Nf_fit),
        }
    )
    df["stressUpper"] = woehler(df["cycles"], df["A"], df["B"])

    # compression dominated spectra should switch max stress
    df.loc[abs(df["stressRatio"]) > 1, "stressUpper"] = (
        -1 * df.loc[abs(df["stressRatio"]) > 1, "stressUpper"] / df.loc[abs(df["stressRatio"]) > 1, "stressRatio"]
    )
    df["stressLower"] = df["stressUpper"] * df["stressRatio"]
    return addMeanstressesAndAmplitudesNorm(df, tensileStrength)


class FatigueParamFitter:
    """fits the fatique parameters f, u, v"""

    def __init__(self, strengthRatio, stressRatioCount):
        self.strengthRatio = strengthRatio
        self.stressRatioCount = stressRatioCount

    def getFatigueParameters(self, normMeanstresses, normAmplitudes):
        """Calculates fatigue parameters analog to table 8.2 assuming equal u,v

        :param normMeanstresses: normalized stress amplitude
        :param normAmplitudes: normalized mean stress
        :return: f, u, v - fatigue stress factor and parameter of fitting process
        """
        bounds = (
            [-np.inf, -np.inf, -np.inf, -np.inf, -np.inf, 1.0, 1.0],
            [np.inf, np.inf, np.inf, np.inf, np.inf, np.inf, np.inf],
        )
        popt, pcov = curve_fit(self.f_u_v, normMeanstresses, normAmplitudes, bounds=bounds)
        f1 = popt[0]
        f2 = popt[1]
        f3 = popt[2]
        f4 = popt[3]
        f5 = popt[4]
        u = popt[5]
        v = popt[6]
        f = [f1, f2, f3, f4, f5]
        return f, u, v

    def f_u_v(self, normMeanstresses, f1, f2, f3, f4, f5, u, v):
        """eq 8.4: relationship between nomalized mean stress and normalized amplitude"""
        strengthRatio = self.strengthRatio
        i = self.stressRatioCount
        normAmplitudes1 = f1 * ((1.0 - normMeanstresses[0:i]) ** u * (strengthRatio + normMeanstresses[0:i]) ** v)
        normAmplitudes2 = f2 * (
            (1.0 - normMeanstresses[i : 2 * i]) ** u * (strengthRatio + normMeanstresses[i : 2 * i]) ** v
        )
        normAmplitudes3 = f3 * (
            (1.0 - normMeanstresses[2 * i : 3 * i]) ** u * (strengthRatio + normMeanstresses[2 * i : 3 * i]) ** v
        )
        normAmplitudes4 = f4 * (
            (1.0 - normMeanstresses[3 * i : 4 * i]) ** u * (strengthRatio + normMeanstresses[3 * i : 4 * i]) ** v
        )
        normAmplitudes5 = f5 * (
            (1.0 - normMeanstresses[4 * i : 5 * i]) ** u * (strengthRatio + normMeanstresses[4 * i : 5 * i]) ** v
        )

        return np.array([normAmplitudes1, normAmplitudes2, normAmplitudes3, normAmplitudes4, normAmplitudes5]).flatten()


def fitMastercurveParameters(Nf_fit, fatigueStressfactor):
    """Calculates C and D

    :param Nf_fit: cycle number for generating CLDs and cycle range for fitting
    :param fatigueStressfactor: fatigue stress factor
    :return: C, D - parameters for master curve
    """
    x0 = [0.0, 0.0]
    popt, pcov = curve_fit(masterCurveLog10, Nf_fit, fatigueStressfactor, x0)
    C = 10 ** popt[0]
    D = popt[1]
    return C, D


def scaleFatigueParameters():
    pass


def getStrengths(direction, material):
    if direction not in allDirections:
        raise Tankoh2Error(f"direction {direction} not in allDirections {allDirections}")
    if direction == 11:
        tensileStrength = material.R_1_t
        compressionStrength = material.R_1_c
    elif direction == 22:
        tensileStrength = material.R_2_t
        compressionStrength = material.R_2_c
    else:
        tensileStrength = material.R_21
        compressionStrength = material.R_21
    return tensileStrength, compressionStrength


def plotMasterCurve():
    """just for testing
    similar to fig 8.7
    """
    from os.path import join

    from matplotlib import pyplot as plt

    csvPath = join(programDir, "test/test_mechanics/fatigue_test_data/testData.csv")
    testDataDf = readFatigueTestData(csvPath)

    if 0:
        direction = 22
        u_v = 2.2798066873167544, 2.543927034161581
        C, D = 0.028560893436064654, -0.04347065755731098
    else:
        direction = 11
        u_v = 1.16652, 1.18426
        C, D = 1.34437, -0.02105

    testDataDf = testDataDf[testDataDf["direction"] == direction].copy()

    materialName = "CFRP_HyMod.json"
    material = FrpMaterialProperties().readMaterial(materialName)
    tensileStrength, compressionStrength = material.getStrengths(direction)
    strengthRatio = compressionStrength / tensileStrength
    testDataDf = addMeanstressesAndAmplitudesNorm(testDataDf, tensileStrength)
    f = getFatigueStressFactor(testDataDf["stressAmplitudeNorm"], testDataDf["meanStressNorm"], strengthRatio, *u_v)
    testDataDf["fatigueFittingFactor"] = f

    # master curve
    Nf_master = np.power(10, np.linspace(1, 7, 101))
    f_master = masterCurve(Nf_master, C, D)

    fig, ax = plt.subplots()
    markers = ["^", "o", "s"]
    for R, marker in zip(testDataDf["stressRatio"].unique(), markers):
        Nf = testDataDf[testDataDf["stressRatio"] == R]["cycles"]
        f = testDataDf[testDataDf["stressRatio"] == R]["fatigueFittingFactor"]
        ax.loglog(Nf, f, marker=marker, color="black", linestyle="None", label=f"test data, R={R}")
    ax.loglog(Nf_master, f_master, label="master curve")
    ax.legend()
    if direction == 22:
        plt.ylim((1e-3, 1e-1))
    plt.show()


if __name__ == "__main__":
    doPlot = False
    if doPlot:
        plotMasterCurve()
    else:
        testDataFrame = readFatigueTestData(join(programDir, "test/test_mechanics/fatigue_test_data/testData.csv"))
        resultDf = fitFatigueParameters(testDataFrame, "CFRP_HyMod.json")
        writeFatigueParametersToFile("CFRP_T700SC_LY556.json", resultDf)
