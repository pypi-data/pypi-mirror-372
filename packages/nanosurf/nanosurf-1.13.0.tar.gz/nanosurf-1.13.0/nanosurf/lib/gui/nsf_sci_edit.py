# ///
# /// Line Edit for advanced number formatting
# ///
# /// Copyright (C) Nanosurf AG - All Rights Reserved (2021)
# /// Unauthorized copying of this file, via any medium is strictly prohibited
# /// https://www.nanosurf.com
# ///

import typing
import enum
import math
import sys

from PySide6 import QtGui, QtWidgets
from PySide6.QtCore import Qt, QTimer, Signal

import nanosurf.lib.datatypes.sci_val as sci_val
import nanosurf.lib.datatypes.sci_val.unit_prefix as up
from nanosurf.lib.gui.nsf_widgets_common import LabelWidgetSize, WidgetLayout


class StepMode(enum.IntEnum):
    rel_1st_digi = 0, # increment relative the first significant digit 123.45 -> 223.45
    rel_2nd_digi = 1, # increment relative the first significant digit 123.45 -> 223.45
    abs_double = 2,   # increment by doubling the value  123.45 -> 246.9
    abs_01 = 3,       # increment by doubling the value  123.45 -> 246.9
    abs_1 = 4,        # increment by 1
    odd_1 = 5         # increment by 2 to the next odd value

