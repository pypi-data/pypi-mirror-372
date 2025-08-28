# SPDX-FileCopyrightText: 2023 German Aerospace Center (DLR)
#
# SPDX-License-Identifier: MIT

import numpy as np
from CoolProp.CoolProp import PropsSI

medium = "Hydrogen"
psiToMPaFac = 6.89476
MPaToPsiFac = 1 / psiToMPaFac
g = 9.81  # m/s**2

arrayOrScalar = lambda x: np.array(x) if hasattr(x, "__len__") else x

# rho in [kg/m**3]
rhoLh2ByTSaturation = lambda T: PropsSI("D", "T", arrayOrScalar(T), "Q", 0, medium)  # T in K
rhoGh2ByTSaturation = lambda T: PropsSI("D", "T", arrayOrScalar(T), "Q", 1, medium)  # T in K
rhoLh2ByPSaturation = lambda p: PropsSI("D", "P", arrayOrScalar(p) * 1e6, "Q", 0, medium)  # p in MPa
rhoGh2ByPSaturation = lambda p: PropsSI("D", "P", arrayOrScalar(p) * 1e6, "Q", 1, medium)  # p in MPa

pressureLh2Saturation = lambda T: PropsSI("P", "T", arrayOrScalar(T), "Q", 0, medium)  # T in K
pressureGh2Saturation = lambda T: PropsSI("P", "T", arrayOrScalar(T), "Q", 1, medium)  # T in K

rhoByPTh2 = lambda p, T: PropsSI("D", "T", arrayOrScalar(T), "P", arrayOrScalar(p) * 1e6, medium)  # T in K, p in MPa
pressureByRhoTh2 = lambda rho, T: PropsSI("P", "T", arrayOrScalar(T), "D", arrayOrScalar(rho), medium)  # T in K

if __name__ == "__main__":
    print(rhoByPTh2(0.1, 273))
    print(rhoByPTh2(70, 293))
    print(rhoByPTh2(35, 293))
    print(rhoLh2ByTSaturation(20.3))
    print(rhoLh2ByPSaturation(0.2), rhoLh2ByPSaturation(0.25))
    print(pressureLh2Saturation(20.3))
