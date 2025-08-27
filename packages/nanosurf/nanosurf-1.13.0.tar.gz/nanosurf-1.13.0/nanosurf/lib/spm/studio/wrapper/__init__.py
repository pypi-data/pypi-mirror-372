# studio node base class.py

import os
import sys
import importlib
import importlib.util
import pathlib
import enum
import re
import lupa
from typing import Any
import hashlib
import keyword
import nanosurf.lib.datatypes.sci_val.convert as convert
from nanosurf.lib.util.fileutil import create_folder
g_this_compiler_version = "2.5"
g_context_package_name_prefix = "cmd_tree_"
g_cmd_tree_root_name = "root"

g_skip_sequencer_definition = True

class LuaType(enum.Enum):
    Nil = "nil"
    Table = "list"
    Float = "float"
    Int = "int"
    Str = "str"
    Bool = "bool"
    Function = "function"
    EnumType = "EnumType"

def get_lua_type(obj) -> LuaType:
    """ Get the type of a lua object as LuaType enum """
    lua_type = lupa.lua_type(obj) if lupa.lua_type(obj) else type(obj)

    if lua_type == "function":
        return LuaType.Function
    elif lua_type == "table":
        return LuaType.Table
    elif lua_type is list:
        return LuaType.Table
    elif lua_type is str:
        return LuaType.Str
    elif lua_type is float:
        return LuaType.Float
    elif lua_type is int:
        return LuaType.Int
    elif lua_type is bool:
        return LuaType.Bool
    elif isinstance(lua_type, enum.Enum):
        return LuaType.EnumType
    return LuaType.Nil

def get_lua_type_str(obj) -> str:
    """ Get the type of a lua object as string representation """
    # if argument is not already a LuaType, try to convert it
    if not(isinstance(obj, LuaType)):
        lua_type = get_lua_type(obj)
    else:
        lua_type = obj
    try:
        return lua_type.value
    except Exception:
        pass
    return LuaType.Nil.value

class CmdTreeNode():
    def __init__(self):
        self._lua_tree_name = ""
        self._context : 'StudioScriptContext' = None

    def __getitem__(self, key):
        return self._context.get(f"{self._lua_tree_name}[{key}]")

    def __setitem__(self, key, value):
        return self._context.set(f"{self._lua_tree_name}[{key}]",value)
    
    @property
    def is_studio(self)-> bool:
        return True

class CmdTreeProp(CmdTreeNode):
    def __init__(self):
        super().__init__()
        self._lua_value_type = LuaType.Nil

    def __repr__(self) -> str:
        if self._lua_value_type == LuaType.Float or self._lua_value_type == LuaType.Int:
            return convert.to_string(value=self.value, unit=self.unit)
        return super().__repr__()

