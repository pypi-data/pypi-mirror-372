# SPDX-FileCopyrightText: 2023 German Aerospace Center (DLR)
#
# SPDX-License-Identifier: MIT

from collections import OrderedDict

# see https://gitlab.dlr.de/freu_se_projects/lh2tank_doc

insulationDens = OrderedDict(
    [
        ("Rohacell41S", 35.24),  # Source: Brewer [kg/m^3]
    ]
)

linerDens = OrderedDict(
    [
        ("PVDF", 1500),  # kg/m^3
        ("PA6", 1140),  # kg/m^3
        ("PA12", 1050),  # kg/m^3
    ]
)

fairingDens = OrderedDict([("Kevlar", 1440)])  # kg/m3
