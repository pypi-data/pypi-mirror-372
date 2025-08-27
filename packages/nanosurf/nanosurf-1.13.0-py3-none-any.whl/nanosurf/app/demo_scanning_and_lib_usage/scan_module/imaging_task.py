""" The long lasting worker thread which start the scan and store the scan lines
Copyright Nanosurf AG 2021
License - MIT
"""
import time
from dataclasses import dataclass
from PySide6.QtCore import Signal

import nanosurf as nsf
from scan_module import settings

@dataclass
class ScanData():
    stream = nsf.SciStream(channels=2)
    scan_line_index = -1

class ScanFrameWorker(nsf.frameworks.qt_app.nsf_thread.SPMWorker):
    """ This class implements the long lasting activity of reading the scan data in the background to not freeze the gui """    

    sig_tick = Signal() # is emitted if par_send_tick is True
    sig_new_data = Signal() # is emitted each time a new scan line is measured. Result is read by self.get_result()

    """ parameter for the background work"""
    
    par_image_size = 1e-9
    par_time_per_line = 1.0
    par_points_per_line = 128
    par_channel_id = settings.ChannelD.Topography
    par_send_ticks = True
    par_time_between_ticks = 0.1

    _sig_message = Signal(str, int)

    def __init__(self, my_module: nsf.frameworks.qt_app.ModuleBase):
        """ setup the thread and wait until the task is started by thread.start()"""
        self.module = my_module
        self.result = ScanData()
        super().__init__(my_module)

    def do_work(self):
        """ This is the working function for the long task"""
        self.result = ScanData()

        if self.connect_to_controller():
            self.spm_scan = self.spm.application.Scan

            #first stop a running scan
            if self.spm_scan.IsScanning:
                self.spm_scan.Stop()
                while self.spm_scan.IsScanning:
                    time.sleep(0.01)

            # prepare frame
            self.spm_scan.ImageSize(self.par_image_size, self.par_image_size)
            self.spm_scan.Scantime = self.par_time_per_line
            self.spm_scan.Points = self.par_points_per_line
            self.spm_scan.Lines = self.par_points_per_line
            
            self.result.stream.set_stream_length(self.par_points_per_line)
            self.result.stream.define_stream_range(min=0.0, max=self.par_image_size, unit="m")
            self.result.stream.set_channel_count(2)
            #start our frame
            self.spm_scan.StartFrameUp()

            # monitor scanning and read new scan lines as they are available
            self.next_scan_line = 0
            self.tick_time = 0.0
            while (self.next_scan_line < self.par_points_per_line) and not self.is_stop_request_pending():
                
                # wait for new data 
                self.tick_time = 0.0
                while (self.next_scan_line > (self.spm_scan.Currentline - 1)) and self.spm_scan.IsScanning and not self.is_stop_request_pending():
                    time.sleep(self.par_time_between_ticks)
                    self.tick_time += self.par_time_between_ticks
                    if self.par_send_ticks:
                        self.sig_tick.emit()
                    self.send_info_message(f"Wait for scan line {self.next_scan_line} since {self.tick_time:.2f}s")

                # read new measured line
                channel = self.par_channel_id
                self.result.stream.set_channel(0, self._read_scan_line(self.next_scan_line, channel, forward=True, raw_data=False))
                self.result.stream.set_channel(1, self._read_scan_line(self.next_scan_line, channel, forward=False, raw_data=False))
                self.result.scan_line_index = self.next_scan_line
                self.sig_new_data.emit()
                
                # prepare for next line
                self.next_scan_line += 1

            self.spm_scan.Stop()
            self.logger.info(f"Scan ended at line: {self.spm_scan.Currentline}")

        self.disconnect_from_controller()

    def get_task_result(self) -> ScanData:
        return self.result

    def _read_scan_line(self, line: int, channel: int, forward=True, raw_data: bool = True) -> nsf.SciChannel:
        group  = nsf.Spm.ScanGroupID.Forward if forward else nsf.Spm.ScanGroupID.Backward
        filter = nsf.Spm.DataFilter.RAW if raw_data else nsf.Spm.DataFilter.LineFit
        unit_str = "m" if channel == 1 else "V"
        line_str:str = self.spm_scan.GetLine(group, channel, line, filter, nsf.Spm.DataConversion.Physical)
        line_str = line_str.replace(',','.') # needed in case the numbers are formatted with a ',' as decimal separator (e.g. standard german windows number format setting)
        line_split_str = line_str.split(";")
        scan_data = [float(p) for p in line_split_str]
        return nsf.SciChannel(scan_data, unit=unit_str)
