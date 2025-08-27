""" Application template to be used to build own nice python applications
Copyright Nanosurf AG 2021
License - MIT
"""

import sys
import nanosurf as nsf

from switching_spec_module import module as switching_spec_func
from switching_spec_module import gui as switching_gui

company_name = "Nanosurf"
app_name_short = "SwitchingSpectroscopy"
app_name_long = "Switching spectroscopy application"

class MyAppSettings(nsf.frameworks.qt_app.AppSettings):
    """ Settings defined here as PropVal are stored persistently in a ini-file"""
    app_hello_msg = nsf.PropVal(f"Welcome to {app_name_long}")
    
class MyApp(nsf.frameworks.qt_app.ApplicationBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.settings = MyAppSettings()

    def do_startup(self):
        """ Insert any module used in this app. 
            If more than one module is added, a menu bar is shown in the app window
        """
        self.add_module(switching_spec_func.SwitchingSpecModule(self, switching_gui.SwitchingSpecScreen()), "Switching Spectroscopy")
        self.show_info_message(self.settings.app_hello_msg.value)
        
    def do_shutdown(self):
        """ Handle cleaning up stuff here"""
        pass

if __name__ == "__main__":
    App = MyApp(company_name, app_name_short, app_name_long)
    App.start_app()
    sys.exit(App.execute())

