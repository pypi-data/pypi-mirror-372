""" The long lasting worker thread to perform the frequency sweep
Copyright Nanosurf AG 2021
License - MIT
"""
import time
import numpy as np
from PySide6.QtCore import Signal

import nanosurf as nsf
import nanosurf.lib.spm.workflow.frequency_sweep as freq_sweep
from  nanosurf.lib.frameworks.qt_app import nsf_thread, module_base
from frequency_sweep_module import sweep_settings

class FrequencySweepData():
    def __init__(self):
        self.result_ok = False
        self.result_freq:list[float] = []
        self.result_amplitude:list[float] = []
        self.result_phase:list[float] = []

class FrequencySweepWorker(nsf_thread.SPMWorker):
    
    sig_sweep_tick = Signal(float, float) # send out ticker during sweeping with remaining time

    """ parameter for the background work"""
    par_cantilever = None
    par_excitation_method : sweep_settings.ExcitationMethodID = sweep_settings.ExcitationMethodID.PiezoDrive 
    par_input_source:freq_sweep.InputSource = freq_sweep.InputSource.Deflection
    par_output_source:freq_sweep.FrequencySweepOutput = freq_sweep.FrequencySweepOutput.Normal_Excitation
    par_bandwidth:freq_sweep.Bandwidths = freq_sweep.Bandwidths.Hz_360

    par_center_frequency = 150000
    par_frequency_range = 100000
    par_frequency_step = 100
    par_excitation_amplitude = 0.2
    par_deflection_setpoint = 0

    par_plot_style_id=sweep_settings.PlotStyleID.Linear

    def __init__(self, my_module: module_base.ModuleBase):
        self.module = my_module
        self.result = FrequencySweepData()
        super().__init__(my_module)

    def get_task_result(self) -> FrequencySweepData:
        return self.result

    def do_work(self):
        """ This is the working function for the long task"""
        self.result = FrequencySweepData()
        if self.connect_to_controller():
            self.application = self.spm.application
            self.freq_sweeper = freq_sweep.FrequencySweep(self.spm)
            if self.par_excitation_method == sweep_settings.ExcitationMethodID.PiezoDrive:
                self.application.OperatingMode.ExcitationMode = nsf.Spm.ExcitationMode.PiezoElectric
            else:
                self.application.OperatingMode.ExcitationMode = nsf.Spm.ExcitationMode.PhotoThermal 

            sweep_time = self.freq_sweeper.start_execute(
                start_frequency=self.par_center_frequency-(self.par_frequency_range/2),
                end_frequency=self.par_center_frequency+(self.par_frequency_range/2),
                frequency_step=self.par_frequency_step,
                sweep_amplitude=self.par_excitation_amplitude,
                input_source=self.par_input_source,
                input_range=freq_sweep.InputRanges.Full,
                mixer_bw_select=self.par_bandwidth,
                reference_phase=0.0, 
                output=self.par_output_source
                )

            self.logger.info(f"Wait for {sweep_time:.1f}s.")
            start_time = time.time()
            while self.freq_sweeper.is_executing() and not self.is_stop_request_pending():
                time.sleep(0.1)
                cur_freq = self.freq_sweeper.get_current_sweep_frequency()
                remaining_time = sweep_time - (time.time() - start_time)
                self.sig_sweep_tick.emit(cur_freq, remaining_time)
            data = self.freq_sweeper.finish_execution()

            if not self.is_stop_request_pending():
                self.result.result_amplitude = np.abs(data[0])
                self.result.result_phase = np.unwrap(np.angle(data[0], deg=True), discont=180)
                self.result.result_freq = data[1]
                self.result.result_ok = True
            else:
                self.result.result_ok = False

        self.disconnect_from_controller()
