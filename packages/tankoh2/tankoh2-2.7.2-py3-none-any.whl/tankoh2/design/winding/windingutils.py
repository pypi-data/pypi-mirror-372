# SPDX-FileCopyrightText: 2023 German Aerospace Center (DLR)
#
# SPDX-License-Identifier: MIT
"""utility functions for µWind objects"""


import json
import shutil

import numpy as np
import pandas as pd

from tankoh2 import log
from tankoh2.service.exception import Tankoh2Error
from tankoh2.service.utilities import indent

hoopLayerAngleThreshold = 88  # degrees, angle above which the layer is considered a hoop layer


def getAnglesFromVesselCylinder(vessel):
    """returns a list with the cylindrical angles from the vessel"""
    return np.rad2deg(
        [
            vessel.getVesselLayer(layerNumber).getVesselLayerElement(0, True).clairaultAngle
            for layerNumber in range(vessel.getNumberOfLayers())
        ]
    )


def getHoopShiftsFromVessel(vessel):
    """Returns a list with all hoop shifts for side 1 and side2 using zero for helical layers"""
    side1hoops = [vessel.getHoopLayerShift(layerNumber, True) for layerNumber in range(vessel.getNumberOfLayers())]
    side2hoops = [vessel.getHoopLayerShift(layerNumber, False) for layerNumber in range(vessel.getNumberOfLayers())]
    return side1hoops, side2hoops


def checkAnglesAndShifts(anglesAndShifts, vessel):
    """Compares the tankoh2 "anglesAndShifts" with the ones defined in the vessel object

    :param anglesAndShifts: list [(angle1, shift1, shift2), () ...]
    :param vessel: µWind vessel instance
    :raises: Tankoh2Error if angles and shifts do not match
    """
    anglesVessel = getAnglesFromVesselCylinder(vessel)
    side1hoopsVessel, side2hoopsVessel = getHoopShiftsFromVessel(vessel)
    anglesAndShiftsT = np.array(anglesAndShifts).T
    symtank = vessel.isSymmetric()
    if symtank:
        if not np.allclose(side1hoopsVessel, side2hoopsVessel, rtol=6e-2):
            msgTable = [["tankoh2 tank is symmetric ", "hoop shift side 1", "hoop shift side 2"]]
            msgTable += list(zip(str(symtank), side1hoopsVessel, side2hoopsVessel))
            msgTable = indent(msgTable)
            log.error("\n" + msgTable)
            raise Tankoh2Error(f"Shifts must match for a symmetric tank. \n{msgTable}")

    if not np.allclose(anglesAndShiftsT, [anglesVessel, side1hoopsVessel, side2hoopsVessel], rtol=6e-2):
        msgTable = [
            [
                "tankoh2 angle",
                "µWind angle",
                "tankoh2 shift side 1",
                "µWind shift side 1",
                "tankoh2 shift side 2",
                "µWind shift side 2",
            ]
        ]
        msgTable += list(
            zip(
                anglesAndShiftsT[0],
                anglesVessel,
                anglesAndShiftsT[1],
                side1hoopsVessel,
                anglesAndShiftsT[2],
                side2hoopsVessel,
            )
        )
        msgTable = indent(msgTable)
        log.error("\n" + msgTable)
        raise Tankoh2Error(f"Angles and shifts do not match. \n{msgTable}")


def getLayerThicknesses(vessel, symmetricContour, layerNumbers=None):
    """returns a dataframe with thicknesses of each layer along the whole vessel

    :param vessel: vessel obj
    :param symmetricContour: flag if symmetric contour is used
    :param layerNumbers: list of layers that should be evaluated. If None, all layers are used
    :return:
    """
    thicknesses = []
    if layerNumbers is None:
        layerNumbers = range(vessel.getNumberOfLayers())
    designAngles = getAnglesFromVesselCylinder(vessel)
    columns = ["lay{}_{:04.1f}".format(layNum, designAngles[layNum]) for layNum in layerNumbers]

    liner = vessel.getLiner()
    numberOfElements1 = liner.getMandrel1().numberOfNodes - 1
    numberOfElements2 = liner.getMandrel2().numberOfNodes - 1
    for layerNumber in layerNumbers:
        vesselLayer = vessel.getVesselLayer(layerNumber)
        layerThicknesses = []
        elemsMandrels = [(numberOfElements1, True)]
        if not symmetricContour:
            elemsMandrels.append((numberOfElements2, False))
        for numberOfElements, isMandrel1 in elemsMandrels:
            for elementNumber in range(numberOfElements):
                layerElement = vesselLayer.getVesselLayerElement(elementNumber, isMandrel1)
                layerThicknesses.append(layerElement.elementThickness)
            if not symmetricContour and isMandrel1:
                layerThicknesses = layerThicknesses[::-1]  # reverse order of mandrel 1
        thicknesses.append(layerThicknesses)
    thicknesses = pd.DataFrame(thicknesses).T
    thicknesses.columns = columns
    return thicknesses


