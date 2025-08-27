""" The long lasting worker thread as demo - just wait some time and create data periodically
Copyright Nanosurf AG 2021
License - MIT
"""

import time
import pathlib
from PySide6.QtCore import Signal
import nanosurf as nsf
from vmf_control import vmf_module

class AutoImageWorkerData():
    def __init__(self) -> None:
        self.ok = False
        self.msg = ""

class AutoImageWorker(nsf.frameworks.qt_app.nsf_thread.SPMWorker):
    """ This class implements the long lasting activity in the background to not freeze the gui """

    sig_tick = Signal() # is emitted if par_send_tick is True
    sig_new_field= Signal(float) # is emitted each time a new field value is available
    sig_new_frame= Signal(float) # is emitted each time a new field value is available

    """ parameter for the background work"""
    par_start_field = 0.0
    par_stop_field = 0.0
    par_field_steps = 2
    par_images_per_step = 1
    par_time_between_ticks = 0.3
    par_target_dir = pathlib.Path("")
    par_target_file_mask = pathlib.Path("")
    _sig_message = Signal(str, int)

    def __init__(self, vmf_module: 'vmf_module.VMFModule'):
        super().__init__(vmf_module)
        self.vmf_module = vmf_module

    def do_work(self):
        """ This is the working function for the long task"""
        self.logger.info("start_Auto_Image_Work")
        self.result = AutoImageWorkerData()
        if self.connect_to_controller():

            do_capture_measurement = self.par_target_dir.name != "" and self.par_target_file_mask.name != ""

            try:
                if do_capture_measurement:
                    self.spm.application.SetGalleryHistoryDirectoryPath(str(self.par_target_dir))
                    self.spm.application.SetGalleryHistoryFilenameIndex(0)
                    self.spm.application.Scan.AutoCapture = True
                else:
                    self.spm.application.Scan.AutoCapture = False
            except Exception as e:
                self.logger.error(f"Could not set destination directory. Reason: {e}")
                self.send_error_message(f"Could not set destination directory: {self.par_target_dir}")
                return 
            
            if self.par_field_steps < 2:
                self.logger.error(f"Internal Error: Minimal number of steps must be 2. Given: {self.par_field_steps}")
                self.send_error_message(f"Internal Error: Minimal number of steps must be 2. Given: {self.par_field_steps}")
                return 

            self.spm_scan = self.spm.application.Scan

            # step through fields, measure and store 
            field_change_per_step = (self.par_stop_field - self.par_start_field) / ( self.par_field_steps - 1)
            for field_step in range(self.par_field_steps):
                if self.is_stop_request_pending():
                    break    
            
                current_field = self.par_start_field + field_step*field_change_per_step
                self.vmf_module.start_move_to_field(current_field)
                while self.vmf_module.is_moving():
                    time.sleep(0.5)
                    if self.is_stop_request_pending():
                        self.vmf_module.stop_moving()
                        while self.vmf_module.is_moving():
                            time.sleep(0.5)
                        break
                        
                if not self.vmf_module.is_last_cmd_ok():
                    self.result.ok = False
                    self.result.msg = f"Could not reached target field. {nsf.SciVal(current_field,'T')}"
                    self.abort_worker(wait=False)
                
                if do_capture_measurement:
                    mask = f"{self.par_target_file_mask}_{nsf.SciVal(self.vmf_module.get_last_h_field(),'T')}_[INDEX]".replace(" ", "_")
                    self.spm.application.SetGalleryHistoryFilenameMask(mask)

                for image_no in range(self.par_images_per_step):
                    if self.is_stop_request_pending():
                        break

                    #first stop a running scan
                    if self.spm_scan.IsScanning:
                        self.spm_scan.Stop()
                        while self.spm_scan.IsScanning:
                            time.sleep(0.1)

                    #start new imaging frame
                    self._points_per_line = self.spm_scan.Lines
                    self.spm_scan.StartFrameUp()

                    # wait until frame is done
                    while self.spm_scan.IsScanning and not self.is_stop_request_pending():
                        time.sleep(self.par_time_between_ticks)
                        self.sig_tick.emit()
                        self.send_info_message(f"Measuring step {field_step+1}/{self.par_field_steps} at {nsf.sci_val.convert.to_string(current_field,'T', precision=2)}, Image: {image_no+1}/{self.par_images_per_step}. Scan line: {self.spm_scan.Currentline}")

                    self.send_info_message("Done.")
                    self.spm_scan.Stop()
                    if self.spm_scan.IsScanning:
                        self.spm_scan.Stop()
                        while self.spm_scan.IsScanning:
                            time.sleep(0.1)

            if not self.is_stop_request_pending():
                self.result.ok = True
                self.result.msg = "Measurements done."
        else:
            self.result.ok = False
            self.result.msg = "Could not connect to SPM Software"
            
    def get_task_result(self) -> AutoImageWorkerData:
        return self.result
