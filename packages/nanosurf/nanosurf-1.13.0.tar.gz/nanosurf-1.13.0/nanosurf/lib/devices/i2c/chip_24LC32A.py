"""Copyright (C) Nanosurf AG - All Rights Reserved (2021)
License - MIT"""


import time
import nanosurf.lib.devices.i2c.bus_master as i2c 

class Chip_24LC32A(i2c.I2CChip):
    """ EEPROM chip"""
    def __init__(self, bus_addr: int, **kwargs):
        super().__init__(bus_addr, offset_mode=i2c.I2COffsetMode.U16Bit_MSBFiRST, **kwargs)

    def memory_read_bytes(self, base_addr: int, len: int) -> list[int]:
        return self.read_bytes_with_offset(base_addr, len)

    def memory_write_bytes(self, base_addr: int, data: list[int]):
        page_size = 32
        page_base_addr = int(base_addr / page_size)

        # make sure the data array is block aligned, in base addr and size
        data_to_write: list[int] = []

        # if not fill it up at the beginning
        page_base_start_offset = base_addr % page_size
        if page_base_start_offset > 0:
            data_to_write = self.read_bytes_with_offset(page_base_addr, page_base_start_offset)
            data_to_write.extend(data)
        else:
            data_to_write = list(data)

        # fill up at the end
        missing_bytes = page_size - (len(data_to_write) % page_size)
        if missing_bytes > 0:
            missing_page_data = self.read_bytes_with_offset(page_base_addr+len(data_to_write), missing_bytes)
            data_to_write.extend(missing_page_data)

        # check if we did correctly prepare the data
        assert (page_base_addr % page_size) == 0, "Error: base addr is not page aligned"
        assert (len(data_to_write) % page_size) == 0, "Error: data array size is not multiple of page size"
        test = data_to_write[base_addr - page_base_addr:base_addr-page_base_addr+len(data)]
        assert test == data, "Error: data alignment failed"

        # writing data page by page
        bytes_to_send = len(data_to_write)
        pages_to_write = int(bytes_to_send / page_size)
        for current_page in range(pages_to_write):
            current_page_addr = page_base_addr + current_page*page_size
            current_data_start = current_page*page_size
            current_data_stop = (current_page+1)*page_size
            self.write_bytes_with_offset(current_page_addr, data_to_write[current_data_start:current_data_stop])
            time.sleep(0.5) # is needed to let the EEPROM finish internal write cycle

