""" Multithreading made simpler. 
This package provides classes to handle background tasks and sig/slot communication
Copyright Nanosurf AG 2022
License - MIT
"""
import sys
import time
import logging
import platform

if platform.system() == "Windows":
    import pythoncom # to connect to SPM Controller within thread

from PySide6.QtCore import QThread, QObject, Signal
from PySide6.QtWidgets import QApplication

from nanosurf.lib.frameworks.qt_app.module_base import ModuleBase

if platform.system() == "Windows":
    from nanosurf.lib.spm.spm_app import SPMApp

global_is_in_debugging_mode = (getattr(sys, 'gettrace', lambda : None)() is not None)
if global_is_in_debugging_mode:
    import debugpy 

def activate_debugger_support_for_this_thread():
    """ This function has to be called from each new thread to activate debugger support for it"""
    if global_is_in_debugging_mode:
        debugpy.debug_this_thread()

def slot(f):
    """ decorator which makes debugging possible in slots called in background tasks"""
    def decorated(*args, **kwargs):
        activate_debugger_support_for_this_thread()
        return f(*args, **kwargs)
    return decorated

class NSFThread(QObject):
    """ This class implements basic infrastructure for background activity. 

        The communication with the threads functionality is done by signal/slot mechanism of Qt. 
        Subclass from this class and define signal handler functions. 
        Each handler function should be decorated with @nsf_thead.slot

        Usage
        -----

        Define command signal handler with type Signal() as class attributes
        Redefine _init_in_new_thread() and connect signal handles functions to each defined signal there.

        At runtime, create an instance of your NSFThread class and call start_tread().
        Then emit your defined signal to send commands to your thread

        start_thread() - starts the background task. do_on_start_thread() can implement initialization work
        stop_thread()  - stops the background task. do_on_finish_thread can implement  cleanup work
        is_thread_running() - returns True if the task is running. Even if no worker is executing

        Signals
        -------

        sig_task_started - is sent after background task is started and do_on_start_thread() is executed
        sig_task_finished - is sent after background task  do_on_finish_thread() is executed and background task is stopped

    """
    sig_task_started = Signal()
    sig_task_finished = Signal()

    #--------------- for sub classing ------------------------------------------------------------

    def do_on_start_thread(self):
        pass

    def do_on_finish_thread(self):
        pass

    #--------------- implementation ------------------------------------------------------------

    def __init__(self, *args, **kwargs):
        """ setup the thread and wait until the task is started by thread.start()"""
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.is_thread_start_done = False
        self.is_thread_finish_done = False
        self.the_thread = QThread()
        self.moveToThread(self.the_thread)
        self.the_thread.started.connect(self._on_thread_started)
        self.the_thread.finished.connect(self._on_thread_finished)
        self._init_in_new_thread()

    def _init_in_new_thread(self):
        """ Init new thread functions here 
        Most common is to connect signal handler functions to signals
        """
        pass
    
    @slot
    def _on_thread_started(self):
        self.logger.info("on_thread_started()") 
        self.do_on_start_thread()
        self.is_thread_start_done = True
        self.is_thread_finish_done = False
        self.sig_task_started.emit()
        
    @slot
    def _on_thread_finished(self):
        self.logger.info("on_thread_finished()") 
        self.do_on_finish_thread()
        self.is_thread_start_done = False
        self.is_thread_finish_done = True
        self.sig_task_finished.emit()
        
    def start_thread(self):
        """ Start the worker activity. """
        if not self.is_thread_running():
            self.the_thread.start()
        else:
            self.logger.warning("background thread already started")

    def stop_thread(self, wait: bool = False, timeout : float = 10.0) -> bool:
        """ Send stop request to worker thread.  
            'sig_finished' is emitted when the worker thread has finished its job.

            Parameters
            ----------
            wait: bool
                If True the function waits until the worker thread has really finished
            timeout: float
                maximal wait time 

            Returns
            -------
            Bool:
                True if task could be stopped.
        """
        if self.is_thread_running():
            self.logger.info("Stop background task")
            self.the_thread.exit(0)

            # The following code replaces the simple command:
            #    has_finished = self.the_thread.wait(timeout*1000)
            # This, because the event self.the_thread.finished was not emitted in all circumstances
            # and therefore the connected  self._on_thread_finished function never called
            if wait and self.is_thread_start_done:
                start_time = time.time()
                while not self.is_thread_finish_done:
                    QApplication.processEvents()
                    time.sleep(0.1)
                    if time.time() >= (start_time + timeout):
                        break

                if not self.is_thread_finish_done:
                    self.logger.warning(f"Thread stop request was not served in {timeout}s")
                    self.the_thread.terminate()
        else:
            self.logger.info("Thread is not running")
        return not self.is_thread_running()

    def is_thread_running(self) -> bool:
        return self.the_thread.isRunning() if self.the_thread is not None else False

