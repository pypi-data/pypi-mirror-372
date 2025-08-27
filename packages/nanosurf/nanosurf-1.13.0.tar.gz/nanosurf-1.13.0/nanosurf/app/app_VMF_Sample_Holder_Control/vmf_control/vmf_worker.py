""" The long lasting worker thread as demo - just wait some time and create data periodically
Copyright Nanosurf AG 2021
License - MIT
"""

import enum
import pathlib
from PySide6.QtCore import Signal, QTimer
import nanosurf as nsf
from vmf_control import device_vmf_sample_holder

class VFMWorkerCmd(enum.Enum):
    Connect = enum.auto()
    Disconnect = enum.auto()
    Move = enum.auto()
    Move_to_Field = enum.auto()
    Move_to_Pos = enum.auto()
    Reference_move = enum.auto()
    Save_Calibration = enum.auto()
    Initialize_VMF_Controller = enum.auto()
    Initialize_VMF_SampleHolder = enum.auto()
    Load_Calibration = enum.auto()
    Load_Calibration_from_File = enum.auto()
    Save_Calibration_to_File = enum.auto()

class VMFWorkerData():
    def __init__(self) -> None:
        self.last_cmd: VFMWorkerCmd = None
        self.cmd_finished_ok:bool = True
        self.cmd_msg: str = ""

