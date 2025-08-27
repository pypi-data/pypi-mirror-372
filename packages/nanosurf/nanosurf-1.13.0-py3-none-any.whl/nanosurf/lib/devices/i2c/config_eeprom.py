"""Accessory Interface port scanner to demonstrate usage of Accessor_Interface Module
Copyright (C) Nanosurf AG - All Rights Reserved (2021)
License - MIT"""

import enum
import struct
from typing import Any, Callable, Optional, cast
import array
import nanosurf.lib.devices.i2c as i2c

class DataSerializer():
    class Formats(enum.Enum):
        String = enum.auto()
        Int8 = enum.auto()
        Int16 = enum.auto()
        Int32 = enum.auto()
        Double = enum.auto()
        
    def __init__(self, version: int = 1, max_string_size: int = 16) -> None:
        self._write_layout_version = version
        self._max_string_size = max_string_size
        self._read_layout_version = 0
        self._write_data_bytes = bytearray()
        self._read_data_bytes = bytearray()
        self._read_index = -1
        self._estimate_size = False
        self._init_write_buffer()

    def write_to(self, write_func:Callable[[type[bytearray]], bool]) -> bool:
        self._init_write_buffer()
        data = self.serialize()
        done = False
        try: 
            write_func(data)
            done = True
        except Exception:
            pass
        return done

    def read_from(self, read_func:Callable[[int], type[bytearray]]) -> bool:
        done = False
        try:
            len = self.estimate_buffer_size()
            data = read_func(len)
            if not isinstance(data, bytearray):
                data = bytearray(data)
            done = self.deserialize(data)
        except Exception as e:
            print(e)
        return done
    
    def _init_write_buffer(self):
        self._write_data_bytes.clear()

    def _deserialize_version(self, data:bytearray):
        if self._estimate_size:
            self._read_layout_version = self._write_layout_version
        else:
            self._read_data_bytes = data
            self._read_index = 0
            self._read_layout_version = self._deserialize(DataSerializer.Formats.Int8)
        return self._read_layout_version
        
    def _serialize_version(self):
        self._serialize(self._write_layout_version, DataSerializer.Formats.Int8)

    def _serialize(self, val: Any | list[Any], t:Formats, list_size:Optional[int] = None) -> int:
        """ Returns number of bytes added """
        start_size = len(self._write_data_bytes)

        if isinstance(val, list):
            if list_size is None:
                raise ValueError("Missing parameter 'list_size' for values of type 'list'")
            self._write_data_bytes.extend([list_size])
            for i in range(list_size):
                self._serialize(val[i], t)
        else:
            if t == DataSerializer.Formats.String:
                if self._estimate_size:
                    val = val.ljust(self._max_string_size)
                byte_data = bytearray(cast(str,val[:self._max_string_size]), encoding="UTF-8")
                self._write_data_bytes.extend([len(byte_data)])
                self._write_data_bytes.extend(byte_data)
            elif t == DataSerializer.Formats.Int8:
                byte_data = struct.pack("b", val)
                self._write_data_bytes.extend(byte_data)
            elif t == DataSerializer.Formats.Int16:
                byte_data = struct.pack("<h", val)
                self._write_data_bytes.extend(byte_data)
            elif t == DataSerializer.Formats.Int32:
                byte_data = struct.pack("<i", val)
                self._write_data_bytes.extend(byte_data)
            elif t == DataSerializer.Formats.Double:
                byte_data = struct.pack("d", val)
                self._write_data_bytes.extend(byte_data)
            else:
                raise TypeError("Unknown Type defined in parameter 't'")
        return len(self._write_data_bytes) - start_size

    
    def _deserialize(self, t:Formats, list_size:Optional[int] = None) -> Any | list[Any]:
        if list_size is not None:
            stored_size = int(self._read_data_bytes[self._read_index])
            assert stored_size == list_size, f"Data storage size differ from expected size: Found {stored_size}, expected {list_size}."
            self._read_index += 1
            res = []
            for i in range(stored_size):
                res.append(self._deserialize(t))
            return res
        else:
            if t == DataSerializer.Formats.String:
                len = int(self._read_data_bytes[self._read_index])
                self._read_index += 1
                read_str = array.array('B', self._read_data_bytes[self._read_index:self._read_index+len]).tobytes().decode()
                self._read_index += len
                return read_str
            elif t == DataSerializer.Formats.Int8:
                len = struct.calcsize("b")
                byte_data, *_ = struct.unpack("b", self._read_data_bytes[self._read_index:self._read_index+len])
                self._read_index += len
                return int(byte_data)
            elif t == DataSerializer.Formats.Int16:
                len = struct.calcsize("h")
                word_data, *_ = struct.unpack("<h", self._read_data_bytes[self._read_index:self._read_index+len])
                self._read_index += len
                return int(word_data)
            elif t == DataSerializer.Formats.Int32:
                len = struct.calcsize("i")
                long_data, *_ = struct.unpack("<i", self._read_data_bytes[self._read_index:self._read_index+len])
                self._read_index += len
                return int(long_data)
            elif t == DataSerializer.Formats.Double:
                len = struct.calcsize("d")
                double_data, *_ = struct.unpack("d", self._read_data_bytes[self._read_index:self._read_index+len])
                self._read_index += len
                return double_data
            else:
                raise TypeError("Unknown Type defined in parameter 't'")
            return 0
    
    def estimate_buffer_size(self) -> int:
        self._estimate_size = True
        self._init_write_buffer()
        self.serialize()
        self._estimate_size = False
        return len(self._write_data_bytes) 
    
    def serialize(self) -> bytearray:
        raise NotImplementedError("This function has to be overwritten by subclass")
    
    def deserialize(self, data:bytearray):
        raise NotImplementedError("This function has to be overwritten by subclass")


class ConfigEEPROM(i2c.Chip_24LC32A, DataSerializer):
    def __init__(self, bus_addr: int, version:int, **kwargs):
        i2c.Chip_24LC32A.__init__(self,bus_addr, **kwargs)
        DataSerializer.__init__(self, version, **kwargs)

    def load_config(self) -> bool:
        return self.read_from(lambda len : self.memory_read_bytes(0x00, len))

    def store_config(self) -> bool:
        return self.write_to(lambda data : self.memory_write_bytes(0x00, list(data)))

