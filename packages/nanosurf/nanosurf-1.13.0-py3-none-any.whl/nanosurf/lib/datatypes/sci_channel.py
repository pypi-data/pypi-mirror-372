"""Copyright (C) Nanosurf AG - All Rights Reserved (2021)
License - MIT"""


from typing import Optional, Union
import numpy as np

class SciChannel:
    def __init__(self, 
        copy_from: Optional[Union[list,np.ndarray,'SciChannel']] = None, 
        array_length:int = 0, 
        unit:str = "arb", name:str = "Data"):

        self.value = np.zeros(array_length)
        self.unit = unit
        self.name = name

        if copy_from is not None:
            if isinstance(copy_from, SciChannel):
                self.value = np.copy(copy_from.value)
                self.unit = copy_from.unit
                self.name = copy_from.name
            else:
                self.value = np.copy(copy_from)
                self.unit = unit
                self.name = name

    def __len__(self):
        return len(self.value)
        

