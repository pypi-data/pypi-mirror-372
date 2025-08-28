# SPDX-FileCopyrightText: 2023 German Aerospace Center (DLR)
#
# SPDX-License-Identifier: MIT

import sys
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser

from tankoh2 import description, name
from tankoh2.arguments import allArgs
from tankoh2.control.control_cryotank import createDesign as createDesignCryoTank
from tankoh2.control.control_metal import createDesign as createDesignMetal
from tankoh2.control.control_winding import createDesign as createDesignWinding
from tankoh2.control.genericcontrol import parseConfigFile
from tankoh2.service.exception import Tankoh2Error


def main():
    parserDesc = f"""{description}.
    Use the following optional arguments to customize the tank design.
    Any argument not given, will be extended by the ones defined in
    tankoh2.design.existingdesigns.defaultDesign."""
    parser = ArgumentParser(
        prog=name, description=parserDesc, add_help=False, formatter_class=ArgumentDefaultsHelpFormatter
    )

    grouped = allArgs.groupby("group")
    groupNames = allArgs["group"].unique()

    # if the help is requested, all defaults should be listed. If not, it is important to know which params are set explicitly
    includeDefaults = True if "--help" in sys.argv else False

    for groupName in groupNames:
        argsGroup = allArgs[allArgs["group"] == groupName]
        parserGroup = parser.add_argument_group(groupName)
        for argName, group, metavar, default, dataType, helpStr, action in argsGroup.iloc:
            kwargs = {}
            kwargs.update({"metavar": metavar} if metavar else {})
            if includeDefaults:
                kwargs.update({"default": default})
                kwargs.update({"action": action} if action else {})
            kwargs.update({"type": dataType} if dataType else {})
            parserGroup.add_argument(f"--{argName}", help=helpStr, **kwargs)

    options = parser.parse_args()
    params = {key: val for key, val in vars(options).items() if val is not None}
    windingOrMetal = params.pop("windingOrMetal").lower() if "windingOrMetal" in params else None
    singleOrDoubleVessels = params.get("singleOrDoubleVessels", "single")
    if "configFile" in params and params["configFile"] is not None:
        configArgs = parseConfigFile(params["configFile"])
        if "windingOrMetal" in configArgs:
            windingOrMetal = configArgs["windingOrMetal"].lower()
        if "singleOrDoubleVessels" in configArgs:
            singleOrDoubleVessels = configArgs["singleOrDoubleVessels"]
    if windingOrMetal is None:
        windingOrMetal = "winding"
    paramsWithoutDefaults = {key: value for key, value in params.items() if value != parser.get_default(key)}
    try:
        if singleOrDoubleVessels == "single":
            if windingOrMetal == "winding":
                createDesignWinding(**paramsWithoutDefaults)
            elif windingOrMetal == "metal":
                createDesignMetal(**paramsWithoutDefaults)
            else:
                raise Tankoh2Error(
                    f'Parameter "windingOrMetal" can only be one of [winding, metal] but got ' f"{windingOrMetal}"
                )
        elif singleOrDoubleVessels == "double":
            createDesignCryoTank(**paramsWithoutDefaults)
        else:
            raise Tankoh2Error(
                f'Parameter "singleOrDoubleVessels" can only be one of [single, double] but got '
                f"{singleOrDoubleVessels}"
            )
    except:
        sys.stdout.flush()
        raise


if __name__ == "__main__":
    main()
