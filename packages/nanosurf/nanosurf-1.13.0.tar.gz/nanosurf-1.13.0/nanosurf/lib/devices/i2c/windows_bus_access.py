# nanosurf linux I2C bus access driver
import enum
from typing import Any
from nanosurf.lib.devices.i2c.bus_access import I2CBusAccess, I2CByteMode, I2CBusSpeed, I2COffsetMode, I2CSyncing,I2CMasterType, I2CInstances,I2CMetaData

from nanosurf.lib.spm.com_proxy import Spm
from nanosurf.lib.spm.studio import Studio

class I2CBusID(enum.IntEnum):
    Unassigned = -1
    User      = 0x2000300
    HV        = 0x2000320
    ScanHead  = 0x2000360
    Interface = 0x2000340

class SPMBusAccess(I2CBusAccess):
    def __init__(self, parent:"I2CBusMaster", bus_id:I2CBusID, spm:Spm, instance_id, master_type):
        super().__init__(parent, bus_id)
        self._spm = spm
        self._instance_id = instance_id
        self._master_type  = master_type
        self._rx_packet_buffer_len  = 50
        self._tx_packet_buffer_len  = 50  
        self._bus_speed = I2CBusSpeed.kHz_Default      
        self._i2c_proxy = self._spm.application.CreateTestObj
        self._master_type = master_type 
        if self._master_type == I2CMasterType.AUTO_DETECT:
            self._master_type = self._auto_set_bus_master()

    def _auto_set_bus_master(self) -> I2CMasterType:
        detected_master = I2CMasterType.AUTO_DETECT
        if self._spm.is_studio:
            if self._bus_id == I2CBusID.User:
                detected_master = I2CMasterType.EMBEDDED_AVALON
            else:
                detected_master = I2CMasterType.EMBEDDED_LINUX
        else:
            if self._instance_id == I2CInstances.CONTROLLER:
                if self._bus_master._spm_root.get_controller_type() == self._bus_master._spm_root.ControllerType.CX:
                    if self._bus_master._spm_root.get_firmware_type() == self._bus_master._spm_root.FirmwareType.LINUX:
                        if self._bus_id == I2CBusID.User:
                            detected_master = I2CMasterType.EMBEDDED_AVALON
                        else:
                            detected_master = I2CMasterType.EMBEDDED_LINUX
                    else:
                        detected_master = I2CMasterType.EMBEDDED_AVALON
            elif self._instance_id == I2CInstances.MAIN_APP:
                detected_master = I2CMasterType.ACCESSORY_MASTER
        return detected_master

    def update_bus_parameter(self,  bus_id: I2CBusID, bus_speed: I2CBusSpeed):    
        self._bus_id = bus_id
        self._bus_speed = bus_speed

    def set_metadata(self, addr: int, offset_mode: I2COffsetMode, auto_lock: bool = True) -> Any:
        self._i2c_proxy.I2CSetupMetaDataEx(self._rx_packet_buffer_len, self._tx_packet_buffer_len, I2CSyncing.NoSync, I2CByteMode.SingleByteOff, self._bus_speed)
        self._i2c_proxy.I2CSetupMetaData(self._instance_id, self._master_type, self._bus_id, addr, offset_mode, auto_lock)
        return None
 
    def is_connected(self, metadata:I2CMetaData) -> bool:
        return self._i2c_proxy.I2CIsConnected > 0
    
    def write(self, metadata:I2CMetaData, offset:int, data:list[int]) -> int:
        done: bool = self._i2c_proxy.I2CWrite(offset, len(data), data)
        return 0 if done else -1
    
    def read(self, metadata:I2CMetaData, offset:int, data_count:int) -> list[int]:
        return list(self._i2c_proxy.I2CReadEx(offset, data_count)) 



