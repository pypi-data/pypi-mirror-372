"""Nanosurf nhf-file reader implementation for studio data
Copyright (C) Nanosurf AG - All Rights Reserved (2023)
License - MIT"""

import typing
from typing import Optional, Tuple, Any
import enum
import pathlib 
import re
import json
import numpy as np
import numpy.ma as ma
import h5py
from nanosurf.lib.datatypes import sci_val

class _CalMapType(enum.Enum):
    Linear                = enum.auto()
    Linear_Non_Invertible = enum.auto()
    Exponential           = enum.auto()
    Logarithmic           = enum.auto()
    Linear_Interpolation  = enum.auto()

class _CalNode():
    """ A CalcNode stores the information on how to convert a dataset from one signal into another.
        Attention: The naming convention for source and sink is swapped from the the 'signal_source_id' and signal_sink_id' convention used in the hdf file!
        In a CalcNode the parameters defined in map_par are used to convert sink = f(source).
        Only if 'calc_sink_from_source' is False it's swapped and source = f(sink) is calculated with the parameter are used to reverse the calculation
        Note: Not all conversion type defined in 'map_type' can be reversed!
    """
    def __init__(self, uuid:str, sink_name:str, unit:str, map_type:_CalMapType, map_par:list[float], calc_sink_from_source:bool, source_name:str):
        self.uuid = uuid
        self.sink_name = sink_name
        self.unit = unit
        self.source_name = source_name
        self.map_type = map_type
        self.map_par = map_par
        self.calc_sink_from_source = calc_sink_from_source

    def apply_calibration(self, source_data:np.ndarray) -> np.ndarray:
        if self.map_type == _CalMapType.Linear:
            a = self.map_par[0]
            b = self.map_par[1]
            if (a == 1.0) and (b == 0.0):
                return source_data
            else:
                if self.calc_sink_from_source:
                    return source_data * a + b
                else:
                    return (source_data - b)/a
        elif self.map_type == _CalMapType.Linear_Non_Invertible:
            a = self.map_par[0]
            b = self.map_par[1]
            if self.calc_sink_from_source:
                if (a == 1.0) and (b == 0.0):
                   return source_data
                else:
                   return source_data * a + b
            else:
                raise TypeError("Error: Unsupported calibration direction 'left_to_right' for Linear_Non_Invertible map type detected")    
        elif self.map_type == _CalMapType.Exponential:
            a = self.map_par[0]
            b = self.map_par[1]
            c = self.map_par[2]
            if self.calc_sink_from_source:
                return b * np.exp((source_data-c)/a)
            else:
                return a * np.log(source_data/b) + c  
        elif self.map_type == _CalMapType.Logarithmic:
            a = self.map_par[0]
            b = self.map_par[1]
            c = self.map_par[2]
            if self.calc_sink_from_source:
                return a * np.log(source_data/b) + c
            else:
                return b * np.exp((source_data-c)/a)  
        else:
            raise TypeError(f"Error: Unsupported calibration node type: {self.map_type=} detected")        

class NHFMeasurementType(enum.Enum):
    Undefined = enum.auto()
    Unknown = enum.auto()
    Image = enum.auto()
    Spectroscopy = enum.auto()
    WaveModeNMA = enum.auto()

def _default_verbose_output_handler(msg:str):
    print(msg)

def extract_unit(text_with_unit:str) -> str:
    def _isolate_unit(text_with_unit:str) -> str:
        """ Extracts the unit from a text string containing the unit in parentheses (e.g 'Meter (m)' return 'm')
            if no parentheses are found the returned string is empty.
        """
        si_unit = ""
        matches  = re.findall(r'\(([^\)]+)\)',text_with_unit)
        try:
            si_unit = matches[0]
        except IndexError:
            pass
        return si_unit      

    si_unit = _isolate_unit(text_with_unit)
    if si_unit == "":
        si_unit = text_with_unit
    return si_unit   

def get_attributes(instance: h5py.File |h5py.Group | h5py.Dataset) -> dict[str, Any]:
    """ Iterates over the attributes of the given instance and puts them to a dictionary.
    If the attribute for the data type is available, data type specific information is stored.

    Parameters
    ----------

        instance: h5py.File | h5py.Group | h5py.Dataset
            Instance within the .nhf file to be read.

    Return
    ------
        attributes_dict: dict
            Contains the attributes of the analyzed instance.

    """
    if not isinstance(instance, (h5py.File, h5py.Group, h5py.Dataset)):
        raise TypeError("Not supported type of instance provided")
    
    attributes_dict: dict = {}
    for attributes_key, attributes_val in instance.attrs.items():
        attributes_dict[attributes_key] = attributes_val
    return attributes_dict

def _get_sub_items_by_name(instance: h5py.File | h5py.Group, identifiers: list[str]) -> dict[str, str]:
    """ Reads the names of the sub items of the given instance and puts them to a dict, where key - segment id, value- segment name

    Parameters
    ----------

        instance: h5py.File | h5py.Group | h5py.Dataset
            Instance within the .nhf file to be read.
        identifiers: list of strings
            The attribute which identifies the items by its name

    Return
    ------
        item_names: dict
            Contains the names to the given instance.
            key - segment id, value- segment name

    """
    if isinstance(instance, (h5py.File, h5py.Group)):
        item_names: dict[str, str] = {}
        for seg_key in instance.keys():
            for id_name in identifiers:
                try:
                    item_names[seg_key] = str(instance[seg_key].attrs[id_name])
                    break
                except KeyError:
                    pass # try next name
        return item_names
    else:
        return None

def _get_unidentified_sub_groups(instance: h5py.File | h5py.Group, known_names: dict[str, str]) -> dict[str, h5py.Group]:
    """ Reads the names of the sub items of the given instance which are not already identified by the known_name dict and puts them into a dict
    """
    if isinstance(instance, (h5py.File, h5py.Group)):
        if known_names is None:
            known_names = {}
        item_names: dict[str, h5py.Group] = {}
        for seg_key in instance.keys():
            seg_key:str
            if seg_key not in known_names: 
                if isinstance(instance[seg_key],h5py.Group):
                    item_names[seg_key] = typing.cast(h5py.Group,instance[seg_key])
                    sub_groups = _get_unidentified_sub_groups(item_names[seg_key],{})
                    if sub_groups is not None:
                        item_names[seg_key].groups = sub_groups
                    sub_dataset = _get_unidentified_sub_dataset(item_names[seg_key],{})
                    if sub_dataset is not None:
                        item_names[seg_key].datasets = sub_dataset
        return item_names
    else:
        return None 
            
