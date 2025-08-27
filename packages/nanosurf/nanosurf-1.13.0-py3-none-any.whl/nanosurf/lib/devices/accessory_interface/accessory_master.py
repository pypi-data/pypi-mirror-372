"""Provide support for Nanosurf Accessory Interface Electronics
Copyright (C) Nanosurf AG - All Rights Reserved (2021)
License - MIT"""

from dataclasses import dataclass
import typing
import nanosurf.lib.devices.i2c.bus_master as i2c
from nanosurf.lib.devices.i2c import chip_PCA9548
from nanosurf.lib.devices.i2c.config_eeprom import DataSerializer, ConfigEEPROM


class GenericIDEEPROM(ConfigEEPROM):

    def __init__(self, bus_addr:int = 0x57, version:int=1) -> None: 
        super().__init__(bus_addr, version=version)
        self.bt_number = ""   
        self.sn_number = ""

    def serialize(self) -> bytearray:
        self._serialize_version()
        self._serialize(self.bt_number, DataSerializer.Formats.String)
        self._serialize(self.sn_number, DataSerializer.Formats.String)
        return self._write_data_bytes

    def deserialize(self, data:bytearray) -> bool:
        if self._deserialize_version(data) == 1:
            self.bt_number = typing.cast(str,self._deserialize(DataSerializer.Formats.String))
            self.sn_number = typing.cast(str,self._deserialize(DataSerializer.Formats.String))
        else:
            raise ValueError(f"Unknown layout version: {self._read_layout_version}")
        return True


@dataclass
class AccessoryNode:
    bus:'AccessoryBus' = None
    port:int = -1
    sub_port:int = -1
    
    def __repr__(self) -> str:
        return f"(port={self.port}, sub_port={self.sub_port})"

