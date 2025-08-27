
""" Property Library.  Useful to organize, manipulate, store and change values 
Copyright Nanosurf AG 2021
License - MIT
"""

import pathlib
import configparser
from typing import Any

from PySide6 import QtCore
    
from nanosurf.lib.datatypes import sci_val 

convert_str_to_type_map = {
   "str" : lambda x : repr_str_to_str(str(x)),
   "float" : lambda x : float(x),
   "int" : lambda x : int(x),
   "bool" : lambda x : bool((x == "True") or (x == "true")),
   "SciVal" : lambda x : sci_val.from_str(x),
   "WindowsPath" : lambda x : repr_str_to_pathlib(str(x)),
}

def repr_str_to_str(repstr:str) -> str:
    return repstr.removeprefix("'").removesuffix("'")

def repr_str_to_pathlib(path_str: str) -> pathlib.Path:
    return pathlib.Path(path_str.removeprefix("WindowsPath('").removesuffix("')"))

class PropVal(QtCore.QObject):
    sig_value_changed = QtCore.Signal()
    
    def __init__(self, var = None, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.__var = var

    # property based interface

    @property
    def var(self) -> Any:
        return self.__var

    @property
    def value(self) -> Any:
        if isinstance(self.__var, sci_val.SciVal):
            return self.__var.value()
        else:
            return self.__var

    @value.setter
    def value(self, val):
        if isinstance(self.__var, sci_val.SciVal) :
            if isinstance(val, sci_val.SciVal): 
                self.__var = val
                self.sig_value_changed.emit()        
            else:
                if  self.__var.value() != val:
                    self.__var.set_value(val)
                    self.sig_value_changed.emit()
        else:
            if isinstance(val, sci_val.SciVal): 
                if self.__var != val.value():
                    self.__var = val.value()
                    self.sig_value_changed.emit()
            else:
                assert type(val) == type(self.__var), "Error: Type of argument has to be equal to initial value type. Use change_type() instead"
                if self.__var != val:
                    self.__var = val
                    self.sig_value_changed.emit()

    # classic style interface. 
    # For calls where the property based interface cannot be used (e.g as lambda function)
    def set_value(self, val):
        self.value = val

    def get_value(self):
        return self.value

    def change_type(self, new_value:Any):
        self.__var = new_value
        self.sig_value_changed.emit()

    def serialize(self) -> str:
        return type(self.__var).__qualname__ + "@" + repr(self.__var)

    def deserialize(self, str) -> bool:
        type_str, ser_val = str.split("@")
        done = False
        try:
            self.value = convert_str_to_type_map[type_str](ser_val)
            done = True
        except KeyError:
            self.__var = None
        return done

class PropStore():
    def has_property(self, prop_name: str) ->bool:
        prop = getattr(self, prop_name, None)
        return isinstance(prop, PropVal)

    def get_property(self, prop_name: str) -> PropVal:
        prop = getattr(self, prop_name, None)
        if isinstance(prop, PropVal):
            return prop
        else:
            return PropVal()

    def set_property(self, prop_name: str, prop_value: PropVal):
        setattr(self, prop_name, prop_value)

    def get_property_dict(self, hide_locals: bool = True) -> dict:
        prop_dict = {}
        for v in dir(self):
            if isinstance(getattr(self, v), PropVal):
                if not(hide_locals and v[0] == "_"): 
                    prop_dict[v] = getattr(self, v)
        return prop_dict

    def serialize(self, ignore_locals: bool = True) -> dict:
        prop_dict = self.get_property_dict(hide_locals=ignore_locals)
        
        name_serial_str_dict = {}
        try:
            for name, prop in prop_dict.items():
                name_serial_str_dict[name] = prop.serialize()
        except Exception:
            pass
        return name_serial_str_dict

    def deserialize(self, name_serial_str_dict : dict, ignore_locals: bool = True) -> bool:
        # convert each key into a property
        done = True
        for name, ser_str in name_serial_str_dict.items():
            if not (name[0]=='_' and ignore_locals):
                # create new or update property
                prop = getattr(self, name, PropVal())
                if prop.deserialize(ser_str):
                    self.set_property(name, prop)
                else:
                    done = False
        return done

def save_to_ini_file(store: PropStore, file: pathlib.Path, section: str, 
    do_not_save_locals: bool = True, update_content: bool = True) -> bool:
    """ Save all properties and their values into a text file in a human readable form
        
    Parameters
    ----------
    file: pathlib.Path
        The file to write to, including path 
    section: str
        The name of the section to write into
    do_not_save_locals : bool, optional
        if this option is True, then do not save properties with a "_" prefix in their name
    update_content : bool, optional
        if set to True, update file content with section. Otherwise overwrite file.

    Returns
    -------
    bool 
        True in case the write to file was successful, otherwise False
    """

    try:
        config = configparser.ConfigParser()
        config.optionxform = lambda option: option # preserve upper/lower case

        if update_content and file.is_file():
            try:
                config.read(file)
            except Exception:  
                pass

        key_value_dict = store.serialize(ignore_locals=do_not_save_locals)
        config[section] = key_value_dict

        with open(file, 'w') as f:
            config.write(f)
            f.close()
        done = True
    except Exception:
        done = False        
    return done

def load_from_ini_file(store:PropStore, file: pathlib.Path, section: str, 
    do_not_load_locals: bool = True) -> bool:
    """ Load all properties and their values from a text file
    
    Parameters
    ----------
    file: pathlib.Path
        The file to load from, including path 
    section: str
        The name of the section to read from
    do_not_load_locals
        if this option is True, do not load stored values with a "_" prefix in their name

    Returns
    -------
    bool 
        True in case the write to file was successful, otherwise False
    """
    done = False
    try:
        # read in section
        config = configparser.ConfigParser(interpolation=None)
        config.optionxform = lambda option: option # preserve upper/lower case
        config.read(file)

        sec = config[section]

        store.deserialize(sec, ignore_locals=do_not_load_locals)
        done = True
    except Exception:
        pass
    return done
