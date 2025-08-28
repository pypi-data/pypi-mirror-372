import json
from copy import deepcopy

from tankoh2.sensitivityAnalysis.parameters import *


class parameterSet:
    def __init__(self, baseVesselFile, burstPressure, parameters):
        self.baseVesselFile = baseVesselFile
        self.burstPressure = burstPressure
        self.parameters = parameters
        self.prepareFiles()

    def prepareFiles(self):
        with open(self.baseVesselFile) as f:
            vessel = json.load(f)
            design = vessel["vessel"]["designGroup"]
            liner = {}
            liner["liner"] = vessel["vessel"]["liner"]
            numberOfLayers = design["designs"]["1"]["number_of_layers"]
            oldMaterials = {}
            for material in design["materials"]:
                oldMaterials[design["materials"][material]["uuid"]] = deepcopy(design["materials"][material])

            for layer in range(1, numberOfLayers + 1):
                design["materials"][str(layer)] = deepcopy(
                    oldMaterials[design["designs"]["1"][str(layer)]["material_uuid"]]
                )
                design["materials"][str(layer)]["name"] = (
                    design["materials"][str(layer)]["name"] + "_Layer" + str(layer)
                )
                design["materials"][str(layer)]["uuid"] = (
                    design["materials"][str(layer)]["uuid"] + "_Layer" + str(layer)
                )
                design["designs"]["1"][str(layer)]["material_uuid"] = (
                    design["designs"]["1"][str(layer)]["material_uuid"] + "_Layer" + str(layer)
                )
            design["number_of_materials"] = numberOfLayers

        self.baseCompositeFile = self.baseVesselFile + ".prepared.design"
        self.baseLinerFile = self.baseCompositeFile + ".prepared.liner"
        with open(self.baseCompositeFile, "w") as f:
            json.dump(design, f)
        with open(self.baseLinerFile, "w") as f:
            json.dump(liner, f)


class ECCMParameterSet(parameterSet):
    def __init__(self):
        baseCompositeFile = "C:/Users/jaco_li/Tools/tankoh2/save/SensitivityAnalyses/ECCM_Final/dLight_ISA.design"
        baseLinerFile = "C:/Users/jaco_li/Tools/tankoh2/save/SensitivityAnalyses/ECCM_Final/dLight_ISA.liner"
        burstPressure = 140
        innerHoop = [3, 4, 5]
        middleHoop = [9, 10, 11]
        outerHoop = [15, 16, 17]
        bossHelical = [0, 1, 2]
        lowAngleHelical = [6, 7, 8]
        midAngleHelical = [12, 13, 14]
        highAngleHelical = [18, 19, 20]
        helicalLayers = bossHelical + lowAngleHelical + midAngleHelical + highAngleHelical
        hoopLayers = innerHoop + middleHoop + outerHoop
        allLayers = hoopLayers + helicalLayers
        baseParameters = [
            E1("E1", range(0, 21), mu=168640.5, sigma=6745.62),
            E2_3("E2", range(0, 21), mu=10800.0, sigma=0.08 * 10800),
            G12_13("G12", range(0, 21), mu=5140.0, sigma=0.08 * 5140),
            nu12_13("ν12", range(0, 21), mu=0.276, sigma=0.08 * 0.276),
            R1t("X1t\nHoop", hoopLayers, distributionType="Normal", mu=2555.0, sigma=102.2),
            R1t("X1t\nHelical", helicalLayers, distributionType="Normal", mu=2555.0, sigma=102.2),
            FVC("FVC", range(0, 21), mu=0.621395, sigma=0.031),
            VC("VC", range(0, 21), mu=0.0, sigma=0.01),
            friction("Deviation\nMidAngle", midAngleHelical, mu=0, sigma=0.00016),
            friction("Deviation\nHighAngle", midAngleHelical, mu=0, sigma=0.00016),
            friction("Deviation\nLowAngle", lowAngleHelical, distributionType="TruncatedNormal", mu=0, sigma=0.00016),
            friction("Deviation\nBoss", bossHelical, distributionType="TruncatedNormal", mu=0, sigma=0.00016),
            hoopDropOff("Ply drop\ninnerHoop", innerHoop, mu=0, sigma=1),
            hoopDropOff("Ply drop\nmiddleHoop", middleHoop, mu=0, sigma=1),
            hoopDropOff("Ply drop\nouterHoop", outerHoop, mu=0, sigma=1),
        ]
        E1Parameters = [E1(f"E1_{i}", [i], mu=168640.5, sigma=6745.62) for i in range(0, 21)]
        StrengthParameters = [R1t(f"Xt_{i}", [i], mu=2555.0, sigma=102.2) for i in range(0, 21)]
        VCParameters = [VC(f"VC_{i}", [i], mu=0.0, sigma=0.01) for i in range(0, 21)]
        FVCParameters = [FVC(f"FC_{i}", [i], mu=0.621395, sigma=0.031) for i in range(0, 21)]
        FrictionParameters = [
            friction(f"Deviation_{i}", [i], mu=0, sigma=0.00016) for i in midAngleHelical + highAngleHelical
        ]
        FittingFrictionParameters = [
            friction(f"Deviation_{i}", [i], distributionType="TruncatedNormal", mu=0, sigma=0.00016)
            for i in bossHelical + lowAngleHelical
        ]
        hoopParameters = [hoopDropOff(f"hoopDrop{i}", [i], mu=0, sigma=1) for i in hoopLayers]
        fullParameters = (
            baseParameters
            + E1Parameters
            + StrengthParameters
            + VCParameters
            + FVCParameters
            + FrictionParameters
            + hoopParameters
            + FittingFrictionParameters
        )
        super().__init__(baseCompositeFile, baseLinerFile, burstPressure, baseParameters)


