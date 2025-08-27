"""Parser for LogicalUnit_InterfaceShared.h
Copyright (C) Nanosurf AG - All Rights Reserved (2021)
License - MIT"""

import enum
import re

class ParseShared():

    def __init__(self, lu_shared_file_path, verbose=False):
        self._lu_file = open(lu_shared_file_path, 'r')
        self._verbose = verbose
        self.lu_type_definitions = dict()
        self._parse_lu_shared_file()
        self._lu_file.close()

    def __del__(self):
        self._lu_file.close()

    def _parse_enum(self):
        state_wait_for_enum = 1
        state_wait_for_open_brace = 2
        state_read_ID = 3
        enum_name = ""
        enum_dict = {}
        state = state_wait_for_enum
        for lu_line in self._lu_file:
            # ignore comments and emty spaces
            lu_line = lu_line.split("//")[0].strip()

            if state == state_wait_for_enum:
                curline = lu_line.split(" ")
                if curline[0] == "enum":
                    enum_name = curline[1]
                    # print("enum = " + enum)
                    state = state_wait_for_open_brace
                    continue

            if state == state_wait_for_open_brace:
                curline = lu_line.split(" ")
                if curline[0] == "{":
                    index = -1
                    state = state_read_ID
                    continue

            if state == state_read_ID:
                curline = lu_line.split(",")
                if curline[0] == "":
                    # print("Skip empty line")
                    pass
                elif "}" in curline[0]:
                    # print("End of block found")
                    break
                else:
                    curvalue = curline[0].strip().split("=")
                    # print(curvalue)
                    name = curvalue[0].strip()
                    if name in ('BEGIN', 'END', 'NumInstances'):
                        continue

                    if len(curvalue) > 1:
                        index = int(curvalue[1].strip().split("/")[0], 0)
                        # print("index = " + str(index))
                    else:
                        index = index + 1
                        # print("AutoIndex = " + str(index))
                    enum_dict.update({name: index})
                    continue
        return enum_name, enum_dict

    def _clear_dictionaries(self):
        self._instances = dict()
        self._attribute_dict = dict()
        self._attribute_enum_dict = dict()
        self._trigger_dict = dict()
        self._busy_dict = dict()

    def _add_dictionaries(self, lu_type):
        if len(self._instances) > 0:
            self.lu_type_definitions[lu_type] = {
                'id': self.lu_type_dict[lu_type],
                'instances': self._instances,
                'attributes': self._attribute_dict,
                'attribute_enumerations': self._attribute_enum_dict,
                'triggers': self._trigger_dict,
                'busy': self._busy_dict
            }

    def _parse_lu_shared_file(self):
        def print_warning(message):
            if (self._verbose):
                print("Warning: Enumeration \"" + name + "\": "
                      + message
                )

        (name, self.lu_type_dict) = self._parse_enum()
        if name != 'LUTypeID':
            print_warning("First enumeration must be \"LUTypeID\"!")
            raise ValueError

        last_lu_type = ''
        current_lu_type = ''
        self._clear_dictionaries()

        ParseState = enum.Enum(
            'ParseState',
            ['instances', 'attributes', 'triggers', 'attribute_enum'])
        state = ParseState.instances
        while True:
            (name, dictionary) = self._parse_enum()
            if name == "":
                self._add_dictionaries(last_lu_type)
                break

            lu_enum_type_match = re.match(r"LU([a-zA-Z]+)_(\w+)", name)
            if lu_enum_type_match is None:
                print_warning("Skip, Enumeration name not parsable as LU enumeration type.")
                continue

            current_lu_type = lu_enum_type_match.group(1)
            if current_lu_type not in self.lu_type_dict:
                print_warning("Skip, does not match an LU type from LUTypeID.")
                continue

            if current_lu_type != last_lu_type:
                self._add_dictionaries(last_lu_type)
                self._clear_dictionaries()
                last_lu_type = current_lu_type
                state = ParseState.instances

            enum_type = lu_enum_type_match.group(2)

            if state == ParseState.instances:
                if enum_type != "InstID":
                    print_warning("Instance ID enumeration expected !")
                    raise ValueError

                self._instances = dictionary
                state = ParseState.attributes
                continue

            if state == ParseState.attributes:
                if enum_type != "AttrID":
                    print_warning(f"Attribute enumeration for {last_lu_type} expected."
                    )
                    raise ValueError

                self._attribute_dict = dictionary
                state = ParseState.triggers
                continue

            if state == ParseState.triggers:
                if enum_type != "TriggerID":
                    print_warning(f"Trigger enumeration for {last_lu_type} expected.")
                    raise ValueError

                self._trigger_dict = dictionary
                state = ParseState.attribute_enum
                continue

            if state == ParseState.attribute_enum:
                if enum_type == "BusyID":
                    # busy is an optional, pre-defined type
                    self._busy_dict = dictionary
                else:
                    # add attribute value enumeraton to ???
                    self._attribute_enum_dict[enum_type] = dictionary
                    state = ParseState.attribute_enum
                continue


if __name__ == "__main__":
    print("\nParse test")
    my_test = ParseShared(r"../../test/LogicalUnit_InterfaceShared.h", True)
