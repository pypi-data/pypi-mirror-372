""" Application template to be used to build own nice python applications
Copyright Nanosurf AG 2021
License - MIT
"""

import sys
import os
import nanosurf as nsf

from demo_module import module as demo_func
from demo_module import gui as demo_gui

company_name = "My Company"
app_name     = "My Template Application"

class MyAppSettings(nsf.frameworks.qt_app.AppSettings):
    """ Settings defined here as PropVal are stored persistently in a ini-file"""
    AppHelloMsg = nsf.PropVal("Welcome to the template")
    
class MyApp(nsf.frameworks.qt_app.ApplicationBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.settings = MyAppSettings()

    def do_startup(self):
        """ Insert any module used in this app. 
            If more than one module is added, a menu bar is shown in the app window
        """
        self.add_module(demo_func.DemoModule(self), "PlotModule1", demo_gui.DemoScreen("Demo Module 1"))
        self.add_module(demo_func.DemoModule(self), "PlotModule2", demo_gui.DemoScreen("Demo Module 2"))
        # use self.add_module() again for more modules used in this application
        # or use self.add_screen() if a module has multiple screens  

        # here we apply a setting value just for fun
        self.show_message(self.settings.AppHelloMsg.value)
        
    def do_shutdown(self):
        """ Handle cleaning up stuff here"""
        pass

if __name__ == "__main__":
    App = MyApp(company_name, app_name, main_file = os.path.abspath(__file__))
    App.start_app()
    sys.exit(App.execute())

