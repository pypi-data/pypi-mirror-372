""" The functional module of the scan demo
Copyright Nanosurf AG 2021
License - MIT
"""

from PySide6.QtCore import Signal

import nanosurf as nsf
from scan_module import imaging_task, settings

class ScanModule(nsf.frameworks.qt_app.ModuleBase):

    sig_work_start_requested = Signal()
    sig_work_stop_requested = Signal()
    sig_work_active = Signal()
    sig_work_done = Signal()
    sig_new_data_available = Signal()
    sig_data_invalid = Signal()

    """ Initialization functions of the module """

    def __init__(self, app: nsf.frameworks.qt_app.ApplicationBase, gui):
        super().__init__(app, gui)
        """ Prepare here module settings which are stored and loaded from file by the app framework """
        self.app: nsf.frameworks.qt_app.ApplicationBase
        self.settings = settings.ScanSettings()
        self.result = settings.ScanResults()

    def do_start(self):
        """ This function is called once at startup of application
            Initialize here all module specific values.
        """
        self.setup_imaging_task()
        self.connect_to_properties()

    def do_stop(self):
        """ This function is called at module shutdown"""
        if self.imaging_task.is_thread_running():
            self.logger.info("Wait until worker thread has ended...")
            self.imaging_task.stop_thread(wait=True)

    def connect_to_properties(self):
        """ Connect action functions to settings 
            The connected functions are called whenever a setting is changed (e.g. by GUI elements)
        """
        self.settings.image_size.sig_value_changed.connect(self.update_worker_parameter)
        self.settings.time_per_line.sig_value_changed.connect(self.update_worker_parameter)
        self.settings.points_per_line.sig_value_changed.connect(self.update_worker_parameter)
        self.settings.channel_id.sig_value_changed.connect(self.update_worker_parameter)
        self.settings.show_backward.sig_value_changed.connect(self.update_worker_parameter)

    def setup_imaging_task(self):
        """ Create the background worker task and connect to its event """
        self.imaging_task = imaging_task.ScanFrameWorker(self)
        self.imaging_task.sig_worker_started.connect(self._on_sig_worker_started)
        self.imaging_task.sig_worker_finished.connect(self._on_sig_worker_finished)
        self.imaging_task.sig_new_data.connect(self._on_sig_worker_new_data)
        self.imaging_task.sig_tick.connect(self._on_sig_worker_tick)
        self.imaging_task.start_thread()

    """ Now the business logic of the module """
        
    def start_worker(self):
        if not self.imaging_task.is_worker_running():
            self.update_worker_parameter()
            self.sig_work_start_requested.emit()
            self.imaging_task.start_worker()

    def stop_worker(self):
        if self.imaging_task.is_worker_running():
            self.sig_work_stop_requested.emit()
            self.imaging_task.abort_worker(wait=True)
    
    def is_worker_busy(self) -> bool:
        return self.imaging_task.is_worker_running()

    def get_result(self) -> settings.ScanResults:
        return self.result

    def get_worker_result(self) -> imaging_task.ScanData:
        return self.imaging_task.get_task_result()

    def update_worker_parameter(self):
        self.imaging_task.par_image_size = self.settings.image_size.value
        self.imaging_task.par_points_per_line = self.settings.points_per_line.value
        self.imaging_task.par_time_per_line = self.settings.time_per_line.value
        self.imaging_task.par_channel_id = self.settings.channel_id.value

    def do_analysis(self):
        data = self.imaging_task.get_task_result()
        result_valid = True

        if result_valid:
            self.sig_new_data_available.emit()
        else:
            self.app.show_error_message(f"Could not analyze data") 
            self.sig_data_invalid.emit()

    """ worker thread state handling """

    def _on_sig_worker_started(self):
        self.app.show_info_message("Start Scanning ...") 
        self.logger.info("Background worker started")
        self.sig_data_invalid.emit()
        self.sig_work_active.emit()

    def _on_sig_worker_finished(self):
        self.sig_work_done.emit()
        if not self.imaging_task.is_worker_aborted():
            self.app.show_info_message("Scan finished") 
            self.logger.info("Background worker finished ")
            self.do_analysis()
        else:
            self.app.show_info_message("Scanning aborted") 
            self.logger.info("Background worker aborted ")
 
    def _on_sig_worker_tick(self):
        self.app.show_info_message("Tick") 

    def _on_sig_worker_new_data(self):
        self.sig_new_data_available.emit()
