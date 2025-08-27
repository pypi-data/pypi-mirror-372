""" The functional module where the functionality goes
Copyright Nanosurf AG 2021
License - MIT
"""
import numpy as np
import pathlib
from PySide6.QtCore import Signal
import nanosurf as nsf

from switching_spec_module import settings, worker_task

class SwitchingSpecModule(nsf.frameworks.qt_app.ModuleBase):

    sig_work_start_requested = Signal()
    sig_work_stop_requested = Signal()
    sig_work_active = Signal()
    sig_work_done = Signal()
    sig_new_data_available = Signal()
    sig_data_invalid = Signal()

    """ Initialization functions of the module """

    def __init__(self, app: nsf.frameworks.qt_app.ApplicationBase, gui):
        super().__init__(app, gui)
        self.app:nsf.frameworks.qt_app.ApplicationBase = app
        """ Prepare here module settings which are stored and loaded from file by the app framework """
        self.settings = settings.SpecSettings()
        self.result = settings.SpecResults()

    def do_start(self):
        """ This function is called once at startup of application
            Initialize here all module specific values.
        """
        self.setup_worker_thread()
        self.connect_to_properties()

    def do_stop(self):
        """ This function is called at module shutdown"""
        if self.worker_thread.is_thread_running():
            self.logger.info("Wait until worker thread has ended...")
            self.worker_thread.stop_thread(wait=True)

    def connect_to_properties(self):
        """ Connect action functions to settings 
            The connected functions are called whenever a setting is changed (e.g. by GUI elements)
        """
        self.settings.output_span.sig_value_changed.connect(self.update_worker_parameter)
        self.settings.output_center.sig_value_changed.connect(self.update_worker_parameter)
        self.settings.number_of_steps.sig_value_changed.connect(self.update_worker_parameter)
        self.settings.time_delay_after_step.sig_value_changed.connect(self.update_worker_parameter)
        self.settings.output_id.sig_value_changed.connect(self.update_worker_parameter)
        self.settings.revers_ramp.sig_value_changed.connect(self.update_worker_parameter)

    def setup_worker_thread(self):
        """ Create the background worker task and connect to its event """
        self.worker_thread = worker_task.SpecWorker(self)
        self.worker_thread.sig_worker_started.connect(self._on_sig_worker_started)
        self.worker_thread.sig_worker_finished.connect(self._on_sig_worker_finished)
        self.worker_thread.sig_new_data.connect(self._on_sig_worker_new_data)
        self.worker_thread.sig_tick.connect(self._on_sig_worker_tick)
        self.worker_thread.start_thread()

    """ Now the business logic of the module """
        
    def start_worker(self):
        if not self.worker_thread.is_worker_running():
            self.result = settings.SpecResults()
            self.update_worker_parameter()
            self.sig_work_start_requested.emit()
            self.worker_thread.start_worker()

    def stop_worker(self):
        if self.worker_thread.is_worker_running():
            self.sig_work_stop_requested.emit()
            self.worker_thread.abort_worker()
    
    def is_worker_busy(self) -> bool:
        return self.worker_thread.is_worker_running()

    def get_result(self) -> settings.SpecResults:
        return self.result

    def get_worker_result(self) -> worker_task.SpecWorkerData:
        return self.worker_thread.get_result()

    def update_worker_parameter(self):
        self.worker_thread.par_output_id = self.settings.output_id.value
        if self.settings.revers_ramp.value:
            self.worker_thread.par_output_span = -1.0 * self.settings.output_span.value
        else:
            self.worker_thread.par_output_span = self.settings.output_span.value
        self.worker_thread.par_output_center = self.settings.output_center.value
        self.worker_thread.par_time_per_step = self.settings.time_delay_after_step.value
        self.worker_thread.par_steps = self.settings.number_of_steps.value
        self.sig_data_invalid.emit()

    """ worker thread state handling """

    def _on_sig_worker_started(self):
        self.app.show_info_message("Working ...") 
        self.logger.info("Thread started to work")
        self.sig_data_invalid.emit()
        self.sig_work_active.emit()

    def _on_sig_worker_finished(self):
        self.sig_work_done.emit()
        if not self.worker_thread.is_worker_aborted():
            self.app.show_info_message("Work done") 
            self.logger.info("Background worker finished ")
            if self.settings.auto_save_data.value:
                if len(self.get_result().outputs) > 0:
                    self.save_data()
                else:
                    self.app.show_info_message("Auto save info: No data measured") 
                    self.logger.info("Auto save info: No data measured")
        else:
            self.app.show_info_message("Work aborted") 
            self.logger.info("Background worker aborted ")
 
    def _on_sig_worker_tick(self):
        self.app.show_info_message("Tick") 

    def _on_sig_worker_new_data(self):
        data = self.worker_thread.get_result()
        self.result.outputs = np.append(self.result.outputs, data.output)
        self.result.outputs_unit = data.output_unit
        self.result.amplitudes_unit = data.amplitude_unit
        # print(data.amplitude_off)
        self.result.amplitudes_off = np.append(self.result.amplitudes_off, data.amplitude_off)
        self.result.amplitudes_on = np.append(self.result.amplitudes_on, data.amplitude_on)
        self.result.phases_off = np.append(self.result.phases_off, data.phase_off)
        self.result.phases_on = np.append(self.result.phases_on, data.phase_on)
        self.sig_new_data_available.emit()

    def save_data(self):
        folder = self.settings.folder_name.value
        basename = self.settings.file_name_mask.value
        if nsf.util.fileutil.create_folder(folder):
            current_data = self.get_result()
            dataset = {}
            dataset[0] = current_data.outputs
            dataset[1] = current_data.amplitudes_on
            dataset[2] = current_data.amplitudes_off
            dataset[3] = current_data.phases_on
            dataset[4] = current_data.phases_off

            file_name = f"{basename}_{int(self.settings.file_index.value):03d}.csv"
            file_path = pathlib.Path(folder) / pathlib.Path(file_name)
            nsf.util.dataexport.savedata_txt(file_path, dataset, header="Voltage[V]; Amp_on[V]; Amp_off[V]; Phase_on[°]; Phase_off[°]", separator=";")
           
            self.settings.file_index.value += 1

            self.app.show_message(f"Data saved to: {str(file_path)}") 
        else:
            self.app.show_error_message(f"Error: Could not save data to folder: {str(folder)}") 

