from abc import abstractmethod

import numpy as np
import openturns as ot
from scipy import special

from tankoh2 import pychain
from tankoh2.service.exception import Tankoh2Error


class Parameter:
    def __init__(self, name, distributionType="Normal", mu=None, sigma=None, shape=None, scale=None):
        self.name = name
        self.distributionType = distributionType
        self.mu = mu
        self.sigma = sigma
        self.shape = shape
        self.scale = scale

    def createDistribution(self):
        if self.distributionType == "Normal":
            if self.mu is not None and self.sigma is not None:
                return ot.Normal(self.mu, self.sigma)
            else:
                raise Tankoh2Error("mu and sigma not defined for normal distribution.")
        if self.distributionType == "TruncatedNormal":
            if self.mu is not None and self.sigma is not None:
                return ot.TruncatedNormal(self.mu, self.sigma, self.mu - 3 * self.sigma, self.mu + 3 * self.sigma)
            else:
                raise Tankoh2Error("mu and sigma not defined for truncated normal distribution.")
        elif self.distributionType == "Lognormal":
            if self.mu is not None and self.sigma is not None:
                return ot.LogNormal(self.mu, self.sigma)
            else:
                raise Tankoh2Error(f"mu and sigma not defined for lognormal distribution")
        elif self.distributionType == "Weibull":
            if self.scale is not None and self.shape is not None:
                return ot.WeibullMin(self.scale, self.shape)
        else:
            raise Tankoh2Error(f"Unknown distribution type: {self.distributionType}")


class MaterialParameter(Parameter):
    def __init__(self, name, layers, distributionType="Normal", mu=None, sigma=None, shape=None, scale=None):
        super().__init__(name, distributionType, mu, sigma, shape, scale)
        self.layers = layers

    def setMaterialParameter(self, value, composite):
        """Set the Parameter to the specified value inside the composite object"""
        for layer in self.layers:
            self.setMaterialParameterForLayer(value, composite, layer)

    @abstractmethod
    def setMaterialParameterForLayer(self, value, composite, layer):
        """Set the Parameter to the specified value inside the composite object"""


class CompositeParameter(Parameter):
    def __init__(self, name, layers, distributionType="Normal", mu=None, sigma=None, shape=None, scale=None):
        super().__init__(name, distributionType, mu, sigma, shape, scale)
        self.layers = layers

    def setCompositeParameter(self, value, composite):
        """Set the Parameter to the specified value inside the composite object"""
        for layer in self.layers:
            self.setCompositeParameterForLayer(value, composite, layer)

    @abstractmethod
    def setCompositeParameterForLayer(self, value, composite, layer):
        """Set the Parameter to the specified value inside the composite object"""


class VesselParameter(Parameter):
    def __init__(self, name, layers, distributionType="Normal", mu=None, sigma=None, shape=None, scale=None):
        super().__init__(name, distributionType, mu, sigma, shape, scale)
        self.layers = layers

    def setVesselParameter(self, value, vessel):
        """Set the Parameter to the specified value inside the vessel object"""
        for layer in self.layers:
            self.setVesselParameterForLayer(value, vessel, layer)

    @abstractmethod
    def setVesselParameterForLayer(self, value, vessel, layer):
        """Set the Parameter to the specified value inside the composite object"""


class LinerParameter(Parameter):
    def __init__(self, name, distributionType="Normal", mu=None, sigma=None, shape=None, scale=None):
        super().__init__(name, distributionType, mu, sigma, shape, scale)

    @abstractmethod
    def setLinerParameter(self, value, liner, deltaSpline):
        """Set the Parameter to the specified value inside the vessel object"""


class Angle(CompositeParameter):
    def setCompositeParameterForLayer(self, value, composite, layer):
        composite.setLayerAngle(layer, value)


class FVC(CompositeParameter):
    def setCompositeParameterForLayer(self, value, composite, layer):
        # Sets FVC, adjusts Thickness, adjust Tensile Strength
        material = composite.getMaterialPyChain(layer)
        composite.getOrthotropLayer(layer).phi = value
        composite.setLayerThickness(layer, composite.getLayerThicknessFromWindingProps(layer))

        puckProperties = material.puckProperties
        puckProperties.R_1_c = puckProperties.R_1_t  # Save Old Value
        alpha = 6.0
        strength_m = 50
        Method = "Cohen"
        if Method == "Cohen":
            puckProperties.R_1_t = self.strength_scaling(
                self.mu, puckProperties.R_1_t, value, alpha, strength_m
            )  # Simplification of Cohen2001

            puckProperties.R_1_t = puckProperties.R_1_t / (value / self.mu)
        else:
            pass

        material.puckProperties = puckProperties
        composite.setLayerMaterial(layer, material)

    def strength_scaling(self, Vf1, strength_1, Vf2, alpha, strength_m):
        strength_2 = (strength_1 - (1 - Vf1) * strength_m) * (Vf2 / Vf1) * (
            (Vf2 / Vf1) * (1 - np.sqrt(Vf1)) / (1 - np.sqrt(Vf2))
        ) ** (1 / (2 * alpha)) + (1 - Vf2) * strength_m
        return strength_2

    def strength_scaling_old(self, Vf1, strength_1, Vf2, alpha):
        strength_2 = (
            strength_1 * (Vf2 / Vf1) * ((Vf2 / Vf1) * (1 - np.sqrt(Vf1)) / (1 - np.sqrt(Vf2))) ** (1 / (2 * alpha))
        )
        return strength_2

    def tsai_strength_function(self, E_f, E_m, V_f, d_f, weibull_shape, L, R_t_mean, R_m_mean):
        loadTransferLength = d_f * np.sqrt((3 * E_f / (2 * E_m) * (1 - np.sqrt(V_f)) / np.sqrt(V_f)))
        R_c = (
            1
            / ((weibull_shape * np.e) ** (1 / weibull_shape) * special.gamma(1 + 1 / weibull_shape))
            * (L / loadTransferLength)
            * V_f
            * R_t_mean
            + (1 - V_f) * R_m_mean
        )
        return R_c


