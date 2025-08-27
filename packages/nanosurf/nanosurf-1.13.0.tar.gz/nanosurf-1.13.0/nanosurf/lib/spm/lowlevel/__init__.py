"""Module for scripting the logical units of the low level scripting interface.
Copyright (C) Nanosurf AG - All Rights Reserved (2021)
License - MIT"""

import enum
import nanosurf.lib.spm.lowlevel.ctrlunits.factory as ctrl_factory

class Lowlevel():
    ctrlunits = ctrl_factory._CtrlUnitFactory()

    """Contains the low-level interface classes."""
    def __init__(self, spm_ctrl_manager = None, lu_shared_file_path: str = ""):
        """Creates the objects of the low-level interface.

        Parameters
        ----------
        spm_ctrl_manager:
            COM object `application.SpmCtrlManager`

        lu_shared_file_path: str
            The file path of the file that describes the logical unit
            interface. (Usually `LogicalUnit_InterfaceShared.h`)
        """
        if spm_ctrl_manager is not None:
            self._logical_unit_com = spm_ctrl_manager.LogicalUnit
            self._create_data_buffer_interface(spm_ctrl_manager.DataBuffer)

            # Try to auto detect the LU Interface declaration
            if lu_shared_file_path == "":
                try:
                    # only v3.10.1 or newer has this property
                    lu_shared_file_path = self._logical_unit_com.GetInterfaceDescriptionFile
                except:
                    pass
            if lu_shared_file_path != "":
                self.create_logical_unit_interface(lu_shared_file_path)

    def _create_data_buffer_interface(self, data_buffer_com):
        import nanosurf.lib.spm.lowlevel.data_buffer_interface as nsf_data
        type_dict = {'_data_buffer_com': data_buffer_com}
        Interface = type(
            'DataBuffer', (nsf_data.DataBufferInterface,), type_dict)
        setattr(self, 'DataBuffer', Interface)

    def create_logical_unit_interface(self, lu_shared_file_path):
        import nanosurf.lib.spm.lowlevel.logical_unit_interface as lu
        import nanosurf.lib.spm.lowlevel.logical_unit_interface_parser as lu_parse
        
        type_items = lu_parse.ParseShared(
            lu_shared_file_path).lu_type_definitions.items()
        for type_name, type_definition in type_items:
            Interface = lu.logical_unit_type(
                    type_name, self._logical_unit_com, type_definition)
            setattr(self, type_name, Interface)

class StartStopMaskBit(enum.IntEnum): 
  DataCapture                 = 0x00000001
  DataSampling                = 0x00000002
  Unused                      = 0x00000004
  RampGenPOSITIONX            = 0x00000008
  RampGenPOSITIONY            = 0x00000010
  RampGenPLANEZ               = 0x00000020
  RampGenCTRLZ                = 0x00000040
  RampGenMAXZ                 = 0x00000080
  RampGenALTERNATEZ           = 0x00000100
  RampGenTIPVOLTAGE           = 0x00000200
  RampGenAPPROACH             = 0x00000400
  TimerPROC0                  = 0x00000800
  MemSigGen                   = 0x00001000
  RampGenTEST                 = 0x00002000
  RampGenUSER4                = 0x00004000
  TimerDBG1                   = 0x00008000

class EventMaskBits(enum.IntEnum):
    DataCapture_Done            = 0x00000001
    DataSampling_Done           = 0x00000002
    Unused_Done                 = 0x00000004
    RampGenPOSITIONX_Done       = 0x00000008
    RampGenPOSITIONY_Done       = 0x00000010
    RampGenPLANEZ_Done          = 0x00000020
    RampGenCTRLZ_Done           = 0x00000040
    RampGenMAXZ_Done            = 0x00000080
    RampGenALTERNATEZ_Done      = 0x00000100
    RampGenTIPVOLTAGE_Done      = 0x00000200
    RampGenAPPROACH_Done        = 0x00000400
    TimerPROC0_Done             = 0x00000800
    MemSigGen_Done              = 0x00001000
    RampGenTEST_Done            = 0x00002000
    RampGenUSER4_Done           = 0x00004000
    TimerDBG1_Done              = 0x00008000
    ZCtrlReachedErrorLimit_True = 0x00040000
    ZCtrlReachedMinZ_True       = 0x00080000
    ZCtrlReachedMaxZ_True       = 0x00100000
    ZCtrlReachedOutLimit_True   = 0x00200000
    ExtEvent0_True              = 0x00400000
    ExtEvent1_True              = 0x00800000
    SoftEvent0_True             = 0x01000000
    SoftEvent1_True             = 0x02000000
    SoftEvent2_True             = 0x04000000
    UserAbortEvent_True         = 0x08000000
    ANDMask0_True               = 0x10000000
    ANDMask1_True               = 0x20000000
    ANDMask2_True               = 0x40000000
    ANDMask3_True               = 0x80000000

if __name__ == '__main__':
    import nanosurf.lib.spm.lowlevel.manager_mock

    lowlevel = Lowlevel(
        nanosurf.lib.spm.lowlevel.manager_mock.SPMCtrlManager(),
        r"..\..\test\LogicalUnit_InterfaceShared.h")