class NSFBackgroundWorker(NSFThread):
    """ This class provides a background worker function which can be called multiple times. 
        
        Usage
        -----

        Implement self.do_work() which your code. 
        Call start_thread() once to start background task
        Call start_worker(args, kwargs) as many times as you like 

        New functions
        -------------

        start_work()   - starts the background working task implemented by do_work()
        abort_worker() - send an abort request to the worker implemented in do_work().

        do_work() - implement this function and do the background work. 
                    Check regularly self.is_stop_request_pending()  and abort if it returns True.
                    in 'self._args' and 'self._kwargs' the parameters are passed from start_work()

        is_worker_running() - returns True if the background worker is executing
        is_worker_aborted() - returns True if the worker is finished by abortion

        New Signals
        -----------

        sig_worker_started  - is send each time the background worker function has started to do its work.
        sig_worker_finished - is send each time the background worker function has finished. Also in case of abortion.

    """
    sig_worker_started = Signal()
    sig_worker_finished = Signal()

    _sig_error_message  = Signal(str) # is emitted  by show_error_message()
    _sig_info_message  = Signal(str) # is emitted  by show_info_message()

    _cmd_start_worker = Signal()

    #--------------- to sub class ------------------------------------------------------------
   
    def do_work(self):
        self.logger.info("Base implementation of do_work(): was called. This function should be overwritten by subclass to do real stuff.") 

    #--------------- implementation ------------------------------------------------------------

    def __init__(self, my_module: ModuleBase = None, *args, **kwargs):
        self.module = my_module
        self.worker_stop_request_flag = False
        self.is_worker_active_flag = False
        super().__init__(*args, **kwargs)
        if self.module is not None:
            self._sig_error_message.connect(self.module.app.show_error_message)
            self._sig_info_message.connect(self.module.app.show_info_message)

    def send_info_message(self, msg:str):
        self._sig_info_message.emit(msg)
        self.logger.info(msg) 
        self._reschedule_event_loop() 

    def send_error_message(self, msg:str):
        self._sig_error_message.emit(msg)
        self.logger.info(msg)  
        self._reschedule_event_loop() 

    def _init_in_new_thread(self):
        self._cmd_start_worker.connect(self._start_background_worker)
    
    def do_on_start_thread(self):
        self.is_worker_active_flag = False
        self.worker_stop_request_flag = False
        
    def do_on_finish_thread(self):
        self.is_worker_active_flag = False
        
    def start_worker(self, *args, **kwargs):
        """ start the provided function  in the context of the background thread
        sig_function_started is emitted when the function really starts.
        sig_function_finished is emitted when the function returned
        To stop the function, call abort_worker() to try to abort the function.
        The function has to monitor if self.is_stop_request_pending() is True and abort accordingly
        """
        self.worker_stop_request_flag = False
        self.is_worker_active_flag = True
        self._args = args
        self._kwargs = kwargs
        self._cmd_start_worker.emit()

    def abort_worker(self, wait: bool = True, timeout: float = 10.0) -> bool:
        """ Send stop request to client function thread.  

            Parameters
            ----------
            wait: bool
                If True the function waits until the client function has really finished
            timeout: float
                maximal wait time 

            Returns
            -------
            Bool:
                True if function could be stopped.
        """
        if self.is_worker_running():
            self.logger.info("Set worker_stop_request_flag")
            self.worker_stop_request_flag = True

            if wait:
                if not self.wait_end_of_worker(timeout):
                    self.logger.warning(f"Stop worker request was not served in {timeout}s")
        return not self.is_worker_running()

    def wait_end_of_worker(self, timeout: float = 10.0) -> bool:
        """ wait until a running worker functions ends.  

            Parameters
            ----------
            timeout: float
                maximal wait time 

            Returns
            -------
            Bool:
                True if function ended before timeout.
        """        
        ticks = 0
        waiting_time = 0.0
        while self.is_worker_running() and (waiting_time < timeout):
            time.sleep(0.1)
            ticks += 1
            if ticks > 10:
                ticks = 0
                waiting_time += 1.0
                if waiting_time >= timeout:
                    break
        return not self.is_worker_running()
    
    def is_worker_running(self) -> bool:
        return self.is_worker_active_flag

    def is_worker_aborted(self) -> bool:
        return self.worker_stop_request_flag and (not self.is_worker_active_flag)

    def stop_thread(self, wait: bool = False, timeout : float = 10.0) -> bool:
        """ Send stop request to worker thread.  
            'sig_finished' is emitted when the worker thread has finished its job.

            Parameters
            ----------
            wait: bool
                If True the function waits until the worker thread has really finished
            timeout: float
                maximal wait time 

            Returns
            -------
            Bool:
                True if task could be stopped.
        """
        if self.is_thread_running():
            self.the_thread.requestInterruption()
            self.worker_stop_request_flag = True

            if self.is_worker_running():
                self.logger.info("Stop running worker")
                has_finished = self.abort_worker(wait, timeout)
                if not has_finished:
                    self.logger.info("Could not stop worker")

        return super().stop_thread(wait=wait, timeout=timeout)    

    def is_stop_request_pending(self):
        return self.the_thread.isInterruptionRequested() or self.worker_stop_request_flag

    @slot
    def _start_background_worker(self):
        self.is_worker_active_flag = True
        self.sig_worker_started.emit()

        if not self.worker_stop_request_flag:
            self.do_work()
        
        self.is_worker_active_flag = False
        self.sig_worker_finished.emit()
       
    def _reschedule_event_loop(self):
        time.sleep(0.01)