def getElementThicknesses(vessel):
    """returns a vector with thicknesses of each element along the whole vessel"""
    thicknesses = getLayerThicknesses(vessel).T
    return thicknesses.sum()


def getLayerAngles(vessel, symmetricContour, layerNumbers=None):
    """returns a dataframe with angles of each layer along the whole vessel

    :param vessel: vessel obj
    :param symmetricContour: flag if symmetric contour is used
    :param layerNumbers: list of layers that should be evaluated. If None, all layers are used
    :return:
    """
    angles = []
    if layerNumbers is None:
        layerNumbers = range(vessel.getNumberOfLayers())
    DesignAngles = getAnglesFromVesselCylinder(vessel)
    columns = ["lay{}_{:04.1f}".format(layNum, DesignAngles[layNum]) for layNum in layerNumbers]

    liner = vessel.getLiner()
    numberOfElements1 = liner.getMandrel1().numberOfNodes - 1
    numberOfElements2 = liner.getMandrel2().numberOfNodes - 1
    for layerNumber in layerNumbers:
        vesselLayer = vessel.getVesselLayer(layerNumber)
        layerAngles = []
        elemsMandrels = [(numberOfElements1, True)]
        if not symmetricContour:
            elemsMandrels.append((numberOfElements2, False))
        for numberOfElements, isMandrel1 in elemsMandrels:
            for elementNumber in range(numberOfElements):
                layerElement = vesselLayer.getVesselLayerElement(elementNumber, isMandrel1)
                layerAngles.append(np.rad2deg(layerElement.clairaultAngle))
            if not symmetricContour and isMandrel1:
                layerAngles = layerAngles[::-1]  # reverse order of mandrel 1
        angles.append(layerAngles)
    angles = pd.DataFrame(angles).T
    angles.columns = columns
    return angles


def getMandrelNodalCoordinates(liner, symmetricContour):
    """returns a dataframe with thicknesses of each layer along the whole vessel

    :param liner: liner obj
    :param symmetricContour: flag if symmetric contour is used
    :return:
    """
    mandrel1 = liner.getMandrel1()
    x = mandrel1.getXArray()
    r = mandrel1.getRArray()
    l = mandrel1.getLArray()
    if not symmetricContour:
        x = x[::-1]  # reverse order of mandrel 1
        r = r[::-1]
        l = l[::-1]
        mandrel2 = liner.getMandrel2()
        x2 = mandrel2.getXArray()
        x = np.append(x, mandrel2.getXArray())
        r = np.append(r, mandrel2.getRArray())
        l = np.append(l, mandrel2.getLArray())

    coordinatesDataframe = pd.DataFrame(np.array([x, r, l]).T, columns=["x_mandrel", "r_mandrel", "l_mandrel"])

    return coordinatesDataframe


def getLayerNodalCoordinates(windingResults, symmetricContour, layerNumbers=None):
    """returns a dataframe with thicknesses of each layer along the whole vessel

    :param windingResults: windingResults obj
    :param symmetricContour: flag if symmetric contour is used
    :param layerNumbers: list of layers that should be evaluated. If None, all layers are used
    :return:
    """
    if layerNumbers is None:
        layerNumbers = range(0, windingResults.getNumberOfLayers())
    coordinates = []
    columns = []
    Mandrels = [True]
    if not symmetricContour:
        Mandrels.append(False)
    for layerNumber in layerNumbers:
        columns.append("x_lay{}".format(layerNumber))
        columns.append("r_lay{}".format(layerNumber))
        x = []
        r = []
        for isMandrel1 in Mandrels:
            numberOfNodes = windingResults.getNumberOfNodesInLayer(layerNumber + 1, isMandrel1)
            for nodeNumber in range(1, numberOfNodes + 1):
                node = windingResults.getNode(layerNumber + 2, nodeNumber, isMandrel1)
                x.append(node.x)
                r.append(node.y)
            if not symmetricContour and isMandrel1:
                x = x[::-1]  # reverse order of mandrel 1
                r = r[::-1]
        coordinates.append(x)
        coordinates.append(r)
    coordinatesDataframe = pd.DataFrame(coordinates).T
    coordinatesDataframe.columns = columns
    return coordinatesDataframe


