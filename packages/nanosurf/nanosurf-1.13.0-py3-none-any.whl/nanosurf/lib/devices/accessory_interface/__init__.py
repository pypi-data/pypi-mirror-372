"""Provide support for Nanosurf Accessory Interface Electronics
Copyright (C) Nanosurf AG - All Rights Reserved (2021)
License - MIT"""

from array import array
from typing import Union
import platform

if platform.system() == "Windows":
    from nanosurf.lib.spm.com_proxy import Spm
    from nanosurf.lib.spm.studio import Studio

    import nanosurf.lib.devices.i2c.bus_master as i2c
    import nanosurf.lib.devices.i2c.chip_24LC32A as chip_24LC32A
    import nanosurf.lib.devices.i2c.chip_PCA9548 as chip_PCA9548


    class AISlaveIDHeader:
        """ This class stores the information found in the id eeprom of each slave device"""

        def __init__(self, binaryarray: list = [int]):
            """ This class stores the information found in the id eeprom of each slave device

                As standart identification a bt-number is read from the device
                Optional a serial number is provided

            Parameters
            ----------
            binaryarray : array of byte data, optional
                data array (e.g. read from eeprom) to be decoded and filled into the class structure
            """

            self._version = 0
            self._bt_number = ""
            self._serial_no = ""
            self.decode_eeprom_data(binaryarray)

        def decode_eeprom_data(self, binaryarray: list[int]):
            """ This function can extract the id header information stored in a binary data stream, normally read from a id eeprom.
                The information is stored as class variables and can be ready by accessor functions

            Parameters
            ----------
            binaryarray : array of byte data, optional
                data array (e.g. read from eeprom) to be decoded and filled into the class structure

        """
            if len(binaryarray) > 10:
                self._version = binaryarray[0]
                assert self._version == 1, "AISlaveIDHeader: unknown id header version detected."
                try:
                    self._bt_number = array('B', binaryarray[2:2+binaryarray[1]]).tobytes().decode()
                    if binaryarray[9] > 0:
                        self._serial_no = array('B', binaryarray[10:10+binaryarray[9]]).tobytes().decode()
                    else:
                        self._serial_no = ""
                except Exception:
                    self._serial_no = ""
                    self._bt_number =""
                
        
        def get_bt_number(self) -> str:
            """ Returns the slave devices identification string.
                It's usual form is "BTxxxxx"

            Returns
            -------
            bt_number: str
                identification string

            """
            return self._bt_number

        def get_serial_number(self) -> str:
            """ Return the slave devices (optional) serial number.
                It's usual form is "xxx-xx-xxx"

            Returns
            -------
                serial_number: str
                    serial number as string or empty string if no serial number is defined

            """
            return self._serial_no

    class AccessoryInterface(i2c.I2CBusMaster):
        """ This is the main class to get access to an accessory interface (AI) and its slave devices.

            Connect to a know AI by its serial-no, or scan first for available AIs, or connect to first found
            Then access to a slave device of this AI can be etablished by select_port()

            slave devices are identified by get_slave_device_id().
            To talk to a slave device, specific classes have to be build.

        """
        def __init__(self, spm: "Union[Studio, Spm]"):
            """ This is the main class to get access to an accessory interface (AI) and its slave devices.

            Parameters
            ----------
            spm
                reference to the connected spm COM class for MobileS or a reference to studio 

            """
            if isinstance(spm, Studio):
                raise NotImplementedError("Studio support for Accessory Master is not implemented yet")
            
            super().__init__(spm_root=spm, bus_id=i2c.I2CBusID.Unassigned, 
                instance_id=i2c.I2CInstances.MAIN_APP, 
                master_type=i2c.I2CMasterType.ACCESSORY_MASTER, 
                bus_speed=i2c.I2CBusSpeed.kHz_200)
            self._i2c_proxy = self._bus_access._i2c_proxy
            self._own_id_header = AISlaveIDHeader()
            self._active_port = -1
            self._chip_bus_switch = chip_PCA9548.Chip_PCA9548(0x70)
            self.assign_chip(self._chip_bus_switch, port=0)

        def get_list_of_available_interfaces(self) -> list[str]:
            """ Searches for attached accessory interfaces and create list of available devices
                Have to be called at least once before a connect() can be done

            Returns
            ------
            list of str
                list of serial numbers of all found accessory interfaces

            """
            self._list_of_found_ai = []

            count_ai = self._i2c_proxy.GetAccessoryInterfaceInUseCount
            for i in range(count_ai):
                self._list_of_found_ai.append(self._i2c_proxy.GetAccessoryInterfaceInUseSerial(i))

            count_ai = self._i2c_proxy.GetAccessoryInterfaceAvailableCount
            for i in range(count_ai):
                self._list_of_found_ai.append(self._i2c_proxy.GetAccessoryInterfaceAvailableSerial(i))

            return self._list_of_found_ai

        def connect(self, serial_no: str = "") -> bool:
            """ connect this instance to a accessory interface identified by device serial-number

            Parameters
            ----------
            serial_no : str, optional
                serial-number of accessory interface to be connected to. If omitted it connects to fist AI found

            Returns
            ------
            Bool
                true if connection could be set up

            """
            self._bus_id = i2c.I2CBusID.Unassigned # no connection
            self._active_port = -1

            # without given serial number we try auto detection
            if serial_no == "":
                self.get_list_of_available_interfaces()
                if len(self._list_of_found_ai) > 0:
                    serial_no = self._list_of_found_ai[0]

            # setup connection
            try:
                self._bus_id = self.get_bus_addr_of_ai_device(serial_no)
                self._bus_access.update_bus_parameter(self._bus_id, self._bus_speed)

                # if connection could be done read and store device information
                if self._bus_id != i2c.I2CBusID.Unassigned:
                    self.select_port(0) # port 0 is the internal port with self identification eeprom
                    self._own_id_header = self.get_slave_device_id()
                else:
                    self._own_id_header = AISlaveIDHeader()

                self.select_port(1) # default port

            except AssertionError:
                self._own_id_header = AISlaveIDHeader()
                self._bus_id = i2c.I2CBusID.Unassigned

            self.assign_i2c_bus(self._bus_id, self._bus_speed)
            return self._bus_id != i2c.I2CBusID.Unassigned

        def get_port_count(self) -> int:
            """ return the number of slave port the connected interface has

            Returns
            -------
            int
                number of ports available on this accessory interface

            """
            known_ai_devices = {"BT07172": 5}
            if self._own_id_header.get_bt_number() in known_ai_devices:
                return known_ai_devices[self._own_id_header.get_bt_number()]
            else:
                return 0

        def get_serial_number(self) -> str:
            """ returns the serial number of the connected accessory interface

            Returns
            -------
            str
                Onw serial_number as a string in the form "xxx-yy-zzz" or empty string if not connected

            """
            return self._own_id_header.get_serial_number()

        def get_bus_addr(self) -> int:
            """ returns the communication bus address. Used for further I2C communication with a slave

            Returns
            -------
            int
                bus_address - identification number to be used for I2C communication

            """
            return self._bus_id

        def select_port(self, port_nr: int):
            """ opens the port to communication with a slave device at port
                Only one port at a given time can be selected. all further slave communication goes through the selected port
                Port 0 is assigned to accessory interface internal configuration and should be used carefully

            Parameters
            ----------
            port_nr : int
                identification number of the port to be used
            """
            assert self._bus_id != i2c.I2CBusID.Unassigned, "Accessory Interface: Error: Slave Access, but connection not assigned"
            self._active_port = port_nr
            self._chip_bus_switch.reg_control = 1 << port_nr

        def is_slave_device_connected(self) -> bool:
            """ check if a slave device is connected to selected port
                It looks if the id eeprom can be found

            Returns
            -------
            bool
                returns True if a device is found on selected port, otherwise False

            """

            assert self._bus_id != i2c.I2CBusID.Unassigned, "Accessory Interface: Error: Slave Access, but connection not assigned"
            id_eeprom = chip_24LC32A.Chip_24LC32A(0x57) 
            self.assign_chip(id_eeprom)
            return id_eeprom.is_connected()

        def get_slave_device_id(self) -> AISlaveIDHeader:
            """ read the identification information from the device on selected port
                The information is read from the id eeprom and stored in a AISlaveIDHeader class

            input:
                none
            return:
                slave_id - AISlaveIDHeader class type with the retrieved information
            """
            assert self._bus_id != i2c.I2CBusID.Unassigned, "Accessory Interface: Error: Slave Access, but connection not assigned"
            id_eeprom = chip_24LC32A.Chip_24LC32A(0x57) 
            self.assign_chip(id_eeprom)
            id_eeprom_data = id_eeprom.memory_read_bytes(0, 20)
            return AISlaveIDHeader(id_eeprom_data)

        def select_port_with_slave(self, serial_nr: str) -> bool:
            """ Auto select the port where a device with 'serial_nr' is connected

                Parameters:
                -----------
                serial_nr: str
                    The serial number of the connected device to find. Need the form 'xxx-yy-zzz'

                returns True if found otherwise False
            """
            device_found = False
            try:
                for port_nr in range(1, self.get_port_count()+1):
                    self.select_port(port_nr)
                    if self.is_slave_device_connected():
                        slave_id = self.get_slave_device_id()
                        if serial_nr == slave_id.get_serial_number():
                            device_found = True
                            break
            except AssertionError:
                pass
            return device_found

        def get_current_port(self) -> int:
            return self._active_port

        def assign_chip(self, chip: 'I2CChip', port: int = -1):
            """ Tell the software that a certain 'chip' is connected to current or specific port
            
            Parameters:
            -----------
            chip: class of I2CChip 
            port: int  
                if no port number is given (or -1) then  assume the chip is connected to current selected port
            """
            chip.assigned_ai_port = port if port>=0 else self._active_port
            super().assign_chip(chip)

        def get_bus_addr_of_ai_device(self, serial_no: str) -> int:
            """ returns the bus_address to a accessory interface with provided serial_no

            Parameters
            ----------
            serial_no : str
                serial-number of accessory interface to provide the bus_adr

            Returns
            ------
            bus_adr: int
                bus_adr of AI with provided serial_no or a negative number if AI was not found

            """

            found_bus_addr = i2c.I2CBusID.Unassigned # init return value

            # search for bus address of given serial number in list of InUse devices
            count_ai = self._i2c_proxy.GetAccessoryInterfaceInUseCount
            for i in range(count_ai):
                if serial_no == self._i2c_proxy.GetAccessoryInterfaceInUseSerial(i):
                    found_bus_addr = self._i2c_proxy.GetAccessoryInterfaceInUseI2CBus(i)
                    break

            # if not found, search in list of free devices
            if found_bus_addr == i2c.I2CBusID.Unassigned:
                count_ai = self._i2c_proxy.GetAccessoryInterfaceAvailableCount
                for i in range(count_ai):
                    if serial_no == self._i2c_proxy.GetAccessoryInterfaceAvailableSerial(i):
                        found_bus_addr = self._i2c_proxy.ActivateAccessoryInterfaceAvailable(i)
                        break

            return found_bus_addr

        # overwrite base functions to support automatic port switching-----------------------------------------

        def activate_chip(self, chip: 'I2CChip'):
            if  chip.assigned_ai_port != self._active_port:
                self.select_port(chip.assigned_ai_port)
            super().activate_chip(chip)
