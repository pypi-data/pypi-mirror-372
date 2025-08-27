""" The long lasting worker thread as demo - just wait some time and create data periodically
Copyright Nanosurf AG 2021
License - MIT
"""
import time
import enum
from PySide6.QtCore import Signal

import nanosurf as nsf
from nanosurf.lib.frameworks.qt_app import nsf_thread
import nanosurf.lib.spm.lowlevel.ctrlunits as cu
from switching_spec_module import settings

class SpecWorkerData():
    def __init__(self):
        self.output : float = 0.0
        self.output_unit :str = ""
        self.amplitude_on : float = 0.0
        self.amplitude_off : float = 0.0
        self.amplitude_unit : str = ""
        self.phase_on : float = 0.0
        self.phase_off : float = 0.0

OutputChannel_ID_to_LUInst_Map = {
    settings.OutputChannelID.User1.value : cu.DAC.HiResOut_USER1,
    settings.OutputChannelID.User2.value : cu.DAC.HiResOut_USER2,
    settings.OutputChannelID.TipVoltage.value : cu.DAC.HiResOut_TIPVOLTAGE,
}

class SpecDir(enum.Enum):
    SpecFwd = 0
    SpecBwd = 1

class SpecWorker(nsf_thread.SPMWorker):
    """ This class implements the long lasting activity in the background to not freeze the gui """

    sig_tick = Signal() # is emitted if par_send_tick is True
    sig_new_data = Signal() # is emitted each time new data are available . Result is read by self.get_result()

    """ parameter for the background work"""
    par_output_id = settings.OutputChannelID.User1
    par_output_span = 10.0   # V: spec range, using the scaling and unit as defined in the software
    par_output_center = 0.0
    par_time_per_step = 0.1    # equilibration time for voltage and lock-in to settle
    par_steps = 10             # number of steps per direction

    _sig_message = Signal(str, int)

    def __init__(self, my_module: nsf.frameworks.qt_app.ModuleBase):
        self.module = my_module
        self.result = SpecWorkerData()
        super().__init__(my_module)


    def do_work(self):
        """ This is the working function for the long task"""
        # clear data
        self.result = SpecWorkerData()

        if self.connect_to_controller():
                           
            lock_in = self.spm.lowlevel.ctrlunits.get_lock_in()
            dac_out = self.spm.lowlevel.ctrlunits.get_dac(OutputChannel_ID_to_LUInst_Map[self.par_output_id])
            original_out = dac_out.dc
            original_source = dac_out._lu.input.value

            self.cur_voltage_range = self.par_output_span
            self.cur_steps = self.par_steps 
            self.cur_time_per_step = self.par_time_per_step 
            self.cur_offset_voltage = self.par_output_center

            self.result.amplitude_unit = lock_in.input_amp_unit 
            self.result.output_unit = dac_out.unit
            
            #move in both spectroscopy directions
            for spec_dir in SpecDir:
                #voltage step size with opposite sign for fwd and bwd
                cur_offset = self.cur_offset_voltage  + self.cur_voltage_range/2*(2*(spec_dir.value % 2) - 1)
                cur_voltage_step = self.cur_voltage_range/(self.cur_steps - 1)*(1 - 2*(spec_dir.value % 2)) 
                
                # This loop creates the shape of switching spectroscopy in time
                for cur_step in range(self.cur_steps): 
                    cur_output = cur_offset + cur_step*cur_voltage_step
                    self.result.output = cur_output

                    # write a dc level to an output and measure response during voltage application
                    dac_out.dc = cur_output
                    time.sleep(self.cur_time_per_step)
                    self.result.amplitude_on = lock_in.input_amp 
                    self.result.phase_on = lock_in.input_phase

                    # switch potential back to offset voltage and measure response again
                    dac_out.dc = self.cur_offset_voltage 
                    time.sleep(self.cur_time_per_step)
                    self.result.amplitude_off = lock_in.input_amp 
                    self.result.phase_off = lock_in.input_phase
            
                    if self.is_stop_request_pending():
                        break
                    self.sig_new_data.emit()

            # restore original setting of output        
            dac_out.dc = original_out
            dac_out._lu.input.value = original_source
        self.disconnect_from_controller()

    def get_result(self) -> SpecWorkerData:
        return self.result
