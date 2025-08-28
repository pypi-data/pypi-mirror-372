import logging
import os
from datetime import datetime

import defusedxml.ElementTree as ET  # Package Documentation: https://docs.python.org/3/library/xml.etree.elementtree.html
import yaml

from tankoh2 import log, programDir
from tankoh2.service.utilities import writeParametersToYAML


class tankFromCpacs:
    def __init__(self, cpacsName, tankuID):
        """
        This class imports a cpacs-tank-file and holds its parameters as a dictionary-attribute. With the method
        outputData(), the dictionary can be converted into a tankoh2 readable yaml-file. Change the directories of
        self.cpacsDirectory, self.logDirectory and self.yamlDirectory according to your project or use case.
        @param cpacsName: Name of the cpacs-file to be imported
        @param tankuID: uID of the generic fuel tank to be imported from the cpacs-file
        """
        self.isParameterCpacs = True
        self.tankDictionary = {}
        self.cpacsDirectory = "../../cpacsfiles/"
        self.logDirectory = "../../logCpacsImport/"
        self.yamlDirectory = "../../outputYamlFile/"
        lengthName = len(cpacsName)
        self.yamlName = cpacsName[: (lengthName - 4)] + "Tankoh2Config"  # to avoid .xml in the Yaml-file name
        self.tankuID = tankuID
        self.importCpacsData(self.cpacsDirectory + cpacsName)

    def outputData(self, writeYamlFile=False):
        """
        The Data output is handled by this method. Currently, "writeTankoH2ConfigDictionary()" is used. If you want to output
        the data in another way, replace or overwrite "writeTankoH2ConfigDictionary()" by your own method. Of course,
        you can also extend this method.
        """
        tankOH2Dictionary = self.writeTankoH2ConfigDictionary()

        if writeYamlFile:
            file = open(self.yamlDirectory + self.yamlName, "w")
            yaml.dump(tankOH2Dictionary, file)
            file.close()
            logging.info(f"TankOH2 readable yaml-file saved at: {self.yamlDirectory + self.yamlName}")
        return tankOH2Dictionary

    def importCpacsData(self, cpacsPath):
        tree = ET.parse(cpacsPath)
        root = tree.getroot()
        time = datetime.now()
        filename = "tankFromCpacs" + str(time.hour) + "_" + str(time.minute) + "_" + str(time.second) + "log"
        logging.basicConfig(filename=self.logDirectory + filename, level=logging.INFO, filemode="a")
        logging.info(time.isoformat())
        logging.info("XMLfile:")
        logging.info(cpacsPath)

        foundTank = False
        for genericFuelTank in root.iter("genericFuelTank"):
            if genericFuelTank.get("uID") == self.tankuID:
                self.genericFuelTank = genericFuelTank
                foundTank = True
                break
        if foundTank is False:
            logging.info("Generic fuel tank with the specified uID has not been found in the cpacs-file")

            raise Exception("Generic fuel tank with the specified uID has not been found in the cpacs-file")

        self.isAParameterCpacs()
        if self.isParameterCpacs:
            self.importParameterCpacs()
        else:
            self.importHullsCpacs()

    def isAParameterCpacs(self):
        self.designParameters = self.genericFuelTank.find("designParameters")  # search for a "designParameters-Node
        if self.designParameters is not None:  # if a "designParameters-Node is there:"
            self.cylinderRadius = self.designParameters.find("cylinderRadius")  # search for a "cylinderRadius-Node
            if self.cylinderRadius is not None:  # if a "cylinderRadius-Node is there:"
                self.isParameterCpacs = True  # The genericFuelTank is considered as the "designParameters" version
                logging.info("The genericFuelTank is considered as the designParameters version")
            else:
                self.isParameterCpacs = False
                logging.info("The genericFuelTank is considered as the hull version")
        else:
            self.isParameterCpacs = False
            logging.info("The genericFuelTank is considered as the hull version")

    def importParameterCpacs(self):
        self.tankDictionary["cylinderRadius"] = float(self.designParameters.find("cylinderRadius").text)
        self.tankDictionary["cylinderLength"] = float(self.designParameters.find("cylinderLength").text)
        self.Dome = self.designParameters.find("domeType")
        domeList = ["isotensoid", "ellipsoid", "spherical", "torispherical"]
        for node in self.Dome[0].iter():
            if any(node.tag in string for string in domeList):
                self.tankDictionary["domeType"] = node.tag
            else:
                self.tankDictionary[node.tag] = float(node.text)
        self.tankDictionary["burstPressure"] = float(self.genericFuelTank.find("burstPressure").text)
        logging.info("Imported values from xml:")
        logging.info(self.tankDictionary)

    def importHullsCpacs(self):
        pass  # Todo to be implemented

    def writeTankoH2ConfigDictionary(self):
        if self.isParameterCpacs:
            tankDictionaryPython = self.tankDictionary.copy()
            tankDictionaryPython.pop("burstPressure")  # remove "burstPressure since it is not used in tankOH2"
            keys2tankOH2 = {
                "cylinderRadius": "dcyl",
                "cylinderLength": "lcyl",
                "domeType": "domeType",
                "polarOpeningRadius": "polarOpeningRadius",
                "dishRadius": "r1ToD0",
                "knuckleRadius": "r2ToD0",
                "halfAxisFraction": "dome2LengthByR",
            }
            units2tankOH2 = {
                "cylinderRadius": 1000,
                "cylinderLength": 1000,
                "polarOpeningRadius": 1000,
                "dishRadius": 1000,
                "knuckleRadius": 1000,
                "halfAxisFraction": 1000,
            }

            parameterValueTranslate = {"domeType": {"spherical": "circle", "ellipsoid": "ellipse"}}
            # Replace parameter values in tankDictionaryPython:
            for key, value in parameterValueTranslate.items():  # for all items in parameterValueTranslate
                if tankDictionaryPython.get(key) is not None:  # if key is in tankDictionaryPython
                    if value.get(tankDictionaryPython[key]) is not None:  # if parameter value is in subdirectory
                        tankDictionaryPython[key] = value[
                            tankDictionaryPython[key]
                        ]  # translate the parameter value in tankDictionaryPython
            # Create a new dictionary in tankOH2 language:
            tankDictionaryTankOH2 = {}
            for key, value in tankDictionaryPython.items():
                if units2tankOH2.get(key) is not None:
                    tankDictionaryTankOH2[keys2tankOH2[key]] = value * units2tankOH2[key]
                else:
                    tankDictionaryTankOH2[keys2tankOH2[key]] = value

        else:
            raise Exception("Generic fuel tank of type hull yet not supported")

        return tankDictionaryTankOH2


