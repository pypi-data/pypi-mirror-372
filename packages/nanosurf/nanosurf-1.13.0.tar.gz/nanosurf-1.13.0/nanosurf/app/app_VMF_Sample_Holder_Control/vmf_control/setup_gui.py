""" This is the screen of the module
Copyright Nanosurf AG 2021
License - MIT
"""


from PySide6 import QtWidgets

import nanosurf as nsf
from vmf_control import setup_module


""" some useful list of allowed prefixes used by nsf_sci_edit widgets"""
allowed_count_units = [nsf.sci_val.up.Prefix.base]
allowed_time_units = [nsf.sci_val.up.Prefix.base, nsf.sci_val.up.Prefix.milli]
allowed_meter_units = [nsf.sci_val.up.Prefix.milli, nsf.sci_val.up.Prefix.micro, nsf.sci_val.up.Prefix.nano]
allowed_tesla_units = [nsf.sci_val.up.Prefix.milli, nsf.sci_val.up.Prefix.micro]

class SetupScreen(nsf.frameworks.qt_app.ModuleScreen):
    def __init__(self, screen_name: str = None, **kwargs):
        super().__init__(screen_name, **kwargs)
        self.module:setup_module.SetupModule # give pylance a type hint

    def do_setup_screen(self, module: 'setup_module.SetupModule'):
        """ create here your gui with all controls and their layout"""
        self.module = module

        # left layout - main controls ------------------------------------------------------------

        self.edit_controller_sn = nsf.gui.NSFEdit("VMF-Controller S/N")
        self.edit_sample_holder_sn = nsf.gui.NSFEdit("VMF-Sample-Holder S/N")
        self.button_init_ctrl_setup = nsf.gui.NSFPushButton("Write default settings to Controller EEPROM")
        self.button_init_holder_setup = nsf.gui.NSFPushButton("Write default settings to Controller EEPROM")

        self.button_load_calibration = nsf.gui.NSFPushButton("Load from EEPROM")
        self.button_save_calibration = nsf.gui.NSFPushButton("Store to EEPROM")
        self.label_holder_settings = nsf.gui.NSFEdit("Sample-Holder calibration")
        self.label_holder_settings.set_read_only()
        self.label_holder_cal_0 = nsf.gui.NSFEdit("Calibration cal_0")
        self.label_holder_cal_0.set_read_only()
        self.label_holder_cal_1 = nsf.gui.NSFEdit("Calibration cal_1")
        self.label_holder_cal_1.set_read_only()
        self.label_holder_cal_2 = nsf.gui.NSFEdit("Calibration cal_2")
        self.label_holder_cal_2.set_read_only()
        self.button_load_cal_from_file = nsf.gui.NSFPushButton("Load Calibration from File")
        self.button_save_cal_to_file = nsf.gui.NSFPushButton("Save Calibration to File")

        self.layout_left = QtWidgets.QVBoxLayout()
        self.layout_position = QtWidgets.QHBoxLayout()
        self.layout_position.addWidget(self.edit_controller_sn)
        self.layout_position.addWidget(self.button_init_ctrl_setup)
        self.layout_left.addLayout(self.layout_position)
        self.layout_left.addSpacing(10)
        self.layout_left.addWidget(nsf.gui.NSFHLine())
        self.layout_left.addSpacing(10)
        self.layout_auto = QtWidgets.QHBoxLayout()
        self.layout_auto.addWidget(self.edit_sample_holder_sn)
        self.layout_auto.addWidget(self.button_init_holder_setup)
        self.layout_left.addLayout(self.layout_auto)
        self.layout_left.addSpacing(10)
        self.layout_left.addWidget(nsf.gui.NSFHLine())
        self.layout_left.addSpacing(10)
        self.layout_left.addWidget(self.label_holder_settings)
        self.layout_left.addWidget(self.label_holder_cal_0)
        self.layout_left.addWidget(self.label_holder_cal_1)
        self.layout_left.addWidget(self.label_holder_cal_2)
        self.layout_load_save = QtWidgets.QGridLayout()
        self.layout_load_save.addWidget(self.button_load_calibration,1,1)
        self.layout_load_save.addWidget(self.button_save_calibration,2,1)
        self.layout_load_save.addWidget(QtWidgets.QLabel(),1,2)
        self.layout_load_save.addWidget(QtWidgets.QLabel(),2,2)
        self.layout_load_save.addWidget(self.button_load_cal_from_file,1,3)
        self.layout_load_save.addWidget(self.button_save_cal_to_file,2,3)
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
        nsf.gui.connect_to_property(self.edit_controller_sn, self.module.settings._controller_sn)        
        nsf.gui.connect_to_property(self.edit_sample_holder_sn, self.module.settings._sample_holder_sn)        
        self.button_init_ctrl_setup.clicked_event.connect(self.on_button_init_controller_clicked)    
        self.button_init_holder_setup.clicked_event.connect(self.on_button_init_sample_holder_clicked)    
        self.button_load_calibration.clicked_event.connect(self.on_button_load_calibration_clicked)    
        self.button_save_calibration.clicked_event.connect(self.on_button_save_calibration_clicked)    
        self.button_load_cal_from_file.clicked_event.connect(self.on_button_load_calibration_from_file_clicked)    
        self.button_save_cal_to_file.clicked_event.connect(self.on_button_save_calibration_to_file_clicked)    

        self.module.vmf_module.sig_connecting_done.connect(self._on_connecting_done)   
        self.module.vmf_module.sig_init_controller_started.connect(self.enter_gui_state_wait)
        self.module.vmf_module.sig_init_controller_ended.connect(self.enter_gui_state_idle)
        self.module.vmf_module.sig_init_sample_holder_started.connect(self.enter_gui_state_wait)
        self.module.vmf_module.sig_init_sample_holder_ended.connect(self.enter_gui_state_idle)
        self.module.vmf_module.sig_load_calibration_started.connect(self.enter_gui_state_wait)
        self.module.vmf_module.sig_load_calibration_ended.connect(self.enter_gui_state_idle)
        self.module.vmf_module.sig_load_calibration_ended.connect(self.update_sample_configuration)
        self.module.vmf_module.sig_save_calibration_started.connect(self.enter_gui_state_wait)
        self.module.vmf_module.sig_save_calibration_ended.connect(self.enter_gui_state_idle)

        self.module.sig_update_device_infos.connect(self.update_sample_configuration)

    def _on_connecting_done(self):
        self.update_sample_configuration()

    def enter_gui_state_wait(self):
        self.set_parameter_widget_enable_state(enabled=False)
        self.start_stop_button_state(wait=True)

    def enter_gui_state_active(self, button_to_keep_active=None):
        self.set_parameter_widget_enable_state(enabled=False, active_button=button_to_keep_active)
        self.start_stop_button_state(wait=False, stop_state=False)
    
    def enter_gui_state_unref(self):
        self.set_parameter_widget_enable_state(enabled=False)
        self.start_stop_button_state(wait=True, stop_state=False)
    
    def enter_gui_state_idle(self):
        self.set_parameter_widget_enable_state(enabled=True)
        self.start_stop_button_state(wait=False, stop_state=False)

    def set_parameter_widget_enable_state(self, enabled: bool = True, active_button=None):
        self.label_holder_settings.setEnabled(enabled)


    def start_stop_button_state(self, wait: bool = False, stop_state: bool = False):
        self.button_load_cal_from_file.setEnabled(not wait)
        self.button_save_cal_to_file.setEnabled(not wait)
        self.button_load_calibration.setEnabled(not wait)
        self.button_save_calibration.setEnabled(not wait)
        self.button_init_ctrl_setup.setEnabled(not wait)
        self.button_init_holder_setup.setEnabled(not wait)

    def on_button_init_controller_clicked(self):
        self.module.vmf_module._vmf_controller_sn_number = self.module.settings._controller_sn.value
        self.module.vmf_module.start_initialize_controller()

    def on_button_init_sample_holder_clicked(self):
        self.module.vmf_module._vmf_sample_holder_sn_number = self.module.settings._sample_holder_sn.value
        self.module.vmf_module.start_initialize_sample_holder()

    def on_button_load_calibration_clicked(self):
        self.module.vmf_module.start_load_calibration_from_sample_holder()

    def on_button_save_calibration_clicked(self):
        self.module.vmf_module.start_store_calibration_to_sample_holder()

    def on_button_load_calibration_from_file_clicked(self):
        self.module.vmf_module.start_load_calibration_from_file()

    def on_button_save_calibration_to_file_clicked(self):
        self.module.vmf_module.start_save_calibration_to_file()

    def update_sample_configuration(self):
        self.label_holder_settings.set_value(self.module.settings._cal_names)
        self.label_holder_cal_0.set_value(str(self.module.settings._cal_0_values))
        self.label_holder_cal_1.set_value(str(self.module.settings._cal_1_values))
        self.label_holder_cal_2.set_value(str(self.module.settings._cal_2_values))