class VC(CompositeParameter):
    def setCompositeParameterForLayer(self, value, composite, layer):
        # Empirical Observation: 1% Void reduces linear characteristics by 1%
        material = composite.getMaterialPyChain(layer)
        puckProperties = material.puckProperties
        puckProperties.R_1_t = puckProperties.R_1_t * (1 - value)  # Linear Assumption
        puckProperties.R_1_c = puckProperties.R_1_c * (1 - value)  # Linear Assumption
        material.puckProperties = puckProperties
        elasticProperties = material.elasticProperties
        elasticProperties.E_2 = elasticProperties.E_2 * (1 - value * 10)
        elasticProperties.E_3 = elasticProperties.E_3 * (1 - value * 10)
        elasticProperties.G_12 = elasticProperties.G_12 * (1 - value * 10)
        material.elasticProperties = elasticProperties
        composite.setLayerMaterial(layer, material)


class E1(MaterialParameter):
    def setMaterialParameterForLayer(self, value, composite, layer):
        material = composite.getMaterialPyChain(layer)
        elasticProperties = material.elasticProperties
        elasticProperties.E_1 = value
        material.elasticProperties = elasticProperties
        composite.setLayerMaterial(layer, material)


class E2_3(MaterialParameter):
    def setMaterialParameterForLayer(self, value, composite, layer):
        material = composite.getMaterialPyChain(layer)
        elasticProperties = material.elasticProperties
        elasticProperties.E_2 = value
        elasticProperties.E_3 = value
        material.elasticProperties = elasticProperties
        composite.setLayerMaterial(layer, material)


class E3(MaterialParameter):
    def setMaterialParameterForLayer(self, value, composite, layer):
        material = composite.getMaterialPyChain(layer)
        elasticProperties = material.elasticProperties
        elasticProperties.E_3 = value
        material.elasticProperties = elasticProperties
        composite.setLayerMaterial(layer, material)


class G12_13(MaterialParameter):
    def setMaterialParameterForLayer(self, value, composite, layer):
        material = composite.getMaterialPyChain(layer)
        elasticProperties = material.elasticProperties
        elasticProperties.G_12 = value
        elasticProperties.G_13 = value
        material.elasticProperties = elasticProperties
        composite.setLayerMaterial(layer, material)


class nu12_13(MaterialParameter):
    def setMaterialParameterForLayer(self, value, composite, layer):
        material = composite.getMaterialPyChain(layer)
        elasticProperties = material.elasticProperties
        elasticProperties.nu_12 = value
        elasticProperties.nu_13 = value

        material.elasticProperties = elasticProperties
        composite.setLayerMaterial(layer, material)


class nu23(MaterialParameter):
    def setMaterialParameterForLayer(self, value, composite, layer):
        material = composite.getMaterialPyChain(layer)
        elasticProperties = material.elasticProperties
        elasticProperties.nu_23 = value
        material.elasticProperties = elasticProperties
        composite.setLayerMaterial(layer, material)


class R1t(MaterialParameter):
    def setMaterialParameterForLayer(self, value, composite, layer):
        material = composite.getMaterialPyChain(layer)
        puckProperties = material.puckProperties
        puckProperties.R_1_t = value
        puckProperties.R_1_c = value
        material.puckProperties = puckProperties
        composite.setLayerMaterial(layer, material)


class hoopDropOff(VesselParameter):
    def setVesselParameterForLayer(self, value, vessel, layer):
        currentShift = vessel.getHoopLayerShift(layer, True)
        vessel.setHoopLayerShift(layer, currentShift + value, True)


class friction(VesselParameter):
    def setVesselParameterForLayer(self, value, vessel, layer):
        vessel.setLayerFriction(layer, value, True)


class linerDiameter(LinerParameter):
    def setLinerParameter(self, value, liner, deltaSpline):
        dome = liner.getDome1()
        dome.buildDome(value / 2, 23, pychain.winding.DOME_TYPES.ISOTENSOID)
        liner.buildFromDome(dome, liner.cylinderLength, deltaSpline)


if __name__ == "__main__":
    alpha_test = 2000.0
    strength_m_test = 61
    FVC6 = FVC("FVC", 6, mu=0.603, sigma=0.03015)
    print(FVC6.strength_scaling(0.6, 2650, 0.6, alpha_test, strength_m_test))
    print(FVC6.strength_scaling(0.65, 2921.0932, 0.6, alpha_test, strength_m_test))

    print(FVC6.strength_scaling_old(0.6, 2650, 0.6, alpha_test))
    print(FVC6.strength_scaling(0.6, 2650, 0.65, alpha_test, strength_m_test))
    print(FVC6.strength_scaling_old(0.6, 2650, 0.65, alpha_test))
    print((2650 - 0.4 * 61) * 0.65 / 0.6 + 61 * 0.35)
