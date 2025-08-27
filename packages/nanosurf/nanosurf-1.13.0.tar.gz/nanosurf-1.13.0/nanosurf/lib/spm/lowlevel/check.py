""" Functions to detect objects from standard spm software or studio 
Copyright (C) Nanosurf AG - All Rights Reserved (2023)
License - MIT"""

from nanosurf.lib.spm.lowlevel.logical_unit_interface import _Attribute, _LogicalUnit
from nanosurf.lib.spm.studio.wrapper import CmdTreeNode, CmdTreeProp

def is_studio_attribute(obj) -> bool:
        return isinstance(obj, CmdTreeProp)

def is_spm_attribute(obj) -> bool:
        return isinstance(obj, _Attribute)

def is_spm_lu(obj) -> bool:
        return isinstance(obj, _LogicalUnit)

def is_studio_lu(obj) -> bool:
        return isinstance(obj, CmdTreeNode)

def is_studio(obj) -> bool:
       return is_studio_attribute(obj) or is_studio_lu(obj)
       
def is_spm(obj) -> bool:
       return is_spm_attribute(obj) or is_spm_lu(obj)