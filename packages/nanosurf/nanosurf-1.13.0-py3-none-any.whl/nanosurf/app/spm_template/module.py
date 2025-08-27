""" The functional module where the functionality goes
Copyright Nanosurf AG 2021
License - MIT
"""
import pathlib
import numpy as np
from scipy import io as sio
from typing import Tuple
from PySide6.QtCore import Signal

import nanosurf as nsf
from nanosurf.lib.spm.spm_app import SPMApp
import settings, measure_task

class WorkerModule(nsf.frameworks.qt_app.ModuleBase):

    sig_work_start_requested = Signal()
    sig_work_stop_requested = Signal()
    sig_work_active = Signal()
    sig_work_done = Signal()
    sig_new_data_available = Signal()
    sig_data_invalid = Signal()

    #  Initialization functions of the module 

    def __init__(self, app: nsf.frameworks.qt_app.ApplicationBase, gui):
        super().__init__(app, gui)
        self.app:nsf.frameworks.qt_app.ApplicationBase # give pylance a type hint
        self.settings = settings.Settings()
        self.results = settings.ModuleResults()
        self.spm_app:SPMApp = None
        self.spm = None
        self.lu = None

    def do_start(self):
        # This function is called once at startup of application 

        # do this if connection to controller shall be checked at startup 
        # and used by the worker module (and not only by the worker_task)
        if self._connect_to_controller():
            self.app.show_info_message("Connected to controller")

        self.worker_thread = measure_task.MeasureTask(self)
        self.worker_thread.sig_worker_started.connect(self._on_sig_worker_started)
        self.worker_thread.sig_worker_finished.connect(self._on_sig_worker_finished)
        self.worker_thread.sig_new_result.connect(self._on_sig_worker_new_data)
        self.worker_thread.start_thread()

    def do_stop(self):
        # This function is called once at application shutdown 
        if self.worker_thread.is_thread_running():
            self.worker_thread.stop_thread(wait=True)
        self._disconnect_from_controller()

    """ Now the main logic of the module ----------------------------------------- 

        start_background_task()  - This function is called by the GUI "Start" button.
                                   Define here the parameters of the task. 

        do_at_every_new_data_from_worker_task() - This is called from sig_new_result by the worker_thread. 
                                                  Code here what must be done each time the task has new data

        do_at_end_of_worker_task() - This is called from sig_worker_finished by the worker_thread. 
                                     Code here what must be done at the end of the task
    """    
        
    def start_background_task(self):
        """ This function is called by the GUI "Start" button 
            Define here the parameters of the task.
        """
        self.app.clear_message()
        if not self.worker_thread.is_worker_running():

            # prepare all parameters for background task
            self.worker_thread.par_sample_points = self.settings.repetitions.value
            self.worker_thread.par_time_per_sample = self.settings.time_per_repetition.value
            self.worker_thread.par_monitor_id = self.settings.channel_id.value
            self.worker_thread.par_continuous_rolling = self.settings.continuous_rolling.value

            # start task
            self.sig_work_start_requested.emit()
            self.worker_thread.start_worker()

    def do_at_every_new_data_from_worker_task(self):
        """ This is called from sig_new_result by the worker_thread.  
            Code here what must be done each time the task has new data
        """
        # example what could be done with new data. 
        # At the end of processing inform the gui about new data by elf.sig_data_invalid.emit()

        new_data = self.worker_thread.get_task_result() 
        if new_data.last_index >= 0: 
            if new_data.last_index == 0:
                self.results.mean_value.set_unit(new_data.monitor_stream.channels[0].unit)
                self.results.last_value.set_unit(new_data.monitor_stream.channels[0].unit)

            self.results.mean_value.set_value(np.mean(new_data.monitor_stream.channels[0].value))
            self.results.last_value.set_value(new_data.monitor_stream.channels[0].value[new_data.last_index])
            self.results.data_stream = new_data.monitor_stream
            self.results.last_index  = new_data.last_index
            self.sig_new_data_available.emit()
        else:
            self.app.show_error_message(f"No data from task") 
            self.sig_data_invalid.emit()

    def do_at_end_of_worker_task(self):
        """ This is called from sig_worker_finished by the worker_thread. 
            Code here what must be done at the end of the task
        """
        # nothing to do in this example
        pass

    def save_stream_to_file(self, filename:pathlib.Path) -> bool:
        """ Save result in matlab style"""
        done = False
        try:
            stream = self.results.data_stream
            mat_file_rows = {
                "Time" : stream.x.value,
                "Data" : stream.channels[0].value,
            }
            sio.savemat(filename, mat_file_rows)
            done = True
        except Exception:
            pass
        return done

    def load_stream_from_file(self, filename:pathlib.Path) -> Tuple[bool, nsf.SciStream]:
        done = False
        stream:nsf.SciStream = None
        try:
            loaded_dict = sio.loadmat(filename)
            stream = nsf.SciStream(source=loaded_dict["Time"][0])
            stream.channels[0].value = loaded_dict["Data"][0]
            done = True
        except Exception:
            pass
        return done, stream

    """ worker thread state handling - in many use cases this can by left just like this"""

    def stop_background_task(self):
        if self.worker_thread.is_worker_running():
            self.sig_work_stop_requested.emit()
            self.worker_thread.abort_worker(wait=True)
    
    def is_task_busy(self) -> bool:
        return self.worker_thread.is_worker_running()

    def _on_sig_worker_new_data(self):
        self.do_at_every_new_data_from_worker_task()
        self.sig_new_data_available.emit()

    def _on_sig_worker_started(self):
        self.app.show_info_message("Measuring ...") 
        self.sig_data_invalid.emit()
        self.sig_work_active.emit()

    def _on_sig_worker_finished(self):
        self.sig_work_done.emit()
        if not self.worker_thread.is_worker_aborted():
            self.app.show_info_message("Measurement done") 
            self.do_at_end_of_worker_task()
        else:
            self.app.show_info_message("Measurement aborted") 

    """ Connect / disconnect to SPM controller or Studio """            

    def _connect_to_controller(self) -> bool:
        ok = self.spm_app is not None
        if not ok:
            self.spm_app = SPMApp()
            self.spm_ctrl = self.spm_app.connect()
            if self.spm_ctrl is not None:
                if self.spm_app.is_scripting_enabled():
                    self.spm = self.spm_ctrl.spm
                    self.lu = self.spm.lu
                    ok = True
                else:
                    self.app.show_error_message("Error: Scripting interface is not enabled")
            else:
                self.app.show_error_message("Error: Could not connect to controller. Check if software is started")
        return ok

    def _disconnect_from_controller(self):
        if self.lu is not None:
            del self.lu
            self.lu = None
        if self.spm is not None:
            del self.spm
            self.spm = None
        if self.spm_app is not None:
            del self.spm_app
            self.spm_app = None


