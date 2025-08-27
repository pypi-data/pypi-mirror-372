""" The application entry point
Copyright Nanosurf AG 2021
License - MIT
"""

import sys
import os
import nanosurf as nsf

from scan_module import module as scan_func
from scan_module import gui as scan_gui

company_name = "Nanosurf"
app_name = "Nanosurf Python Imaging and Library Demo"

class MyAppSettings(nsf.frameworks.qt_app.AppSettings):
    """ Settings defined here as PropVal are stored persistently in a ini-file"""
    AppHelloMsg = nsf.PropVal("Welcome to scan and library usage demo.")
    
class MyApp(nsf.frameworks.qt_app.ApplicationBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.settings = MyAppSettings()

    def do_startup(self):
        """ Insert any module used in this app. 
            If more than one module is added, a menu bar is shown in the app window
        """
        self.add_module(scan_func.ScanModule(self, scan_gui.ScanScreen()), "Scan Demo")

        # here we apply a setting value just for fun
        self.show_message(self.settings.AppHelloMsg.value)
        
    def do_shutdown(self):
        """ Handle cleaning up stuff here"""
        pass

if __name__ == "__main__":
    App = MyApp(company_name, app_name, main_file =  os.path.abspath(__file__))
    App.start_app()
    sys.exit(App.execute())