def _get_unidentified_sub_dataset(instance: h5py.File | h5py.Group, known_names: dict[str, str]) -> dict[str, h5py.Dataset]:
    """ Reads the names of the datasets of the given instance which are not already identified by the known_name dict and puts them into a dict
    """
    if isinstance(instance, h5py.File) or isinstance(instance, h5py.Group):
        if known_names is None:
            known_names = {}
        item_names: dict[str, h5py.Dataset] = {}
        for seg_key in instance.keys():
            seg_key:str
            if seg_key not in known_names: 
                if isinstance(instance[seg_key],h5py.Dataset):
                    item_names[seg_key] = typing.cast(h5py.Dataset,instance[seg_key])
        return item_names
    else:
        return None 
            

class NHFDataset():
    def __init__(self, parent:'NHFSegment|NHFMeasurement', h5_dataset:h5py.Dataset, delay_load_of_data_from_file:bool=True) -> None:
        self.parent = parent
        self.h5_dataset = h5_dataset
        self.attribute = get_attributes(self.h5_dataset)
        self._inject_data_conversion_attributes()
        if delay_load_of_data_from_file:
            # type hint is only correct after scale_dataset_to_physical_units() is called at data read time
            self.dataset:np.ndarray = self.h5_dataset # type: ignore
        else:
            self.dataset = self._convert_h5py_dataset_to_numpy_array(self.h5_dataset)
        self.cached_signal_id = ""

    def has_nan_values(self) -> bool:
        nan_val = self.get_nan_value() 
        if np.isnan(nan_val): 
            # nan values cannot be looked up by simple 'val in array' method 
            has_nan = len(np.argwhere(np.isnan(self.dataset))) > 0
        else:
            has_nan = nan_val in self.dataset
        return has_nan

    def get_nan_value(self) -> float:
        nan_value = np.nan
        if 'target_nan_value' in self.attribute:
            nan_value = self.attribute['target_nan_value']
        return nan_value

    def get_masked_dataset(self, fill_value=None) -> ma.MaskedArray:
        if 'target_nan_value' in self.attribute:
            nan_value = self.attribute['target_nan_value']
            if np.isnan(nan_value): 
                # nan values cannot be found and replaced by simple masked_values() method 
                masked_dataset:ma.MaskedArray = ma.masked_array(data=self.dataset[:], mask=np.isnan(self.dataset), fill_value = np.finfo(np.float64).min, copy=True, shrink=True)  
            else:
                masked_dataset:ma.MaskedArray = ma.masked_values(self.dataset[:], value=nan_value, copy=True, shrink=True)  
        else:
            masked_dataset = ma.array(self.dataset, copy=True, shrink=True)  

        if fill_value is not None:
            masked_dataset.filled(fill_value)
            self.attribute['target_nan_value'] = fill_value        
        return masked_dataset
    
    def _convert_h5py_dataset_to_numpy_array(self,h5_dataset:h5py.Dataset) -> np.ndarray:
        if 'type_nan_value' in self.attribute:
            self.attribute['target_nan_value'] = self.attribute['type_nan_value'] 
        return np.array(h5_dataset, dtype=np.float64)
    
    def _need_conversion_to_physical_unit(self, target_signal_id:Optional[str]=None) -> bool:
        """ Returns True if data conversion to target signal is not yet done. . 
        """
        if extract_unit(self.attribute['signal_unit'])  == 'int' and extract_unit(self.attribute['signal_calibration_unit']) == 'int':
            return False
        else:
            if target_signal_id is not None:
                return target_signal_id != self.attribute["target_signal_id"]
            else:
                try:
                    _ = self.attribute['signal_calibration_min']
                    _ = self.attribute['signal_calibration_max']
                    _ = self.attribute['type_min']
                    _ = self.attribute['type_max']
                    return True
                except KeyError:
                    pass
        return False
    
    def _scale_with_calibration_attributes_of_dataset(self):
        try:
            signal_min = typing.cast(float,self.attribute['signal_calibration_min'])
            signal_max = typing.cast(float,self.attribute['signal_calibration_max'])
            type_min = typing.cast(float,self.attribute['type_min'])
            type_max = typing.cast(float,self.attribute['type_max'])
        except KeyError:
            signal_min = 0.0
            signal_max = 1.0
            type_min = 0.0
            type_max = 1.0
        
        try:
            calibration_factor = (signal_max - signal_min) / (type_max-type_min)
        except ZeroDivisionError:
            calibration_factor = 1.0
            signal_min = 0.0
            type_min = 0.0

        self.attribute['target_signal_unit'] = self.attribute['signal_calibration_unit']
        self.attribute['target_signal_id'] = self.attribute['signal_name']
        
        # prepare destination dataset with raw date
        self.dataset = self._convert_h5py_dataset_to_numpy_array(self.h5_dataset)

        # calculate scaling from dataset
        if self.has_nan_values():
            self.attribute['target_nan_value'] = self.attribute['type_nan_value'] 
            masked_dataset = self.get_masked_dataset()
            masked_dataset = typing.cast(ma.MaskedArray,(masked_dataset[:] - type_min) * calibration_factor + signal_min)
            nan_value = np.iinfo(np.int32).min if self.unit == 'int' else np.finfo(masked_dataset.dtype).min
            self.dataset = ma.filled(masked_dataset, fill_value=nan_value)
            self.attribute['target_nan_value'] = nan_value
        else:
            self.dataset = (self.dataset[:] - type_min) * calibration_factor + signal_min

    def get_default_signal(self) -> str | None:
        target_signal_id = None
        try:
            target_signal_id = self.attribute["signal_selected"]
            source_signal_id = self.attribute["signal_id"]
            if target_signal_id == source_signal_id:
                return None
        except KeyError:
            pass
        return target_signal_id
    
    def calc_dataset_by_calibration_graph(self, calibration_graph:list[int]):
        assert self.parent._file_hdl.cal_group is not None, "Missing calibration group in file"
        cal_nodes = self.parent._file_hdl.cal_group.calibration_nodes

        self.attribute['target_signal_unit'] = cal_nodes[calibration_graph[-1]].unit
        self.attribute['target_signal_id']   = cal_nodes[calibration_graph[-1]].sink_name

        # prepare destination dataset with raw date
        self.dataset = self._convert_h5py_dataset_to_numpy_array(self.h5_dataset)

        if self.has_nan_values():
            masked_dataset = self.get_masked_dataset()

            # follow the calibration graph and update dataset
            for node_index in calibration_graph:
                masked_dataset = cal_nodes[node_index].apply_calibration(masked_dataset)

            nan_value = np.iinfo(np.int32).min if self.unit == 'int' else np.finfo(masked_dataset.dtype).min
            self.dataset = ma.filled(masked_dataset, fill_value=nan_value)
            self.attribute['target_nan_value'] = nan_value
        else:
            # follow the calibration graph and update dataset
            for node_index in calibration_graph:
                self.dataset = cal_nodes[node_index].apply_calibration(self.dataset)

    def _scale_with_calibration_graph(self, target_signal_id:str):
        calibration_graph = self._build_calibration_graph(target_signal_id)
        if len(calibration_graph) < 1:
            raise IOError(f"Could not find a calibration named '{target_signal_id}' for channel named '{self.attribute['signal_name']}' ")
        self.calc_dataset_by_calibration_graph(calibration_graph)
        
    def _build_calibration_graph(self, target_signal_id:str) -> list[int]:
        assert self.parent._file_hdl.cal_group is not None, "Missing calibration group in file"
        calibration_graph = []
        try:
            source_signal_id = self.attribute["signal_id"]
            calibration_graph = self.parent._file_hdl.cal_group.build_calibration_graph(source_signal_id, target_signal_id)
        except KeyError as e:
            raise IOError(f"Missing complete signal calibration information for {self.attribute['name']}. Reason: {e}")
        return calibration_graph
    
    def _get_calib_node_by_index(self, node_index:int) -> _CalNode:
        assert self.parent._file_hdl.cal_group is not None, "Missing calibration group in file"
        return self.parent._file_hdl.cal_group.calibration_nodes[node_index]

    def _find_calibration_nodes_by_uuid(self, uuid:str) -> list[_CalNode]:
        assert self.parent._file_hdl.cal_group is not None, "Missing calibration group in file"
        all_nodes = self.parent._file_hdl.cal_group.calibration_nodes
        found_nodes = [node for node in all_nodes if node.uuid == uuid]
        return found_nodes
    
    def _load_dataset_without_conversion(self, target_signal_id:Optional[str], handle_nan:bool=False):
        if target_signal_id is None:
            target_signal_id = self.attribute['signal_name']

        self.dataset = self._convert_h5py_dataset_to_numpy_array(self.h5_dataset)

        self.attribute['target_signal_unit'] = self.attribute['signal_calibration_unit']
        self.attribute['target_signal_id'] = target_signal_id

        if handle_nan and self.has_nan_values():
            masked_dataset = self.get_masked_dataset()
            nan_value = np.iinfo(np.int32).min if self.unit == 'int' else np.finfo(masked_dataset.dtype).min
            self.dataset = ma.filled(masked_dataset, fill_value=nan_value)
            self.attribute['target_nan_value'] = nan_value

        
    def _load_dataset_with_physical_unit(self, target_signal_id:Optional[str] = None) -> None:
        """ If scaling information are provided in the Dataset, apply them.
        Converts the bit pattern of the saved raw data to the value of the given datatype saved in the attributes
        and scales it with the given calibration values.

        Attention: 
            'dataset' is read from file in this process, which can last long depending on array size.
            Also dataset is converted from h5py dataset into numpy.ndarray
        """
        if target_signal_id is None:
            target_signal_id = self.get_default_signal()

        if target_signal_id is None:
            self._scale_with_calibration_attributes_of_dataset()
        else:
            self._scale_with_calibration_graph(target_signal_id)

    def read_data(self, with_signal:Optional[str]=None):
        """If target is omitted default signal is used"""
        if with_signal is None:
            with_signal = self.get_default_signal()

        if self.cached_signal_id != with_signal:
            if self._need_conversion_to_physical_unit(with_signal):
                self._load_dataset_with_physical_unit(with_signal)
            else:
                self._load_dataset_without_conversion(with_signal, handle_nan=True)

            if self.unit == 'int':
                self.dataset = self.dataset.astype(dtype=np.int32)
        
        self.cached_signal_id = with_signal

    def signals(self) -> set[str]:
        cal_targets:set[str] = set()
        cal_map = self._create_unit_to_signal_map()
        cal_targets.update(cal_map.values())
        return cal_targets

    def units(self) -> set[str]:
        cal_targets_units:set[str] = set()
        cal_map = self._create_unit_to_signal_map()
        cal_targets_units.update(cal_map.keys())
        return cal_targets_units

    def get_signal_from_unit(self, unit:str) -> str:
        cal_targets = self._create_unit_to_signal_map()
        if unit in cal_targets:
            return cal_targets[unit]
        return ""

    def _create_unit_to_signal_map(self) -> dict[str,str]:
        cal_targets:dict[str,str] = {}
        file_version = self.parent._file_hdl.version()
        if  file_version >= (2,0) and file_version < (3,0):
            uuids:list[str] = []
            if "signal_calibration_source" in self.attribute:
                uuids.append(self.attribute["signal_calibration_source"])
            elif "signal_calibration_source_0" in self.attribute:
                index = 0
                while (attr_node_name:=f"signal_calibration_source_{index}") in self.attribute:
                    uuids.append(self.attribute[attr_node_name])
                    index += 1
            elif "signal_selected" in self.attribute:
                uuids.append(self.attribute["signal_selected"])
            elif "signal_id" in self.attribute:
                uuids.append(self.attribute["signal_id"])

            for uuid in uuids:
                cal_nodes = self._find_calibration_nodes_by_uuid(uuid)
                for cal_node in cal_nodes:
                    cal_targets[extract_unit(cal_node.unit)] = cal_node.sink_name
        elif file_version >= (1,0) and file_version < (2,0):
            cal_targets[self.attribute["signal_unit"]] = "" # no calibration signals defined in version 1.x
        return cal_targets

    @property
    def unit(self) -> str:
        try:
            si_unit = extract_unit(self.attribute['target_signal_unit'])
        except KeyError:
            si_unit = ""
        return si_unit   

    @property
    def name(self) -> str:
        my_name = ""
        try:
            my_name = self.attribute['signal_name']
        except KeyError:
            try:
                my_name = self.attribute['name']
            except KeyError:
                my_name = ""
        return my_name

    @property
    def dataset_size_x(self) -> int:
        return self.parent.dataset_size_x

    @property
    def dataset_size_y(self) -> int:
        return self.parent.dataset_size_y

    @property
    def dataset_offset_x(self) -> float:
        return self.parent.dataset_offset_x

    @property
    def dataset_offset_y(self) -> float:
        return self.parent.dataset_offset_y

    @property
    def dataset_range_x(self) -> float:
        return self.parent.dataset_range_x

    @property
    def dataset_range_y(self) -> float:
        return self.parent.dataset_range_y
    
    @property
    def dataset_rotation_z(self) -> float:
        return self.parent.dataset_rotation_z

    @property
    def measurement_type(self) -> NHFMeasurementType:
        return self.parent.measurement_type

    def _inject_data_conversion_attributes(self):
        """ Search for attributes defining information about data value scaling 

        Parameters
        ----------
            attr_dict: dict
                dictionary to be analyzed and populate with conversion information.
        """
        if 'dataset_element_type' in self.attribute:
            element_type = self.attribute['dataset_element_type']
            if isinstance(element_type, str): # file version 2.x
                    try:
                        self.attribute['type_min']      = NHFFileReader.dataset_element_type_defined_as_str[element_type][0]
                        self.attribute['type_max']      = NHFFileReader.dataset_element_type_defined_as_str[element_type][1]
                        self.attribute['type']          = NHFFileReader.dataset_element_type_defined_as_str[element_type][2]
                        self.attribute['type_nan_value']= self.h5_dataset.fillvalue #NHFFileReader.dataset_element_type_defined_as_str[element_type][3]                         
                    except  IndexError:
                        raise IOError(f"Unknown dataset_element_type '{element_type}'. ")
                    
                    if 'signal_name' in self.attribute:
                        if 'signal_calibration_unit' not in self.attribute:
                            self.attribute['signal_calibration_unit'] = ""
                        if 'signal_calibration_max' not in self.attribute:
                            self.attribute['signal_calibration_max'] = 1.0
                        if 'signal_calibration_min' not in self.attribute:
                            self.attribute['signal_calibration_min'] = 0.0
            else: # file version 1.x
                try:
                    self.attribute['type_min'] = NHFFileReader.dataset_element_type_defined_as_int[element_type][0]
                    self.attribute['type_max'] = NHFFileReader.dataset_element_type_defined_as_int[element_type][1]
                    self.attribute['type']     = NHFFileReader.dataset_element_type_defined_as_int[element_type][2]
                except IndexError:
                    raise IOError(f"Unknown dataset_element_type number {element_type}. ")
                
                try:
                    if 'base_calibration_unit' in self.attribute:
                        self.attribute['signal_name'] = self.attribute['name']
                        self.attribute['signal_unit'] = self.attribute['base_calibration_unit']
                        self.attribute['signal_calibration_unit'] = self.attribute['base_calibration_unit']
                        self.attribute['signal_calibration_max'] = self.attribute['base_calibration_max']
                        self.attribute['signal_calibration_min'] = self.attribute['base_calibration_min']
                except KeyError:
                    raise IOError(f"Missing complete signal calibration information for {self.attribute['name']}")

        self.attribute['target_signal_unit'] = ""
        self.attribute['target_signal_id'] = ""
        
    def convert_to_matrix(self,size_x:int, size_y:int):
        self.dataset = np.flipud(np.reshape(np.array(self.dataset), (size_y, size_x)))