class AccessoryDevice():
    """ This class is the base class for all accessory compatible devices

    A minimal device implementation is the ID_EEPROM at reserved bus addr 0x57.
    Most of all other addresses are free for other device chips.
    Exceptions are: 0x70, 0x71, these are reserved to the bus multiplexers
    """
    Assigned_BTNumber = "BT00000"
    
    def __init__(self, bt_number:str="", serial_no:str = "", config:GenericIDEEPROM = None):
        """ This class stores the information found in the id eeprom of each slave device

            As standard identification a bt-number is read from the device
            Optional a serial number is provided

        Parameters
        ----------
        bt_number : string, optional
            identifier number of the device type. it has to be in the form of "BT00000"
            This BT number act as assigned BT number which identifies the type of the device.
            Normally it is provided from the child class as a constant 
        serial_no : string, optional
            identification serial number in form xxx-yy-zzzzzz
        config : GenericIDEEPROM, optional
            The type of configuration used in the specific device.
            If not provided it is assumed that it represents minimal the GenericIDEEPROM information
            which has a BTNumber and a SerialNo as content.
        """
        if config is None:
            config = GenericIDEEPROM()
        self.config = config
        self._assigned_bt_number = bt_number
        self._assigned_serial_no = serial_no
        self._bus_node:AccessoryNode = None
        self._is_connected = False

    def assign_bus(self, node : AccessoryNode):
        self._bus_node = node
        if self._bus_node is not None:
            self.assign_chip(self.config)
            self.register_chips()
            
    def assign_chip(self, chip:i2c.I2CChip):
        self._bus_node.bus.assign_chip(chip, self._bus_node.port, self._bus_node.sub_port)
    
    def connect(self, init_device:bool = True) -> bool:
        try:
            if self.is_connected(dont_use_cached_connection=True):
                if self._assigned_serial_no != "":
                    self._is_connected = self.config.sn_number == self._assigned_serial_no
            if self._is_connected and init_device:
                self.init_device()
                
            return self._is_connected
        except IOError:
            return False

    def is_connected(self, dont_use_cached_connection:bool = False) -> bool:
        if dont_use_cached_connection:
            self._is_connected = self.is_attached(check_assigned_bt_number=dont_use_cached_connection)
        return self._is_connected

    def is_attached(self, check_assigned_bt_number:bool=True) -> bool:
        if self._bus_node is None:
            return False
        
        is_attached = self.config.is_connected()

        if is_attached and check_assigned_bt_number:
            try:
                self.config.load_config()
                is_attached = ("" == self._assigned_bt_number) or (self.config.bt_number == self._assigned_bt_number)
            except IOError:
                is_attached = False
        return is_attached

    def register_chips(self):
        """This Function should be reimplemented by Device implementation class"""
        pass
    
    def init_device(self):
        """This Function should be reimplemented by Device implementation class"""
        pass

    def get_assigned_bt_number(self) -> str:
        return self._assigned_bt_number

    def get_bt_number(self) -> str:
        """ Returns the slave devices identification string.
            It's usual form is "BTxxxxx"

        Returns
        -------
        bt_number: str
            identification string

        """
        # check if bt number is already read, otherwise read eeprom content
        if len(self.config.bt_number) <= 0:
            self.config.load_config()
        return self.config.bt_number

    def get_serial_number(self) -> str:
        """ Return the slave devices (optional) serial number.
            It's usual form is "xxx-xx-xxx"

         Returns
         -------
            serial_number: str
                 serial number as string or empty string if no serial number is defined

        """
        # check if bt number is already read, otherwise read eeprom content
        if len(self.config.sn_number) <= 0: 
            self.config.load_config()
        return self.config.sn_number

    def get_assigned_serial_number(self) -> str:
        return self._assigned_serial_no

    def get_bus_node(self) -> AccessoryNode:
        return self._bus_node
    
    def initialize_id_eeprom(self, serial_no:str, bt_number:str=None, config:GenericIDEEPROM = None) -> bool:
        """ Writes a initial configuration to eeprom. Handle with care!
            If a configuration is passed then this is written to the eeprom, else the own current configuration
        """
        if self._bus_node is None:
            raise IOError("Access to device without assigned bus_node!")
        
        if config is None:
            config = self.config
            
        if bt_number is None:
            bt_number = self._assigned_bt_number

        if not bt_number.startswith("BT") or len(bt_number) != 7:
            raise ValueError("bt_number must have the format BT01234")
        if len(serial_no) < 10 or len(serial_no) > 11:
            raise ValueError("serial_no must have the format 000-00-000")
        config.bt_number = bt_number
        config.sn_number = serial_no
            
        self.assign_chip(config)
        done = config.store_config()
        return done


