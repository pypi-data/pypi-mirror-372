# SPDX-FileCopyrightText: 2023 German Aerospace Center (DLR)
#
# SPDX-License-Identifier: MIT
import time
from functools import partial
from multiprocessing import Pool

import numpy as np
import openturns.viewer as viewer
from matplotlib import pyplot as plt

from tankoh2 import log, pychain
from tankoh2.design.winding.solver import getThickShellScaling
from tankoh2.design.winding.windingutils import getAnglesFromVesselCylinder
from tankoh2.sensitivityAnalysis.parameterSets import *
from tankoh2.service.exception import Tankoh2Error
from tankoh2.settings import settings


def getParameterDistribution(parameters):
    distributionInputs = []
    for parameter in parameters:
        distributionInputs.append(parameter.createDistribution())
    composedDistribution = ot.ComposedDistribution(distributionInputs)
    composedDistribution.setDescription([parameter.name for parameter in parameters])
    return composedDistribution


def getPuck(vessel, composite, burstPressure):

    converter = pychain.mycrofem.VesselConverter()
    shellModel = converter.buildAxShellModell(vessel, burstPressure, True, True)  # pressure in MPa (bar / 10.)
    linearSolver = pychain.mycrofem.LinearSolver(shellModel)
    linearSolver.run(True)
    S11, S22, S12, puckFF = shellModel.calculateLayerStressesBottom()
    if settings.ignoreLastElements:
        puckFF[-settings.ignoreLastElements :] = 0
    else:
        puckFF[-1] = 0
    thickShellScaling = getThickShellScaling(vessel, burstPressure, composite)
    puckFF = np.multiply(puckFF, thickShellScaling)
    return puckFF


class windingSimulationFunction(ot.OpenTURNSPythonFunction):
    def __init__(
        self,
        appliedParameterSet,
        deltaSpline,
    ):
        super(windingSimulationFunction, self).__init__(len(appliedParameterSet.parameters), 1)
        self.parameters = appliedParameterSet.parameters
        self.baseCompositeFile = appliedParameterSet.baseCompositeFile
        self.baseLinerFile = appliedParameterSet.baseLinerFile
        self.deltaSpline = deltaSpline
        self.burstPressure = appliedParameterSet.burstPressure

    def _exec(self, inputs):
        composite = pychain.material.Composite()
        composite.loadFromFile(self.baseCompositeFile)
        baseLiner = pychain.winding.Liner()
        baseLiner.loadFromFile(self.baseLinerFile)

        for i, parameter in enumerate(self.parameters):
            if hasattr(parameter, "setMaterialParameter"):
                parameter.setMaterialParameter(inputs[i], composite)

        for i, parameter in enumerate(self.parameters):
            if hasattr(parameter, "setCompositeParameter"):
                parameter.setCompositeParameter(inputs[i], composite)
            elif hasattr(parameter, "setLinerParameter"):
                parameter.setLinerParameter(inputs[i], baseLiner, self.deltaSpline)

        vessel = pychain.winding.Vessel()
        vessel.setLiner(baseLiner)
        vessel.setComposite(composite)

        for i, parameter in enumerate(self.parameters):
            if hasattr(parameter, "setVesselParameter"):
                parameter.setVesselParameter(inputs[i], vessel)

        vessel.finishWinding()

        saveVessel = False
        if saveVessel:
            vessel.saveToFile("C:/Users/jaco_li/Tools/tankoh2/save/SensitivityAnalyses/testresult.vessel")
            windingResults = pychain.winding.VesselWindingResults()
            windingResults.buildFromVessel(vessel)
            windingResults.saveToFile("C:/Users/jaco_li/Tools/tankoh2/save/SensitivityAnalyses/testresult.wresult")

        puckFailure = getPuck(vessel, self.burstPressure)
        puckMax = puckFailure.max().max()
        return [self.burstPressure * 10 / puckMax]


