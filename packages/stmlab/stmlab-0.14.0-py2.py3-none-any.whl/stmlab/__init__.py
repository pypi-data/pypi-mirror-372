# -*- coding: utf-8 -*-
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#                             STMLab                             %
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
"""
STMLab is a composite application written in Python acting as a 
package manager to all scientific softare projects related to SY-STM.
Acts as a shim to PyCODAC to start the web-based graphical user
interface locally on the current machine.

@version: 1.0.0   
----------------------------------------------------------------------------------------------
@requires:
       - 

@change: 
       -    
                           
@author: garb_ma                                                     [DLR-SY,STM Braunschweig]
----------------------------------------------------------------------------------------------
"""

## @package STMLab
# STMLab is a composite application written in Python acting as a 
# package manager to all scientific softare projects related to SY-STM.
## @authors 
# Marc Garbade
## @date
# 20.03.2024
## @par Notes/Changes
# - Added documentation // mg 19.03.2024

import os

# Try to import metadata reader. Allowed to fail.
try: import importlib_metadata
except ImportError: pass

try: import tomlkit
except ImportError: pass

## Absolute system path to STMLab.
STMLabPath = os.path.dirname(os.path.abspath(__file__))

## Get the current project name
__project__ = os.path.basename(os.path.normpath(STMLabPath))

## Provide canonical version identifiers
try:
    # Obtain version directly from metadata
    __version__ = importlib_metadata.version(__project__)
except:
    # We have a partial install 
    try:
        # Obtain version directly from metadata
        with open(os.path.join(STMLabPath,os.path.pardir,os.path.pardir,"pyproject.toml")) as pyproject: content = pyproject.read()
        __version__ = tomlkit.parse(content)["tool"]["poetry"]["version"]
    except Exception as _:
        # We have only the source code
        __version__ = str("0.0.0dev")

# Create version info for compatibility
__version_info__ = tuple(__version__.split("."))

if __name__ == '__main__':
    pass