class AccessoryBus(i2c.I2CBusMaster):
    """ This is the main class to get access to accessory devices connected to an accessory bus (AB). 
        Devices can be connected directly to the bus, after a bus multiplexer or even a secondary multiplexer

        Connect to a AB by its bus number. Then access to a slave device of this AI can be granted by select_port()

        slave devices are identified by get_slave_device_id().
        To talk to a slave device, specific class drivers have to be build based on class AccessoryDevice.

    """
    def __init__(self, bus_id:i2c._I2CBusID):
        """ This is the main class to get access to an accessory interface (AI) and its slave devices.

        Parameters
        ----------
        bus_id
            reference to the i2c bus id provided from host operating system 

        """
        super().__init__(spm_root=None, bus_id=bus_id, 
            instance_id=i2c.I2CInstances.CONTROLLER, 
            master_type=i2c.I2CMasterType.ACCESSORY_MASTER, 
            bus_speed=i2c.I2CBusSpeed.kHz_Default)
        self._active_port = -1
        self._active_sub_port = -1
        self._chip_mux_primary:chip_PCA9548.Chip_PCA9548 = None 
        self._chip_mux_secondary:chip_PCA9548.Chip_PCA9548 = None 
        self._available_ports = 0

    def init_bus(self):
        self._active_port = -1

        # check if a bus multiplexer is there
        self._chip_mux_primary = chip_PCA9548.Chip_PCA9548(0x70)
        self.assign_chip(self._chip_mux_primary, port=-1, sub_port=-1)
        self._chip_mux_secondary = chip_PCA9548.Chip_PCA9548(0x71)
        self.assign_chip(self._chip_mux_secondary, port=-1, sub_port=0)

        if self._chip_mux_primary.is_connected():
            self._available_ports = self._read_primary_port_count()
        else:
            self._available_ports = 1

        if self._chip_mux_secondary.is_connected():
            self._available_sub_ports = self._read_secondary_port_count(-1)
        else:
            self._available_sub_ports = 0
            
        self.select_port(1,1 if self._available_sub_ports > 0 else -1)
        

    def _read_primary_port_count(self) -> int:
        return 6

    def _read_secondary_port_count(self, primary_port:int = -1) -> int:
        """ read the amount of secondary port provided my port switch (if any)

            Parameter
            ---------
            primary_port:int, optional
                if -1 is provided the actual selected port is used
                if port number is > 0 then these port is checked
                port number 0 is not allowed
                if port number is higher that available ports, a ValueError is raised

            Result
            ------
            port_count:int
                if a switch is detected the number of available sub_ports are returned,
                if no switch is detected 0, is returned
                if argument of primary_port is not valid -1 is returned
        """
        if primary_port != -1:
            if self._chip_mux_primary.is_connected():
                assert primary_port == 0, "Port 0 is for internal use only and cannot be activated"
                if primary_port > self._available_ports:
                    raise ValueError("Parameter primary port is out of range")
            else:
                raise ValueError("Parameter primary port is selected without primary port chip detected.")
            
        old_port = self._active_port
        old_sub_port = self._active_sub_port
        self.select_port(primary_port,0)
            
        sub_ports_detected = 0    
        if not self._chip_mux_secondary.is_connected():
            sub_ports_detected = 0
        else:
            sub_ports_detected = self._read_gss_switch_port_count()
            
        if not (old_port == primary_port and old_sub_port == 0):
            self.select_port(old_port,old_sub_port)
        return sub_ports_detected

    def _read_gss_switch_port_count(self) -> int:
        return 4
    
    def get_port_count(self) -> int:
        """ return the number of primary ports the connected interface has

        Returns
        -------
        int
            number of primary ports available on this accessory bus

        """
        return self._available_ports

    def get_sub_port_count(self) -> int:
        self._available_sub_ports = self._read_secondary_port_count(-1)
        return self._available_sub_ports

    def get_bus_addr(self) -> int:
        """ returns the communication bus address. Used for further I2C communication with a slave

        Returns
        -------
        int
            bus_address - identification number to be used for I2C communication

        """
        return self._bus_id

    def select_port(self, port: int = -1, sub_port:int = -1):
        """ opens the port to communication with a slave device at port
            Only one port at a given time can be selected. all further slave communication goes through the selected port
            Port 0 is assigned to accessory interface internal configuration and should be used carefully

        Parameters
        ----------
        port : int
            identification number of the port to be used, -1 to keep the current value
        sub_port : int
            identification number of the sub-port to be used. -1 if keep the current value
        """

        if port >= 0:
            self._active_port = port
            self._chip_mux_primary.reg_control = 1 << port

        if sub_port >= 0:
            self.assign_chip(self._chip_mux_secondary, port = self._active_port, sub_port = sub_port)
            self._active_sub_port = sub_port
            self._chip_mux_secondary.reg_control = 1 << sub_port
       

    def is_any_device_attached(self) -> bool:
        """ check if a device of any type is connected to selected port

        Returns
        -------
        bool
            returns True if a device is found on selected port, otherwise False

        """
        device = self.get_generic_device()
        return device.is_attached(check_assigned_bt_number=False)

    def get_generic_device(self) -> AccessoryDevice:
        """ read the identification information from the device on selected port
            The information is read from the id eeprom and stored in a AISlaveIDHeader class

         input:
            none
         return:
            device - a generic AccessoryDevice class 
        """
        device = AccessoryDevice(bt_number="")
        self.assign_device_to_current_port(device)
        _ = device.is_attached(check_assigned_bt_number=False)
        return device
    
    def assign_device(self, device:AccessoryDevice, primary_port:int, secondary:int=-1):
        """ assign a device to a port of this bus"""
        device.assign_bus(AccessoryNode(bus=self, port=primary_port, sub_port=secondary))

    def assign_device_to_current_port(self, device:AccessoryDevice):
        """ assign a device to current selected port"""
        self.assign_device(device, self._active_port, self._active_sub_port)
        
    def lookup_device(self, bt_number:str = "", serial_nr: str = "", device:AccessoryDevice=None) -> bool:
        """ Search for a device with given serial-number and assign "device" to it

            Parameters:
            -----------
            bt_number: str, optional
                The bt_number of the device to find. Need the form 'BTxxxxx'
            serial_nr: str, optional
                The serial number of the device to find. Need the form 'xxx-yy-zzz'
            device: AccessoryDevice, optional
                If device pointer is given, assign it to found port

            returns True if device with given serial number and/or bt_number could be found, otherwise False
        """
        try:
            for port_nr in range(1, self.get_port_count()+1):
                self.select_port(port_nr, -1)
                sub_ports = [-1] if (sub_port_count := self.get_sub_port_count()) == 0 else range(0, sub_port_count+1) 
                for sub_port_nr in sub_ports:
                    self.select_port(port_nr, sub_port_nr)
                    if self.is_any_device_attached():
                        dev = self.get_generic_device()
                        self.assign_device_to_current_port(dev)
                        if dev.is_attached(check_assigned_bt_number=False):
                            found = True
                            if bt_number != "":
                                found &= bt_number == dev.get_bt_number()
                            if serial_nr != "":
                                found &= serial_nr == dev.get_serial_number()
                            if found:
                                if device is not None:
                                    self.assign_device_to_current_port(device)
                                    found &= device.is_attached()
                                return found
        except IOError:
            pass
        return False
    
    def lookup_attached_devices(self) -> list[AccessoryDevice]:
        """ scan the bus and returns a list of all found devices"""
        dev_list:list[AccessoryDevice] = []
        try:
            for port_nr in range(1, self.get_port_count()+1):
                self.select_port(port_nr, -1)
                sub_ports = [-1] if (sub_port_count := self.get_sub_port_count()) == 0 else range(0, sub_port_count+1) 
                for sub_port_nr in sub_ports:
                    self.select_port(port_nr, sub_port_nr)
                    if self.is_any_device_attached():
                        dev = self.get_generic_device()
                        self.assign_device_to_current_port(dev)
                        dev_list.append(dev)
        except IOError:
            pass
        return dev_list
        
    
    def get_current_port(self) -> int:
        return self._active_port

    def get_current_sub_port(self) -> int:
        return self._active_sub_port

    def assign_chip(self, chip: 'i2c.I2CChip', port: int = -1, sub_port:int = -1):
        """ Tell the software that a certain 'chip' is connected to current or specific port
        
        Parameters:
        -----------
        chip: class of I2CChip 
        port: int  
            if no port number is given (or -1) then  assume the chip is connected to current selected port
        """
        chip.assigned_primary_port = port if port>=0 else self._active_port
        chip.assigned_secondary_port = sub_port if sub_port>=0 else self._active_sub_port
        super().assign_chip(chip)


    # overwrite base functions to support automatic port switching-----------------------------------------

    def activate_chip(self, chip: 'i2c.I2CChip'):
        if  (chip.assigned_primary_port != self._active_port) or (chip.assigned_secondary_port != self._active_sub_port):
            self.select_port(chip.assigned_primary_port, chip.assigned_secondary_port)
        super().activate_chip(chip)