class NHFProperties():
    def __init__(self) -> None:
        pass

class NHFSegment():
    def __init__(self, parent: 'NHFMeasurement', name: str, file_hdl: 'NHFFileReader', hdf_group:h5py.Group) -> None:
        self._name = name
        self._file_hdl = file_hdl
        self._hdf_group = hdf_group
        self.parent = parent
        self.channel: dict[str, NHFDataset] = {}
        self.h5_groups: dict[str, h5py.Group] = {}
        self.h5_datasets: dict[str, h5py.Dataset] = {}
        self.property = NHFProperties()
        self.attribute = get_attributes(self._hdf_group) 
        self._dataset_size = (0,0)
        self._dataset_range = (0.0,0.0)
        self._dataset_offset = (0.0,0.0)
        self._dataset_rotation = 0.0
        self._inject_segment_configuration_properties(known_identifiers=['segment_configuration', 'scan_configuration'])
        # cached values for related properties, will be calculated by first call
        self._spec_offsets:np.ndarray = None # type: ignore
        self._spec_data_points:np.ndarray = None # type: ignore

    @property
    def name(self) -> str:
        return self._name
    
    @property
    def channels(self) -> list[NHFDataset]:
        return list(self.channel.values())
    
    @property
    def groups(self) -> list[h5py.Group]:
        return list(self.h5_groups.values())
    
    @property
    def datasets(self) -> list[h5py.Dataset]:
        return list(self.h5_datasets.values())
    
    @property
    def dataset_size_x(self) -> int:
        return self._dataset_size[0]

    @property
    def dataset_size_y(self) -> int:
        return self._dataset_size[1]

    @property
    def dataset_offset_x(self) -> float:
        return self._dataset_offset[0]

    @property
    def dataset_offset_y(self) -> float:
        return self._dataset_offset[1]

    @property
    def dataset_range_x(self) -> float:
        return self._dataset_range[0]

    @property
    def dataset_range_y(self) -> float:
        return self._dataset_range[1]

    @property
    def dataset_rotation_z(self) -> float:
        return self._dataset_rotation

    @property
    def measurement_type(self) -> NHFMeasurementType:
        return self.parent.measurement_type
    
    @property
    def spec_offsets(self) -> np.ndarray:
        if self._spec_offsets is None:
            self._calc_spec_offset_and_data_points()
        return self._spec_offsets
    
    @property
    def spec_data_points(self) -> np.ndarray:
        if self._spec_data_points is None:
            self._calc_spec_offset_and_data_points()
        return self._spec_data_points

    def _calc_spec_offset_and_data_points(self):
        if self._file_hdl.version() >= (2,0):
            block_size_source = self.channels[0].attribute["dataset_block_size_source"]
            dataset_with_block_sizes = self.find_dataset_by_attribute_value("dataset_block_size_id", block_size_source)
            if dataset_with_block_sizes:
                self._spec_offsets = np.insert(np.cumsum(dataset_with_block_sizes), 0, 0) 
                self._spec_data_points = np.diff(self._spec_offsets)  
        else: # version 1 files
            self._spec_offsets = self.read_channel('channel_data_offsets').dataset
            self._spec_data_points = self.read_channel('number_of_datapoints_acquired').dataset

    def channel_signals(self, ch:str | int) -> set[str]:
        nhf_dataset = None
        if isinstance(ch, str):
            nhf_dataset = self.channel[ch]
        elif isinstance(ch, int):
            nhf_dataset = self.channels[ch]
        else:
            raise TypeError(f"Parameter 'ch' has not supported data type of '{type(ch)}'")       
        return nhf_dataset.signals()        

    def channel_units(self, ch:str | int) -> set[str]:
        nhf_dataset = None
        if isinstance(ch, str):
            nhf_dataset = self.channel[ch]
        elif isinstance(ch, int):
            nhf_dataset = self.channels[ch]
        else:
            raise TypeError(f"Parameter 'ch' has not supported data type of '{type(ch)}'")       
        return nhf_dataset.units()        

    def read_channel(self, ch:str | int, as_matrix:bool=False, with_signal:Optional[str]=None, with_unit:Optional[str]=None) -> NHFDataset:
        """ Loads a specified data channel by name or index.
            The data provided by physical units as specified in the file's calibration information.

            For file version 2.0 and newer multiple calibrations per channel are possible. 
            The default calibration and unit is defined by the selected signal at the time of file storage.
            
            Returns:
            --------
                NHFDataset:
                    A class holding the channel data itself and supplementary information (e.g. unit)
                    If a channel has invalid numbers (e.g., not measured data points) these numbers are converted to NHFDataset.get_nan_value(). 
                    One can check if such numbers are in the data set by NHFDataset.has_nan_values(). 
                    If there are NaN values, a masked data array can be provided by NHFDataSet.get_masked_dataset() to process only valid data points.

            Parameters:
            ------------
            ch: str, int
                Define the channel to load by its name or its index.

            as_matrix: bool, optional
                If set to True, the dataset is converted to a 2D numpy array. Otherwise, the data is a 1D array

            with_signal: str, optional
                If a signal name is provided, the corresponding calibration is used for the channel. 
                If not defined, the channels default signal is used.
                Possible signals can be accessed by self.channel_signals()

            with_unit: str, optional
                If a unit name is provided, the corresponding calibration is used for the channel. 
                If not defined, the channels default unit is used.
                Possible signals can be read by self.channel_units()
        """
        nhf_dataset = None
        if isinstance(ch, str):
            nhf_dataset = self.channel[ch]
        elif isinstance(ch, int):
            nhf_dataset = self.channels[ch]
        else:
            raise TypeError(f"Parameter 'ch' has not supported data type of '{type(ch)}'")
        
        if (with_signal is not None) and self._file_hdl.version() < (2,0):
            raise ValueError("Parameter 'as_signal' is not supported by file version below 2.0")

        if (with_unit is not None) and self._file_hdl.version() < (2,0):
            if with_unit in nhf_dataset.units(): # only default unit can be selected
                with_unit = None # 'None' selects default unit
            else:
                raise ValueError(f"Channel '{ch} does not contain calibration information for selected unit '{with_unit}'") 
        
        if with_unit is not None:
            known_units = nhf_dataset.units()
            if with_unit in known_units:
                with_signal = nhf_dataset.get_signal_from_unit(with_unit)
                if with_signal == "":
                    raise RuntimeError(f"Error: A target_id for known unit '{with_unit}' was not found.") 
            else:
                raise ValueError(f"Channel '{ch} does not contain calibration information for selected unit '{with_unit}'") 
                
        nhf_dataset.read_data(with_signal) 

        if as_matrix:
            if self._dataset_size == (0,0):
                raise ValueError("No size information stored in segment. Dataset cannot be converted to matrix.")
            nhf_dataset.convert_to_matrix(size_x=self.dataset_size_x, size_y=self.dataset_size_y)
        return nhf_dataset
    
    def channel_list(self) -> list[str]:
        return list(self.channel.keys())
    
    def channel_name(self, index: int) -> str:
        return self.channel_list()[index]
    
    def channel_count(self) -> int:
        return len(self.channel)
    
    def group_count(self) -> int:
        return len(self.h5_groups)        

    def group_list(self) -> list[str]:
        return list(self.h5_groups.keys())

    def group_name(self, key: int) -> str:
        return list(self.h5_groups.keys())[key]

    def dataset_count(self) -> int:
        return len(self.h5_datasets)
        
    def dataset_name(self, key: int) -> str:
        return list(self.h5_datasets.keys())[key]

    def find_dataset_by_attribute_value(self, attr_name:str, attr_value:Any) -> h5py.Dataset | None:
        for dataset in self.h5_datasets.values():
            if attr_name in dataset.attrs:
                if dataset.attrs[attr_name] == attr_value:
                    return dataset
        for channel in self.channels:
            if attr_name in channel.attribute:
                if channel.attribute[attr_name] == attr_value:
                    return channel.h5_dataset
        return None
    
    def find_group_by_attribute_value(self, attr_name:str, attr_value:Any) -> h5py.Group | None:
        for gr in self.h5_groups.values():
            if attr_name in gr.attrs:
                if gr.attrs[attr_name] == attr_value:
                    return gr
        return None
    
    def read_dataset_size(self) -> Tuple[int, int]:
        rect_axis_size = (0,0)
        try:
            points_per_line = int(self.attribute['image_points_per_line'])
            number_of_lines = int(self.attribute['image_number_of_lines'])
            rect_axis_size = (points_per_line, number_of_lines)
        except KeyError:
            pass
        try:
            points_per_line = int(self.attribute["grid_number_of_columns"])
            number_of_lines = int(self.attribute["grid_number_of_rows"])
            rect_axis_size = (points_per_line, number_of_lines)   
        except KeyError:
            pass         
        try:
            points_per_line = int(self.attribute["rect_axis_size"][1])
            number_of_lines = int(self.attribute["rect_axis_size"][0])
            rect_axis_size = (points_per_line, number_of_lines)   
        except KeyError:
            pass         
        return rect_axis_size
    
    def read_dataset_range(self) -> Tuple[float, float]:
        rect_axis_range = (0.0,0.0)
        try:
            range_x = float(self.attribute['image_size_x'])
            range_y = float(self.attribute['image_size_y'])
            rect_axis_range = (range_x, range_y)
        except KeyError:
            pass
        try:
            range_x = float(self.attribute["rect_axis_range"][1])
            range_y = float(self.attribute["rect_axis_range"][0])
            rect_axis_range = (range_x, range_y)   
        except KeyError:
            pass         
        try:
            range_x = self.attribute["grid_width"]
            range_y = self.attribute["grid_height"]
            rect_axis_range = (range_x, range_y)   
        except KeyError:
            pass         
        return rect_axis_range

    def read_dataset_offset(self) -> Tuple[float, float]:
        rect_axis_offset = (0.0,0.0)
        try:
            offset_x = float(self.attribute['scanner_offset_x'])
            offset_y = float(self.attribute['scanner_offset_y'])
            rect_axis_offset = (offset_x, offset_y)
        except KeyError:
            pass
        return rect_axis_offset

    def read_dataset_rotation(self) -> float:
        rotation_z = 0.0
        try:
            rotation_z = float(self.attribute['rect_rotation'])
        except KeyError:
            pass
        try:
            rotation_z = float(self.attribute['scanner_rotation'])
        except KeyError:
            pass
        return rotation_z

    def _read_segment_structure(self):
        # read known dataset as 'channels'
        channel_identifier = 'signal_name' if self._file_hdl.version() >= (2,0) else 'name'        
        dataset_names = _get_sub_items_by_name(self._hdf_group, identifiers=[channel_identifier])
        if dataset_names:
            for dataset_id, dataset_name in dataset_names.items():
                h5_dataset = typing.cast(h5py.Dataset,self._hdf_group[dataset_id])
                self.channel[dataset_name] = NHFDataset(self,h5_dataset)
        
        # read unknown dataset as 'group'
        self.h5_groups = _get_unidentified_sub_groups(self._hdf_group, dataset_names)
        self.h5_datasets = _get_unidentified_sub_dataset(self._hdf_group, dataset_names)
        self._dataset_size = self.read_dataset_size()
        self._dataset_range = self.read_dataset_range()
        self._dataset_offset = self.read_dataset_offset()
        self._dataset_rotation = self.read_dataset_rotation()
                
    def _inject_segment_configuration_properties(self, known_identifiers: list[str]):
        for identifier in known_identifiers:
            if identifier in  self.attribute:
                segment_config = json.loads(self.attribute[identifier])
                if 'property' in segment_config:
                    for prop_name, prop_value in segment_config['property'].items():
                            if isinstance(prop_value, dict) and 'value' in prop_value:
                                try: # to create a SciVal access to property
                                    # prepare value and unit
                                    prop_value['value'] = float(prop_value['value'])
                                    if 'unit' not in prop_value:
                                        prop_value['unit'] = ""

                                    # create attribute access to properties
                                    if prop_name not in self.attribute:
                                        self.attribute[prop_name] = prop_value
                                    else:
                                        self._file_hdl.print_verbose(f"Warning: Cannot create property '{prop_name}'. Attribute already exists")
    
                                    setattr(self.property,prop_name,sci_val.SciVal(value=prop_value['value'], unit_str=extract_unit(prop_value['unit'])))
                                except Exception:
                                    # properties seems not to be a number 
                                    if prop_name not in self.attribute:
                                        self.attribute[prop_name] = prop_value['value']
                                    else:
                                        self._file_hdl.print_verbose(f"Warning: Cannot create property '{prop_name}'. Attribute already exists")
                            else:
                                self._file_hdl.print_verbose(f"Warning: Unexpected property format of type '{type(prop_value)}' found")

