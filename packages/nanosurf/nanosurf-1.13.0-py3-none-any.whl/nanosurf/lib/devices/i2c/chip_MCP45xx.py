
"""Copyright (C) Nanosurf AG - All Rights Reserved (2021)
License - MIT"""

import enum
import nanosurf.lib.devices.i2c.bus_master as i2c 

class Chip_MCP45XX(i2c.I2CChip):
    """ 7/8 bit Single Digital potentiometer chip.
        Details see data sheet of MCP453X/455X from Microchip Technology 
    """

    class TCON_BITS(enum.IntEnum):
        POT_0_TERMINAL_B_CONNECTED = 0x01
        POT_0_WIPER_CONNECTED      = 0x02
        POT_0_TERMINAL_A_CONNECTED = 0x04
        POT_0_HW_ENABLED           = 0x08
        POT_1_TERMINAL_B_CONNECTED = 0x10
        POT_1_WIPER_CONNECTED      = 0x20
        POT_1_TERMINAL_A_CONNECTED = 0x40
        POT_1_HW_ENABLED           = 0x80

    class _MCP_Command(enum.IntEnum):
        Command_Write = 0
        Command_Inc   = 1
        Command_Dec   = 2
        Command_Read  = 3
        
    def __init__(self, bus_addr: int, **kwargs):
        super().__init__(bus_addr, i2c.I2COffsetMode.NoOffset, **kwargs)

    def _assemble_command_byte(self, mem_address: int, command: _MCP_Command, data_value: int) -> int:
        command_byte = mem_address*16 + command.value*4 + int(data_value / 256)
        return command_byte

    def read_wiper_position(self) -> int:
        self.write_byte(self._assemble_command_byte(0x00, self._MCP_Command.Command_Read, 0))
        high_byte, low_byte = self.read_bytes(2)
        return high_byte*256 + low_byte

    def set_wiper_position(self, position: int):
        self.write_bytes([self._assemble_command_byte(0x00, self._MCP_Command.Command_Write, position), int(position & 0x00ff)])

    def increment_wiper_position(self):
        self.write_byte(self._assemble_command_byte(0x00, self._MCP_Command.Command_Inc, 0))

    def decrement_wiper_position(self):
        self.write_byte(self._assemble_command_byte(0x00, self._MCP_Command.Command_Dec, 0))

    @property
    def reg_tcon(self) -> int:
        self.write_byte(self._assemble_command_byte(0x04, self._MCP_Command.Command_Read, 0))
        _, low_byte = self.read_bytes(2)
        return low_byte

    @reg_tcon.setter
    def reg_tcon(self, bit_mask: int):
        self.write_bytes([self._assemble_command_byte(0x04, self._MCP_Command.Command_Write, 0), bit_mask])


