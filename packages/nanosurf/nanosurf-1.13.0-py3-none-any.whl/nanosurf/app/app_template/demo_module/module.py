""" The functional module where the functionality goes
Copyright Nanosurf AG 2021
License - MIT
"""
import numpy as np
from PySide6.QtCore import Signal
import nanosurf as nsf
from demo_module import settings, worker_task

class DemoModule(nsf.frameworks.qt_app.ModuleBase):

    sig_work_start_requested = Signal()
    sig_work_stop_requested = Signal()
    sig_work_active = Signal()
    sig_work_done = Signal()
    sig_new_data_available = Signal()
    sig_data_invalid = Signal()

    """ Initialization functions of the module """

    def __init__(self, app: nsf.frameworks.qt_app.ApplicationBase):
        super().__init__(app)
        self.app:nsf.frameworks.qt_app.ApplicationBase
        """ Prepare here module settings which are stored and loaded from file by the app framework """
        self.settings = settings.DemoSettings()
        self.result = settings.DemoResults()

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
        self.settings.repetitions.sig_value_changed.connect(self.update_worker_parameter)
        self.settings.time_per_repetition.sig_value_changed.connect(self.update_worker_parameter)
        self.settings.send_ticks.sig_value_changed.connect(self.update_worker_parameter)

    def setup_worker_thread(self):
        """ Create the background worker task and connect to its event """
        self.worker_thread = worker_task.MyWorker(self)
        self.worker_thread.sig_worker_started.connect(self._on_sig_worker_started)
        self.worker_thread.sig_worker_finished.connect(self._on_sig_worker_finished)
        self.worker_thread.sig_new_data.connect(self._on_sig_worker_new_data)
        self.worker_thread.sig_tick.connect(self._on_sig_worker_tick)
        self.worker_thread.start_thread()

    """ Now the business logic of the module """
        
    def start_worker(self):
        self.app.clear_message()
        if not self.worker_thread.is_worker_running():
            self.update_worker_parameter()
            self.sig_work_start_requested.emit()
            self.worker_thread.start_worker()

    def stop_worker(self):
        if self.worker_thread.is_worker_running():
            self.sig_work_stop_requested.emit()
            self.worker_thread.abort_worker(wait=True)
    
    def is_worker_busy(self) -> bool:
        return self.worker_thread.is_worker_running()

    def get_result(self) -> settings.DemoResults:
        return self.result

    def get_worker_result(self) -> worker_task.MyWorkerData:
        return self.worker_thread.get_task_result()

    def update_worker_parameter(self):
        self.worker_thread.par_repetition = self.settings.repetitions.value
        self.worker_thread.par_send_ticks = self.settings.send_ticks.value
        self.worker_thread.par_time_per_repetition = self.settings.time_per_repetition.value
        self.worker_thread.par_time_between_ticks = 0.01
        self.worker_thread.par_plot_func_id = self.settings.plot_func_id

    def do_analysis(self):
        data = self.worker_thread.get_task_result()

        if data.last_index >= 0: 
            arr = np.array(data.value)
            mean = np.mean(arr)
            self.result.mean_value = mean
            self.result.last_data = data.value[-1]
            self.result.number_of_data_points = data.last_index
            result_valid = True
        else:
            result_valid = False

        if result_valid:
            self.sig_new_data_available.emit()
        else:
            self.app.show_error_message(f"Could not analyze data") 
            self.sig_data_invalid.emit()

    """ worker thread state handling """

    def _on_sig_worker_started(self):
        self.app.show_message("Working ...") 
        self.logger.info("Thread started to work")
        self.sig_data_invalid.emit()
        self.sig_work_active.emit()

    def _on_sig_worker_finished(self):
        self.sig_work_done.emit()
        if not self.worker_thread.is_worker_aborted():
            self.app.show_info_message("Work done") 
            self.logger.info("Background worker finished ")
            self.do_analysis()
        else:
            self.app.show_info_message("Work aborted") 
            self.logger.info("Background worker aborted ")
 
    def _on_sig_worker_tick(self):
        self.app.show_info_message("Tick") 

    def _on_sig_worker_new_data(self):
        self.do_analysis()