class _SciLineEditQt(QtWidgets.QLineEdit):

    value_changed_event = Signal(float)

    def __init__(self, precision: int = 3, step_mode : StepMode = StepMode.rel_2nd_digi, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._unit_prefix_automode = sci_val.up.Prefix.auto_
        self._precision = precision
        self._precision_default = precision
        self._step_mode = step_mode
        self._step_delay_time = 800
        self._max_characters = 20
        self._block_value_change_signal = False
        self._sci_value = sci_val.SciVal()
        self._edit_finished_timer = QTimer() 
        self._edit_finished_timer.timeout.connect(self._value_changed_timeout)
        self.cursorPositionChanged.connect(self._handle_cursor_position_changed)

    # public interface ------------------------------------------

    def set_value(self, value: sci_val.SciVal | float, notify: bool = True):
        if isinstance(value, sci_val.SciVal):
            self._sci_value._value = value._value
            self._sci_value._unit = value._unit
            self._show_value() 
            if notify:
                self._value_changed()
        else:
            do_notify = notify and (value != self._sci_value.value())
            self._sci_value.set_value(value)
            self._show_value()   
            if do_notify:
                self._value_changed()

    def set_unit(self, unit: str, notify: bool = True):
        do_notify = notify and (unit != self._sci_value.unit())
        self._sci_value.set_unit(unit)
        self._show_value()     
        if do_notify:
            self._value_changed()

    def set_precision(self, precision: int, notify: bool = True):
        do_notify = notify and (precision != self._precision)
        self._precision = precision
        self._show_value()     
        if do_notify:
            self._value_changed()

    def set_prefix_id(self, prefix_id: sci_val.up.Prefix, notify: bool = True):
        do_notify = notify and (prefix_id != self._sci_value.prefix_id())
        self._sci_value.set_prefix_id(prefix_id)
        if do_notify:
            self._value_changed()

    def set_stepping_mode(self, mode: StepMode):
        self._step_mode = mode

    def set_allowed_prefix_ids(self, allowed_prefix_ids: list[up.Prefix]) :
        return self._sci_value.set_allowed_prefixes(allowed_prefix_ids)

    def set_value_min(self, value: float, notify: bool =True):
        oldval = self._sci_value.value()
        self._sci_value.set_value_min(value)
        do_notify = notify and (oldval != self._sci_value.value())
        if do_notify:
            self._value_changed()
              
    def set_value_max(self, value: float, notify: bool = True):
        oldval = self._sci_value.value()
        self._sci_value.set_value_max(value)
        do_notify = notify and (oldval != self._sci_value.value())
        if do_notify:
            self._value_changed()

    def sci_value(self) -> sci_val.SciVal:
        return self._sci_value

    def value(self) -> float:
        return self._sci_value.value()  

    def unit(self) -> str:
        return self._sci_value.unit()  

    def precision(self) -> int:
        return self._precision

    def prefix_id(self) -> sci_val.up.Prefix:
        return self._sci_value.prefix_id()

    def allowed_prefix_ids(self) -> list:
        return self._sci_value.allowed_prefixes()

    def value_min(self) -> float:
        return self._sci_value.value_min()

    def value_max(self) -> float:
        return self._sci_value.value_max()

    def stepping_mode(self) -> StepMode:
        return self._step_mode

    # internal functions --------------------------------------------    

    def focusInEvent(self, event: QtGui.QFocusEvent) -> None:
        """ overwrite handler for widget focus events"""
        super().focusInEvent(event)
        self._limit_cursor_to_last_digi()

    def focusOutEvent(self, event: QtGui.QFocusEvent) -> None:
        """  overwrite handler for widget focus events"""
        super().focusOutEvent(event)
        self._limit_cursor_to_last_digi()
        self._reformat(True)

    def mousePressEvent(self, arg__1: QtGui.QMouseEvent) -> None:
        """ overwrite handler for mouse events"""
        super().mousePressEvent(arg__1)
        if self._is_cursor_behind_last_digit():
            self._limit_cursor_to_last_digi()

    def mouseDoubleClickEvent(self, arg__1: QtGui.QMouseEvent) -> None:
        """ overwrite handler for mouse click events"""
        if self._is_cursor_behind_last_digit():
            start = self._get_last_digi_position()+1
            end = len(self.text())
            self.setCursorPosition(end)
            self.setSelection(start, end -start)
        else:
            super().mouseDoubleClickEvent(arg__1)
            
    def mouseMoveEvent(self, arg__1: QtGui.QMouseEvent) -> None:
        """ overwrite handler for move events"""
        super().mouseMoveEvent(arg__1)
        if self.hasSelectedText():
            last_digi = self._get_last_digi_position()
            start = self.selectionStart()
            end = self.selectionEnd()
            if start <= last_digi:
                if end > (last_digi+1):
                    end = last_digi+1
                    self.setSelection(start, end - start)
            elif start > last_digi:
                end = len(self.text())
                self.setSelection(start, end - start)
  
    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        """ overwrite handler for key events"""
        if self.isReadOnly():
            return
        shift = (event.modifiers() == Qt.ShiftModifier)
        ctrl = (event.modifiers() == Qt.ControlModifier)
        key = event.key()
        if (key == Qt.Key_Return) or (key == Qt.Key_Enter):
            super().keyPressEvent(event)
            self._reformat(True)
        elif (key==Qt.Key_Delete) or event.matches(QtGui.QKeySequence.Delete):
            if not(self._is_cursor_behind_last_digit()):
                super().keyPressEvent(event)
        elif (key == Qt.Key_Escape):
            self._show_value()
            self._reformat(True)
            self.clearFocus()
        elif (key == Qt.Key_Down) or (key == Qt.Key_PageDown):
            self._decrement()
            self._show_value()     
        elif (key == Qt.Key_Up) or (key == Qt.Key_PageUp):
            self._increment()
            self._show_value()   
        elif (key == Qt.Key_F):
            self._update_prefix_id(sci_val.up.Prefix.femto)
        elif (key == Qt.Key_P):
            self._update_prefix_id(sci_val.up.Prefix.pico)
        elif (key == Qt.Key_N):
            self._update_prefix_id(sci_val.up.Prefix.nano)
        elif (key == Qt.Key_M):
            self._update_prefix_id(sci_val.up.Prefix.milli)
        elif (key == Qt.Key_U):
            self._update_prefix_id(sci_val.up.Prefix.micro)
        elif (key == Qt.Key_B) or (key == Qt.Key_Space):
            self._update_prefix_id(sci_val.up.Prefix.base)
        elif (key == Qt.Key_K):
            self._update_prefix_id(sci_val.up.Prefix.kilo)
        elif (key == Qt.Key_M) and shift:
            self._update_prefix_id(sci_val.up.Prefix.mega)
        elif (key == Qt.Key_G):
            self._update_prefix_id(sci_val.up.Prefix.giga)
        elif (key == Qt.Key_T):
            self._update_prefix_id(sci_val.up.Prefix.tera)
        elif (key == Qt.Key_H) and ctrl:
            self._toggle_auto_prefix_mode()
        elif (key == Qt.Key_A) and ctrl:
            self._toggle_auto_prefix_mode()
        elif (key == Qt.Key_Backspace) :
            super().keyPressEvent(event)
        elif event.matches(QtGui.QKeySequence.SelectAll) or event.matches(QtGui.QKeySequence.Copy) or event.matches(QtGui.QKeySequence.Paste):
            super().keyPressEvent(event)
            self._handle_selection()
        elif (key == Qt.Key_Insert) or (key == Qt.Key_Insert) or (key == Qt.Key_End):
            super().keyPressEvent(event)
            self._handle_selection()
        elif (key == Qt.Key_Home):
            self.setCursorPosition(0)
            super().keyPressEvent(event)
        elif (key == Qt.Key_End):
            self.setCursorPosition(len(self.text()))
            self._limit_cursor_to_last_digi()
            super().keyPressEvent(event)
        elif (key == Qt.Key_Left):
            if self.text() == self.selectedText():
                self.setCursorPosition(0)
            super().keyPressEvent(event)
            self._limit_cursor_to_last_digi()
        elif (key == Qt.Key_Right):
            if self.text() == self.selectedText():
                self.setCursorPosition(len(self.text()))
                self._limit_cursor_to_last_digi()
            else:    
              super().keyPressEvent(event)
              self._limit_cursor_to_last_digi()
        elif (key == Qt.Key_0) or \
             (key == Qt.Key_1) or \
             (key == Qt.Key_2) or \
             (key == Qt.Key_3) or \
             (key == Qt.Key_4) or \
             (key == Qt.Key_5) or \
             (key == Qt.Key_6) or \
             (key == Qt.Key_7) or \
             (key == Qt.Key_8) or \
             (key == Qt.Key_9):
            if len(self.text()) < self._max_characters:
                super().keyPressEvent(event)
        elif (key == Qt.Key_Plus) or \
             (key == Qt.Key_Minus):
            if len(self.text()) < self._max_characters:
                super().keyPressEvent(event)
        elif (key == Qt.Key_Asterisk) or \
             (key == Qt.Key_Slash) or \
             (key == Qt.Key_AsciiCircum) or \
             (key == Qt.Key_E) or \
             (key == Qt.Key_Period):
            if len(self.text()) > self._max_characters:
                return
            if self.text() == self.selectedText():
                self.setCursorPosition(len(self.text()))
                self._limit_cursor_to_last_digi()
            super().keyPressEvent(event)
            self._handle_selection()
        else:
            if not (ctrl or shift):
                self._handle_selection()

    def wheelEvent(self, event: QtGui.QWheelEvent) -> None:
        """ overwrite handler for wheel event"""
        if self.isReadOnly():
            return
        has_focus = self.hasFocus()
        delta = event.angleDelta().y()
        if has_focus and (delta >0.0):
            self._increment()
            event.accept()
        elif has_focus and (delta < 0.0):
            self._decrement()
            event.accept()
        else:
            super().wheelEvent(event)    

    def _handle_cursor_position_changed(self):
        self._limit_cursor_to_last_digi()

    def _show_value(self):
        self.setText(self._sci_value.to_string_formatted(prefix_id=self._sci_value.prefix_id(), precision=self._precision))  

    def _calc_step_size(self, is_incrementing:bool):
        if self._step_mode == StepMode.rel_1st_digi:
            return self._calc_step_size_real_significant(0, is_incrementing)    
        elif self._step_mode == StepMode.rel_2nd_digi:
            return self._calc_step_size_real_significant(1, is_incrementing)    
        elif self._step_mode == StepMode.abs_double:
            return self._calc_step_size_double(is_incrementing)    
        elif self._step_mode == StepMode.abs_01:
            return self._calc_step_size_abs(0.1, is_incrementing)                
        elif self._step_mode == StepMode.abs_1:
            return self._calc_step_size_abs(1.0, is_incrementing)                
        elif self._step_mode == StepMode.odd_1:
            return self._calc_step_size_odd(is_incrementing)                            
        return self._calc_step_size_real_significant(1, is_incrementing)

    def _calc_step_size_real_significant(self, sig:int, is_inc:bool) -> float:
        current_val = self._sci_value.value()
        value_abs = abs(current_val) + sys.float_info.epsilon
        number_digits = math.floor(math.log10(value_abs))
        start_with_10 = (math.floor(value_abs / math.pow(10, number_digits-1)) == 10.0)
        dec_pos_num =  (not(is_inc) and current_val >= 0.0)        
        inc_neg_num =  (    is_inc  and current_val < 0.0)

        if  start_with_10 and (dec_pos_num or inc_neg_num):
            sig += 1

        second_significant = number_digits - sig
        step_size = math.pow(10, second_significant)

        if not self._sci_value._is_real:    
            step_size = math.ceil(step_size)
            step_size = min(max(1.0, math.ceil(step_size)), step_size)
        elif step_size == 0.0:
            step_size = up.prefix_id_to_absolute_value(self._sci_value._prefix_id) / math.pow(10, sig)    
        return step_size

    def _calc_step_size_abs(self, step:float, is_inc:bool) -> float:
        current_val = self._sci_value.value()
        if is_inc:
            new_value = current_val + step
        else:
            new_value = current_val - step

        if new_value == 0.0:
            return step + 0.01
        return step

    def _calc_step_size_odd(self, is_inc:bool) -> float:
        current_val = self._sci_value.value()
        step = 2
        if is_inc:
            new_value = current_val + step
        else:
            new_value = current_val - step
        if (new_value % 2) == 0:
            return step + 1
        return step    

    def _calc_step_size_double(self, is_inc:bool) -> float:
        current_val = self._sci_value.value()
        if is_inc:
            return current_val
        return current_val / 2.0    

    def _adapt_step_size(self, step_size:float) ->float:
        if (self._step_mode == StepMode.rel_1st_digi or self._step_mode == StepMode.rel_2nd_digi):
            expo = -1 * int(self._precision)
            min_step = math.pow(10,expo) * up.prefix_id_to_absolute_value(self._sci_value._prefix_id)
            if step_size <= min_step:
                return min_step
        return step_size    

    def _make_odd_if_step_odd1(self, val:float) -> float:
        must_be_odd = (self._step_mode == StepMode.odd_1) and not(self._sci_value._is_real)  
        if must_be_odd:
            is_even = ((val % 2) == 0)                 
            if is_even:
                return val -1

        return val
    def _update_prefix_id(self, new_prefix_id: sci_val.up.Prefix):
        cur_text = self.text() 

        # set cursor at the end of the number
        if self._is_cursor_behind_last_digit():
            display_prefix = new_prefix_id
        else:
            display_prefix = sci_val.up.Prefix.auto_

        self._limit_cursor_to_last_digi()
        cur_pos = self.cursorPosition()     
        
        # add to number ne prefix
        new_text = cur_text[:cur_pos]
        new_text = new_text + sci_val.up.prefix_id_to_string(new_prefix_id)+self.unit()
        res = sci_val.convert.to_value(new_text,self.unit())
        if res.success:
            self._sci_value.set_value(res.value)

        self._sci_value.set_prefix_id(display_prefix)

        self._value_changing()
        self._presentaton_changed()
        self._reposition_icons()   

    def _is_auto_mode(self) -> bool:
        return (self._sci_value.prefix_id() == sci_val.up.Prefix.auto_)

    def _toggle_auto_prefix_mode(self):
        if self._is_auto_mode():
            self._sci_value.set_prefix_id(self._unit_prefix_automode)
            self._highlight_unit_and_prefix()
        else:
            self._sci_value.set_prefix_id(sci_val.up.Prefix.auto_)
            self._set_default_text_format()
            self._presentaton_changed()

    def _increment(self):
        self._reformat(False)
        self._prepare_step_mode()
        self._value_changing(self._step_delay_time)
        step_size = self._calc_step_size(is_incrementing=True)
        step_size = self._adapt_step_size(step_size)
        self.set_value(self._sci_value.value() + step_size)
        self._presentaton_changed()

    def _decrement(self):
        self._reformat(False)
        self._prepare_step_mode()
        self._value_changing(self._step_delay_time)
        step_size = self._calc_step_size(is_incrementing=False)
        step_size = self._adapt_step_size(step_size)
        self.set_value(self._sci_value.value() - step_size)
        self._presentaton_changed()

    def _reformat(self, notify: bool):
        cur_text = self.text()
        has_val_changed = self._sci_value.from_string(cur_text)
        if has_val_changed and notify:
            self._edit_finished_timer.stop()
            self._presentaton_changed()
            self._value_changed()
        else:
            self._presentaton_changed()

    def _value_changing(self, timeout=0):
        self._edit_finished_timer.stop()
        self._edit_finished_timer.start(timeout)

    def _value_changed_timeout(self):
        self._edit_finished_timer.stop()
        cur_text = self.text()
        if not(cur_text=="") and (cur_text[0]!=" "):
            self._reformat(False)
            self._value_changed()

    def _value_changed(self):
        if not(self._block_value_change_signal):
            self.value_changed_event.emit(self._sci_value.value())    

    def _presentaton_changed(self):
        self._show_value()
        self._limit_cursor_to_last_digi()
        if self._is_auto_mode():
            t = sci_val.convert.to_value(self.text(), self._sci_value.unit, self._sci_value.prefix_id())
            if t.success:
                self._unit_prefix_automode = t.prefix_id
        else:
            self._highlight_unit_and_prefix()

    def _reposition_icons(self):
        pass

    def _set_default_text_format(self):
        pass

    def _prepare_step_mode(self):
        pass
    
    def _handle_selection(self):
        txt = self.text()
        prefix_id = self._sci_value.prefix_id()
        if self._is_auto_mode():
            prefix_str = sci_val.up.prefix_id_to_string(self._unit_prefix_automode)
        else:
            prefix_str = sci_val.up.prefix_id_to_string(prefix_id)
        expected_end = prefix_str + self._sci_value.unit()

        if (len(txt) < len(expected_end)):
            txt = txt + expected_end 
            self.setText(txt)
            self._limit_cursor_to_last_digi()
        elif not(txt[-len(expected_end):]==expected_end) and not(txt[-len(self._sci_value.unit())]==self._sci_value.unit()):
            new_txt = txt + expected_end
            self.setText(new_txt)
            self._limit_cursor_to_last_digi()

        if not(self._is_auto_mode()):
            self._highlight_unit_and_prefix()

    def _is_cursor_behind_last_digit(self):
        cur_pos = self.cursorPosition()
        last_digi_pos = self._get_last_digi_position()
        return (cur_pos > last_digi_pos)

    def _limit_cursor_to_last_digi(self):
        cur_pos = self.cursorPosition()
        last_digi_pos = self._get_last_digi_position()

        if cur_pos > last_digi_pos:
            self.setCursorPosition(last_digi_pos+1)     

    def _get_last_digi_position(self) ->int:
        cur_str = self.text()
        last_digi_pos = -1
        for index, c in enumerate(cur_str):
            if (c >= '0' and c <= '9') or (c=='.') or (c==',') or (c=='-'):
                last_digi_pos = index
            else:
                break
        return last_digi_pos

    def _highlight_unit_and_prefix(self):
        prefix_str =  sci_val.up.prefix_id_to_string(self._sci_value.prefix_id()) + self._sci_value.unit()
        prefix_str_len = len(prefix_str)
        self._set_italic_range(len(self.text())-prefix_str_len,prefix_str_len)

    def _set_italic_range(self, start:int, length:int):
        custom_format = QtGui.QTextCharFormat()
        custom_format.setProperty(QtGui.QTextCharFormat.FontItalic,True)
        range = QtGui.QTextLayout.FormatRange()
        range.start = start
        range.length = length
        range.format = custom_format
        self._format_range(range)
        self.update()

    def _format_range(self, fr:QtGui.QTextLayout.FormatRange):
        start = fr.start - self.cursorPosition()
        length = fr.length
        # TODO: send text format to edit: 
        # see lineedit_qt.cpp:226 lineedit_qt::format_range(...)


class NSFSciEdit(QtWidgets.QWidget):
    """ Custom Qt Widget to show scientific numbers in a edit with a descriptive label. """
    value_changed_event = Signal(float)

    def __init__(self, label_str = "", layout:WidgetLayout = WidgetLayout.Vertical, text_align_edit:Qt.AlignmentFlag=Qt.AlignmentFlag.AlignLeft, text_align_label:Qt.AlignmentFlag=Qt.AlignmentFlag.AlignLeft, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._setup_widgets(label_str, layout, text_align_edit, text_align_label)
        self._edit.value_changed_event.connect(self._on_value_changed_from_edit)
        self.set_prefix_id(sci_val.up.Prefix.auto_)
        self.set_precision(3)
 
    def set_value(self, value: sci_val.SciVal | float, notify: bool = True):
        self._edit.set_value(value, notify)
       
    def set_unit(self, unit_str: str, notify: bool = True):
       self._edit.set_unit(unit_str,notify)
   
    def set_label(self, label: str):
       self._label.setText(label) 

    def set_precision(self, precision: int, notify: bool = True):
        self._edit.set_precision(precision,notify)

    def set_prefix_id(self, prefix_id: sci_val.up.Prefix, notify: bool = True):
        self._edit.set_prefix_id(prefix_id,notify)

    def set_allowed_prefix_ids(self, allowed_prefix_ids: list[sci_val.up.Prefix]) :
        return self._edit.set_allowed_prefix_ids(allowed_prefix_ids)

    def set_read_only(self, set_read_only: bool):
        self._edit.setReadOnly(set_read_only)
        self._edit.setDisabled(set_read_only)

    def set_value_min(self, value: float, notify: bool = True):
       self._edit.set_value_min(value, notify)
               
    def set_value_max(self, value: float, notify: bool = True):
       self._edit.set_value_max(value, notify)
               
    def set_value_min_max(self, value_min: float, value_max: float, notify: bool = True):
       self._edit.set_value_min(value_min, notify)
       self._edit.set_value_max(value_max, notify)
    
    def read_only(self) -> bool:
        return self._edit.isReadOnly()

    def label(self) -> str:
        return self._label.text()

    def value(self) -> float:
        return self._edit.value()  

    def sci_value(self) -> sci_val.SciVal:
        return self._edit.sci_value()  

    def unit(self) -> str:
        return self._edit.unit()  

    def precision(self) -> int:
        return self._edit.precision()

    def prefix_id(self) -> sci_val.up.Prefix:
        return self._edit.prefix_id()

    def allowed_prefix_ids(self) -> list[sci_val.up.Prefix]:
        return self._edit.allowed_prefix_ids()

    def value_min(self) -> float:
        return self._edit.value_min()

    def value_max(self) -> float:
        return self._edit.value_max()

    # internal ----------------------------------------------------
    
    def _setup_widgets(self, label_str: str, layout:WidgetLayout, text_align_edit:Qt.AlignmentFlag.AlignLeft, text_align_label:Qt.AlignmentFlag):
        widget_layout = QtWidgets.QGridLayout()
        widget_layout.setContentsMargins(*LabelWidgetSize.content_margins)
        self._edit = _SciLineEditQt()
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

    def _on_value_changed_from_edit(self, newvalue: float):
        self.value_changed_event.emit(newvalue)

