""" This is the screen of the module
Copyright Nanosurf AG 2021
License - MIT
"""

import pathlib
from PySide6 import QtWidgets, QtCore
import nanosurf as nsf

import module
import settings

class ResultTableID(nsf.gui.nsf_tables.TableEntryIDs):
    """ identifier id are used in a nsf_table widget"""
    CurrentSample = 0
    LastValue = 1
    MeanValue = 2

""" This connects a NSFComboBox item list with id used by the worker. Read active id with NSFComboBox.value() """
ComboCalcIDs = [
    nsf.gui.NSFComboEntry(settings.MonitorChannelID.User1Input,'User 1 Input'),
    nsf.gui.NSFComboEntry(settings.MonitorChannelID.Deflection,'Deflection Input'),
    nsf.gui.NSFComboEntry(settings.MonitorChannelID.ZAxisOut,'Z-Axis Out')
]

""" some useful list of allowed prefixes used by NSFSciEdit widgets"""
allowed_count_units = [nsf.sci_val.up.Prefix.base]
allowed_time_units = [nsf.sci_val.up.Prefix.base, nsf.sci_val.up.Prefix.milli]
allowed_meter_units = [nsf.sci_val.up.Prefix.milli, nsf.sci_val.up.Prefix.micro, nsf.sci_val.up.Prefix.nano]

