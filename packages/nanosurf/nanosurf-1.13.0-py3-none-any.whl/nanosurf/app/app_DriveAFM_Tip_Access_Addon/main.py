""" Application template to be used to build own nice python applications
Copyright Nanosurf AG 2021
License - MIT
"""

import sys
import os
import nanosurf as nsf

import worker, gui

company_name = "Nanosurf"
app_name = "DriveAFM_TipAccess_Addon"

class MyApp(nsf.frameworks.qt_app.ApplicationBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def do_startup(self):
        self.add_module(worker.Worker(self, gui.Screen()))
       
if __name__ == "__main__":
    App = MyApp(company_name, app_name, main_file = os.path.abspath(__file__))
    App.start_app()
    sys.exit(App.execute())

