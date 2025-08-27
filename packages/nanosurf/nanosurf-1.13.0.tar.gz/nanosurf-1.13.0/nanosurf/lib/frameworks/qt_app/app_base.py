""" The application base class of the application framework
Copyright Nanosurf AG 2021
License - MIT
"""

import sys
import os
import platform
import ctypes
import logging
import pathlib

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QSettings


import nanosurf as nsf
from nanosurf.lib.frameworks.qt_app.app_gui import AppWindow
from nanosurf.lib.frameworks.qt_app.app_common import MsgType
from nanosurf.lib.frameworks.qt_app.module_base import ModuleBase, ModuleScreen
from nanosurf.lib.datatypes.prop_val import PropStore, PropVal

dir_name_log = "log"
dir_name_config = "config"

class AppSettings(PropStore):
    Logging  = PropVal(True)
    LoadLastSettings = PropVal(True)
    ActiveModuleIndex = PropVal(int(0))

class ApplicationBase(QApplication):
    def __init__(self, company: str, app_name: str, main_file:pathlib.Path, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.company = company

        # check if second parameter 'main_file' is the path to application 
        # or 'app_name_long' as used up to v1.6 nanosurf library
        if pathlib.Path(main_file).is_absolute():
            self.main_path = pathlib.Path(main_file).parent
            name_long = str(app_name)
            name_short = name_long
        else:
            self.main_path = None
            name_short = str(app_name)
            name_long = str(main_file)

        self.app_name_long = name_long.removeprefix(" ").removesuffix(" ")
        self.app_name_short = name_short.removeprefix(" ").removesuffix(" ").replace(" ","_")
        
        if platform.system() == "Windows":
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(self.app_name_short)
            
        self.is_in_debugging_mode = (getattr(sys, 'gettrace', lambda : None)() is not None)

        """ Standard registry connection is defined here for further usage also by modules"""
        self.registry = QSettings(self.company, self.app_name_short)

        """ Standard files and folders are defined here for further usage also by modules"""
        self.framework_path = pathlib.Path(os.path.abspath(__file__)).parent
        self.app_data_path = pathlib.Path(os.path.expandvars(r'%LOCALAPPDATA%')) / pathlib.Path(self.company) / pathlib.Path(self.app_name_short) 
        self.log_path = self.app_data_path / dir_name_log
        self.config_path = self.app_data_path / dir_name_config
        self.config_file =  self.config_path / "last_config.ini"

        """ application specific settings """
        self.config_section = "Application"
        self.resource_path = self.framework_path 
        if self.main_path is not None:
            self.resource_path_user = self.main_path / "app"  
        else: 
            self.resource_path_user = self.resource_path
        self.settings = AppSettings()
        self.modules:dict[str, ModuleBase] = {}

    def start_app(self):
        nsf.util.fileutil.create_folder(self.config_path)
        nsf.datatypes.prop_val.load_from_ini_file(self.settings, self.config_file, self.config_section)   

        self.setup_logger()
        self.logger.debug(f"{self.main_path=}")
        self.logger.debug(f"{self.framework_path=}")
        self.logger.debug(f"{self.app_data_path=}")
        self.logger.debug(f"{self.log_path=}")
        self.logger.debug(f"{self.config_path=}")
        self.logger.debug(f"{self.resource_path=}")
        self.logger.debug(f"{self.resource_path_user=}")

        self.appwindow = AppWindow(self)
        self.appwindow.create_gui(self.get_resource_file("app_stylesheet.qss"), self.get_resource_file("app_icon.ico"))
        self.lastWindowClosed.connect(self.quit_app)
        self.do_startup()
        self.close_splash_screen()
        self.appwindow.activate_screen(self.settings.ActiveModuleIndex.value)
        self.appwindow.show()
        self.logger.info("App running...")

    def quit_app(self):
        self.stop_modules()
        self.do_shutdown()
        nsf.datatypes.prop_val.save_to_ini_file(self.settings, self.config_file, self.config_section)   

    def close_splash_screen(self):
        """ this function closes the splash screen created by pyinstaller """
        try:
            import pyi_splash
            pyi_splash.close()
        except Exception:
            pass

    def set_user_resource_path(self, resource_path: pathlib.Path):
        self.resource_path_user = resource_path

    def do_startup(self):
        raise NotImplementedError(f"Subclass of '{self.__class__.__name__}' has to implement '{sys._getframe().f_code.co_name}()'")
   
    def do_shutdown(self):
        pass

    def execute(self):
        self.exec()

    def save_settings(self, module: ModuleBase):
        if isinstance(module.settings, PropStore):
            nsf.datatypes.prop_val.save_to_ini_file(module.settings,self.config_file, module.name)
 
    def load_settings(self, module: ModuleBase):
        if isinstance(module.settings, PropStore):
            if self.settings.LoadLastSettings.value:
                nsf.datatypes.prop_val.load_from_ini_file(module.settings, self.config_file, module.name)
    
    def get_resource_file(self, filename:str) -> pathlib.Path:
        file_name = pathlib.Path(filename)
        resource_path_user = self.resource_path_user / file_name
        resource_path_framework = self.resource_path / file_name
        if resource_path_user.is_file(): 
            return resource_path_user
        else: 
            return resource_path_framework       
    
    def setup_logger(self, logfile: pathlib.Path = pathlib.Path("latest.log")):   
        """
        Setup Logger if needed and differ between consol and file output
        set up logging to file and choose logger level (from highest level to lowest: Debug, info, warning, error, critical)
        """ 
        if self.settings.Logging.value:
            nsf.util.fileutil.create_folder(self.log_path)
            logfilepath = str(self.log_path / logfile) 
            logging.basicConfig(level=logging.DEBUG,
                                format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                                datefmt='%m-%d %H:%M:%S',
                                filename=logfilepath,
                                filemode='w')
            console = logging.StreamHandler()
            console.setLevel(logging.INFO)
            formatter = logging.Formatter('%(name)-12s %(levelname)-8s %(message)s')
            console.setFormatter(formatter)
            logging.getLogger('').addHandler(console)
        self.logger = logging.getLogger('Application')
        self.logger.setLevel(logging.DEBUG)

    def show_error_message(self, msg:str):
        self.show_message(msg, MsgType.Error)
        
    def show_warn_message(self, msg:str):
        self.show_message(msg,MsgType.Warn)
        
    def show_info_message(self, msg:str):
        self.show_message(msg,MsgType.Info)
        
    def clear_message(self):
        self.appwindow.hide_message()

    def show_message(self, msg: str, msg_type: MsgType = MsgType.Info):
        self.appwindow.show_message(msg, msg_type)

    def add_module(self, new_module: ModuleBase, name:str ="Module", new_screen:ModuleScreen = None):
        new_module.name = name
        if new_screen is not None:
            new_module.ui = new_screen
        if new_module.name not in self.modules: 
            self.logger.info(f"Start module: {new_module.name}")
            self.modules[new_module.name] = new_module
            new_module.start()
            if new_module.ui is not None:
                if new_module.ui.name is None:
                    new_module.ui.name = name
                self.add_screen(new_module, new_module.ui, new_module.ui.name)
      
    def add_screen(self, module: ModuleBase, new_screen:ModuleScreen, screen_name:str = None):
        if screen_name is not None:
            new_screen.name = screen_name
        if not self.appwindow.has_screen(new_screen):
            new_screen.create_screen(module)
            self.appwindow.add_screen(new_screen, screen_name)
        self.appwindow.activate_screen(new_screen)

    def get_module_count(self) -> int:
        return len(self.modules)    

    def find_module(self, module_name:str) -> ModuleBase:
        if module_name in self.modules:
            return self.modules[module_name]
        return None

    def activate_module(self, module_index: int):
        self.settings.ActiveModuleIndex.value = module_index
        self.appwindow.set_active_module_by_index(module_index)   

    def remove_module(self, module: ModuleBase = None, name:str = None):
        if name is not None:
            module = self.find_module(name)
        if module is not None:
            if module.name in self.modules:
                screen = self.appwindow.find_screen(module.name)
                if screen is not None:
                    screen.cleanup_screen()
                module.stop()
                del self.modules[module.name]
        
    def stop_modules(self):
        for name, mod in list(self.modules.items()):
            self.logger.info(f"Stop module: {name}")
            self.remove_module(mod)

    def activate_debugger_support_for_this_thread(self):
        """ This function has to be called from each new thread to activate debugger support for it"""
        if self.is_in_debugging_mode:
            import debugpy
            debugpy.debug_this_thread()            
 
