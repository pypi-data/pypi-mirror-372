import json
import os
from collections import OrderedDict

import numpy as np
import patme
from patme.mechanics.material import MaterialDefinition as MaterialDefinitionPatme

from tankoh2 import log, programDir
from tankoh2.service.exception import Tankoh2Error

directions = OrderedDict(((11, 0), (22, 1), (12, 2)))  # dict referencing to index of stress array


class MaterialDefinition(MaterialDefinitionPatme):
    """Material class for tankoh2. It adds only µWind specific additional properties"""

    def getFromMuWindMaterial(self, materialMuWind):
        """Converts a pychain.material.OrthotropMaterial to patme.mechanics.material.MaterialDefinition."""

        self.id = materialMuWind.name
        self.name = materialMuWind.name

        stiffnessMuWind = materialMuWind.elasticProperties
        self.setStiffnessMatrix(
            stiffnessMuWind.E_1, stiffnessMuWind.G_12, stiffnessMuWind.E_2, stiffnessMuWind.nu_12, stiffnessMuWind.nu_23
        )

        puckProperties = materialMuWind.puckProperties
        self.strength = {
            "sigma11t": puckProperties.R_1_t,
            "sigma11c": puckProperties.R_1_c,
            "sigma22t": puckProperties.R_2_t,
            "sigma22c": puckProperties.R_2_c,
            "tau": puckProperties.R_21,
        }

        self.rho = materialMuWind.calculateDensity()

        thermalProperties = materialMuWind.thermalProperties
        # patme: XX XY XZ YY YZ ZZ
        self.thermalExpansionCoeff = np.array(
            [thermalProperties.alpha_1, 0, 0, thermalProperties.alpha_2, 0, thermalProperties.alpha_3]
        )
        return self

    def getMaterialFromMuWindJsonFile(self, muWindJsonFile):
        """"""
        if not os.path.exists(muWindJsonFile):
            raise FileNotFoundError(f"could not find file {muWindJsonFile}")
        with open(muWindJsonFile, "r") as f:
            muWindJsonData = json.load(f)
        elasticProperties = muWindJsonData["materials"]["1"]["elasticProperties"]
        thermalProperties = muWindJsonData["materials"]["1"]["thermalProperties"]
        puckProperties = muWindJsonData["materials"]["1"]["puckProperties"]

        elProps = [
            elasticProperties["E_1"],
            elasticProperties["G_12"],
            elasticProperties["E_2"],
            elasticProperties["nu_12"],
            elasticProperties["nu_23"],
        ]
        if (
            abs(elasticProperties["E_2"] - elasticProperties["E_3"]) > patme.epsilon
            or abs(elasticProperties["nu_12"] - elasticProperties["nu_13"]) > patme.epsilon
        ):
            elProps.extend(
                [
                    elasticProperties["E_3"],
                    elasticProperties["G_23"],
                    elasticProperties["G_13"],
                    elasticProperties["nu_13"],
                ]
            )
        self.setStiffnessMatrix(*elProps)

        self.strength = {
            "sigma11t": puckProperties["R_1_t"],
            "sigma11c": puckProperties["R_1_c"],
            "sigma22t": puckProperties["R_2_t"],
            "sigma22c": puckProperties["R_2_c"],
            "tau": puckProperties["R_21"],
        }

        # patme: XX XY XZ YY YZ ZZ
        self.thermalExpansionCoeff = np.array(
            [thermalProperties["alpha_1"], 0, 0, thermalProperties["alpha_2"], 0, thermalProperties["alpha_3"]]
        )
        return self


class FrpMaterialFatigueProperties:
    def __init__(self, **kwargs):
        self.A_11 = None
        self.B_11 = None
        self.u_11 = None
        self.v_11 = None
        self.A_22 = None
        self.B_22 = None
        self.u_22 = None
        self.v_22 = None
        self.A_12 = None
        self.B_12 = None
        self.u_12 = None
        self.v_12 = None
        self.beta_1_11t = None
        self.beta_1_11c = None
        self.beta_1_22t = None
        self.beta_1_22c = None
        self.beta_1_12 = None
        self.beta_2_11t = None
        self.beta_2_11c = None
        self.beta_2_22t = None
        self.beta_2_22c = None
        self.beta_2_12 = None
        self.R_1_t = None
        self.R_1_c = None
        self.R_2_t = None
        self.R_2_c = None
        self.R_21 = None

        self._applyAttrs(**kwargs)

    def _applyAttrs(self, **kwargs):
        for key in kwargs:
            if not hasattr(self, key):
                log.debug(f'Unknown key "{key}" in class {self.__class__} with name "{str(self)} will be omitted"')
                continue
            setattr(self, key, kwargs[key])

    def readMaterial(self, materialFilename):
        """reads material properties from material filename. If materialFilename does not point to a file,
        it is assumed, that it references a file in tankoh2/data"""
        if not os.path.exists(materialFilename):
            materialFilename = os.path.join(programDir, "data", materialFilename)
        with open(materialFilename) as file:
            jsonDict = json.load(file)
        self._applyAttrs(**jsonDict["materials"]["1"]["umatProperties"]["data_sets"]["1"]["umatPuckProperties"])
        self._applyAttrs(**jsonDict["materials"]["1"]["umatProperties"]["data_sets"]["1"]["fatigueProperties"])
        return self

    def getStrengths(self, direction):
        if direction not in directions:
            raise Tankoh2Error(f"direction {direction} not in allDirections {directions}")
        if direction == 11:
            return self.R_1_t, self.R_1_c
        elif direction == 22:
            return self.R_2_t, self.R_2_c
        else:
            return self.R_21, self.R_21

    def getUV(self, direction):
        if direction not in directions:
            raise Tankoh2Error(f"direction {direction} not in allDirections {directions}")
        if direction == 11:
            return self.u_11, self.v_11
        elif direction == 22:
            return self.u_22, self.v_22
        else:
            return self.u_12, self.v_12

    def getCD(self, direction):
        if direction not in directions:
            raise Tankoh2Error(f"direction {direction} not in allDirections {directions}")
        if direction == 11:
            return self.A_11, self.B_11
        elif direction == 22:
            return self.A_22, self.B_22
        else:
            return self.A_12, self.B_12