class StudioBusAccess(I2CBusAccess):
    
    def __init__(self, parent:"I2CBusMaster", bus_id:I2CBusID, spm:Studio, instance_id, master_type):
        super().__init__(parent, bus_id)
        self._spm = spm
        self._instance_id = instance_id
        self._master_type  = master_type
        self._rx_packet_buffer_len  = 50
        self._tx_packet_buffer_len  = 50
        self._bus_speed = I2CBusSpeed.kHz_Default         
        self._obj_i2c = self._spm.workflow.i2c
        self._map_bus_type_to_studio_enum = {
            I2CMasterType.ACCESSORY_MASTER: self._obj_i2c.enums.Bus_types.mcp2221.value,
            I2CMasterType.EMBEDDED_AVALON: self._obj_i2c.enums.Bus_types.cx_user.value,
            I2CMasterType.EMBEDDED_LINUX: self._obj_i2c.enums.Bus_types.cx_linux.value,
        }
        self._map_bus_id_to_studio_enum = {
            I2CBusID.User: self._obj_i2c.enums.Bus_ids.user.value,
            I2CBusID.ScanHead: self._obj_i2c.enums.Bus_ids.scan_head.value,
            I2CBusID.Interface: self._obj_i2c.enums.Bus_ids.interface_box.value,
            I2CBusID.HV: self._obj_i2c.enums.Bus_ids.hv.value,
        }
        self._map_offset_mode_to_studio_enum = {
            I2COffsetMode.NoOffset: self._obj_i2c.enums.Offset_type.none.value,
            I2COffsetMode.U16Bit_LSBFiRST: self._obj_i2c.enums.Offset_type.u16lsb.value,
            I2COffsetMode.U16Bit_MSBFiRST: self._obj_i2c.enums.Offset_type.u16msb.value,
            I2COffsetMode.U8Bit: self._obj_i2c.enums.Offset_type.u8.value,
        }
        self._map_sync_mode_to_studio_enum = {
            I2CSyncing.NoSync: self._obj_i2c.enums.I2c_write_sync_mode.nosync.value,
            I2CSyncing.Sync: self._obj_i2c.enums.I2c_write_sync_mode.sync.value,
        }
        self._map_byte_mode_to_studio_enum = {
            I2CByteMode.SingleByteOff: self._obj_i2c.enums.I2c_single_byte_mode.off.value,
            I2CByteMode.SingleByteOn: self._obj_i2c.enums.I2c_single_byte_mode.on.value,
        }
        self._map_bus_speed_mode_to_studio_enum = {
            I2CBusSpeed.kHz_Default: self._obj_i2c.enums.I2c_speed.khz_default.value,
            I2CBusSpeed.kHz_100: self._obj_i2c.enums.I2c_speed.khz_100.value,
            I2CBusSpeed.kHz_200: self._obj_i2c.enums.I2c_speed.khz_200.value,
            I2CBusSpeed.kHz_400: self._obj_i2c.enums.I2c_speed.khz_400.value,
        }
        self._master_type = master_type 
        if self._master_type == I2CMasterType.AUTO_DETECT:
            self._master_type = self._auto_set_bus_master()

    def update_bus_parameter(self,  bus_id: I2CBusID, bus_speed: I2CBusSpeed):    
        self._bus_id = bus_id
        self._bus_speed = bus_speed

    def _auto_set_bus_master(self) -> I2CMasterType:
        detected_master = I2CMasterType.AUTO_DETECT
        if self._spm.is_studio:
            if self._bus_id == I2CBusID.User:
                detected_master = I2CMasterType.EMBEDDED_AVALON
            else:
                detected_master = I2CMasterType.EMBEDDED_LINUX
        else:
            if self._instance_id == I2CInstances.CONTROLLER:
                if self._bus_master._spm_root.get_controller_type() == self._bus_master._spm_root.ControllerType.CX:
                    if self._bus_master._spm_root.get_firmware_type() == self._bus_master._spm_root.FirmwareType.LINUX:
                        if self._bus_id == I2CBusID.User:
                            detected_master = I2CMasterType.EMBEDDED_AVALON
                        else:
                            detected_master = I2CMasterType.EMBEDDED_LINUX
                    else:
                        detected_master = I2CMasterType.EMBEDDED_AVALON
            elif self._instance_id == I2CInstances.MAIN_APP:
                detected_master = I2CMasterType.ACCESSORY_MASTER
        return detected_master

    def set_metadata(self, addr: int, offset_mode: I2COffsetMode, auto_lock: bool = True) -> Any:
        try:
            bus_type = self._map_bus_type_to_studio_enum[self._master_type]
        except Exception:
            raise ValueError(f"Selected bus master '{self._master_type}' is not available.")
        try:
            bus_id = self._map_bus_id_to_studio_enum[self._bus_id]
        except Exception:
            raise ValueError(f"Selected bus id '{self._bus_id}' is not available.")
        
        bus_addr = self._obj_i2c.map_bus_id_to_address(bus_type, bus_id)
        metadata = self._obj_i2c.create_metadata(bus_type, bus_addr, addr, convert_table=True, parse_tree=True)  
        metadata['offset_type'] = self._map_offset_mode_to_studio_enum[offset_mode]      
        metadata['auto_lock'] = auto_lock          
        metadata['max_length_rx'] = self._rx_packet_buffer_len          
        metadata['max_length_tx'] = self._tx_packet_buffer_len          
        metadata['write_sync_mode'] = self._map_sync_mode_to_studio_enum[I2CSyncing.NoSync]       
        metadata['single_byte_mode'] = self._map_byte_mode_to_studio_enum[I2CByteMode.SingleByteOff]         
        metadata['max_speed'] = self._map_bus_speed_mode_to_studio_enum[self._bus_speed]
        return metadata

    def is_connected(self, metadata:I2CMetaData) ->  bool:
        return self._obj_i2c.connected(metadata) > 0
    
    def write(self, metadata:I2CMetaData, offset:int, data:list[int]) -> int:
        return self._obj_i2c.write(metadata, offset, data)
    
    def read(self, metadata:I2CMetaData, offset:int, data_count:int) -> list[int]:
        return list(self._obj_i2c.read(metadata, offset, data_count)) 
