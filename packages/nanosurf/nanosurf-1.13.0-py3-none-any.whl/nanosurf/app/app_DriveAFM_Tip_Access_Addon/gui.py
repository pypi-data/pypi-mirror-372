""" This is the screen of the module
Copyright Nanosurf AG 2021
License - MIT
"""


from PySide6 import QtWidgets
import nanosurf as nsf

import worker
import settings

""" This connects a NSFComboBox item list with id used by the worker. Read active id with NSFComboBox.value() """
ComboTipModeIDs = [
    nsf.gui.NSFComboEntry(settings.TipMode.Internal,  'Internal'),
    nsf.gui.NSFComboEntry(settings.TipMode.External,  'External'),
    nsf.gui.NSFComboEntry(settings.TipMode.Open,      'Open'),
    nsf.gui.NSFComboEntry(settings.TipMode.Unknown,   'Unknown'),
]

""" some useful list of allowed prefixes used by NSFSciEdit widgets"""
allowed_count_units = [nsf.sci_val.up.Prefix.base]
allowed_time_units = [nsf.sci_val.up.Prefix.base, nsf.sci_val.up.Prefix.milli]
allowed_meter_units = [nsf.sci_val.up.Prefix.milli, nsf.sci_val.up.Prefix.micro, nsf.sci_val.up.Prefix.nano]


class Screen(nsf.frameworks.qt_app.ModuleScreen):
    
    def __init__(self):
        super().__init__()
        self.module:worker.Worker 

    def do_setup_screen(self, worker: worker.Worker):
        self.worker = worker

        # left layout - main controls ------------------------------------------------------------
        self.combo_tip_mode_id = nsf.gui.NSFComboBox(ComboTipModeIDs,"Select the connection")
        self.layout_left = QtWidgets.QVBoxLayout()
        self.layout_left.addWidget(self.combo_tip_mode_id)
        self.layout_left.addSpacerItem(nsf.gui.NSFHSpacer(minimal_width=300))
        self.layout_left.addStretch()

        self.screen_layout = QtWidgets.QHBoxLayout()
        self.screen_layout.addLayout(self.layout_left, 0)

        self.setLayout(self.screen_layout)
        self.bind_gui_elements()

        if not self.module.is_connected_to_controller():
            self.combo_tip_mode_id.setEnabled(False)

        if not self.module.is_addon_detected():
            self.combo_tip_mode_id.setEnabled(False)

    def on_activate_screen(self):
        pass

    def bind_gui_elements(self):
        nsf.gui.connect_to_property(self.combo_tip_mode_id, self.worker.settings.tip_mode)

