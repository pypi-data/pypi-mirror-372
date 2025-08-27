
"""
Device driver for DS28E07 - A onw-wire bus EEPROM
Implementation needs a i2C bus converter chip DS2484 as interface.  
Implementation works only with single one-wire chip attached to DS2484
For more detail see data sheet

Copyright (C) Nanosurf AG - All Rights Reserved (2024)
License - MIT
"""

import enum
from nanosurf.lib.devices.i2c.chip_DS2484 import Chip_DS2484
        
class Chip_DS28E07(Chip_DS2484):
    """ OneWire EEPROM 1kBit"""
    
    class _MemoryCommand(enum.IntEnum):
        Write_Scratchpad = 0x0F
        Read_Scratchpad  = 0xAA
        Copy_Scratchpad  = 0x55
        Read_Memory     = 0xF0

    class _OneWireCommand(enum.IntEnum):
        Read_Rom     = 0x33
        Match_Rom    = 0x55
        Search_Rom   = 0xF0
        Skip_Rom     = 0xCC
        Resume       = 0xA5
        OD_Skip_Rom  = 0x3C
        OD_Match_Rom = 0x69

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.write_block_len = 8

    def _write_block_memory(self, address: int, block_data: list[int]) -> bool:
        """ write single block of data to chip.  """
        assert len(block_data) == self.write_block_len, f"Memory write block error: Assumed {self.write_block_len} bytes, but got {len(block_data)} bytes."
        addr_lo_byte =  address & 0xFF
        addr_hi_byte = (address >> 8) & 0xFF
        
        # Step 1 - Write to Scratchpad
        self.one_wire_reset()
        self.one_wire_write_bytes( [self._OneWireCommand.Skip_Rom, self._MemoryCommand.Write_Scratchpad, addr_lo_byte, addr_hi_byte ] + block_data)
        read_res = self.one_wire_read_bytes(3)
        read_ok = read_res[2] == 0xFF
        #print("Write Scratchpad: Done \t CRC: " + str((read[0] << 8) +  read[1]) + " FFLoop: " + str(read[2]))
        
        # Step 2 - Read from Scratchpad
        self.one_wire_reset()
        self.one_wire_write_bytes( [self._OneWireCommand.Skip_Rom, self._MemoryCommand.Read_Scratchpad])
        scratchpad = self.one_wire_read_bytes(14) # 2x Address, 1x EsByte, 8x Data, 2x CRC, 1x FFLoop
        transfer_add_stat = scratchpad[0:3]
        #print("Read Scratchpad: Done \t  Address: " + str(scratchpad[0:2]) + " Number of Bytes: " + str(scratchpad[2]+1) + " Data: " + str(scratchpad[3:11]) + " CRC: " + str((scratchpad[12] << 8) +  scratchpad[13]))
        
        # step 3 -Copy Scratchpad
        self.one_wire_reset()
        self.one_wire_write_bytes( [self._OneWireCommand.Skip_Rom, self._MemoryCommand.Copy_Scratchpad] + transfer_add_stat )
        transfer_stat = self.one_wire_read_bytes(1)
        return transfer_stat[0] == 0xAA

    def memory_read_bytes(self, base_addr: int, len: int) -> list[int]:
        """ read memory locations starting at base_address. len  defines number of bytes to read"""
        addr_lo_byte =  base_addr & 0xFF
        addr_hi_byte = (base_addr >> 8) & 0xFF
        self.one_wire_reset()
        self.one_wire_write_bytes([self._OneWireCommand.Skip_Rom, self._MemoryCommand.Read_Memory, addr_lo_byte, addr_hi_byte])
        return self.one_wire_read_bytes(len)
    
    def memory_write_bytes(self, base_addr: int, data: list[int]) -> bool:
        """ write byte array in 'data' to memory, starting at address defined by 'base_addr' """
        page_size = self.write_block_len
        page_base_addr = int(base_addr / page_size)* page_size

        # make sure the data array is block aligned, in base addr and size
        data_to_write: list[int] = []

        # if not fill it up at the beginning
        page_base_start_offset = base_addr % page_size
        if page_base_start_offset > 0:
            data_to_write = self.memory_read_bytes(page_base_addr, page_base_start_offset)
            data_to_write.extend(data)
        else:
            data_to_write = list(data)

        # fill up at the end
        data_bytes_in_last_page = len(data_to_write) % page_size
        if data_bytes_in_last_page > 0:
            missing_bytes = page_size - data_bytes_in_last_page
            missing_page_data = self.memory_read_bytes(page_base_addr+len(data_to_write), missing_bytes)
            data_to_write.extend(missing_page_data)

        # check if we did correctly prepare the data
        assert (page_base_addr % page_size) == 0, "Error: base addr is not page aligned"
        assert (len(data_to_write) % page_size) == 0, "Error: data array size is not multiple of page size"
        test = data_to_write[base_addr - page_base_addr:base_addr-page_base_addr+len(data)]
        assert test == data, "Error: data alignment failed"

        # writing data page by page
        ok = True
        bytes_to_send = len(data_to_write)
        pages_to_write = int(bytes_to_send / page_size)
        for current_page in range(pages_to_write):
            current_page_addr = page_base_addr + current_page*page_size
            current_data_start = current_page*page_size
            current_data_stop = (current_page+1)*page_size
            ok &= self._write_block_memory(current_page_addr, data_to_write[current_data_start:current_data_stop])
            if not ok:
                break
        return ok


