# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %             Command Module - Classes and Functions           %
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
"""
Main entry point of STMLab package
 
@note: STMLab command line interface
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

## @package stmlab.command
# Module containing all command line options.
## @author 
# Marc Garbade
## @date
# 12.09.2024
## @par Notes/Changes
# - Added documentation  // mg 12.09.2024

import os, sys
import subprocess
import argparse
import keyring
import importlib.util
import shutil

try:
    ## Try to use typer as a modern CLI interface. 
    # Is allowed to fail
    from typing import Optional #@UnresolvedImport

    from typer import Typer as Command, Argument
    from typer import Context, Exit, Option
    
    from enum import Enum
except ImportError: pass

# Get current project version as code
from stmlab import __version__

## Definition of dictionary with default settings.
# Set the current project name
__settings__ = {"__base__" : "STMLab"}

# Get the current active user
try: __settings__.update({"__user__":os.getlogin()})
except OSError: __settings__.update({"__user__":None})

# Latest default environment 
__settings__.update({"__env__":{"py38":"python=3.8"}})

# Detect default virtual environment. Defaults to None.
if os.path.exists(os.path.join(sys.prefix,"conda-meta")): __settings__.update({"__backend__":"conda"})
else: __settings__.update({"__backend__":None})

# Define additional reqistry for package resolver
__url__ = "https://gitlab.dlr.de/api/v4/groups/541/-/packages/pypi/simple"

# All descriptions for duplicate methods and arguments
__help__= { "browser": "Start the application using the default system browser. Only meaningful in local mode. Defaults to False.",
            "create":"Create a new supported runtime using the currently active virtual environment manager.",
            "info":"Show the current version and system information.",
            "install":"Install additional python packages using the default package manager.",
            "login":"Provide credentials to access yet unpublished additional resources.",
            "main": 'CLI commands for %s.' % __settings__["__base__"],
            "name":"Name of the new environment.",
            "package":"Additional package(s) to be installed in the current environment",
            "password":"Associated password or token",
            "python":"A valid major and minor release version of python. Patch level (micro) is automatically determined upon installation.",
            "remote":"Your personal %s container is ready!\n\nPlease open:\n%s\n\nin a browser or application of your choice or use this command with '--use-browser'\nto connect to the application with your default browser immediately.",
            "start": "Launch STMLab application from the current system (based on JupyterLab) either locally or remotely.",
            "show": "Show all commands in execution order, but do not execute them.",
            "user": "User name used to access additional services",
            "version": "%s (%s)" % (__settings__["__base__"],__version__),
            }

def check(*args, **kwargs):
    """
    Validate if new environments can be created locally with the current settings
    """
    # Load path explicitly
    from stmlab import STMLabPath
    # Start of function
    if args: kind = args[-1]
    else: kind = next(iter(__settings__["__env__"]))
    paths = [os.path.abspath(os.path.join(STMLabPath,*x,"config","python",kind)) for x in (["service"],[os.path.os.path.pardir]*2)]
    # Check if a new environment can be created from scratch
    success = __settings__["__backend__"] and any(os.path.exists(x) for x in paths)
    # Return if new environment can be created from scratch
    if not kwargs.get("get_path",False) : return success
    # Return found path. Defaults to empty list of no paths can be found
    return success, [x for x in paths if os.path.exists(x)] if success else []

def install(package):
    # type: (str) -> None
    """
    Install additional packages using the default package manager with access to STMLab
    """
    # Define base command
    command = [os.path.join(sys.prefix,"scripts","pip"),"install","%s" % package]
    # Append all additional command line args
    command.extend(["%s" % x for x in sys.argv[sys.argv.index(package)+1:]])
    # Fetch token from keyring
    token = keyring.get_password(__url__,"token")
    # Modify CLI command if token has been given
    command.extend(["--extra-index-url"])
    if token: command.extend([__url__.replace("gitlab","token:%s@gitlab" % token)])
    else: command.extend([__url__])
    # Execute install command
    if package.strip(): subprocess.check_call(command)
    pass

def new(kind, *args, **kwargs):
    # type: (str) -> None
    """
    Create a new environment using the default virtual environment based on supported presets.
    """
    # Local lazy imports
    from PyXMake.Tools import Utility
    try: from rich import print
    except ImportError: pass
    # Some local variables
    delimn = "."; require = None; ListofCommands = []
    # Version and name of the new environment
    env_version = kind.replace("py","")
    env_name = kwargs.get("name","stmlab"+env_version)
    # Define a custom environment
    env = {"PIP_PREFER_BINARY":"1"}; env.update(os.environ.copy())
    # Check if the requested backend actually exists
    backend = kwargs.get("backend",__settings__["__backend__"])
    backend = Utility.GetExecutable(backend, get_path=True)[-1]
    if not backend: raise RuntimeError
    # Check if the requested backend is supported. 
    if not any(x in Utility.PathLeaf(backend) for x in ["conda"]): raise NotImplementedError
    else: command = [backend]
    # At this point, we have an error or a list named command
    command.extend(["env","create","-n", env_name])
    # Create the commands
    if check(kind, get_path=True)[-1]:
        # Create a new supported environment from YAML file
        command.extend(['--file=%s' % os.path.join(*check(kind, get_path=True)[-1],"conda.yml")])
    else: 
        # Remove unsupported entry. Add auto-install
        command.remove("env"); command.extend(["-y"])
        # Create a new environment for a given version. Only use the given requirements. 
        command.extend(["python=%s" % delimn.join([env_version[0]] + [*env_version.split(env_version[0])[1:]])])
    # Run the command in a temporary environment
    with Utility.TemporaryEnvironment(environ=env) as _, Utility.TemporaryDirectory() as _:
        ## Copy environment file into a temporary directory
        # This hack is meaningful only when using docker
        if Utility.IsDockerContainer() and command[-1].startswith("--file"):
            filepath = command[-1].split("--file=")[-1]
            newpath = os.path.join(os.getcwd(),Utility.PathLeaf(filepath))
            shutil.copy(filepath,newpath); command.pop(-1)
            command.extend(['--file=%s' % newpath])
            # Remove pip entry from the list
            with open(newpath, "r+") as f:
                lines = f.readlines(); f.seek(0);
                # Loop over all lines in the environment file
                require = [line.split("- -r" )[-1].strip() for line in lines if "- -r" in line][0]
                for line in lines:
                    ## Remove requirements part. Only when a requirements file is found.
                    # In all other cases, do nothing
                    if (line.strip().endswith("pip:") or "- -r" in line) and require: continue
                    f.write(line)
                f.truncate()
            # We have a relative requirements file. Get absolute path
            if require: require = os.path.abspath(os.path.join(os.path.dirname(filepath),require))
        # Base command
        ListofCommands.append(command)
        # We have no predefined environment. Use requirements directly
        if any(x.startswith("python") for x in command) or require: 
            ListofCommands.append([backend,"run","--live-stream","-n",env_name,"pip","install","-r",require or os.path.join(os.path.dirname(*check(get_path=True)[-1]),"requirements.txt")])
        # Iterative over all commands
        for i, command in enumerate(ListofCommands,1):
            # Execute the command
            if not kwargs.get("show"): subprocess.check_call(command)
            # Show all commands, but do not execute them
            else: print("%s: %s" % (str(i), command))
    pass

def run(*args, **kwargs): 
    """
    Launch main application
    """
    # Fetch all possible keyword arguments
    handle = kwargs.pop("method","local")
    token = kwargs.pop("token",None)
    # Local imports
    from stmlab import __exe__ as local
    from stmlab import service as server
    from stmlab import remote as remote #@UnresolvedImports
    # Create a local handle
    if handle in ["local"]: handle = local
    elif handle in ["server"]: handle = server
    elif handle in ["remote"]: handle = remote
    else: raise RuntimeError
    # Remove initial command to prevent inheriting
    try: sys.argv = sys.argv[:sys.argv.index('start')]
    except: pass
    # Obtain settings and with default launch settings
    settings = getattr(handle, "__settings__", {})
    # Collect mandatory token in remote 
    if token and handle in ["remote"]: 
        settings.update(kwargs)
    # Launch application with default settings
    return handle.main(**settings)

def secret(user, password):
    # type: (str, str) -> None
    """
    Provide login credentials for internal resources. 
    """
    keyring.set_password(__url__,"token",password)
    pass

try:
    # Modern interface using typer. Overwrite legacy method. Allowed to fail
    main = Command(help=__help__["main"], context_settings={"help_option_names": ["-h", "--help"]}, no_args_is_help=True)

    # Create a function to return the current version
    def __version_callback(value: bool):
        """
        Callback function to return the current version
        """
        # Only return value is requested. False by default
        if value:
            print(__help__["version"])
            raise Exit()
        pass

    # Modified entrypoint for typer interface
    @main.callback()
    def common(
        ctx: Context,
        version: Optional[bool] = Option(None, "--version", "-v", help="Show the current version.", callback=__version_callback, is_eager=True)):
        """
        Main entrypoint of STMLab CLI. All other commands are derived from here
        """
        pass

    # Entrypoint to return local system and version information
    @main.command("info",help=__help__["info"])
    def info(): 
        """
        Return local system information
        """
        return __version_callback(True)

    # Provide login credentials
    @main.command("login",help=__help__["login"])
    def login(
        user: str = Option(__settings__["__user__"],  "--user", "-u", help=__help__["user"]),
        password: str = Option(..., "--password", "-p", help=__help__["password"], prompt_required=False, prompt=True, confirmation_prompt=True, hide_input=True)):
        """
        Provide login credentials
        """
        secret(user, password)

    def create(
        kind: Enum("EnvObjectKind", eval('{**{"py27":"python=2.7"},**{"py3%s"%str(s) : "python=3.%s"%str(s) for s in range(5,14)}}')) = Argument(next(iter(__settings__["__env__"].values())),
                            metavar="python=<sys.version>",case_sensitive=False, show_default="python=3.8", help=__help__["python"]),
        name: str = Option("stmlab<sys.version>","--name","-n", help=__help__["name"]),
        show: Optional[bool] = Option(False, "--dry-run", help=__help__["show"])):
        """
        Create a new pristine environment from supported presets
        """
        # Collect all user inputs
        settings = {"backend":__settings__["__backend__"],"show":show}
        # Create a name for the environment. If left blank, add nothing
        if name not in ["stmlab<sys.version>"]:settings.update({"name":name})
        # Execute function to set up a new environment
        return new(str(kind.name).lower(),**settings)

    # Unified entry point to start local, server & remote version
    def launch(
        kind: Enum("ServerObjectKind",{"local":"local","server":"server","remote":"remote"}) = Argument("local",case_sensitive=False),
        browser: Optional[bool] = Option(False, "--use-browser", help=__help__["browser"]), 
        password: Optional[str] = Option(None, "--password","-p", prompt_required=False, prompt=False, hide_input=True, help=__help__["password"])):
        """
        Unified launch application entry point
        """
        # Local import to avoid naming collision
        from typer import launch as connect
        # If no browser version is requested, set environment variable to deactivate default runtime
        if browser: os.environ["NO_WEBRUNTIME"] = str(True)
        # Collect all other methods
        settings = {"method": str(kind.value).lower(),"token":password}
        # Execute start procedure
        result = run(**settings)
        # Only meaningful with remote version
        if settings["method"] in ["remote"] and browser: connect(result)
        # Do not launch remote application immediately. Instead, present the corresponding link.
        elif settings["method"] in ["remote"]:
            print("==================================")
            print(__help__["remote"] % (__settings__["__base__"], result))
            print("==================================")
        # Just to make it clear
        else: pass
        # Return result
        return result

    # Register all possible functions
    main.command("install", context_settings={"allow_extra_args": True, "ignore_unknown_options": True}, help=__help__["install"])(install)
    if check(): main.command("create",help=__help__["create"])(create)

except:
    # Solution w/o typer installed.
    def main():
        """
        Legacy entrypoint for STMLab. Only used when typer is not installed. Deprecated.
        """
        # Set description for CLI command
        parser = argparse.ArgumentParser(prog=__settings__["__base__"], description=__help__["main"])
        parser.add_argument('-v', '--version', action='version', version=__help__["version"])
        # Add all subcommands
        subparsers = parser.add_subparsers(dest='command')
        # Add info command
        subparsers.add_parser('info', help=__help__["info"])
        # Add create command
        subparsers.add_parser('create', help=__help__["create"])
        # Add arguments to install object
        _ = subparsers.add_parser('install', help=__help__["install"])
        _.add_argument("package", type=str, help=__help__["package"], nargs=argparse.REMAINDER)
        # Add arguments to login object
        _ = subparsers.add_parser('login', help=__help__["login"])
        _.add_argument("-u", "--user", type=str, help=__help__["user"], nargs=1, default=__settings__["__user__"])
        _.add_argument("-p", "--password", type=str, help=__help__["password"], nargs=argparse.REMAINDER)
        ## Only show start option when local requirements are met
        # Deprecated. Launching a new application is likely to fail in future version.
        try:
            if importlib.util.find_spec("PyCODAC") is None: raise ImportError
            subparsers.add_parser('start', help=__help__["start"])
        except ImportError: pass
        # Call functions from command line
        args = parser.parse_args()
        if args.command in ["info"]: parser.parse_args(['--version'])
        elif args.command in ["install"]: install(*args.package)
        elif args.command in ["login"]: secret(next(iter(args.user)), *args.password)
        elif args.command in ["create"]: 
            settings = {} # Collect all possible user options
            if args.name: settings.update({"name":next(iter(args.name))})
            if args.show: settings.update({"show":next(iter(args.show))})
            # Execute the command
            new(next(iter(args.kind)), **settings)
        elif args.command in ["start"]: run()
        # Always print help by default
        else: parser.print_help(sys.stdout)
        # Return nothing if called directly.
        return 0

try: 
    # Local imports
    if importlib.util.find_spec("PyCODAC") is None: raise ImportError
    # Only activate this option when PyCODAC can be found
    main.command("start", help=__help__["start"])(launch)
except (AttributeError, ImportError) as _: pass

if __name__ == "__main__":
    main(); sys.exit()