class VMFWorker(nsf.frameworks.qt_app.nsf_thread.SPMWorker):
    """ This class implements the long lasting activity in the background to not freeze the gui """

    sig_tick = Signal() # is emitted if par_send_tick is True
    sig_new_field= Signal(float) # is emitted each time a new field value is available
    sig_new_field_cmd = Signal()

    """ parameter for the background work"""
    par_repetition = 10
    par_time_per_repetition = 2.0
    par_send_ticks = True
    par_time_between_ticks = 0.05

    _sig_message = Signal(str, int)

    def __init__(self, my_module: nsf.frameworks.qt_app.ModuleBase):
        super().__init__(my_module)
        self.module = my_module
        self.vmf_controller_serial_no = ""
        self.vmf_holder_serial_no = ""
        self.vmf_controller: device_vmf_sample_holder.VMFSampleHolderController = None
        self.config_file = my_module.app.config_file
        self.config_section = "VFMSampleHolderState"

    def do_on_finish_thread(self):
        super().do_on_finish_thread()

    def do_on_start_thread(self):
        super().do_on_start_thread()
        self.sig_new_field_cmd.connect(self._on_end_of_poll_timer)

    def move_hook(self, current_field:float) -> bool:
        " This function is called during move actions. If the hook returns False, the move is aborted"
        self.sig_new_field.emit(current_field)
        stop_request = self.is_stop_request_pending()
        return not stop_request
       
    def message_hook(self, msg:str, is_error:bool=False):
        " This function is called during actions"
        if is_error:
            self.send_error_message(msg)
        else:
            self.send_info_message(msg)
       
    def _on_end_of_poll_timer(self):
        if not self.is_worker_running():
            h_field = self.vmf_controller.get_current_h_field()
            self.sig_new_field.emit(h_field)

    def do_work(self):
        """ This is the working function for the long task"""
        # self.logger.info(f"{self._args=}")
        # self.logger.info(f"{self._kwargs=}")
        self.result = VMFWorkerData()
        
        try: # parse command
            self.new_cmd = self._kwargs['command']
        except KeyError:
            self.send_error_message("Internal Error: VMFWorker started with no command.")
            return

        if self.new_cmd == VFMWorkerCmd.Connect:
            call_setup = bool(self._kwargs['call_setup'])
            ai_port_in_use = int(self._kwargs['ai_port'])
            restore_last_motor_pos = bool(self._kwargs['restore_last_motor_pos']) if 'restore_last_motor_pos' in self._kwargs else False
            self.send_info_message("Connecting to SPM Controller...")
            if self.connect_to_controller():
                
                self.send_info_message("Connecting to VMF-Controller...")
                if self.vmf_controller is None:
                    sim_mode = self.module.app.settings._is_in_simulation_mode
                    self.vmf_controller = device_vmf_sample_holder.VMFSampleHolderController(simulation=sim_mode)
                    self.vmf_controller.register_move_hook(self.move_hook)
                    self.vmf_controller.register_message_hook(self.message_hook)

                if self.vmf_controller.connect(self.spm, "", auto_setup=call_setup, ai_port=ai_port_in_use):
                    self.send_info_message("Setting up configuration...")
                    self.vmf_controller_serial_no = self.vmf_controller.get_serial_no()
                    self.vmf_holder_serial_no = self.vmf_controller.get_sample_holder_serial_no()
                    self.send_info_message(self.vmf_controller.get_message())

                    if restore_last_motor_pos:
                        if not self.vmf_controller.restore_sample_holder_state(self.config_file, self.config_section):
                            self.send_error_message(self.vmf_controller.get_message())
                else:
                    self.send_error_message(self.vmf_controller.get_message())
            else:
                self.send_error_message("Could not connect to SPM Control Software.")
        elif self.new_cmd == VFMWorkerCmd.Disconnect:
            self.send_info_message("Disconnecting from VMF-Controller...")
            if self.vmf_controller is not None:
                self.vmf_controller.store_sample_holder_state(self.config_file, self.config_section)
                self.vmf_controller.register_message_hook(None)
                self.vmf_controller.register_move_hook(None)
                del self.vmf_controller
                self.vmf_controller = None   
            self.disconnect_from_controller()
        elif self.new_cmd == VFMWorkerCmd.Move:
            forward_move = bool(self._kwargs['forward'])
            move_speed = float(self._kwargs['speed'])
            done = self.vmf_controller.move(direction_forward=forward_move, speed=move_speed)
            self.result.cmd_finished_ok = done
            self.result.cmd_msg = self.vmf_controller.get_message()

        elif self.new_cmd == VFMWorkerCmd.Move_to_Field:
            target_field = float(self._kwargs['target_field'])
            done = self.vmf_controller.move_to_field(target_field)
            self.result.cmd_finished_ok = done
            self.result.cmd_msg = self.vmf_controller.get_message()

        elif self.new_cmd == VFMWorkerCmd.Move_to_Pos:
            target_pos = float(self._kwargs['target_pos'])
            move_speed = float(self._kwargs['speed'])
            done = self.vmf_controller.move_to_pos(target_pos, move_speed)
            self.result.cmd_finished_ok = done
            self.result.cmd_msg = self.vmf_controller.get_message()

        elif self.new_cmd == VFMWorkerCmd.Reference_move:
            done = self.vmf_controller.reference_move()
            self.result.cmd_finished_ok = done
            self.result.cmd_msg = self.vmf_controller.get_message()

        elif self.new_cmd == VFMWorkerCmd.Save_Calibration:
            done = self.vmf_controller._save_calibration_to_sample_holder()
            self.result.cmd_finished_ok = done
            self.result.cmd_msg = self.vmf_controller.get_message()
            
        elif self.new_cmd == VFMWorkerCmd.Initialize_VMF_Controller:
            sn_number = str(self._kwargs['serial_no'])
            done = self.vmf_controller._initialize_controller_eeprom(sn_number)
            self.vmf_controller_serial_no = self.vmf_controller.get_serial_no()
            self.result.cmd_finished_ok = done
            self.result.cmd_msg = self.vmf_controller.get_message()

        elif self.new_cmd == VFMWorkerCmd.Initialize_VMF_SampleHolder:
            sn_number = str(self._kwargs['serial_no'])
            done = self.vmf_controller._initialize_sample_holder_eeprom(sn_number)
            self.vmf_controller._load_calibration_from_sample_holder()
            self.vmf_holder_serial_no = self.vmf_controller.get_sample_holder_serial_no()
            self.result.cmd_finished_ok = done
            self.result.cmd_msg = self.vmf_controller.get_message()
            
        elif self.new_cmd == VFMWorkerCmd.Load_Calibration:
            try:
                self.vmf_controller._load_calibration_from_sample_holder()
                self.vmf_controller_serial_no = self.vmf_controller.get_serial_no()
                self.vmf_holder_serial_no = self.vmf_controller.get_sample_holder_serial_no()
                self.result.cmd_finished_ok = True
                self.result.cmd_msg = "Done"
            except Exception as e:
                self.result.cmd_msg = f"Error: Could not setup device. Reason: {e}"
                self.result.cmd_finished_ok = False
        elif self.new_cmd == VFMWorkerCmd.Load_Calibration_from_File:
            try:
                file_name = pathlib.Path(self._kwargs['file_name'])
                self.vmf_controller._load_calibration_from_file(file_name)
                self.result.cmd_finished_ok = True
                self.result.cmd_msg = f"Done. Loaded from: {file_name}"
            except Exception as e:
                self.result.cmd_msg = f"Error: Could not load calibration. Reason: {e}"
                self.result.cmd_finished_ok = False
        elif self.new_cmd == VFMWorkerCmd.Save_Calibration_to_File:
            try:
                file_name = pathlib.Path(self._kwargs['file_name'])
                self.vmf_controller._save_calibration_to_file(file_name)
                self.result.cmd_finished_ok = True
                self.result.cmd_msg = f"Done. Saved to: {file_name}"
            except Exception as e:
                self.result.cmd_msg = f"Error: Could not save calibration. Reason: {e}"
                self.result.cmd_finished_ok = False
        else: 
            self.send_error_message(f"Internal Error: VMFWorker started with unknown command {self.new_cmd}.")
        self.result.last_cmd = self.new_cmd

    def get_task_result(self) -> VMFWorkerData:
        return self.result

