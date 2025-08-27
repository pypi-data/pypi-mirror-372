""" This is the screen of the module
Copyright Nanosurf AG 2021
License - MIT
"""

import pathlib
from PySide6 import QtWidgets
from PySide6.QtCore import Qt

import nanosurf as nsf
from vmf_control.auto_image_module import AutoImageModule 

class ResultTableID(nsf.gui.nsf_tables.TableEntryIDs):
    """ identifier id are used in a nsf_table widget"""
    Items = 0
    last_data = 1
    mean_value = 2

ComboGapConfig = [
    nsf.gui.NSFComboEntry(0,"Gap 6mm"),
    nsf.gui.NSFComboEntry(1,'Gap 3mm'),
]

""" some useful list of allowed prefixes used by nsf_sci_edit widgets"""
allowed_count_units = [nsf.sci_val.up.Prefix.base]
allowed_time_units = [nsf.sci_val.up.Prefix.base, nsf.sci_val.up.Prefix.milli]
allowed_meter_units = [nsf.sci_val.up.Prefix.milli, nsf.sci_val.up.Prefix.micro, nsf.sci_val.up.Prefix.nano]
allowed_tesla_units = [nsf.sci_val.up.Prefix.milli, nsf.sci_val.up.Prefix.micro]

class AutoImageScreen(nsf.frameworks.qt_app.ModuleScreen):
    def __init__(self, screen_name: str = None, **kwargs):
        super().__init__(screen_name, **kwargs)
        self.module:AutoImageModule # give pylance a type hint

    def do_setup_screen(self, module: AutoImageModule):
        """ create here your gui with all controls and their layout"""
        self.module = module

        # left layout - main controls ------------------------------------------------------------
        self.scival_cur_h_field = nsf.gui.NSFSciEdit("Current H-Field")
        self.scival_cur_h_field.set_allowed_prefix_ids(allowed_tesla_units)
        self.scival_cur_h_field.set_prefix_id(nsf.sci_val.up.Prefix.milli)
        self.scival_cur_h_field.set_precision(2)
        self.scival_cur_h_field.set_unit("T")
        self.scival_cur_h_field.setEnabled(False)

        self.scival_start_h_field = nsf.gui.NSFSciEdit("Start H-Field")
        self.scival_start_h_field.set_allowed_prefix_ids(allowed_tesla_units)
        self.scival_start_h_field.set_prefix_id(nsf.sci_val.up.Prefix.milli)
        self.scival_start_h_field.set_precision(2)
        self.scival_start_h_field.set_unit("T")
        self.scival_start_h_field.setEnabled(False)

        self.scival_stop_h_field = nsf.gui.NSFSciEdit("End H-Field")
        self.scival_stop_h_field.set_allowed_prefix_ids(allowed_tesla_units)
        self.scival_stop_h_field.set_prefix_id(nsf.sci_val.up.Prefix.milli)
        self.scival_stop_h_field.set_precision(2)
        self.scival_stop_h_field.set_unit("T")
        self.scival_stop_h_field.set_value_min_max(-1.0, 1.0)

        self.scival_steps = nsf.gui.NSFSciEdit("Number of steps")
        self.scival_steps.set_allowed_prefix_ids(allowed_count_units)
        self.scival_steps.set_prefix_id(nsf.sci_val.up.Prefix.base)
        self.scival_steps.set_precision(0)
        self.scival_steps.set_unit("")
        self.scival_steps.set_value_min_max(2,1000)

        self.scival_frames = nsf.gui.NSFSciEdit("Images per steps")
        self.scival_frames.set_allowed_prefix_ids(allowed_count_units)
        self.scival_frames.set_prefix_id(nsf.sci_val.up.Prefix.base)
        self.scival_frames.set_precision(0)
        self.scival_frames.set_unit("")
        self.scival_frames.set_value_min_max(1,100)

        self.edit_file_mask = nsf.gui.NSFEdit("Filename mask")
        self.edit_file_dir = nsf.gui.NSFEdit("Target directory")
        self.button_dir_browse = nsf.gui.NSFPushButton("Browse dir")

        self.button_start_stop_imaging = nsf.gui.NSFPushButton("")

        self.layout_left = QtWidgets.QVBoxLayout()
        self.layout_position = QtWidgets.QHBoxLayout()
        self.layout_position.addWidget(self.scival_cur_h_field)
        self.layout_position.addStretch()
        self.layout_position.addStretch()
        self.layout_left.addLayout(self.layout_position)
        self.layout_left.addSpacing(10)
        self.layout_left.addWidget(nsf.gui.NSFHLine())
        self.layout_left.addSpacing(10)
        self.layout_auto = QtWidgets.QHBoxLayout()
        self.layout_auto.addWidget(self.scival_start_h_field)
        self.layout_auto.addWidget(self.scival_stop_h_field)
        self.layout_auto.addWidget(self.scival_steps)
        self.layout_auto.addWidget(self.scival_frames)
        self.layout_left.addLayout(self.layout_auto)
        self.layout_save = QtWidgets.QGridLayout()
        self.layout_save.addWidget(self.edit_file_mask,0,0)
        self.layout_save.addWidget(self.edit_file_dir, 0,1)
        self.layout_save.addWidget(self.button_dir_browse,0,2,alignment=Qt.AlignmentFlag.AlignBottom)
        self.layout_left.addLayout(self.layout_save)
        self.layout_left.addSpacing(10)
        self.layout_left.addWidget(nsf.gui.NSFHLine())
        self.layout_left.addSpacing(10)
        self.layout_left.addWidget(self.button_start_stop_imaging)
        self.layout_left.addStretch()

        # set GUI controls
        self.screen_layout = QtWidgets.QHBoxLayout()

        self.screen_layout.addLayout(self.layout_left, 0)

        self.setLayout(self.screen_layout)

        self.bind_gui_elements()
        self.enter_gui_state_idle()
        self.update_min_max_h_field()

    def bind_gui_elements(self):
        nsf.gui.connect_to_property(self.scival_start_h_field, self.module.settings.auto_field_start)
        nsf.gui.connect_to_property(self.scival_stop_h_field, self.module.settings.auto_field_stop)
        nsf.gui.connect_to_property(self.scival_frames, self.module.settings.auto_field_frame_rep)
        nsf.gui.connect_to_property(self.scival_steps, self.module.settings.auto_field_steps)
        nsf.gui.connect_to_property(self.edit_file_dir,self.module.settings.save_to_path)
        nsf.gui.connect_to_property(self.edit_file_mask,self.module.settings.data_file_mask)
        self.button_dir_browse.clicked_event.connect(self.on_button_browse_clicked)    
        self.button_start_stop_imaging.clicked_event.connect(self.on_button_start_stop_clicked)    

        self.module.sig_imaging_started.connect(lambda : self.enter_gui_state_active(button_to_keep_active=self.button_start_stop_imaging))
        self.module.sig_imaging_finished.connect(self.enter_gui_state_idle)
        self.module.sig_imaging_start_requested.connect(self.enter_gui_state_wait)
        self.module.sig_imaging_stop_requested.connect(self.enter_gui_state_wait)
        self.module.vmf_module.sig_reference_move_started.connect(self.enter_gui_state_unref)
        self.module.vmf_module.sig_reference_move_ended.connect(self.enter_gui_state_idle)
        self.module.vmf_module.sig_reference_move_ended.connect(self.update_min_max_h_field)
        self.module.vmf_module.sig_h_field_available.connect(self._on_new_h_field_available)

    def on_button_start_stop_clicked(self):
        if self.module.is_measuring():
            self.module.stop_auto_imaging()
        else:
            self.module.start_auto_imaging()

    def enter_gui_state_wait(self):
        self.set_parameter_widget_enable_state(enabled=False)
        self.start_stop_button_state(wait=True)

    def enter_gui_state_active(self, button_to_keep_active=None):
        self.set_parameter_widget_enable_state(enabled=False, active_button=button_to_keep_active)
        if button_to_keep_active is self.button_start_stop_imaging:
            self.start_stop_button_state(wait=False, stop_state=self.module.is_measuring())
    
    def enter_gui_state_unref(self):
        self.set_parameter_widget_enable_state(enabled=False)
        self.start_stop_button_state(wait=True, stop_state=self.module.is_measuring())
    
    def enter_gui_state_idle(self):
        self.set_parameter_widget_enable_state(enabled=True)
        self.start_stop_button_state(wait=False, stop_state=self.module.is_measuring())

    def set_parameter_widget_enable_state(self, enabled: bool = True, active_button=None):
        self.scival_start_h_field.setEnabled(enabled)
        self.scival_stop_h_field.setEnabled(enabled)
        self.scival_steps.setEnabled(enabled)
        self.scival_frames.setEnabled(enabled)
        self.button_start_stop_imaging.setEnabled(enabled and (active_button is self.button_start_stop_imaging))

    def start_stop_button_state(self, wait: bool = False, stop_state: bool = False):
        if wait:
            self.button_start_stop_imaging.setEnabled(False)
            self.button_start_stop_imaging.set_label("Wait...")
        else:
            self.button_start_stop_imaging.setEnabled(True)
            self.button_start_stop_imaging.set_label("Stop" if stop_state else "Start Imaging")

    def update_min_max_h_field(self):
        if self.module.vmf_module.is_referenced():
            h_min, h_max = self.module.vmf_module.get_min_max_field()
            self.module.logger.info(f"New min_h_field = {h_min}, h_max_field={h_max}")
            self.scival_start_h_field.set_value_min(h_min)
            self.scival_start_h_field.set_value_max(h_max)
            self.scival_stop_h_field.set_value_min(h_min)
            self.scival_stop_h_field.set_value_max(h_max)
        else:
            h_min, h_max = (0.0,0.0)
            self.module.logger.info("Not referenced.")
            self.scival_start_h_field.set_value_min(h_min)
            self.scival_start_h_field.set_value_max(h_max)
            self.scival_stop_h_field.set_value_min(h_min)
            self.scival_stop_h_field.set_value_max(h_max)

    def _on_new_h_field_available(self, new_val:float):
        self.scival_cur_h_field.set_value(new_val)

    def on_button_browse_clicked(self):
        selected_folder = QtWidgets.QFileDialog.getExistingDirectory(self, 'Open folder', 'c:\\')
        if selected_folder != '':
            self.module.settings.save_to_path.value = pathlib.Path(selected_folder)    