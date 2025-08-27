""" This is the screen of the module
Copyright Nanosurf AG 2021
License - MIT
"""

from PySide6 import QtWidgets
import nanosurf as nsf
from demo_module import module, settings

class ResultTableID(nsf.gui.nsf_tables.TableEntryIDs):
    """ identifier id are used in a nsf_table widget"""
    Items = 0
    last_data = 1
    mean_value = 2

ComboPlotStyles = [
    nsf.gui.NSFComboEntry(settings.PlotStyleID.PlotSin,'Sin-Plot'),
    nsf.gui.NSFComboEntry(settings.PlotStyleID.PlotCos,'Cos-Plot'),
]

""" some useful list of allowed prefixes used by nsf_sci_edit widgets"""
allowed_count_units = [nsf.sci_val.up.Prefix.base]
allowed_time_units = [nsf.sci_val.up.Prefix.base, nsf.sci_val.up.Prefix.milli]
allowed_meter_units = [nsf.sci_val.up.Prefix.milli, nsf.sci_val.up.Prefix.micro, nsf.sci_val.up.Prefix.nano]

class DemoScreen(nsf.frameworks.qt_app.ModuleScreen):
    def __init__(self, screen_name: str = None, **kwargs):
        super().__init__(screen_name, **kwargs)
        self.module:module.DemoModule # give pylance a type hint

    def do_setup_screen(self, module: module.DemoModule):
        """ create here your gui with all controls and their layout"""
        self.module = module

        # left layout - main controls ------------------------------------------------------------

        self.scival_repetitions = nsf.gui.NSFSciEdit("Repetitions")
        self.scival_repetitions.set_allowed_prefix_ids(allowed_count_units)
        self.scival_repetitions.set_prefix_id(nsf.sci_val.up.Prefix.base)
        self.scival_repetitions.set_precision(0)
        self.scival_repetitions.set_value_min_max(1, 1000)

        self.scival_time_per_rep = nsf.gui.NSFSciEdit("Time per Repetition")
        self.scival_time_per_rep.set_allowed_prefix_ids(allowed_time_units)
        self.scival_time_per_rep.set_prefix_id(nsf.sci_val.up.Prefix.base)
        self.scival_time_per_rep.set_precision(2)
        self.scival_time_per_rep.set_value_min_max(0.01, 10.0)
        
        self.check_emit_ticks = nsf.gui.NSFCheckBox("Emit Ticks")
        self.button_start_stop = nsf.gui.NSFPushButton("Start")

        self.layout_left = QtWidgets.QVBoxLayout()
        self.layout_left.addWidget(self.scival_repetitions)
        self.layout_left.addWidget(self.scival_time_per_rep)
        #self.layout_left.addSpacerItem(nsf.gui.NSFVSpacer())
        self.layout_left.addWidget(self.check_emit_ticks)
        self.layout_left.addStretch()
        self.layout_left.addWidget(self.button_start_stop)

        # mid layout - plots and result ---------------------------------------------------------
        self.chart_plot = nsf.gui.NSFChart(logmodex=False)

        self.tableResults = nsf.gui.NSFNameValueTable(ResultTableID)
        self.tableResults.define_entry(ResultTableID.Items,"Items")
        self.tableResults.define_entry(ResultTableID.last_data,"Last Data")
        self.tableResults.define_entry(ResultTableID.mean_value,"Mean Value")

        self.layout_mid  = QtWidgets.QVBoxLayout()
        self.layout_mid.addWidget(self.chart_plot)
        self.layout_mid.addWidget(self.tableResults)

        # right layout - additional user inputs
        self.combo_plot_style = nsf.gui.NSFComboBox(ComboPlotStyles,"Plot Style")
        
        self.layout_right= QtWidgets.QVBoxLayout()
        self.layout_right.addWidget(self.combo_plot_style)
        self.layout_right.addSpacerItem(nsf.gui.NSFVSpacer())

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
        nsf.gui.connect_to_property(self.combo_plot_style, self.module.settings.plot_func_id)
        nsf.gui.connect_to_property(self.scival_repetitions, self.module.settings.repetitions)
        nsf.gui.connect_to_property(self.scival_time_per_rep, self.module.settings.time_per_repetition)
        nsf.gui.connect_to_property(self.check_emit_ticks, self.module.settings.send_ticks)

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
        self.chart_plot.set_title("Measurements")
        self.chart_plot.set_label(nsf.gui.NSFChart.Axis.bottom, "Index")
        self.chart_plot.set_unit(nsf.gui.NSFChart.Axis.bottom, "")
        self.chart_plot.set_label(nsf.gui.NSFChart.Axis.left, "Data")
        self.chart_plot.set_unit(nsf.gui.NSFChart.Axis.left, "Arb")  
        self.chart_plot.set_range_x(0, self.module.settings.repetitions.value-1)
        # self.chart_plot.plot.vb.enableAutoRange(y=True)
        # self.chart_plot.plot.vb.setAutoVisible(y=False)
        self.chart_plot.clear_plots()

    def on_button_start_stop_clicked(self):
        if self.module.is_worker_busy():
            self.module.stop_worker()
        else:
            self.module.start_worker()

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
        self.scival_time_per_rep.setEnabled(enabled)
        self.scival_repetitions.setEnabled(enabled)
        self.combo_plot_style.setEnabled(enabled)

    def start_stop_button_state(self, wait: bool = False, stop_state: bool = False):
        if wait:
            self.button_start_stop.setEnabled(False)
            self.button_start_stop.setText("Wait...")
        else:
            self.button_start_stop.setEnabled(True)
            self.button_start_stop.setText("Stop" if stop_state else "Start")

    def show_new_data(self):
        self.update_plot()
        self.update_result()

    def set_data_invalid(self):
        self.chart_plot.clear_plots()
        self.tableResults.clear_values()

    def update_result(self):
        res = self.module.get_result()
        self.tableResults.set_value(ResultTableID.Items, res.number_of_data_points, "", precision=0)
        self.tableResults.set_value(ResultTableID.last_data, res.last_data, "")
        self.tableResults.set_value(ResultTableID.mean_value, res.mean_value, "")

    def update_plot(self): 
        current_data = self.module.get_worker_result()
        self.chart_plot.plot_data(y=current_data.value)
