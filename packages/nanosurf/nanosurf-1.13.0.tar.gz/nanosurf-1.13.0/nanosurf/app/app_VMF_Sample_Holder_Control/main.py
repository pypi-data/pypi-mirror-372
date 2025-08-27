""" Application template to be used to build own nice python applications
Copyright Nanosurf AG 2021
License - MIT
"""

import sys
import os
import argparse
import nanosurf as nsf

from start_screen.start_module import StartModule
from start_screen.start_gui import StartScreen

from vmf_control.vmf_module import VMFModule
from vmf_control.auto_image_module import AutoImageModule
from vmf_control.calibrate_module import CalibrateModule
from vmf_control.setup_module import SetupModule


company_name = "Nanosurf"
app_name     = "VMF Sample Holder Controller"

class MyAppSettings(nsf.frameworks.qt_app.AppSettings):
    """ Settings defined here as PropVal are stored persistently in a ini-file"""
    AppHelloMsg = nsf.PropVal("Welcome to the template")
    _is_in_simulation_mode = False
    _is_in_setup_mode = False
    _is_calibration_panel_shown = False
    
class MyApp(nsf.frameworks.qt_app.ApplicationBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.settings = MyAppSettings()

    def sw_version(self) -> tuple[int,int,int]:
        import _version
        major, minor, revision = _version.__version__.split(".")
        return (int(major), int(minor), int(revision))

    def do_startup(self):
        """ Insert any module used in this app. 
            If more than one module is added, a menu bar is shown in the app window
        """
        parser = argparse.ArgumentParser()
        parser.add_argument("--setup", help="Open the setup panel to prepare EEPROM", type=int, default=0)
        parser.add_argument("--calibrate", help="Display the calibration panel to calibrate field measurement", type=int, default=0)

        args = parser.parse_args()
        if args.setup:
            self.settings._is_in_setup_mode = bool(args.setup)
        if args.calibrate:
            self.settings._is_calibration_panel_shown = bool(args.calibrate)

        self.add_module(VMFModule(self), "VMF Control", None) 
        vmf_module = self.find_module("VMF Control")

        if self.settings._is_in_setup_mode:
            self.add_module(SetupModule(self, vmf_module), "Setup", None) 
        else:
            self.add_module(AutoImageModule(self, vmf_module), "Auto Imaging", None)
            if self.settings._is_calibration_panel_shown:
                self.add_module(CalibrateModule(self,vmf_module), "Calibration", None) 

        self.add_module(StartModule(self), "Start", StartScreen())

        
    def do_shutdown(self):
        """ Handle cleaning up stuff here"""
        pass

if __name__ == "__main__":
    App = MyApp(company_name, app_name, main_file = os.path.abspath(__file__))
    App.start_app()
    sys.exit(App.execute())