class NHFMeasurement(NHFSegment):
    def __init__(self, name: str, file_hdl: 'NHFFileReader', hdf_group:h5py.Group) -> None:
        super().__init__(self, name, file_hdl, hdf_group)
        self.segment: dict[str, NHFSegment] = {}
        self._measurement_type = NHFMeasurementType.Undefined

    @property
    def segments(self) -> list[NHFSegment]:
        return list(self.segment.values())
    
    def segment_list(self) -> list[str]:
        return list(self.segment.keys())
    
    def segment_name(self, key: int) -> str:
        return self.segment_list()[key]
    
    def segment_count(self) -> int:
        return len(self.segment)
    
    @property
    def measurement_type(self) -> NHFMeasurementType:
        return self._detect_group_type()
    
    def read_dataset_size(self) -> Tuple[int, int]:
        size = super().read_dataset_size()
        if (0,0) == size:
            for seg in self.segment.values():
                size = seg.read_dataset_size()
                if size != (0,0):
                    break
        return size
    
    def _detect_group_type(self) -> NHFMeasurementType:
        if self._measurement_type == NHFMeasurementType.Undefined:
            match self._file_hdl.version():
                case (2,_):
                    measurement_type_map = {
                        'image_line_based': NHFMeasurementType.Image,
                        'spectroscopy':     NHFMeasurementType.Spectroscopy,
                        'wavemode_nma':     NHFMeasurementType.WaveModeNMA
                    }
                    try:
                        self._measurement_type = measurement_type_map[self.attribute['group_type']]
                    except KeyError:
                        self._measurement_type = NHFMeasurementType.Unknown
                case (1,1):
                    measurement_type_map = {
                        'image_line_based':   NHFMeasurementType.Image,
                        'spectroscopy_grid':  NHFMeasurementType.Spectroscopy,
                        'wavemode_nma':       NHFMeasurementType.WaveModeNMA
                    }
                    try:
                        self._measurement_type = measurement_type_map[self.attribute['measurement_type']]
                    except KeyError:
                        self._measurement_type = NHFMeasurementType.Unknown
                
        if self._measurement_type == NHFMeasurementType.Undefined:
            self._file_hdl.print_verbose(f"Warning: measurement '{self.name}' has unknown 'group_type'")
        return self._measurement_type

    def _read_measurement_structure(self):
        # read known dataset as 'channels'
        channel_identifier = 'signal_name' if self._file_hdl.version() >= (2,0) else 'name'        
        dataset_names = _get_sub_items_by_name(self._hdf_group, identifiers=[channel_identifier])
        if dataset_names:
            for dataset_id, dataset_name in dataset_names.items():
                h5_dataset = typing.cast(h5py.Dataset,self._hdf_group[dataset_id])
                self.channel[dataset_name] = NHFDataset(self,h5_dataset)

        segment_names = _get_sub_items_by_name(self._hdf_group, identifiers=['segment_name', 'name'])
        if segment_names:
            for segment_id, segment_name in segment_names.items():
                segment_data = self._hdf_group[segment_id]

                if isinstance(segment_data, h5py.Group):
                    self.segment[segment_name] = NHFSegment(self, segment_name, self._file_hdl, segment_data)
                    self.segment[segment_name]._read_segment_structure()
                elif isinstance(segment_data, h5py.Dataset):
                    self.channel[segment_name] = NHFDataset(self,segment_data)

        self.h5_groups = _get_unidentified_sub_groups(self._hdf_group, segment_names)
        self.h5_datasets = _get_unidentified_sub_dataset(self._hdf_group, segment_names | dataset_names)

        self._dataset_size = self.read_dataset_size()
        self._dataset_range = self.read_dataset_range()    
        self._dataset_offset = self.read_dataset_offset()    
        self._dataset_rotation = self.read_dataset_rotation()    
        for seg in self.segment.values():
            seg._dataset_range = self._dataset_range
            seg._dataset_size = self._dataset_size
            seg._dataset_offset = self._dataset_offset
            seg._dataset_rotation = self._dataset_rotation