def function(appliedParameterSet, input):
    composite = pychain.material.Composite()
    composite.loadFromFile(appliedParameterSet.baseCompositeFile)
    baseLiner = pychain.winding.Liner()
    baseLiner.loadFromFile(appliedParameterSet.baseLinerFile)
    vessel = pychain.winding.Vessel()
    vessel.setLiner(baseLiner)

    for j, parameter in enumerate(appliedParameterSet.parameters):
        if hasattr(parameter, "setMaterialParameter"):
            parameter.setMaterialParameter(input[j], composite)

    for j, parameter in enumerate(appliedParameterSet.parameters):
        if hasattr(parameter, "setCompositeParameter"):
            parameter.setCompositeParameter(input[j], composite)
        # elif hasattr(parameter, "setLinerParameter"):
        #    parameter.setLinerParameter(input[j], baseLiner, deltaSpline)

    vessel.setComposite(composite)

    for j, parameter in enumerate(appliedParameterSet.parameters):
        if hasattr(parameter, "setVesselParameter"):
            parameter.setVesselParameter(input[j], vessel)
    vessel.finishWinding()

    saveVessel = False
    if saveVessel:
        vessel.saveToFile("C:/Users/jaco_li/Tools/tankoh2/save/SensitivityAnalyses/testresult.vessel")
        windingResults = pychain.winding.VesselWindingResults()
        windingResults.buildFromVessel(vessel)
        windingResults.saveToFile("C:/Users/jaco_li/Tools/tankoh2/save/SensitivityAnalyses/testresult.wresult")

    puckFailure = getPuck(vessel, composite, appliedParameterSet.burstPressure)
    puckMax = puckFailure.max()
    angles = getAnglesFromVesselCylinder(vessel)
    puckMaxHelicals = [
        puckLayerFailure.max() if angles[layer] < 88 else 0 for layer, puckLayerFailure in enumerate(puckFailure.T)
    ]
    puckMaxDome = max(puckMaxHelicals)
    return [appliedParameterSet.burstPressure * 10 / puckMax, appliedParameterSet.burstPressure * 10 / puckMaxDome]


def windingSimulations(appliedParameterSet, inputs):
    print(f"{inputs.getSize()} Evaluations.")
    partial_function = partial(function, appliedParameterSet)

    parallel = True
    if parallel:
        processes_pool = Pool(12)
        t1 = time.time()
        outputs = processes_pool.map(partial_function, inputs)
        t2 = time.time()
        planNumbers = 100000
        print(f"{planNumbers} calculations will probably take {(t2-t1)/3600*planNumbers/inputs.getSize()} hours.")
    else:
        outputs = [partial_function(input) for input in inputs]
    outputSamples = ot.Sample.BuildFromPoint([output[0] for output in outputs])
    outputSamplesHelical = ot.Sample.BuildFromPoint([output[1] for output in outputs])
    return outputSamples, outputSamplesHelical


def sobolSensitivityAnalysis():

    appliedParameterSet = NGT_BIT_parameterSet()
    calculate = False
    secondOrderIndices = False
    size = 20000

    if calculate:
        distribution = getParameterDistribution(appliedParameterSet.parameters)
        experiment = ot.SobolIndicesExperiment(distribution, size, secondOrderIndices)
        inputs = experiment.generate()
        outputs = windingSimulations(appliedParameterSet, inputs)
        timestr = time.strftime("%Y%m%d_%H%M%S")
        inputs.exportToCSVFile(f"C:/Users/jaco_li/Tools/tankoh2/save/SensitivityAnalyses/inputSample_NGT_Bit_Dome.csv")
        outputs.exportToCSVFile(
            f"C:/Users/jaco_li/Tools/tankoh2/save/SensitivityAnalyses/outputSample_NGT_Bit_Dome.csv"
        )
    else:
        inputs = ot.Sample.ImportFromCSVFile(
            "C:/Users/jaco_li/Tools/tankoh2/save/SensitivityAnalyses/inputSample_NGT_Bit_Dome.csv"
        )
        outputs = ot.Sample.ImportFromCSVFile(
            "C:/Users/jaco_li/Tools/tankoh2/save/SensitivityAnalyses/outputSample_NGT_Bit_Dome.csv"
        )
        if secondOrderIndices:
            if inputs.getDimension() == 2:
                size = int(inputs.getSize() / (2 + inputs.getDimension()))
            else:
                size = int(inputs.getSize() / (2 + 2 * inputs.getDimension()))
        else:
            size = int(inputs.getSize() / (2 + inputs.getDimension()))

    sensitivityAnalysis = ot.SaltelliSensitivityAlgorithm(inputs, outputs, size)
    print(sensitivityAnalysis.getFirstOrderIndices())
    print(sensitivityAnalysis.getTotalOrderIndices())
    if secondOrderIndices:
        second_order = sensitivityAnalysis.getSecondOrderIndices()
        for i in range(len(appliedParameterSet.parameters)):
            for j in range(i):
                print("2nd order indice (%d,%d)=%g" % (i, j, second_order[i, j]))

    graph = sensitivityAnalysis.draw()

    graph.setYTitle("Sobol Index: Influence on Burst Pressure")
    graph.setXTitle("")
    graph.setBoundingBox(ot.Interval([0, 0], [8, 0.6]))
    drawables = graph.getDrawables()
    for idx, drawable in enumerate(drawables):
        if drawable.getColor() == "black":
            graph.erase(idx)
    view = viewer.View(graph, (1920, 1080))
    ax = view.getAxes()[0]
    ax.set_yticks(np.arange(-0.05, 1.0, 0.05))
    ax.set_xticks(np.arange(0, 10, 1), [""] + [parameter.name for parameter in appliedParameterSet.parameters] + [""])
    plt.show()


