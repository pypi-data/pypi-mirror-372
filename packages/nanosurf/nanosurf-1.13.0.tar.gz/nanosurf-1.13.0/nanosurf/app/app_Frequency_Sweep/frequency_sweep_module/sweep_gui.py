""" This is the screen of the module
Copyright Nanosurf AG 2021
License - MIT
"""

from PySide6 import QtWidgets
import nanosurf as nsf
import nanosurf.lib.spm.workflow.frequency_sweep as freq_sweep
from frequency_sweep_module import sweep_module, sweep_settings

class ResultTableID(nsf.gui.TableEntryIDs):
    """ identifier id are used in a nsf_table widget"""
    resonance_frequency = 0
    q_factor = 1
    spring_constant = 2

ComboPlotStyles = [
    nsf.gui.NSFComboEntry(sweep_settings.PlotStyleID.Linear,'Linear'),
    nsf.gui.NSFComboEntry(sweep_settings.PlotStyleID.Logarithmic,'Logarithmic'),
]

ComboExcitationMethods = [
    nsf.gui.NSFComboEntry(sweep_settings.ExcitationMethodID.CleanDrive,'CleanDrive'),
    nsf.gui.NSFComboEntry(sweep_settings.ExcitationMethodID.PiezoDrive,'Piezo Excitation'),
]

""" some useful lists of allowed prefixes used by nsf_sci_edit widgets"""
allowed_count_units = [nsf.sci_val.up.Prefix.base]
allowed_time_units = [nsf.sci_val.up.Prefix.base, nsf.sci_val.up.Prefix.milli]
allowed_meter_units = [nsf.sci_val.up.Prefix.milli, nsf.sci_val.up.Prefix.micro, nsf.sci_val.up.Prefix.nano]
allowed_frequency_units = [nsf.sci_val.up.Prefix.mega, nsf.sci_val.up.Prefix.kilo, nsf.sci_val.up.Prefix.base]
allowed_voltage_units = [nsf.sci_val.up.Prefix.milli, nsf.sci_val.up.Prefix.micro, nsf.sci_val.up.Prefix.base]
allowed_spring_constant_units = [nsf.sci_val.up.Prefix.base]