class NHFCalibrationDataset():
    def __init__(self, file_hdl: 'NHFFileReader', hdf_dataset:h5py.Dataset) -> None:
        self._file_hdl = file_hdl
        self._hdf_dataset = hdf_dataset
        self.attribute = get_attributes(self._hdf_dataset) 

class NHFCalibrationGroup():
    def __init__(self, file_hdl: 'NHFFileReader', hdf_calibration_group:h5py.Group, group_id:str) -> None:
        self._file_hdl = file_hdl
        self._hdf_group = hdf_calibration_group
        self.group_id = group_id
        self.calibration_nodes:list[_CalNode] = []
        self.attribute = get_attributes(self._hdf_group) 
        self._load_calibration_graph()

    def build_calibration_graph(self, from__id_name:str, target_id_name:str) -> list[int]:
        node_source_name = from__id_name
        exclude_sink_names:list[str] = []
        calibration_graph = self._traverse_calibration_graph(node_source_name,target_id_name,exclude_sink_names)
        return calibration_graph
    
    def _traverse_calibration_graph(self,from__id_name:str, target_id_name:str,exclude_sink_names:list[str]) -> list[int]:
        node_graph:list[int] = []
        nodes = self.find_all_calibration_nodes_by_name(from__id_name,exclude_sink_names)
        for node_source_index in nodes:
            calib_node = self.calibration_nodes[node_source_index]
            
            # break recursion loop and return if target found 
            if calib_node.sink_name == target_id_name:
                node_graph.append(node_source_index)
                return node_graph   
                 
            # traverse down the graph
            node_source_name = calib_node.sink_name
            exclude_sink_names = exclude_sink_names.copy()
            exclude_sink_names.append(calib_node.source_name)
            next_node_graph = self._traverse_calibration_graph(node_source_name, target_id_name, exclude_sink_names)
            
            # break recursion and return found path
            if len(next_node_graph) > 0:
                node_graph.append(node_source_index)
                node_graph.extend(next_node_graph)
                return node_graph
            
        # stop recursion without result
        return []   
             
    def find_all_calibration_nodes_by_name(self, source_name:str, exclude_sink_names:list[str]) -> list[int]:
        nodes:list[int] = []
        for node_index, node in enumerate(self.calibration_nodes):
            if (node.source_name == source_name) and (node.sink_name not in exclude_sink_names):
                nodes.append(node_index)
        return nodes

    def _load_calibration_graph(self) -> None:
        self.calibration_nodes.clear()
        for dataset in self._hdf_group.values():
            if not self._load_calibration_node(dataset):
                break

    def _load_calibration_node(self, hdf_dataset:h5py.Dataset) -> bool:
        done = False
        hdf_map_type_to_eunm = {
            "linear": _CalMapType.Linear,
            "linear_non_invertible": _CalMapType.Linear_Non_Invertible,
            "exponential": _CalMapType.Exponential,
            "logarithmic": _CalMapType.Logarithmic,
            "linear_interpolation": _CalMapType.Linear_Interpolation,
        }

        try:
            calib_attributes = get_attributes(hdf_dataset)
            signal_calibration_id = calib_attributes["signal_calibration_id"]
            signal_sink_id = calib_attributes["signal_sink_id"]
            signal_sink_unit = calib_attributes["signal_sink_unit"]
            signal_source_unit = calib_attributes["signal_source_unit"]
            signal_source_id = calib_attributes["signal_source_id"]
            signal_mapping_type = calib_attributes["signal_mapping_type"]
            signal_mapping_parameters = calib_attributes["signal_mapping_parameters"]
            signal_invertibility = calib_attributes["signal_invertibility"]

            # check attributes against know values
            try: 
                calib_map_type = hdf_map_type_to_eunm[signal_mapping_type]
            except KeyError:
                raise ValueError(f"Unsupported calibration attribute value: {signal_mapping_type=} in calibration dataset {signal_calibration_id=}")

            if signal_invertibility not in ["right","left", "two_way"]:
                raise ValueError(f"Unsupported calibration attribute value: {signal_invertibility=} in calibration dataset {signal_calibration_id=}")

            if signal_invertibility in ["right", "two_way"]:  
                self.calibration_nodes.append(
                    _CalNode(
                        uuid = signal_calibration_id,
                        sink_name = signal_sink_id,
                        unit = signal_sink_unit,
                        map_type = calib_map_type,
                        map_par = signal_mapping_parameters,
                        calc_sink_from_source = signal_invertibility == "right",
                        source_name = signal_source_id
                    )
                )

            if signal_invertibility in ["left", "two_way"]:
                self.calibration_nodes.append(
                    _CalNode(
                        uuid = signal_calibration_id,
                        sink_name = signal_source_id,
                        unit = signal_source_unit,
                        map_type = calib_map_type,
                        map_par = signal_mapping_parameters,
                        calc_sink_from_source = True,
                        source_name = signal_sink_id
                    )
                )
            done = True

        except Exception as e:
            print(e)
        return done


