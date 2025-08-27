"""Data Buffer Wrapper
Copyright (C) Nanosurf AG - All Rights Reserved (2021)
License - MIT"""

class _Dimension():
    def __init__(self, data_buffer, group_id, channel_id, dimension_id):
        self._data_buffer_com = data_buffer
        self._group_id = group_id
        self._channel_id = channel_id
        self._dimension_id = dimension_id

    @property
    def name(self):
        return self._data_buffer_com.DataName(
            self._group_id, self._channel_id, self._dimension_id)

    @property
    def unit(self):
        return self._data_buffer_com.DataUnit(
            self._group_id, self._channel_id, self._dimension_id)

    @property
    def data_min(self):
        return self._data_buffer_com.DataMin(
            self._group_id, self._channel_id, self._dimension_id)

    @property
    def data_range(self):
        return self._data_buffer_com.DataRange(
            self._group_id, self._channel_id, self._dimension_id)


class _Channel():
    def __init__(self, data_buffer, group_id, channel_id):
        # TODO: can we not access the properties of the containing class ?
        self._data_buffer_com = data_buffer
        self._group_id = group_id
        self._channel_id = channel_id

    @property
    def data(self):
        # If we get the data as soon as we are not syncing and the data is
        # valid, we nevertheless get back None.
        # If we try a little later, we get valid data.
        # TODO: why is this neccessary ?
        tmp_data = None
        while tmp_data is None:
            tmp_data = self._data_buffer_com.DataRAW(
                self._group_id, self._channel_id)
        return tmp_data

    # Transfer of raw data from PC to controller (e.g. for memory signal generator)
    #
    # The raw data is expected to be in channel interleaved format
    # with the channel_id set to the channel mask.
    # Memory signal generator has fixed 8 channel data format therefore
    # channel_id must be set to 255 and the data has the interleaved format
    # ch1[0] ch2[0] ch3[0] ch4[0] ch5[0] ch6[0] ch7[0] ch8[0] ch1[1] ch2[1], ch3[1], ...
    #
    # example:
    # group = ll.DataBuffer()
    # channel = group.channel(255) # channel mask always 8 interleaved channels!
    # d = np.array(d1)
    # buffer = np.empty((d.size * 8,))
    # buffer[0::8] = d1 # Position x
    # buffer[1::8] = d2 # Drive x
    # buffer[2::8] = d3 # Position y
    # buffer[3::8] = d4 # Drive y
    # buffer[4::8] = d5 # Position z
    # buffer[5::8] = d6 # Drive Z
    # buffer[6::8] = d7 # Out7
    # buffer[7::8] = d8 # Out8
    # channel.data = buffer

    @data.setter
    def data(self, my_data):
        self._data_buffer_com.DataRAW(
            self._group_id, self._channel_id, my_data)

    def filtered_data(self, filter_id):
        tmp_data = None
        while tmp_data is None:
            tmp_data = self._data_buffer_com.Data(
                self._group_id, self._channel_id, filter_id)
        return tmp_data

    def dimension(self, dimension_id):
        return _Dimension(
            self._data_buffer_com, self._group_id, self._channel_id,
            dimension_id)


class DataBufferInterface():
    """Python Interface to the DataBuffer COM object."""
    # Reference to a DataBuffer COM object,
    # Value should be added set on creation of sub-class by data_buffer_type.
    # Thus, each COM interface application interace has its own Python
    # interace.
    _data_buffer_com = None

    def __init__(self, group_id=-1):
        if group_id == -1:
            self._group_id = self._data_buffer_com.CreateDataGroup
            self._new_group = True
        else:
            self._group_id = group_id
            self._new_group = False

    def __del__(self):
        # TODO:
        # - make destructor instead
        # - it (or the spm object) should check if the DataGroup is still in
        #   use
        if self._new_group:
            if self._data_buffer_com is not None:
                self._data_buffer_com.DeleteDataGroup(self._group_id)

    def channel(self, channel_id: int):
        """Returns a channel of the data buffer.

        Parameters
        ----------
        channel_id:
            the index of the channel to create.
        """
        return _Channel(self._data_buffer_com, self._group_id, channel_id)

    def synchronize_data_group(self):
        self._data_buffer_com.SyncDataGroup(self._group_id)

    @classmethod
    def delete_all(cls):
        cls._data_buffer_com.DeleteAllDataGroups()

    @property
    def available_points(cls):
        return cls._data_buffer_com.AvailableBufferPoints

    @property
    def count(cls):
        return cls._data_buffer_com.DataGroupCount

    @property
    def group_id(self):
        return self._group_id

    @property
    def is_synchronizing(self):
        return self._data_buffer_com.IsSyncingDataGroup(self._group_id)

    @property
    def is_valid(self):
        return self._data_buffer_com.DataValid(self._group_id)

    @property
    def timestamp_first_sample(self):
        return self._data_buffer_com.TimestampFirstSample(self._group_id)

    @property
    def timestamp_first_sample_str(self):
        return str(self.timestamp_first_sample(self))

    @property
    def channel_count(self):
        return self._data_buffer_com.DataChannelCount(self._group_id)


def data_buffer_type(data_buffer):
    """Creates a Python databuffer interface type for a DataBuffer COM object.
    To be used by the LowLevel() class.

    Returns
    -------
    DataBufferInterface derived object type.

    Parameters
    ----------
    data_buffer: DataBuffer COM object.
    """
    type_dict = {'_data_buffer_com': data_buffer}
    return type('DataBuffer', (DataBufferInterface,), type_dict)
