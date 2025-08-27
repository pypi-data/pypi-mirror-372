""" This is the screen of the module
Copyright Nanosurf AG 2021
License - MIT
"""

import pathlib
from PySide6 import QtWidgets, QtCore
import nanosurf as nsf

from start_screen import start_module

class StartScreen(nsf.frameworks.qt_app.ModuleScreen):
    
    def __init__(self):
        super().__init__()
        self.module:start_module.StartModule # give pylance a type hint

    def do_setup_screen(self, worker: start_module.StartModule):
        """ create here your gui with all controls and their layout"""
        self.module = worker
 
        self.button_connect = nsf.gui.NSFPushButton("Connect")
        self.label_sn_number = QtWidgets.QLabel("")

        self.layout_screen = QtWidgets.QVBoxLayout()

        self.layout = QtWidgets.QGridLayout()
        self.layout.addWidget(QtWidgets.QLabel(""),0,0)
        self.layout.addWidget(QtWidgets.QLabel("Power up and connect VMF-Controller"),0,1, alignment=QtCore.Qt.AlignmentFlag.AlignHCenter)
        self.layout.addWidget(QtWidgets.QLabel(""),0,2)
        self.layout.addWidget(QtWidgets.QLabel(""),1,0)
        self.layout.addWidget(QtWidgets.QLabel("Start AFM Software and then connect"),1,1, alignment=QtCore.Qt.AlignmentFlag.AlignHCenter)
        self.layout.addWidget(QtWidgets.QLabel(""),1,2)
        self.layout.addWidget(QtWidgets.QLabel(""),2,0)
        self.layout.addWidget(self.button_connect,2,1)
        self.layout.addWidget(QtWidgets.QLabel(""),2,2)
        self.layout.addWidget(QtWidgets.QLabel(""),3,0)
        self.layout.addWidget(self.label_sn_number,3,1, alignment=QtCore.Qt.AlignmentFlag.AlignHCenter)
        self.layout.addWidget(QtWidgets.QLabel(""),3,2)

        self.layout_screen.addStretch()
        self.layout_screen.addLayout(self.layout)
        self.layout_screen.addStretch()
        self.layout_screen.addWidget(QtWidgets.QLabel(f"SW Version {self.module.app.sw_version()}"))
        self.setLayout(self.layout_screen)

        self.bind_gui_elements()

    def bind_gui_elements(self):
        self.button_connect.clicked_event.connect(self.on_button_connect_clicked)   
        self.module.sig_update_serial_no.connect(self.on_end_of_startup) 

    def on_button_connect_clicked(self):
        self.button_connect.setEnabled(False)
        self.button_connect.setText("Connecting...")
        self.label_sn_number.setText("")
        self.module.startup()

    def on_end_of_startup(self, sn_no:str, holder_no:str):
        if sn_no == "":
            sn_no = "-"
        if holder_no == "":
            holder_no = "-"
        self.label_sn_number.setText(f"VMF-Controller: {sn_no}, Sample Holder: {holder_no}")
        self.button_connect.setText("Connect")
        self.button_connect.setEnabled(True)