if platform.system() == "Windows":
    class SPMWorker(NSFBackgroundWorker):
        """ This class provides a background worker function with spm controller"""

        def __init__(self, my_module: ModuleBase = None):
            self.module = my_module
            self.spm_app:SPMApp = None
            self.spm = None
            self.lu = None
            super().__init__(my_module)

        def do_on_finish_thread(self):
            if self.spm_app is not None:
                self.disconnect_from_controller()
            super().do_on_finish_thread()

        def connect_to_controller(self) -> bool:
            ok = False
            if self.spm_app is None:
                self.send_info_message("Connecting to Nanosurf controller")
                pythoncom.CoInitialize()
                self.spm_app = SPMApp()
                self.spm_ctrl = self.spm_app.connect()
                if self.spm_ctrl is not None:
                    if self.spm_app.is_scripting_enabled():
                        self.spm = self.spm_ctrl.spm
                        self.lu = self.spm.lu
                        ok = True
                    else:
                        self.send_error_message("Error: Scripting interface is not enabled")
                else:
                    self.send_error_message("Error: Could not connect to controller. Check if software is started")
                    del self.spm_app
                    self.spm_app = None
            else:
                ok = self.spm_app.is_connected()
            return ok

        def disconnect_from_controller(self):
            self.send_info_message("Disconnecting from Nanosurf controller")
            if self.lu is not None:
                del self.lu
                self.lu = None
            if self.spm is not None:
                del self.spm
                self.spm = None
            if self.spm_app is not None:
                del self.spm_app
                self.spm_app = None
            