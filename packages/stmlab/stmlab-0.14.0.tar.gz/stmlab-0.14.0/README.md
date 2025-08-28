[![doi](https://img.shields.io/badge/DOI-10.5281%2Fzenodo.13844636-red.svg)](https://zenodo.org/records/13844636)
[![PyPi](https://img.shields.io/pypi/v/stmlab?label=PyPi)](https://pypi.org/project/stmlab/)

# STMLab
> This Python package provides an independent standard runtime environment for software projects developed by the [Department of Structural Mechanics](https://www.dlr.de/en/sy/about-us/departments/structural-mechanics) at the [Institute of Lightweight Structures](https://www.dlr.de/en/sy) of the [German Aerospace Center](https://www.dlr.de/en) It uses the [Jupyter](https://jupyter.org/) project as its graphical user interface. Two types of installation procedures are available. A community version can be installed and executed using pip. An enterprise version with yet unpublished software projects is available as an offline installer on request.

## Downloading
Use GIT to get the latest code base. From the command line, use
```
git clone https://gitlab.dlr.de/dlr-sy/stmlab stmlab
```
If you check out the repository for the first time, you have to initialize all submodule dependencies first. Execute the following from within the repository. 
```
git submodule update --init --recursive
```
To update all refererenced submodules to the latest production level, use
```
git submodule foreach --recursive 'git pull origin $(git config -f $toplevel/.gitmodules submodule.$name.branch || echo master)'
```
## Installation
STMLab can be installed from source using [poetry](https://python-poetry.org). If you don't have [poetry](https://python-poetry.org) installed, run
```
pip install poetry --pre --upgrade
```
to install the latest version of [poetry](https://python-poetry.org) within your python environment. Use
```
poetry update
```
to update all dependencies in the lock file or directly execute
```
poetry install
```
to install all dependencies from the lock file. Last, you should be able to import STMLab as a python package.
```python
import stmlab
```
## Contact
* [Marc Garbade](mailto:marc.garbade@dlr.de)