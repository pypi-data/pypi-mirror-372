"""Package for scripting the Nanosurf control software.
Copyright (C) Nanosurf AG - All Rights Reserved (2021)
License - MIT"""

from typing import Union
from nanosurf.lib.spm.studio import Studio
try:
    from nanosurf.lib.spm.studio.wrapper.cmd_tree_spm import Root
except ImportError: 
    pass
from nanosurf.lib.spm.com_proxy import Spm, SPM

class SPMApp():
    def __init__(self, *args, **kwargs) -> None:
        self.ctrl_studio:Studio = None
        self.ctrl_mobile_s:Spm = None

    def connect(self, *args, **kwargs) -> Union[Studio, Spm]:
        self.ctrl_studio = Studio()
        if self.ctrl_studio.connect(*args, **kwargs):
            return self.ctrl_studio
        else:
            self.ctrl_studio:Studio = None
            self.ctrl_mobile_s = SPM(*args, **kwargs)
            if self.ctrl_mobile_s.is_connected():
                return self.ctrl_mobile_s
            else:
                self.ctrl_mobile_s:SPM = None
        return None

    def is_connected(self) -> bool:
        return (self.ctrl_mobile_s != None) or (self.ctrl_studio != None)
    
    def is_scripting_enabled(self) -> bool:
        if self.ctrl_studio != None:
            return self.ctrl_studio.is_scripting_enabled()
        if self.ctrl_mobile_s != None:
            return self.ctrl_mobile_s.is_scripting_enabled() and self.ctrl_mobile_s.is_lowlevel_scripting_enabled()
        return False

    @property
    def spm(self) -> Union['Root', Spm]:
        if self.ctrl_studio != None:
            return self.ctrl_studio.spm
        if self.ctrl_mobile_s != None:
            return self.ctrl_mobile_s
        return None

