""" The GUI of the application framework
Copyright Nanosurf AG 2021
License - MIT
"""

from PySide6 import QtWidgets
from PySide6 import QtGui, QtWidgets, QtCore

import typing
from dataclasses import dataclass
import nanosurf as nsf

from . import app_common, module_base

control_layout_width = 200

class StdVSpacer(nsf.lib.gui.NSFVSpacer):
    def __init__(self):
        super().__init__(width=control_layout_width, minimal_height=40)
        print("Depreciation warning: StdVSpacer will be removed in further library version. use nanosurf.gui.lib.NSFVSpacer instead")

class MenuSeparator(nsf.lib.gui.NSFHLine):
    def __init__(self, hidden:bool = False, height: int = 1,  **kargs):
        super().__init__(show=not hidden, width=height, *kargs)

class MenuButton(QtWidgets.QWidget):
  
    sig_on_menu_clicked = QtCore.Signal(int)
   
    def __init__(self, menutext: str, menuitem: int):
        super().__init__()
        self._setup_widgets(menutext)
        self.set_highlight(False)
        self.menuitem = menuitem
        self._button.clicked.connect(self._on_clicked)
    
    def set_highlight(self, highlight: bool = False):
        color = nsf.gui.nsf_colors.NSFColorHexStr.Orange if highlight else nsf.gui.nsf_colors.NSFColorHexStr.Soft_Gray
        self._marker_line.setStyleSheet(f"background-color:#{color};")

    def _on_clicked(self):
        self.sig_on_menu_clicked.emit(self.menuitem)

    def _setup_widgets(self, label_str: str):
        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0,0,0,0)
        self._button = QtWidgets.QPushButton(label_str)
        self._marker_line = MenuSeparator(hidden=False, height=2)
        layout.addWidget(self._marker_line)
        layout.addWidget(self._button)
        self.setLayout(layout)      


@dataclass
class ScreenDef:
    screen:module_base.ModuleScreen = None
    name:str = ""

