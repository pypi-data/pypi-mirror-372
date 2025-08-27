# ///
# /// Nanosurf version of PushButton
# ///
# /// Copyright (C) Nanosurf AG - All Rights Reserved (2021)
# /// Unauthorized copying of this file, via any medium is strictly prohibited
# /// https://www.nanosurf.com
# ///


from PySide6 import QtWidgets
from PySide6.QtCore import Signal


class NSFPushButton(QtWidgets.QPushButton):
    """ Custom PushButton version """
    clicked_event = Signal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.clicked.connect(self._on_clicked)
 
    def set_label(self, label: str):
       self.setText(label) 

    def label(self) -> str:
        return self.text()


    # internal ----------------------------------------------------
    
    def _on_clicked(self):
        self.clicked_event.emit()

