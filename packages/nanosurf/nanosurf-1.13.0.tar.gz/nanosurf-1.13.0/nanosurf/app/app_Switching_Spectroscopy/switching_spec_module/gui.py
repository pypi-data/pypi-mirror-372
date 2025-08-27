""" This is the screen of the module
Copyright Nanosurf AG 2021
License - MIT
"""

import pathlib
from PySide6 import QtWidgets
from PySide6.QtCore import Qt
import nanosurf as nsf

from switching_spec_module import module, settings

class ResultTableID(nsf.gui.nsf_tables.TableEntryIDs):
    """ identifier id are used in a nsf_table widget"""
    Items = 0
    last_data = 1
    mean_value = 2

ComboOutputChannels = [
    nsf.gui.NSFComboEntry(settings.OutputChannelID.User1,'User 1'),
    nsf.gui.NSFComboEntry(settings.OutputChannelID.User2,'User 2'),
    nsf.gui.NSFComboEntry(settings.OutputChannelID.TipVoltage,'Tip Voltage'),
]

""" some useful lists of allowed prefixes used by nsf_sci_edit widgets"""
allowed_count_units = [nsf.sci_val.up.Prefix.base]
allowed_time_units = [nsf.sci_val.up.Prefix.base, nsf.sci_val.up.Prefix.milli]
allowed_meter_units = [nsf.sci_val.up.Prefix.milli, nsf.sci_val.up.Prefix.micro, nsf.sci_val.up.Prefix.nano]
allowed_volt_units = [nsf.sci_val.up.Prefix.base, nsf.sci_val.up.Prefix.milli, nsf.sci_val.up.Prefix.micro]

