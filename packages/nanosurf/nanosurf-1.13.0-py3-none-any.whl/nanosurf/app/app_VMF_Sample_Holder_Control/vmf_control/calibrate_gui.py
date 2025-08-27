""" This is the screen of the module
Copyright Nanosurf AG 2021
License - MIT
"""

import pathlib
from PySide6 import QtWidgets


import nanosurf as nsf
from vmf_control import calibrate_module

class ResultTableID(nsf.gui.nsf_tables.TableEntryIDs):
    """ identifier id are used in a nsf_table widget"""
    Items = 0
    last_data = 1
    mean_value = 2

ComboGapConfig = [
    nsf.gui.NSFComboEntry(0,"Gap 6mm"),
    nsf.gui.NSFComboEntry(1,'Gap 3mm'),
]


class CalibResultTableID(nsf.gui.TableEntryIDs):
    """ identifier id are used in a nsf_table widget"""
    Name = 0
    Offset = 1
    Linear = 2
    Square = 3

""" some useful list of allowed prefixes used by nsf_sci_edit widgets"""
allowed_count_units = [nsf.sci_val.up.Prefix.base]
allowed_time_units = [nsf.sci_val.up.Prefix.base, nsf.sci_val.up.Prefix.milli]
allowed_meter_units = [nsf.sci_val.up.Prefix.milli, nsf.sci_val.up.Prefix.micro, nsf.sci_val.up.Prefix.nano]
allowed_tesla_units = [nsf.sci_val.up.Prefix.milli, nsf.sci_val.up.Prefix.micro]

