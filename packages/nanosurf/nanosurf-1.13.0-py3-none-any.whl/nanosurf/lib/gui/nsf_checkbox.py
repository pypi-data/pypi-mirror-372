# ///
# /// NAnosurf version of CheckBox
# ///
# /// Copyright (C) Nanosurf AG - All Rights Reserved (2021)
# /// Unauthorized copying of this file, via any medium is strictly prohibited
# /// https://www.nanosurf.com
# ///


from PySide6 import QtWidgets
from PySide6.QtCore import Qt, Signal


class NSFCheckBox(QtWidgets.QCheckBox):
    """ Custom CheckBox version """
    value_changed_event = Signal(str)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stateChanged.connect(self._on_value_changed)
 
    def set_value(self, checked: bool, notify: bool = True):
        self.setChecked(checked)
        if notify:
            self._on_value_changed()        
       
    def value(self) -> bool:
        return self.checkState() != Qt.CheckState.Unchecked

    def set_label(self, label: str):
       self.setText(label) 

    def label(self) -> str:
        return self.text()


    # internal ----------------------------------------------------
    
    def _on_value_changed(self):
        self.value_changed_event.emit(self.value())