class SwitchingSpecScreen(nsf.frameworks.qt_app.ModuleScreen):
    def __init__(self):
        super().__init__()
        self.module:module.SwitchingSpecModule # give pylance a type hint

    def do_setup_screen(self, module: module.SwitchingSpecModule):
        """ create here your gui with all controls and their layout"""
        self.module = module

        # left layout - main controls ------------------------------------------------------------

        self.combo_output_id = nsf.gui.NSFComboBox(ComboOutputChannels,"Output")

        self.scival_output_span = nsf.gui.NSFSciEdit("Voltage range")
        self.scival_output_span.set_allowed_prefix_ids(allowed_volt_units)
        self.scival_output_span.set_prefix_id(nsf.sci_val.up.Prefix.base)
        self.scival_output_span.set_precision(2)
        self.scival_output_span.set_value_min_max(0.0, 2000.0)

        self.scival_output_center = nsf.gui.NSFSciEdit("Center offset")
        self.scival_output_center.set_allowed_prefix_ids(allowed_volt_units)
        self.scival_output_center.set_prefix_id(nsf.sci_val.up.Prefix.base)
        self.scival_output_center.set_precision(2)
        self.scival_output_center.set_value_min_max(-1000.0, +1000.0)
        
        self.scival_num_steps = nsf.gui.NSFSciEdit("Number of steps")
        self.scival_num_steps.set_allowed_prefix_ids(allowed_meter_units)
        self.scival_num_steps.set_prefix_id(nsf.sci_val.up.Prefix.base)
        self.scival_num_steps.set_precision(0)
        self.scival_num_steps.set_value_min_max(2, 1000)

        self.scival_time_delay = nsf.gui.NSFSciEdit("Time delay after step")
        self.scival_time_delay.set_allowed_prefix_ids(allowed_time_units)
        self.scival_time_delay.set_prefix_id(nsf.sci_val.up.Prefix.base)
        self.scival_time_delay.set_precision(2)
        self.scival_time_delay.set_value_min_max(0.0, +1.0)
        
        self.scival_file_index = nsf.gui.NSFSciEdit("File index")
        self.scival_file_index.set_allowed_prefix_ids(allowed_count_units)
        self.scival_file_index.set_prefix_id(nsf.sci_val.up.Prefix.base)
        self.scival_file_index.set_precision(0)
        self.scival_file_index.set_value_min_max(1, 10000)

        self.check_show_on_data = nsf.gui.NSFCheckBox("Show 'on' data")
        self.check_do_revers_ramp = nsf.gui.NSFCheckBox("Backward first")

        self.edit_file_mask = nsf.gui.NSFEdit("File name mask")
        self.edit_file_path = nsf.gui.NSFEdit("Destination path")

        self.check_auto_save = nsf.gui.NSFCheckBox("Auto save data")
        self.button_start_stop = nsf.gui.NSFPushButton("Start")        
        self.button_browse = nsf.gui.NSFPushButton("Browse")
        self.button_export = nsf.gui.NSFPushButton("Save data")

        self.layout_left = QtWidgets.QVBoxLayout()
        self.layout_left.addWidget(self.combo_output_id)
        self.layout_left.addWidget(self.scival_output_span)
        self.layout_left.addWidget(self.scival_output_center)
        self.layout_left.addWidget(self.scival_num_steps)
        self.layout_left.addWidget(self.scival_time_delay)
        self.layout_left.addSpacing(10)
        self.layout_left.addWidget(self.check_do_revers_ramp)
        self.layout_left.addSpacing(10)
        self.layout_left.addWidget(self.check_show_on_data)
        self.layout_left.addStretch()
        self.layout_left.addSpacerItem(nsf.gui.NSFVSpacer())
        self.layout_left.addWidget(self.button_start_stop)

        # mid layout - plots and result ---------------------------------------------------------
        self.chart_amp = nsf.gui.NSFChart(logmodex=False)
        self.chart_phase = nsf.gui.NSFChart(logmodex=False)

        self.layout_mid = QtWidgets.QVBoxLayout()
        self.layout_mid.addWidget(self.chart_amp)
        self.layout_mid.addWidget(self.chart_phase)
        self.layout_path = QtWidgets.QHBoxLayout()
        self.layout_path.addWidget(self.edit_file_path)
        self.layout_path.addWidget(self.button_browse,alignment=Qt.AlignmentFlag.AlignBottom)        
        self.layout_mid.addLayout(self.layout_path)
        self.layout_file = QtWidgets.QHBoxLayout()
        self.layout_file_mask = QtWidgets.QVBoxLayout()
        self.layout_file_mask.addWidget(self.edit_file_mask)  
        self.layout_file.addLayout(self.layout_file_mask)      
        self.layout_file.addWidget(self.scival_file_index,alignment=Qt.AlignmentFlag.AlignBottom)  
        self.layout_file.addWidget(self.check_auto_save,alignment=Qt.AlignmentFlag.AlignVCenter)
        self.layout_file.addStretch()      
        self.layout_file.addWidget(self.button_export,alignment=Qt.AlignmentFlag.AlignBottom)
        self.layout_mid.addLayout(self.layout_file)


        # right layout - additional user inputs
        self.layout_right= QtWidgets.QVBoxLayout()

        # set GUI controls
        self.screen_layout = QtWidgets.QHBoxLayout()
        # stretch only plot area and keep controls fix in size
        self.screen_layout.addLayout(self.layout_left, 0)
        self.screen_layout.addLayout(self.layout_mid,  1) 
        self.screen_layout.addLayout(self.layout_right,0)
        self.setLayout(self.screen_layout)

        self.bind_gui_elements()
        self.init_plot()
        self.enter_gui_state_idle()

    def bind_gui_elements(self):
        """ connect all gui widgets to module settings or any other source """
        
        # binding ProVal to widgets ensure that they are alway in sync 
        nsf.gui.connect_to_property(self.combo_output_id, self.module.settings.output_id)
        nsf.gui.connect_to_property(self.scival_output_span, self.module.settings.output_span)
        nsf.gui.connect_to_property(self.scival_output_center, self.module.settings.output_center)
        nsf.gui.connect_to_property(self.scival_num_steps, self.module.settings.number_of_steps)
        nsf.gui.connect_to_property(self.scival_time_delay, self.module.settings.time_delay_after_step)
        nsf.gui.connect_to_property(self.edit_file_path, self.module.settings.folder_name)
        nsf.gui.connect_to_property(self.edit_file_mask, self.module.settings.file_name_mask)
        nsf.gui.connect_to_property(self.scival_file_index, self.module.settings.file_index)
        nsf.gui.connect_to_property(self.check_auto_save, self.module.settings.auto_save_data)
        nsf.gui.connect_to_property(self.check_do_revers_ramp, self.module.settings.revers_ramp)
        nsf.gui.connect_to_property(self.check_show_on_data, self.module.settings.show_on_data_values)

        # buttons have to be connected separately
        self.button_start_stop.clicked_event.connect(self.on_button_start_stop_clicked)    
        self.button_export.clicked_event.connect(self.on_button_export_clicked)    
        self.button_browse.clicked_event.connect(self.on_button_browse_clicked)    
        
        # listen to signals from the core module to react and update the gui
        self.module.sig_work_start_requested.connect(self.enter_gui_state_wait)
        self.module.sig_work_stop_requested.connect(self.enter_gui_state_wait)
        self.module.sig_work_active.connect(self.enter_gui_state_active)
        self.module.sig_work_done.connect(self.enter_gui_state_idle)
        self.module.sig_new_data_available.connect(self.show_new_data)
        self.module.sig_data_invalid.connect(self.set_data_invalid)

        self.module.settings.show_on_data_values.sig_value_changed.connect(self.change_plot_view)
        self.module.settings.output_id.sig_value_changed.connect(self.init_plot)

    def init_plot(self):
        self.chart_amp.set_title("Amplitude")
        self.chart_amp.set_label(nsf.gui.NSFChart.Axis.bottom, f"Output '{self.combo_output_id.current_entry_name()}'")
        self.chart_amp.set_unit(nsf.gui.NSFChart.Axis.bottom, "")
        self.chart_amp.set_unit(nsf.gui.NSFChart.Axis.left, "")  
        self.chart_amp.set_label(nsf.gui.NSFChart.Axis.left, "Amplitude")
        self.chart_amp.set_unit(nsf.gui.NSFChart.Axis.left, "V")  
        self.chart_amp.clear_plots()
        self.chart_phase.set_title("Phase")
        self.chart_phase.set_label(nsf.gui.NSFChart.Axis.bottom, f"Output '{self.combo_output_id.current_entry_name()}'")
        self.chart_phase.set_unit(nsf.gui.NSFChart.Axis.bottom, "")
        self.chart_phase.set_label(nsf.gui.NSFChart.Axis.left, "Phase")
        self.chart_phase.set_unit(nsf.gui.NSFChart.Axis.left, "°")  
        self.chart_phase.clear_plots()        

    def on_button_start_stop_clicked(self):
        if self.module.is_worker_busy():
            self.module.stop_worker()
        else:
            self.module.start_worker()

    def on_button_export_clicked(self):
        self.module.save_data()            

    def on_button_browse_clicked(self):
        dlg = QtWidgets.QFileDialog()
        dlg.setFileMode(QtWidgets.QFileDialog.FileMode.Directory)
        dlg.setDirectory(str(self.module.settings.folder_name.value))
        if dlg.exec_():
            fileNames = dlg.selectedFiles()
            self.module.settings.folder_name.value = pathlib.Path(fileNames[0])

    def enter_gui_state_wait(self):
        self.set_parameter_widget_enable_state(enabled=False)
        self.start_stop_button_state(wait=True)

    def enter_gui_state_active(self):
        self.set_parameter_widget_enable_state(enabled=False)
        self.start_stop_button_state(wait=False, stop_state=self.module.is_worker_busy())
        self.init_plot()

    def enter_gui_state_idle(self):
        self.set_parameter_widget_enable_state(enabled=True)
        self.start_stop_button_state(wait=False, stop_state=self.module.is_worker_busy())

    def set_parameter_widget_enable_state(self, enabled: bool = True):
        self.scival_output_span.setEnabled(enabled)
        self.scival_output_center.setEnabled(enabled)
        self.scival_num_steps.setEnabled(enabled)
        self.scival_time_delay.setEnabled(enabled)
        self.check_do_revers_ramp.setEnabled(enabled)

    def start_stop_button_state(self, wait: bool = False, stop_state: bool = False):
        if wait:
            self.button_start_stop.setEnabled(False)
            self.button_start_stop.set_label("Wait...")
        else:
            self.button_start_stop.setEnabled(True)
            self.button_start_stop.set_label("Stop" if stop_state else "Start")

    def show_new_data(self):
        self.update_plot()
        self.update_result()

    def set_data_invalid(self):
        half_range = self.module.settings.output_span.value/2.0
        min_v = self.module.settings.output_center.value - half_range
        max_v = self.module.settings.output_center.value + half_range
        self.chart_amp.clear_plots()
        self.chart_amp.set_range_x(min_v, max_v)
        self.chart_phase.clear_plots()
        self.chart_phase.set_range_x(min_v, max_v)

    def update_result(self):
        res = self.module.get_result()
        # self.tableResults.set_value(ResultTableID.Items, res.number_of_data_points, "", precision=0)
        # self.tableResults.set_value(ResultTableID.last_data, res.last_data, "")
        # self.tableResults.set_value(ResultTableID.mean_value, res.mean_value, "")

    def update_plot(self): 
        current_data = self.module.get_result()
        self.chart_amp.set_unit(nsf.gui.NSFChart.Axis.bottom, current_data.outputs_unit)
        self.chart_phase.set_unit(nsf.gui.NSFChart.Axis.bottom, current_data.outputs_unit)  
        self.chart_amp.set_unit(nsf.gui.NSFChart.Axis.left, current_data.amplitudes_unit)  
        self.chart_amp.plot_data(x=current_data.outputs, y=current_data.amplitudes_off, layer_index=0)
        self.chart_phase.plot_data(x=current_data.outputs, y=current_data.phases_off, layer_index=0)
        if self.module.settings.show_on_data_values.value:
            self.chart_amp.plot_data(x=current_data.outputs, y=current_data.amplitudes_on, layer_index=1)
            self.chart_phase.plot_data(x=current_data.outputs, y=current_data.phases_on, layer_index=1)

    def change_plot_view(self):
        self.init_plot()
        self.update_plot()