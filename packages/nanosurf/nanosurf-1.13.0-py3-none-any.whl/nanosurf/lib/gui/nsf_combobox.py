# ///
# /// Line Edit for advanced number formatting
# ///
# /// Copyright (C) Nanosurf AG - All Rights Reserved (2021)
# /// Unauthorized copying of this file, via any medium is strictly prohibited
# /// https://www.nanosurf.com
# ///


from enum import IntEnum
import typing

from PySide6 import QtWidgets
from PySide6.QtCore import Qt, Signal

from nanosurf.lib.gui.nsf_widgets_common import LabelWidgetSize, WidgetLayout

class NSFComboEntry():
    id: int
    name : str

    def __init__(self, id: int | IntEnum, name: str) -> None:
        self.id = int(id)
        self.name = name


class _ComboboxQt(QtWidgets.QComboBox):

    value_changed_event = Signal(float)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._block_value_change_signal = False
        self.currentIndexChanged.connect(self._index_changed)

    # public interface ------------------------------------------

    def set_index(self, new_index: int, notify: bool = True):
        do_notify = notify and (new_index != self.currentIndex())
        self.setCurrentIndex(new_index)
        if do_notify:
            self._index_changed()

    def index(self) -> int:
        return int(self.currentIndex())  

    # internal functions --------------------------------------------    

    def _index_changed(self):
        if not(self._block_value_change_signal):
            self.value_changed_event.emit(self.index())    


class NSFComboBox(QtWidgets.QWidget):
    """ Custom Qt Widget to show text in a edit with a descriptive label. """
    value_changed_event = Signal(str)

    @staticmethod
    def create_entry_list_from_dict(entry_dict:dict[int,str]) -> list[NSFComboEntry]:
        entry_list:list[NSFComboEntry] = [] 
        for key, value in entry_dict.items():
            entry_list.append(NSFComboEntry(key, value))
        return entry_list

    def __init__(self, entries: list[NSFComboEntry] = [], label_str = "", layout:WidgetLayout = WidgetLayout.Vertical, text_align_label:Qt.AlignmentFlag=Qt.AlignmentFlag.AlignLeft, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._setup_widgets(label_str, layout, text_align_label)
        self.comp_entries = entries
        self.define_entries(self.comp_entries)
        self._combo.value_changed_event.connect(self._on_value_changed)

    def define_entries(self, entries: list[NSFComboEntry]):
        self.comp_entries = entries
        new_count = len(self.comp_entries)
        cur_count = self._combo.count()
                
        if new_count < cur_count: # trunc list of items to length of new_count
            cur_select = self._combo.currentIndex()
            for i in range(new_count, cur_count):
                self._combo.removeItem(0)
            if cur_select < new_count:
                self._combo.setCurrentIndex(cur_select)
            cur_count = new_count
        
        for i in range(cur_count): # replace available item with new text
            self._combo.setItemText(i,self.comp_entries[i].name)
        
        if new_count > cur_count: # add missing entries 
            for i in range(cur_count, new_count):
                self._combo.addItem(self.comp_entries[i].name)
 
    def set_value(self, id: int, notify: bool = True):
        self._combo.set_index(self._get_index_from_id(id))
        if notify:
            self._on_value_changed()        
       
    def set_label(self, label: str):
       self._label.setText(label) 

    def label(self) -> str:
        return self._label.text()

    def value(self) -> int:
        return self._get_id_from_index(self._combo.index())  

    def current_entry_name(self) -> str:
        return self._combo.currentText()

    def entry_name(self, id : int) -> str:
        return self.comp_entries[self._get_index_from_id(id)].name


    # internal ----------------------------------------------------
    
    def _setup_widgets(self, label_str: str, layout:WidgetLayout, text_align_label:Qt.AlignmentFlag):
        widget_layout = QtWidgets.QGridLayout()
        widget_layout.setContentsMargins(*LabelWidgetSize.content_margins)
        self._label = QtWidgets.QLabel()
        self._combo = _ComboboxQt()
        self._label.setText(label_str)
        if layout == WidgetLayout.Horizontal:
            widget_layout.setSpacing(LabelWidgetSize.spacing_horizontal) 
            widget_layout.setColumnStretch(0,1)
            widget_layout.setColumnStretch(1,2)
            self._label.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
            self._combo.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
            widget_layout.addWidget(self._label, 0,0, alignment=Qt.AlignVCenter | text_align_label)
            widget_layout.addWidget(self._combo, 0,1, alignment=Qt.AlignVCenter)        
        else:
            widget_layout.setSpacing(LabelWidgetSize.spacing_vertical) 
            self._label.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
            self._combo.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
            widget_layout.addWidget(self._label, 0,0, alignment=Qt.AlignTop    | text_align_label)
            widget_layout.addWidget(self._combo, 1,0, alignment=Qt.AlignBottom )
        self.setLayout(widget_layout)

    def _on_value_changed(self):
        self.value_changed_event.emit(self.value())

    def _get_index_from_id(self, id: int) -> int:
        found_index = -1
        index = 0
        for entry in self.comp_entries:
            if entry.id == id:
                found_index = index
                break
            index += 1
        return found_index

    def _get_id_from_index(self, index: int) -> int:
        return self.comp_entries[index].id