class SweepScreen(nsf.frameworks.qt_app.ModuleScreen):
    def __init__(self):
        self.module:sweep_module.FrequencySweepModule # give pylance a type hint
        super().__init__()

    def do_setup_screen(self, module: sweep_module.FrequencySweepModule):
        """ create here your gui with all controls and their layout"""
        self.module = module

        # left layout - main controls ------------------------------------------------------------
        self.label_cantilever = QtWidgets.QLabel("Cantilever")
        self.combo_cantilever = QtWidgets.QComboBox()
        self.update_cantilever_list()

        self.combo_excitation_method = nsf.gui.NSFComboBox(ComboExcitationMethods, "Excitation Method")

        self.combo_input_source_items =  nsf.gui.NSFComboBox.create_entry_list_from_dict(freq_sweep.FrequencySweep.input_sources_names)
        self.combo_input_source = nsf.gui.NSFComboBox(self.combo_input_source_items , "Input Source")

        self.combo_output_source_items =  nsf.gui.NSFComboBox.create_entry_list_from_dict(freq_sweep.FrequencySweep.output_names)
        self.combo_output_source = nsf.gui.NSFComboBox(self.combo_output_source_items , "Output Source")
     
        self.combo_bandwidth_items =  nsf.gui.NSFComboBox.create_entry_list_from_dict(freq_sweep.FrequencySweep.bandwidths_names)
        self.combo_bandwidth = nsf.gui.NSFComboBox(self.combo_bandwidth_items , "Bandwidth")

        self.scival_center_frequency = nsf.gui.NSFSciEdit("Center Frequency")
        self.scival_center_frequency.set_allowed_prefix_ids(allowed_frequency_units)
        self.scival_center_frequency.set_prefix_id(nsf.sci_val.up.Prefix.auto_)
        self.scival_center_frequency.set_precision(0)
        self.scival_center_frequency.set_value_min(0)

        self.scival_frequency_range = nsf.gui.NSFSciEdit("Frequency Range")
        self.scival_frequency_range.set_allowed_prefix_ids(allowed_frequency_units)
        self.scival_frequency_range.set_prefix_id(nsf.sci_val.up.Prefix.auto_)
        self.scival_frequency_range.set_precision(0)
        self.scival_frequency_range.set_value_min(0)

        self.scival_frequency_steps = nsf.gui.NSFSciEdit("Frequency Steps")
        self.scival_frequency_steps.set_allowed_prefix_ids(allowed_frequency_units)
        self.scival_frequency_steps.set_prefix_id(nsf.sci_val.up.Prefix.auto_)
        self.scival_frequency_steps.set_precision(0)
        self.scival_frequency_steps.set_value_min(0)

        self.scival_excitation_amplitude = nsf.gui.NSFSciEdit("Excitation Amplitude")
        self.scival_excitation_amplitude.set_allowed_prefix_ids(allowed_voltage_units)
        self.scival_excitation_amplitude.set_prefix_id(nsf.sci_val.up.Prefix.auto_)
        self.scival_excitation_amplitude.set_precision(1)
        self.scival_excitation_amplitude.set_value_min(0)
        self.scival_excitation_amplitude.set_value_max(2)
        
        self.button_start_stop = nsf.gui.NSFPushButton("Start Sweep")
        
        self.layout_left = QtWidgets.QVBoxLayout()
        # self.layout_left.addWidget(self.label_cantilever)
        # self.layout_left.addWidget(self.combo_cantilever)
        self.layout_left.addWidget(self.combo_excitation_method)
        self.layout_left.addWidget(self.combo_input_source)
        self.layout_left.addWidget(self.combo_output_source)
        self.layout_left.addWidget(self.combo_bandwidth)
        self.layout_left.addWidget(self.scival_center_frequency)
        self.layout_left.addWidget(self.scival_frequency_range)
        self.layout_left.addWidget(self.scival_frequency_steps)
        self.layout_left.addWidget(self.scival_excitation_amplitude)
        self.layout_left.addStretch()
        self.layout_left.addWidget(self.button_start_stop)
        self.layout_left.addSpacerItem(nsf.gui.NSFVSpacer())

        # mid layout - plots and result ---------------------------------------------------------
        self.amplitude_plot = nsf.gui.NSFChart()
        self.phase_plot = nsf.gui.NSFChart()
        self.tableResults = nsf.gui.NSFNameValueTable(ResultTableID)
        self.tableResults.define_entry(ResultTableID.resonance_frequency,"Resonance Frequency")
        self.tableResults.define_entry(ResultTableID.q_factor,"Q-Factor")

        self.layout_mid  = QtWidgets.QVBoxLayout()
        self.layout_mid.addWidget(self.amplitude_plot)
        self.layout_mid.addWidget(self.phase_plot)
        self.layout_mid.addWidget(self.tableResults)
        self.layout_mid.addSpacerItem(nsf.gui.NSFVSpacer())

        # right layout - additional user inputs
        self.combo_plot_style = nsf.gui.NSFComboBox(ComboPlotStyles, "Plot Style")
        
        self.layout_right= QtWidgets.QVBoxLayout()
        self.layout_right.addWidget(self.combo_plot_style)
        self.layout_right.addSpacerItem(nsf.gui.NSFVSpacer())
        
        # set GUI controls
        self.screen_layout = QtWidgets.QHBoxLayout()
        # stretch only plot area and keep controls fix in size
        self.screen_layout.addLayout(self.layout_left, 0)
        self.screen_layout.addLayout(self.layout_mid, 1) 
        self.screen_layout.addLayout(self.layout_right, 0)
        
        self.setLayout(self.screen_layout)

        self.bind_gui_elements()
        self.init_plot()
        self.enter_gui_state_idle()
        self.update_plot()

    def bind_gui_elements(self):
        """ connect here all gui widgets to settings of the module or any other source"""
        
        # binding ProVal to widgets ensure that they are alway in sync 
        nsf.gui.connect_to_property(self.combo_plot_style, self.module.settings.plot_style_id)
        nsf.gui.connect_to_property(self.combo_excitation_method, self.module.settings.excitation_method)
        nsf.gui.connect_to_property(self.combo_input_source, self.module.settings.input_source)
        nsf.gui.connect_to_property(self.combo_output_source, self.module.settings.output_source)
        nsf.gui.connect_to_property(self.combo_bandwidth, self.module.settings.bandwidth)
        nsf.gui.connect_to_property(self.scival_center_frequency, self.module.settings.center_frequency)
        nsf.gui.connect_to_property(self.scival_frequency_range, self.module.settings.frequency_range)
        nsf.gui.connect_to_property(self.scival_frequency_steps, self.module.settings.frequency_steps)
        nsf.gui.connect_to_property(self.scival_excitation_amplitude, self.module.settings.excitation_amplitude)
        
        # combo boxes have to be connected separately
        self.combo_cantilever.activated.connect(self.update_cantilever)
        self.module.settings.plot_style_id.sig_value_changed.connect(self.update_plot)

        # buttons have to be connected separately  
        self.button_start_stop.clicked_event.connect(self.on_button_start_stop_clicked)
        
        # listen to signals from the core module to react and update the gui
        self.module.sig_work_start_requested.connect(self.enter_gui_state_wait)
        self.module.sig_work_stop_requested.connect(self.enter_gui_state_wait)
        self.module.sig_work_active.connect(self.enter_gui_state_active)
        self.module.sig_work_done.connect(self.enter_gui_state_idle)
        self.module.sig_new_data_available.connect(self.show_new_data)
        self.module.sig_data_invalid.connect(self.set_data_invalid)

    def init_plot(self):
        self.amplitude_plot.set_title("Amplitude Spectrum")
        self.amplitude_plot.set_label(nsf.gui.NSFChart.Axis.bottom, "Frequency")
        self.amplitude_plot.set_unit(nsf.gui.NSFChart.Axis.bottom, "Hz")
        self.amplitude_plot.set_label(nsf.gui.NSFChart.Axis.left, "Amplitude")
        self.amplitude_plot.set_unit(nsf.gui.NSFChart.Axis.left, "V") 
        self.amplitude_plot.clear_plots()

        self.phase_plot.set_title("Phase Spectrum")
        self.phase_plot.set_label(nsf.gui.NSFChart.Axis.bottom, "Frequency")
        self.phase_plot.set_unit(nsf.gui.NSFChart.Axis.bottom, "Hz")
        self.phase_plot.set_label(nsf.gui.NSFChart.Axis.left, "Phase")
        self.phase_plot.set_unit(nsf.gui.NSFChart.Axis.left, "deg")
        self.phase_plot.clear_plots()

    def on_button_start_stop_clicked(self):
        if self.module.is_sweep_busy():
            self.module.stop_sweep()
            self.start_stop_button_state(wait=True)
        else:
            self.module.start_sweep()

    def enter_gui_state_wait(self):
        self.set_parameter_widget_enable_state(enabled=False)
        self.start_stop_button_state(wait=True)

    def enter_gui_state_active(self):
        self.set_parameter_widget_enable_state(enabled=False)
        self.start_stop_button_state(wait=False, stop_state=self.module.is_sweep_busy())
        self.init_plot()

    def enter_gui_state_idle(self):
        self.set_parameter_widget_enable_state(enabled=True)
        self.start_stop_button_state(wait=False, stop_state=self.module.is_sweep_busy())

    def set_parameter_widget_enable_state(self, enabled: bool = True):
        self.combo_cantilever.setEnabled(enabled)
        self.combo_excitation_method.setEnabled(enabled)
        self.combo_input_source.setEnabled(enabled)
        self.combo_output_source.setEnabled(enabled)
        self.combo_bandwidth.setEnabled(enabled)
        self.scival_center_frequency.setEnabled(enabled)
        self.scival_frequency_range.setEnabled(enabled)
        self.scival_frequency_steps.setEnabled(enabled)
        self.scival_excitation_amplitude.setEnabled(enabled)

    def start_stop_button_state(self, wait: bool = False, stop_state: bool = False):
        if wait:
            self.button_start_stop.setEnabled(False)
            self.button_start_stop.set_label("Wait...")
        else:
            self.button_start_stop.setEnabled(True)
            self.button_start_stop.set_label("Stop Sweep" if stop_state else "Start Sweep")

    def show_new_data(self):
        self.update_plot()
        self.update_result_table()

    def set_data_invalid(self):
        self.amplitude_plot.clear_plots()
        self.phase_plot.clear_plots()

    def update_result_table(self):
        res = self.module.get_result()
        self.tableResults.set_value(ResultTableID.resonance_frequency, res.resonance_frequency, "Hz", precision=3)
        self.tableResults.set_value(ResultTableID.q_factor, res.q_factor, "", precision=3)

    def update_plot(self):
        log_style = self.module.settings.plot_style_id.value == sweep_settings.PlotStyleID.Logarithmic
        self.amplitude_plot.set_log_mode_x(log_style)
        self.amplitude_plot.set_log_mode_y(log_style)
        self.phase_plot.set_log_mode_x(log_style)
        current_measured_data = self.module.get_sweep_result()
        current_fitted_data = self.module.get_fit_result()

        self.amplitude_plot.clear_plots()
        self.phase_plot.clear_plots()
        if current_measured_data.result_ok:
            self.amplitude_plot.plot_data(x=current_measured_data.result_freq, y=current_measured_data.result_amplitude, layer_index=0)
            self.phase_plot.plot_data(x=current_measured_data.result_freq, y=current_measured_data.result_phase, layer_index=0)
        if current_fitted_data.result_ok:
            self.amplitude_plot.plot_data(x=current_fitted_data.result_fit_freq, y=current_fitted_data.result_fit_amplitude, layer_index=1)
            self.phase_plot.plot_data(x=current_fitted_data.result_fit_freq, y=current_fitted_data.result_fit_phase, layer_index=1)

    def update_cantilever_list(self):
        self.combo_cantilever.clear()
        cantilever_list = self.module.get_cantilever_list()
        self.combo_cantilever.addItems(cantilever_list)

    def update_cantilever(self):
        self.module.cantilever.name = self.combo_cantilever.currentText()
        self.module.cantilever.index = self.combo_cantilever.currentIndex()
        self.module.select_cantilever()

    def update_excitation_method(self):
        excitation_method = self.combo_excitation_method.value()
        self.module.select_excitation_method(excitation_method)