def copyAsJson(filename, typename):
    """copy a file creating a .json file

    Files in mycrowind have specific file types although they are json files.
    This method creates an additional json file besides the original file."""
    if filename.endswith(f".{typename}"):
        # also save as json for syntax highlighting
        shutil.copy2(filename, filename + ".json")


def updateName(jsonFilename, name, objsName, attrName="name"):
    """updates the name of an item in a json file.

    The given json file will be updated in place

    :param jsonFilename: name of json file
    :param name: name that should be updated
    :param objsName: name of the object which name tag should be updated
    """
    with open(jsonFilename) as jsonFile:
        data = json.load(jsonFile)
    item = data
    for objName in objsName:
        try:
            item = item[objName]
        except KeyError:
            raise Tankoh2Error(f'Tree of "{objsName}" not included in "{jsonFilename}"')
    item[attrName] = name
    with open(jsonFilename, "w") as jsonFile:
        json.dump(data, jsonFile, indent=4)


def changeSimulationOptions(vesselFilename, nLayers, minThicknessValue, hoopLayerCompressionStart):
    """changes simulation options for all layers by modifying .vessel (json) file

    The given json file vesselFilename will be updated in place

    :param vesselFilename: name of vessel file (.vessel)
    :param nLayers: number of layers to be wind

    """

    with open(vesselFilename) as jsonFile:
        data = json.load(jsonFile)

    for n in range(1, nLayers + 1):
        data["vessel"]["simulationOptions"]["thicknessOptions"][str(n)]["minThicknessValue"] = minThicknessValue
        data["vessel"]["simulationOptions"]["thicknessOptions"][str(n)][
            "hoopLayerCompressionStart"
        ] = hoopLayerCompressionStart

    with open(vesselFilename, "w") as jsonFile:
        json.dump(data, jsonFile, indent=4)


def getLinearResultsAsDataFrame(results=None):
    """returns the mechanical results as dataframe

    :param results: tuple with results returned by getLinearResults()
    :return: dataframe with results
    """
    if len(results) == 2:
        puckFF, puckIFF = results
        S11, S22, S12, epsAxialBot, epsAxialTop, epsCircBot, epsCircTop = [[]], [[]], [[]], [], [], [], []
    else:
        S11, S22, S12, epsAxialBot, epsAxialTop, epsCircBot, epsCircTop, puckFF, puckIFF = results
    layers = range(puckFF.shape[1])
    dfList = [puckFF, puckIFF]
    for data, name in zip(
        [S11, S22, S12, epsAxialBot, epsAxialTop, epsCircBot, epsCircTop],
        ["S11", "S22", "S12", "epsAxBot", "epsAxTop", "epsCircBot", "epsCircTop"],
    ):
        if len(data.shape) == 2:
            columns = [f"{name}lay{layerNumber}" for layerNumber in layers]
            dfAdd = pd.DataFrame(data, columns=columns)
        else:
            dfAdd = pd.DataFrame(np.array([data]).T, columns=[name])
        dfList.append(dfAdd)
    df = pd.concat(dfList, join="outer", axis=1)
    return df


def getMostCriticalElementIdxPuck(puck):
    """Returns the index of the most critical element

    :param puck: 2d array defining puckFF or puckIFF for each element and layer
    """
    layermax = puck.max().argmax()
    elemIdxPuckMax = puck.idxmax().iloc[layermax]
    return elemIdxPuckMax, layermax


