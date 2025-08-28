# tankoh2

[![pipeline status](https://gitlab.com/DLR-SY/tank/tankoh2/badges/master/pipeline.svg)](https://gitlab.com/DLR-SY/tank/tankoh2/-/commits/master)
[![coverage report](https://gitlab.com/DLR-SY/tank/tankoh2/badges/master/coverage.svg)](https://gitlab.com/DLR-SY/tank/tankoh2/-/commits/master)
[![Latest Release](https://gitlab.com/DLR-SY/tank/tankoh2/-/badges/release.svg)](https://gitlab.com/DLR-SY/tank/tankoh2/-/releases)


Design and optimization of H2 tanks.

For metal structures, tankoh2 is a standalone pre-design tool.
For CFRP structures, a detailed winding optimization is performed.
The winding simulation is carried out by [µChain](https://www.mefex.de/software/)

## Features

- Material/layup read/write
- Define requirements for cryogenic or high-pressure hydrogen storage
- Create dome (spherical, isotensoid, torisspherical or conical) and liner from cylindrical length and radius or using a dome contour
- Setup of a vessel model
- Optimization of each layer with respect to minimizing puck fibre failure, bending loads, and maintaining a good contour
- Create and run DOE with support of DLR tools (delismm, fa_pyutils)
- Routines for the improvement of the FEM model generatred by Abaqus CAE
- Planned features:
  - Global optimization of
    - All angles of helical layers
    - All hoop layer shifts
    - Target: mass minimization
    - Constraint: puck fibre failure
  - Improved DOE: Liner and fitting adjustment w.r.t. vessel geometry
  - Abaqus: introduction of the abaqus solver at the end of the optimization process

## Documentation
Here is the full [Documentation](https://dlr-sy.gitlab.io/tank/tankoh2/)

## Installation

### Installation for users
Coming soon: installation via pypi using `pip install tankoh2`

When tankoh2 is installed, please follow the steps in [Settings File](#settings-file).

### Installation from source
- Get tankoh2 from
  > https://gitlab.com/DLR-SY/tank/tankoh2.git
- Install python 3.10 (On the Windows Installer, check the advanced option to add Python to your path and to install pip)
- Install poetry
  > pip install poetry
- Install requirements for the project
  > cd <path_to_tankoh2>
  > poetry install
- When tankoh2 is installed, please follow the steps in [Settings File](#settings-file).

### For winding: Path to µChain

Add an environment variable named MYCROPYCHAINPATH
and set its value to the path of your [µChain](https://www.mefex.de/software/) installation.

Old Method, will be deprecated soon: Alternatively, in the folder `/src/tankoh2/`, create a file `settings.json`
and include the path here.

```
{
  "mycropychainPath": "<path_to_muChain>"
}
```

### Activate the environment

This needs to be done whenever you want to use tankoh2.
First, navigate into tankoh2's source directory.

```
cd <path_to_tankoh2>/src
```

Then, before running tankoh2, you need to activate the python environment created by poetry during the installation. Alternatively replace 'python' in the commands with 'poetry run'.

```
poetry shell
```

### Test the installation

```
python -m tankoh2 --help
```

You can perform a standalone test for metal tanks

```
python -m tankoh2 --materialName alu2219 --windingOrMetal metal --domeType circle
```

### Developers
- Follow the steps [Installation from source](#installation-from-source) above
- Install all dev dependencies and test dependencies listed in ``pyproject.toml``

#### Pre-Commit Hooks

Developers may also install the pre-commit hook.

**Precommit**
1. If not installed: install the pre-commit
   > pip install pre-commit
2. In the tankoh2 folder
   > pre-commit install

This enables the pre-commit hooks defined in _.pre-commit-config.yaml_
and eases your commits and successful pipline runs. You can test pre-commit by running
> pre-commit run

### Requirements

see **tool.poetry.dependencies** section in [pyproject.toml](pyproject.toml)

FreeCAD is required for conical domes

## Usage
A full list the available parameters is created with

```
python -m tankoh2 --help
```

### Winding

For winding mode, a valid µWind license is required!
Run the following, to start a winding optimization.

```
python -m tankoh2
```

### Metal

A design run for metal structures can be run by

```
python -m tankoh2 --materialName alu2219 --windingOrMetal metal --domeType circle
```

### Config Files:
It's easiest to write design config files in .yaml format to define any parameters for the winding or metal simulation. Using config files, it's possible to reproduce and modify runs.
Config files need to be put in the folder tankoh2/designs and are used via the option --configFile [nameOfFile.yaml]. For example:

```
python -m tankoh2 --configFile 700bar_example.yaml
```

Any non-default parameters can be defined in parameter:value pairs. All possible parameters with descriptions can be seen in defaults.yaml and in the documentation. Config files can also recursively include other configFiles as parameters, whose parameters can be overwritten.
The parameters which were used in each run are also saved in .yaml format in the run directory. These directories are located under tankoh2/tmp by default.

Parameters given in config files are overwritten by parameters supplied explicitly via options.

```
python -m tankoh2 --configFile 700bar_example.yaml --safetyFactor 2.0
```
The option --windingOrMetal can currently not be defined in a config file and must be given explicitly for metal simulation (default is winding).

## Contributing to _tankoh2_

We welcome your contribution!

If you want to provide a code change, please:

* Create a fork of the project.
* Develop the feature/patch
* Provide a merge request.

> If it is the first time that you contribute, please add yourself to the list
> of contributors below.


## Citing

Please cite name and web address of the project

## License

see [license](LICENSE.md)

## Change Log

see [changelog](changelog.md)

## Authors

[Sebastian Freund](mailto:sebastian.freund@dlr.de)
[Caroline Lüders](mailto:caroline.lueders@dlr.de)
[Linus Jacobsen](mailto:linus.jacobsen@dlr.de)
[Felipe Franzoni](mailto:felipe.franzoni@dlr.de)
