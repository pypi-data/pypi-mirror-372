""" The long lasting worker thread as demo - just wait some time and create data periodically
Copyright Nanosurf AG 2021
License - MIT
"""

import time
import pathlib
from PySide6.QtCore import Signal
import nanosurf as nsf
from vmf_control import vmf_module
from vmf_control.device_vmf_sample_holder import VMFSampleHolderController

import serial
from serial.tools.list_ports_windows import comports

class CalibrateWorkerData():
    def __init__(self) -> None:
        self.ok = False
        self.msg = ""

class CalibrateWorker(nsf.frameworks.qt_app.nsf_thread.NSFBackgroundWorker):
    """ This class implements the long lasting activity in the background to not freeze the gui """

    sig_tick = Signal() # is emitted if par_send_tick is True
    sig_new_field= Signal(float) # is emitted each time a new field value is available
    sig_new_frame= Signal(float) # is emitted each time a new field value is available

    """ parameter for the background work"""
    par_config_index = 0
    par_start_pos = -0.8
    par_end_pos = 0.8
    par_speed = 0.8
    par_num_steps = 20

    par_target_dir = pathlib.Path("")
    par_target_file_mask = pathlib.Path("")
    _sig_message = Signal(str, int)

    def __init__(self, vmf_module: 'vmf_module.VMFModule'):
        super().__init__(vmf_module)
        self.vmf_module = vmf_module
        self._FM302COM = ""
        self.un_cal_measurement = []
        self.ref_measurement = []

    def do_work(self):
        """ This is the working function for the long task"""
        self.logger.info("start_calibration_work")
        self.result = CalibrateWorkerData()
        sim_mode = self.module.app.settings._is_in_simulation_mode

        if self._FM302COM == "":
            self.init_FM302()

        if self._FM302COM != "" or sim_mode:

            self.vmf_module.worker_thread.vmf_controller.configuration_select(self.par_config_index)
            active_config_backup = self.vmf_module.worker_thread.vmf_controller._get_active_config()
            
            un_cal_config = VMFSampleHolderController.VMFConfiguration()
            un_cal_config.cal_values = [0.0, 1.0, 0.0]
            un_cal_config.name = active_config_backup.name
            self.vmf_module.worker_thread.vmf_controller._set_active_config(un_cal_config)

            self.un_cal_measurement = []
            self.ref_measurement = []
            pos_step  = (self.par_end_pos - self.par_start_pos) / (self.par_num_steps - 1)
            next_pos = self.par_start_pos        
            for pos_index in range(self.par_num_steps):
                if self.is_stop_request_pending():
                    break    

                self.vmf_module.start_move_to_pos(next_pos, self.par_speed)
                while self.vmf_module.is_moving() and not self.is_stop_request_pending():
                    time.sleep(0.5)

                if self.is_stop_request_pending():
                    self.vmf_module.stop_moving()
                    while self.vmf_module.is_moving():
                        time.sleep(0.5)

                if not self.vmf_module.is_last_cmd_ok() and not self.is_stop_request_pending():
                    self.result.ok = False
                    self.result.msg = f"Could not reached target pos: {next_pos}"
                    self.abort_worker(wait=False)
                
                cur_measured_value = self.vmf_module.get_last_h_field() 
                cur_ref_value = self.read_FM302() if not sim_mode else next_pos / 1e6

                self.un_cal_measurement.append(cur_measured_value)
                self.ref_measurement.append(cur_ref_value)
                print(f"pos({pos_index}) = {next_pos}, {cur_measured_value=}, cur_ref_field={cur_ref_value}" )  

                next_pos += pos_step

            self.vmf_module.worker_thread.vmf_controller._set_active_config(active_config_backup)

            if not self.is_stop_request_pending():
                self.result.msg = "Moving back to zero..."

                self.vmf_module.start_move_to_pos(0.0, self.par_speed)
                while self.vmf_module.is_moving() and not self.is_stop_request_pending():
                    time.sleep(0.5)
                self.result.msg = "Calibration done."
                self.result.ok = True
        else:
            self.result.ok = False
            self.result.msg = "Could not connect to FM302 Tesla-Meter."           

    def init_FM302(self):  # Detect FM 302
        FMport = self.find_FM302()
        if FMport != 'COM0':
         self._FM302COM = FMport

    def find_FM302(self):
        ports = []
        for info in comports(False):
            arr = info.description.split(" ")
            if arr[0] == 'USB':
                ports.append(info.device)

        FMport = 'COM10'
        for port in ports:
            try:
                ser = serial.Serial(port, 9600, timeout=1, parity=serial.PARITY_NONE, stopbits=1, rtscts=0)
                ser.write("fmstatus\r\n".encode(encoding='windows-1250'))
                s = ser.read(2).decode("utf-8")

                if s == 'FM':
                    self.vmf_module.app.show_info_message(f"Detected FM302 on {port=}")
                    FMport = port
                ser.close()

            except Exception:
                print("FM302 not found please connect it via USB")
        return FMport
    
    def read_FM302(self) -> float:
        """read the magnetic field from the external USB Tesla meter"""
        try:
            ser = serial.Serial(self._FM302COM, 9600, timeout=1, parity=serial.PARITY_NONE, stopbits=1, rtscts=0)
            ser.write("logging 1\r\n".encode(encoding='windows-1250'))
            s = ser.read(50).decode("utf-8").split("\r\n")
            field = float(s[1].split(" ")[0])
            ser.close()
        except Exception as e:
            self.vmf_module.app.show_error_message(f"Error while reading from FM302 Tesla meter: Reason: {e}")
            field = 0
                    
        field = field / 1000
        return field

    def get_task_result(self) -> CalibrateWorkerData:
        return self.result
