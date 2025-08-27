"""Logical Unit Interface Runtime Wrapper
Copyright (C) Nanosurf AG - All Rights Reserved (2021)
License - MIT"""

import enum
import re
import pythoncom

def to_snake_case(word):
    # one could argue, that a number starts and ends a word, but this is
    # not too bad. (Numbers in variable names are a code smell anyhow)
    str1 = re.sub('([0-9]+)([A-Za-z]+)', r'\1_\2', word)
    str2 = re.sub('([A-Za-z])([0-9]+)', r'\1_\2', str1)
    str3 = re.sub('(^_)([A-Z][a-z]+)', r'\1_\2', str2)
    # break between lower case and upper case
    # this leaves abbreviations (consecutive capitals) together)
    return re.sub('([a-z])([A-Z])', r'\1_\2', str3).lower()

class _StudioLikeAttributes():
    pass

class _StudioLikeTriggers():
    pass

class _StudioLikeIsBusy():
    _type_id = -1
    _logical_unit = None
    _instance_id = -1

class _Attribute():
    """Accessor for LU Attributes"""
    # TODO: simplify the Attribute call
    # (it has too go too much back and forth to the parent).
    def __init__(self, parent, attribute_id):
        self._parent = parent
        self._id = attribute_id

    def __str__(self):
        try:
            value = self.value
        except pythoncom.com_error as exception:
            if ': Parameter error.' in exception.excepinfo[2]:
                value = "write-only"
        return f'{value} ({self.value_min} - {self.value_max}) {self.unit}'

    @property
    def value(self):
        return self._parent._logical_unit.Attribute(
            self._parent._type_id, self._parent._instance_id, self._id)

    @value.setter
    def value(self, value):
        self._parent._logical_unit.Attribute(
            self._parent._type_id, self._parent._instance_id, self._id, value)

    @property
    def unit(self):
        return self._parent._logical_unit.AttributeUnit(
            self._parent._type_id, self._parent._instance_id, self._id)

    @property
    def value_max(self):
        return self._parent._logical_unit.AttributeMax(
            self._parent._type_id, self._parent._instance_id, self._id)

    @property
    def value_min(self):
        return self._parent._logical_unit.AttributeMin(
            self._parent._type_id, self._parent._instance_id, self._id)

    @property
    def max(self):
        return self.value_max

    @property
    def min(self):
        return self.value_min
    
class _AttributeVector(_Attribute):
    class _ItemAccess():
        def __init__(self, parent, attribute_id):
            self._parent = parent
            self._id = attribute_id

        def __getitem__(self, index):
            return self._parent._logical_unit.AttributeVectorByIndexDouble(
                self._parent._type_id, self._parent._instance_id, self._id,
                index)

        def __setitem__(self, index, value):
            self._list[index] = value
            self._parent._logical_unit.AttributeVectorByIndexDouble(
                self._parent._type_id, self._parent._instance_id, self._id,
                index, value)

    def __init__(self, parent, attribute_id):
        super().__init__(parent, attribute_id)
        self._item_access = self._ItemAccess(
            parent, attribute_id)

    @property
    def item(self):
        return self._item_access

    @property
    def value(self):
        return self._parent._logical_unit.AttributeVectorDouble(
            self._parent._type_id, self._parent._instance_id, self._id)

    @value.setter
    def value(self, value):
        self._item_access._list = value
        self._parent._logical_unit.AttributeVectorDouble(
            self._parent._type_id, self._parent._instance_id, self._id, value)


class _LogicalUnit():
    """virtual base class for logical units."""
    _type_id = -1
    _attribute_dict = {}
    _trigger_dict = {}
    _busy_dict = {}
    _logical_unit = None

    def __init__(self, instance_id=0):
        self._instance_id = instance_id
        self._attributes = _StudioLikeAttributes()
        self._triggers = _StudioLikeTriggers()
        self._is_busy = _StudioLikeIsBusy()

        for name, ident in self._attribute_dict.items():
            snake_name = to_snake_case(name)
            if snake_name[-4:] == "_vec":
                new_attribute = _AttributeVector(self, ident)
            else:
                new_attribute = _Attribute(self, ident)
            setattr(self, snake_name, new_attribute)
            setattr(self._attributes, snake_name, new_attribute)

        # add triggers
        for name, ident in self._trigger_dict.items():
            setattr(self._triggers, to_snake_case(name), _LogicalUnit._create_a_studio_trigger(self, ident))

        # add busy properties
        busy_class_dict = {
            '_type_id': self._type_id,
            '_logical_unit': self._logical_unit,
            '_instance_id': self._instance_id,
        }
        for name, ident in self._busy_dict.items():
            busy_class_dict[to_snake_case(name)] = _LogicalUnit._create_is_busy(ident)
        type_name = str(type(self)).split(".")[-1][:-2]
        busy_class = type(f"{type_name}BusyClass", (_StudioLikeIsBusy,), busy_class_dict)
        setattr(self, "_is_busy", busy_class())

    @property
    def attribute(self) -> _StudioLikeAttributes:
        return self._attributes

    @property
    def trigger(self) -> _StudioLikeTriggers:
        return self._triggers
                     
    @property
    def busy(self) -> _StudioLikeIsBusy:
        return self._is_busy
                     
    def __str__(self):
        result = ""
        for name, ident in self._attribute_dict.items():
            attr_name = to_snake_case(name)
            result = result + attr_name + ": " + str(getattr(self, attr_name)) + '\n'
        return result

    def _create_a_studio_trigger(self, trigger_id):
        return lambda : self._logical_unit.Trigger(
            self._type_id, self._instance_id, trigger_id)

    def _create_trigger(trigger_id):
        return lambda self: self._logical_unit.Trigger(
            self._type_id, self._instance_id, trigger_id)

    def _create_is_busy(busy_id):
        return property(lambda self: self._logical_unit.IsBusy(
            self._type_id, self._instance_id, busy_id))


