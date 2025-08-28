# SPDX-FileCopyrightText: 2023 German Aerospace Center (DLR)
#
# SPDX-License-Identifier: MIT

"""plots for design of experiments (DOE)"""
import numpy as np
from matplotlib import pyplot as plt


def _getAx(useLogScale=True):
    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(1, 1, 1)
    if useLogScale:
        ax.set_yscale("log")
    ax.set_title("Parameter bounds")
    ax.set_xlabel("Diameter [m]")
    ax.set_ylabel("Volume [m³]")
    return ax


def plotGeometryRange(
    lowerBoundDict,
    upperBoundDict,
    plotDir="",
    show=False,
    samples=None,
    addBox=False,
    addBounds=True,
    axes=None,
    samplesKwargs={},
):
    """Plot diameter vs volume

    :param lowerBoundDict: dict with lower bounds
    :param upperBoundDict: dict with upper bounds
    :param plotDir: directroy to save plot
    :param show: show plot
    :param samples: samples to be included in plot as scatter
    :param addBox: add box plot for region of specific aircraft
    :param ax: matplotlib axis to plot on
    :return: None
    """
    lb, ub = lowerBoundDict, upperBoundDict

    def volumeFunc(d, lcyl):
        """volume of a tank with circular domes [m**3]

        Used as rough estimation!"""
        return 4 / 3 * np.pi * (d / 2) ** 3 + lcyl * np.pi * (d / 2) ** 2

    dcylBounds = (lb["dcyl"], ub["dcyl"])
    dcylBounds = np.array(dcylBounds) / 1e3  # convert to m
    if "lcyl" in lb:
        lcylBounds = np.array([lb["lcyl"], ub["lcyl"]]) / 1e3  # convert to m
        lcylByRBounds = lcylBounds / (dcylBounds / 2)  # convert to ratio
    else:
        lcylByRBounds = np.array([lb["lcylByR"], ub["lcylByR"]])

    if axes is None:
        ax = _getAx()
    else:
        ax = axes

    boxColor = "tab:blue"
    if addBounds:
        for lcylByR in lcylByRBounds:
            x = np.linspace(*dcylBounds, 51)
            volumes1 = [volumeFunc(d, lcylByR * d / 2) for d in x]
            ax.plot(x, volumes1, color=boxColor, label=f"lcyl / r={lcylByR}")
            boxColor = "tab:orange"
    if addBox:
        linewidth = 2
        ax.add_patch(
            plt.Rectangle((1.2, 3), 1.0, 2, ec="gray", fc="none", linestyle="-", linewidth=linewidth, label="D70-FC")
        )
        ax.add_patch(
            plt.Rectangle(
                (2, 20), 1.6, 5, ec="gray", fc="none", linestyle="--", linewidth=linewidth, label="D250-TPLH2"
            )
        )
        ax.add_patch(
            plt.Rectangle(
                (5, 100), 1, 20, ec="gray", fc="none", linestyle=":", linewidth=linewidth, label="D350L-TFLH2 T1"
            )
        )
        ax.add_patch(
            plt.Rectangle(
                (5, 260), 1, 40, ec="gray", fc="none", linestyle="-.", linewidth=linewidth, label="D350L-TFLH2 T2"
            )
        )
    if samples is not None:
        samplesD, samplesLcylByR = samples[:2, :]
        samplesD = samplesD / 1e3
        samplesLcyl = samplesLcylByR * samplesD / 2

        volumes2 = volumeFunc(samplesD, samplesLcyl)
        ax.scatter(samplesD, volumes2, **samplesKwargs)
    if axes is None:
        ax.legend()

    if plotDir:
        plt.savefig(plotDir + "/geometryRange.png")
    if show:
        plt.show()
    return ax


def plotExact2GeometryRange(lb, ub, mmRunDir, sampleXFile, useLogScale=True):
    keys = ("", "dcyl_", "lcylByR_", "pressure_")
    sampleXFileBase = sampleXFile
    lbList, ubList = np.array(list(lb.values())), np.array(list(ub.values()))
    maxUbList = ubList + (ubList - lbList)
    maxUb = {key: value for key, value in zip(lb.keys(), maxUbList)}
    ax = _getAx(useLogScale=useLogScale)
    for key in keys:
        sampleXFile = sampleXFileBase.replace("exact2_doe_", f"exact2_doe_{key}")
        sampleXFile = sampleXFile.replace("sampleX.txt", "sampleX_bounds.txt")
        from delismm.model.doe import DOEfromFile

        doe = DOEfromFile(sampleXFile)
        plotGeometryRange(
            lb,
            ub,
            samples=doe.sampleXNormalized,
            axes=ax,
            addBounds=False,
            samplesKwargs=(
                {"label": "Higher pressure", "color": "tab:green"} if "pressure" in key else {"color": "tab:blue"}
            ),
        )
    plotGeometryRange(lb, maxUb, addBox=True, addBounds=True, axes=ax)
    ax.legend()
    plt.savefig(mmRunDir + f"/geometryRange{'' if useLogScale else '_noLogScale'}.png")
    plt.show()
