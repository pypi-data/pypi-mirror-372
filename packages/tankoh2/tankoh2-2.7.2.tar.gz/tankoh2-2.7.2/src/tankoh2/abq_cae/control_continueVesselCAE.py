# SPDX-FileCopyrightText: 2023 German Aerospace Center (DLR)
#
# SPDX-License-Identifier: MIT

# Continue vessel model implementation
# -*- coding: utf-8 -*-

# Created on Wed July 14 12:30 2021
# Author: Carloline Lueders


import os
import sys

###############################################################################


sys.path.append(
    "C://DATA//Projekte//NGT_lokal//05_Abwicklung//03_Simulationsmodelle//01_Tankmodellierung_MikroWind//Projekt_MikroWind//tankoh2//src//tankoh2//abq_cae"
)
os.add_dll_directory(
    "C://DATA//Projekte//NGT_lokal//05_Abwicklung//03_Simulationsmodelle//01_Tankmodellierung_MikroWind//Projekt_MikroWind//tankoh2//src//tankoh2//abq_cae"
)

import importlib
import json
from datetime import datetime

import continueVesselCAE as cvc
import mesh
import numpy as np

cvc = importlib.reload(cvc)


def getModel(projectname):
    # sourcepath=os.getcwd()
    # projectname=getInput('Geben Sie den Projektnamen ein:',default='test')
    # projectpath=sourcepath+'////'+projectname
    # os.chdir(projectpath)
    # filename=os.listdir(projectpath)

    modelname = projectname
    global model
    model = mdb.models[modelname]
    global parts
    parts = model.parts
    global assembly
    assembly = model.rootAssembly


# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% MAIN PROGRAMM %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


