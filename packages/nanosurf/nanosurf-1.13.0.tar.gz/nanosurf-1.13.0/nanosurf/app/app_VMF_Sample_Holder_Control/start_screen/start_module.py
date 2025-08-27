""" The functional module where the functionality goes
Copyright Nanosurf AG 2021
License - MIT
"""
# import pathlib
# import numpy as np
# from scipy import io as sio
# from typing import Tuple
from PySide6.QtCore import Signal

import nanosurf as nsf
from start_screen import start_settings as settings

from vmf_control import vmf_gui
from vmf_control import setup_gui
from vmf_control import vmf_module
import typing

class StartModule(nsf.frameworks.qt_app.ModuleBase):

    sig_update_serial_no = Signal(str, str)

    #  Initialization functions of the module 

    def __init__(self, app: nsf.frameworks.qt_app.ApplicationBase, gui = None):
        super().__init__(app, gui)
        self.app:nsf.frameworks.qt_app.ApplicationBase #  type hint
        self.settings = settings.StartSettings()

    def do_start(self):
        self.vmf_control = typing.cast(vmf_module.VMFModule,self.app.find_module("VMF Control"))
        pass

    def do_stop(self):
        # This function is called once at application shutdown 
        pass

    def startup(self):
        self.app.clear_message()
        self.vmf_control.sig_connecting_done.connect(self._on_end_of_connecting)
        self.vmf_control.start_connect_to_vmf_controller()

    def _on_end_of_connecting(self):
        vmf_ctrl_sn = self.vmf_control.vmf_controller_sn_number() 
        vmf_holder_sn =  self.vmf_control.vmf_sample_holder_sn_number()
        if not self.app.settings._is_in_setup_mode:
            if self.vmf_control.is_vmf_ready():
                self.app.add_screen(self.vmf_control, vmf_gui.VMFScreen(), "VMF Control")
            elif vmf_ctrl_sn == "" or vmf_ctrl_sn == "124-xx-xxx":
                self.app.show_info_message("Could not find any VMF-Controller")
            elif vmf_holder_sn == ""  or vmf_holder_sn == "125-xx-xxx":
                self.app.show_info_message(self.vmf_control.get_last_message())
                self.app.show_error_message("No VMF Sample Holder is connected to VMF-Controller")
            else:
                self.app.show_info_message(self.vmf_control.get_last_message())
                self.app.show_error_message("Unknown startup error detected.")
        else:
            self.app.add_screen(self.app.find_module("Setup"), setup_gui.SetupScreen(), "Setup") 

        self.sig_update_serial_no.emit(vmf_ctrl_sn, vmf_holder_sn)
