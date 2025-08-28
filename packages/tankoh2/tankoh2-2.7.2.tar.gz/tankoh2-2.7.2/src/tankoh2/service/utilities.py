# SPDX-FileCopyrightText: 2023 German Aerospace Center (DLR)
#
# SPDX-License-Identifier: MIT

"""utility functions"""

import functools
import getpass
import glob
import io
import itertools
import math
import os
import re
import sys
import time
from datetime import datetime
from os.path import abspath, exists, join

import numpy as np
from ruamel.yaml import YAML, comments

from tankoh2 import log, programDir
from tankoh2.arguments import allArgs
from tankoh2.service.exception import Tankoh2Error

designDir = "designs"


def importFreeCad():
    """searches for the freecad folder and puts it into the system path"""
    stdInstallPath = f"C:\\Users\\{getpass.getuser()}\\AppData\\Local\\Programs\\"
    searchPaths = glob.glob(stdInstallPath + "/FreeCAD*")[::-1]

    for searchPath in searchPaths:
        if exists(join(searchPath, "bin")) and exists(join(searchPath, "bin", "FreeCAD.exe")):
            freecadLibPaths = [join(searchPath, "lib"), join(searchPath, "bin")]
            log.debug(f"Add freecad to path: {freecadLibPaths}")
            sys.path.extend(freecadLibPaths)
            os.environ["PATH"] = ";".join(freecadLibPaths + [os.environ["PATH"]])
            break
    else:
        log.info(
            f"Could not find FreeCAD (required if conical dome shapes used). "
            f"Searched in this folder: {stdInstallPath}"
        )


def getTimeString(useMilliSeconds=False):
    """returns a time string of the format: yyyymmdd_hhmmss"""
    dt = datetime.now()
    return dt.strftime("%Y%m%d_%H%M%S") + ("_{}".format(dt.microsecond) if useMilliSeconds else "")


def makeAllDirs(directory):
    absPath = abspath(directory)
    for i in range(0, absPath.count(os.sep))[::-1]:
        # Split path into subpaths beginning from the top of the drive
        subPath = absPath.rsplit(os.sep, i)[0]
        if not exists(subPath):
            os.makedirs(subPath)


def getRunDir(runDirExtension="", useMilliSeconds=False):
    """Creates a folder that will be used as directory for the actual run.

    The created folder has this name::

        tmp/tank_<timestamp><runDirExtension>

    :param runDirExtension: optional string appended to the folder name. Defaults to ''
    :param useMilliSeconds: include milliseconds to the run dir name or not
    :returns: absolute path to the new folder

    Example::

        >> getRunDir('_bar', False)
        C:/tankoh2/tmp/tank_20170206_152323_bar

    """
    if runDirExtension and runDirExtension[0] != "_":
        runDirExtension = "_" + runDirExtension
    while True:
        runDir = join(programDir, "tmp", "tank_" + getTimeString(useMilliSeconds)) + runDirExtension
        if exists(runDir):
            log.warning("runDir already exists. Wait 1s and retry with new timestring.")
            time.sleep(1)
        else:
            makeAllDirs(runDir)
            break

    return runDir


def createRstTable(inputMatrix, numberOfHeaderLines=1):
    """Returns a string containing a well formatted table that can be used in rst-documentation.

    :param inputMatrix: A sequence of sequences of items, one sequence per row.
    :param numberOfHeaderLines: number of lines that are used as header. the header is printed bold.
    :return: string containing well formatted rst table

    Example::

        >>> from tankoh2.service.utilities import createRstTable
        >>> a=[]
        >>> a.append(['','major','minor','revision'])
        >>> a.append(['Example','13','2','0'])
        >>> a.append([  'Explanation','New feature, incompatibe to prev versions','New feature, compatible to prev versions','Patch/Bugfix'])
        >>> print(createRstTable(a))
        +-------------+-------------------------------------------+------------------------------------------+--------------+
        |             | major                                     | minor                                    | revision     |
        +=============+===========================================+==========================================+==============+
        | Example     | 13                                        | 2                                        | 0            |
        +-------------+-------------------------------------------+------------------------------------------+--------------+
        | Explanation | New feature, incompatibe to prev versions | New feature, compatible to prev versions | Patch/Bugfix |
        +-------------+-------------------------------------------+------------------------------------------+--------------+
    """
    tableString = indent(inputMatrix, separateRows=True, hasHeader=True, headerChar="-", prefix="| ", postfix=" |")
    tableLines = tableString.splitlines()
    # get second row to extract the position of '|'
    pipePositions = []
    line = tableLines[1]
    for index, character in enumerate(line):
        if character == "|":
            pipePositions.append(index)

    # alter tableLines containing text
    for halfLineNumber, line in enumerate(tableLines[::2]):
        for index in pipePositions:
            line = line[:index] + "+" + line[index + 1 :]
        tableLines[halfLineNumber * 2] = line

    tableLines[2 * numberOfHeaderLines] = tableLines[2 * numberOfHeaderLines].replace("-", "=")
    return "\n".join(tableLines)