### NGT-BIT


class NGT_BIT_parameterSet(parameterSet):

    def __init__(self):
        baseCompositeFile = "C:/Users/jaco_li/Tools/tankoh2/save/SensitivityAnalyses/NGT_Bit/NGT-BIT-Invent-V2.design"
        baseLinerFile = "C:/Users/jaco_li/Tools/tankoh2/save/SensitivityAnalyses/NGT_Bit/NGT-BIT-Invent-V2.liner"
        burstPressure = 20
        hoopLayers = [1, 3, 5]
        fittingLayers = [0, 2, 4]
        helicalLayers = [0, 2, 4, 6]
        allLayers = hoopLayers + helicalLayers
        baseParameters = [
            E1("E1", allLayers, mu=120050.0, sigma=0.04 * 120050.0),
            E2_3("E2", allLayers, mu=8460.0, sigma=0.08 * 8460),
            G12_13("G12", allLayers, mu=3910.0, sigma=0.08 * 3910),
            nu12_13("ν12", allLayers, mu=0.317, sigma=0.08 * 0.317),
            R1t("X1t\nHoop", allLayers, distributionType="Normal", mu=2850.0, sigma=0.04 * 2850.0),
            FVC("FVC", allLayers, mu=0.602, sigma=0.0301),
            friction("Deviation\nMidAngle", [6], mu=0, sigma=0.0001),
            hoopDropOff("Ply drop\ninnerHoop", hoopLayers, mu=0, sigma=1),
        ]
        super().__init__(baseCompositeFile, baseLinerFile, burstPressure, baseParameters)


### D-Light Rear


class DLight_Rear_parameterSet(parameterSet):

    def __init__(self):
        baseVesselFile = "C:/Users/jaco_li/Tools/tankoh2/save/SensitivityAnalyses/DLight_rear/DLight_rear_final.vessel"
        burstPressure = 140
        allLayers = list(range(0, 78))
        hoopLayers = (
            list(range(0, 8)) + list(range(16, 24)) + list(range(30, 38)) + list(range(45, 53)) + list(range(60, 63))
        )
        medAngleHelicals = [11, 14, 24, 26, 28, 38, 40, 42, 53, 54, 56, 58, 59, 64, 66, 67, 68]
        highAngleHelicals = list(range(69, 78))
        lowAngleHelicals = list(set(allLayers) - set(hoopLayers) - set(medAngleHelicals) - set(highAngleHelicals) - {8})
        baseParameters = []
        baseParameters = [
            E1("E1", allLayers, mu=168640.5, sigma=0.04 * 168640.5),
            R1t("X1t\nHoop", allLayers, distributionType="Normal", mu=2555.0, sigma=0.0146 * 2555.0),
        ]
        E1Parameters = [E1(f"E1_{i}", [i], mu=168640.5, sigma=0.04 * 168640.5) for i in allLayers]
        StrengthParameters = [R1t(f"Xt_{i}", [i], mu=2555.0, sigma=0.0146 * 2555.0) for i in allLayers]
        VCParameters = [VC(f"VC_{i}", [i], mu=0.0, sigma=0.01) for i in allLayers]
        FVCParameters = [FVC(f"FC_{i}", [i], mu=0.621395, sigma=0.031) for i in allLayers]
        FrictionParameters = [
            friction(f"Deviation_{i}", [i], mu=0, sigma=0.00015) for i in medAngleHelicals + highAngleHelicals
        ]
        FittingFrictionParameters = [
            friction(f"Deviation_{i}", [i], distributionType="TruncatedNormal", mu=0, sigma=0.0001)
            for i in lowAngleHelicals
        ]
        hoopParameters = [hoopDropOff(f"hoopDrop{i}", [i], mu=0, sigma=1) for i in hoopLayers]
        baseParameters = (
            baseParameters
            + FVCParameters
            + VCParameters
            + FrictionParameters
            + FittingFrictionParameters
            + hoopParameters
        )
        super().__init__(baseVesselFile, burstPressure, baseParameters)
