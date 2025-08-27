"""Package for scripting the Nanosurf control software.
Copyright (C) Nanosurf AG - All Rights Reserved (2021)
License - MIT"""

import os
import platform 
import pathlib

from nanosurf._version import __version__

from nanosurf.lib import datatypes, math, util

# make all library modules accessible from this level
if platform.version() != "Nanosurf_Linux":
    from nanosurf.lib import gui, frameworks
    from nanosurf.lib import plot

# direct access to most used datatypes
from nanosurf.lib.datatypes import sci_val
from nanosurf.lib.datatypes.sci_stream import SciStream
from nanosurf.lib.datatypes.sci_val import SciVal
from nanosurf.lib.datatypes.sci_channel import SciChannel

if platform.version() != "Nanosurf_Linux":
    from nanosurf.lib.datatypes.prop_val import PropStore, PropVal

# other direct access to common sub packages
from nanosurf.lib.math import sci_math 

if platform.system() == "Windows":
    from nanosurf.lib import spm, devices
    from nanosurf.lib.spm.com_proxy import Spm, SPM, C3000, USPM, Naio, CoreAFM, Easyscan2, MobileS, SPM_S
    from nanosurf.lib.spm.studio import Studio
    from nanosurf.lib.spm.spm_app import SPMApp
    from nanosurf.lib.spm import studio

if platform.system() == "Linux":
    from nanosurf.lib import devices

def package_path() -> pathlib.Path:
    return pathlib.Path(os.path.dirname(os.path.abspath(__file__)))

def doc_path() -> pathlib.Path:
    return package_path() / "doc"

def lib_path() -> pathlib.Path:
    return package_path() / "lib"

def app_path() -> pathlib.Path:
    return package_path() / "app"

def library_version() -> tuple[int,int,int,int]:
    major, minor, revision = __version__.split(".")
    return (int(major), int(minor), int(revision), 0)

def help(): 
    print("Nanosurf python script package:")
    print("-------------------------------")
    print(f"Installed version: {__version__}")
    print("\nThe library documentation is here:")
    print(doc_path())
    for doc in os.listdir(doc_path()):
        print(f"  {doc}")
    print("\nThe demos and apps are stored here:")
    print(app_path())
    for demo in os.listdir(app_path()):
        print(f"  {demo}")

def get_py_installer_hook_dirs():
    return [os.path.dirname(__file__)]