def main():
    #    %%%%%%%%%%%%% DEFINE PARAMETER %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

    # ------- general
    modelname = "NGT-BIT-2020-09-16_Solid3D"
    domefile = "C://DATA//Projekte//NGT_lokal//09_Projektdaten//03_Simulationsmodelle//01_Tankmodellierung_MikroWind//Projekt_MikroWind//Current_vessel//SetSimulationOptions//Dome_contour_NGT-BIT-2020-09-16_48mm.txt"
    rzylinder = 412.42 / 2.0  # radius of cylindrical part
    lcylinder = 240.16  # length of cylindrical part
    nMandrels = 1  # number of mandrels
    layerPartPrefix = "Layer"  # name before underline character; for 3D Solid models / solid axissymmetric models, where each layer is a seperate part
    reveloveAngle = 10.0
    CoordAxisWhichIsRotAxis = "y"  # coordinate main axis which acts as vessels's rotation axis
    windingPartName = "Mandrel1"  # part including the whole winding with all layers, e.g. for shell modells
    WindingOfDiffParts = True  # true =  winding composed of differnt layer parts; false -- winding is one part

    # ------- Liner ## function not fully completed; only sketch of liner is created in cae
    linerthickness = 4.0
    createLiner = False

    # ------- Material
    layerMaterialPrefix = "Layer"
    # layerMaterialPrefix = "M1_Section"
    # layerMaterialPrefix = 'WCM_Tank1_Mat1_Bin'
    materialName = "CFRP_HyMod"  # name of material to be used
    materialPath = (
        "C://DATA//Projekte//NGT_lokal//05_Abwicklung//03_Simulationsmodelle//01_Tankmodellierung_MikroWind//Projekt_MikroWind//tankoh2//data//"
        + materialName
        + ".json"
    )
    UMATprefix = "MCD_SHOKRIEH"  # prefix in material name required by umat
    AbqMATinAcuteTriangles = (
        False  # if true, ABQ-Material is set for very acute triangle elements yielding warnings in mesh verification
    )
    # nDepvar = 312 # number of solution dependen variables
    nDepvar = 156  # number of solution dependen variables in umat
    # degr_fac = 0.40 # last value for berst pressure analysis
    degr_fac = 0.1  # degradation factor for material properties after failure initiation
    udLayers = False  # if winding is modelled as composite layup, angle plies can be respresented as single ud plies instead of effective angle plys
    compositeLayup = False
    noSectionPoint = 3  # number of section points per layer in composite layup
    userDefinedField = False  # is user defined field used?
    useThickShellExtension = False
    createUMAT = True
    removeUMAT = False

    # ------------------- rename Material
    oldChars = "_ABQMAT"
    newChars = ""
    renameMaterials = False

    # ------- Mesh    # remeshes with given number of elements per layer thickness (elementsPerLayerThickness) and wedge elements in very narrow regions (minAngle)
    # set to elements to reduced integration
    # to do: distorted elements at fitting in widning and fitting
    # --> hex-dominated in fitting, smaller global element size
    # --> virtual topology /ignore edges --> modifiy Orientations as surfaces and edges for ori definition may be deleted
    elementsPerLayerThickness = 1
    minAngle = 10.0  # minimum anlge for using hex elements (for regions with lower angles, wedge elements are set)
    remesh = True

    # ------- Periodic Boundary Conditions
    exceptionSets = (("Fitting1", "contactFacesWinding"), ("Layer_2", "FittingContact"))  # (partname, setname)
    # exceptionSets = ()  # (partname, setname)
    createPeriodicBCs = False

    # -------- Step-Definition

    steptime = [
        10.0,
    ]
    minInk = [
        1.0e-8,
    ]
    startInk = [
        0.0005,
    ]
    maxInk = [
        0.05,
    ]
    stab = [
        2.0e-5,
    ]
    maxNumInk = [
        5000,
    ]
    NLGEOM = [
        ON,
    ]

    createStepDefinition = True

    # ------ Output definition

    dt = 0.1  # time interval for output request; set 0 if no reuqest per time interval
    dnInk = 10  # interval of increment number for output request; set 0 if no reuqest per increment number
    fieldVariables = ("S", "SDV", "LE", "P", "U")
    historyVariables = ()  # leave empty if no history output
    createOutputDefinition = True

    # ---------- Load Definition

    pressure = 250  # bar
    valveForce = 0.0
    createLoadDefinition = True

    # ----------- Layer connection

    useContact = False  # True -- use contact, False -- use Tie
    checkLayerConnection = False

    ############# START

    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    print("---------------------- START SCRIPT at " + current_time + " ---------------------------------")

    getModel(modelname)

    if remesh == True:
        cvc.reMeshVessel(elementsPerLayerThickness, layerPartPrefix, minAngle, parts)

    if createLiner == True:
        cvc.loadDomeContourToSketch(domefile, rzylinder, lcylinder, linerthickness, model)

    if createUMAT == True:
        cvc.createUMATmaterials(
            model,
            layerMaterialPrefix,
            UMATprefix,
            materialPath,
            materialName,
            nDepvar,
            degr_fac,
            AbqMATinAcuteTriangles,
            udLayers,
            compositeLayup,
            windingPartName,
            userDefinedField,
            noSectionPoint,
            useThickShellExtension,
        )

    if removeUMAT == True:
        cvc.removeUMAT(model)

    if renameMaterials:
        cvc.renameMaterials(model, oldChars, newChars)

    if createStepDefinition:
        cvc.createStepDefinition(steptime, minInk, maxInk, startInk, maxNumInk, stab, NLGEOM, model)

    if createOutputDefinition:
        if maxInk[0] > dt:
            print(
                "WARNING: maximal increment size is larger then output frequency. Output frequency is increased to fit maximum increment size"
            )
            dt = max(maxInk[0])
        cvc.createOutputDefinition(model, dt, dnInk, fieldVariables, historyVariables)

    if createLoadDefinition:
        cvc.createLoads(model, valveForce, pressure)

    if checkLayerConnection:
        cvc.adaptLayerConnection(model, parts, assembly, layerPartPrefix, useContact)

    if createPeriodicBCs:
        cvc.applyPeropdicBCs(
            layerPartPrefix,
            reveloveAngle,
            exceptionSets,
            assembly,
            parts,
            model,
            useContact,
            CoordAxisWhichIsRotAxis,
            WindingOfDiffParts,
        )  #

    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    print("---------------------- SCRIPT FINISHED at " + current_time + " ---------------------------------")


if __name__ == "__main__":
    main()