class Screen(nsf.frameworks.qt_app.ModuleScreen):
    
    def __init__(self, screen_name: str = None, **kwargs):
        super().__init__(screen_name, **kwargs)
        self.module:module.WorkerModule # give pylance a type hint
    
    def on_activate_screen(self):
        """ called each time a screen is getting focus"""
        """ Overwrite default implementation to suppress clear message"""
        pass

    def do_setup_screen(self, worker: module.WorkerModule):
        """ create here your gui with all controls and their layout"""
        self.module = worker

        # left layout - main controls ------------------------------------------------------------

        self.scival_repetitions = nsf.gui.NSFSciEdit("Number of Samples")
        self.scival_repetitions.set_allowed_prefix_ids(allowed_count_units)
        self.scival_repetitions.set_prefix_id(nsf.sci_val.up.Prefix.base)
        self.scival_repetitions.set_precision(0)
        self.scival_repetitions.set_value_min_max(1, 1000)

        self.scival_time_per_rep = nsf.gui.NSFSciEdit("Time per Sample")
        self.scival_time_per_rep.set_allowed_prefix_ids(allowed_time_units)
        self.scival_time_per_rep.set_prefix_id(nsf.sci_val.up.Prefix.base)
        self.scival_time_per_rep.set_precision(2)
        self.scival_time_per_rep.set_value_min_max(0.01, 10.0)
        
        self.combo_calc_func = nsf.gui.NSFComboBox(ComboCalcIDs,"Monitor Channel")

        self.checkbox_continuous_rolling = nsf.gui.NSFCheckBox("Continuous")
        self.checkbox_auto_y_range = nsf.gui.NSFCheckBox("Y Auto Range")
        
        self.button_start_stop = nsf.gui.NSFPushButton("Start")
        self.button_save_data = nsf.gui.NSFPushButton("Save Data")
        self.button_load_data = nsf.gui.NSFPushButton("Load Data")
    
        self.layout_left = QtWidgets.QVBoxLayout()
        self.layout_left.addWidget(self.scival_repetitions)
        self.layout_left.addWidget(self.scival_time_per_rep)
        self.layout_left.addWidget(self.combo_calc_func)
        self.layout_left.addWidget(self.checkbox_continuous_rolling)
        self.layout_left.addStretch()
        self.layout_left.addWidget(self.button_start_stop)
        self.layout_left.addStretch()
        self.layout_left.addWidget(self.button_save_data)
        self.layout_left.addWidget(self.button_load_data)

        # mid layout - plots and result ---------------------------------------------------------
        self.chart_plot = nsf.gui.NSFChart()

        self.tableResults = nsf.gui.NSFNameValueTable(ResultTableID)
        self.tableResults.define_entry(ResultTableID.CurrentSample,"Samples")
        self.tableResults.define_entry(ResultTableID.LastValue,"Last Data")
        self.tableResults.define_entry(ResultTableID.MeanValue,"Mean Value")

        self.layout_mid  = QtWidgets.QVBoxLayout()
        self.layout_mid.addWidget(self.chart_plot)

        self.layout_result = QtWidgets.QHBoxLayout()
        self.layout_result.addWidget(self.tableResults)
        self.layout_result.addWidget(self.checkbox_auto_y_range, alignment=QtCore.Qt.AlignmentFlag.AlignTop)
        self.layout_mid.addLayout(self.layout_result)
        # set GUI controls
        self.screen_layout = QtWidgets.QHBoxLayout()
        # stretch only plot area and keep controls fix in size
        self.screen_layout.addLayout(self.layout_left, 0)
        self.screen_layout.addLayout(self.layout_mid,  1) 

        self.setLayout(self.screen_layout)

        self.bind_gui_elements()
        self.init_plot()
        self.enter_gui_state_idle()

    def bind_gui_elements(self):
        """ connect all gui widgets to module settings or any other source """
        
        # binding ProVal to widgets ensure that they are alway in sync 
        nsf.gui.connect_to_property(self.combo_calc_func, self.module.settings.channel_id)
        nsf.gui.connect_to_property(self.scival_repetitions, self.module.settings.repetitions)
        nsf.gui.connect_to_property(self.scival_time_per_rep, self.module.settings.time_per_repetition)
        nsf.gui.connect_to_property(self.checkbox_continuous_rolling, self.module.settings.continuous_rolling)
        nsf.gui.connect_to_property(self.checkbox_auto_y_range, self.module.settings.auto_y_range)

        # buttons have to be connected separately
        self.button_start_stop.clicked_event.connect(self.on_button_start_stop_clicked)    
        self.button_save_data.clicked_event.connect(self.on_button_save_data_clicked)    
        self.button_load_data.clicked_event.connect(self.on_button_load_data_clicked)

        # listen to signals from the core module to react and update the gui
        self.module.sig_work_start_requested.connect(self.enter_gui_state_wait)
        self.module.sig_work_stop_requested.connect(self.enter_gui_state_wait)
        self.module.sig_work_active.connect(self.enter_gui_state_active)
        self.module.sig_work_done.connect(self.enter_gui_state_idle)
        self.module.sig_new_data_available.connect(self.show_new_data)
        self.module.sig_data_invalid.connect(self.set_data_invalid)

    def init_plot(self):
        self.chart_plot.set_title("Measurements")
        self.chart_plot.set_label(nsf.gui.NSFChart.Axis.bottom, "Index")
        self.chart_plot.set_unit(nsf.gui.NSFChart.Axis.bottom, "")
        self.chart_plot.set_label(nsf.gui.NSFChart.Axis.left, "Data")
        self.chart_plot.set_unit(nsf.gui.NSFChart.Axis.left, "Arb")  
        self.chart_plot.set_range_x(0, self.module.settings.repetitions.value * self.module.settings.time_per_repetition.value)
        self.chart_plot.clear_plots()

    def on_button_start_stop_clicked(self):
        self.enter_gui_state_wait()
        if self.module.is_task_busy():
            self.module.stop_background_task()
        else:
            self.module.start_background_task()

    def on_button_save_data_clicked(self):
        source_dir = self.module.settings.save_path.value
        selected_filename = QtWidgets.QFileDialog.getSaveFileName(self, 'Save Data', dir=str(source_dir), filter="Matlab Files (*.mat)")
        if selected_filename[0] != '':
            selected_filename = pathlib.Path(selected_filename[0])
            self.module.settings.save_path.value = selected_filename.parent
            done = self.module.save_stream_to_file(selected_filename)
            if not done:
                self.module.app.show_error_message(f"Could not save data to: '{selected_filename}'!")
            else:
                self.module.app.show_info_message(f"Saved data to: '{selected_filename}'")

    def on_button_load_data_clicked(self):
        source_dir = self.module.settings.save_path.value
        selected_filename = QtWidgets.QFileDialog.getOpenFileName(self, 'Load Data', dir=str(source_dir), filter="Matlab Files (*.mat)")
        if selected_filename[0] != '':
            selected_filename = pathlib.Path(selected_filename[0])
            self.module.settings.save_path.value = selected_filename.parent
            ok, new_stream = self.module.load_stream_from_file(selected_filename)
            if ok:
                self.module.results.data_stream = new_stream
                self.module.results.last_index = new_stream.get_stream_length()
                self.module.sig_new_data_available.emit()
                self.module.app.show_info_message(f"Loaded data from: '{selected_filename}'")
            else:
                self.module.app.show_error_message(f"Could not load data from: '{selected_filename}'!")

    def enter_gui_state_wait(self):
        self.set_parameter_widget_enable_state(enabled=False)
        self.start_stop_button_state(wait=True)

    def enter_gui_state_active(self):
        self.set_parameter_widget_enable_state(enabled=False)
        self.start_stop_button_state(wait=False, stop_state=self.module.is_task_busy())
        self.init_plot()

    def enter_gui_state_idle(self):
        self.set_parameter_widget_enable_state(enabled=True)
        self.start_stop_button_state(wait=False, stop_state=self.module.is_task_busy())

    def set_parameter_widget_enable_state(self, enabled: bool = True):
        self.scival_time_per_rep.setEnabled(enabled)
        self.scival_repetitions.setEnabled(enabled)
        self.combo_calc_func.setEnabled(enabled)
        self.checkbox_continuous_rolling.setEnabled(enabled)

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
        self.chart_plot.clear_plots()
        self.tableResults.clear_values()

    def update_result(self):
        data = self.module.results
        self.tableResults.set_value(ResultTableID.CurrentSample, data.last_index, "", precision=0)
        self.tableResults.set_value(ResultTableID.LastValue, data.last_value)
        self.tableResults.set_value(ResultTableID.MeanValue, data.mean_value)

    def update_plot(self): 
        data = self.module.results
        self.chart_plot.plot_stream(data.data_stream, max_index=data.last_index)
        self.chart_plot.set_range_x(data.data_stream.x.value[0],data.data_stream.x.value[-1])            

        if self.module.settings.auto_y_range.value:
            measured_data = data.data_stream.channels[0].value[:data.last_index]
            if len(measured_data) > 0:
                min_val, max_val = measured_data.min(), measured_data.max()
                border_size = abs(max_val - min_val)*0.05
                self.chart_plot.set_range_y(min_val-border_size, max_val+border_size)
