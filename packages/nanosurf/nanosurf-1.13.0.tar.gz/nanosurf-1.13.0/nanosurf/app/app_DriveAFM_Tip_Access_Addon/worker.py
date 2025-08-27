""" The functional module where the functionality goes
Copyright Nanosurf AG 2021
License - MIT
"""

import nanosurf as nsf

import settings
import nanosurf.lib.devices.device_tip_access_addon as device_tip_access_addon 


class Worker(nsf.frameworks.qt_app.ModuleBase):

    def __init__(self, app: nsf.frameworks.qt_app.ApplicationBase, gui):
        super().__init__(app, gui)
        self.app:nsf.frameworks.qt_app.ApplicationBase = app
        self.settings = settings.Settings()
        self.spm:nsf.Spm = None
        self.addon_device : device_tip_access_addon.DriveAFM_Tip_Access_Addon = None

    def do_start(self):
        if self._connect_to_controller():
            self.app.show_message("Connected to controller")
            self.addon_device = device_tip_access_addon.DriveAFM_Tip_Access_Addon()
            if self.addon_device.connect(self.spm):
                self.app.show_info_message("Ready. Connected to Tip Access Addon Module")
            else:
                self.settings.tip_mode.value = settings.TipMode.Unknown.value
                self.app.show_error_message("No Tip Access Addon Module detected")
        else:
            self.settings.tip_mode.value = settings.TipMode.Unknown.value
          
        self.settings.tip_mode.sig_value_changed.connect(self.on_tip_mode_changed)
        self.set_tip_mode(self.settings.tip_mode.value)

    def do_stop(self):
        self._disconnect_from_controller()

    def on_tip_mode_changed(self):
        self.set_tip_mode(self.settings.tip_mode.value)

    def set_tip_mode(self, tip_mode:settings.TipMode):
        if (self.addon_device is not None) and self.addon_device.is_connected():
            if tip_mode == settings.TipMode.Internal:
                self.addon_device.set_tip_connection(device_tip_access_addon.TipConnection.Internal)
            elif tip_mode == settings.TipMode.External:
                self.addon_device.set_tip_connection(device_tip_access_addon.TipConnection.External)
            elif tip_mode == settings.TipMode.Open:
                self.addon_device.set_tip_connection(device_tip_access_addon.TipConnection.Open)
            elif tip_mode == settings.TipMode.Unknown:
                self.app.show_info_message("Tip Current Addon not connected")
            else:
                raise ValueError(f"Unknown tip mode: {tip_mode}")
        else: 
            self.settings.tip_mode.value = settings.TipMode.Unknown.value
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
        return (self.addon_device is not None) and self.addon_device.is_connected()
