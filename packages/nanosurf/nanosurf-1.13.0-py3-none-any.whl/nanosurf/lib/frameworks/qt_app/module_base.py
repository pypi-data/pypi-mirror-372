""" The base class for functional modules
Copyright Nanosurf AG 2021
License - MIT
"""
import sys
import logging

from PySide6 import QtWidgets, QtCore


control_layout_width = 200

class CtrlSpacer(QtWidgets.QSpacerItem):
    def __init__(self):
        super().__init__(control_layout_width,40, QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.MinimumExpanding)

class ModuleBase(QtCore.QObject):
    def __init__(self, app:'ApplicationBase', gui = None):
        super().__init__()
        self.app:'ApplicationBase' = app
        self.ui:ModuleScreen = gui
        self.settings = None
        self.__name = ""
        self.logger = logging.getLogger(self.__name)
 
    def start(self):
        self.app.load_settings(self)
        self.do_start()

    @property
    def gui(self):
        return self.ui

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, name):
        self.__name = name
        self.logger = logging.getLogger(self.__name)

    def stop(self):
        self.do_stop()
        self.app.save_settings(self)

    def do_start(self):
        raise NotImplementedError(f"Subclass of '{self.__class__.__name__}' has to implement '{sys._getframe().f_code.co_name}()'")

    def do_stop(self):
        raise NotImplementedError(f"Subclass of '{self.__class__.__name__}' has to implement '{sys._getframe().f_code.co_name}()'")

class ModuleScreen(QtWidgets.QWidget):
    def __init__(self, screen_name:str = None):
        self.module:ModuleBase = None
        self.name = screen_name
        super().__init__()

    def create_screen(self, module: ModuleBase):
        """
        lets create the gui. Creates all GUI elements but no action yet. 
        This is done later in ConnectGUI()
        """
        self.module = module
        self.do_setup_screen(self.module)
    
    def cleanup_screen(self):
        self.do_cleanup_screen()

    def do_setup_screen(self, module: ModuleBase):
        """ Called once during initialization of a new screen"""
        raise NotImplementedError(f"Subclass of '{self.__class__.__name__}' has to implement '{sys._getframe().f_code.co_name}()'")

    def do_cleanup_screen(self):
        """ Called once during destruction of a screen"""
        pass
    
    def on_activate_screen(self):
        """ called each time a screen is getting focus"""
        self.module.app.clear_message()

    def on_deactivate_screen(self):
        """ called each time a screen is loosing focus"""
        pass