class AppWindow(QtWidgets.QMainWindow):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.list_of_screens:list[ScreenDef] = []

    def create_gui(self, ui_style_file : str, icon_file : str):
        # create main GUI layout
        style_sheet_str = self._read_style_sheet_into_str(ui_style_file)
        self.setStyleSheet(style_sheet_str)
        self.setWindowTitle(self.app.app_name_long)
        self.setWindowIcon(QtGui.QIcon(str(icon_file)))
        self.statusBar().showMessage("Ready")

        # setup general GUI layout
        # on the left will be a menu to open the modules stacked guis on the right
        self.mainScreen = QtWidgets.QWidget()
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_menu = QtWidgets.QHBoxLayout()
        self.main_messagebox = nsf.gui.NSFInfoBox(hidden=True)
        self.main_stack = QtWidgets.QStackedLayout()
        self.main_stack.addWidget(QtWidgets.QLabel("Main screen"))

        self.menu_sep = MenuSeparator(hidden=True)
        self.status_sep = MenuSeparator(hidden=False)
        self.main_layout.addLayout(self.main_menu,0)
        self.main_layout.addWidget(self.menu_sep,1)
        self.main_layout.addWidget(self.main_messagebox,2)
        self.main_layout.addLayout(self.main_stack,3)
        self.main_layout.addWidget(self.status_sep,4)
        #self.main_layout.addSpacerItem(nsf.gui.NSFVSpacer()))
        self.mainScreen.setLayout(self.main_layout)
        self.setCentralWidget(self.mainScreen)
        self.load_window_size()

    def show_message(self, msg: str, msg_type: app_common.MsgType = app_common.MsgType.Info):
        if msg_type == app_common.MsgType.Error:
            self.show_info_box(msg, background_color=nsf.gui.nsf_colors.NSFColorHexStr.Orange)
        elif msg_type == app_common.MsgType.Warn:
            self.show_info_box(msg, background_color=nsf.gui.nsf_colors.NSFColorHexStr.Orange)
        else:
            self.statusBar().showMessage(msg)        

    def hide_message(self):
        self.statusBar().showMessage("")       
        self.hide_info_box()

    def save_window_size(self):
        self.app.registry.setValue("geometry", self.saveGeometry())
        self.app.registry.setValue("windowState", self.saveState())
    
    def load_window_size(self):
        self.restoreGeometry(self.app.registry.value("geometry"))
        self.restoreState(self.app.registry.value("windowState"))

    def has_screen(self, screen: module_base.ModuleScreen) -> bool:
        found = False
        for screen_def in self.list_of_screens:
            if screen_def.screen.name == screen.name:
                found = True
                break
        return found
    
    def add_screen(self, gui: module_base.ModuleScreen, screen_name:str):
        self.list_of_screens.append(ScreenDef(gui, screen_name))
        if isinstance(gui, QtWidgets.QWidget):
            self.main_stack.addWidget(gui)
            # activate first screen 
            if self.main_stack.currentIndex() == 0:
                self.main_stack.setCurrentWidget(gui)
        self.update_menu()

    def get_active_module_index(self) -> int:
        return self.main_stack.currentIndex() - 1

    def set_active_module_by_index(self, index: int):
        self.main_stack.setCurrentIndex(index+1)
        screen = typing.cast(module_base.ModuleScreen, self.main_stack.currentWidget())
        screen.on_activate_screen()
        self._update_menu_button_highlight()

    def find_screen(self, screen_name:str) -> module_base.ModuleScreen:
        for screen_def in self.list_of_screens:
            if screen_def.name == screen_name:
                return screen_def.screen
        return None
    
    def is_menu_visible(self) -> bool:
        return len(self.list_of_screens) > 0

    def update_menu(self):
        num_of_screens = len(self.list_of_screens)
        # show menu only if there are more than one modules with gui present
        if num_of_screens > 1:
            #remove all menu items
            while self.main_menu.count():
                child = self.main_menu.takeAt(0)
                if child.widget() is not None:
                    child.widget().deleteLater()
            # add menu items
            for menuindex, screendef in enumerate(self.list_of_screens):
                    menuitem = MenuButton(screendef.name, menuindex)
                    menuitem.sig_on_menu_clicked.connect(self._on_menu_button_clicked)
                    self.main_menu.addWidget(menuitem)
            self.main_menu.addStretch() 

        self.menu_sep.setHidden(num_of_screens <= 1)
        
    def activate_screen(self, screen: int | str | module_base.ModuleScreen):
        screen_index = -1
        if isinstance(screen, int):
            screen_index = screen
        if isinstance(screen, str):
            for index, screen_def in enumerate(self.list_of_screens):
                if screen_def.name == screen:
                    screen_index = index
                    break
        if isinstance(screen, module_base.ModuleScreen):
            for index, screen_def in enumerate(self.list_of_screens):
                if screen_def.screen.name == screen.name:
                    screen_index = index
                    break
        if screen_index >= 0:                
            self.app.settings.ActiveModuleIndex.value = screen_index
            self.set_active_module_by_index(screen_index)   
                
    # internal use only

    def closeEvent(self, arg):
        """ capture close button from application window"""
        self.save_window_size()
        super().closeEvent(arg)

    def _read_style_sheet_into_str(self, style_file: str):
        style = ""
        with open(style_file) as f:
            style = f.read()
        return style
    
    def _on_menu_button_clicked(self, index: int):
        self.activate_screen(index)

    def _update_menu_button_highlight(self):
        if self.is_menu_visible():
            active_index = self.get_active_module_index()
            for i in range(self.main_menu.count()-1):
                self.main_menu.itemAt(i).widget().set_highlight(i == active_index)

    def show_info_box(self, msg: str, background_color: str, text_color: str = ""):
        self.main_messagebox.set_background_color(background_color)
        if text_color != "":
            self.main_messagebox.set_text_color(text_color)
        self.main_messagebox.set_message(msg)
        self.main_messagebox.setHidden(False)

    def hide_info_box(self):
        self.main_messagebox.setHidden(True)
