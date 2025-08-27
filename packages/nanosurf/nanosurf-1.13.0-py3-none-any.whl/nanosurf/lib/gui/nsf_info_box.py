
""" application wide info box
Copyright Nanosurf AG 2021
License - MIT
"""

from PySide6 import QtWidgets

from nanosurf.lib.gui import nsf_colors

class InfoBox(QtWidgets.QWidget):
    def __init__(self,  *args, hidden : bool = True, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_background_color(nsf_colors.NSFColorHexStr.Orange)
        self.set_text_color("000000")
        self.message = QtWidgets.QLabel()
        self.message.setFixedHeight(30)
        self.closeButton = QtWidgets.QPushButton("X")
        self.closeButton.setSizePolicy(QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)        
        self.box_layout = QtWidgets.QHBoxLayout()
        self.box_layout.addWidget(self.message)
        self.box_layout.addWidget(self.closeButton)
        self.setLayout(self.box_layout)
        self.setMaximumHeight(60)
        self.setHidden(hidden)
        self.closeButton.clicked.connect(self._on_close_button_clicked)
    
    def set_message(self, msg: str):
        self.message.setText(f"    {msg}")
        self.show_box(True)

    def show_box(self, show: bool):
        self.setHidden(not(show))

    def set_background_color(self, rgb_color_str: str):
        self.setStyleSheet(f"background-color:#{rgb_color_str};")

    def set_text_color(self, rgb_color_str: str):
        pass
        # self.setStyleSheet(f"color:#{rgb_color_str};")

    def _on_close_button_clicked(self):
        self.setHidden(True)

class NSFInfoBox(InfoBox):
    pass
