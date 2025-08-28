import numpy as np
import openturns as ot
from matplotlib import pyplot as plt
from openturns import viewer

if __name__ == "__main__":
    ESAStrengths = np.array([2400, 2413, 2552, 2552, 2352, 2374])
    POSICOSSStrengths = np.array([2549, 2753, 2691, 2800, 2719, 2788, 2666, 2719, 2555, 2683, 2836, 2810])
    DAEDALOSStrengths = np.array([2584, 2453, 2518, 2664, 2672, 2619, 2436, 2584, 2588, 2410, 2475])
    DESICOSSStrengths = np.array([2658.29, 2623.22, 2511.25, 2413, 2406.62, 2507.04, 2596.35])

    HyModStrengths = np.array([2562.058225, 2566.691812, 2551.195369, 2613.814698, 2537.469712, 2500.05409])

    IM7Strengths = np.concatenate(
        (ESAStrengths, POSICOSSStrengths, DAEDALOSStrengths, DESICOSSStrengths, HyModStrengths)
    )

    IM7Samples = ot.Sample(np.column_stack((IM7Strengths,)))
    ESASamples = ot.Sample(np.column_stack((ESAStrengths,)))
    POSICOSSSamples = ot.Sample(np.column_stack((POSICOSSStrengths,)))
    DAEDALOSSSamples = ot.Sample(np.column_stack((DAEDALOSStrengths,)))
    DESICOSSSamples = ot.Sample(np.column_stack((DESICOSSStrengths,)))
    HyModSamples = ot.Sample(np.column_stack((HyModStrengths,)))
    weibullFactory = ot.WeibullMinFactory()
    normalFactory = ot.NormalFactory()

    DAEDALOSSDESICOSSSamples = ot.Sample()
    DAEDALOSSDESICOSSSamples.add(DAEDALOSSSamples)
    DAEDALOSSDESICOSSSamples.add(DESICOSSSamples)
    DAEDALOSSDESICOSSDistribution = normalFactory.build(DAEDALOSSDESICOSSSamples)

    IM7Distribution = weibullFactory.build(IM7Samples)
    ESADistribution = weibullFactory.build(ESASamples)
    POSICOSSDistribution = weibullFactory.build(POSICOSSSamples)
    DAEDALOSSDistribution = weibullFactory.build(DAEDALOSSSamples)
    DESICOSSDistribution = weibullFactory.build(DESICOSSSamples)
    HyModDistribution = normalFactory.build(HyModSamples)

    print(DAEDALOSSDESICOSSDistribution.getParameterDescription())
    print(DAEDALOSSDESICOSSDistribution.getParameter())

    print(HyModDistribution.getParameterDescription())
    print(HyModDistribution.getParameter())

    ot.ResourceMap.SetAsUnsignedInteger("FittingTest-LillieforsMaximumSamplingSize", 1000)
    dist, result = ot.FittingTest.Lilliefors(HyModSamples, normalFactory)
    print("Conclusion=", result.getBinaryQualityMeasure(), "P-value=", result.getPValue())
    #  Hymod COV is 1,462%
    graph1 = IM7Distribution.drawPDF()

    graph1.add(POSICOSSDistribution.drawPDF())
    graph1.add(DAEDALOSSDistribution.drawPDF())
    graph1.add(DESICOSSDistribution.drawPDF())
    graph1.add(ESADistribution.drawPDF())
    graph1.add(HyModDistribution.drawPDF())
    graph1.setColors(ot.Drawable.BuildDefaultPalette(6))
    graph1.setLegends(["All IM7", "POSICOSS", "DAEDALOSS", "DESICOSS", "ESA", "HyMod"])

    view = viewer.View(graph1)
    plt.show()
