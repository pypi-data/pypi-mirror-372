# SPDX-FileCopyrightText: 2023 German Aerospace Center (DLR)
#
# SPDX-License-Identifier: MIT

"""
h2 tank optimization
"""

import logging
import sys

from tankoh2.__about__ import __author__, __description__, __programDir__, __title__, __version__
from tankoh2.settings import PychainWrapper

# main program information
name = __title__
programDir = __programDir__
version = __version__
description = __description__
author = __author__


# create logger
level = logging.INFO
formatter = logging.Formatter("%(levelname)s\t%(asctime)s: %(message)s")
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(level)
handler.formatter = formatter
log = logging.getLogger(f"{name}_logger")
log.handlers.append(handler)
log.setLevel(level)

# make mycropychain available
pychainIsLoaded = False
pychain = PychainWrapper()