def indent(
    rows,
    hasHeader=False,
    headerChar="-",
    delim=" | ",
    justify="left",
    separateRows=False,
    prefix="",
    postfix="",
    wrapfunc=lambda x: wrap_npstr(x),
):  # lambda x:x):
    """
    Indents a table by column.

    :param rows: A sequence of sequences of items, one sequence per row.

    :param hasHeader: True if the first row consists of the columns' names.

    :param headerChar: Character to be used for the row separator line
      (if hasHeader==True or separateRows==True).

    :param delim: The column delimiter.

    :param justify: Determines how are data justified in their column.
      Valid values are 'left','right' and 'center'.

    :param separateRows: True if rows are to be separated by astr
     line of 'headerChar's.

    :param prefix: A string prepended to each printed row.

    :param postfix: A string appended to each printed row.

    :param wrapfunc: A function f(text) for wrapping text; each element in
      the table is first wrapped by this function.

    remark:

    :Author: George Sakkis
    :Source: http://code.activestate.com/recipes/267662/
    :License: MIT (http://code.activestate.com/help/terms/)
    """

    # closure for breaking logical rows to physical, using wrapfunc
    def rowWrapper(row):
        newRows = [str(wrapfunc(item)).split("\n") for item in row]
        return [[substr or "" for substr in item] for item in map(lambda *x: x, *newRows)]

    # break each logical row into one or more physical ones
    logicalRows = [rowWrapper(row) for row in rows]
    # columns of physical rows
    columns = list(itertools.zip_longest(*[row[0] for row in logicalRows]))
    # get the maximum of each column by the string length of its items
    maxWidths = [max([len(str(item)) for item in column]) for column in columns]
    rowSeparator = headerChar * (len(prefix) + len(postfix) + sum(maxWidths) + len(delim) * (len(maxWidths) - 1))
    # select the appropriate justify method
    justify = {"center": str.center, "right": str.rjust, "left": str.ljust}[justify.lower()]
    output = io.StringIO()
    if separateRows:
        print(rowSeparator, file=output)
    for physicalRows in logicalRows:
        for row in physicalRows:
            outRow = prefix + delim.join([justify(str(item), width) for (item, width) in zip(row, maxWidths)]) + postfix
            print(outRow, file=output)
        if separateRows or hasHeader:
            print(rowSeparator, file=output)
            hasHeader = False
    return output.getvalue()


def wrap_npstr(text):
    """A function to distinguisch between np-arrays and others.
    np-arrays are returned as string without newline symbols that are usually returned by np.ndarray.__str__()
    lists are cut at the beginning and end to 75 characters
    """
    if isinstance(text, np.ndarray):
        text = np.array2string(text, separator=",").replace("\n", "")
    if isinstance(text, list):
        textStr = str(text)
        if len(textStr) > 75:
            text = textStr[:35] + " ... " + textStr[-35:]
    return text


def wrap_onspace(text, width):
    """A word-wrap function that preserves existing line breaks
    and most spaces in the text. Expects that existing line
    breaks are posix newlines (\\n).
    """
    return functools.reduce(
        lambda line, word, width=width: "%s%s%s"
        % (line, " \n"[(len(line[line.rfind("\n") + 1 :]) + len(word.split("\n", 1)[0]) >= width)], word),
        text.split(" "),
    )


def wrap_onspace_strict(text, width):
    """Similar to wrap_onspace, but enforces the width constraint:
    words longer than width are split."""
    wordRegex = re.compile(r"\S{" + str(width) + r",}")
    return wrap_onspace(wordRegex.sub(lambda m: wrap_always(m.group(), width), text), width)


def wrap_always(text, width):
    """A simple word-wrap function that wraps text on exactly width characters.
    It doesn't split the text in words."""
    return "\n".join([text[width * i : width * (i + 1)] for i in range(int(math.ceil(1.0 * len(text) / width)))])


