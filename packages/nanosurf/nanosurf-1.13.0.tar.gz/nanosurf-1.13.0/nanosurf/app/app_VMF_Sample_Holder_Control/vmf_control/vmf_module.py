""" The functional module where the functionality goes
Copyright Nanosurf AG 2021
License - MIT
"""
import typing
from PySide6.QtCore import Signal, QTimer

import nanosurf as nsf
from vmf_control import vmf_settings, vmf_worker


class VMFModule(nsf.frameworks.qt_app.ModuleBase):

    sig_work_start_requested = Signal()
    sig_work_stop_requested = Signal()

    sig_connecting_started = Signal()
    sig_connecting_done = Signal()
    sig_h_field_available = Signal(float)
    sig_target_field_started = Signal()
    sig_target_field_ended = Signal(bool)
    sig_target_pos_started = Signal()
    sig_target_pos_ended = Signal(bool)
    sig_reference_state_changed = Signal()
    sig_reference_move_started = Signal()
    sig_reference_move_ended = Signal(bool)
    sig_save_calibration_started = Signal()
    sig_save_calibration_ended = Signal(bool)
    sig_load_calibration_started = Signal()
    sig_load_calibration_ended = Signal(bool)
    sig_init_controller_started = Signal()
    sig_init_controller_ended = Signal(bool)
    sig_init_sample_holder_started = Signal()
    sig_init_sample_holder_ended = Signal(bool)
    
    # sig_data_invalid = Signal()

    """ Initialization functions of the module """

    def __init__(self, app: nsf.frameworks.qt_app.ApplicationBase):
        super().__init__(app)
        self.app:nsf.frameworks.qt_app.ApplicationBase
        """ Prepare here module settings which are stored and loaded from file by the app framework """
        self.settings = vmf_settings.VMFSettings()
        self.result = vmf_settings.VMFResults()
        self.last_h_field = 0.0
        self._vmf_controller_sn_number = ""
        self._vmf_sample_holder_sn_number = ""
        self._vmf_ready = False
        self._is_moving = False
        self._poll_timer = QTimer()
        self.poll_timing = 500
        self.list_of_known_sample_holder_configurations = ["2mm Gap","4mm Gap", "6mm Gap", "8mm Gap", "10mm Gap", "Out-of-plane"]
        self._poll_timer.timeout.connect(self._on_end_of_poll_timer)
        self.sig_h_field_available.connect(self._on_new_h_field_available)
        self.sig_connecting_done.connect(self._on_connecting_done)

    def do_start(self):
        """ This function is called once at startup of application
            Initialize here all module specific values.
        """
        self._setup_worker_thread()
        self._connect_to_properties()

    def do_stop(self):
        if self._poll_timer:
            self._poll_timer.stop()
            del self._poll_timer
        self._poll_timer = None

        """ This function is called at module shutdown"""
        if self.worker_thread is not None:
            if self.worker_thread.is_thread_running():
                self.logger.info("Wait until worker thread disconnected...")
                self.worker_thread.start_worker(command=vmf_worker.VFMWorkerCmd.Disconnect)
                self.worker_thread.wait_end_of_worker()
                self.logger.info("Wait until worker thread has ended...")
                self.worker_thread.stop_thread(wait=True)
            del self.worker_thread
        self.worker_thread = None

    """ Business logic of the module """

    def start_connect_to_vmf_controller(self):
        if self.worker_thread is not None:
            ai_port_in_use = 1 if self.app.settings._is_in_setup_mode else -1 # type: ignore
            auto_setup = False if self.app.settings._is_in_setup_mode else True # type: ignore
            self.worker_thread.start_worker(command=vmf_worker.VFMWorkerCmd.Connect, 
                call_setup=auto_setup, 
                ai_port=ai_port_in_use, 
                restore_last_motor_pos=True, 
            )
        
    def is_vmf_ready(self) -> bool:
        return self._vmf_ready
    
    def vmf_controller_sn_number(self):
        """ return the serial number of the connected vmf_controller or empty string is not connected """
        return self._vmf_controller_sn_number
    
    def vmf_sample_holder_sn_number(self):
        """ return the serial number of the connected sample holder or empty string is not connected """
        return self._vmf_sample_holder_sn_number
    
    def get_last_message(self) -> str:
        if self.worker_thread is not None:
            return self.worker_thread.vmf_controller.get_message()
        return ""

    def get_result(self) -> vmf_settings.VMFResults:
        return self.result

    def start_reading_h_field(self):
        if self._poll_timer:
            self._poll_timer.start(self.poll_timing)

    def stop_reading_h_field(self):
        if self._poll_timer:
            self._poll_timer.stop()

    def start_move(self, direction_forward: bool, speed:float):
        if self.worker_thread is not None:
            self._is_moving = True
            self.worker_thread.start_worker(command=vmf_worker.VFMWorkerCmd.Move, forward=direction_forward, speed=speed)
            self.app.show_info_message("Moving...")

    def start_move_to_field(self, target_field:float):
        if self.worker_thread is not None:
            self.app.show_info_message("Adjusting field...")
            self._is_moving = True
            self.sig_target_field_started.emit()
            self.worker_thread.start_worker(command=vmf_worker.VFMWorkerCmd.Move_to_Field, target_field=target_field)

    def start_move_to_pos(self, target_pos:float, speed:float):
        if self.worker_thread is not None:
            self.app.show_info_message("Adjusting position...")
            self._is_moving = True
            self.sig_target_pos_started.emit()
            self.worker_thread.start_worker(command=vmf_worker.VFMWorkerCmd.Move_to_Pos, target_pos=target_pos, speed=speed)

    def start_reference_move(self):
        if self.worker_thread is not None:
            self.app.show_info_message("Referencing...")
            self._is_moving = True
            self.sig_reference_move_started.emit()
            self.worker_thread.start_worker(command=vmf_worker.VFMWorkerCmd.Reference_move)

    def stop_moving(self):
        if self.worker_thread is not None:
            if not self.worker_thread.is_worker_aborted():
                self.worker_thread.abort_worker()
                self.app.show_info_message("")
                self._is_moving = False

    def is_moving(self) -> bool:
        return self._is_moving
    
    def is_last_cmd_ok(self) -> bool:
        if self.worker_thread:
            res = self.worker_thread.get_task_result()
            return res.cmd_finished_ok
        else:
            return False
    
    def is_referenced(self) -> bool:
        if self.worker_thread is not None and self.worker_thread.vmf_controller is not None:
            return self.worker_thread.vmf_controller.is_referenced()
        else:
            return False
    
    def is_motor_position_known(self) -> bool:
        if self.worker_thread is not None and self.worker_thread.vmf_controller is not None:
            return self.worker_thread.vmf_controller.is_motor_pos_defined()
        else:
            return False
    
    def get_min_max_field(self) -> typing.Tuple[float, float]:
        if self.worker_thread is not None and self.worker_thread.vmf_controller is not None:
            # let user only reach +-90% of full range, this make sure the end value is really reachable with the motor
            # second, it  limits the time needed to reach avery large field close to the max due to the sine-wave behavior of the field vs. position 
            h_min, h_max = self.worker_thread.vmf_controller.get_reference_field_min_max()
            h_min *= 0.97
            h_max *= 0.97
            return (h_min, h_max)
        else:
            return (1,-1)
    
    def get_last_h_field(self) -> float:
        return self.last_h_field 
    
    def get_last_motor_pos_normalized(self) -> float:
        if self.worker_thread is not None and self.worker_thread.vmf_controller is not None:
            cur_pos = self.worker_thread.vmf_controller.get_current_motor_pos_normalized()
            return cur_pos
        else:
            return 0.0
    
    def get_sample_holder_configurations(self) -> typing.List[str]:
        return self.list_of_known_sample_holder_configurations

    def start_store_calibration_to_sample_holder(self):
        if self.worker_thread is not None:
            self.app.show_info_message("Saving data to EEPROM...")
            self.sig_save_calibration_started.emit()
            self.worker_thread.start_worker(command=vmf_worker.VFMWorkerCmd.Save_Calibration)

    def start_initialize_controller(self):
        if self.worker_thread is not None:
            self.app.show_info_message("Initialize controller...")
            self.sig_init_controller_started.emit()
            self.worker_thread.start_worker(command=vmf_worker.VFMWorkerCmd.Initialize_VMF_Controller, serial_no = self._vmf_controller_sn_number)

    def start_initialize_sample_holder(self):
        if self.worker_thread is not None:
            self.app.show_info_message("Initialize sample-holder...")
            self.sig_init_sample_holder_started.emit()
            self.worker_thread.start_worker(command=vmf_worker.VFMWorkerCmd.Initialize_VMF_SampleHolder, serial_no = self._vmf_sample_holder_sn_number)

    def start_load_calibration_from_sample_holder(self):
        if self.worker_thread is not None:
            self.app.show_info_message("Loading data from EEPROM...")
            self.sig_load_calibration_started.emit()
            self.worker_thread.start_worker(command=vmf_worker.VFMWorkerCmd.Load_Calibration)

    def start_load_calibration_from_file(self):
        if self.worker_thread is not None:
            file = nsf.util.fileutil.ask_open_file("Select a calibration file to load", start_dir=None, suffix_mask="vmf_calib")
            if file is not None:
                self.app.show_info_message("Loading data from file...")
                self.sig_load_calibration_started.emit()
                self.worker_thread.start_worker(command=vmf_worker.VFMWorkerCmd.Load_Calibration_from_File, file_name=str(file))

    def start_save_calibration_to_file(self):
        if self.worker_thread is not None:
            file = nsf.util.fileutil.ask_save_file("Select a file to store the calibration", target_dir=None, suffix_mask="*.vmf_calib")
            if file is not None:
                self.app.show_info_message("Saving data to file...")
                self.worker_thread.start_worker(command=vmf_worker.VFMWorkerCmd.Save_Calibration_to_File, file_name=str(file))

    """ Internal functions """
    def _on_end_of_poll_timer(self):
        if self.worker_thread is not None:
            if not self.worker_thread.is_worker_running():
                self.worker_thread.sig_new_field_cmd.emit()
            elif not self.worker_thread.is_thread_finish_done:
                if self._poll_timer is not None:
                    self._poll_timer.start(self.poll_timing)

    def _on_new_h_field_available(self, field:float):
        if self._poll_timer is not None:
            self._poll_timer.start(self.poll_timing)

    def _connect_to_properties(self):
        self.settings.sample_holder_config.sig_value_changed.connect(self.on_sample_holder_calibration_change)

    def _setup_worker_thread(self):
        """ Create the background worker task and connect to its event """
        self.worker_thread = vmf_worker.VMFWorker(self)
        self.worker_thread.sig_worker_finished.connect(self._handle_end_of_command)
        self.worker_thread.sig_new_field.connect(self._on_sig_worker_new_field)
        self.worker_thread.sig_tick.connect(self._on_sig_worker_tick)
        self.worker_thread.start_thread()

    def _start_worker(self):
        #self.app.clear_message()
        if self.worker_thread:
            if not self.worker_thread.is_worker_running():
                self.sig_work_start_requested.emit()
                self.worker_thread.start_worker()

    def _stop_worker(self):
        if self.worker_thread:
            if self.worker_thread.is_worker_running():
                self.sig_work_stop_requested.emit()
                self.worker_thread.abort_worker(wait=True)
    
    def _is_worker_busy(self) -> bool:
        if self.worker_thread:
            return self.worker_thread.is_worker_running()
        else:
            return False

    def _get_worker_result(self) -> vmf_worker.VMFWorkerData:
        if self.worker_thread:
            return self.worker_thread.get_task_result()
        else:
            return vmf_worker.VMFWorkerData()

    def _on_sig_worker_tick(self):
        self.app.show_info_message("Tick") 

    def _on_sig_worker_new_field(self, current_h_field:float):
        self.last_h_field = current_h_field
        self.sig_h_field_available.emit(current_h_field)

    def _on_connecting_done(self):
        if self.is_vmf_ready():
            self.on_sample_holder_calibration_change()
            if not self.app.settings._is_in_setup_mode: # type: ignore
                self.start_reading_h_field()

    def on_sample_holder_calibration_change(self):
        cur_index = self.settings.sample_holder_config.value
        try:
            if self.worker_thread is not None:
                if self.worker_thread.vmf_controller is not None:
                    self.worker_thread.vmf_controller.configuration_select(cur_index)
        except IndexError:
            self.app.show_error_message("No calibration stored for selected configuration")
            self.settings.sample_holder_config.value = 0
        self.sig_reference_state_changed.emit()

    def _handle_end_of_command(self):
        # check if not in shutdown phase of application
        if self.worker_thread is None or self.worker_thread.is_thread_finish_done:
            return
        
        res = self.worker_thread.get_task_result()
        if res.last_cmd == vmf_worker.VFMWorkerCmd.Connect:
            self._vmf_controller_sn_number = self.worker_thread.vmf_controller_serial_no if self.worker_thread.vmf_controller else ""
            self._vmf_sample_holder_sn_number = self.worker_thread.vmf_holder_serial_no if self.worker_thread.vmf_controller else ""
            self._vmf_ready = (self._vmf_controller_sn_number not in ["","124-xx-xxx"]) and (self._vmf_sample_holder_sn_number not in ["", "125-xx-xxx"])
            self.sig_connecting_done.emit()
            if self.is_referenced():
                self.sig_reference_move_ended.emit(True)

        elif res.last_cmd == vmf_worker.VFMWorkerCmd.Disconnect:
            self._is_moving = False

        elif res.last_cmd == vmf_worker.VFMWorkerCmd.Move_to_Field:
            res = self.worker_thread.get_task_result()
            self.app.show_info_message(res.cmd_msg)
            self._is_moving = False
            self.sig_target_field_ended.emit(res.cmd_finished_ok)

        elif res.last_cmd == vmf_worker.VFMWorkerCmd.Move_to_Pos:
            res = self.worker_thread.get_task_result()
            self.app.show_info_message(res.cmd_msg)
            self._is_moving = False
            self.sig_target_pos_ended.emit(res.cmd_finished_ok)

        elif res.last_cmd == vmf_worker.VFMWorkerCmd.Reference_move:
            res = self.worker_thread.get_task_result()
            self.app.show_info_message(res.cmd_msg)
            self._is_moving = False
            self.sig_reference_move_ended.emit(res.cmd_finished_ok)

        elif res.last_cmd == vmf_worker.VFMWorkerCmd.Move:
            self._is_moving = False

        elif res.last_cmd == vmf_worker.VFMWorkerCmd.Save_Calibration:
            res = self.worker_thread.get_task_result()
            self.app.show_info_message(res.cmd_msg)
            self.sig_save_calibration_ended.emit(res.cmd_finished_ok)

        elif res.last_cmd == vmf_worker.VFMWorkerCmd.Initialize_VMF_Controller:
            self._vmf_controller_sn_number = self.worker_thread.vmf_controller_serial_no if self.worker_thread.vmf_controller else ""
            self._vmf_ready = (self._vmf_controller_sn_number != "") and (self._vmf_sample_holder_sn_number != "")
            res = self.worker_thread.get_task_result()
            self.app.show_info_message(res.cmd_msg)
            self.sig_init_controller_ended.emit(res.cmd_finished_ok)

        elif res.last_cmd == vmf_worker.VFMWorkerCmd.Initialize_VMF_SampleHolder:
            self._vmf_sample_holder_sn_number = self.worker_thread.vmf_holder_serial_no if self.worker_thread.vmf_controller else ""
            self._vmf_ready = (self._vmf_controller_sn_number != "") and (self._vmf_sample_holder_sn_number != "")
            res = self.worker_thread.get_task_result()
            self.app.show_info_message(res.cmd_msg)
            self.sig_init_sample_holder_ended.emit(res.cmd_finished_ok)
            self.sig_load_calibration_ended.emit(res.cmd_finished_ok)

        elif res.last_cmd == vmf_worker.VFMWorkerCmd.Load_Calibration:
            self._vmf_controller_sn_number = self.worker_thread.vmf_controller_serial_no if self.worker_thread.vmf_controller else ""
            self._vmf_sample_holder_sn_number = self.worker_thread.vmf_holder_serial_no if self.worker_thread.vmf_controller else ""
            self._vmf_ready = (self._vmf_controller_sn_number != "") and (self._vmf_sample_holder_sn_number != "")
            res = self.worker_thread.get_task_result()
            self.app.show_info_message(res.cmd_msg)
            self.sig_load_calibration_ended.emit(res.cmd_finished_ok)

        elif res.last_cmd == vmf_worker.VFMWorkerCmd.Load_Calibration_from_File:
            res = self.worker_thread.get_task_result()
            self.app.show_info_message(res.cmd_msg)
            self.sig_load_calibration_ended.emit(res.cmd_finished_ok)

        elif res.last_cmd == vmf_worker.VFMWorkerCmd.Save_Calibration_to_File:
            res = self.worker_thread.get_task_result()
            self.app.show_info_message(res.cmd_msg)
        else:
            self.logger.info(f"Unknown worker command {res.last_cmd} finished ")        