def taylorMoments():
    appliedParameterSet = ECCMParameterSet()
    baseComposite = pychain.material.Composite()
    baseComposite.loadFromFile(appliedParameterSet.baseCompositeFile)
    baseLiner = pychain.winding.Liner()
    baseLiner.loadFromFile(appliedParameterSet.baseLinerFile)
    baseWindingProps = baseComposite.getOrthotropLayer(0).windingProperties
    deltaSpline = baseWindingProps.rovingWidth * baseWindingProps.numberOfRovings / 8  # 8 Elements per Band
    distribution = getParameterDistribution(appliedParameterSet.parameters)
    inputVector = ot.RandomVector(distribution)
    model = windingSimulationFunction(appliedParameterSet, deltaSpline)
    windingFunction = ot.Function(model)
    output = ot.CompositeRandomVector(windingFunction, inputVector)
    TaylorExpansionMoments = ot.TaylorExpansionMoments(output)
    print(TaylorExpansionMoments.getImportanceFactors())


def monteCarlo():
    calculate = False

    if calculate:
        size = 5000
        appliedParameterSet = DLight_Rear_parameterSet()
        baseComposite = pychain.material.Composite()
        baseComposite.loadFromFile(appliedParameterSet.baseCompositeFile)
        baseWindingProps = baseComposite.getOrthotropLayer(0).windingProperties
        deltaSpline = baseWindingProps.rovingWidth * baseWindingProps.numberOfRovings / 8  # 8 Elements per Band
        distribution = getParameterDistribution(appliedParameterSet.parameters)
        experiment = ot.MonteCarloExperiment(distribution, size)
        inputs = experiment.generate()
        samples, samplesHelical = windingSimulations(appliedParameterSet, inputs)
        samples.exportToCSVFile("C:/Users/jaco_li/Tools/tankoh2/save/SensitivityAnalyses/DLight_Rear.csv")
        samplesHelical.exportToCSVFile("C:/Users/jaco_li/Tools/tankoh2/save/SensitivityAnalyses/DLIGHT_Rear_Dome.csv")

    else:
        samples = ot.Sample.ImportFromCSVFile("C:/Users/jaco_li/Tools/tankoh2/save/SensitivityAnalyses/DLight_Rear.csv")
        samplesHelical = ot.Sample.ImportFromCSVFile(
            "C:/Users/jaco_li/Tools/tankoh2/save/SensitivityAnalyses/DLight_Rear_Dome.csv"
        )

    # Create histograms for both samples
    histogram1 = ot.HistogramFactory().buildAsHistogram(samples, 32)
    histogram2 = ot.HistogramFactory().buildAsHistogram(samplesHelical, 40)

    # Draw the PDFs of both histograms
    graph1 = histogram1.drawPDF()
    graph2 = histogram2.drawPDF()

    # Set different colors for each histogram
    graph1.setColors(["blue"])  # Blue for the first sample
    graph2.setColors(["darkgreen"])  # Darkgreen for the second sample

    # Set titles and legend
    graph1.setXTitle("Burst Pressure [Bar]")
    graph1.setYTitle("Probability Density Function")

    # Add both graphs to the same plot
    graph1.add(graph2)
    graph1.setLegendFontSize(32)
    plt.rcParams.update({"font.size": 32})

    # Display the plot
    view = viewer.View(graph1)
    ax = view.getAxes()[0]
    ax.set_xticks(np.arange(1300, 1800, 100))  # Customize x-ticks
    ax.legend(labels=["Cylinder Region", "Dome Region"])
    getDistribution = False
    if getDistribution:
        normalFactory = ot.NormalFactory()
        weibullMinFactory = ot.WeibullMinFactory()

        burstDistributionWeibullMin = weibullMinFactory.build(samples)
        burstDistributionNormal = normalFactory.build(samples)

        ot.ResourceMap.SetAsUnsignedInteger("FittingTest-LillieforsMaximumSamplingSize", 1000)
        dist, result = ot.FittingTest.Lilliefors(samples, normalFactory)
        print("Normal Distribution Conclusion=", result.getBinaryQualityMeasure(), "P-value=", result.getPValue())

        print(burstDistributionNormal.getParameterDescription())
        print(burstDistributionNormal.getParameter())

        ot.ResourceMap.SetAsUnsignedInteger("FittingTest-LillieforsMaximumSamplingSize", 1000)
        dist, result = ot.FittingTest.Lilliefors(samples, weibullMinFactory)
        print("WeibullMin Distribution Conclusion=", result.getBinaryQualityMeasure(), "P-value=", result.getPValue())

        print(burstDistributionWeibullMin.getParameterDescription())
        print(burstDistributionWeibullMin.getParameter())

    plt.show()


if __name__ == "__main__":
    # sobolSensitivityAnalysis()
    # taylorMoments()
    monteCarlo()
