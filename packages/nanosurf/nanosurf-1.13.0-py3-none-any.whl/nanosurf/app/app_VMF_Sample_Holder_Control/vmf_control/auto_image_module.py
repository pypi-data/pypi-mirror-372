""" The functional module where the functionality goes
Copyright Nanosurf AG 2021
License - MIT
"""

import pathlib
from PySide6.QtCore import Signal
import nanosurf as nsf
from vmf_control import auto_imaging_settings, auto_image_worker


class AutoImageModule(nsf.frameworks.qt_app.ModuleBase):

    sig_imaging_started = Signal()
    sig_imaging_start_requested = Signal()
    sig_imaging_stop_requested = Signal()
    sig_imaging_finished = Signal()

    # sig_data_invalid = Signal()

    """ Initialization functions of the module """

    def __init__(self, app: nsf.frameworks.qt_app.ApplicationBase, vmf_mod):
        super().__init__(app)
        self.app:nsf.frameworks.qt_app.ApplicationBase
        self.settings = auto_imaging_settings.AutoImageSettings()
        self.vmf_module = vmf_mod 
        self.vmf_module.sig_reference_move_ended.connect(self._on_end_of_reference_move)
        self.vmf_module.sig_target_field_ended.connect(self._on_end_of_move_to_field)
        self.worker_thread = None

    def do_start(self):
        self._setup_worker_thread()
        self._connect_to_properties()

    def do_stop(self):
        """ This function is called at module shutdown"""
        if self.worker_thread.is_thread_running():
            self.logger.info("Wait until worker thread has ended...")
            self.worker_thread.stop_thread(wait=True)
        del self.worker_thread
        self.worker_thread:auto_image_worker.AutoImageWorker = None # type: ignore

    """ Business logic of the module """
    def start_auto_imaging(self):
        if self.check_parameter():
            if self.prepare_destination_data_folder():
                self.sig_imaging_start_requested.emit()
                self._update_worker_parameter()
                self.worker_thread.start_worker()
            else:
                self.app.show_error_message(f"Cannot create folder to save measurement data at: {self.settings.save_to_path.value }")          

    def stop_auto_imaging(self):
        self.sig_imaging_stop_requested.emit()
        self.worker_thread.abort_worker()
    
    def is_measuring(self) -> bool:
        if  self.worker_thread is not None:
            return self.worker_thread.is_worker_running()
        else:
            return False
    
    """ Internal functions """

    def check_parameter(self) -> bool:
        ok = True
        if self.vmf_module.is_referenced():
            min_field, max_field = self.vmf_module.get_min_max_field()
            
            start_val = self.settings.auto_field_start.value 
            if start_val < min_field or start_val > max_field:
                self.app.show_error_message(f"Start field out of possible field range: Min field= {nsf.SciVal(min_field, 'T')}, max field= {nsf.SciVal(max_field, 'T')}")
                ok = False
            
            end_val = self.settings.auto_field_start.value + self.settings.auto_field_steps.value*self.settings.auto_field_stop.value
            if end_val < min_field or end_val > max_field:
                self.app.show_error_message(f"End field out of possible field range: Min field= {nsf.SciVal(min_field, 'T')}, max field= {nsf.SciVal(max_field, 'T')}")
                ok = False
        else:
            self.app.show_error_message("Sample Holder not referenced.")
            ok = False
        return ok    
        
    def  prepare_destination_data_folder(self) -> bool:
        done = True
        dest_dir = pathlib.Path(self.settings.save_to_path.value)
        if dest_dir.name != "":
            done = nsf.util.fileutil.create_folder(self.settings.save_to_path.value)
        return done

    def _on_end_of_reference_move(self):
        if self.vmf_module.is_last_cmd_ok():
            auto_screen_name = "Automation"
            if not self._has_screen(auto_screen_name):
                from vmf_control.auto_image_gui import AutoImageScreen
                self.app.add_screen(self, AutoImageScreen(auto_screen_name), auto_screen_name)
                self.app.appwindow.set_active_module_by_index(1)

    def _on_end_of_move_to_field(self, done:bool):
        pass

    def _connect_to_properties(self):
        """ Connect action functions to settings 
            The connected functions are called whenever a setting is changed (e.g. by GUI elements)
        """
        pass

    def _setup_worker_thread(self):
        """ Create the background worker task and connect to its event """
        self.worker_thread = auto_image_worker.AutoImageWorker(self.vmf_module)
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
        self.worker_thread.par_start_field = self.settings.auto_field_start.value
        self.worker_thread.par_stop_field = self.settings.auto_field_stop.value
        self.worker_thread.par_images_per_step = int(self.settings.auto_field_frame_rep.value)
        self.worker_thread.par_field_steps = int(self.settings.auto_field_steps.value)
        self.worker_thread.par_target_dir = self.settings.save_to_path.value
        self.worker_thread.par_target_file_mask = self.settings.data_file_mask.value

    def _on_sig_worker_started(self):
        self.sig_imaging_started.emit()

    def _on_sig_worker_finished(self):
        res = self.worker_thread.get_task_result()
        if res.msg != "":
            if res.ok:
                self.app.show_info_message(res.msg)
            else: 
                self.app.show_error_message(res.msg)
        self.sig_imaging_finished.emit()
 
    def _has_screen(self, screen: str) -> bool:
        found = False
        for screen_def in self.app.appwindow.list_of_screens:
            if screen_def.screen.name == screen:
                found = True
                break
        return found