class CmdTreeCompiler():
    def __init__(self, parent : 'StudioScriptContext'):
        self.parent_context = parent
        self._file_content = [""]
        self._last_error = ""
        self.my_own_path = pathlib.Path(os.path.dirname(os.path.abspath(__file__)))
        self.regex_non_enum_chars = re.compile('[^0-9a-zA-Z]+', flags=re.UNICODE)
        self.regex_first_char_a_number = re.compile(r'\d\w*', flags=re.UNICODE)

    def build_wrapper_class(self, context_name: str, cmd_table) -> bool:
        """ Creates a new class tree if new table from studio is different from stored class tree.
        
            Returns:
            --------
            reload: bool
                If True reload of wrapper class is needed by caller
        """
        self.cmd_package_name = g_context_package_name_prefix + context_name

        # check if recompilation of command tree is necessary
        runtime_cmd_tree_hash = self.get_table_version(cmd_table, g_cmd_tree_root_name)
        compiled_cmd_tree_hash, compiled_compiler_version = self.get_compiled_versions()

        create_new_class_tree = (runtime_cmd_tree_hash != compiled_cmd_tree_hash) or (compiled_compiler_version != g_this_compiler_version)
        if create_new_class_tree:
            compiled_tree_file = self.my_own_path / (self.cmd_package_name + '.py')
            new_module_name = "nanosurf.lib.spm.studio.wrapper."+self.cmd_package_name
            if self.compile_command_tree_to_file(cmd_table, runtime_cmd_tree_hash, compiled_tree_file, root_node_name=g_cmd_tree_root_name):
                # after compiling load the new generated wrapper
                try:
                    spec = importlib.util.spec_from_file_location(new_module_name, compiled_tree_file)
                    module = importlib.util.module_from_spec(spec)
                    sys.modules[new_module_name] = module
                except Exception:
                    self._last_error = f"Could not import dynamically created package from:\n{compiled_tree_file}"
                    raise ImportError(self._last_error)
            else:
                self._last_error = f"Could not create wrapper for '{self.cmd_package_name}':\nReason: {self._last_error}"
                raise IOError(self._last_error)
        return create_new_class_tree

    @property
    def last_error(self) -> str:
        return self._last_error

    def get_compiled_versions(self) -> tuple[str, str]:
        tree_hash = ""
        compiler_version = ""
        try:
            mod = importlib.import_module("nanosurf.lib.spm.studio.wrapper."+self.cmd_package_name)
            tree_hash = mod.g_cmd_tree_hash
            compiler_version = mod.g_compiler_version
        except Exception:
            pass
        return (tree_hash, compiler_version)

    def get_table_version(self, table, lua_tree_name: str) -> str:
        hash_str = ""
        hash_str = self._get_table_hash_str(table, lua_tree_name)
        hash_str_sorted = ";".join(sorted(hash_str.split(";")))
        table_hash = hashlib.md5(bytes(hash_str_sorted, encoding='utf-8'))
        return table_hash.hexdigest()

    def _get_table_hash_str(self, table, lua_tree_name: str) -> str:
        hash_str = lua_tree_name
        for item_name, item_value in table.items():
            item_type = get_lua_type(item_value)
            if (item_type == LuaType.Table) and type(item_name) == str: # Ignore arrays with numeric index
                new_lua_tree_name = str(lua_tree_name+"."+item_name)
                hash_str += str(";" + self._get_table_hash_str(item_value, new_lua_tree_name))
            elif (item_type != LuaType.Nil) and type(item_name) == str:
                new_lua_tree_name = str(lua_tree_name+"."+item_name)
                hash_str += str(";" + new_lua_tree_name)
        return hash_str

    def _has_table_functions(self, table) -> bool:
        for _, item_value in table.items():
            if get_lua_type(item_value) == LuaType.Function:
                return True
        return False

    def _is_lu_trigger_func(sel, tree_name:str) -> bool:
        try:
            prefix = tree_name[:7]
            suffix = tree_name[-8:]
            return prefix == "root.lu" and suffix == ".trigger"
        except Exception:
            return False

    def _is_lu_busy_func(sel, tree_name:str) -> bool:
        try:
            prefix = tree_name[:7]
            suffix = tree_name[-5:]
            return prefix == "root.lu" and suffix == ".busy"
        except Exception:
            return False

    def _is_property_access_func(self, func_name:str) -> bool:
        try:
            suffix = func_name[-4:]
            return (suffix == "_set") or (suffix == "_get")
        except Exception:
            return False


    def _is_table_a_studio_property(self, table) -> bool:
        """ Detect if a lua table contains a studio property definition

        Implementation
        --------------
        This detection method is coupled with the studio lua script "make_property.lua"
        This script implements the 'meta table' implementation to access variables.
        for each variable it create a pair of set/get function.
        """
        found_access_func = False
        found_value = False

        # search for key word
        for item_name, _ in table.items():
            if item_name == "value" or item_name == "vector":
                found_value = True
                break

        # if key word found check for accessor function
        if found_value:
            for item_name, item_value in table.items():
                item_type = get_lua_type(item_value)
                if (item_type == LuaType.Function) and self._is_property_access_func(item_name):
                    found_access_func = True
                    break

        # if key value and accessor found, it is a property definition
        return found_access_func and found_value

    def _is_table_item_a_enums_definition(self, item_name, item_value) -> bool:
        """ Detects if a lua table item is a enum definition"""
        item_value_type = get_lua_type(item_value)
        return (item_value_type == LuaType.Table) and (item_name == "enums")
            
    def _has_table_enums_node(self, table) -> bool:
        """ Detects if a lua table contains enum definitions as sub table"""
        found = False
        for item_name, item_value in table.items():
            found = self._is_table_item_a_enums_definition(item_name, item_value)
            if found:
                break
        return found
    
    def _is_enum_property(self, prop_elements:dict[str, str]) -> bool:
        return "enum" in prop_elements

    def _is_vector_property(self, prop_elements:dict[str, str]) -> bool:
        return "vector" in prop_elements

    def _is_power_of_two(self, n:int):
        return (n != 0) and (n & (n-1) == 0)

    def _is_enum_mask(self, enum_table) -> bool:
        has_only_bit_mask = True
        for item_name, item_value in enum_table.items():
            if item_name != "all" and not(item_name == "none" and item_value == 0):
                has_only_bit_mask &= self._is_power_of_two(int(item_value))
                if not has_only_bit_mask:
                    break
        return has_only_bit_mask

    def _convert_enum_str_to_enum_class_name(self, enum_name:str) -> str:
        class_name = enum_name
        class_name = self.regex_non_enum_chars.sub('_', class_name)
        if self.regex_first_char_a_number.match(class_name):
            class_name =  "num_" + class_name
        if keyword.iskeyword(class_name):
            class_name =  class_name + "_"
        return class_name

    def _get_correct_number_type(self, lua_tree_name : str,  item_name : str) -> LuaType:
        type_str = self.parent_context.lua_number_type_str(f"{lua_tree_name}.{item_name}")
        if type_str == "float":
            return LuaType.Float
        elif type_str == "integer":
            return LuaType.Int
        return LuaType.Nil

    def _get_studio_property_elements(self, prop_table, lua_tree_name : str) -> dict[str, str]:
        """ Extract from property style lua_table a list of all property names and their types
            returns a dict with key:name, val:type
        """
        property_elements: dict[str, str] = {}
        for item_name, item_value in prop_table.items():
            item_type = get_lua_type(item_value)
            if item_type == LuaType.Int:
                item_type = self._get_correct_number_type(lua_tree_name, item_name)
            if item_type != LuaType.Function:
                property_elements[item_name] = get_lua_type_str(item_type)
        return property_elements

    def _get_studio_attribute_elements(self, attribute_table) -> dict[str, str]:
        """ Extract from attribute style lua_table a list of all attribute access functions and enum list
            returns a dict with key:name, val:type
        """
        attr_elements: dict[str, str] = {}
        for item_name, item_value in attribute_table.items():
            attr_elements[item_name] = get_lua_type_str(item_value)
        return attr_elements

    def compile_command_tree_to_file(self, studio_cmd_tree, table_version_hash: str, python_file: pathlib.Path, root_node_name:str) -> bool:
        done = False
        print(f"Creating new wrapper classes in file : {python_file}")
        # create file content
        self._file_content = [""]
        self._write_cmd_tree_node(studio_cmd_tree, class_name=root_node_name.capitalize(), lua_tree_name=root_node_name)
        self.write_header(table_version_hash, g_this_compiler_version)

        # write content to file
        if not python_file.parent.exists():
            if not create_folder(python_file.parent):
                self._last_error = f"Could not create parent of '{python_file}'"
                return done
            
        try:
            f =  open(python_file, "w")
        except Exception:
            self._last_error = f"Could not create file: '{python_file}'"
            return done

        try:
            for line in self._file_content:
                f.write(line)
            done = True
        except Exception:
            self._last_error = f"Could not write to file: '{python_file}'"

        f.close()
        return done

    def create_pretty_print_command_table(self, table) -> str:
        self.dump = ""
        self._dump_command_table(table, indent="")
        return self.dump

    def _dump_command_table(self, table, indent:str) -> str:
        for item_name, item_value in table.items():
            item_type = get_lua_type(item_value)
            self.dump += f"{indent}{item_name}={get_lua_type_str(item_type)}"
            if item_type == LuaType.Table:
                self._dump_command_table(item_value, indent + "   "  )

    def write_header(self, table_version_hash: str, compiler_version: str):
        class_list = []
        class_list.append(f"# studio_wrapper.py\n")
        class_list.append(f"\n")
        class_list.append(f"import enum\n")
        class_list.append(f"from typing import Any\n")
        class_list.append(f"import nanosurf.lib.spm.studio.wrapper as wrap\n")
        class_list.append(f"\n")
        class_list.append(f"g_cmd_tree_hash = '{table_version_hash}'\n")
        class_list.append(f"g_compiler_version = '{compiler_version}'\n")
        class_list.append(f"\n")

        self._file_content = class_list + self._file_content

    def _write_enums_node(self, enum_tables, class_name:str, lua_tree_name: str) -> list[str]:
        class_list = []
        class_list.append(f"class {class_name}(wrap.CmdTreeProp):\n")
        class_list.append("\n")

        for enum_class, enum_class_entries in enum_tables.items():
            class_list.append(f"    class {str(enum_class).capitalize()}(enum.Enum):\n")
            for enum_name, enum_value in enum_class_entries.items():
                class_list.append(f"        {self._convert_enum_str_to_enum_class_name(enum_name)} = {enum_value}\n")
            class_list.append("\n")
        
        class_list.append(f"    def __init__(self, context: 'StudioScriptContext'):\n")
        class_list.append(f"        super().__init__()\n")
        class_list.append(f"        self._context = context\n")
        class_list.append(f"        self._lua_tree_name = '{lua_tree_name}'\n")
        class_list.append("\n")

        self._file_content = class_list + self._file_content
        
    def _write_cmd_tree_node(self, table, class_name:str, lua_tree_name: str) -> list[str]:
        class_list = []

        if self._is_table_a_studio_property(table):
            class_list.append(f"class {class_name}(wrap.CmdTreeProp):\n")
            prop_elements = self._get_studio_property_elements(table, lua_tree_name)

            is_enum_type = self._is_enum_property(prop_elements)
            if is_enum_type:
                enum_table = table["enum"]
                is_enum_mask_type = self._is_enum_mask(enum_table)
                class_list.append("\n")
                if is_enum_mask_type:
                    class_list.append(f"    class ValueMask(enum.IntEnum):\n")
                else:
                    class_list.append(f"    class ValueEnum(enum.Enum):\n")
                for enum_name, enum_value in enum_table.items():
                    class_list.append(f"        {self._convert_enum_str_to_enum_class_name(enum_name)} = {enum_value}\n")
                class_list.append("\n")

            class_list.append(f"    def __init__(self, context: 'StudioScriptContext'):\n")
            class_list.append(f"        super().__init__()\n")
            class_list.append( "        self._context = context\n")
            class_list.append(f"        self._lua_tree_name = '{lua_tree_name}'\n")
            if self._is_vector_property(prop_elements):
                class_list.append(f"        self._lua_value_type = wrap.LuaType('{prop_elements['vector']}')\n")
            else:
                class_list.append(f"        self._lua_value_type = wrap.LuaType('{prop_elements['value']}')\n")
            class_list.append("\n")

            for value_name, value_type in prop_elements.items():
                if value_name == "value":
                    if is_enum_type:
                        if is_enum_mask_type:
                            class_list.append( "    @property\n")
                            class_list.append(f"    def {value_name}(self) -> int:\n")
                            class_list.append(f"        return int(self._context.get('{lua_tree_name}.value_raw'))\n")
                            class_list.append("\n")
                            class_list.append(f"    @{value_name}.setter\n")
                            class_list.append(f"    def {value_name}(self, new_val:int):\n")
                            class_list.append(f"        self._context.set('{lua_tree_name}.value_raw', int(new_val))\n")
                            class_list.append("\n")
                        else:
                            class_list.append( "    @property\n")
                            class_list.append(f"    def {value_name}(self) -> ValueEnum:\n")
                            class_list.append(f"        return self.ValueEnum(self._context.get('{lua_tree_name}.value_raw'))\n")
                            class_list.append("\n")
                            class_list.append(f"    @{value_name}.setter\n")
                            class_list.append(f"    def {value_name}(self, new_val:ValueEnum):\n")
                            class_list.append(f"        self._context.set('{lua_tree_name}.value_raw', new_val.value)\n")
                            class_list.append("\n")
                    else:
                        class_list.append( "    @property\n")
                        class_list.append(f"    def {value_name}(self) -> {value_type}:\n")
                        class_list.append(f"        return {value_type}(self._context.get('{lua_tree_name}.{value_name}'))\n")
                        class_list.append("\n")
                        class_list.append(f"    @{value_name}.setter\n")
                        class_list.append(f"    def {value_name}(self, new_val:{value_type}):\n")
                        class_list.append(f"        self._context.set('{lua_tree_name}.{value_name}', {value_type}(new_val))\n")
                        class_list.append("\n")
                elif value_name == "vector":
                    class_list.append( "    @property\n")
                    class_list.append(f"    def vector(self) -> {value_type}:\n")
                    class_list.append(f"        return {value_type}(self._context.get('{lua_tree_name}.vector'))\n")
                    class_list.append("\n")
                    class_list.append( "    @vector.setter\n")
                    class_list.append(f"    def vector(self, new_val:{value_type}):\n")
                    class_list.append(f"        self._context.set('{lua_tree_name}.vector', {value_type}(new_val))\n")
                    class_list.append("\n")
                    class_list.append( "    def get_vector_value(self, index:int):\n")
                    class_list.append(f"        return self._context.call('{lua_tree_name}.get_vector_value',int(index))\n")
                    class_list.append("\n")
                    class_list.append( "    def set_vector_value(self, index:int, new_val:float):\n")
                    class_list.append(f"        self._context.call('{lua_tree_name}.set_vector_value', int(index), new_val)\n")
                    class_list.append("\n")
                else:
                    class_list.append( "    @property\n")
                    class_list.append(f"    def {value_name}(self) -> {value_type}:\n")
                    class_list.append(f"        return {value_type}(self._context.get('{lua_tree_name}.{value_name}'))\n")
                    class_list.append("\n")
                    class_list.append(f"    @{value_name}.setter\n")
                    class_list.append(f"    def {value_name}(self, new_val:{value_type}):\n")
                    class_list.append(f"        self._context.set('{lua_tree_name}.{value_name}', {value_type}(new_val))\n")
                    class_list.append("\n")

            class_list.append("\n")

            self._file_content = class_list + self._file_content
        else:
            class_list.append(f"class {class_name}(wrap.CmdTreeNode):\n")

            has_table_enums_node =  self._has_table_enums_node(table)
            class_list.append( "    def __init__(self, context: 'StudioScriptContext'):\n")
            class_list.append( "        super().__init__()\n")
            class_list.append( "        self._context = context\n")
            class_list.append(f"        self._lua_tree_name = '{lua_tree_name}'\n")

            for item_name, item_value in table.items():
                item_type = get_lua_type(item_value)
                if item_type == LuaType.Table:
                    if (class_name == "Root") and (item_name == "seq") and g_skip_sequencer_definition:
                        continue
                    if not isinstance(item_name,str): # Ignore arrays with numeric index
                        continue
                    if has_table_enums_node and (item_name == "enums"): # enums tables are handled as read only property called 'enums'  
                        continue
                    class_list.append(f"        self.{item_name} = {class_name+item_name.capitalize()}(self._context)\n")
            class_list.append("\n")

            if has_table_enums_node:
                enum_class_name = class_name + "Enums"
                class_list.append( "    @property\n")
                class_list.append(f"    def enums(self) -> {enum_class_name}:\n")
                class_list.append(f"        return {enum_class_name}(self._context)\n")
                class_list.append("\n")

            for item_name, item_value in table.items():
                item_type = get_lua_type(item_value)
                if item_type == LuaType.Function:
                    if self._is_lu_trigger_func(lua_tree_name):
                        class_list.append(f"    def {item_name}(self) -> None:\n")
                        class_list.append(f"        return self._context.call('{lua_tree_name}.{item_name}')\n")
                        class_list.append("\n")
                    elif self._is_lu_busy_func(lua_tree_name):
                        class_list.append( "    @property\n")
                        class_list.append(f"    def {item_name}(self) -> bool:\n")
                        class_list.append(f"        return bool(self._context.call('{lua_tree_name}.{item_name}'))\n")
                        class_list.append("\n")
                    elif not(self._is_property_access_func(item_name)):
                        class_list.append(f"    def {item_name}(self, *args, **kwargs) -> Any:\n")
                        class_list.append(f"        return self._context.call('{lua_tree_name}.{item_name}', *args, **kwargs)\n")
                        class_list.append("\n")
                elif (item_type != LuaType.Nil) and (item_type != LuaType.Table) and isinstance(item_name, str):
                    if item_type == LuaType.Int:
                        item_type = self._get_correct_number_type(lua_tree_name, item_name)
                    type_str = get_lua_type_str(item_type)
                    class_list.append( "    @property\n")
                    class_list.append(f"    def {item_name}(self) -> {type_str}:\n")
                    class_list.append(f"        return {type_str}(self._context.get('{lua_tree_name}.{item_name}'))\n")
                    class_list.append("\n")
                    class_list.append(f"    @{item_name}.setter\n")
                    class_list.append(f"    def {item_name}(self, new_val:{type_str}):\n")
                    class_list.append(f"        self._context.set('{lua_tree_name}.{item_name}', {type_str}(new_val))\n")
                    class_list.append("\n")

            class_list.append("\n")

            # add new class on top of base classes
            self._file_content = class_list + self._file_content

            # follow cmd_tree nodes recursively
            for item_name, item_value in table.items():
                item_type = get_lua_type(item_value)
                if (item_type == LuaType.Table) and isinstance(item_name,str): # Ignore arrays with numeric index
                    new_class_name = str(class_name+item_name.capitalize())
                    new_lua_tree_name = str(lua_tree_name+"."+item_name)

                    # currently we skip sequencer definition
                    if new_lua_tree_name == "root.seq" and g_skip_sequencer_definition:
                        continue
                    
                    if has_table_enums_node and self._is_table_item_a_enums_definition(item_name, item_value):
                        enum_tables = table["enums"]
                        self._write_enums_node(enum_tables, new_class_name, new_lua_tree_name)
                    else:
                        self._write_cmd_tree_node(item_value, new_class_name, new_lua_tree_name)