class CalibrateScreen(nsf.frameworks.qt_app.ModuleScreen):
    def __init__(self, screen_name: str = None, **kwargs):
        super().__init__(screen_name, **kwargs)
        self.module:calibrate_module.CalibrateModule # give pylance a type hint

    def do_setup_screen(self, module: 'calibrate_module.CalibrateModule'):
        """ create here your gui with all controls and their layout"""
        self.module = module

        # left layout - main controls ------------------------------------------------------------
        self.combo_holder_setup = nsf.gui.NSFComboBox(ComboGapConfig,"Sample Holder setup")
        self.tableResults = nsf.gui.NSFNameValueTable(CalibResultTableID)
        self.tableResults.define_entry(CalibResultTableID.Name,"Name")
        self.tableResults.define_entry(CalibResultTableID.Offset,"Offset")
        self.tableResults.define_entry(CalibResultTableID.Linear,"Gain")
        self.tableResults.define_entry(CalibResultTableID.Square,"Square")

        self.scival_cur_h_field = nsf.gui.NSFSciEdit("Current H-Field")
        self.scival_cur_h_field.set_allowed_prefix_ids(allowed_tesla_units)
        self.scival_cur_h_field.set_prefix_id(nsf.sci_val.up.Prefix.milli)
        self.scival_cur_h_field.set_precision(3)
        self.scival_cur_h_field.set_unit("T")
        self.scival_cur_h_field.setEnabled(False)

        self.scival_steps = nsf.gui.NSFSciEdit("Calibration steps")
        self.scival_steps.set_allowed_prefix_ids(allowed_count_units)
        self.scival_steps.set_prefix_id(nsf.sci_val.up.Prefix.base)
        self.scival_steps.set_precision(0)
        self.scival_steps.set_unit("")
        self.scival_steps.set_value_min_max(2,1000)

        self.edit_file_mask = nsf.gui.NSFEdit("Filename mask")
        self.edit_file_dir = nsf.gui.NSFEdit("Target directory")
        self.button_dir_browse = nsf.gui.NSFPushButton("Browse dir")
        self.button_start_stop_calibration = nsf.gui.NSFPushButton("")
        self.button_save_calibration = nsf.gui.NSFPushButton("Store calibration in sample holder")
        self.button_save_calibration_to_file = nsf.gui.NSFPushButton("Save calibration to file")

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
        self.layout_auto.addWidget(self.combo_holder_setup)
        self.layout_auto.addWidget(self.scival_steps)
        self.layout_auto.addStretch()
        self.layout_auto.addStretch()        
        self.layout_left.addLayout(self.layout_auto)
        self.layout_left.addSpacing(10)
        self.layout_left.addWidget(nsf.gui.NSFHLine())
        self.layout_left.addSpacing(10)
        self.layout_left.addWidget(self.button_start_stop_calibration)
        self.layout_left.addWidget(self.tableResults)
        self.layout_load_save = QtWidgets.QGridLayout()
        self.layout_load_save.addWidget(self.button_save_calibration,1,1)
        self.layout_load_save.addWidget(QtWidgets.QLabel(),1,2)
        self.layout_load_save.addWidget(self.button_save_calibration_to_file,1,3)
        self.layout_left.addLayout(self.layout_load_save)
        self.layout_left.addStretch()

        # set GUI controls
        self.screen_layout = QtWidgets.QHBoxLayout()

        self.screen_layout.addLayout(self.layout_left, 0)

        self.setLayout(self.screen_layout)

        self.bind_gui_elements()
        self.enter_gui_state_idle()
        self.update_sample_configuration()

    def bind_gui_elements(self):
        nsf.gui.connect_to_property(self.combo_holder_setup, self.module.settings.calibrate_configuration)        
        nsf.gui.connect_to_property(self.scival_steps, self.module.settings.cal_steps)
        nsf.gui.connect_to_property(self.edit_file_dir,self.module.settings.save_to_path)
        nsf.gui.connect_to_property(self.edit_file_mask,self.module.settings.data_file_mask)
        self.button_dir_browse.clicked_event.connect(self.on_button_browse_clicked)    
        self.button_start_stop_calibration.clicked_event.connect(self.on_button_start_stop_clicked)    
        self.button_save_calibration.clicked_event.connect(self.on_button_save_calibration_clicked)    
        self.button_save_calibration_to_file.clicked_event.connect(self.on_button_save_calibration_to_file_clicked)    

        self.module.sig_calibration_started.connect(lambda : self.enter_gui_state_active(button_to_keep_active=self.button_start_stop_calibration))
        self.module.sig_calibration_finished.connect(self.enter_gui_state_idle)
        self.module.sig_calibration_finished.connect(self.update_calibration_value)
        self.module.sig_calibrate_start_requested.connect(self.enter_gui_state_wait)
        self.module.sig_calibrate_stop_requested.connect(self.enter_gui_state_wait)
        self.module.vmf_module.sig_reference_move_started.connect(self.enter_gui_state_unref)
        self.module.vmf_module.sig_reference_move_ended.connect(self.enter_gui_state_idle)
        self.module.vmf_module.sig_h_field_available.connect(self.on_new_h_field_available)
        self.module.vmf_module.sig_connecting_done.connect(self._on_connecting_done)
        self.module.vmf_module.sig_save_calibration_started.connect(self.enter_gui_state_wait)
        self.module.vmf_module.sig_save_calibration_ended.connect(self.enter_gui_state_idle)
        self.module.settings.calibrate_configuration.sig_value_changed.connect(self.update_calibration_value)

    def _on_connecting_done(self):
        if self.module.vmf_module.is_vmf_ready():
            self.update_sample_configuration()

    def on_button_start_stop_clicked(self):
        if self.module.is_measuring():
            self.module.stop_calibrating()
        else:
            self.module.start_calibrating()

    def enter_gui_state_wait(self):
        self.set_parameter_widget_enable_state(enabled=False)
        self.start_stop_button_state(wait=True)

    def enter_gui_state_active(self, button_to_keep_active=None):
        self.set_parameter_widget_enable_state(enabled=False, active_button=button_to_keep_active)
        if button_to_keep_active is self.button_start_stop_calibration:
            self.start_stop_button_state(wait=False, stop_state=self.module.is_measuring())
    
    def enter_gui_state_unref(self):
        self.set_parameter_widget_enable_state(enabled=False)
        self.start_stop_button_state(wait=True, stop_state=self.module.is_measuring())
    
    def enter_gui_state_idle(self):
        self.set_parameter_widget_enable_state(enabled=True)
        self.start_stop_button_state(wait=False, stop_state=self.module.is_measuring())

    def set_parameter_widget_enable_state(self, enabled: bool = True, active_button=None):
        self.scival_steps.setEnabled(enabled)
        self.combo_holder_setup.setEnabled(enabled)
        self.button_start_stop_calibration.setEnabled(enabled and (active_button is self.button_start_stop_calibration))
        self.button_save_calibration.setEnabled(enabled)

    def start_stop_button_state(self, wait: bool = False, stop_state: bool = False):
        if wait:
            self.button_start_stop_calibration.setEnabled(False)
            self.button_start_stop_calibration.set_label("Wait...")
        else:
            self.button_start_stop_calibration.setEnabled(True)
            self.button_start_stop_calibration.set_label("Stop" if stop_state else "Start Calibrate")
            self.scival_cur_h_field.set_unit("V" if stop_state else "T")

    def on_new_h_field_available(self, new_val:float):
        self.scival_cur_h_field.set_value(new_val)

    def on_button_browse_clicked(self):
        selected_folder = QtWidgets.QFileDialog.getExistingDirectory(self, 'Open folder', 'c:\\')
        if selected_folder != '':
            self.module.settings.save_to_path.value = pathlib.Path(selected_folder)    

    def on_button_save_calibration_clicked(self):
        self.module.vmf_module.start_store_calibration_to_sample_holder()

    def on_button_save_calibration_to_file_clicked(self):
        self.module.vmf_module.start_save_calibration_to_file()

    def update_sample_configuration(self):
        config_list = self.module.vmf_module.get_sample_holder_configurations()
        new_combo_list = [ nsf.gui.NSFComboEntry(i,name) for i, name in enumerate(config_list)]
        self.combo_holder_setup.define_entries(new_combo_list)
        self.combo_holder_setup.set_value(self.module.settings.calibrate_configuration.value)
        self.update_calibration_value()

    def update_calibration_value(self):
        cur_index = self.module.settings.calibrate_configuration.value
        config = self.module.vmf_module.worker_thread.vmf_controller.configurations[cur_index]
        self.tableResults.set_value(CalibResultTableID.Name, config.name)
        self.tableResults.set_value(CalibResultTableID.Offset, config.cal_values[0])
        self.tableResults.set_value(CalibResultTableID.Linear, config.cal_values[1])
        self.tableResults.set_value(CalibResultTableID.Square, config.cal_values[2])
