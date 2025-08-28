# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %             Service Module - Classes and Functions           %
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
"""
Main entry point of STMLab package
 
@note: STMLab command line interface
Created on 21.10.2024

@version:  1.0    
----------------------------------------------------------------------------------------------
@requires:
       - 

@change: 
       -    
   
@author: garb_ma                                                     [DLR-SY,STM Braunschweig]
----------------------------------------------------------------------------------------------
"""

## @package stmlab.service
# Module containing all command line options.
## @author 
# Marc Garbade
## @date
# 21.10.2024
## @par Notes/Changes
# - Added documentation  // mg 21.10.2024

import os, sys
import requests
import tempfile

from stmlab import __version__, STMLabPath

from PyCODAC.API import main
from PyCODAC.API import Remote as remote

from PyCODAC.Tools import Utility

# Top-level module for modern relative import definitions
__module__ = Utility.PathLeaf(os.path.abspath(os.path.join(__file__,os.path.join(*[os.pardir]*2))))

# Top-level modifications of base application
__settings__ = {"workers":1, "api_version":__version__}

# Verify that default documentation can be reached in development mode
default_documentation = os.path.abspath(os.path.join(STMLabPath,"..","..","doc","stmlab"))
if os.path.exists(default_documentation):
    __settings__.update({ "static": os.path.abspath(os.path.join(default_documentation,"html","stmlab.html")),
                          "icon":os.path.abspath(os.path.join(default_documentation,"pics","stm_lab_logo_gitlab.jpg"))})
# Only attempt to download image when running in a docker container
elif Utility.IsDockerContainer():
    try: 
        # Try to download additional resources on-the-fly
        with open(os.path.join(tempfile.gettempdir(),"stm_lab_logo_gitlab.jpg"), 'wb') as handle:
            response = requests.get("https://gitlab.com/dlr-sy/stmlab/-/raw/stm_docs/stmlab/pics/stm_lab_logo_gitlab.jpg", allow_redirects=True, stream=True)
            # Something went wrong. Raise an error
            if not response.ok: raise FileNotFoundError
            # Download the image in chunks
            for block in response.iter_content(1024):
                if not block: break
                handle.write(block)
            # Update local settings upon success
            __settings__.update({"icon":os.path.join(tempfile.gettempdir(),"stm_lab_logo_gitlab.jpg")})
    # Fail gracefully
    except FileNotFoundError: pass

## Forward compatibility for remote calls.
setattr(sys.modules[__module__],"remote", remote)

if __name__ == '__main__':
    # Load local settings
    settings = __settings__
    # Execute application
    main(**settings); sys.exit()