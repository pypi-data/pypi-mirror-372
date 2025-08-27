""" The functional module where the functionality goes
Copyright Nanosurf AG 2021
License - MIT
"""

import nanosurf as nsf
import nanosurf.lib.spm.workflow.frequency_sweep as freq_sweep

from PySide6.QtCore import Signal

from frequency_sweep_module import sweep_settings, sweep_task, sweep_fit

class FrequencySweepModule(nsf.frameworks.qt_app.ModuleBase):

    sig_work_start_requested = Signal()
    sig_work_stop_requested = Signal()
    sig_work_active = Signal()
    sig_work_tick = Signal(float) # inform about sweep progress
    sig_work_done = Signal()
    sig_new_data_available = Signal()
    sig_data_invalid = Signal()

    """ Initialization functions of the module """

    def __init__(self, app: nsf.frameworks.qt_app.ApplicationBase, gui):
        super().__init__(app, gui)
        self.app: nsf.frameworks.qt_app.ApplicationBase = app
        self.spm:nsf.spm.Spm = None
        self.freq_sweeper:freq_sweep.FrequencySweep = None

        """ Prepare here module settings which are stored and loaded from file by the app framework """
        self.settings = sweep_settings.SweepSettings()
        self.cantilever = self.settings.cantilever
        self.result = sweep_settings.SweepResults()

    def do_start(self):
        """ This function is called once at startup of application
            Initialize here all module specific values.
        """
        if self._connect_to_controller():
            self.application = self.spm.application
            self.scan_head = self.application.ScanHead
            self.freq_sweeper = freq_sweep.FrequencySweep(self.spm)

        self.setup_sweep_thread()
        self.setup_fit_thread()
        self.connect_to_properties()

    def do_stop(self):
        """ This function is called at module shutdown"""
        if self.sweep_thread.is_thread_running():
            self.logger.info("Wait until worker thread has ended...")
            self.sweep_thread.stop_thread(wait=True)

        if self.fit_thread.is_thread_running():    
            self.fit_thread.stop_thread(wait=True)

    def get_cantilever_list(self) -> list[str]:
        self.cantilever_list:list[str] = []
        try:
            cantilever_list_count = self.application.CantileverList.Count
            for i in range(cantilever_list_count):
                self.cantilever_list.append(self.application.CantileverList.name(i))
        except Exception:
            pass
        return self.cantilever_list

    def connect_to_properties(self):
        """ Connect action functions to settings 
            The connected functions are called whenever a setting is changed (e.g. by GUI elements)
        """
        self.settings.center_frequency.sig_value_changed.connect(self.update_sweep_parameter)
        self.settings.frequency_range.sig_value_changed.connect(self.update_sweep_parameter)
        self.settings.frequency_steps.sig_value_changed.connect(self.update_sweep_parameter)
        self.settings.excitation_amplitude.sig_value_changed.connect(self.update_sweep_parameter)
        self.settings.input_source.sig_value_changed.connect(self.update_sweep_parameter)
        self.settings.output_source.sig_value_changed.connect(self.update_sweep_parameter)
        self.settings.bandwidth.sig_value_changed.connect(self.update_sweep_parameter)
        self.settings.plot_style_id.sig_value_changed.connect(self.update_sweep_parameter)

    def setup_sweep_thread(self):
        """ Create the sweep worker task and connect to its event """
        self.sweep_thread = sweep_task.FrequencySweepWorker(self)
        self.sweep_thread.sig_worker_started.connect(self._on_sig_sweep_started)
        self.sweep_thread.sig_worker_finished.connect(self._on_sig_sweep_finished)
        self.sweep_thread.sig_sweep_tick.connect(self._on_sig_sweep_ticker)
        self.sweep_thread.start_thread()

    def setup_fit_thread(self):
        """ Create the fit worker task and connect to its event """
        self.fit_thread = sweep_fit.FrequencySweepFitWorker(self)
        self.fit_thread.sig_worker_started.connect(self._on_sig_fit_started)
        self.fit_thread.sig_worker_finished.connect(self._on_sig_fit_finished)
        self.fit_thread.start_thread()
    
    """ Now the business logic of the module """

    def _connect_to_controller(self) -> bool:
        ok = self.spm is not None
        if not ok:
            self.spm = nsf.SPM()
            if self.spm.is_connected():
                if self.spm.is_scripting_enabled():
                    ok = True
                else:
                    self.app.show_error_message("Error: Scripting interface is not enabled")
            else:
                 self.app.show_error_message("Error: Could not connect to controller. Check if software is started")
        if not ok:
            self.spm = None
        return ok

    def _disconnect_from_controller(self):
        if self.spm is not None:
            if self.spm.application is not None:
                del self.spm
            self.spm = None

    def select_cantilever(self):
        self.scan_head.Cantilever = self.cantilever.index
        self.get_cantilever_properties()

    def get_cantilever_properties(self):
        self.cantilever.length = self.scan_head.GetCantileverProperty(0)
        self.cantilever.width = self.scan_head.GetCantileverProperty(1)
        self.cantilever.spring_constant = self.scan_head.GetCantileverProperty(2)
        self.cantilever.resonance_frequency_air = self.scan_head.GetCantileverProperty(3)
        self.cantilever.q_factor_air = self.scan_head.GetCantileverProperty(4)
        self.cantilever.resonance_frequency_liquid = self.scan_head.GetCantileverProperty(5)
        self.cantilever.q_factor_liquid = self.scan_head.GetCantileverProperty(6)

    def select_excitation_method(self, excitation_method: sweep_settings.ExcitationMethodID):
        if excitation_method == sweep_settings.ExcitationMethodID.CleanDrive: 
            self.settings.excitation_method = nsf.Spm.ExcitationMode.PhotoThermal
        else: 
            self.settings.excitation_method = nsf.Spm.ExcitationMode.PiezoElectric
        self.update_sweep_parameter()


    def start_sweep(self):
        if not self.sweep_thread.is_worker_running():
            self.app.clear_message()
            self.update_sweep_parameter()
            self.sweep_thread.start_worker()

    def stop_sweep(self):
        if self.sweep_thread.is_worker_running():
            self.app.show_info_message("Aborting Sweep...")
            self.sweep_thread.abort_worker(wait=False)
    
    def is_sweep_busy(self) -> bool:
        return self.sweep_thread.is_worker_running()

    def get_result(self) -> sweep_settings.SweepResults:
        return self.result

    def get_sweep_result(self) -> sweep_task.FrequencySweepData:
        return self.sweep_thread.get_task_result()
    
    def start_fit(self):
        if not self.fit_thread.is_worker_running():
            self.update_sweep_parameter()
            self.update_fit_parameter()
            self.fit_thread.start_worker()
    
    def get_fit_result(self) -> sweep_fit.FrequencySweepFitData:
        return self.fit_thread.get_task_result()

    """ Parameter update"""   

    def update_sweep_parameter(self):
        self.sweep_thread.par_cantilever = self.cantilever
        self.sweep_thread.par_input_source = self.settings.input_source.value
        self.sweep_thread.par_output_source = self.settings.output_source.value
        self.sweep_thread.par_bandwidth=self.settings.bandwidth.value

        self.sweep_thread.par_center_frequency = self.settings.center_frequency.value
        self.sweep_thread.par_frequency_range = self.settings.frequency_range.value
        self.sweep_thread.par_frequency_step = self.settings.frequency_steps.value
        self.sweep_thread.par_excitation_amplitude = self.settings.excitation_amplitude.value
        self.sweep_thread.par_deflection_setpoint = self.settings.deflection_setpoint.value
        self.sweep_thread.par_excitation_method = self.settings.excitation_method.value

    def update_fit_parameter(self):
        data = self.sweep_thread.get_task_result()
        self.fit_thread.par_measured_amplitudes = data.result_amplitude
        self.fit_thread.par_measured_phases = data.result_phase
        self.fit_thread.par_measured_frequencys = data.result_freq

    """ thread state handling """

    """ sweep thread state handling """
    def _on_sig_sweep_started(self):
        self.app.show_info_message("Sweeping ...") 
        self.logger.info("Thread started to work")
        self.sig_data_invalid.emit()
        self.sig_work_active.emit()

    def _on_sig_sweep_finished(self):
        if not self.sweep_thread.is_worker_aborted():
            self.app.show_info_message("Sweep done")
            self.sig_new_data_available.emit()            
            self.start_fit()
            self.logger.info("Thread done ")
        else:
            self.app.show_info_message("Sweep aborted") 
            self.logger.info("Thread aborted ")
        self.sig_work_done.emit()

    def _on_sig_sweep_ticker(self, cur_freq, remaining_time):
        self.app.show_info_message(f"Sweeping in progress. Current frequency: {cur_freq:.2f}Hz, Remaining time {remaining_time:.1f}s.") 
        self.sig_work_tick.emit(remaining_time)

    """ fit thread state handling """
    def _on_sig_fit_started(self):
        self.app.show_info_message("Fitting ...") 
        self.logger.info("Thread started to work")
        self.sig_work_active.emit()

    def _on_sig_fit_finished(self):
        if not self.sweep_thread.is_worker_aborted():
            fit_data = self.fit_thread.get_task_result()
            if fit_data.result_ok:
                self.app.show_info_message("Fitting done")
                self.logger.info("Fitting done")
                self.result.resonance_frequency = fit_data.result_resonance_frequency_amplitude
                self.result.q_factor = fit_data.result_q_factor_amplitude
            else:
                self.app.show_info_message("Fitting error: Could not extract amplitude and phase curve from data") 
                self.logger.info("Thread aborted ")
        else:
            self.app.show_message("Fitting aborted") 
            self.logger.info("Thread aborted ")
        self.sig_new_data_available.emit()
        self.sig_work_done.emit()
