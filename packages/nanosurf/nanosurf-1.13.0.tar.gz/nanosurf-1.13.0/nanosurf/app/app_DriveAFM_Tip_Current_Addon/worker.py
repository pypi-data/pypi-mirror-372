""" The functional module where the functionality goes
Copyright Nanosurf AG 2021
License - MIT
"""

import nanosurf as nsf

import settings
import nanosurf.lib.devices.device_tip_current_addon as device_tip_current_addon 

g_Addon_SignalID = 18

class Worker(nsf.frameworks.qt_app.ModuleBase):

    def __init__(self, app: nsf.frameworks.qt_app.ApplicationBase, gui):
        super().__init__(app, gui)
        self.app:nsf.frameworks.qt_app.ApplicationBase = app
        self.settings = settings.Settings()
        self.spm:nsf.Spm = None
        self.tip_current_addon : device_tip_current_addon.DriveAFM_Tip_Current_Addon = None

    def do_start(self):
        # This function is called once at startup of application 

        if self._connect_to_controller():
            self.app.show_message("Connected to controller")
            self.tip_current_addon = device_tip_current_addon.DriveAFM_Tip_Current_Addon()
            if self.tip_current_addon.connect(self.spm):
                if self.spm.get_sw_version() >= (3,10,5,0):
                    self.spm.application.ScanHead.SetCalibrationSignalUnit(g_Addon_SignalID, "A")
                    self.spm.application.ScanHead.SetCalibrationSignalName(g_Addon_SignalID, "Tip Current")
            else:
                self.app.show_error_message("No Tip Current Addon Module detected")
            
        self.settings.gain_id.sig_value_changed.connect(self.on_gain_changed)
        self.set_gain(self.settings.gain_id.value)

    def do_stop(self):
        self._disconnect_from_controller()

    def on_gain_changed(self):
        self.set_gain(self.settings.gain_id.value)

    def set_gain(self, gain_id:settings.AmplifierGainID):
        if (self.tip_current_addon is not None) and self.tip_current_addon.is_connected():

            if gain_id == settings.AmplifierGainID.Gain_500uA:
                self.tip_current_addon.set_gain(device_tip_current_addon.AmplifierGain.Gain_10k)
                if self.spm.get_sw_version() >= (3,10,5,0):
                    self.spm.application.ScanHead.SetCalibrationSignalMax(g_Addon_SignalID, 500e-6)
                else:
                    self.app.show_info_message("Please change 'Addon'-Input calibration in CX Software to 500uA")
            elif gain_id == settings.AmplifierGainID.Gain_5uA:
                self.tip_current_addon.set_gain(device_tip_current_addon.AmplifierGain.Gain_1Meg)
                if self.spm.get_sw_version() >= (3,10,5,0):
                    self.spm.application.ScanHead.SetCalibrationSignalMax(g_Addon_SignalID, 5e-6)
                else:
                    self.app.show_info_message("Please change 'Addon'-Input calibration in CX Software to 5uA")
            elif gain_id == settings.AmplifierGainID.Gain_50nA:
                self.tip_current_addon.set_gain(device_tip_current_addon.AmplifierGain.Gain_100Meg)
                if self.spm.get_sw_version() >= (3,10,5,0):
                    self.spm.application.ScanHead.SetCalibrationSignalMax(g_Addon_SignalID, 50e-9)
                else:
                    self.app.show_info_message("Please change 'Addon'-Input calibration in CX Software to 50nA")
            else:
                raise ValueError(f"Unknown AmplifierGainID: {gain_id}")
        else: 
            self.app.show_info_message("Tip Current Addon not connected")
        
    """ Connect / disconnect to SPM controller """            

    def _connect_to_controller(self) -> bool:
        ok = self.spm is not None
        if not ok:
            self.spm = nsf.SPM()
            if self.spm.is_connected():
                if self.spm.is_scripting_enabled():
                    ok = True
                else:
                    self.app.show_error_message("Error: Scripting interface is not enabled")
            else:
                 self.app.show_error_message("Error: Could not connect to controller. Check if software is started")
        if not ok:
            self.spm = None
        return ok

    def _disconnect_from_controller(self):
        if self.spm is not None:
            if self.spm.application is not None:
                del self.spm
            self.spm = None

    def is_connected_to_controller(self) -> bool:
        return (self.spm is not None) and self.spm.is_connected()
    
    def is_addon_detected(self) -> bool:
        return (self.tip_current_addon is not None) and self.tip_current_addon.is_connected()