class NHFFileReader():
    """ Main class to access nhf-files """

    # used by v1. NAN is not supported
    dataset_element_type_defined_as_int: dict = {
        0: [-(2.0**31), 2.0**31-1.0, 'dt_int32' ],
        1: [       0.0, 2.0**8 -1.0, 'dt_uint8' ],
        2: [       0.0, 2.0**16-1.0, 'dt_uint16'],
        3: [       0.0, 2.0**32-1.0, 'dt_uint32'],
        4: [       0.0, 2.0**64-1.0, 'dt_uint64'],
        5: [-(2.0**15), 2.0**15-1.0, 'dt_int16' ],
        6: [-(2.0**63), 2.0**63-1.0, 'dt_int64' ],
        7: [       0.0, 1.0        , 'dt_double']
    }
    # used by v2. NAN is defined as max "uint" or min "int"
    dataset_element_type_defined_as_str: dict = {
        'int32' : [-2.0**31 + 1.0, +2.0**31 - 1.0, 'dt_int32',  -2**31    ],
        'uint8' : [           0.0, +2.0**8  - 2.0, 'dt_uint8',   2**8  - 1],
        'uint16': [           0.0, +2.0**16 - 2.0, 'dt_uint16',  2**16 - 1],
        'uint32': [           0.0, +2.0**32 - 2.0, 'dt_uint32',  2**32 - 1],
        'uint64': [           0.0, +2.0**64 - 2.0, 'dt_uint64',  2**64 - 1],
        'int16' : [-2.0**15 + 1.0, +2.0**15 - 1.0, 'dt_int16' , -2**15    ],
        'int64' : [-2.0**63 + 1.0, +2.0**63 - 1.0, 'dt_int64' , -2**63    ],
        'double': [           0.0, +1.0          , 'dt_double',  np.nan]
    }
    
    def __init__(self, filename: Optional[pathlib.Path | str]=None, verbose:Optional[bool]=False, verbose_handler=None):
        """ Provide a nhf-file path directly at creating of the class or call later read() with filename
         
        Parameters
        ----------
            verbose: bool
                Set this to True if messages during reading or accessing is desired
            
            verbose_handler: func(msg:str)
                Define an own message handler functions to redirect the messages 
                A None is provided the default message handler print the message to console
        """
        self.h5_groups: dict[str, h5py.Group] = {}        
        self.h5_datasets: dict[str, h5py.Dataset] = {}        
        self.measurement: dict[str, NHFMeasurement] = {}
        self.attribute: dict[str, Any] = {}
        self._filename = pathlib.Path(filename) if filename is not None else pathlib.Path("")
        self._file_id:h5py.File = None # type: ignore
        self._last_file_version = (0,0)
        self._verbose = verbose
        self._verbose_output_handler = verbose_handler if verbose_handler else _default_verbose_output_handler
        self._last_print_verbose_message = ""
        if self._filename:
            if not self.read():
                raise IOError(self._last_print_verbose_message)
            
    def version(self) -> Tuple[int, int]:
        """ returns file version information in form of (major, minor) version number. If not accessible it returns (0,0)"""
        try: 
            return self._last_file_version
        except IndexError:
            return (0,0)
        
    def read(self, filename: Optional[pathlib.Path | str]=None) -> bool:
        """ Open the nid-file with given path for read access. """
        self._clear_data()
        if filename is not None:
            self._filename = pathlib.Path(filename) 
        if self._filename.is_file():
            try:
                self._file_id = h5py.File(self._filename, 'r')
                self.attribute = get_attributes(self._file_id)
                self._read_version()
                file_version = self.version()
                if file_version == (1,1) or (file_version>=(2,0) and file_version<(3,0)):
                    self._read_file_structure()
                    return True
                else:
                    self.print_verbose(f"File version {self.version()} is not supported.")
                    return False
                    
            except Exception as e:
                if self._file_id is not None: 
                    self._file_id.close()
                self._file_id = None # type: ignore
                self._clear_data()
                self.print_verbose(f"Could not read structure of file.'\nReason: {e}")
                return False
        else:
           self.print_verbose(f"File does not exist: {self._filename}")
           return False
        

    @property
    def measurements(self) -> list[NHFMeasurement]:
        return list(self.measurement.values())
    
    def measurement_count(self) -> int:
        return len(self.measurement)
    
    def measurement_list(self) -> list[str]:
        return list(self.measurement.keys())
        
    def measurement_name(self, key: int) -> str:
        return list(self.measurement.keys())[key]
    
    @property
    def groups(self) -> list[h5py.Group]:
        return list(self.h5_groups.values())
        
    def group_count(self) -> int:
        return len(self.h5_groups)        

    def group_list(self) -> list[str]:
        return list(self.h5_groups.keys())

    def group_name(self, key: int) -> str:
        return self.group_list()[key]

    @property
    def datasets(self) -> list[h5py.Dataset]:
        return list(self.h5_datasets.values())
        
    def dataset_count(self) -> int:
        return len(self.h5_datasets)
        
    def dataset_list(self) -> list[str]:
        return list(self.h5_datasets.keys())

    def dataset_name(self, key: int) -> str:
        return self.dataset_list()[key]

    def print_verbose(self, msg:str):
        self._last_print_verbose_message = msg
        if self._verbose:
            self._verbose_output_handler(msg)

    def last_message(self) -> str:
        return self._last_print_verbose_message
    
    def pretty_print_structure(self):
        print(self)

    def print_file_structure(self):
        self.pretty_print_structure()

    # internal functions, not for user access
    
    def _read_version(self):
        major = int(self.attribute['nsf_file_version_major'])
        minor = int(self.attribute['nsf_file_version_minor'])
        self._last_file_version = (major, minor)        

    def _read_file_structure(self):    
        measurement_identifier = 'measurement_name' if self.version() >= (2,0) else 'name'
        measurement_names = _get_sub_items_by_name(self._file_id, identifiers=[measurement_identifier])
        if measurement_names:
            for measurement_id, measurement_name in measurement_names.items():
                measurement_data = typing.cast(h5py.Group,self._file_id[measurement_id])
                self.measurement[measurement_name] = NHFMeasurement(measurement_name, self, measurement_data)
                self.measurement[measurement_name]._read_measurement_structure()

        self.cal_group = self._read_calibration_group()
        known_groups = measurement_names
        if self.cal_group is not None:
            known_groups[self.cal_group.group_id] = ""
        self.h5_groups = _get_unidentified_sub_groups(self._file_id, known_groups)
        self.h5_datasets = _get_unidentified_sub_dataset(self._file_id, known_groups)

    def _read_calibration_group(self) -> NHFCalibrationGroup | None:
        cal_group = None

        group_type_names = _get_sub_items_by_name(self._file_id, identifiers=["group_type"])  
        for group_name, group_type in  group_type_names.items():  
            if group_type == "calibration":
                cal_group = NHFCalibrationGroup(self, typing.cast(h5py.Group,self._file_id[group_name]), group_name)
                break
        return cal_group

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._clear_data()
        if self._file_id:
            self._file_id.close()
        self._file_id = None # type: ignore

    def __str__(self) -> str:
        structure = ""
        for m in self.measurements:
            structure += f"Measurement '{m.name}' of type '{m.measurement_type.name}':\n"
            for s in m.segments:
                structure += f"    Segment '{s.name}':\n"
                for ch in s.channels:
                    structure += f"        Channel '{ch.name}':\n"
                for gr in s.groups:
                        structure += f"        Group '{gr.name}':\n"
                for d in s.datasets:
                        structure += f"        Dataset '{d.name}':\n"
            for ch in m.channels:
                structure += f"    Channel '{ch.name}':\n"
            for gr in m.groups:
                structure += f"    Group '{gr.name}':\n"
            for d in m.datasets:
                structure += f"    Dataset '{d.name}':\n"
        if self.cal_group is not None:
            structure += f"Calibration Group '{self.cal_group.group_id}':\n"
        for gr in self.groups:
            structure += f"Group '{gr.name}':\n"
        for d in self.datasets:
            structure += f"Dataset '{d.name}':\n"
        return structure

    def __del__(self):
        if self._file_id:
            self._file_id.close()
        self._file_id = None # type: ignore

    def _clear_data(self):
        self.h5_groups: dict[str, h5py.Group] = {}
        self.measurement: dict[str, NHFMeasurement] = {}
        self.attribute: dict[str, Any] = {}