def orderLayersAscending(anglesShifts):
    """Order a list of angles/shifts with helical angles in ascending order, keeping hoop layers in place

    :param anglesShifts: current AnglesShifts
    """
    sortedAngles = sorted(anglesShifts)
    iterSortedAngles = iter(sortedAngles)
    for i, angle in enumerate(anglesShifts):
        if not isHoopLayer(angle[0]):
            anglesShifts[i] = next(iterSortedAngles)


def moveLastLayerAscending(anglesShifts):
    """Move the last layer downwards until it reaches a layer with lower angle, or a hoop layer. In this way, helical clusters are sorted.

    :param anglesShifts: current AnglesShifts
    """
    for i in range(len(anglesShifts) - 1, 0, -1):
        if anglesShifts[i][0] <= anglesShifts[i - 1][0] < hoopLayerAngleThreshold:
            anglesShifts[i], anglesShifts[i - 1] = anglesShifts[i - 1], anglesShifts[i]
        else:
            break


def moveHighAnglesOutwards(anglesShifts, minAngle):
    """Move any angles higher than minAngle to the outside, then sort their position according to angle

    :param anglesShifts: current AnglesShifts
    :param minAngle: angle above which angles are sorted
    """
    for i in range(len(anglesShifts) - 1, 0, -1):
        if minAngle <= anglesShifts[i][0] < hoopLayerAngleThreshold:
            anglesShifts.append(anglesShifts.pop(i))
            moveLastLayerAscending(anglesShifts)


def getStartOfSortedLayers(anglesShifts, minAngle):
    """Find the first layer with an angle > minAngle

    :param anglesShifts: current AnglesShifts
    :param minAngle: angle above which angles are sorted
    :return: layerNumber of first layer with angle > minAngle
    """
    for i in range(len(anglesShifts) - 1, 0, -1):
        if not (minAngle <= anglesShifts[i][0] < hoopLayerAngleThreshold):
            return i + 1
    else:
        return len(anglesShifts)


def isHoopLayer(angle):
    """Check if the angle is a hoop layer

    :param angle: angle of layer
    :return: True if angle is a hoop layer, False otherwise
    """
    return angle > hoopLayerAngleThreshold


def clusterHoopLayers(anglesShifts):
    """Move the last n hoop layers together, at the position of the first of these layers.

    :param anglesShifts: current AnglesShifts
    """
    hoopLayerFound = False
    for i in range(len(anglesShifts) - 1, -1, -1):
        angle, shift1, shift2 = anglesShifts[i]
        if isHoopLayer(angle):
            if not hoopLayerFound:
                hoopLayerToMove = anglesShifts.pop(i)
                hoopLayerFound = True
            else:
                anglesShifts.insert(i + 1, hoopLayerToMove)
                break
    else:
        raise Tankoh2Error(f"clusterHoopLayers failed to find 2 hoop layers!")


def getStartAndEndOfFullCylinder(vessel, symmetricContour):
    """Find the nodes marking the full-thickness cylinder, where the hoop layers start dropping off

    :param vessel:
    :param symmetricContour:
    :return startOfFullCylinder:
    :return endOfFullCylinder:
    """

    polarOpeningNodes = []
    for layer in range(vessel.getNumberOfLayers()):
        polarOpeningNodes.append(vessel.getVesselLayer(layer).getPolarOpeningID(True))
    minPolarOpeningNode = min(polarOpeningNodes)
    if symmetricContour:
        startOfFullCylinder = 0
        endOfFullCylinder = minPolarOpeningNode
    else:
        middleNode = vessel.getLiner().getMandrel1().numberOfNodes
        polarOpeningNodesSide2 = []
        for layer in range(vessel.getNumberOfLayers()):
            polarOpeningNodesSide2.append(vessel.getVesselLayer(layer).getPolarOpeningID(False))
        minPolarOpeningNodeSide2 = min(polarOpeningNodesSide2)
        startOfFullCylinder = middleNode - minPolarOpeningNode
        endOfFullCylinder = middleNode + minPolarOpeningNodeSide2
    return startOfFullCylinder, endOfFullCylinder


def getLayerThicknessesFromVesselCylMid(vessel):
    """returns a list with all layer thicknesses from the vessel"""
    return [
        (vessel.getVesselLayer(layerNumber).getVesselLayerElement(0, True).elementThickness)
        for layerNumber in range(vessel.getNumberOfLayers())
    ]