def logical_unit_type(type_name, logical_unit, definition_dict):
    # The attributes must be created dynamically, because we
    # need to pass the self object, or some other properties of the
    # containing class to them.
    # I could find a way to do this with attributes created at class creation
    # time.
    type_dict = {
        '_type_id': definition_dict['id'],
        '_attribute_dict': definition_dict['attributes'],
        '_trigger_dict': definition_dict['triggers'],
        '_busy_dict': definition_dict['busy'],
        '_logical_unit': logical_unit,
        'Instance': enum.IntEnum('Instance', definition_dict['instances'])}

    for name, enum_dict in definition_dict['attribute_enumerations'].items():
        type_dict[name] = enum.IntEnum(name, enum_dict)

    # This could be done in the _LogicalUnit constructor as well, it is 
    # actually a bit strange that the capture of self by the lambda returned by
    # _create_trigger works at all.
    for name, ident in definition_dict['triggers'].items():
        type_dict[to_snake_case(name)] = _LogicalUnit._create_trigger(ident)

    # This must be called here, it cannot be called in the _LogicalUnit constructor.
    for name, ident in definition_dict['busy'].items():
        type_dict[to_snake_case(name)] = _LogicalUnit._create_is_busy(ident)

    return type(type_name, (_LogicalUnit,), type_dict)


if __name__ == "__main__":
    import manager_mock

    assert to_snake_case("CurrentAFMLockInYBinary") == "current_afm_lock_in_y_binary"

    test_lu_definition = {
        'id': 1,
        'instances': {'Z': 0, 'X': 1},
        'attributes':  {'input': 0, 'speed_vec': 1},
        'attribute_enumerations': {
            'Input':      {'x': 0, 'y': 1, 'z': 2},
            'Something':   {'NoThing': 0, 'OneThing': 1}
        },
        'triggers': {'start': 0, 'stop': 1},
        'busy': {'test_busy': 0, 'busy_too': 1}}
    test_lu3_definition = {
        'id': 3,
        'instances': {'BLI': 0, 'BLA': 1},
        'attributes':  {'output': 0, 'speedVec': 1},
        'attribute_enumerations': {
            'Output':      {'x': 0, 'y': 1, 'z': 2},
            'Something':   {'NoThing': 0, 'OneThing': 1}
        },
        'triggers': {'start': 0, 'stop': 1},
        'busy': {'test_busy': 0}}

    logical_unit = manager_mock.LogicalUnit()
    globals()['RampGen'] = logical_unit_type(
        'RampGen', logical_unit, test_lu_definition)
    globals()['TestLu2'] = logical_unit_type(
        'TestLu2', logical_unit, test_lu3_definition)

    ramp_z = RampGen(RampGen.Instance.Z)
    bli_unit = TestLu2(TestLu2.Instance.BLI)
    bla_unit = TestLu2(TestLu2.Instance.BLA)

    print("Test _logical_unit member")
    ramp_z._logical_unit.Attribute(1, 2, 3, 1.0)
    print(ramp_z._logical_unit.Attribute(1, 2, 3))
    print()

    print("Attribute directory:")
    print(dir(ramp_z))
    print()

    ramp_z.start()
    # Trig: Type_id: 1 Inst No: Instance.FIRST Trigger ID: 0
    ramp_z.stop()
    # Trig: Type_id: 1 Inst No: Instance.FIRST Trigger ID: 1
    print(ramp_z.test_busy)
    # False

    z_input = ramp_z.input
    z_input.value = RampGen.Input.z
    # SetAttr: Type ID: 1 Inst No: Instance.FIRST Attr ID: 0 Value: Input.z
    print(z_input.value)
    # GetAttr: Type ID: 1 Inst No: Instance.FIRST Attr ID: 0 Value: Input.z
    # Input.z
    print(z_input.value_max)
    # 10.0
    print(ramp_z.speed_vec.unit)
    # m  actually, all units will return m in this test.

    ramp_z.speed_vec.value = [0.1, 0.2]
    # SetAttr: Type ID: 1 Inst No: Instance.FIRST Attr ID: 1 Value: [0.1, 0.2]
    ramp_z.speed_vec.item[0] = 0.3
    # SetItem: Type ID: 1 Inst No: Instance.FIRST Attr ID: 1 At[0] Value: 0.3
    speeds = ramp_z.speed_vec.value
    # GetAttr: Type ID: 1 Inst No: Instance.FIRST Attr ID: 1 Value: [0.3, 0.2]
    print(speeds)
    # [0.3, 0.2]
    print(speeds[1])
    # 0.2
    print(ramp_z.speed_vec.item[0])
    # GetItem: Type ID: 1 Inst No: Instance.FIRST Attr ID: 1 At[0] Value: 0.3
    # 0.3

    print("\nNote that these statements have different effect:")
    z_input = ramp_z.input
    # -
    z_input_val = z_input.value
    # GetAttr: Type ID: 1 Inst No: Instance.FIRST Attr ID: 0 Value: Input.z
    print("")
    z_input.value = RampGen.Input.x
    # SetAttr: Type ID: 1 Inst No: Instance.FIRST Attr ID: 0 Value: Input.x
    z_input_val = RampGen.Input.y
    # -