def readParametersFromYAML(filepath, openedFiles=None):
    """Reads Parameters from YAML file and returns a dict. Allows recursive relations between config files.

    :param filepath: Full path to a .yaml file
    :param openedFiles: list of already opened files passed to recursive calls of the function
    :return: dictionary of keyworded input arguments
    """
    yaml = YAML()
    yaml.encoding = "utf-8"
    # recursively read base designs, checking if the file has already been opened
    if openedFiles is None:
        openedFiles = []
    if filepath not in openedFiles:
        if not os.path.exists(filepath):
            filepath += ".yaml"
        with open(filepath, "rb") as inputFile:
            inputArgs = yaml.load(inputFile)
        openedFiles.append(filepath)
        if "configFile" in inputArgs and inputArgs["configFile"] is not None:
            configFile = inputArgs.pop("configFile")
            pathOptions = [
                configFile,  # abspath or correct relative path
                os.path.join(os.path.dirname(filepath), configFile),  # relative to actual config file
                os.path.join(programDir, designDir, configFile),
            ]  # in tankoh2 designDir
            for nextFilePath in pathOptions:
                if os.path.exists(nextFilePath):
                    break
            else:
                raise FileNotFoundError(
                    f"Config file {configFile} not found in any of the paths provided: {pathOptions}"
                )
            baseArgs = readParametersFromYAML(nextFilePath, openedFiles)
            baseArgs.update(inputArgs)
            inputArgs = baseArgs
    else:
        raise Tankoh2Error(f"Cyclic import in config files detected: {filepath}")

    return inputArgs


def writeParametersToYAML(parameters, filepath, descriptions=False):
    """Writes parameters from a dict to a YAML file, ordered by groups

    :param parameters: dict of keyworded parameters
    :param filepath: Full path to a .yaml file
    :param descriptions: Flag if end-of-line descriptions should be output for all parameters
    """
    # initialize YAML
    yaml = YAML()
    yaml.default_flow_style = False
    yaml.encoding = "utf-8"
    # get defined args from allArgs dataframe
    definedArgs = allArgs.loc[allArgs["name"].isin(parameters.keys())]
    # get groups of the defined args
    parametersWithGroups = dict(zip(definedArgs["name"], definedArgs["group"]))
    groups = list(definedArgs["group"].unique())
    # get parameter descriptions
    parametersWithDescriptions = dict(zip(definedArgs["name"], allArgs["help"]))
    # look for unknown Arguments
    unknownArgs = set(parameters.keys()).difference(allArgs["name"])
    if unknownArgs:
        groups.append("Unknown")
    # write arguments into a commented map, sorted by group names
    commentedYAML = comments.CommentedMap()
    with open(filepath, "wb") as outputFile:
        for group in groups:
            parametersInGroup = {
                key: value for (key, value) in parameters.items() if parametersWithGroups.get(key, "Unknown") == group
            }
            for key, value in parametersInGroup.items():
                # Use flow style for (nested) lists
                # Cast list-like objects into lists for the emitter
                if type(value) in [list, tuple, np.ndarray, comments.CommentedSeq]:
                    seq = comments.CommentedSeq(value.tolist() if type(value) == np.ndarray else list(value))
                    if type(value[0]) in [list, tuple, np.ndarray, comments.CommentedSeq]:
                        seq.fa.set_block_style()
                        for idx, subseq in enumerate(seq):
                            seq[idx] = comments.CommentedSeq(
                                subseq.tolist() if type(subseq) == np.ndarray else list(subseq)
                            )
                            seq[idx].fa.set_flow_style()
                    else:
                        seq.fa.set_flow_style()
                    commentedYAML[key] = seq
                else:
                    if type(value) == np.float64:
                        commentedYAML[key] = float(value)
                    else:
                        commentedYAML[key] = value
                if descriptions:
                    commentedYAML.yaml_add_eol_comment(parametersWithDescriptions.get(key, ""), key)
            commentedYAML.yaml_set_comment_before_after_key(list(parametersInGroup.keys())[0], group)
        # output
        yaml.dump(commentedYAML, outputFile)


def writeDefaultsToYAML():
    """Function to write all parameters with default arguments to a file named defaults.yaml"""
    defaultDesign = dict(zip(allArgs["name"], allArgs["default"]))
    filename = "defaults.yaml"
    filepath = os.path.join(programDir, designDir, filename)
    writeParametersToYAML(defaultDesign, filepath, descriptions=True)


def addDictHierarchyIfNotPresent(inputDict, hierarchyArray):
    """

    :param inputDict:
    :param hierarchyArray:
    """
    subDict = inputDict
    for hierarchyItem in hierarchyArray:
        if hierarchyItem not in subDict:
            subDict[hierarchyItem] = {}
        subDict = subDict[hierarchyItem]


if __name__ == "__main__":
    if 1:
        writeDefaultsToYAML()
