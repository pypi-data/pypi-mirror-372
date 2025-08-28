# -*- coding: utf-8 -*-
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %                        Application                           %
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
"""
Main entry point of STMLab package
 
@note: STMLab executable
Created on 09.09.2024

@version:  1.0    
----------------------------------------------------------------------------------------------
@requires:
       - 

@change: 
       -    
   
@author: garb_ma                                                     [DLR-SY,STM Braunschweig]
----------------------------------------------------------------------------------------------
"""

## @package STMLab.__exe__
# Initialize STMLab environment for üython scripts executed using a standalone executable.
## @author 
# Marc Garbade
## @date
# 30.08.2024
## @par Notes/Changes
# - Added documentation // mg 30.08.2024

import os, sys
import marshal
import ipykernel_launcher

## Support environments where GIT is not installed. 
# Since GIT is not necessarily required to run this application, we overwrite the default error here
try: import git as _#@UnusedImport
except ImportError: os.environ["GIT_PYTHON_REFRESH"] = "quiet"

from stmlab import STMLabPath
from past.builtins import execfile

from PyCODAC.__exe__ import main

# Top-level modifications of base application
__settings__ = {"icon": os.path.join(STMLabPath,"assets","stmlab_icon.png"),"open_browser": bool(os.getenv("NO_WEBRUNTIME"))}

# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %                      Execute script                          %
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
if __name__ == '__main__':
    # Load local settings
    settings = __settings__
    
    # Start a interactive python kernel explicitly here   
    if ipykernel_launcher.__name__ in sys.argv:
        # Start a JupyterLab kernel
        sys.argv = sys.argv[2:]
        try:
            # We have a compiled source code base        
            s = open(os.path.join(sys._MEIPASS,".".join([ipykernel_launcher.__name__,"pyc"])), 'rb'); s.seek(12) #@UndefinedVariable
            code_obj = marshal.load(s); exec(code_obj) #@UndefinedVariable
        except:
            # We have the source code directly given in the resource folder
            execfile(os.path.join(sys._MEIPASS,".".join([ipykernel_launcher.__name__,"py"]))) #@UndefinedVariable            
        sys.exit()
    
    # Import top-level script from PyCODAC
    main(**settings); sys.exit()