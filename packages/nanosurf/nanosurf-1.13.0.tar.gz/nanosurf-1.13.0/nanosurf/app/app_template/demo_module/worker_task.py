""" The long lasting worker thread as demo - just wait some time and create data periodically
Copyright Nanosurf AG 2021
License - MIT
"""
import time
import math
from dataclasses import dataclass, field
from PySide6.QtCore import Signal
import nanosurf as nsf
from demo_module import settings

class MyWorkerData():
    def __init__(self) -> None:
        self.value:list[float] = []
        self.last_index:int = -1

class MyWorker(nsf.frameworks.qt_app.nsf_thread.NSFBackgroundWorker):
    """ This class implements the long lasting activity in the background to not freeze the gui """

    sig_tick = Signal() # is emitted if par_send_tick is True
    sig_new_data = Signal() # is emitted each time new data are available . Result is read by self.get_result()

    """ parameter for the background work"""
    par_repetition = 10
    par_time_per_repetition = 2.0
    par_send_ticks = True
    par_time_between_ticks = 0.05
    par_plot_func_id = settings.PlotStyleID.PlotSin

    _sig_message = Signal(str, int)

    def __init__(self, my_module: nsf.frameworks.qt_app.ModuleBase):
        super().__init__(my_module)
        self.module = my_module
        self.result = MyWorkerData()

    def do_work(self):
        """ This is the working function for the long task"""
        # clear data
        self.result = MyWorkerData()

        self.count = 0
        while (self.count < self.par_repetition) and not self.is_stop_request_pending():
            self.count += 1

            if self.par_send_ticks:
                self.tick_time = 0.0
                while self.tick_time < self.par_time_per_repetition and not self.is_stop_request_pending():
                    self.tick_time += self.par_time_between_ticks
                    time.sleep(self.par_time_between_ticks)
                    self.sig_tick.emit()
                    self.send_info_message(f"Tick: {self.tick_time:.2f}s")
            else:
                time.sleep(self.par_time_per_repetition)        
            
            if self.par_plot_func_id.value == settings.PlotStyleID.PlotSin:
                self.result.value.append(math.sin(self.count / self.par_repetition * math.pi))
            elif self.par_plot_func_id.value == settings.PlotStyleID.PlotCos:
                self.result.value.append(math.cos(self.count / self.par_repetition * math.pi))
            else:
                self.send_error_message("Unknown plot style")

            self.result.last_index += 1
            self.sig_new_data.emit()

    def get_task_result(self) -> MyWorkerData:
        return self.result
