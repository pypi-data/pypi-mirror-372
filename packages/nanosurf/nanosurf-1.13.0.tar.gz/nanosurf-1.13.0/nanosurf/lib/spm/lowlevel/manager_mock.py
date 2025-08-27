"""Mock for application.SPMCtrlManager.LogicalUnit object.
Copyright (C) Nanosurf AG - All Rights Reserved (2021)
License - MIT"""


class SPMCtrlManager():
    def __init__(self):
        self.LogicalUnit = LogicalUnit()
        self.DataBuffer = None


class LogicalUnit():
    """Mock for application.SPMCtrlManager.LogicalUnit object."""
    def __init__(self):
        self._value_store = [[[
            0.0 for attr_id in range(50)]
                for inst_id in range(20)]
                for type_id in range(100)
        ]

    def Attribute(self, type_id, instance_id, attr_id, value=None):
        if value is None:
            value = self._value_store[type_id][instance_id][attr_id]
            print(
                "GetAttr: Type ID: " + str(type_id) +
                " Inst No: " + str(instance_id) +
                " Attr ID: " + str(attr_id) +
                " Value: " + str(value)
            )
            return value
        else:
            self._value_store[type_id][instance_id][attr_id] = value
            print(
                "SetAttr: Type ID: " + str(type_id) +
                " Inst No: " + str(instance_id) +
                " Attr ID: " + str(attr_id) +
                " Value: " + str(value)
            )

    def AttributeMax(self, type_id, instance_id, attr_id):
        return 10.0

    def AttributeMin(self, type_id, instance_id, attr_id):
        return -10.0

    def AttributeUnit(self, type_id, instance_id, attr_id):
        return "m"

    def AttributeVectorDouble(self, type_id, instance_id, attr_id, value=None):
        if value is None:
            value = self._value_store[type_id][instance_id][attr_id]
            print(
                "GetAttr: Type ID: " + str(type_id) +
                " Inst No: " + str(instance_id) +
                " Attr ID: " + str(attr_id) +
                " Value: " + str(value)
            )
        else:
            self._value_store[type_id][instance_id][attr_id] = value
            print(
                "SetAttr: Type ID: " + str(type_id) +
                " Inst No: " + str(instance_id) +
                " Attr ID: " + str(attr_id) +
                " Value: " + str(value)
            )
        return value

    def AttributeVectorByIndexDouble(self, type_id, instance_id, attr_id, index, value=None):
        if value is None:
            value = self._value_store[type_id][instance_id][attr_id][index]
            print(
                "GetItem: Type ID: " + str(type_id) +
                " Inst No: " + str(instance_id) +
                " Attr ID: " + str(attr_id) +
                " Index: " + str(index) +
                " Value: " + str(float(value))
            )
        else:
            self._value_store[type_id][instance_id][attr_id][index] = value
            print(
                "SetItem: Type ID: " + str(type_id) +
                " Inst No: " + str(instance_id) +
                " Attr ID: " + str(attr_id) +
                " Index: " + str(index) +
                " Value: " + str(float(value)))
        return value

    def Trigger(self, type_id, instance_id, trigger_id):
        print(
            "Trig: Type_id: " + str(type_id) +
            " Inst No: " + str(instance_id) +
            " Trigger ID: " + str(trigger_id))

    def IsBusy(self, type_id, instance_id, busy_id):
        print(
            "IsBusy: Type_id: " + str(type_id) +
            " Inst No: " + str(instance_id) +
            " Busy ID: " + str(busy_id))
        return False

if __name__ == '__main__':
    print("\nTest LUI")
    lui = LogicalUnit()
    lui.Trigger(3, 2, 1)
    assert (not lui.IsBusy(3, 2, 5))

    test_val = 0.4
    lui.Attribute(1, 2, 3, test_val)
    assert lui.Attribute(1, 2, 3) == test_val

    test_val = [0.1, 0.2, 0.3]
    lui.AttributeVectorDouble(1, 3, 3, test_val)
    assert lui.AttributeVectorDouble(1, 3, 3) == test_val
    assert lui.AttributeVectorByIndexDouble(1, 3, 3, 0) == test_val[0]

    test_val = 2.0
    lui.AttributeVectorByIndexDouble(1, 3, 3, 1, test_val)
    assert lui.AttributeVectorByIndexDouble(1, 3, 3, 1) == test_val
    del(lui)
