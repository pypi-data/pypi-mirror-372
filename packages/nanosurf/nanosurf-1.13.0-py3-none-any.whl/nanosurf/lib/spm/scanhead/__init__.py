"""Package for scripting the Nanosurf control software.
Copyright (C) Nanosurf AG - All Rights Reserved (2021)
License - MIT"""

import logging
import nanosurf.lib.spm.com_proxy as spm

class Scanhead():
    def __init__(self, spm: spm.Spm = None, *args):
        """Base class for dealing with Nanosurf scan heads. In this base class general scan head control. 
           For head specific functions, see the corresponding child classes
        """
        self.connected = False
        self.spm = None
        self.spm_app = None
        self.logger = logging.getLogger("Scanhead")

        if spm is not None:
            self.connect(spm)

    def connect(self, spm: spm.Spm) -> bool:
        """ Connect and setup d scan head"""
        if not self.connected:
            if spm is not None:
                self.spm = spm

                if self.spm.is_scripting_enabled():
                    self.spm_app = self.spm.application
                    
                    # let subclass connect to its hardware component
                    self.connected = self.do_connect()
                else:
                    self.logger.error("Scripting interface of spm controller is not enabled.")
            else:
                self.logger.error("Cannot connect to spm controller. spm of None was provided")
        return self.connected

    def is_connected(self) -> bool:
        """ return True if scan head controll is available"""
        return self.connected

    def do_connect(self) -> bool:
        """ This function has to be overwritten by the sub class"""
        raise NotImplementedError(self.__class__.__name__ + '.do_connect')

