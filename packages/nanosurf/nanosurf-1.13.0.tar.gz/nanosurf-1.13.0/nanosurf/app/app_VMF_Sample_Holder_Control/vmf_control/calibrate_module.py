""" The functional module where the functionality goes
Copyright Nanosurf AG 2021
License - MIT
"""
import numpy as np
import pathlib
from PySide6.QtCore import Signal
import nanosurf as nsf
from vmf_control import vmf_module, calibrate_settings, calibrate_worker


class CalibrateModule(nsf.frameworks.qt_app.ModuleBase):

    sig_calibration_started = Signal()
    sig_calibrate_start_requested = Signal()
    sig_calibrate_stop_requested = Signal()
    sig_calibration_finished = Signal()

    """ Initialization functions of the module """

    def __init__(self, app: nsf.frameworks.qt_app.ApplicationBase, vmf_mod):
        super().__init__(app)
        self.app:nsf.frameworks.qt_app.ApplicationBase
        self.settings = calibrate_settings.CalibrateSettings()
        self.vmf_module: vmf_module.VMFModule = vmf_mod 
        self.vmf_module.sig_reference_move_ended.connect(self._on_end_of_reference_move)
        self.worker_thread:calibrate_worker.CalibrateWorker = None # type: ignore

    def do_start(self):
        self._setup_worker_thread()
        self._connect_to_properties()

    def do_stop(self):
        """ This function is called at module shutdown"""
        if self.worker_thread.is_thread_running():
            self.logger.info("Wait until worker thread has ended...")
            self.worker_thread.stop_thread(wait=True)
        del self.worker_thread
        self.worker_thread = None # type: ignore

    """ Business logic of the module """
    def start_calibrating(self):
        if self.prepare_destination_data_folder():
            self.sig_calibrate_start_requested.emit()
            self._update_worker_parameter()
            self.worker_thread.start_worker()
        else:
            self.app.show_error_message(f"Cannot create folder to save measurement data at: {self.settings.save_to_path.value }")          

    def stop_calibrating(self):
        self.sig_calibrate_stop_requested.emit()
        self.worker_thread.abort_worker()
    
    def is_measuring(self) -> bool:
        if  self.worker_thread is not None:
            return self.worker_thread.is_worker_running()
        else:
            return False
    
    """ Internal functions """


    def  prepare_destination_data_folder(self) -> bool:
        done = True
        dest_dir = pathlib.Path(self.settings.save_to_path.value)
        if dest_dir.name != "":
            done = nsf.util.fileutil.create_folder(self.settings.save_to_path.value)
        return done

    def _on_end_of_reference_move(self):
        if self.vmf_module.is_last_cmd_ok():
            if self.app.settings._is_calibration_panel_shown:
                calibrate_screen_name = "Calibrate"
                if not self._has_screen(calibrate_screen_name):
                    from vmf_control.calibrate_gui import CalibrateScreen
                    self.app.add_screen(self, CalibrateScreen(calibrate_screen_name), calibrate_screen_name)
                    self.app.appwindow.set_active_module_by_index(1)

    def _on_end_of_move_to_field(self, done:bool):
        pass

    def _connect_to_properties(self):
        """ Connect action functions to settings 
            The connected functions are called whenever a setting is changed (e.g. by GUI elements)
        """
        # self.settings.repetitions.sig_value_changed.connect(self.update_worker_parameter)
        # self.settings.time_per_repetition.sig_value_changed.connect(self.update_worker_parameter)
        # self.settings.send_ticks.sig_value_changed.connect(self.update_worker_parameter)

    def _setup_worker_thread(self):
        """ Create the background worker task and connect to its event """
        self.worker_thread = calibrate_worker.CalibrateWorker(self.vmf_module)
        self.worker_thread.sig_worker_started.connect(self._on_sig_worker_started)
        self.worker_thread.sig_worker_finished.connect(self._on_sig_worker_finished)
        self.worker_thread.start_thread()

    def _start_worker(self):
        self.app.clear_message()
        if not self.worker_thread.is_worker_running():
            self._update_worker_parameter()
            self.worker_thread.start_worker()

    def _stop_worker(self):
        if self.worker_thread.is_worker_running():
            self.worker_thread.abort_worker(wait=True)
    
    def _is_worker_busy(self) -> bool:
        return self.worker_thread.is_worker_running()

    def _update_worker_parameter(self):
        self.worker_thread.par_config_index = int(self.settings.calibrate_configuration.value)
        self.worker_thread.par_num_steps = int(self.settings.cal_steps.value)
        self.worker_thread.par_target_dir = self.settings.save_to_path.value
        self.worker_thread.par_target_file_mask = self.settings.data_file_mask.value

    def _on_sig_worker_started(self):
        self.sig_calibration_started.emit()

    def _on_sig_worker_finished(self):
        res = self.worker_thread.get_task_result()
        if res.msg != "":
            if res.ok:
                self.app.show_info_message(res.msg)
                self.do_analysis()
            else: 
                self.app.show_error_message(res.msg)
        self.sig_calibration_finished.emit()
 
    def _has_screen(self, screen: str) -> bool:
        found = False
        for screen_def in self.app.appwindow.list_of_screens:
            if screen_def.screen.name == screen:
                found = True
                break
        return found
    
    def do_analysis(self):
        ref_field_in_T = self.worker_thread.ref_measurement
        uncal_adc_values_in_V = self.worker_thread.un_cal_measurement
        
        fit_degree = 2   
        fit_param = np.polyfit(x=ref_field_in_T, y=uncal_adc_values_in_V, deg = fit_degree)

        # y = offset + x*slope + x^2*square
        if fit_degree == 1: 
            offset = fit_param[1]
            slope = fit_param[0]
            square = 0.0
        elif fit_degree == 2:
            offset = fit_param[2]
            slope = fit_param[1]
            square = fit_param[0]
        else:
            self.vmf_module.app.show_error_message("error fit degree")
            offset = 0.0
            slope = 0.0
            square = 0.0

        print(f"{offset=},{slope=},{square=},")

        calib_adc_values_in_T = []
        for i in range(len(uncal_adc_values_in_V)):
            x = uncal_adc_values_in_V[i]
            calib_adc_values_in_T.append(offset + x*slope + x*x*square)

        active_config = self.vmf_module.worker_thread.vmf_controller._get_active_config()
        active_config.cal_values = [offset, slope, square]
        self.vmf_module.worker_thread.vmf_controller._set_active_config(active_config)
