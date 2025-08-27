""" The functional module where the functionality goes
Copyright Nanosurf AG 2021
License - MIT
"""

from PySide6.QtCore import Signal
import nanosurf as nsf
from vmf_control import vmf_module, setup_settings
from vmf_control.device_vmf_sample_holder import VMFControllerConfig, VMFSampleHolderConfig


class SetupModule(nsf.frameworks.qt_app.ModuleBase):

    sig_calibration_started = Signal()
    sig_calibrate_start_requested = Signal()
    sig_calibrate_stop_requested = Signal()
    sig_calibration_finished = Signal()
    sig_update_device_infos = Signal()

    # sig_data_invalid = Signal()

    """ Initialization functions of the module """

    def __init__(self, app: nsf.frameworks.qt_app.ApplicationBase, vmf_mod):
        super().__init__(app)
        self.app:nsf.frameworks.qt_app.ApplicationBase
        self.settings = setup_settings.SetupSettings()
        self.vmf_module: vmf_module.VMFModule = vmf_mod 

    def do_start(self):
        self._connect_to_properties()
        self.vmf_module.sig_connecting_done.connect(self._on_connecting_done)        
        self.vmf_module.sig_load_calibration_ended.connect(self._on_load_setup_done)   

    def do_stop(self):
        """ This function is called at module shutdown"""
        pass

    """ Business logic of the module """

    def _connect_to_properties(self):
        """ Connect action functions to settings 
            The connected functions are called whenever a setting is changed (e.g. by GUI elements)
        """
        pass

    def _on_connecting_done(self):
        self.update_device_infos()
        self.vmf_module.start_load_calibration_from_sample_holder()     

    def _on_load_setup_done(self):
        self.update_device_infos()

    def update_device_infos(self):
        ctrl_sn = self.vmf_module.vmf_controller_sn_number() 
        if ctrl_sn == "":
            ctrl_sn = VMFControllerConfig(bus_addr=None).sn_number
        self.settings._controller_sn.value = ctrl_sn

        holder_sn = self.vmf_module.vmf_sample_holder_sn_number()
        if holder_sn == "":
            holder_sn = VMFSampleHolderConfig(bus_addr=None).sn_number
        self.settings._sample_holder_sn.value = holder_sn 
          
        self.settings._cal_names = str(self.vmf_module.get_sample_holder_configurations())

        config_list = self.vmf_module.worker_thread.vmf_controller.configurations
        self.settings._cal_0_values = [ cal.cal_values[0] for cal in config_list]
        self.settings._cal_1_values = [ cal.cal_values[1] for cal in config_list]
        self.settings._cal_2_values = [ cal.cal_values[2] for cal in config_list]

        self.sig_update_device_infos.emit()

