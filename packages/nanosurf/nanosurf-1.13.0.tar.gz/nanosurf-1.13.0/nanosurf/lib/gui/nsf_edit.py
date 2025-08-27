# ///
# /// Line Edit for advanced number formatting
# ///
# /// Copyright (C) Nanosurf AG - All Rights Reserved (2021)
# /// Unauthorized copying of this file, via any medium is strictly prohibited
# /// https://www.nanosurf.com
# ///

from PySide6 import QtGui, QtWidgets
from PySide6.QtCore import Qt, Signal

from nanosurf.lib.gui.nsf_widgets_common import LabelWidgetSize, WidgetLayout

class _LineEditQt(QtWidgets.QLineEdit):

    value_changed_event = Signal(float)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._block_value_change_signal = False

    # public interface ------------------------------------------

    def set_value(self, new_value: str, notify: bool = True):
        do_notify = notify and (new_value != self.text())
        self.setText(new_value)
        if do_notify:
            self._value_changed()

    def value(self) -> str:
        return self.text()  

    # internal functions --------------------------------------------    

    # def focusInEvent(self, event: QtGui.QFocusEvent) -> None:
    #     """ overwrite handler for widget focus events"""
    #     super().focusInEvent(event)

    def focusOutEvent(self, event: QtGui.QFocusEvent) -> None:
        """  overwrite handler for widget focus events"""
        super().focusOutEvent(event)
        self._value_changed()

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        """ overwrite handler for key events"""
        if self.isReadOnly():
            return
        shift = (event.modifiers() == Qt.ShiftModifier)
        ctrl = (event.modifiers() == Qt.ControlModifier)
        key = event.key()
        if (key == Qt.Key_Return) or (key == Qt.Key_Enter):
            super().keyPressEvent(event)
            self._value_changed()
        else:
            super().keyPressEvent(event)

    def _value_changed(self):
        if not(self._block_value_change_signal):
            self.value_changed_event.emit(self.value())    


class NSFEdit(QtWidgets.QWidget):
    """ Custom Qt Widget to show text in a edit with a descriptive label. """
    value_changed_event = Signal(str)

    def __init__(self, label_str = "", layout:WidgetLayout = WidgetLayout.Vertical, text_align_edit:Qt.AlignmentFlag=Qt.AlignmentFlag.AlignLeft, text_align_label:Qt.AlignmentFlag=Qt.AlignmentFlag.AlignLeft, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._setup_widgets(label_str, layout, text_align_edit, text_align_label)
        self._edit.value_changed_event.connect(self._on_value_changed)
 
    def set_value(self, text: str, notify: bool = True):
        self._edit.set_value(text)
        if notify:
            self._on_value_changed()        
       
    def set_label(self, label: str):
       self._label.setText(label) 

    def set_read_only(self, set_read_only: bool = True):
        self._edit.setReadOnly(set_read_only)
        self._edit.setDisabled(set_read_only)
   
    def read_only(self) -> bool:
        return self._edit.isReadOnly()

    def label(self) -> str:
        return self._label.text()

    def value(self) -> str:
        return self._edit.value()  


    # internal ----------------------------------------------------

    def _setup_widgets(self, label_str: str, layout:WidgetLayout, text_align_edit:Qt.AlignmentFlag.AlignLeft, text_align_label:Qt.AlignmentFlag):
        widget_layout = QtWidgets.QGridLayout()
        widget_layout.setContentsMargins(*LabelWidgetSize.content_margins)
        self._edit = _LineEditQt()
        self._edit.setAlignment(text_align_edit)
        self._label = QtWidgets.QLabel()
        self._label.setText(label_str)
        if layout == WidgetLayout.Horizontal:
            widget_layout.setSpacing(LabelWidgetSize.spacing_horizontal)        
            widget_layout.setColumnStretch(0,1)
            widget_layout.setColumnStretch(1,2)
            self._label.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
            self._edit.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
            widget_layout.addWidget(self._label, 0,0, alignment=Qt.AlignVCenter | text_align_label)
            widget_layout.addWidget(self._edit,  0,1, alignment=Qt.AlignVCenter )        
        else:
            widget_layout.setSpacing(LabelWidgetSize.spacing_vertical)        
            self._label.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
            self._edit.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
            widget_layout.addWidget(self._label, 0,0, alignment=Qt.AlignTop    | text_align_label)
            widget_layout.addWidget(self._edit,  1,0, alignment=Qt.AlignBottom )
        self.setLayout(widget_layout)

    def _on_value_changed(self):
        self.value_changed_event.emit(self.value())

