# SPDX-FileCopyrightText: 2023 German Aerospace Center (DLR)
#
# SPDX-License-Identifier: MIT

"""read/write setting file"""

import json
import os
import sys
from types import NoneType

from tankoh2.arguments import allArgs
from tankoh2.service.exception import Tankoh2Error

myCrOSettings = None
exampleSettingsFileName = "settings_example.json"


class windingSettings:
    """This class stores advanced settings. All available advanced settings are listed in /designs/defaults.yaml under "Advanced Settings" """

    def __init__(self):
        settingsKeys = list(allArgs[allArgs["group"] == "Advanced Settings"]["name"])
        self.applySettings(dict((name, allArgs[allArgs["name"] == name]["default"].values[0]) for name in settingsKeys))

    def applySettings(self, settingsDict):
        for key in settingsDict:
            setattr(self, key, settingsDict[key])
            # create RNG seed for optimizer if not set or set to -1:
        if hasattr(self, "optimizerSeed"):
            # check that optimizerSeed is int or None, if provided
            if not isinstance(self.optimizerSeed, (NoneType, int)):
                raise Tankoh2Error(f'Parameter "optimizerSeed" must be int or None.')
            if self.optimizerSeed == -1:
                setattr(self, "optimizerSeed", None)


# create the settings object
settings = windingSettings()


class PychainMock:
    """This class is a mock of pychain.

    When pychain can not be imported, it stores the respective error message.
    The error will be raised when trying to access pychain attributes."""

    def __init__(self, errorMsg=None):
        self.errorMsg = errorMsg

    def __getattr__(self, item):
        from tankoh2 import log

        log.error(self.errorMsg)
        return None


class PychainWrapper:
    """This class is wrapper for the implementation of pychain.

    It is created at the beginning of the program. When a pychain function is needed for the first time,
    it attempts to import the actual pychain class. If it fails, it creates a pychainMock object instead.
    By this, tankoh2 standalone functions can be used without error messages due to missing pychain."""

    def __init__(self):
        self.pychain = None
        self.pychainIsLoaded = False

    def __getattr__(self, item):
        if not self.pychain:
            self.initializePychain()
        if self.pychain:
            return getattr(self.pychain, item)
        else:
            return None

    def initializePychain(self):
        """reads pychain location from the MYCROPYCHAINPATH environment variable and imports the module"""
        global myCrOSettings
        from tankoh2 import log

        log.info("Importing myCroPyChain API...")
        mycropychainPath = os.environ.get("MYCROPYCHAINPATH", None)
        if not mycropychainPath:
            # Old Behavior, search in settings file
            log.info(
                "Environment variable MYCROPYCHAINPATH not set. Trying to find it from settings file (deprecated method)."
            )
            defaultSettingsFileName = "settings.json"
            searchDirs = [".", os.path.dirname(__file__), os.path.dirname(os.path.dirname(os.path.dirname(__file__)))]
            filename = None
            for searchDir in searchDirs:
                if defaultSettingsFileName in os.listdir(searchDir):
                    # look for settings file in actual folder
                    filename = os.path.join(searchDir, defaultSettingsFileName)
            if filename is None:
                writeSettingsExample()
                self.pychain = PychainMock(
                    f'Could not find the settings file "{defaultSettingsFileName}" in the '
                    f"following folders: {searchDirs}.\n"
                    f"An example settings file is written to ./{exampleSettingsFileName}.\n"
                    f"Please add the required settings and rename the file to "
                    f'{exampleSettingsFileName.replace("_example", "")}.'
                    f"Alternatively, set the environment variable MYCROPYCHAINPATH to the correct path."
                )
                return False

            with open(filename, "r") as f:
                oldSettings = json.load(f)
                mycropychainPath = oldSettings["mycropychainPath"]

        #############################################################################
        # Read pychain and abq_pychain path and put it in sys.path
        #############################################################################
        # v0.95.3
        major, minor = str(sys.version_info.major), str(sys.version_info.minor)
        pyVersionString = f"{major}_{minor}"
        pythonApiPath = os.path.join(mycropychainPath, f"pythonAPI", f"{pyVersionString}")
        if not os.path.exists(pythonApiPath):
            # v 0.90c
            pythonApiPath = os.path.join(mycropychainPath, f"pythonAPI", f"python{pyVersionString}_x64")
            if not os.path.exists(pythonApiPath):
                # v 0.95.2
                pythonApiPath = os.path.join(mycropychainPath, f"pythonAPI", f"python{pyVersionString}")
        # abaqusPythonLibPath = os.path.join(mycropychainPath, 'abaqus_interface_0_89')
        abaqusPythonLibPath = os.path.join(mycropychainPath, "abaqus_interface_0_95_4")

        log.info(f"Append mycropychain path to sys path: {pythonApiPath}")
        sys.path.append(pythonApiPath)
        pychainActive = True
        # import API - MyCrOChain GUI with activated TCP-Connector needed
        try:
            # v <= 0.90
            import mycropychain as pychain
        except ModuleNotFoundError:
            # v > 0.90
            try:
                if minor == "6":
                    import mycropychain36 as pychain
                elif minor == "8":
                    import mycropychain38 as pychain
                elif minor == "10":
                    previousWorkingDir = os.getcwd()
                    os.chdir(pythonApiPath)
                    import mycropychain310 as pychain

                    os.chdir(previousWorkingDir)
                else:
                    raise Tankoh2Error(f"Python Version {major}.{minor} is not compatible with mycroWind API")
            except (ModuleNotFoundError, FileNotFoundError):
                self.pychain = PychainMock(
                    "Could not find package 'mycropychain'. Please check the path to myCroChain main directory in the MYCROPYCHAINPATH environment variable."
                )
                log.info("Import Failed")
                self.pychainIsLoaded = False
                return False
            else:
                if len(pychain.__dict__) < 10:
                    pychainActive = False
        else:
            if len(pychain.__dict__) < 10:
                pychainActive = False

        if not pychainActive:
            self.pychain = PychainMock(
                "Could not connect to mycropychain GUI. " 'Did you start the GUI and activated "TCP Conn."?'
            )
            log.info("Import Failed")
            self.pychainIsLoaded = False
            # len(pychain.__dict__) was 8 on failure and 17 on success
        else:
            self.pychain = pychain
            # set general path information
            myCrOSettings = pychain.utility.MyCrOSettings()
            myCrOSettings.abaqusPythonLibPath = abaqusPythonLibPath
            log.info("mycropychain import Successful")
            self.pychainIsLoaded = True
        return self.pychainIsLoaded


def writeSettingsExample():
    """writes an example for settings"""
    from tankoh2 import log

    log.info(f"write file {exampleSettingsFileName}")
    with open(exampleSettingsFileName, "w") as f:
        json.dump(
            {
                "comment": "Please rename this example file to 'settings.json' and set "
                "'mycropychainPath' to run µWind. For paths in Windows, please use '\\' or '/'",
                "mycropychainPath": "",
            },
            f,
            indent=2,
        )


if __name__ == "__main__":
    writeSettingsExample()