"""The class tankFromCpacs works as a stand-alone solution,
in configfromCpacs some methods are overwritten for better integration into tankoh2 """


class configFromCpacs(tankFromCpacs):
    def __init__(self, cpacsName, tankuID):
        """
        This class imports a cpacs-tank-file and holds its parameters as a dictionary-attribute. With the method
        outputData(), the dictionary can be converted into a tankoh2 readable yaml-file. Change the directories of
        self.cpacsDirectory, self.logDirectory and self.yamlDirectory according to your project or use case.
        @param cpacsName: Name of the cpacs-file to be imported
        @param tankuID: uID of the generic fuel tank to be imported from the cpacs-file
        """
        self.isParameterCpacs = True
        self.tankDictionary = {}
        self.cpacsDirectory = os.path.join(programDir, "cpacs")
        self.yamlDirectory = os.path.join(programDir, "designs")
        lengthName = len(cpacsName)
        self.yamlName = cpacsName[: (lengthName - 4)] + "tankoH2Config"  # to avoid .xml in the Yaml-file name
        self.tankuID = tankuID
        self.importCpacsData(self.cpacsDirectory + "/" + cpacsName)

    def outputData(self, writeYamlFile=False):
        """
        The Data output is handled by this method. Currently, "writeTankoH2ConfigDictionary()" is used. If you want to output
        the data in another way, replace or overwrite "writeTankoH2ConfigDictionary()" by your own method. Of course,
        you can also extend this method.
        """
        tankOH2Dictionary = self.writeTankoH2ConfigDictionary()

        if writeYamlFile:
            writeParametersToYAML(tankOH2Dictionary, self.yamlDirectory + "/" + self.yamlName)
            log.info(f"TankOH2 readable yaml-file saved at: {self.yamlDirectory + self.yamlName}")
        return tankOH2Dictionary

    def importCpacsData(self, cpacsPath):
        tree = ET.parse(cpacsPath)
        root = tree.getroot()
        log.info("__Import of Config from Cpacs__")
        log.info(f"XMLfile: {cpacsPath}")

        foundTank = False
        for genericFuelTank in root.iter("genericFuelTank"):
            if genericFuelTank.get("uID") == self.tankuID:
                self.genericFuelTank = genericFuelTank
                foundTank = True
                break
        if foundTank is False:
            log.info("Generic fuel tank with the specified uID has not been found in the cpacs-file")

            raise Exception("Generic fuel tank with the specified uID has not been found in the cpacs-file")

        self.isAParameterCpacs()
        if self.isParameterCpacs:
            self.importParameterCpacs()
        else:
            self.importHullsCpacs()

    def isAParameterCpacs(self):
        self.designParameters = self.genericFuelTank.find("designParameters")  # search for a "designParameters-Node
        if self.designParameters is not None:  # if a "designParameters-Node is there:"
            self.cylinderRadius = self.designParameters.find("cylinderRadius")  # search for a "cylinderRadius-Node
            if self.cylinderRadius is not None:  # if a "cylinderRadius-Node is there:"
                self.isParameterCpacs = True  # The genericFuelTank is considered as the "designParameters" version
                log.info("The genericFuelTank is considered as the designParameters version")
            else:
                self.isParameterCpacs = False
                log.info("The genericFuelTank is considered as the hull version")
        else:
            self.isParameterCpacs = False
            log.info("The genericFuelTank is considered as the hull version")

    def importParameterCpacs(self):
        self.tankDictionary["cylinderRadius"] = float(self.designParameters.find("cylinderRadius").text)
        self.tankDictionary["cylinderLength"] = float(self.designParameters.find("cylinderLength").text)
        self.Dome = self.designParameters.find("domeType")
        domeList = ["isotensoid", "ellipsoid", "spherical", "torispherical"]
        for node in self.Dome[0].iter():
            if any(node.tag in string for string in domeList):
                self.tankDictionary["domeType"] = node.tag
            else:
                self.tankDictionary[node.tag] = float(node.text)
        self.tankDictionary["burstPressure"] = float(self.genericFuelTank.find("burstPressure").text)
        log.info("Imported values from xml:")
        log.info(self.tankDictionary)


if __name__ == "__main__":
    "Demonstration of the class configFromCpacs:"
    tank = configFromCpacs("defaultParametricCryoTank.xml", "CryoFuelTank")
    print("This dictionary contains all imported values:")
    print(tank.tankDictionary)
    tank.outputData(writeYamlFile=True)
    print("TankOH2 readable yaml-file saved in /designs")
